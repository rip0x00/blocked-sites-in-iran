# Changelog | سابقه‌ی تغییرات

All notable changes to the lists and the project, newest first. Automated
syncs are appended by `tools/update_lists.py` and the weekly workflow.

همه‌ی تغییرات مهم لیست‌ها و پروژه، از تازه به قدیمی. همگام‌سازی‌های خودکار
توسط `tools/update_lists.py` و گردش‌کار هفتگی اینجا ثبت می‌شوند.

<!-- new entries are inserted below this line -->

## 2026-11-20 — Hardening: tests, licenses, metadata v2

- `tools/update_lists.py` v2.0.0: all-or-nothing writes (all sources are
  fetched and built in memory before anything is written, so a failed run
  changes nothing), network retry with backoff (3 attempts, 60s timeout),
  documented exit codes (0 ok, 1 source-data problem, 2 network failure).
- `lists.json` metadata v2 (schema_version 1): each list now records the
  SHA-256 of the raw upstream snapshot, the exact retrieval time, and a
  `status_semantics` statement of what an entry does and does not mean.
- Added `data/domains.jsonl`: per-domain OONI evidence for `list.txt`
  (measurements and confirmed rate per domain, from the source CSV).
- Added `tools/build_dist.py` and `dist/`: ready-made consumer outputs
  for every list (JSON, CSV, AdGuard, dnsmasq, hosts, Clash, Surge,
  sing-box), regenerated on each sync, with `dist/manifest.json`
  recording the SHA-256 of every generated file.
- Added `data/sanctions.jsonl`: structured per-domain records for the
  sanctions list (status `historical`, direction, source, confidence).
  Update generator is now v2.1.0.
- Added unit tests in `tests/` for the validator and the update builders,
  the delta guard, and malformed-source handling; CI runs them on every
  push and pull request.
- The weekly sync workflow now opens a pull request instead of pushing to
  `main` directly.
- Added `LICENSE` (code, MIT), `DATA-LICENSE.md` (data, CC BY-NC-SA 4.0)
  and `NOTICE` with upstream attributions.
- Added `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`,
  `CODE_OF_CONDUCT.md`, issue templates, a pull request template,
  Dependabot for GitHub Actions, and `STATUS.md`.
- README clarifications (English + Persian): explicit semantics of the
  Iran-hosted list (registry data, not per-domain reachability testing),
  historical status of the sanctions list, "What this is not", definitions
  rubric, IDN/subdomain policy, and a development section with the
  clean-environment commands. No list contents changed in this entry.

## 2026-11-20 — tooling, metadata and validation

- Added `lists.json`: per-list source, method, entry count and last-sync date.
- Added `tools/update_lists.py`: rebuilds all three lists from their upstream
  sources (verified to reproduce the published lists exactly) with a safety
  limit against large unexpected changes.
- Added `tools/validate_lists.py` and a CI workflow that validates the lists
  on every push and pull request.
- Added a weekly GitHub Actions workflow that syncs the lists automatically
  and records the change here.
- README: added a list-status section (source and last sync per list, in
  English and Persian). No list contents changed in this entry.

## 2026-11-19 — two more lists

- Added `blocked-from-outside.txt`: 57,557 Iranian-hosted domains.
- Added `blocked-by-sanctions.txt`: 605 foreign services that block Iran.
- README rewritten bilingually (English / Persian) with sources, method and
  limitations for each list.

## 2026-11-19 — initial release

- `list.txt`: 773 domains confirmed blocked inside Iran — OONI measurements
  from October 2026, at least 20 measurements per domain and confirmed
  blocking in at least 50% of them.
