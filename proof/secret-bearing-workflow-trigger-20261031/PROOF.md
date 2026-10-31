# Secret-bearing workflow trigger guard

- Base: `4ff41ca7` (`origin/main`).
- Finding class: `secret-bearing-workflow-trigger`, recurring ×6 across
  `dinkuskit/inventory`, `dinkuskit/payments`, `dinkuskit/commerce` and
  `dinkuskit/template-store`.
- Scope: add the reusable `.github/workflows/workflow-lint.yml` (zizmor,
  actionlint and the custom `secret-bearing-workflow-trigger` rule), the rule
  in `scripts/secret_bearing_workflow_trigger.rb`, and its fixture tests.

## Rule

On `pull_request_target` or `issue_comment`, a job that passes secrets
(`secrets: inherit` or a mapping) to a reusable workflow must directly `needs`
a gate job. The gate job's step with an `id` must query the actor's repository
permission. The job must export that step's output, and the calling job's `if`
must require `needs.<gate>.outputs.<name> == 'true'`. The `if` must not use
`||` or `!` negation. actionlint has no plugin interface, so the rule runs
beside it and reports in actionlint's `path:line:col: message [rule]` format.

## Verification

```text
ruby tests/test_secret_bearing_workflow_trigger.rb
actionlint
actionlint tests/fixtures/secret-bearing-workflow-trigger/*.yml
ruby scripts/secret_bearing_workflow_trigger.rb
git diff --check
```

Result: 11 runs, 50 assertions, 0 failures, 0 errors, 0 skips. The tests
include running the fixture gate's script against a fake `gh`. For `read`,
`triage` and `none` actors, the gate exits non-zero with `allowed=false`. For
`write`, `maintain` and `admin` actors, it passes with `allowed=true`. The
fixtures also show that the secret-bearing `uses:` job requires that output.
actionlint and the rule passed on this repository's workflows, and actionlint
accepted every fixture.

zizmor could not be run locally because it is not installed on this machine,
and this lane does not install tools. It first runs in this repository's
`Workflow lint` CI.
