# Security policy

## Reporting a vulnerability

If you find a problem that affects the **integrity of the data or the
tooling** — for example a way to make the sync script publish corrupted or
attacker-controlled lists, a supply-chain issue in the workflows, or a bug
that silently drops the safety checks — please report it privately first:

- Telegram: https://t.me/rip00
- or a GitHub issue with **security** in the title if the detail is not
  sensitive.

Aim: a first response within about **7 days**.

## What is NOT a security issue

- A domain being listed or not listed. That is a **data report** — please
  use the issue templates (incorrect entry / missing entry) instead.
- A service having started or stopped blocking Iran. Also a data report.
- Blocking itself: this repository only documents measurements and source
  data; it does not operate any filtering or circumvention service.

## Scope

In scope: `tools/`, `tests/`, the GitHub Actions workflows, and the
integrity of the published lists. Out of scope: the upstream projects
(report to them directly) and GitHub's own platform.
