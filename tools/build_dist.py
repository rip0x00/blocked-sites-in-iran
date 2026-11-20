#!/usr/bin/env python3
"""Build the ready-made consumer outputs in dist/ from the three lists.

For each list, dist/ gets the same domains in the formats tools actually
consume:

  <base>.json          JSON array of the domains
  <base>.csv           "domain" header, then one domain per line
  <base>.adguard.txt   ||<domain>^ rules ("!" comment header)
  <base>.dnsmasq.conf  server=/<domain>/ lines ("#" comment header)
  <base>.hosts         0.0.0.0 <domain> lines ("#" comment header)
  <base>.clash.yaml    Clash payload rules (DOMAIN-SUFFIX)
  <base>.surge.conf    DOMAIN-SUFFIX,<domain> lines ("#" comment header)
  <base>.sing-box.json sing-box rule-set (domain_suffix)

plus dist/manifest.json recording the entry count, byte size and SHA-256
of every generated file.

The per-format files are deterministic: they contain no timestamps. Only
manifest.json carries generated_at.

Usage:
  python3 tools/build_dist.py    # rebuild dist/ from the on-disk lists

tools/update_lists.py calls build_all() with the freshly built in-memory
lists during its build phase, so dist/ is regenerated in the same
all-or-nothing write phase as the lists themselves.

Requirements: Python >= 3.10, standard library only.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Source list file -> output base name, header title and semantics line.
LIST_SPECS = {
    "list.txt": {
        "base": "blocked-in-iran",
        "title": "Blocked in Iran",
        "semantics": (
            "Confirmed blocked in Iran in the data period (OONI measurements)."
        ),
    },
    "blocked-from-outside.txt": {
        "base": "iran-hosted",
        "title": "Iran-hosted domains",
        "semantics": (
            "Iran-hosted domains (official registries). Not individually "
            "tested for reachability from outside Iran."
        ),
    },
    "blocked-by-sanctions.txt": {
        "base": "sanctions",
        "title": "Services that block Iran (sanctions)",
        "semantics": (
            "Historical / community-reported: the service has blocked Iran "
            "at some point; current blocking is not guaranteed."
        ),
    },
}


def _header(spec: dict, marker: str) -> str:
    return f"{marker} {spec['title']}\n{marker} {spec['semantics']}\n"


def _render(spec: dict, domains: list[str]) -> dict[str, bytes]:
    """Render one list into {filename: bytes} (no manifest, no dist/ prefix)."""
    base = spec["base"]
    out: dict[str, bytes] = {}

    out[f"{base}.json"] = (
        json.dumps(domains, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")

    out[f"{base}.csv"] = (
        "domain\n" + "".join(f"{d}\n" for d in domains)
    ).encode("utf-8")

    out[f"{base}.adguard.txt"] = (
        _header(spec, "!")
        + "".join(f"||{d}^\n" for d in domains)
    ).encode("utf-8")

    out[f"{base}.dnsmasq.conf"] = (
        _header(spec, "#")
        + "".join(f"server=/{d}/\n" for d in domains)
    ).encode("utf-8")

    out[f"{base}.hosts"] = (
        _header(spec, "#")
        + "".join(f"0.0.0.0 {d}\n" for d in domains)
    ).encode("utf-8")

    out[f"{base}.clash.yaml"] = (
        "payload:\n" + "".join(f"  - 'DOMAIN-SUFFIX,{d}'\n" for d in domains)
    ).encode("utf-8")

    out[f"{base}.surge.conf"] = (
        _header(spec, "#")
        + "".join(f"DOMAIN-SUFFIX,{d}\n" for d in domains)
    ).encode("utf-8")

    sing_box = {"version": 1, "rules": [{"domain_suffix": list(domains)}]}
    out[f"{base}.sing-box.json"] = (
        json.dumps(sing_box, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")

    return out


def build_all(lists: dict, generated_at: str) -> dict[str, bytes]:
    """Pure builder: {source filename: [domains]} -> {"dist/<file>": bytes}.

    Includes dist/manifest.json. Raises ValueError if a list is missing.
    """
    files: dict[str, bytes] = {}
    manifest_files: dict[str, dict] = {}
    for name, spec in LIST_SPECS.items():
        if name not in lists:
            raise ValueError(f"build_all: missing list {name!r}")
        domains = list(lists[name])
        for filename, data in _render(spec, domains).items():
            files[f"dist/{filename}"] = data
            manifest_files[filename] = {
                "entries": len(domains),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
    manifest = {
        "generated_at": generated_at,
        "generator": "tools/build_dist.py",
        "files": manifest_files,
    }
    files["dist/manifest.json"] = (
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    return files


def read_lists(root: Path) -> dict[str, list[str]]:
    """Read the three source lists (and lists.json) from a repo checkout.

    If lists.json is present, its per-list entry counts are checked
    against the .txt files; a mismatch raises ValueError.
    """
    lists = {}
    for name in LIST_SPECS:
        path = root / name
        if not path.exists():
            raise ValueError(f"missing list file: {path}")
        lists[name] = path.read_text(encoding="utf-8").splitlines()
    meta_path = root / "lists.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for entry in meta.get("lists", []):
            fname = entry.get("file")
            if fname in lists and entry.get("entries") != len(lists[fname]):
                raise ValueError(
                    f"lists.json says {fname} has {entry.get('entries')} "
                    f"entries but the file has {len(lists[fname])}"
                )
    return lists


def build_dist(repo_root, generated_at: str = None) -> dict[str, bytes]:
    """Read the lists under repo_root, build dist/ and write it to disk.

    Returns the {"dist/<file>": bytes} dict that was written.
    """
    root = Path(repo_root)
    if generated_at is None:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = build_all(read_lists(root), generated_at)
    for rel, data in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Rebuild dist/ from the lists.")
    ap.add_argument(
        "--root",
        default=str(ROOT),
        help="repository root (default: the parent of this script's folder)",
    )
    args = ap.parse_args()
    try:
        files = build_dist(args.root)
    except (ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    manifest = json.loads(files["dist/manifest.json"].decode("utf-8"))
    print(
        f"dist/: wrote {len(files)} files "
        f"({len(manifest['files'])} outputs + manifest.json)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
