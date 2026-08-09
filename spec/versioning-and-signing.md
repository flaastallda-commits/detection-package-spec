# DPS Versioning & Signing Model

## Versioning

Packages use [Semantic Versioning 2.0.0](https://semver.org). Because the
"API" of a detection package is *what it detects*, the increments are defined
in detection terms:

| Bump | When |
|---|---|
| **MAJOR** | Detection semantics change: a rule's logic is altered so it matches a different event population; a rule is removed; a telemetry requirement is added (consumers may now be unable to run the package); a rule id is retired. |
| **MINOR** | Detection surface grows compatibly: new rules added; a rule's `level` raised; new optional metadata. |
| **PATCH** | No semantic change to matching: description/investigation/false-positive text, tag hygiene, typo fixes. |

Additional rules:
- Rule **ids never change**; a rewritten rule that targets a different
  behavior is a *new* rule (new id) plus a `status: deprecated` marker on the
  old one for at least one MAJOR cycle.
- `name` + `version` releases are immutable. Fixing a bad release means a new
  version, never a re-tag.
- Pre-releases (`1.2.0-rc.1`) are allowed; consumers MUST NOT auto-promote
  them.

## Content hashing

The `integrity.contentHash` is `sha256:` over the **canonical content
serialization**:

1. Take every file listed in `spec.rules` plus `package.yml` itself with the
   `integrity` block removed.
2. Normalize each file: UTF-8, LF line endings, no trailing whitespace,
   single trailing newline.
3. Hash each normalized file; sort by in-package path; hash the sorted
   `path + "\0" + filehash` concatenation.

Canonicalization is byte-level over the normalized files — **never**
parse-then-reserialize YAML (round-tripping through a YAML/JSON parser can
drop or reorder information and makes honest recomputation
implementation-dependent).

## Signing

Signatures are **detached** and layered on top of the content hash:

```
my-package/
├── package.yml            # contains integrity.contentHash
└── package.sig/           # optional signature directory
    ├── publisher.sig      # signature over the contentHash string
    └── publisher.crt      # certificate / public key reference
```

- v1 supports two schemes:
  - **`x509`/Sigstore-style**: keyless or key-backed signature over the
    `contentHash` value; recommended for public distribution (transparency
    log).
  - **`hmac-sha256`**: shared-secret MAC for closed pipelines
    (author → CI → deployer inside one trust domain).
- Verification is **fail-closed**: a consumer configured to require
  signatures MUST reject a package whose hash does not recompute, whose
  signature does not verify, or whose signature has expired — there is no
  "warn and continue" mode.
- Signatures cover *content*, not process claims. "Reviewed by X",
  "approved for production" are consumer-side attestations layered
  separately (e.g. in-toto/SLSA attestations referencing the same
  contentHash), not part of the package.

## Supersession

A package MAY declare that it replaces another:

```yaml
metadata:
  supersedes:
    - name: snowflake-starter-pack
      versions: "<2.0.0"
```

Consumers treat installed superseded versions as upgrade candidates; they
MUST NOT silently auto-remove them.
