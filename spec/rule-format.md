# DPS Rule Format (Sigma-aligned)

DPS rules are YAML documents based on the
[Sigma](https://github.com/SigmaHQ/sigma-specification) generic signature
format, with a constrained profile chosen for honest multi-platform
translation. A DPS rule is a valid Sigma rule; the reverse is not always true.

## Example

```yaml
title: Snowflake Mass Data Unload
id: 6f1d2c9e-0a44-4a1c-9b6b-1a2b3c4d5e01     # must match the id in package.yml
status: stable                                # experimental | test | stable | deprecated
description: >-
  Data-unload statements (QUERY_TYPE = UNLOAD, i.e. COPY INTO <stage/location>)
  which write table contents out to stages or external cloud storage.
logsource:
  product: snowflake
  service: query_history
detection:
  selection:
    QUERY_TYPE: 'UNLOAD'
  condition: selection
falsepositives:
  - Approved ETL/backup pipelines (filter by known service roles downstream)
level: high
tags:
  - attack.exfiltration
  - attack.t1567.002
  - attack.t1048
```

## Required fields

| Field | Requirement |
|---|---|
| `title` | Unique within the package |
| `id` | UUIDv4, identical to the manifest entry |
| `status` | One of `experimental`, `test`, `stable`, `deprecated` |
| `description` | What the rule detects and why it matters |
| `logsource` | `product` (+ `service` and/or `category`) — must correspond to a `spec.telemetry` entry in the manifest |
| `detection` | See portability profile below |
| `level` | `informational`/`low`/`medium`/`high`/`critical`, ≤ package severity |
| `falsepositives` | ≥1 entry, or the literal `- None known` — silence is not allowed |
| `tags` | MUST include `attack.<tactic>` and/or `attack.t<technique>` tags when a MITRE mapping exists |

## The `dps-flat-v1` portability profile

Full Sigma expressiveness does not survive translation to every SIEM dialect.
Rather than let translators silently drop conditions (a rule that lies about
its own logic), DPS v1 defines a **flat profile** that every conforming
translation target must support completely:

Allowed:
- One or more **flat selections** (maps of `Field: value` /
  `Field|modifier: value`).
- `condition` as a conjunction/disjunction of selection names:
  `selection`, `sel1 and sel2`, `sel1 or sel2` (no parentheses, no mixing
  `and`/`or` in one condition).
- Field modifiers: `contains`, `startswith`, `endswith`, `re` (targets may
  declare `re` unsupported in their capability profile).

Not allowed in `dps-flat-v1`:
- `not`, `1 of ...`, `all of ...`, wildcard selection groups, nested parens.
- **Value lists** (`Field: [a, b]`). Rationale: several dialect adapters
  expand a list into multiple conditions joined by the *top-level* logic,
  silently turning an intended OR into a never-matching AND. Author
  alternatives as separate rules (e.g. one rule per privileged role name).
- Aggregations (`count() by X > N`, `timeframe`). Thresholding is a consumer
  concern; a rule whose aggregation gets dropped in translation would ship
  logic it does not have.
- Field-to-field comparisons.

Packages MAY include richer Sigma rules by declaring a different profile in
`spec.targets` (future profiles, e.g. `dps-full-sigma`), but every declared
target must state — in its capability profile — that it supports that profile.
**A translator encountering an unsupported construct MUST refuse to translate,
never approximate.**

## Field naming

Rule fields are written in the **native field names of the declared
`logsource`** (e.g. Snowflake `ACCOUNT_USAGE` column names). Portability
across platforms comes from the capability-profile layer (canonical field
ontology mapping, see [capability-profiles.md](capability-profiles.md)), not
from forcing an abstract taxonomy into the rule body. A package that wants
cross-platform field portability documents the canonical path of each required
field in `spec.telemetry` (`canonical:` annotation, see
[metadata.md](metadata.md)).
