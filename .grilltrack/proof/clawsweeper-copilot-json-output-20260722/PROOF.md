# ClawSweeper Copilot structured-output repair

Date: 2026-07-22 America/New_York

## Trigger

- `dinkuskit/blocks` PR
  [#7](https://github.com/dinkuskit/blocks/pull/7) reached the isolated Copilot
  model job in run
  [29919272143](https://github.com/dinkuskit/blocks/actions/runs/29919272143).
- Copilot CLI exited `0`, but the workflow converted the result to exit `21`
  because its plain-text response did not satisfy the bounded terminal-marker
  contract. The App published a deterministic
  [`blocked`](https://github.com/dinkuskit/blocks/pull/7#issuecomment-5045702842)
  advisory.
- The allowlisted receipt showed an untruncated, reviewable 39,043-byte diff
  bound to base `c9c9e20167165c9c6907bff7205d3a94a2d6ee4d` and head
  `a1cb3d51a9f23ab8522d77f1e428638f2218512f`. Raw model output and CLI stderr
  were not inspected or published.

## Diagnosis

Authentication, App admission, immutable request preparation, and Copilot model
access all succeeded. The failure was the workflow's own response boundary:
`--silent` returned unconstrained assistant text, while correctness still
depended on a model-authored marker being present exactly once as the final
non-empty line.

The pinned `@github/copilot` `1.0.73` command and package schema confirm:

- `--output-format=json` emits one JSON object per line;
- `--stream=off` is supported;
- the terminal CLI object is `type: result` with an `exitCode`;
- the root assistant text is `assistant.message.data.content`, and root events
  omit `agentId`.

Upstream `saari-co/clawsweeper` at
`43a2ae1f272f434ad6df9b6e26c725a878dbe1f9` does not use Copilot CLI, but it
does establish the relevant pattern: validate a structured application object,
keep process streams private, and render public review Markdown from trusted
code instead of trusting model prose as a control field.

## Repair

- Invoke the pinned Copilot CLI with bounded, non-streaming JSONL output.
- Keep JSONL, extracted assistant content, parsed content, and stderr under the
  private runner temp directory and remove them with an `EXIT` trap. None are
  added to the artifact allowlist.
- Require an all-object JSONL stream, a successful terminal `result`, and
  exactly one root `assistant.message` with non-empty string content.
- Parse that content as an exact versioned application object with only
  `schema_version`, `verdict`, and `review_markdown`; reject extra keys, invalid
  types, invalid verdicts, embedded verdict markers, empty content, oversized
  content, and prohibited clean verdicts on incomplete diffs.
- Accept only an optional whole-response JSON fence, not surrounding prose or
  heuristic JSON extraction.
- Sanitize the validated Markdown and append the sole canonical
  `clawsweeper-verdict:` line deterministically from the validated enum.
- Preserve fail-closed blocked publication with content-free failure reasons.

## Verification

```text
python3 -m unittest tests/test_clawsweeper_workflow.py
ruby -e 'require "yaml"; YAML.parse_file(".github/workflows/clawsweeper-command.yml")'
git diff --check
```

Results:

- 42 workflow-contract tests passed with one expected caller-template skip.
- Executable mocked-Copilot cases cover valid JSONL, deterministic verdict
  rendering, mention neutralization, whole-response fences, malformed and
  oversized streams, missing/failed terminal results, duplicate/malformed root
  messages, strict object rejection, embedded markers, incomplete-diff clean
  prohibition, native CLI failures, stderr privacy, and private-file cleanup.
- YAML parsing and diff hygiene passed.
- An independent read-only security review reported clean at P0-P2 and verified
  the event assumptions against the pinned 1.0.73 package schema.

References:

- [Copilot CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [Copilot CLI programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)
- [Copilot CLI v1.0.73](https://github.com/github/copilot-cli/releases/tag/v1.0.73)

## Gates and next proof

- Human approval is required to merge this reusable-workflow repair and the
  product repository's exact caller pin.
- PR #7 has already consumed both admissions for its current base/head pair.
  After both repairs are active, creating a new PR head (for example, a
  tree-preserving empty commit on its branch) is a separate source mutation and
  requires Bobby's explicit direction before a fresh `@clawsweeper review`.
- Terminal success remains an App-authored model verdict bound to that new exact
  head.
