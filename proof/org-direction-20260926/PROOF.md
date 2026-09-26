# Organization direction profile proof

## Source and scope

- Profile after source: `33fe99ed3624b1af3cfe9a5f3f6261736041260f`.
- Profile before source: `3cd01768907d07bc8b58d58870ea336540f4fa10`.
- Subsequent proof-only commit does not change the rendered profile.
- GitHub Markdown API, GFM context `dinkuskit/.github`; local Playwright
  Chromium renderer with `github-markdown-css` light styling.
- Desktop viewport 1024 px, content 736 px; mobile viewport 360 px, content
  320 px. Full-page captures, both before and after.
- No horizontal overflow at either width. All four captures directly inspected:
  complete content, readable hierarchy, and no clipping.
- Sanitization: only public documentation rendered; no browser account chrome,
  credentials, operator data or local filesystem paths appear in the images.
- This is profile-only visual proof. There is no admin or storefront behavior
  change to exercise, and no deployment. GitHub org chrome and small production
  CSS differences are not represented. Actual deployed profile remains unchanged
  until this PR is merged.

## Verification

- `git diff --check`: passed.
- Markdown relative file links resolve in the proposed source trees.
- Canonical `main` links intentionally become live when this docs PR merges;
  dependent repository PRs must wait for it. Proposed files are reviewable here.
- Public copy reviewed for scope and private operating context; no release
  date, built checkout or release-readiness promise added.
- Confirmed goal is separate from proposed sequencing; Commerce and Inventory
  remain crucial side-by-side launch pieces.

## Immutable sanitized media

- [after-desktop.png](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-direction-20260926/after-desktop.png) — 179685 bytes; SHA-256 `51dc68c629585195e4a0ea98930a4aeda50c061213ea4de2898d67bfb2ddd7b3`.
- [after-mobile.png](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-direction-20260926/after-mobile.png) — 172539 bytes; SHA-256 `cdcc8f7d0a1fd0461ce58e16aec3fc70bf22f0ac2a353a3fbd245202b3363426`.
- [before-desktop.png](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-direction-20260926/before-desktop.png) — 143478 bytes; SHA-256 `3c0828eb24f7cee6b5e891ad698c415ee7cb0943fa3f71e11c5294c93ae11353`.
- [before-mobile.png](https://github.com/dinkuskit/dinkus-pr-assets/releases/download/org-direction-20260926/before-mobile.png) — 137967 bytes; SHA-256 `588086b2fc5203091657a2f1da42a9afd46938a2e7d20471d4ac4b5450fa47f2`.
