# Blocked Sites in Iran | سایت‌های فیلترشده در ایران

Lists of blocked domains around Iran, from three directions — one bare domain per line in every file, sorted alphabetically.

لیست دامنه‌های مسدودشده‌ی مرتبط با ایران، از سه جهت — در همه‌ی فایل‌ها هر دامنه در یک خط، به ترتیب الفبا.

[![Validate lists](https://github.com/rip0x00/blocked-sites-in-iran/actions/workflows/validate.yml/badge.svg)](https://github.com/rip0x00/blocked-sites-in-iran/actions/workflows/validate.yml)

**Contact / تماس:** [Telegram — @rip00](https://t.me/rip00)

## Files | فایل‌ها

| File | Domains | What it is |
|---|---|---|
| [`list.txt`](list.txt) | 773 | Domains **blocked inside Iran** by Iranian filtering |
| [`blocked-from-outside.txt`](blocked-from-outside.txt) | 57,557 | **Iranian** domains hosted in Iran (official registries) — **not** individually tested for reachability from abroad; see the note under its section |
| [`blocked-by-sanctions.txt`](blocked-by-sanctions.txt) | 605 | **Foreign** services that block Iranian IPs themselves (sanctions / geo-blocking) |

| فایل | دامنه | توضیح |
|---|---|---|
| [`list.txt`](list.txt) | ۷۷۳ | دامنه‌هایی که **داخل ایران** فیلترند |
| [`blocked-from-outside.txt`](blocked-from-outside.txt) | ۵۷٬۵۵۷ | دامنه‌های **ایرانی** میزبانی‌شده در ایران (از فهرست‌های رسمی) — تک‌تک از خارج **تست نشده‌اند**؛ یادداشت زیر بخش خودش را ببینید |
| [`blocked-by-sanctions.txt`](blocked-by-sanctions.txt) | ۶۰۵ | سرویس‌های **خارجی** که خودشان آی‌پی ایران را بلاک کرده‌اند (تحریم / جئوبلاک) |

---

## English

### `list.txt` — blocked in Iran

Iran does not publish an official blocklist, so this list is built from real measurements instead of rumours:

- Data comes from [OONI](https://ooni.org) (Open Observatory of Network Interference) probe measurements taken inside Iran, compiled by the [blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) project.
- A domain is included when, in the most recent month of data (October 2026), OONI **confirmed** blocking (a block page or another censorship fingerprint was observed) in at least **50%** of at least **20** measurements.
- A domain missing from the list is usually **untested**, not necessarily unblocked.

### `blocked-from-outside.txt` — Iranian sites blocked from abroad

Domains hosted in Iran, gathered from official Iranian domain registries (ITO / Enamad) by the [iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) project, in the cleaned routing-list form maintained by [Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules). Iranian banks, government services, payment gateways and many local platforms in this set refuse non-Iranian IPs, and during national internet restrictions these are practically the only Iranian services still reachable — from inside.

> **What this list is — and is not:** this is primarily a list of domains **hosted in Iran**, taken from the official domain registries. It is **not** the result of testing each domain's reachability from abroad, and **not every domain in it necessarily blocks foreign IPs**. Many do — banks, government services and payment gateways especially — but read this file as "Iran-hosted domains", not as a measured, per-domain blocklist.

### `blocked-by-sanctions.txt` — services that block Iran

The other direction of the wall: foreign (mostly US) services that geo-block Iranian users on their own side because of sanctions, compiled by [freedomofdevelopers](https://github.com/freedomofdevelopers/fod). Developer-focused and community-maintained — individual entries age: some services later obtained licences and reopened to Iran (for example GitHub), so treat an entry as "has blocked Iran" rather than a live guarantee.

**Status semantics:** every entry in this list is **historical / community-reported** — the service has blocked Iran at some point; current blocking is **not** guaranteed and is not independently confirmed here.

### List status and updates

| File | Entries | Source | Last synced |
|---|---|---|---|
| `list.txt` | 773 | OONI measurements (via Yuix-Networks/blocked-sites-dataset), data month 2026-10 | 2026-11-19 |
| `blocked-from-outside.txt` | 57,557 | Chocolate4U/Iran-clash-rules (from bootmortis/iran-hosted-domains) | 2026-11-19 |
| `blocked-by-sanctions.txt` | 605 | freedomofdevelopers/fod (community-maintained; entries age) | 2026-11-19 |

The same metadata lives in machine-readable form in [`lists.json`](lists.json), and every change is recorded in [`CHANGELOG.md`](CHANGELOG.md).

How the lists stay current:

- [`tools/update_lists.py`](tools/update_lists.py) rebuilds all three lists from the upstream sources above. It fetches and builds everything in memory first and writes files only when every check has passed, so a failed run changes nothing. It refuses to publish a list that comes back empty or changes by more than 25% at once, which would mean an upstream format change rather than real-world change.
- A GitHub Actions workflow re-runs that sync **weekly** and opens a **pull request** with the result (it never pushes to `main` directly); a human reviews and merges it. [`tools/validate_lists.py`](tools/validate_lists.py) checks format, duplicates, ordering and the `lists.json` counts, and the unit tests in [`tests/`](tests/) run in CI on every push and pull request.
- `lists.json` also records, for each list, the **SHA-256 of the raw upstream snapshot** it was built from and the exact **retrieval time** — so any published list can be traced to the precise source bytes it came from. Per-domain OONI evidence (measurements and confirmed rate per domain) is kept in [`data/domains.jsonl`](data/domains.jsonl).
- Ready-made consumer outputs live in [`dist/`](dist/): every list as JSON and CSV, plus AdGuard, dnsmasq, hosts, Clash, Surge and sing-box formats, generated automatically from the lists by [`tools/build_dist.py`](tools/build_dist.py) on every sync; [`dist/manifest.json`](dist/manifest.json) records the SHA-256 of every generated file. Structured sanctions records — one JSON object per domain, status `historical` — are in [`data/sanctions.jsonl`](data/sanctions.jsonl).
- "Last synced" is the date a list's contents were last rebuilt from its source — for the sanctions list especially, a sync date is not a per-entry guarantee: an entry means the service has blocked Iran at some point, not that it necessarily still does.

### What this is not

- This is **not** a VPN, proxy, or circumvention tool — it is data *about* blocking, not a way around it.
- This is **not** an official government list; Iran publishes no official blocklist.
- A domain being **absent** from a list does **not** mean it is reachable — it usually means it was never measured or never listed by a source.
- A domain being **present** is a snapshot from measurement or source data for the stated period — **not** a live connectivity test from your network, your ISP, or right now.

### Definitions

- **Confirmed blocked** (`list.txt`): OONI measurements from inside Iran, in the latest data month, show confirmed blocking (a block page or another censorship fingerprint) in at least **50%** of at least **20** measurements.
- **Historical sanction** (`blocked-by-sanctions.txt`): a community source reports that the service blocks — or has blocked — Iranian users. Its current status is not independently confirmed.
- **Iran-hosted** (`blocked-from-outside.txt`): the source registries classify the domain as hosted in Iran. This is a hosting classification, **not** a reachability measurement from abroad.

### IDN and subdomain policy

- The lists are **ASCII / Punycode**, exactly as published by the sources: internationalized names appear in their `xn--` form, never as Unicode. The validator accepts ASCII domains only.
- Subdomains are kept as **separate entries**, exactly as measured or listed. A root domain does **not** automatically cover its subdomains, and a blocked subdomain does not imply its root is blocked.
- The only normalization anywhere is in `list.txt`, where a leading `www.` is stripped during the build. Every other subdomain (`m.`, `api.`, …) is kept exactly as-is.

### Development

Run everything from a clean environment:

```bash
python3 -m venv .venv
.venv/bin/python tools/update_lists.py --check
.venv/bin/python tools/validate_lists.py
.venv/bin/python -m unittest discover -s tests -v
```

- Requirements: **Python 3.10+** and **no third-party dependencies** — standard library only.
- Network behaviour of the update script: 60-second timeout per request; up to 3 attempts with backoff (2s, then 5s) on network errors and HTTP 5xx; HTTP 4xx fails immediately. Exit codes: `0` success, `1` source-data problem (empty or malformed source, or a change over 25% without `--force`), `2` network failure after all retries. A failed run writes nothing.

### Notes

- Blocking changes over time on all three sides. These lists are snapshots, not permanent truths.
- Found something wrong or missing? Open an issue or a pull request — or message me on Telegram: https://t.me/rip00

### Credits

- Measurement data: [OONI](https://ooni.org), compiled by [Yuix-Networks/blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) — CC BY-NC-SA 4.0.
- Iranian domains: [bootmortis/iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) and [Chocolate4U/Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules).
- Sanctions list: [freedomofdevelopers/fod](https://github.com/freedomofdevelopers/fod).
- Format inspired by [wpzzz/blocked-sites-in-south-korea](https://github.com/wpzzz/blocked-sites-in-south-korea).
- Licenses: the code in this repository (tools, tests, workflows) is MIT — see [`LICENSE`](LICENSE). The lists themselves are data under CC BY-NC-SA 4.0 — see [`DATA-LICENSE.md`](DATA-LICENSE.md) and [`NOTICE`](NOTICE).

---

## فارسی

### `list.txt` — فیلترشده در ایران

ایران هیچ لیست رسمی و عمومی‌ای از سایت‌های فیلترشده منتشر نمی‌کند؛ برای همین این لیست به‌جای شایعه و حدس، از روی اندازه‌گیری واقعی ساخته شده است:

- داده‌ها از اندازه‌گیری‌های [OONI](https://ooni.org) (رصدخانه‌ی باز تداخل در شبکه) از داخل ایران می‌آید که پروژه‌ی [blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) آن‌ها را گردآوری کرده است.
- یک دامنه وقتی وارد لیست می‌شود که در تازه‌ترین ماه داده‌ها (اکتبر ۲۰۲۶)، در دست‌کم **۵۰٪** از حداقل **۲۰** اندازه‌گیری، فیلتر بودنش **تأیید** شده باشد (صفحه‌ی فیلترینگ یا اثر انگشت سانسور دیده شده باشد).
- نبودن یک دامنه در لیست معمولاً یعنی **تست نشده**، نه اینکه حتماً باز باشد.

### `blocked-from-outside.txt` — سایت‌های ایرانیِ مسدود از خارج

دامنه‌های میزبانی‌شده در ایران، گردآوری‌شده از فهرست‌های رسمی دامنه‌های ایرانی (سازمان فناوری اطلاعات / اینماد) توسط پروژه‌ی [iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) و در قالب تمیزشده‌ی [Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules). بانک‌ها، سرویس‌های دولتی، درگاه‌های پرداخت و خیلی از پلتفرم‌های داخلیِ این لیست آی‌پی غیرایرانی را قبول نمی‌کنند و در دوره‌های محدودیت اینترنت ملی هم عملاً فقط همین‌ها — از داخل — در دسترس می‌مانند.

> **این لیست چیست و چه چیزی نیست:** این فهرست عمدتاً فهرست دامنه‌های **میزبانی‌شده در ایران** است که از فهرست‌های رسمی دامنه‌ها گرفته شده است. نتیجه‌ی تستِ تک‌تک دامنه‌ها از خارج از کشور **نیست** و **همه‌ی دامنه‌های آن لزوماً آی‌پی خارجی را بلاک نمی‌کنند**. خیلی‌هایشان بلاک می‌کنند — مخصوصاً بانک‌ها، سرویس‌های دولتی و درگاه‌های پرداخت — اما این فایل را «دامنه‌های میزبانی‌شده در ایران» بدانید، نه فهرست اندازه‌گیری‌شده‌ی مسدودیتِ تک‌تک دامنه‌ها.

### `blocked-by-sanctions.txt` — سرویس‌هایی که ایران را بلاک کرده‌اند

جهت برعکس دیوار: سرویس‌های خارجی (بیشتر آمریکایی) که به‌خاطر تحریم‌ها خودشان کاربر ایرانی را جئوبلاک می‌کنند؛ گردآوری‌شده توسط [freedomofdevelopers](https://github.com/freedomofdevelopers/fod). این لیست جامعه‌محور و توسعه‌دهنده‌محور است و تک‌تک موردهایش ممکن است کهنه شده باشد: بعضی سرویس‌ها بعداً مجوز گرفتند و به روی ایران باز شدند (مثلاً گیت‌هاب) — پس هر مورد را «سابقه‌ی بلاک کردن ایران» بدان، نه تضمین لحظه‌ای.

**معنای وضعیت:** همه‌ی موردهای این لیست **تاریخی / گزارش‌شده توسط جامعه** هستند — یعنی سرویس در مقطعی ایران را بلاک کرده است؛ بلاک بودنِ فعلی‌اش **تضمین‌شده نیست** و اینجا به‌طور مستقل تأیید نشده است.

### وضعیت و به‌روزرسانی لیست‌ها

| فایل | دامنه | منبع | آخرین همگام‌سازی |
|---|---|---|---|
| `list.txt` | ۷۷۳ | اندازه‌گیری‌های OONI (از طریق Yuix-Networks/blocked-sites-dataset)، داده‌ی ماه ۲۰۲۶-۱۰ | ۲۰۲۶-۱۱-۱۹ |
| `blocked-from-outside.txt` | ۵۷٬۵۵۷ | ‏Chocolate4U/Iran-clash-rules (از روی bootmortis/iran-hosted-domains) | ۲۰۲۶-۱۱-۱۹ |
| `blocked-by-sanctions.txt` | ۶۰۵ | ‏freedomofdevelopers/fod (جامعه‌محور؛ موردهایش کهنه می‌شود) | ۲۰۲۶-۱۱-۱۹ |

همین اطلاعات به‌صورت ماشین‌خوان در [`lists.json`](lists.json) هست و همه‌ی تغییرات در [`CHANGELOG.md`](CHANGELOG.md) ثبت می‌شود.

لیست‌ها چطور تازه می‌مانند:

- اسکریپت [`tools/update_lists.py`](tools/update_lists.py) هر سه لیست را از منابع بالا از نو می‌سازد؛ اول همه‌ی منابع را می‌گیرد و همه‌چیز را در حافظه می‌سازد و فقط وقتی همه‌ی بررسی‌ها رد شدند فایل‌ها را می‌نویسد، پس اجرای ناموفق هیچ تغییری ایجاد نمی‌کند. اگر لیستی خالی برگردد یا یک‌باره بیش از ۲۵٪ تغییر کند (که یعنی قالب منبع عوض شده، نه دنیای واقعی) جلوی انتشارش را می‌گیرد.
- یک گردش‌کار GitHub Actions این همگام‌سازی را **هفته‌ای یک‌بار** خودکار انجام می‌دهد و نتیجه را به‌صورت **پول‌ریکوئست** باز می‌کند (مستقیم روی `main` پوش نمی‌کند) تا انسان بازبینی و مرج کند؛ اسکریپت [`tools/validate_lists.py`](tools/validate_lists.py) در هر پوش و پول‌ریکوئست قالب، تکراری‌نبودن، ترتیب و شمارش `lists.json` را بررسی می‌کند و تست‌های واحدِ [`tests/`](tests/) هم در CI اجرا می‌شوند.
- فایل `lists.json` برای هر لیست **SHA-256 داده‌ی خام منبع** و **زمان دقیق دریافت** را هم ثبت می‌کند تا هر لیست منتشرشده به بایت‌های دقیق منبعش قابل ردیابی باشد. شواهد تک‌تک دامنه‌های OONI (تعداد اندازه‌گیری و نرخ تأیید هر دامنه) در [`data/domains.jsonl`](data/domains.jsonl) نگه داشته می‌شود.
- خروجی‌های آماده‌ی مصرف در [`dist/`](dist/) هستند: هر لیست به‌صورت JSON و CSV و در قالب‌های AdGuard، ‏dnsmasq، ‏hosts، ‏Clash، ‏Surge و sing-box، که در هر همگام‌سازی به‌صورت خودکار توسط [`tools/build_dist.py`](tools/build_dist.py) از روی لیست‌ها ساخته می‌شوند؛ [`dist/manifest.json`](dist/manifest.json) هش SHA-256 همه‌ی فایل‌های ساخته‌شده را ثبت می‌کند. رکوردهای ساخت‌یافته‌ی لیست تحریم‌ها — برای هر دامنه یک آبجکت JSON با وضعیت `historical` — در [`data/sanctions.jsonl`](data/sanctions.jsonl) است.
- «آخرین همگام‌سازی» تاریخی است که محتوای لیست آخرین بار از منبعش بازسازی شده — مخصوصاً در لیست تحریم‌ها، این تاریخ تضمین تک‌تک موردها نیست: بودن یک سرویس در لیست یعنی زمانی ایران را بلاک کرده، نه اینکه حتماً هنوز هم بلاک می‌کند.

### این پروژه چه چیزی نیست

- این پروژه VPN، پروکسی یا ابزار دورزدن فیلترینگ **نیست** — داده‌ای *درباره‌ی* مسدودیت است، نه راه عبور از آن.
- فهرست رسمی دولت **نیست**؛ ایران هیچ فهرست رسمی‌ای از سایت‌های فیلترشده منتشر نمی‌کند.
- **نبودن** یک دامنه در لیست به‌معنای باز بودن آن **نیست** — معمولاً یعنی هیچ‌وقت اندازه‌گیری نشده یا در هیچ منبعی نیامده است.
- **بودن** یک دامنه عکس لحظه‌ای از داده‌های اندازه‌گیری یا منبع در دوره‌ی ذکرشده است — تست زنده‌ی اتصال از شبکه یا ISP شما و در همین لحظه **نیست**.

### تعریف‌ها

- **فیلترشده‌ی تأییدشده** (`list.txt`): اندازه‌گیری‌های OONI از داخل ایران در تازه‌ترین ماه داده‌ها، در دست‌کم **۵۰٪** از حداقل **۲۰** اندازه‌گیری، فیلترینگ را تأیید کرده‌اند (صفحه‌ی فیلترینگ یا اثر انگشت سانسور دیده شده است).
- **تحریم تاریخی** (`blocked-by-sanctions.txt`): یک منبع جامعه‌محور گزارش کرده که سرویس کاربران ایرانی را بلاک می‌کند — یا قبلاً بلاک کرده است. وضعیت فعلی‌اش به‌طور مستقل تأیید نشده است.
- **میزبانی‌شده در ایران** (`blocked-from-outside.txt`): فهرست‌های منبع دامنه را میزبانی‌شده در ایران طبقه‌بندی می‌کنند. این طبقه‌بندیِ میزبانی است، **نه** اندازه‌گیری دسترسی از خارج.

### سیاست IDN و زیردامنه‌ها

- لیست‌ها **ASCII / Punycode** هستند، دقیقاً همان‌طور که منابع منتشر می‌کنند: نام‌های بین‌المللی به شکل `xn--` می‌آیند، نه به‌صورت Unicode. اعتبارسنج فقط دامنه‌های ASCII را قبول می‌کند.
- زیردامنه‌ها **ورودی‌های جدا** نگه داشته می‌شوند، دقیقاً همان‌طور که اندازه‌گیری یا فهرست شده‌اند. دامنه‌ی ریشه به‌صورت خودکار زیردامنه‌هایش را پوشش **نمی‌دهد** و فیلتر بودن یک زیردامنه هم به‌معنای فیلتر بودن ریشه نیست.
- تنها نرمال‌سازی در `list.txt` است که هنگام ساخت، `www.` ابتدای دامنه حذف می‌شود. هر زیردامنه‌ی دیگری (`m.` و `api.` و…) دقیقاً همان‌طور که هست می‌ماند.

### توسعه

اجرا در محیط تمیز:

```bash
python3 -m venv .venv
.venv/bin/python tools/update_lists.py --check
.venv/bin/python tools/validate_lists.py
.venv/bin/python -m unittest discover -s tests -v
```

- نیازمندی: **Python 3.10 به بالا** و **بدون هیچ وابستگی خارجی** — فقط کتابخانه‌ی استاندارد.
- رفتار شبکه‌ی اسکریپت به‌روزرسانی: تایم‌اوت ۶۰ ثانیه برای هر درخواست؛ تا ۳ تلاش با مکث پلکانی (۲ و بعد ۵ ثانیه) برای خطاهای شبکه و HTTP 5xx؛ خطاهای HTTP 4xx فوری متوقف می‌شوند. کدهای خروج: `0` موفقیت، `1` مشکل داده‌ی منبع (منبع خالی یا ناقص، یا تغییر بیش از ۲۵٪ بدون `--force`)، `2` شکست شبکه بعد از همه‌ی تلاش‌ها. اجرای ناموفق هیچ فایلی را تغییر نمی‌دهد.

### نکات

- فیلترینگ از هر سه طرف دائماً عوض می‌شود؛ این لیست‌ها عکس لحظه‌ای‌اند، نه حقیقت همیشگی.
- چیزی اشتباه است یا جا افتاده؟ ایشو یا پول‌ریکوئست بفرست — یا در تلگرام پیام بده: https://t.me/rip00

### اعتبار

- داده‌های اندازه‌گیری: [OONI](https://ooni.org)، گردآوری‌شده توسط [Yuix-Networks/blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) — با مجوز CC BY-NC-SA 4.0.
- دامنه‌های ایرانی: [bootmortis/iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) و [Chocolate4U/Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules).
- لیست تحریم: [freedomofdevelopers/fod](https://github.com/freedomofdevelopers/fod).
- فرمت پروژه با الهام از [wpzzz/blocked-sites-in-south-korea](https://github.com/wpzzz/blocked-sites-in-south-korea) است.
- مجوزها: کد این مخزن (ابزارها، تست‌ها، گردش‌کارها) با مجوز MIT است — [`LICENSE`](LICENSE) را ببینید. خود لیست‌ها داده‌اند و زیر مجوز CC BY-NC-SA 4.0 هستند — [`DATA-LICENSE.md`](DATA-LICENSE.md) و [`NOTICE`](NOTICE) را ببینید.
