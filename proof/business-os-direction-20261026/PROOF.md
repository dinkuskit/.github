# Business OS direction: documentation proof

## Scope and source

- Repository: `dinkuskit/.github`.
- Base: `0e553b1fc88fe361c091a32e320d60d85b961bab`.
- Scope: organization profile, vision, planning reference and contributor guidance.
- No runtime code, repository settings, release scope or existing GrillTrack
  records changed. This is documentation proof, not proof that planned product
  capabilities are implemented.

The document hashes below bind this check to the reviewed content without
requiring a self-referential commit hash:

| File | SHA-256 |
| --- | --- |
| `profile/README.md` | `d5a0048df0c75a37096841764566d5355ce9094bd6fad2328310a8cecb8d2081` |
| `VISION.md` | `7f82951ec27c2f88ee88278a6d3c31d9dd59173b77ef92aa6d99262d6ae49064` |
| `ROADMAP.md` | `8acb16bf86456e7e969d81ef35568a1116779dd1608a4e86dfcd6ef8ed42bfac` |
| `CONTRIBUTING.md` | `96d8ac39bfb8627e102f7a3744a536915c546e263215c3b96dda87975f160e07` |

## Checks on October 26, 2026

- `git diff --check`: passed.
- Relative Markdown links and the `v1-store-baseline` anchor: resolved.
- Public repository links: all 14 targets were accessible and public using
  GitHub repository metadata. Profile links to the new `CONTRIBUTING.md` target
  this PR's file and become available on `main` when merged.
- Destination sentence: preserved exactly in the profile and vision.
- The four v1 acceptance steps: compared byte-for-byte with the base and
  unchanged. Optional work is not presented as restarted or committed work.
- Existing `.grilltrack/ledger.json` and `.grilltrack/events.jsonl`:
  byte-for-byte unchanged.
- Public copy: reviewed for private operating context and misleading release
  claims; a targeted private-reference scan found no matches.
- Current public README checks support the two new component descriptions:
  [DinkusGuide](https://github.com/dinkuskit/dinkus-guide) is a read-only,
  source-backed guide; [Books](https://github.com/dinkuskit/books) is a design
  stub without an installable plugin.

## Profile rendering

Rendered the proposed profile using GitHub's Markdown API in GFM mode with
`dinkuskit/.github` context, then local Chromium with a GitHub-like typography
stylesheet. Both full-page previews were visually inspected: the three-star
opener, section hierarchy, links and text remain readable without clipping.
The browser measured no horizontal overflow at either viewport.

| Viewport | Document width | Document height |
| --- | --- | --- |
| 1024 px | 1024 px | 1595 px |
| 360 px | 360 px | 2459 px |

These are local previews, not screenshots of a deployed organization profile.
They do not reproduce GitHub account chrome or exact production CSS.

## Immutable preview assets

Only public documentation appears in these images. No account chrome,
credentials, private business details or local filesystem paths are visible.
Both assets were published without replacing an existing asset.

- [Desktop preview](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-business-os-20261026/profile-desktop.png): 268948 bytes; SHA-256 `7e21168f9632fa578e3732e885f5445af6e6242ce3ddb44cd04e59ac04061e0c`.
- [Mobile preview](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-business-os-20261026/profile-mobile.png): 254499 bytes; SHA-256 `4e01e10ac92c7a27864b0a27ff8a6acd262b8af9302e34fd84ccc5171d0e9379`.

## Review limits

No CI workflows or native-review sender workflow exist in this repository at
this source. None were added or configured. External review results and their
exact source binding belong in the PR conversation; this document does not
claim a clean review verdict. No merge or product deployment was performed.
