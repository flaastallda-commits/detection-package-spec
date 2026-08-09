# Contributing to the Detection Package Specification

Thanks for your interest in improving the Detection Package Specification (DPS).

## Contributor License Agreement

Before we can accept your contribution, you must agree to the
[Contributor License Agreement](CLA.md). By submitting a pull request,
patch, or issue containing code or content intended for inclusion in this
project, you accept the CLA's terms. No separate signature step is required
— submission constitutes acceptance, as described in the CLA itself.

## What contributions look like

- **Spec clarifications and errata** — ambiguities, contradictions, or gaps
  in the documents under [spec/](spec/). Open an issue first for anything
  that changes normative behavior.
- **Capability-profile corrections** — a translation target claims support
  for a construct it can't express (or vice versa). Include a reproducible
  reference (vendor docs or an actual query) with your change.
- **Example packages** — new self-contained examples are welcome. They must
  use only publicly available telemetry schemas and contain no proprietary
  or tenant-specific content.
- **Registry additions** — new canonical platform identifiers, per
  [spec/capability-profiles.md](spec/capability-profiles.md).

## Ground rules

1. **Fail closed, never silently degrade.** Any proposal that lets a
   translation target silently drop or weaken detection logic will be
   rejected. Lossy translations must be explicit and machine-readable.
2. **Portable by default.** Rule-format changes must remain Sigma-aligned;
   platform-specific constructs belong in capability profiles, not the core
   rule format.
3. **Versioning discipline.** Normative spec changes follow the semantic
   versioning rules in [spec/versioning-and-signing.md](spec/versioning-and-signing.md).

## Process

1. Open an issue describing the problem or proposal.
2. For non-trivial changes, wait for a maintainer to confirm direction
   before writing the full change.
3. Open a pull request. Keep it focused — one concern per PR.

## License

All contributions are licensed under [Apache-2.0](LICENSE), per the CLA.
