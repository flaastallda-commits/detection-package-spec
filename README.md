# Detection Package Specification (DPS) v1.0

**An open, vendor-neutral format for packaging detection content — rules, metadata,
telemetry requirements, and multi-platform translation targets — as a single
versioned, signable unit.**

A *Detection Package* is the atomic object of the detection-engineering ecosystem:
the thing you author once, review once, sign once, and deploy to many SIEMs. This
repository contains the specification, reference examples, and (in future) a
validator CLI. It contains **no platform code**.

## Why this exists

Detection content today is trapped in one of two bad states:

1. **Loose rule files** (Sigma/YAML in a git repo) with no manifest, no versioning
   contract, no telemetry prerequisites, and no honest statement of what breaks
   when translated to a given SIEM.
2. **Vendor-locked content packs** that only work inside one product.

DPS defines the missing middle: a small, boring, reviewable package format that

- keeps the **detection logic Sigma-aligned** (portable by default),
- makes **telemetry requirements explicit** (a rule that can't see its data is a lie),
- carries **honest translation-target capability profiles** (what each SIEM dialect
  can and cannot express — fail closed, never silently degrade),
- supports **semantic versioning and cryptographic signing** so a package can move
  through review → approval → deployment pipelines with integrity guarantees.

## Spec documents

| Document | Contents |
|---|---|
| [spec/manifest.md](spec/manifest.md) | The `package.yml` manifest format |
| [spec/rule-format.md](spec/rule-format.md) | Detection rule format (Sigma-aligned) and portability constraints |
| [spec/metadata.md](spec/metadata.md) | MITRE ATT&CK mapping, false-positive assumptions, telemetry requirements, investigation guidance |
| [spec/versioning-and-signing.md](spec/versioning-and-signing.md) | Semantic versioning rules, content hashing, and the signing model |
| [spec/capability-profiles.md](spec/capability-profiles.md) | Translation-target capability profiles and the canonical platform registry |

## Examples

Four complete, self-contained example packages built on Snowflake
`ACCOUNT_USAGE` telemetry (no proprietary or tenant-specific content):

- [examples/snowflake-identity-threats](examples/snowflake-identity-threats/) — MFA-less logins, brute force
- [examples/snowflake-privilege-escalation](examples/snowflake-privilege-escalation/) — ACCOUNTADMIN / SECURITYADMIN grants
- [examples/snowflake-exfiltration](examples/snowflake-exfiltration/) — mass unload, external stages, data shares, presigned URLs
- [examples/snowflake-defense-evasion](examples/snowflake-defense-evasion/) — MFA bypass windows, network-policy tampering

## The open-core boundary, honestly

This spec — and everything in this repository — is Apache-2.0. What's open and
what isn't:

**Open (this repo, forever):**
- The Detection Package format itself: manifest, rule format, metadata schema,
  versioning/signing model, capability-profile schema.
- Reference example packages.
- The canonical platform identifier registry.
- (Planned) a validator CLI and conformance test suite.

**Not open (commercial platform):**
- The multi-platform transpilers that translate DPS rules into vendor query
  dialects (SPL, KQL, Snowflake SQL, …).
- The deployment/readiness engine (schema drift scanning, ship gates,
  verified readback, approval workflows).
- The per-tenant field-ontology learning and mapping infrastructure.

The intent is simple: **the format is a commons; the automation around it is a
product.** Anyone can author, validate, sign, exchange, and manually deploy DPS
packages without ever touching the commercial platform. We commit to evolving
the spec in the open and to never requiring proprietary extensions for a package
to be valid.

## License & contributing

- Licensed under [Apache-2.0](LICENSE).
- Contributions require agreeing to the [Contributor License Agreement](CLA.md).
- Spec changes happen via pull request; breaking changes to the format require a
  new `apiVersion`.

## Status

**v1.0 — draft for public review.** The format is derived from a production
detection-engineering platform's internal model of use cases, rules, field
ontology, and multi-platform deployment targets, generalized for standalone use.
