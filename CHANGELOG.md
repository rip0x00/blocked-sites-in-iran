# Changelog | سابقه‌ی تغییرات

All notable changes to the lists and the project, newest first. Automated
syncs are appended by `tools/update_lists.py` and the weekly workflow.

همه‌ی تغییرات مهم لیست‌ها و پروژه، از تازه به قدیمی. همگام‌سازی‌های خودکار
توسط `tools/update_lists.py` و گردش‌کار هفتگی اینجا ثبت می‌شوند.

<!-- new entries are inserted below this line -->

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
