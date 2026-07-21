# ClawSweeper command workflow (path B)

Public DinkusKit product repositories call the reusable workflow:

`.github/workflows/clawsweeper-command.yml` in this org repo.

## Who can trigger

| Association | Can run `@clawsweeper review`? |
| --- | --- |
| `OWNER`, `MEMBER`, `COLLABORATOR` | Yes |
| `CONTRIBUTOR` (usually after a **merged** PR) | Yes |
| `FIRST_TIME_CONTRIBUTOR` / `FIRST_TIMER` / `NONE` | No — a trusted person must comment for them |

Command must be **alone on a line**. Inline prose is ignored.

```text
@clawsweeper review
```

Re-review after a prior verdict:

```text
@clawsweeper re-review
```

## What runs

1. A deterministic gate on GitHub-hosted `ubuntu-latest` fetches the exact
   public PR diff and records the head SHA.
2. An isolated `ubuntu-latest` model job runs pinned Copilot CLI with
   **`gpt-5.6-terra`**. It receives only the Copilot Requests PAT: no repository
   token, checkout, shell/file tools, built-in MCP, or mutation permission.
3. A deterministic publisher rechecks the head SHA, bounds the response, and
   posts one advisory PR comment with its own short-lived `GITHUB_TOKEN`.

The model never receives the token that can comment on the repository. A
force-push causes the prepared review to be discarded instead of attached to a
different head.

This replaces the earlier design that authorized on GitHub-hosted then scheduled
a `clawsweeper-dinkuskit` Spark runner (blocked for public credential boundary).

## Product-repo caller (thin)

```yaml
name: ClawSweeper command

on:
  issue_comment:
    types: [created]

permissions:
  actions: read
  contents: read
  issues: write
  pull-requests: read

jobs:
  review:
    uses: dinkuskit/.github/.github/workflows/clawsweeper-command.yml@main
    secrets:
      COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}
```

`issue_comment` workflows always execute from the repository **default branch**.

## Activation checklist (human)

1. With human approval, merge this reusable workflow to `dinkuskit/.github`
   `main`.
2. With human approval, set org (or repo) Actions secret
   **`COPILOT_GITHUB_TOKEN`**: a user-owned fine-grained PAT with **Copilot
   Requests only**.
3. Merge thin caller into each product repo (`blocks`, `bundles`, …).
4. On a current PR as OWNER/MEMBER/COLLABORATOR/CONTRIBUTOR, comment
   `@clawsweeper review` alone on a line.
5. Confirm eyes reaction, Actions run, advisory comment, rocket.

App installation for `saari-clawsweeper` is optional for path B (comments can
post as `github-actions[bot]` via `GITHUB_TOKEN`). Spark runner registration is
**not** required for path B.

Primary review requests are deduplicated per PR head and serialized per PR.
Use `@clawsweeper re-review` only after a bot-authored prior verdict.

## Explicitly not this path

- Persistent public Spark self-hosted runners
- ChatGPT subscription / `CODEX_HOME` on a shared host for public PR tools
- Auto-review of every PR from first-time fork authors
