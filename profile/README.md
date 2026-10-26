<p align="center">✱ &nbsp; ✱ &nbsp; ✱</p>

# DinkusKit

> **dinkus** — three stars used as a section break.

DinkusKit helps one accountable operator run a business through independently useful, connected tools—with agents doing more of the routine work as reliability and trust grow.

A kit of open-source plugins, services and templates built around [EmDash](https://github.com/emdash-cms/emdash). Commerce is our first proving ground; the destination is a business operating system. One accountable operator can work with employees, contractors and agents across several sites.

The design constraint: a non-technical human can run the business from the admin, with agents using the same permissioned operations. Adopt useful pieces alongside existing tools, choose your assistant, and keep control of your data and what an agent may do. These are product principles; individual repositories document what is implemented and proven today.

## Current focus

v1: a working EmDash store a non-technical human runs from the admin, from listing products to a paid order to a printed USPS label. The broader vision does not add every future capability to that release.

[Vision](https://github.com/dinkuskit/.github/blob/main/VISION.md) · [Scope and planning](https://github.com/dinkuskit/.github/blob/main/ROADMAP.md) · [Contributing](https://github.com/dinkuskit/.github/blob/main/CONTRIBUTING.md)

<p align="center">* &nbsp; * &nbsp; *</p>

## 🛒 Plugins: make it sell

- 🛒 [**commerce**](https://github.com/dinkuskit/commerce) — the open-source commerce layer for EmDash sites.
- 💳 [**payments**](https://github.com/dinkuskit/payments) — one card processor per store: Stripe or Authorize.net.
- 📮 [**ship**](https://github.com/dinkuskit/ship) — USPS label purchase and printing.
- 📦 [**inventory**](https://github.com/dinkuskit/inventory) — pools, movements, reservations, and reconciliation.
- 🎁 [**bundles**](https://github.com/dinkuskit/bundles) — mix-and-match product selection, pricing, inventory, and fulfillment.
- 🏷️ [**coupons**](https://github.com/dinkuskit/coupons) — coupon codes, rules and limits.

These links describe component responsibilities, not a claim that every feature is released. Inventory and coupons are optional for the v1 baseline; bundles remain a later candidate. Check each repository for current status.

## 🧭 Beyond the storefront

- 🧭 [**DinkusGuide**](https://github.com/dinkuskit/dinkus-guide) — a read-only, source-backed guide to DinkusKit and EmDash.
- 📚 [**books**](https://github.com/dinkuskit/books) — bookkeeping and reconciliation direction; currently a design stub, not an installable plugin.

We aim for independently useful tools, deliberate integrations, portable business knowledge and a practical path to run the system in your own Cloudflare account. That path, broader business capabilities and agent controls still need design and proof; they are not promises of current availability.

## 🚀 Templates: make it yours

- 🛍️ [**template-store**](https://github.com/dinkuskit/template-store) — a store starter built on DinkusKit Commerce; Payments and Ship join it for v1.
- 🧰 [**template-services**](https://github.com/dinkuskit/template-services) — an Astro starter for service businesses.
- 📣 [**template-marketing**](https://github.com/dinkuskit/template-marketing) — a lean Astro starter for marketing sites.

<p align="center">* &nbsp; * &nbsp; *</p>

Under construction and dogfooding in the open. Registry-first plugins, MIT-licensed. Follow each repository's releases and verification notes for availability.
