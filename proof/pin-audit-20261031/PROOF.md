# Pin audit guard

- Base: `4ff41caa493b758f4601be1448137b01d1b511ae`.
- Finding class: `unreviewed-external-pin` (x30 across dinkuskit/payments,
  dinkuskit/commerce, dinkuskit/inventory, dinkuskit/template-store,
  dinkuskit/ship and saari-co/x-api).
- Scope: add the reusable `.github/workflows/pin-audit.yml`, its guard script
  `scripts/pin_audit.rb`, the `reviewed-pins.json` manifest, and fixture
  tests.

## Behavior

- A pin is an external `uses: owner/repo[/path]@<40-hex>` in a job, step or
  composite action, or a step that checks out another repository with a
  literal `repository:` and a 40-hex `ref:` (skills and runtimes).
- Each pin must be listed in `reviewed-pins.json` on dinkuskit/.github `main`
  as `{ "repository", "sha", "review" }`; otherwise the job fails with an
  annotation on the pinning line.
- For each unreviewed pin the source is fetched and a diff from the last
  reviewed SHA of that repository (or the full tree when none is reviewed) is
  uploaded as the `pin-audit-source-diffs` artifact. An unfetchable source
  still fails.
- YAML scalars are read raw, so an all-digit or exponent-looking SHA is not
  coerced to a number and skipped.

## Verification

- `ruby tests/test_pin_audit.rb`: 14 runs, 55 assertions, 0 failures.
- `actionlint`: passed.
- `ruby scripts/pin_audit.rb --manifest reviewed-pins.json`: 0 pins, 0
  unreviewed.
- `git diff --check`: passed.

## Limits

- Tag and branch refs are not pins and are not audited.
- `reviewed-pins.json` starts empty. A caller's pin of this workflow must be
  added to the manifest after review before that caller passes.
- Skill or runtime SHAs pinned outside workflow `uses:`/checkout steps (for
  example in lockfiles or `run:` scripts) are not detected.
- No caller repository was changed; each dinkuskit repository adopts the
  reusable workflow separately.
