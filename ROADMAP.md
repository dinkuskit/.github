# DinkusKit scope and planning

Read the [vision](VISION.md) for the destination and product principles. This
file retains the `ROADMAP.md` address for existing links. It records the v1
store baseline and how work is selected; it is not a dated feature schedule.

## How work becomes a commitment

- **Research** answers a specific question with evidence. It may end in an
  experiment, a recommendation or a question that remains open.
- **Accepted design** records a product decision. It can remain inactive
  until there is a reason and capacity to build it.
- **Active work** has an explicit scope, owner and observable completion
  criteria in its owning repository.

A high-priority question may still need research. A fully designed capability
may deliberately wait. Our stores supply the initial operating needs; feedback
from other merchants also informs priorities. Select work for a useful business
outcome, its dependencies and the evidence needed to show it works, rather than
trying to reproduce another product's feature list.

New research normally informs the next relevant decision. It should not
continually expand a release already underway. If a finding justifies changing
active work, make the tradeoff and its effect on scope explicit. Unsettled
questions belong in existing issues or proposals, with one primary record and
cross-repository links; see [contributing](CONTRIBUTING.md).

## v1 store baseline

This baseline was established on October 10, 2026. The broader business-OS
direction preserves it; the list below is an acceptance contract, not a claim
about today's completion status.

v1 is a working EmDash store, installed from the Registry, that a
non-technical human can run from the admin. It is done when a shop owner can:

1. **List products.** Add products with Regular and Sale prices, hide and show
   them, and set manual availability (in stock, out of stock, backorder).
2. **Take a paid order.** A shopper checks out as a guest and pays by card.
   Stripe and Authorize.net are both qualified before launch, Stripe first;
   each store uses one. Physical items need a U.S. delivery address (the
   store's shipping countries are set to the U.S. only). Free or flat-rate
   shipping is charged at checkout.
3. **Fulfill it in the U.S.** The owner sees the order and buys and prints a
   USPS label for it from the admin, and the order then shows as shipped with
   its tracking number. A store without Ship marks the order shipped by hand
   with a tracking number. **USPS label purchase and printing is required for
   v1.**
4. **Recover.** Failed or unknown payments, retries and missing orders are
   understandable and fixable from the admin without editing data by hand.

Test orders are kept in the normal order list, clearly marked TEST, and never
trigger real fulfillment or postage.

**Proof that v1 works:** a Registry-installed store with current Commerce,
Payments and Ship takes one paid TEST order, sees it in Orders and in Payments'
setup, and buys and prints a USPS label in the carrier's test environment,
all from the admin. Publishing to the Registry, deploying and going live with
real payments stay separate go-aheads from the owner.

**Optional for this baseline:** Inventory (managed stock) and basic coupons.
A store without them uses manual availability and sends no coupon code at
checkout. Neither blocks the four steps above. Inclusion here does not restart
or prioritize work in either repository.

**Outside this baseline:** international shipping and labels, other carriers,
live postage rates at checkout, weight or zone shipping rates, tax, customer
accounts, refunds from the admin, bundles and advanced promotions. These remain
candidate areas, not a promise of their order or inclusion in the next release.

v1 must fit the Registry's current size limits. Check the actual build when a
plugin changes; an old bundle-size measurement is not present-day proof.

## Current implementation status

Use the owning repositories' documentation, releases and verification evidence:

- [Commerce](https://github.com/dinkuskit/commerce)
- [Payments](https://github.com/dinkuskit/payments)
- [Ship](https://github.com/dinkuskit/ship)
- [Store Template](https://github.com/dinkuskit/template-store)
- [Accounts and hosted service connections](https://github.com/dinkuskit/dinkuskit)
- [Inventory](https://github.com/dinkuskit/inventory) and [Coupons](https://github.com/dinkuskit/coupons)

The October 10 `Now`, `Done` and deployment snapshot previously in this file
are historical, not current status. They remain available in Git history;
duplicating them here would obscure the owning repositories' newer evidence.
Open PRs and merged code alone do not establish published or deployed behavior.

## Decisions still to make

The [vision](VISION.md) sets direction for independent plugins, portable
knowledge, optional assistants and operation in a merchant's own Cloudflare
account. Packaging and authentication for self-hosting, shared knowledge
storage, detailed agent permissions, and the boundaries of marketing or email
capabilities still need focused decisions and proof. They are not additions to
v1 or a prescribed workflow list.

## Evidence and status discipline

- Distinguish a locked decision, implemented code, an admin capability and a
  proven integrated result. None is a substitute for the next.
- Record exact source/dependency pins and sanitized evidence. UI work needs
  admin and public proof, including desktop/mobile where relevant.
- Verify initialized-state upgrades, durable read-back and failure recovery
  when a slice changes persistence or operation semantics.
- Keep implementation status in the owning repository and link it here rather
  than maintaining a second backlog.
- Publication, deployment, real postage and production changes remain
  separate human gates. This document authorizes none of them.

---

This document is licensed under the [MIT License](LICENSE-DOCUMENTS.md).
