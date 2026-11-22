# Organization profile README refresh: documentation & visual proof

## Scope and source

- Repository: `dinkuskit/.github`
- Branch: `docs/profile-readme-refresh-20261122`
- Base: `2278ae453fbd08c6d40ad6f8a82997bbff052590`
- Scope: update `profile/README.md` to include `dinkuskit/accounts` and
  `dinkuskit/reviews` alongside current public storefront, agent, and template
  repositories, and add dual-theme (`prefers-color-scheme: dark` / `light`)
  header banners and architecture diagrams aligned with DinkusKit's Stitch
  Emerald & Ultraviolet brand system (`dinkuskit/dinkuskit` `.stitch/DESIGN.md`).
- No runtime code, workflows, repository settings, organization settings, or
  v1 scope boundaries changed.

## Content hashes

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `profile/README.md` | text | `9ee21266b2469df8404f99136a2d7f54eb9b99935327c441d3e3aa7f4a2ae3d1` |
| `profile/assets/banner-dark.jpg` | `175,979` (`1600×900` JPEG) | `1ae6e5ff29675bc8a6fd7fc55757b6d2a40e8da087bd099adb284609ddf00296` |
| `profile/assets/banner-light.jpg` | `199,673` (`1600×900` JPEG) | `650d646d0983dac81e34ff5c8c0a3f59ae5f13a5af446520659f64de55444e90` |
| `profile/assets/kit-architecture-dark.svg` | vector (`980×250` SVG) | `41346ea0ff71f96b9300635bf06671993ceed6f0f6ca1f14b09548a39b3531f3` |
| `profile/assets/kit-architecture-light.svg` | vector (`980×250` SVG) | `9d9281a6f501a8582ce880d2ce260375597e95708a22fc06e5bf020e2577de17` |

## Checks on November 22, 2026

- `git diff --check`: passed (0 whitespace issues).
- `ruby tests/test_pin_audit.rb`: 14 runs, 55 assertions, 0 failures.
- `ruby tests/test_secret_bearing_workflow_trigger.rb`: 11 runs, 50 assertions, 0 failures.
- `smoky-github-design/scripts/verify_github_assets.py` (`--repo-visibility PUBLIC --forbid-in-public dinkus-pr-assets --forbid-in-public swarm-pr-assets --allow-public-shelf dinkuskit/.github`):
  `"ok": true`, 0 errors, 0 warnings; both banners verified at `1600×900` (`1.7778`
  aspect ratio, `< 200 KB`), `<picture>` dark/light sources and non-empty `alt`
  attributes verified.
- Public repository link check (`gh api repos/<owner>/<repo>`): all 18 linked
  repositories (`dinkuskit/.github`, `commerce`, `payments`, `ship`, `accounts`,
  `reviews`, `inventory`, `coupons`, `bundles`, `dinkuskit`, `openclaw`,
  `pi-durable`, `dinkus-guide`, `books`, `template-store`, `template-services`,
  `template-marketing`, and `emdash-cms/emdash`) verified `public` and
  `archived=false`. No private repositories or internal hostnames referenced.
- External URL and anchor check: `https://dinkuskit.com` returned `HTTP/2 200`;
  `VISION.md#packaging-and-independent-operation` and
  `ROADMAP.md#v1-store-baseline` verified against live headings.
- Source fidelity check:
  - Exact destination sentence from `VISION.md` preserved verbatim.
  - `accounts` described honestly as **Scaffold** (shopper sign-in via emailed
    6-digit code and saved addresses; accounts remain in Commerce until ready).
  - `reviews` described honestly as **Scaffold** (1–5 buyer star ratings and
    reviews; rating rules only, not collecting reviews yet).
  - `openclaw`, `pi-durable`, `dinkuskit`, `dinkus-guide`, and `books` match
    their respective repository README statuses without overclaiming.
- Rendering check:
  - Rendered `profile/README.md` via `gh api markdown` (`mode: gfm`,
    `context: dinkuskit/.github`) and captured headless Chrome desktop previews
    (`1024×2550`) for both Dark (`prefers-color-scheme: dark`) and Light
    (`prefers-color-scheme: light`) variants, resolving the
    `raw.githubusercontent.com/dinkuskit/.github/main/profile/assets/*` URLs
    to local tracked files for pre-merge inspection.
  - Visual inspection caught first-column emoji/name wrapping in Markdown
    tables; fixed with `&nbsp;` between each icon and repo link and re-verified
    in both Dark and Light captures.

## Notes and gates

- Absolute `raw.githubusercontent.com/dinkuskit/.github/main/profile/assets/...`
  URLs are used intentionally because GitHub organization profile READMEs
  (`https://github.com/dinkuskit`) do not resolve repo-relative image paths
  from `.github/profile/`. Those URLs return HTTP 200 once this PR merges to
  `main`.
- Merge remains gated on owner approval and CI/review completion.
