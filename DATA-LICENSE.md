# Data license | مجوز داده‌ها

The domain lists in this repository are **data, not code**. The code (tools,
tests, workflows) is under the MIT license in [`LICENSE`](LICENSE); this file
covers the data files: `list.txt`, `blocked-from-outside.txt`,
`blocked-by-sanctions.txt`, `lists.json` and `data/domains.jsonl`.

## Terms

The compiled lists in this repository are shared under the
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
license (CC BY-NC-SA 4.0)**:
https://creativecommons.org/licenses/by-nc-sa/4.0/

That means:

- **Attribution** — you must credit this repository and the upstream sources
  listed below.
- **Non-commercial** — you may not use the lists for commercial purposes.
- **Share-alike** — if you remix or redistribute the data, you must share it
  under the same license.
- **Upstream terms prevail** — where an upstream source imposes stricter
  terms than CC BY-NC-SA 4.0, the stricter terms apply to the derived data.

## Upstream sources and their terms

| List | Upstream | Terms / attribution |
|---|---|---|
| `list.txt`, `data/domains.jsonl` | [OONI](https://ooni.org) measurement data, compiled by [Yuix-Networks/blocked-sites-dataset](https://github.com/Yuix-Networks/blocked-sites-dataset) | CC BY-NC-SA 4.0. Attribute OONI and the blocked-sites-dataset project. |
| `blocked-from-outside.txt` | [bootmortis/iran-hosted-domains](https://github.com/bootmortis/iran-hosted-domains) (official Iranian domain registries: ITO / Enamad), in the cleaned form by [Chocolate4U/Iran-clash-rules](https://github.com/Chocolate4U/Iran-clash-rules) | Attribute both projects; their upstream terms prevail where stricter. |
| `blocked-by-sanctions.txt` | [freedomofdevelopers/fod](https://github.com/freedomofdevelopers/fod) | Community-maintained data; attribute the project. |

Commercial use of the OONI-derived data is **not** permitted under
CC BY-NC-SA 4.0. If you need the data for a commercial purpose, go to the
upstream sources and check their terms directly.
