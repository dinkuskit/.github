# DinkusKit vision

DinkusKit is a kit of plugins and templates for [EmDash](https://github.com/emdash-cms/emdash).
Its first product goal is a working e-commerce store that a non-technical human
can manage from the EmDash admin without changing code. Agents can use the same
durable operations; they do not replace the human operating surface.

## What success means

A shop owner can manage products and prices, understand what is available,
accept a purchase, and carry an order through fulfillment with understandable
results and recovery. Those workflows must work together, not merely exist as
separate package demonstrations.

**Commerce and Inventory are both crucial launch pieces. They launch side by
side.** Inventory is not an optional follow-on to an already-launched Commerce
store. Advanced promotions and bundles can follow the core store workflows.

## Clear ownership

| Component | Owns | Does not own |
| --- | --- | --- |
| [Commerce](https://github.com/dinkuskit/commerce) | Product identity, authoritative prices and sellability, cart, checkout orchestration, orders and Commerce receipts | A second stock ledger |
| [Inventory](https://github.com/dinkuskit/inventory) | Physical stock truth, explicit pools and locations, reservations, stock movements and immutable receipts | Product pricing, checkout or payments |
| [Blocks](https://github.com/dinkuskit/blocks) | Reusable, admin-editable page sections and composition | Commerce or Inventory business rules |
| [Store Template](https://github.com/dinkuskit/template-store) | An integrated storefront and proof of the shop-owner journey | Duplicate product, price or stock authorities |
| EmDash | CMS, content editing and the human administration framework | DinkusKit's commerce or stock contracts |

These are responsibility boundaries, not a claim that every listed capability
is implemented. Repository charters and verified feature documentation describe
individual contracts and their current status.

## Operating principles

- Human admin and agent clients use the same durable, permissioned operations.
- A managed product has one stock authority. Missing or unhealthy stock setup
  must not silently become an invented quantity or a fallback ledger.
- Public storefront facts come from their owning systems, not a second copy in
  page content. Blocks compose the experience; they do not decide the price.
- A successful operation has durable evidence. Retries, unknown outcomes and
  corrections must be understandable without editing data by hand.
- Prove complete workflows on exact source and dependency pins, including
  admin changes, public results, persistence and recovery.

## Direction, not a release claim

This document records the durable product goal. The dated [roadmap](ROADMAP.md)
records current focus and proposed sequencing. Neither document declares a
launch date, release readiness, a built checkout, or permission to publish or
deploy. Product contracts still belong to focused decisions in the owning repo.
