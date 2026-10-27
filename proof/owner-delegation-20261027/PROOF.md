# Owner delegation principle

- Base: `ad903228db64e95c7fa985857df562e9a580c6a8`.
- Scope: add the approved owner-delegation sentence as its own paragraph near
  the top of `VISION.md`, alongside the original destination.
- `VISION.md` SHA-256:
  `23cafae55e1b8457f37203de68ce49699029b29e2ccbadd509e290db83aa548c`.

## Verification

- `git diff --check`: passed.
- Removing the added paragraph reproduces the base `VISION.md` byte-for-byte;
  no existing principle, license notice or link changed.
- `ROADMAP.md`, `profile/README.md`, `LICENSE-DOCUMENTS.md` and both existing
  GrillTrack ledger/event files match the base byte-for-byte.
- No commercial terms, staffing commitments, release scope or product
  implementation claims were added.
- Documentation only; no runtime, deployment or profile rendering change.

Exact-head external review results are recorded in the PR. This repository
has no CI or native-review sender workflow at this base; none was added.
