# Publishing & sync (internal — not part of the public spec)

> This file documents how the public Detection Package Specification repo is
> kept in sync with this directory. It is synced to the public repo too, and
> that is intentional: the public repo should be honest that its source of
> truth lives upstream.

## Source of truth

`docs/detection-package-spec/` in the CyberDEP monorepo is the **only** source
of truth. The public GitHub repo is a published mirror of this directory
(README as its front page, LICENSE/CLA/CONTRIBUTING at root).

## Sync path

One-way sync, monorepo → public repo, via:

```bash
DPS_PUBLIC_REPO_URL=https://<token>@github.com/<org>/detection-package-spec.git \
  bash scripts/sync-detection-package-spec.sh "Sync: <what changed>"
```

The script mirrors this directory into the public repo checkout with
`rsync --delete` (preserving `.git/` and `.github/`), commits, and pushes.

## Handling community contributions

Community PRs land in the public repo. Before the next sync:

1. Review + merge the PR in the public repo (CLA acceptance is by submission,
   see CONTRIBUTING.md / CLA.md).
2. Port the merged change back into `docs/detection-package-spec/` here.
3. Run the sync script — it should then report "already up to date".

Skipping step 2 means the next sync **overwrites** the community change.
