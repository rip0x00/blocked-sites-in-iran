#!/usr/bin/env python3
"""Validate the domain lists in this repository.

Checks every list file for:
  - one bare domain per line (lowercase, no scheme, no path, no wildcard)
  - at least one dot per entry (no bare TLDs)
  - valid domain labels
  - no duplicates
  - strict alphabetical order
  - no blank lines, no trailing whitespace, file ends with a newline
  - entry counts in lists.json match the actual files (when lists.json exists)

Usage: python3 tools/validate_lists.py [list-file ...]
Exit code 0 means every check passed.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LISTS = ["list.txt", "blocked-from-outside.txt", "blocked-by-sanctions.txt"]

LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def valid_domain(name: str) -> bool:
    if len(name) > 253 or "." not in name:
        return False
    return all(LABEL.match(part) for part in name.split("."))


def check_file(path: Path) -> list[str]:
    errors = []
    raw = path.read_bytes()
    if not raw:
        return [f"{path.name}: file is empty"]
    if not raw.endswith(b"\n"):
        errors.append(f"{path.name}: file does not end with a newline")
    lines = raw.decode("utf-8").splitlines()
    seen = set()
    for i, line in enumerate(lines, 1):
        if line != line.strip():
            errors.append(f"{path.name}:{i}: leading/trailing whitespace")
        if not line:
            errors.append(f"{path.name}:{i}: blank line")
            continue
        if line != line.lower():
            errors.append(f"{path.name}:{i}: not lowercase: {line!r}")
        if not valid_domain(line):
            errors.append(f"{path.name}:{i}: not a valid bare domain: {line!r}")
        if line in seen:
            errors.append(f"{path.name}:{i}: duplicate: {line!r}")
        seen.add(line)
    if lines != sorted(lines):
        errors.append(f"{path.name}: entries are not in alphabetical order")
    return errors


def main() -> int:
    names = sys.argv[1:] or DEFAULT_LISTS
    errors = []
    counts = {}
    for name in names:
        path = ROOT / name
        if not path.exists():
            errors.append(f"{name}: file not found")
            continue
        counts[name] = len(path.read_text(encoding="utf-8").splitlines())
        errors.extend(check_file(path))

    meta_path = ROOT / "lists.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for entry in meta.get("lists", []):
            fname, declared = entry.get("file"), entry.get("entries")
            if fname in counts and declared != counts[fname]:
                errors.append(
                    f"lists.json: {fname} declares {declared} entries "
                    f"but the file has {counts[fname]}"
                )

    for name, count in counts.items():
        print(f"{name}: {count} entries")
    if errors:
        print("\nVALIDATION FAILED:")
        for err in errors:
            print(" -", err)
        return 1
    print("All lists valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
