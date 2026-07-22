# ClawSweeper command workflow (path B)

Public DinkusKit product repositories call the reusable workflow:

`.github/workflows/clawsweeper-command.yml` in this org repo.

## Who can trigger

| Association | Can run `@clawsweeper review`? |
| --- | --- |
| `OWNER`, `MEMBER`, `COLLABORATOR` | Yes |
| `CONTRIBUTOR` (usually after a **merged** PR) | Yes — one hosted review per PR; no self re-review; five contributor-triggered reviews per repo/UTC day |
| `FIRST_TIME_CONTRIBUTOR` / `FIRST_TIMER` / `NONE` | No — a trusted person must comment for them |

Command must be **alone on a line**. Inline prose is ignored.

```text
@clawsweeper review
```

Re-review after a prior canonical admission:

```text
@clawsweeper re-review
```

Only `OWNER`, `MEMBER`, or `COLLABORATOR` may request re-review, and each exact
base/head pair is limited to two hosted admissions total. A prior admission is
enough to recover from a pending, stale, failed, or blocked attempt; it need not
have reached a model verdict.

## What runs

1. A deterministic gate on GitHub-hosted `ubuntu-latest` re-fetches and
   digest-binds the exact triggering comment, captures the authorized base/head
   pair, then uses a narrow DinkusKit-owned ClawSweeper App token to persist one
   canonical admission comment. Only that dedicated bot identity is
   authoritative for quota accounting. The record precedes request preparation
   and any model credential, and survives stale, failed, and blocked runs.
2. The gate fetches those exact objects without checkout, generates the complete
   pull-request diff locally from merge-base to head, and records the merge
   base plus prompt/full-diff size and digests. If the 90 KB model input is
   truncated, changes more than 250 paths, or contains binary/LFS/submodule
   changes, a `clean` verdict is deterministically prohibited. Binary
   classification resolves committed `diff` attributes from both immutable
   trees in an ambient-config-isolated bare repository. LFS detection parses
   small changed blobs as reference-compatible pointer files, including
   extension-name punctuation; a header mentioned in ordinary source or
   documentation does not trip the guard.
3. An isolated `ubuntu-latest` model job runs version-pinned Copilot CLI with
   **`gpt-5.6-terra`** on exact Node.js `22.23.1`. It receives only the Copilot
   Requests PAT: no repository token, checkout, shell/file tools, built-in MCP,
   or mutation permission. The request artifact is digest-validated before this
   credential is exposed.
4. A deterministic publisher mints a fresh narrow App token, rechecks the exact
   triggering-comment version and both SHAs, independently validates the receipt
   and output contract, sanitizes and re-bounds the response, and updates only
   the App-owned admission comment. It repeats the source/base/head checks after
   publication and neutralizes in-flight drift without deleting the admission.

The model never receives the token that can comment on the repository. A
force-push or base-branch advance causes the prepared review to be discarded
instead of attached to a different diff.
Raw model output and CLI stderr stay outside the artifact upload allowlist;
only the receipt, bounded review, and numeric exit code cross to the publisher.
Artifact IDs, rather than attempt-derived names, bind partial job reruns to the
actual upstream artifacts.

This replaces the earlier design that authorized on GitHub-hosted then scheduled
a `clawsweeper-dinkuskit` Spark runner (blocked for public credential boundary).

## Product-repo caller (thin)

```yaml
name: ClawSweeper command

on:
  issue_comment:
    types: [created]

permissions:
  contents: read
  issues: read
  pull-requests: read

jobs:
  review:
    uses: dinkuskit/.github/.github/workflows/clawsweeper-command.yml@<reviewed-full-commit-sha>
    with:
      clawsweeper_app_id: ${{ vars.CLAWSWEEPER_APP_ID }}
      clawsweeper_app_bot_login: ${{ vars.CLAWSWEEPER_APP_BOT_LOGIN }}
    secrets:
      CLAWSWEEPER_APP_PRIVATE_KEY: ${{ secrets.CLAWSWEEPER_APP_PRIVATE_KEY }}
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

`issue_comment` workflows always execute from the repository **default branch**.
Production callers pin the reusable workflow to its reviewed full commit SHA;
do not substitute a mutable branch reference.

## Activation checklist (human)

1. With human approval, create a **DinkusKit-owned** private ClawSweeper GitHub
   App, give it only Issues read/write and Pull requests read, and install it on
   the selected product repositories. The existing private
   `saari-clawsweeper` App is owned by `saari-co` and cannot be reused for this
   installation.
2. Set Actions variables `CLAWSWEEPER_APP_ID` and
   `CLAWSWEEPER_APP_BOT_LOGIN` (including `[bot]`), plus secret
   `CLAWSWEEPER_APP_PRIVATE_KEY`, for the selected repositories.
3. With human approval, merge this reusable workflow to `dinkuskit/.github`
   `main`, then record the resulting full commit SHA in each caller.
4. With human approval, set org (or repo) Actions secret
   **`COPILOT_GITHUB_TOKEN`**: a user-owned fine-grained PAT with **Copilot
   Requests only**.
5. Merge thin caller into each product repo (`blocks`, `bundles`, …).
6. On a current PR as OWNER/MEMBER/COLLABORATOR/CONTRIBUTOR, comment
   `@clawsweeper review` alone on a line.
7. Confirm eyes reaction, Actions run, advisory comment, rocket.

The App/private-key setup is required for contributor self-service: the shared
`github-actions[bot]` identity is intentionally not accepted as quota
authority. The private key and short-lived App tokens appear only in fixed
gate/publisher steps and never enter the model job. Spark runner registration
is **not** required for path B.

Primary review requests are deduplicated per base/head pair. A permissionless
preflight admits only standalone command-shaped comments from trusted, non-bot
PR participants to the repository-wide lock. The locked gate then re-fetches
and authoritatively validates the source comment before reserving quota;
App-authored, untrusted, and non-command comments never enter the lock.
Established contributors receive one hosted run per PR and share a hard
allowance of five contributor-triggered reviews per repository per UTC day;
maintainers may request one re-review after a bot-authored canonical admission
for the same base/head pair, including recovery from a pending, stale, failed,
or blocked attempt. Admitted model jobs use a separate expanded repository-wide
queue so only one spends Copilot credits at a time. The CLI receives
`--max-ai-credits=50`; this is a soft session guard and an in-flight response
can exceed it, so the hard controls are the run-admission limits rather than a
currency guarantee. Missing or malformed
artifacts produce a deterministic blocked advisory rather than silently
skipping publication.
Failed, stale, and blocked contributor admissions consume the allowance;
maintainer admissions do not consume the contributor daily allowance.
Editing or deleting the triggering command after admission neutralizes
publication while retaining the admission record.

## Explicitly not this path

- Persistent public Spark self-hosted runners
- ChatGPT subscription / `CODEX_HOME` on a shared host for public PR tools
- Auto-review of every PR from first-time fork authors
