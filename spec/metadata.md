# DPS Metadata: MITRE Mapping, False Positives, Telemetry Requirements

Detection content without honest metadata is noise with a YAML extension.
DPS makes three metadata classes mandatory.

## 1. MITRE ATT&CK mapping

Every rule that maps to ATT&CK MUST carry Sigma-style tags:

```yaml
tags:
  - attack.credential_access          # tactic (lowercase, underscores)
  - attack.t1110                      # technique
  - attack.t1110.004                  # sub-technique
```

Rules:
- Sub-techniques imply the parent technique; do not list both unless the rule
  genuinely covers the broader technique too.
- A rule with **no** applicable ATT&CK mapping (e.g. pure hygiene/audit rules)
  MUST include the tag `attack.not_applicable` so absence is a statement, not
  an omission.
- Package-level ATT&CK coverage is *derived* by tooling from rule tags; it is
  never declared separately in the manifest (no chance of drift).

## 2. False-positive assumptions

Every rule MUST have a non-empty `falsepositives` list (or the explicit
`- None known`). Good entries name the *benign process* that trips the rule
and, where possible, the discriminating signal:

```yaml
falsepositives:
  - Approved ETL/backup pipelines (filter by known service roles downstream)
  - Helpdesk-assisted device re-enrolment (verify ticket)
```

Optional structured form (recommended for tooling):

```yaml
falsepositives:
  - description: Approved ETL/backup pipelines
    discriminator: "ROLE_NAME in the approved service-role allowlist"
    expectedVolume: high        # low | medium | high
```

## 3. Telemetry requirements

The package manifest declares, per `logsource`, exactly what data must exist
for the package's rules to be *capable of matching*:

```yaml
spec:
  telemetry:
    - product: snowflake
      service: query_history
      description: "SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY view (up to 45 min ingest latency)"
      requiredFields:
        - name: QUERY_TEXT
          type: string
          canonical: query.text          # optional — canonical ontology path
        - name: QUERY_TYPE
          type: string
          canonical: query.type
        - name: USER_NAME
          type: string
          canonical: user.name
      latencyNote: "ACCOUNT_USAGE views lag up to 45 minutes; not suitable for sub-hour SLAs"
```

Rules:
- Every field referenced in any rule's `detection` block MUST appear in the
  matching telemetry entry's `requiredFields`. Validators enforce this.
- `type` uses the DPS scalar set: `string | ip | integer | float | boolean |
  timestamp | hash | url | email | json`.
- `canonical` is optional but strongly recommended: it names the
  vendor-neutral ontology path (e.g. `user.name`, `source.ip`,
  `event.outcome`, `authentication.factor.first`) that consuming platforms use
  to re-map the rule onto other telemetry (see
  [capability-profiles.md](capability-profiles.md)).
- `latencyNote` and `description` exist so a consumer can judge fitness *before*
  deploying — a correct rule on telemetry that arrives an hour late is a
  different product than the same rule on a streaming source.

## 4. Investigation guidance (optional, recommended)

Rules MAY carry an `x-dps-investigation` extension listing ordered triage
steps. Consumers that don't understand it ignore it (it is an `x-` extension,
outside core Sigma):

```yaml
x-dps-investigation:
  - Identify user, role, and warehouse that ran the unload
  - Determine target stage/location and data volume (BYTES_WRITTEN)
  - Check whether the destination is an approved internal stage or an external URL
  - Suspend the user and rotate credentials if unauthorised
```

## Severity semantics

| Level | Meaning |
|---|---|
| `informational` | Context enrichment; never pages |
| `low` | Review in aggregate |
| `medium` | Triage within a business day |
| `high` | Triage within hours; likely real attack technique |
| `critical` | Immediate response; high-confidence, high-impact |

Severity describes the *event if true*, not the rule's precision — precision
lives in `falsepositives`.
