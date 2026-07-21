# Profile composition proof

## Accepted lock

- Decision: `profile-composition-001`
- Choice: `Section manual`
- Baseline: `profile/README.md` at
  `82c034649d7800c0054dbd86f486410ca8ca1d78`
- Dependencies: none
- Confirmed boundary: definition-first profile, emoji-led page/commerce/starter
  chapters, star dividers, verified repo facts, and local desktop/mobile proof.
  Exact copy, emoji density, final logo treatment, org settings, delivery, and a
  separate GitHub Pages site remain outside this cycle.

## Implementation

- `profile/README.md`
- Replaced the short baseline with the locked Section-manual composition.
- Preserved the EmDash, npm namespace, MIT-license, and build-in-public claims
  from the baseline.
- Linked every public product and starter repository represented in the chosen
  composition.

## Verification

Commands and interactions:

```text
git diff --check
jq -Rs '{text: ., mode: "gfm", context: "dinkuskit/.github"}' profile/README.md | gh api markdown --input -
gh api repos/dinkuskit/<repo>
gh api repos/emdash-cms/emdash
Playwright desktop capture at a 736 px content width
Playwright mobile capture at a 320 px content width
Playwright mobile horizontal-overflow assertion
Direct visual inspection of both captures
```

Results:

- Git diff whitespace check passed.
- GitHub's Markdown API accepted and rendered the README.
- All seven linked DinkusKit repositories and the EmDash repository resolved as
  public GitHub repositories.
- Desktop rendering preserves the selected editorial hierarchy and spacing.
- Mobile rendering reflows without horizontal overflow or clipped content.
- The first mobile proof attempt was rejected because the standalone proof
  iframe clipped the lower page. The iframe height was corrected and both
  screenshots were recaptured and directly inspected.

Artifacts:

- `desktop.png`
- `mobile.png`
- Working renderer:
  `.grilltrack/work/profile-composition-render.html`

## Fidelity and remaining risk

- The Markdown HTML comes from GitHub's Markdown API. Visual styling uses
  `github-markdown-css` in a local proof renderer, so surrounding GitHub org
  chrome and possible small production CSS differences are not represented.
- The npm organization URL is preserved from the accepted baseline. An
  automated request received HTTP 403, so availability was not claimed from
  that probe.
- The new Dinkus logo was not present in the fetched/local
  `smoky-brand-assets` branches inspected during this cycle. The top mark remains
  the confirmed interim three-star treatment until the imagery grill locates
  the asset.
- Copy voice and emoji density are working content needed to realize the locked
  composition; they are not yet independently locked.
