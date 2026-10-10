# DinkusKit vision

DinkusKit makes [EmDash](https://github.com/emdash-cms/emdash) sites into
working online stores. Its first product goal is a store that a non-technical
human can run from the EmDash admin without changing code. Agents use the same
durable operations wherever a durable route exists; they do not replace the
human operating surface. Today the EmDash admin is the complete surface, and
agent routes and command-line tools follow it.

## What success means

A shop owner can manage products and prices, accept a purchase, and get a
physical order to a customer in the United States, with understandable
results and recovery at every step. Those workflows must work together, not
merely exist as separate package demonstrations.

## Shape: small store plugins, hosted services

Every DinkusKit plugin ships as an EmDash Registry plugin: sandboxed,
installed from the Registry, and small enough for the Registry's size limits.
Work that is heavy, shared between stores, or holds processor and carrier
credentials runs in hosted DinkusKit services that the store plugins call.
A native (code-registered) entry is a developer and test setup only; any
feature it has that the Registry build lacks is a listed gap with the work
that closes it.

DinkusKit plans against the Registry's size limits as they are today and does
not depend on them being raised. Inside Commerce, Catalog, Checkout and Orders
stay separate parts with written handoffs, so Commerce can later split into
several plugins or grow in place without a rewrite.

## Clear ownership

| Component | Kind | Owns | Does not own |
| --- | --- | --- | --- |
| [Commerce](https://github.com/dinkuskit/commerce) | Registry plugin | Products, authoritative prices and sellability, cart, checkout, the shopper's free or flat-rate shipping charge, orders, receipt records and fulfillment status | A stock ledger, payment processing, postage |
| [Payments](https://github.com/dinkuskit/payments) | Registry plugin + hosted service | One processor connection per store, processor callbacks, a normalized paid/failed result | Order totals or checkout decisions |
| [Ship](https://github.com/dinkuskit/ship) | Registry plugin + hosted service | U.S. domestic USPS label quote, purchase, print and tracking, using the merchant's own carrier account | Order totals, stock, payment capture |
| [Inventory](https://github.com/dinkuskit/inventory) | Registry plugin + hosted service | Physical stock truth, pools and locations, reservations, stock movements and receipts | Pricing, checkout or payments |
| [Coupons](https://github.com/dinkuskit/coupons) | Registry admin plugin + hosted service | Coupon codes, rules, limits and redemptions, evaluated with a pinned copy of Commerce's own coupon rules | Order totals beyond the discount it returns |
| [Accounts](https://github.com/dinkuskit/dinkuskit) | Hosted service | Merchant accounts, store identity, consent, and the passes each hosted service accepts | Store content or order data |
| [Store Template](https://github.com/dinkuskit/template-store) | Starter site | An integrated storefront and proof of the shop-owner journey | Duplicate product, price or stock authorities |
| EmDash | CMS | Content editing and the human administration framework | DinkusKit's commerce, stock or shipping contracts |

These are responsibility boundaries, not a claim that every listed capability
is implemented. Repository charters and verified feature documentation describe
individual contracts and their current status.

## Operating principles

- Human admin and agent clients use the same durable, permissioned operations.
- A managed product has one stock authority. Missing or unhealthy stock setup
  must not silently become an invented quantity or a fallback ledger.
- Public storefront facts come from their owning systems, not a second copy in
  page content. Page composition never decides the price.
- A successful operation has durable evidence. Retries, unknown outcomes and
  corrections must be understandable without editing data by hand.
- Prove complete workflows on exact source and dependency pins, including
  admin changes, public results, persistence and recovery.

## Direction, not a release claim

This document records the durable product goal. The dated [roadmap](ROADMAP.md)
records v1 scope, current focus and proposed sequencing. Neither document
declares a launch date, release readiness, or permission to publish or deploy.
Product contracts still belong to focused decisions in the owning repo.
