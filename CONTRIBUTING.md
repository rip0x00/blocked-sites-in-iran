# Contributing

Thanks for helping keep these lists accurate. Most contributions are data
reports, not code — both are welcome.

## Reporting a wrong or missing domain

Open an issue using the matching template:

- **Incorrect entry** — a domain is listed but should not be.
- **Missing entry** — a domain is blocked (or blocks Iran) but is not listed.
- **Source problem** — an upstream source is down, changed format, or wrong.

Evidence matters more than volume. For every report, please include:

- the exact domain,
- what you tested (the site itself? a specific page? DNS? HTTPS?),
- where you tested from (inside Iran / which country, and the ISP if you
  know it),
- when you tested (date),
- what you observed (block page, timeout, geo-block message, HTTP status…).

A report that just says "this site works for me" without the details above
is hard to act on: blocking differs per ISP, per protocol and over time.

## Running the checks locally

Requirements: Python 3.10 or newer. No third-party dependencies — the tools
use only the standard library.

```bash
python3 -m venv .venv
.venv/bin/python tools/validate_lists.py            # format / order / counts
.venv/bin/python -m unittest discover -s tests -v   # unit tests
.venv/bin/python tools/update_lists.py --check      # dry-run sync, writes nothing
```

All three must pass before a pull request is merged. CI runs the validator
and the unit tests on every push and pull request.

## Pull requests

- The weekly sync workflow opens its own PRs from a `sync/<date>` branch —
  review the diff and merge, or close it if the change looks wrong.
- Manual PRs are welcome: for code, for docs, and for documented data fixes.
- Keep the English and Persian sections of the README in sync when you edit
  one of them.
- If your PR changes a list file, update `lists.json` and `CHANGELOG.md` in
  the same PR (running `tools/update_lists.py` does this for source-driven
  changes).

## Removal policy

A domain is removed when:

- its upstream source stops listing it (the next sync then drops it), or
- credible evidence shows the entry is wrong — for example repeated tests
  from inside Iran showing a `list.txt` domain is reachable and unfiltered,
  or proof that a sanctions-list service has reopened to Iranian users.

Removals for the second reason need the same evidence standard as additions:
what was tested, from where, and when.

## Releases

Dated snapshots are published as GitHub releases (`vYYYY.MM.DD`). Attach the
exact raw upstream inputs used to build the snapshot as release assets, so
any release can be rebuilt and audited later: `lists.json` records each
input's SHA-256 and its upstream commit or release tag (`source_ref`).

---

## فارسی — مشارکت

بیشتر مشارکت‌ها گزارش داده‌اند، نه کد. برای گزارش دامنه‌ی اشتباه یا جاافتاده،
از قالب‌های ایشو استفاده کنید و این‌ها را بنویسید: دامنه‌ی دقیق، چه چیزی را
تست کردید، از کجا (داخل ایران یا کدام کشور و کدام ISP)، چه تاریخی، و چه
مشاهده کردید (صفحه‌ی فیلترینگ، تایم‌اوت، پیام جئوبلاک و…).

برای اجرای بررسی‌ها به Python 3.10 یا بالاتر نیاز است و هیچ وابستگی خارجی‌ای
وجود ندارد:

```bash
.venv/bin/python tools/validate_lists.py
.venv/bin/python -m unittest discover -s tests -v
```

دامنه وقتی حذف می‌شود که منبع بالادستی‌اش آن را حذف کرده باشد، یا شواهد
معتبر (با همان جزئیات بالا) نشان دهد ورودی اشتباه است.
