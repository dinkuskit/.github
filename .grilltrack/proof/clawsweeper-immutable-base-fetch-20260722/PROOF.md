# ClawSweeper immutable base-fetch repair

Date: 2026-07-22 America/New_York

## Trigger

- `dinkuskit/blocks` PR
  [#7](https://github.com/dinkuskit/blocks/pull/7) was retriggered after the
  Pull requests write repair was merged and pinned.
- Run
  [29916338549](https://github.com/dinkuskit/blocks/actions/runs/29916338549)
  successfully validated the standalone command, minted the repository-scoped
  App token, and persisted the canonical admission comment. It then failed in
  `Prepare immutable review request`; the model and publisher jobs were
  skipped.
- The App-owned terminal comment was a deterministic
  [`blocked`](https://github.com/dinkuskit/blocks/pull/7#issuecomment-5045303937)
  verdict bound to base
  `c9c9e20167165c9c6907bff7205d3a94a2d6ee4d` and head
  `a1cb3d51a9f23ab8522d77f1e428638f2218512f`. No model review ran.

## Diagnosis

The gate correctly authorized the immutable PR API pair, but request
preparation fetched the moving `refs/heads/main` tip into the base slot and
then required it to equal the authorized base SHA.

At failure time:

- authorized PR base: `c9c9e20167165c9c6907bff7205d3a94a2d6ee4d`;
- moving `main` tip: `6728f90a724ce926d0f172716289067d43ddd1d8`;
- authorized and fetched PR head:
  `a1cb3d51a9f23ab8522d77f1e428638f2218512f`.

The base branch had advanced independently of this older open PR. The mutable
ref fetch therefore made the exact-SHA assertion fail before artifact upload or
model credential access.

## Repair

- Fetch the already-authorized base commit by its immutable SHA into the
  isolated bare repository.
- Continue fetching the server-owned pull-request head ref and verifying both
  fetched object IDs against the admitted pair.
- Add a regression contract that requires the exact-SHA refspec and rejects the
  former moving `refs/heads/$base_ref` input.
- Correct the operator documentation to describe drift in terms of the
  authorized PR base/head pair rather than an unrelated advance of the base
  branch.

This removes a mutable-ref time-of-check/time-of-use edge while preserving all
credential and publication boundaries.

The live run also exposed a recovery-policy mismatch: GitHub's public comment
record labeled the repository administrator `CONTRIBUTOR`, while the
repository-permission endpoint resolved the same account to `admin`. Without a
repair, the required `re-review` command would be rejected. The gate now uses
the caller's existing metadata-read token to normalize only `write` or `admin`
permission to the maintainer policy. It fails closed to the original
association when that lookup fails, does not promote public/read access, and
keeps the raw comment association digest-bound for identity checks.
The permissionless candidate admits only the standalone command shape; the
locked deterministic gate remains the sole authorization and quota authority.

## Verification

```text
python3 -m unittest tests/test_clawsweeper_workflow.py
ruby -e 'require "yaml"; YAML.load_file(".github/workflows/clawsweeper-command.yml")'
git diff --check
git fetch --dry-run --no-tags https://github.com/dinkuskit/blocks.git \
  c9c9e20167165c9c6907bff7205d3a94a2d6ee4d
git ls-remote https://github.com/dinkuskit/blocks.git \
  refs/heads/main refs/pull/7/head
gh api repos/dinkuskit/blocks/collaborators/saariuslystoned/permission \
  --jq '{permission,role_name,user:.user.login}'
```

Results:

- 34 workflow-contract tests passed with one expected caller-template skip,
  including private write/admin maintainer recovery and read-access rejection.
- YAML parsing and diff hygiene passed.
- GitHub accepted the authorized historical base SHA as a direct fetch input.
- The live moving branch/head ref evidence matched the diagnosed identities.
- The authenticated metadata endpoint resolved the trigger author to repository
  role/permission `admin`; the public comment record remained `CONTRIBUTOR`.

## Gates and next proof

- Human approval is required to merge the reusable-workflow repair and its
  exact caller pin.
- The blocked admission consumed the first run for this exact pair. A trusted
  maintainer must use `@clawsweeper re-review` after the fixed workflow and pin
  are active; that is the pair's second and final allowed admission.
- Terminal success still requires a model-backed App-authored verdict bound to
  the unchanged current PR head.
