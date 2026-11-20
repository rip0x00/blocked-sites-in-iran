#!/usr/bin/env python3
"""Refresh the domain lists from their upstream sources. (version 2.1.0)

Sources and rules (each verified to reproduce the published lists exactly):

  list.txt
    From the OONI measurement compilation by Yuix-Networks
    (blocked-sites-dataset, data/latest.csv). Keeps Iranian (IR) rows from
    the newest month in the file with at least 20 measurements and a
    confirmed-blocking rate of at least 50%. A leading "www." is stripped
    and the result is deduplicated and sorted. Per-domain evidence is also
    written to data/domains.jsonl.

  blocked-from-outside.txt
    From Chocolate4U/Iran-clash-rules (release asset ir.txt), itself built
    from the official Iranian domain registries via bootmortis. Keeps the
    "+."-prefixed entries, strips the prefix, drops bare TLDs,
    deduplicates and sorts.

  blocked-by-sanctions.txt
    From freedomofdevelopers/fod (file "domains"). Strips leading dots,
    deduplicates and sorts. Structured per-domain records are also
    written to data/sanctions.jsonl.

  dist/
    Ready-made consumer outputs (JSON, CSV, AdGuard, dnsmasq, hosts,
    Clash, Surge, sing-box) are rendered in memory by
    tools/build_dist.py during the build phase and written in the same
    all-or-nothing write phase as the lists.

Usage:
  python3 tools/update_lists.py           # sync, rewrite lists.json, log to CHANGELOG.md
  python3 tools/update_lists.py --check   # report differences only, write nothing
  python3 tools/update_lists.py --force   # allow changes larger than 25%

Safety and failure behaviour:
  - All three sources are fetched and all lists are built in memory first;
    files are written only after every fetch, build and check has passed.
    A failed run writes NOTHING — the published files are never left
    half-updated.
  - Network: each request has a 60s timeout and is attempted up to 3 times
    with backoff (2s, then 5s) on network errors and HTTP 5xx. HTTP 4xx
    fails immediately.
  - A rebuilt list that comes back empty, a malformed source, or a change
    larger than 25% of a list's current size (without --force) aborts the
    run — that usually means an upstream format change, not real-world
    change.
  - Exit codes: 0 = success (whether or not anything changed),
    1 = source data problem, 2 = network failure after all retries.

Requirements: Python >= 3.10, standard library only.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GENERATOR_VERSION = "2.1.0"
LICENSE_LINE = "Data: CC BY-NC-SA 4.0 (see DATA-LICENSE.md); Code: MIT (see LICENSE)"

ROOT = Path(__file__).resolve().parent.parent

OONI_CSV_URL = (
    "https://raw.githubusercontent.com/Yuix-Networks/"
    "blocked-sites-dataset/main/data/latest.csv"
)
IR_TXT_URL = (
    "https://github.com/Chocolate4U/Iran-clash-rules/"
    "releases/latest/download/ir.txt"
)
FOD_URL = "https://raw.githubusercontent.com/freedomofdevelopers/fod/master/domains"

SOURCES = {
    "list.txt": {
        "source": "OONI measurements compiled by Yuix-Networks/blocked-sites-dataset",
        "source_url": OONI_CSV_URL,
        "method": (
            "Iran (IR) rows from the newest month in the dataset with "
            ">= 20 measurements and >= 50% confirmed blocking; "
            "leading www. stripped; deduplicated; sorted."
        ),
        "status_semantics": (
            "Confirmed blocked in Iran in the data period (OONI measurements)."
        ),
    },
    "blocked-from-outside.txt": {
        "source": "Chocolate4U/Iran-clash-rules (from bootmortis/iran-hosted-domains, official IR registries)",
        "source_url": IR_TXT_URL,
        "method": (
            "Release asset ir.txt: '+.'-prefixed entries with the prefix "
            "stripped; bare TLDs dropped; deduplicated; sorted."
        ),
        "status_semantics": (
            "Iran-hosted domains (official registries). Not individually "
            "tested for reachability from outside Iran."
        ),
    },
    "blocked-by-sanctions.txt": {
        "source": "freedomofdevelopers/fod",
        "source_url": FOD_URL,
        "method": "File 'domains': leading dots stripped; deduplicated; sorted.",
        "status_semantics": (
            "Historical / community-reported: the service has blocked Iran "
            "at some point; current blocking is not guaranteed."
        ),
    },
}

FETCH_TIMEOUT = 60
FETCH_ATTEMPTS = 3
FETCH_BACKOFF = (2, 5)  # seconds to sleep after attempt 1 and attempt 2


class SourceDataError(ValueError):
    """The upstream data is empty, malformed, or changed implausibly."""


class NetworkError(Exception):
    """A source could not be downloaded after all retries."""


def fetch(url: str) -> bytes:
    """Download a URL with retries. Returns the raw response bytes.

    Retries (up to FETCH_ATTEMPTS attempts, sleeping FETCH_BACKOFF between
    them) happen on network errors and HTTP 5xx; HTTP 4xx fails at once.
    Raises NetworkError when the source cannot be fetched.
    """
    last_error = None
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        req = urllib.request.Request(
            url, headers={"User-Agent": "blocked-sites-in-iran-sync"}
        )
        try:
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_error = e
            if not 500 <= e.code < 600:
                raise NetworkError(
                    f"GET {url} failed with HTTP {e.code} (not retrying)"
                ) from e
            reason = f"HTTP {e.code}"
        except (urllib.error.URLError, OSError) as e:
            last_error = e
            reason = str(e)
        if attempt < FETCH_ATTEMPTS:
            delay = FETCH_BACKOFF[attempt - 1]
            print(
                f"warning: GET {url} attempt {attempt} failed ({reason}); "
                f"retrying in {delay}s...",
                file=sys.stderr,
            )
            time.sleep(delay)
    raise NetworkError(
        f"GET {url} failed after {FETCH_ATTEMPTS} attempts: {last_error}"
    )


def build_blocked_in_iran(csv_text: str) -> tuple[list[str], str, dict]:
    """Build list.txt from the OONI compilation CSV text.

    Returns (domains, data_period, stats) where stats maps each domain to
    (measurements, confirmed_rate) from its strongest passing row.
    Raises SourceDataError on malformed input.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    required = {"month", "country_code", "domain", "measurements", "confirmed_rate"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise SourceDataError(
            "OONI CSV is malformed: expected columns "
            f"{sorted(required)}, got {reader.fieldnames!r}"
        )
    try:
        rows = list(reader)
    except csv.Error as e:
        raise SourceDataError(f"OONI CSV could not be parsed: {e}") from e
    months = sorted({r["month"] for r in rows if r["country_code"] == "IR"})
    if not months:
        raise SourceDataError("no IR rows in OONI dataset")
    latest = months[-1]
    stats: dict[str, tuple[int, float]] = {}
    for r in rows:
        if r["country_code"] != "IR" or r["month"] != latest:
            continue
        try:
            measurements = int(r["measurements"])
            rate = float(r["confirmed_rate"])
        except (TypeError, ValueError) as e:
            raise SourceDataError(
                f"OONI CSV has a non-numeric measurements/confirmed_rate "
                f"for domain {r.get('domain')!r}"
            ) from e
        if measurements >= 20 and rate >= 0.5:
            d = r["domain"].strip().lower()
            d = d[4:] if d.startswith("www.") else d
            if d not in stats or measurements > stats[d][0]:
                stats[d] = (measurements, rate)
    return sorted(stats), latest, stats


def build_from_outside(text: str) -> list[str]:
    out = set()
    for line in text.splitlines():
        if line.startswith("+."):
            d = line[2:].strip().lower()
            if "." in d:
                out.add(d)
    return sorted(out)


def build_sanctions(text: str) -> list[str]:
    return sorted({line.strip().lower().lstrip(".") for line in text.splitlines() if line.strip()})


def check_delta(
    old: list[str], new: list[str], force: bool = False
) -> tuple[list[str], list[str]]:
    """Return (added, removed) between old and new.

    Raises SourceDataError if the total change is larger than 25% of the
    current list size and force is not set.
    """
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    delta = len(added) + len(removed)
    if old and delta > 0.25 * len(old) and not force:
        raise SourceDataError(
            f"change of {delta} entries ({len(old)} -> {len(new)}) exceeds "
            "the 25% safety limit; inspect the upstream source and rerun "
            "with --force if this change is real"
        )
    return added, removed


def build_domains_jsonl(
    stats: dict, data_period: str, retrieved_at: str
) -> str:
    """Per-domain evidence for list.txt, one JSON object per line."""
    lines = []
    for domain in sorted(stats):
        measurements, rate = stats[domain]
        lines.append(
            json.dumps(
                {
                    "domain": domain,
                    "list": "blocked-in-iran",
                    "status": "confirmed",
                    "country": "IR",
                    "data_period": data_period,
                    "measurements": measurements,
                    "confirmed_rate": rate,
                    "source_url": OONI_CSV_URL,
                    "retrieved_at": retrieved_at,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + "\n"


def build_sanctions_jsonl(domains: list[str], retrieved_at: str) -> str:
    """Structured per-domain records for the sanctions list.

    The FOD source is community-maintained and records that a service has
    blocked Iran at some point, so every record is status "historical"
    with confidence "community-reported" — never a live guarantee.
    """
    lines = []
    for domain in domains:
        lines.append(
            json.dumps(
                {
                    "domain": domain,
                    "list": "sanctions",
                    "status": "historical",
                    "direction": "foreign_to_iran",
                    "source": "freedomofdevelopers/fod",
                    "source_url": FOD_URL,
                    "confidence": "community-reported",
                    "retrieved_at": retrieved_at,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + "\n"


def load_build_dist():
    """Load the sibling tools/build_dist.py (tools/ is not a package)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_dist", ROOT / "tools" / "build_dist.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_current(name: str) -> list[str]:
    path = ROOT / name
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def load_meta() -> dict:
    path = ROOT / "lists.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"lists": []}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    ap.add_argument("--force", action="store_true", help="allow changes larger than 25%%")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    retrieved_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    today = now.date().isoformat()

    # ---- Phase 1: fetch everything and build everything in memory. ----
    # Nothing is written in this phase; any failure leaves the repo as-is.
    print("Fetching upstream sources...")
    try:
        raw = {
            "list.txt": fetch(OONI_CSV_URL),
            "blocked-from-outside.txt": fetch(IR_TXT_URL),
            "blocked-by-sanctions.txt": fetch(FOD_URL),
        }
    except NetworkError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return 2

    try:
        ooni_domains, data_period, ooni_stats = build_blocked_in_iran(
            raw["list.txt"].decode("utf-8", errors="replace")
        )
        built = {
            "list.txt": ooni_domains,
            "blocked-from-outside.txt": build_from_outside(
                raw["blocked-from-outside.txt"].decode("utf-8", errors="replace")
            ),
            "blocked-by-sanctions.txt": build_sanctions(
                raw["blocked-by-sanctions.txt"].decode("utf-8", errors="replace")
            ),
        }
        for name, new in built.items():
            if not new:
                raise SourceDataError(f"rebuilt {name} is empty")
        currents = {name: read_current(name) for name in built}
        deltas = {
            name: check_delta(currents[name], built[name], force=args.force)
            for name in built
        }
    except SourceDataError as e:
        print(f"ERROR: source data problem: {e}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return 1

    # Render the dist/ consumer outputs in memory too, from the NEW
    # lists, so a dist failure also aborts the run before any write.
    try:
        dist_files = load_build_dist().build_all(built, retrieved_at)
    except Exception as e:
        print(f"ERROR: dist build failed: {e}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return 1

    # ---- Phase 2: report. ----
    changed = []
    for name, new in built.items():
        added, removed = deltas[name]
        status = "unchanged" if new == currents[name] else f"+{len(added)} / -{len(removed)}"
        print(f"{name}: {len(currents[name])} -> {len(new)} entries ({status})")
        if new != currents[name]:
            changed.append((name, len(currents[name]), len(new), len(added), len(removed)))

    if args.check:
        print("Check only — nothing written.")
        return 0

    # ---- Phase 3: write. Only reached when every check above passed. ----
    meta = load_meta()
    meta_by_file = {e["file"]: e for e in meta.get("lists", [])}
    new_meta_lists = []
    for name, new in built.items():
        if new != currents[name]:
            (ROOT / name).write_text("\n".join(new) + "\n", encoding="utf-8")
        entry = dict(meta_by_file.get(name, {}))
        entry.update(SOURCES[name])
        entry["file"] = name
        entry["entries"] = len(new)
        entry["sha256"] = hashlib.sha256(raw[name]).hexdigest()
        entry["retrieved_at"] = retrieved_at
        if name == "list.txt":
            entry["data_period"] = data_period
        if new != currents[name]:
            entry["last_synced"] = today
        else:
            entry.setdefault("last_synced", today)
        new_meta_lists.append(entry)

    # Per-domain evidence for the OONI list, written alongside list.txt.
    jsonl_path = ROOT / "data" / "domains.jsonl"
    if any(c[0] == "list.txt" for c in changed) or not jsonl_path.exists():
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.write_text(
            build_domains_jsonl(ooni_stats, data_period, retrieved_at),
            encoding="utf-8",
        )
        print("data/domains.jsonl updated.")

    # Structured records for the sanctions list, same rule as above.
    sanctions_path = ROOT / "data" / "sanctions.jsonl"
    if any(c[0] == "blocked-by-sanctions.txt" for c in changed) or not sanctions_path.exists():
        sanctions_path.parent.mkdir(parents=True, exist_ok=True)
        sanctions_path.write_text(
            build_sanctions_jsonl(built["blocked-by-sanctions.txt"], retrieved_at),
            encoding="utf-8",
        )
        print("data/sanctions.jsonl updated.")

    # dist/ consumer outputs, rendered in memory during the build phase.
    # Written when a list changed or any dist file is missing, so an
    # unchanged run does not churn dist/manifest.json's timestamp.
    if changed or any(not (ROOT / rel).exists() for rel in dist_files):
        for rel, data in dist_files.items():
            path = ROOT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f"dist/ updated ({len(dist_files)} files).")

    new_meta = {
        "schema_version": 1,
        "generated_at": retrieved_at,
        "generator": "tools/update_lists.py",
        "generator_version": GENERATOR_VERSION,
        "license": LICENSE_LINE,
        "lists": new_meta_lists,
    }
    (ROOT / "lists.json").write_text(
        json.dumps(new_meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if changed:
        changelog = ROOT / "CHANGELOG.md"
        marker = "<!-- new entries are inserted below this line -->"
        lines = [
            f"## {today} — automated sync",
            "",
        ]
        for name, old_n, new_n, a, r in changed:
            line = f"- `{name}`: {old_n} → {new_n} entries (+{a} / −{r})."
            if name == "list.txt":
                line += f" Source period: {data_period}."
            lines.append(line)
        lines.append("")
        if changelog.exists() and marker in changelog.read_text(encoding="utf-8"):
            text = changelog.read_text(encoding="utf-8")
            text = text.replace(marker, marker + "\n\n" + "\n".join(lines), 1)
            changelog.write_text(text, encoding="utf-8")
            print("CHANGELOG.md updated.")
    else:
        print("All lists already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
