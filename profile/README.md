<p align="center">✱ &nbsp; ✱ &nbsp; ✱</p>

# DinkusKit

> **dinkus** — three stars used as a section break.

A kit of plugins, hosted services and templates that turn [EmDash](https://github.com/emdash-cms/emdash) sites into online stores. Plugins install from the EmDash Registry; heavy work runs in hosted DinkusKit services.

> Agents build the code, and it is built so a human can manage it from the admin if need be. An agent may manage it too.

That is the design constraint. Anything in this kit has to be operable from the EmDash admin by a non-technical human without a code change.

## Current focus

v1: a working EmDash store a non-technical human runs from the admin, from
listing products to a paid order to a printed USPS label. Current work is the
first paid test order end to end and USPS labels.

[Vision](https://github.com/dinkuskit/.github/blob/main/VISION.md) ·
[Roadmap](https://github.com/dinkuskit/.github/blob/main/ROADMAP.md)

<p align="center">* &nbsp; * &nbsp; *</p>

## 🛒 Plugins: make it sell

- 🛒 [**commerce**](https://github.com/dinkuskit/commerce) — the open-source commerce layer for EmDash sites.
- 💳 [**payments**](https://github.com/dinkuskit/payments) — one card processor per store: Stripe or Authorize.net.
- 📮 [**ship**](https://github.com/dinkuskit/ship) — USPS label purchase and printing.
- 📦 [**inventory**](https://github.com/dinkuskit/inventory) — pools, movements, reservations, and reconciliation.
- 🎁 [**bundles**](https://github.com/dinkuskit/bundles) — mix-and-match product selection, pricing, inventory, and fulfillment.
- 🏷️ [**coupons**](https://github.com/dinkuskit/coupons) — coupon codes, rules and limits.

Inventory and coupons are wanted for v1 but not required; bundles come later.

## 🚀 Templates: make it yours

- 🛍️ [**template-store**](https://github.com/dinkuskit/template-store) — a store starter built on DinkusKit Commerce; Payments and Ship join it for v1.
- 🧰 [**template-services**](https://github.com/dinkuskit/template-services) — an Astro starter for service businesses.
- 📣 [**template-marketing**](https://github.com/dinkuskit/template-marketing) — a lean Astro starter for marketing sites.

<p align="center">* &nbsp; * &nbsp; *</p>

Under construction and dogfooding in the open. Plugins will ship on the EmDash Registry, MIT-licensed.
