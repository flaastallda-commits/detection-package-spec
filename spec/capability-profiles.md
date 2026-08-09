# DPS Translation-Target Capability Profiles

A Detection Package is authored once and translated to many SIEM/analytics
dialects. Translation is only trustworthy if every target declares — machine
readably — what it can and cannot express, and translators **fail closed** on
anything outside that declaration. Capability profiles are that declaration.

## Canonical platform identifiers

Targets are named by canonical platform ids. Aliases (product marketing names,
abbreviations) MUST be normalized to the canonical id before any lookup;
unknown ids map to themselves (an honest "unknown", never a guess).

| Canonical id | Common aliases |
|---|---|
| `microsoft_sentinel` | sentinel, Azure Sentinel |
| `splunk` | splunk enterprise, splunk cloud |
| `elasticsearch` | elastic, elk |
| `chronicle` | google chronicle, google secops |
| `crowdstrike_falcon` | crowdstrike, falcon |
| `microsoft_defender_endpoint` | defender, mde |
| `sentinelone` | s1 |
| `ibm_qradar` | qradar |
| `snowflake` | — |
| `databricks` | — |
| `bigquery` | — |

The registry grows by pull request; ids are lowercase snake_case and never
reused.

## Profile document

Each target publishes a capability profile:

```yaml
apiVersion: dps/v1
kind: CapabilityProfile
platform: snowflake
dialect: snowflake_sql                # output language
profiles:                             # DPS rule profiles this target fully supports
  - dps-flat-v1
modifiers:                            # supported field modifiers
  contains: true
  startswith: true
  endswith: true
  re: false                           # unsupported → rules using |re are refused, not approximated
logsources:                           # logsources this target can bind
  - product: snowflake
    service: login_history
    binding: "SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY"
    timestampField: EVENT_TIMESTAMP
  - product: snowflake
    service: query_history
    binding: "SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
    timestampField: START_TIME
execution:
  livePush: false                     # can rules be pushed as live detections?
  scheduledExecution: true            # or promoted to scheduled queries/tasks?
  readbackVerification: true          # can deployment be verified by reading the artifact back?
fieldOntology:                        # canonical-path → native-field map (per logsource binding)
  - service: login_history
    map:
      user.name: USER_NAME
      source.ip: CLIENT_IP
      event.outcome: IS_SUCCESS
      error.message: ERROR_MESSAGE
      authentication.factor.first: FIRST_AUTHENTICATION_FACTOR
      authentication.factor.second: SECOND_AUTHENTICATION_FACTOR
  - service: query_history
    map:
      user.name: USER_NAME
      user.role: ROLE_NAME
      query.text: QUERY_TEXT
      query.type: QUERY_TYPE
      warehouse.name: WAREHOUSE_NAME
```

## Semantics

1. **Profile gate.** A translator MUST refuse a rule whose package declares a
   DPS profile the target does not list. No partial translation.
2. **Modifier gate.** Any modifier marked `false` (or absent) causes refusal
   for rules using it.
3. **Logsource binding.** A rule's `logsource` must match a profile
   `logsources` entry; otherwise the target cannot honestly claim coverage.
4. **Field mapping is per-logsource, never global.** The same canonical path
   can bind to different native fields per table/view; conversely a native
   field name may mean different things in different sources. Cross-source
   reuse of a mapping is a correctness bug, not an optimization.
5. **Ambiguity fails closed.** If a canonical path resolves to zero or more
   than one native field for the bound logsource, the translator MUST refuse
   (no last-write-wins, no "best guess").
6. **Execution honesty.** `livePush: false` + `scheduledExecution: true`
   means the target deploys rules as scheduled queries/tasks — consumers MUST
   surface that distinction to operators, not label both "deployed".
   `readbackVerification` declares whether "verified deployed" can ever be
   truthfully claimed for this target.

## Why field portability lives here, not in rules

Rules stay in native field names of their authored logsource (readable,
testable against real data). The ontology map in the capability profile is
what lets a consumer *re-target* a package: resolve the rule's fields to
canonical paths via the source profile, then to native fields via the
destination profile. Any hop that is ambiguous or missing aborts the
translation. This keeps the rule body honest and pushes all portability risk
into an explicit, reviewable, fail-closed artifact.
