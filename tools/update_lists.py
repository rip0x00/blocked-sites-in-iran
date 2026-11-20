#!/usr/bin/env python3
"""Refresh the domain lists from their upstream sources.

Sources and rules (each verified to reproduce the published lists exactly):

  list.txt
    From the OONI measurement compilation by Yuix-Networks
    (blocked-sites-dataset, data/latest.csv). Keeps Iranian (IR) rows from
    the newest month in the file with at least 20 measurements and a
    confirmed-blocking rate of at least 50%. A leading "www." is stripped
    and the result is deduplicated and sorted.

  blocked-from-outside.txt
    From Chocolate4U/Iran-clash-rules (release asset ir.txt), itself built
    from the official Iranian domain registries via bootmortis. Keeps the
    "+."-prefixed entries, strips the prefix, drops bare TLDs,
    deduplicates and sorts.

  blocked-by-sanctions.txt
    From freedomofdevelopers/fod (file "domains"). Strips leading dots,
    deduplicates and sorts.

Usage:
  python3 tools/update_lists.py           # sync, rewrite lists.json, log to CHANGELOG.md
  python3 tools/update_lists.py --check   # report differences only, write nothing

Safety: aborts if a rebuilt list is empty, or if a list would change by
more than 25% of its current size (pass --force to override) — that usually
means an upstream format change, not real-world change.
"""
import argparse
import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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
    },
    "blocked-from-outside.txt": {
        "source": "Chocolate4U/Iran-clash-rules (from bootmortis/iran-hosted-domains, official IR registries)",
        "source_url": IR_TXT_URL,
        "method": (
            "Release asset ir.txt: '+.'-prefixed entries with the prefix "
            "stripped; bare TLDs dropped; deduplicated; sorted."
        ),
    },
    "blocked-by-sanctions.txt": {
        "source": "freedomofdevelopers/fod",
        "source_url": FOD_URL,
        "method": "File 'domains': leading dots stripped; deduplicated; sorted.",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "blocked-sites-in-iran-sync"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read().decode("utf-8", errors="replace")


def build_blocked_in_iran(csv_text: str) -> tuple[list[str], str]:
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    months = sorted({r["month"] for r in rows if r["country_code"] == "IR"})
    if not months:
        raise ValueError("no IR rows in OONI dataset")
    latest = months[-1]
    out = set()
    for r in rows:
        if r["country_code"] != "IR" or r["month"] != latest:
            continue
        if int(r["measurements"]) >= 20 and float(r["confirmed_rate"]) >= 0.5:
            d = r["domain"].strip().lower()
            out.add(d[4:] if d.startswith("www.") else d)
    return sorted(out), latest


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
    ap.add_argument("--force", action="store_true", help="allow changes larger than 25%")
    args = ap.parse_args()

    today = datetime.now(timezone.utc).date().isoformat()
    print("Fetching upstream sources...")
    builders = {
        "list.txt": lambda: build_blocked_in_iran(fetch(OONI_CSV_URL)),
        "blocked-from-outside.txt": lambda: (build_from_outside(fetch(IR_TXT_URL)), None),
        "blocked-by-sanctions.txt": lambda: (build_sanctions(fetch(FOD_URL)), None),
    }

    meta = load_meta()
    meta_by_file = {e["file"]: e for e in meta.get("lists", [])}
    changed = []
    new_meta_lists = []

    for name, build in builders.items():
        new, data_period = build()
        old = read_current(name)
        if not new:
            print(f"ERROR: rebuilt {name} is empty — aborting, nothing written.")
            return 1
        added, removed = sorted(set(new) - set(old)), sorted(set(old) - set(new))
        delta = len(added) + len(removed)
        if old and delta > 0.25 * len(old) and not args.force:
            print(
                f"ERROR: {name} would change by {delta} entries "
                f"({len(old)} -> {len(new)}), over the 25% safety limit. "
                "Inspect the upstream source; rerun with --force if this is real."
            )
            return 1
        status = "unchanged" if new == old else f"+{len(added)} / -{len(removed)}"
        print(f"{name}: {len(old)} -> {len(new)} entries ({status})")

        entry = dict(meta_by_file.get(name, {}))
        entry.update(SOURCES[name])
        entry["file"] = name
        entry["entries"] = len(new)
        if data_period:
            entry["data_period"] = data_period
        if new != old:
            changed.append((name, len(old), len(new), len(added), len(removed)))
            entry["last_synced"] = today
        else:
            entry.setdefault("last_synced", today)
        new_meta_lists.append(entry)

        if new != old and not args.check:
            (ROOT / name).write_text("\n".join(new) + "\n", encoding="utf-8")

    if args.check:
        print("Check only — nothing written.")
        return 0

    meta["lists"] = new_meta_lists
    (ROOT / "lists.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if changed:
        changelog = ROOT / "CHANGELOG.md"
        marker = "<!-- new entries are inserted below this line -->"
        lines = [
            f"## {today} — automated sync",
            "",
        ]
        for name, old_n, new_n, a, r in changed:
            lines.append(f"- `{name}`: {old_n} → {new_n} entries (+{a} / −{r}).")
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
