# DinkusKit vision

DinkusKit helps one accountable operator run a business through independently useful, connected tools—with agents doing more of the routine work as reliability and trust grow.

This is a business operating system built around
[EmDash](https://github.com/emdash-cms/emdash), with commerce as its first
proving ground. “One operator” means one accountable person directing the
business, with employees, contractors or agents helping. A business may have
several stores and websites. Small-business needs guide the initial work;
there is no fixed company-size ceiling or claim of enterprise readiness.

Our own stores provide real operating needs and proof. DinkusKit must also be
useful to other merchants, whose requests and priorities should inform its
development. Existing businesses come first, with approachable onboarding for
new businesses too.

## Useful pieces, gradual adoption

Plugins should be independently useful peers. Commerce is not a mandatory hub
for every business tool. A merchant should be able to adopt a useful piece,
keep a working existing system, and change the combination over time.
Integrations with external providers are deliberate supported capabilities,
not a promise to connect to every product.

Each responsibility has one authoritative owner, including when that owner is
an external provider. Neither an agent nor a second plugin silently creates a
competing source of truth. Partial adoption should provide real value and make
remaining human work explicit.

The first release remains a working EmDash store that a non-technical human
can run from the admin: manage products, accept a purchase and fulfill a U.S.
physical order, with understandable recovery. The broader destination does
not automatically expand that [v1 scope](ROADMAP.md#v1-store-baseline).

## Packaging and independent operation

Plugins target the EmDash Registry and its actual sandbox and size limits.
Heavy work, shared operations and provider connections may require separate
services. Native code-registered entries remain development and test setups;
capabilities missing from a Registry build must be identified as gaps.

Merchants should have a supported way to operate DinkusKit without depending
on DinkusKit-operated services. The first self-hosting target is the merchant's
own Cloudflare account, including separately deployed services where needed.
Business records, history, knowledge and rules should remain portable,
including when a merchant leaves DinkusKit.

This is a product requirement, not a claim that complete self-hosting or export
already works. Packaging, authentication and service connection rules still
need design and proof against upstream EmDash constraints.

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

These are existing component responsibility boundaries, not a claim that every
listed capability is implemented or independently deployable today. Repository
charters and verified feature documentation describe individual contracts and
their current status. New capabilities need their own focused decisions;
marketing, email and shared knowledge do not yet have a settled package split.

## Assistants under the operator's control

Support both optional DinkusKit assistants and merchants' chosen agents and
models. A primary operator assistant can be an existing harness that calls on
specialists. Operator, builder and shopper experiences have different purposes;
the current [DinkusGuide](https://github.com/dinkuskit/dinkus-guide) is a
read-only documentation guide, not an implemented business operator.

Assistant access starts read-only. Capabilities and approval modes should be
easy to configure per assistant, per business. First-party assistants receive
no hidden authority beyond the explicit permissions available through the
same supported interfaces. Detailed permission models and selector wording
remain design work.

Keep proactive assistance selective and group related matters. Start with
quiet in-app notices, let users opt into delivery outside the app, and respect
quiet hours and notification preferences. Explain the reason for urgency.
Notification preferences never grant permission to act.

## Knowledge and continuity

Shared business knowledge should be portable and permissioned, with
business-wide information, site-specific information and explicit authorized
site overrides. Approved knowledge can become shared records; private
conversations do not automatically become shared knowledge. Storage, ownership,
shared APIs and detailed privacy controls remain open design questions.

An approved request should persist until completion or a clearly reported
blocker, within the authority granted. Build useful capabilities with
configurable business rules; this does not commit DinkusKit to a fixed workflow
catalog or a general workflow designer.

## Operating principles

- Human admin and agent clients use the same durable, permissioned operations.
- A non-technical human can operate supported capabilities from the admin
  without changing code; agent routes complement that human surface.
- A managed product has one stock authority. Missing or unhealthy stock setup
  must not silently become an invented quantity or a fallback ledger.
- Public storefront facts come from their owning systems, not a second copy in
  page content. Page composition never decides the price.
- A successful operation has durable evidence. Retries, unknown outcomes and
  corrections must be understandable without editing data by hand.
- Prove complete workflows on exact source and dependency pins, including
  admin changes, public results, persistence and recovery.

## Direction, not a release claim

Research evidence, accepted designs and active work are distinct. Priority and
maturity are independent: an important question may need research, and a
finished design may wait. Experiments can be discarded while their useful
conclusions are retained. Research informs a concrete decision; feature counts
or another product's design do not create implementation commitments.

This document records durable product direction. [Scope and planning](ROADMAP.md)
preserves the v1 baseline and explains how work is selected. Neither document
declares a launch date, release readiness or permission to publish or deploy.
Product contracts belong to focused decisions in the owning repository;
[contributor guidance](CONTRIBUTING.md) explains how to raise them.
