# ClawSweeper pull-request comment permission repair

Date: 2026-07-21 America/New_York

## Trigger

- `dinkuskit/blocks` run
  [29888239015](https://github.com/dinkuskit/blocks/actions/runs/29888239015)
  admitted the command candidate and minted the repository-scoped GitHub App
  token, then received `HTTP 403` when creating the canonical PR timeline
  comment. The model and publisher jobs did not run.
- The reviewed PR head remained
  `a1cb3d51a9f23ab8522d77f1e428638f2218512f`.

## Value-blind probe

- Diagnostic PR:
  [dinkuskit/blocks#10](https://github.com/dinkuskit/blocks/pull/10)
- Terminal probe run:
  [29888573741](https://github.com/dinkuskit/blocks/actions/runs/29888573741)
- The same issues-write installation token produced:
  - `200` reading the fixed PR comment;
  - `422` for an intentionally invalid reaction on real issue `#2`;
  - `403` for the same invalid reaction on pull request `#7` and its timeline
    comment.
- The response permission header reported `issues=write` in each case. The
  invalid reaction value cannot create repository state. Token and private-key
  values were not printed or persisted.

After the App and its installation were changed to Pull requests write with no
Issues access:

- GitHub's public App metadata reported only mandatory `metadata: read` and
  `pull_requests: write`, updated at `2026-07-22T11:16:18Z`.
- The old issues-write token mint failed, confirming the installation dropped
  that permission.
- Final non-mutating run
  [29915267982](https://github.com/dinkuskit/blocks/actions/runs/29915267982)
  minted a repository-selected PR-write token, read the fixed PR comment with
  `HTTP 200`, and received the expected `HTTP 422` validation response when it
  intentionally omitted the required comment body.
- No issue comment, reaction, review, or other repository state was created by
  the probe. Credential values remained outside logs and model context.

## Repair

- Remove cosmetic request/completion reactions.
- Mint gate and publisher tokens for the current repository only, requesting
  `pull-requests: write` and no Issues permission.
- Keep all repository reads and model isolation unchanged.
- Document the human activation gate: the private App must have Pull requests
  read/write, no Issues access, and access only to explicitly selected product
  repositories.

## Upstream comparison

- Current `saari-co/clawsweeper` `origin/main` was inspected at
  `43a2ae1f272f434ad6df9b6e26c725a878dbe1f9`.
- Upstream also mints short-lived, repository-selected installation tokens in
  deterministic steps and keeps App credentials away from the model.
- Its active comment-mutating workflows request Pull requests write; read-only
  lanes request Pull requests read. There is no PAT fallback for deterministic
  GitHub writes. This supports the repaired permission boundary without
  importing upstream's broader repair-runner permissions.

## Verification

- Draft repair PR:
  [dinkuskit/.github#5](https://github.com/dinkuskit/.github/pull/5)
- Repair commit: `4e6602fb5372548defd3d8cbef4489b8eb392d75`
- CI run:
  [29888827937](https://github.com/dinkuskit/.github/actions/runs/29888827937)
  completed successfully.

```text
git diff --check
ruby -e 'require "yaml"; YAML.load_file(ARGV.fetch(0))' \
  .github/workflows/clawsweeper-command.yml
python3 -m unittest -v tests/test_clawsweeper_workflow.py
```

Result: 32 tests passed with one expected caller-template skip. Inline shell
parsing, YAML parsing, token-scope assertions, and diff hygiene passed.
Independent security review was clean with no P0-P2 findings.

## Gates and next proof

- Human approval is required to change the GitHub App permission and repository
  selection.
- Human approval is required to merge the reusable-workflow repair and its
  caller pin.
- After both are active, post a fresh standalone command on `blocks#7` and bind
  the terminal ClawSweeper verdict to the exact PR head and Actions run.
