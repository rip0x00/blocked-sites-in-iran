# Data status | وضعیت داده‌ها

Snapshot of the lists as published. This file is refreshed whenever a sync
changes the data; per-list provenance (source hash, retrieval time) lives in
[`lists.json`](lists.json).

| List | Entries | Data period / basis | Last synced |
|---|---|---|---|
| `list.txt` (blocked in Iran) | 773 | OONI measurements, 2026-10 | 2026-11-19 |
| `blocked-from-outside.txt` (Iran-hosted) | 57,557 | Official IR registries via bootmortis / Chocolate4U | 2026-11-19 |
| `blocked-by-sanctions.txt` (services blocking Iran) | 605 | freedomofdevelopers/fod, community data | 2026-11-19 |

## Upstream availability

As of the last build (2026-11-20):

- OONI compilation (Yuix-Networks/blocked-sites-dataset): **available**
- Iran-clash-rules release asset (Chocolate4U): **available**
- freedomofdevelopers/fod: **available**

## Notes

- Consumer-ready outputs are in `dist/` (JSON, CSV, AdGuard, dnsmasq,
  hosts, Clash, Surge, sing-box) and per-domain structured records in
  `data/` (`domains.jsonl`, `sanctions.jsonl`); both are regenerated on
  each sync.
- "Last synced" is when a list's contents were last rebuilt from its
  source. The sanctions list is historical/community-reported data: an
  entry means the service has blocked Iran at some point, not that it
  necessarily still does.
- The Iran-hosted list is registry data, not a reachability measurement
  from outside Iran.
