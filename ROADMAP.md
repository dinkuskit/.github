# DinkusKit roadmap

**Current direction: 2026-09-26.** This is the canonical whole-kit roadmap.
Read the durable [vision](VISION.md) first. Repository roadmaps retain their
component backlogs; they do not independently reorder the whole kit.

## Confirmed goal

Deliver a working EmDash e-commerce store operable by a non-technical human
from the EmDash admin. Agents can use the same durable operations.
**Commerce and Inventory are crucial launch pieces and launch side by side.**
Inventory is not deferred behind Commerce. There is no launch date or release
readiness claim here.

## Now — approved focus

### Store Template: real Commerce Products drive the catalog

The approved current slice is a shop-owner workflow, not another editorial
product list:

1. Manage the real product in Commerce Products in the EmDash admin.
2. Set Regular to list that product publicly.
3. Set or update Sale and see the public price update.
4. Clear Regular to hide the product publicly while retaining it in admin.

Prove admin saves, reload persistence, public list/detail behavior, and the
hide-without-delete round trip. An explicitly set zero Regular is distinct
from missing Regular. This is approved work, not a statement that the Store
Template has already completed it, and it does not claim a cart or checkout.

### Keep Commerce and Inventory on one launch path

Develop both crucial pieces alongside the integrated storefront. Commerce owns
product and order policy; Inventory owns stock and fulfillment quantity effects.
Their individual kernel progress does not establish an admin-operable end-to-end
store. Close the human-operation and integration gaps as part of launch work,
not as an optional Inventory extension afterward.

## Next — proposed sequencing, not locked contracts

After the current catalog slice, choose bounded work by the missing step in a
complete shop-owner journey. This is a planning proposal, not authorization for
new payment, order, shipping, inventory or UI contracts:

| Workflow | Intended outcome | Evidence needed before claiming it works |
| --- | --- | --- |
| Prepare products and stock | A clerk configures a sellable product and its stock source; sees availability and setup problems | Real admin operations, explicit location/provider binding, durable read-back, public availability and safe provider-failure behavior |
| Purchase | A shopper can move from product selection through cart and payment to a durable order and receipt | Integrated successful purchase plus failure/retry paths; no duplicate order, payment or stock effects; customer and operator results agree |
| Fulfill | A clerk can act on the order and its stock-backed tickets through the approved packing and delivery lifecycle | Human admin proof joined to Inventory receipts and quantities; partial packing, remaining reservations, correction and replay where the owning contract supports them |
| Recover and operate | A clerk can understand failed or unknown outcomes, inspect history and resume safely | Reload/restart and retry proof, useful errors, permission checks and operator-visible recovery without direct database edits |

Commerce owns the order and purchase workflow. Inventory owns reservation and
stock effects. Store Template demonstrates them together; Blocks supplies
editable composition without duplicating those rules. Exact next slices and
unsettled contract details must be decided in the owning repositories.

## Later — proposed, not launch prerequisites

Advanced promotions, coupons and bundles can follow the core product, purchase
and fulfillment journey. Broader templates and additional composition features
remain candidates driven by demonstrated needs. This is not a cancellation of
component backlogs and does not defer Inventory.

## Evidence and status discipline

- Distinguish a locked decision, an implemented kernel, an admin workflow and
  a proven integrated store. None is a substitute for the next.
- Record exact source/dependency pins and sanitized evidence. UI work needs
  admin and public proof, including desktop/mobile where relevant.
- Verify initialized-state upgrades, durable read-back and failure recovery
  when a slice changes persistence or operation semantics.
- Repository [Commerce](https://github.com/dinkuskit/commerce#status),
  [Inventory](https://github.com/dinkuskit/inventory#status),
  [Blocks](https://github.com/dinkuskit/blocks) and
  [Store Template](https://github.com/dinkuskit/template-store#current-proof)
  documentation is the live implementation record. Open PRs are not shipped work.
- Publication, deployment and production changes remain separate human gates.
  This roadmap authorizes none of them and does not claim a built checkout.

## Snapshot basis

Checked the public default-branch documentation on 2026-09-26: Commerce describes
Products with Regular/Sale administration; Inventory describes durable stock
kernels but not a complete installable admin plugin; Store Template describes an
availability/catalog proof with non-purchasable previews, not checkout.
These observations motivate the integration work; they are not a release
assessment. Update this dated roadmap when the direction changes, rather than
turning a proposed sequence into an enduring product rule.
