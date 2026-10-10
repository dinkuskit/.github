# DinkusKit roadmap

**Current direction: 2026-10-10.** This is the canonical whole-kit roadmap.
Read the durable [vision](VISION.md) first. Repository roadmaps keep their
component backlogs; they do not independently reorder the whole kit.

## v1 scope

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
all from the admin. Publishing to the Registry, deploying and going live with real payments
stay separate go-aheads from the owner.

**Wanted for v1, not required:** Inventory (managed stock) and basic coupons.
Both are being built now and ship with v1 if they are proven in time. A store
without them still launches: products use manual availability, and checkout
sends no coupon code. Neither may block the four steps above.

**After v1:** international shipping and labels, other carriers, live postage
rates at checkout, weight or zone shipping rates, tax, customer accounts,
refunds from the admin, bundles and advanced promotions.

**Size:** v1 must fit the Registry's size limits as they are today (Commerce's
plugin file is about 119 KB of 128 KiB). Each Commerce addition gets a size
check; heavy work goes to hosted services.

There is no launch date or release-readiness claim here.

## Now

- **One paid TEST order, end to end.** Needs a deployed test-mode Payments
  service and its status address, Stripe test keys and webhook, the Accounts
  service and consent page (so Payments' "Connect payments" step can finish),
  and the Payments-to-Commerce check that exactly one paid TEST order exists.
- **Commerce order handoff for Ship.** A stable store and order identity, an
  order revision, and a fulfillment status (shipped, tracking number) that is
  set by hand or by a Ship label. Commerce sends each paid order to the
  hosted Ship service, since EmDash plugins cannot call each other.
- **USPS labels on Registry installs.** A hosted Ship service holding the
  merchant's own Pitney Bowes connection; a way for a Registry plugin to show
  and print a label (not designed yet); refuse postage for TEST orders.
- **Store Template checkout.** Move to Registry-installed Commerce, send the
  delivery address for physical items, send no coupon code until coupons are
  proven, and run the demo on current Commerce.
- **Deploy readiness.** Payments, Ship and Accounts services, plus Accounts
  passes for Ship, prepared for a first deploy. Deploying waits for the
  owner's go.

Inventory and Coupons continue alongside without blocking the items above.
Coupons still need their service deployed, Accounts passes for Coupons, and a
coupon box in the Store Template that shows the refusal reason and lets the
shopper drop the code.

## Open platform question

EmDash's Registry caps each plugin file at 128 KiB. A larger limit has been
asked for, with benchmarks. v1 is planned to ship under the current limit, and
nothing in Now waits on that answer. Sharing data between plugins through
content saves works but is not planned for v1; a direct plugin-to-plugin call
needs upstream EmDash work and comes later.

## Done

- Products drive the Store Template catalog: Regular and Sale prices, hide
  without delete (2026-09-30).
- Registry-first rule for every plugin (2026-10-08).
- Commerce guest checkout with coupon checks and specific refusal reasons,
  delivery address for physical baskets (works once a storefront sends it),
  and an Orders page that keeps its own copy of each paid order. Hosted stores
  get the coupon reasons once the pending coupon-service update lands.
- Payments' Registry setup plugin on the shared store identity.
- Command-line tools for Commerce, Coupons, Inventory and Payments, run from
  a checkout and not yet published. On a Registry store the Commerce tool can
  only read the catalog, and the others need Accounts, which is not deployed.
- Google and Meta product feeds.
- Hosted coupon service and Coupons admin plugin; Inventory plugin under the
  Registry size limit.

Code merged is not the same as proven: none of this is published to the
Registry or deployed yet.

## Evidence and status discipline

- Distinguish a locked decision, an implemented kernel, an admin workflow and
  a proven integrated store. None is a substitute for the next.
- Record exact source/dependency pins and sanitized evidence. UI work needs
  admin and public proof, including desktop/mobile where relevant.
- Verify initialized-state upgrades, durable read-back and failure recovery
  when a slice changes persistence or operation semantics.
- Each repository's own status section is the live implementation record.
  Open PRs are not shipped work.
- Publication, deployment, real postage and production changes remain
  separate human gates. This roadmap authorizes none of them.

## Snapshot basis

Checked default branches on 2026-10-10. Commerce has guest checkout, paid-order
records and delivery addresses on main; Payments has a Registry setup plugin
and a test-mode service; Ship has a private installed label workflow with
offline fixtures and no live provider; the demo runs with Inventory off and
an older Commerce. Update this dated roadmap when the direction changes.
