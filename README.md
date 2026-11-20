# Blocked Sites in Iran | سایت‌های فیلترشده در ایران

Lists of blocked domains around Iran, from three directions — one bare domain per line in every file, sorted alphabetically.

لیست دامنه‌های مسدودشده‌ی مرتبط با ایران، از سه جهت — در همه‌ی فایل‌ها هر دامنه در یک خط، به ترتیب الفبا.

**Contact / تماس:** [Telegram — @rip00](https://t.me/rip00)

## Files | فایل‌ها

| File | Domains | What it is |
|---|---|---|
| [`list.txt`](list.txt) | 773 | Domains **blocked inside Iran** by Iranian filtering |
| [`blocked-from-outside.txt`](blocked-from-outside.txt) | 57,557 | **Iranian** domains hosted in Iran — most block foreign IPs or are only reachable from an Iranian IP |
| [`blocked-by-sanctions.txt`](blocked-by-sanctions.txt) | 605 | **Foreign** services that block Iranian IPs themselves (sanctions / geo-blocking) |

| فایل | دامنه | توضیح |
|---|---|---|
| [`list.txt`](list.txt) | ۷۷۳ | دامنه‌هایی که **داخل ایران** فیلترند |
| [`blocked-from-outside.txt`](blocked-from-outside.txt) | ۵۷٬۵۵۷ | دامنه‌های **ایرانی** میزبانی‌شده در ایران — بیشترشان آی‌پی خارجی را بلاک می‌کنند یا فقط با آی‌پی ایران باز می‌شوند |
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

### `blocked-by-sanctions.txt` — services that block Iran

The other direction of the wall: foreign (mostly US) services that geo-block Iranian users on their own side because of sanctions, compiled by [freedomofdevelopers](https://github.com/freedomofdevelopers/fod). Developer-focused and community-maintained — individual entries age: some services later obtained licences and reopened to Iran (for example GitHub), so treat an entry as "has blocked Iran" rather than a live guarantee.

### List status and updates

| File | Entries | Source | Last synced |
|---|---|---|---|
| `list.txt` | 773 | OONI measurements (via Yuix-Networks/blocked-sites-dataset), data month 2026-10 | 2026-11-19 |
| `blocked-from-outside.txt` | 57,557 | Chocolate4U/Iran-clash-rules (from bootmortis/iran-hosted-domains) | 2026-11-19 |
| `blocked-by-sanctions.txt` | 605 | freedomofdevelopers/fod (community-maintained; entries age) | 2026-11-19 |

The same metadata lives in machine-readable form in [`lists.json`](lists.json), and every change is recorded in [`CHANGELOG.md`](CHANGELOG.md).

How the lists stay current:

- [`tools/update_lists.py`](tools/update_lists.py) rebuilds all three lists from the upstream sources above. It refuses to publish a list that comes back empty or changes by more than 25% at once, which would mean an upstream format change rather than real-world change.
- A GitHub Actions workflow re-runs that sync **weekly** and commits the result; [`tools/validate_lists.py`](tools/validate_lists.py) checks format, duplicates, ordering and the `lists.json` counts on every push and pull request.
- "Last synced" is the date a list's contents were last rebuilt from its source — for the sanctions list especially, a sync date is not a per-entry guarantee: an entry means the service has blocked Iran at some point, not that it necessarily still does.

### Notes

- Blocking changes over time on all three sides. These lists are snapshots, not permanent truths.
- Found something wrong or missing? Open an issue or a pull request — or message me on Telegram: https://t.me/rip00

### Credits

- Measurement data: [OONI](https://ooni.org), compiled by [Yuix-Networks/blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) — CC BY-NC-SA 4.0.
- Iranian domains: [bootmortis/iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) and [Chocolate4U/Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules).
- Sanctions list: [freedomofdevelopers/fod](https://github.com/freedomofdevelopers/fod).
- Format inspired by [wpzzz/blocked-sites-in-south-korea](https://github.com/wpzzz/blocked-sites-in-south-korea).

---

## فارسی

### `list.txt` — فیلترشده در ایران

ایران هیچ لیست رسمی و عمومی‌ای از سایت‌های فیلترشده منتشر نمی‌کند؛ برای همین این لیست به‌جای شایعه و حدس، از روی اندازه‌گیری واقعی ساخته شده است:

- داده‌ها از اندازه‌گیری‌های [OONI](https://ooni.org) (رصدخانه‌ی باز تداخل در شبکه) از داخل ایران می‌آید که پروژه‌ی [blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) آن‌ها را گردآوری کرده است.
- یک دامنه وقتی وارد لیست می‌شود که در تازه‌ترین ماه داده‌ها (اکتبر ۲۰۲۶)، در دست‌کم **۵۰٪** از حداقل **۲۰** اندازه‌گیری، فیلتر بودنش **تأیید** شده باشد (صفحه‌ی فیلترینگ یا اثر انگشت سانسور دیده شده باشد).
- نبودن یک دامنه در لیست معمولاً یعنی **تست نشده**، نه اینکه حتماً باز باشد.

### `blocked-from-outside.txt` — سایت‌های ایرانیِ مسدود از خارج

دامنه‌های میزبانی‌شده در ایران، گردآوری‌شده از فهرست‌های رسمی دامنه‌های ایرانی (سازمان فناوری اطلاعات / اینماد) توسط پروژه‌ی [iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) و در قالب تمیزشده‌ی [Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules). بانک‌ها، سرویس‌های دولتی، درگاه‌های پرداخت و خیلی از پلتفرم‌های داخلیِ این لیست آی‌پی غیرایرانی را قبول نمی‌کنند و در دوره‌های محدودیت اینترنت ملی هم عملاً فقط همین‌ها — از داخل — در دسترس می‌مانند.

### `blocked-by-sanctions.txt` — سرویس‌هایی که ایران را بلاک کرده‌اند

جهت برعکس دیوار: سرویس‌های خارجی (بیشتر آمریکایی) که به‌خاطر تحریم‌ها خودشان کاربر ایرانی را جئوبلاک می‌کنند؛ گردآوری‌شده توسط [freedomofdevelopers](https://github.com/freedomofdevelopers/fod). این لیست جامعه‌محور و توسعه‌دهنده‌محور است و تک‌تک موردهایش ممکن است کهنه شده باشد: بعضی سرویس‌ها بعداً مجوز گرفتند و به روی ایران باز شدند (مثلاً گیت‌هاب) — پس هر مورد را «سابقه‌ی بلاک کردن ایران» بدان، نه تضمین لحظه‌ای.

### وضعیت و به‌روزرسانی لیست‌ها

| فایل | دامنه | منبع | آخرین همگام‌سازی |
|---|---|---|---|
| `list.txt` | ۷۷۳ | اندازه‌گیری‌های OONI (از طریق Yuix-Networks/blocked-sites-dataset)، داده‌ی ماه ۲۰۲۶-۱۰ | ۲۰۲۶-۱۱-۱۹ |
| `blocked-from-outside.txt` | ۵۷٬۵۵۷ | ‏Chocolate4U/Iran-clash-rules (از روی bootmortis/iran-hosted-domains) | ۲۰۲۶-۱۱-۱۹ |
| `blocked-by-sanctions.txt` | ۶۰۵ | ‏freedomofdevelopers/fod (جامعه‌محور؛ موردهایش کهنه می‌شود) | ۲۰۲۶-۱۱-۱۹ |

همین اطلاعات به‌صورت ماشین‌خوان در [`lists.json`](lists.json) هست و همه‌ی تغییرات در [`CHANGELOG.md`](CHANGELOG.md) ثبت می‌شود.

لیست‌ها چطور تازه می‌مانند:

- اسکریپت [`tools/update_lists.py`](tools/update_lists.py) هر سه لیست را از منابع بالا از نو می‌سازد و اگر لیستی خالی برگردد یا یک‌باره بیش از ۲۵٪ تغییر کند (که یعنی قالب منبع عوض شده، نه دنیای واقعی) جلوی انتشارش را می‌گیرد.
- یک گردش‌کار GitHub Actions این همگام‌سازی را **هفته‌ای یک‌بار** خودکار انجام می‌دهد و نتیجه را کامیت می‌کند؛ اسکریپت [`tools/validate_lists.py`](tools/validate_lists.py) هم در هر پوش و پول‌ریکوئست قالب، تکراری‌نبودن، ترتیب و شمارش `lists.json` را بررسی می‌کند.
- «آخرین همگام‌سازی» تاریخی است که محتوای لیست آخرین بار از منبعش بازسازی شده — مخصوصاً در لیست تحریم‌ها، این تاریخ تضمین تک‌تک موردها نیست: بودن یک سرویس در لیست یعنی زمانی ایران را بلاک کرده، نه اینکه حتماً هنوز هم بلاک می‌کند.

### نکات

- فیلترینگ از هر سه طرف دائماً عوض می‌شود؛ این لیست‌ها عکس لحظه‌ای‌اند، نه حقیقت همیشگی.
- چیزی اشتباه است یا جا افتاده؟ ایشو یا پول‌ریکوئست بفرست — یا در تلگرام پیام بده: https://t.me/rip00

### اعتبار

- داده‌های اندازه‌گیری: [OONI](https://ooni.org)، گردآوری‌شده توسط [Yuix-Networks/blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) — با مجوز CC BY-NC-SA 4.0.
- دامنه‌های ایرانی: [bootmortis/iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) و [Chocolate4U/Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules).
- لیست تحریم: [freedomofdevelopers/fod](https://github.com/freedomofdevelopers/fod).
- فرمت پروژه با الهام از [wpzzz/blocked-sites-in-south-korea](https://github.com/wpzzz/blocked-sites-in-south-korea) است.
