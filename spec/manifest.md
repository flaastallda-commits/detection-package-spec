# DPS Manifest Format (`package.yml`)

Every Detection Package is a directory containing exactly one `package.yml`
manifest at its root, one or more rule files under `rules/`, and optional
supporting files (`docs/`, `tests/`).

```
my-package/
├── package.yml          # this manifest (required)
├── rules/
│   ├── some-rule.yml    # Sigma-aligned rules (required, ≥1)
│   └── another-rule.yml
├── docs/                # optional free-form documentation
└── tests/               # optional test events / fixtures
```

## Top-level fields

```yaml
apiVersion: dps/v1            # required — spec version this package conforms to
kind: DetectionPackage        # required — literal

metadata:
  name: snowflake-exfiltration      # required — DNS-label style: [a-z0-9]([a-z0-9-]*[a-z0-9])?
  version: 1.0.0                    # required — semver (see versioning-and-signing.md)
  title: "Snowflake Exfiltration"   # required — human title
  description: >-                   # required — what threat surface this covers and why
    Detections for bulk data exfiltration channels in Snowflake ...
  license: Apache-2.0               # required — SPDX identifier for the CONTENT
  authors:                          # required — ≥1
    - name: Example SecEng Team
      email: seceng@example.com     # optional
  homepage: https://example.com     # optional
  tags: [snowflake, exfiltration]   # optional — lowercase kebab-case

spec:
  category: exfiltration            # required — primary category (see metadata.md)
  severity: high                    # required — package-level ceiling: informational|low|medium|high|critical

  telemetry:                        # required — what data the package needs (see metadata.md)
    - product: snowflake
      service: query_history
      description: "SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY view"
      requiredFields: [QUERY_TEXT, QUERY_TYPE, USER_NAME, ROLE_NAME]

  rules:                            # required — ≥1; every file under rules/ MUST be listed
    - path: rules/mass-data-unload.yml
      id: 6f1d2c9e-0a44-4a1c-9b6b-1a2b3c4d5e01   # required — UUIDv4, stable for the rule's lifetime
    - path: rules/external-stage-creation.yml
      id: 6f1d2c9e-0a44-4a1c-9b6b-1a2b3c4d5e02

  targets:                          # optional — declared translation targets (see capability-profiles.md)
    - platform: snowflake           # canonical platform id
      profile: dps-flat-v1          # capability profile the rules were authored within
    - platform: splunk
      profile: dps-flat-v1

integrity:                          # populated at packaging time (see versioning-and-signing.md)
  contentHash: sha256:...           # required when signed — hash over canonical content
  signatures: []                    # optional — detached signatures may live alongside instead
```

## Rules of validity

1. `apiVersion` MUST be `dps/v1`. Unknown versions MUST be rejected, not
   best-effort parsed.
2. Every file in `rules/` MUST appear in `spec.rules`, and vice versa. Orphan
   rule files are a validation error (a package must be fully accounted).
3. Rule `id` values are UUIDv4, unique within the package, and **immutable
   across versions** — a rule keeps its id through edits; a semantically new
   rule gets a new id. Tooling uses ids (not titles) for dedup, deployment
   tracking, and supersession.
4. `metadata.name` + `metadata.version` uniquely identify a package release.
   Re-publishing different content under the same name+version is forbidden.
5. `spec.severity` is the maximum severity of any rule in the package; a rule
   MUST NOT declare a `level` above the package severity.
6. If `spec.targets` is present, every listed rule MUST validate against each
   named capability profile (fail closed: a package that declares a target it
   cannot honestly satisfy is invalid).
7. Consumers MUST ignore unknown *optional* fields (forward compatibility) but
   MUST reject unknown *required-section* structures.

## Relationship to use-case metadata

DPS deliberately excludes workflow state (draft/approved/deployed status,
assignees, ticket keys, validation results). Those belong to the consuming
platform, not the portable artifact. A package is *content + claims*, never
*process state*.
