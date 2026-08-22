# Visual Audit Findings

## Confirmed Theme Leak

The deployed Fern page is rendered with `html.light` and `color-scheme: light`, so Fern’s native header uses a white background. The custom stylesheet currently forces only `html`, `body`, and `.fern-layout-page` to black. This produces a white Fern header above an otherwise black content canvas, which is the observed light/dark mismatch.

## Confirmed Homepage Issue

The homepage uses a two-column hero that is too compressed at the deployed content width. The left copy column becomes narrow enough to turn the hero headline and lede into excessive line breaks. The hero should instead use a full-width editorial heading followed by a separate, lower grid panel.

## Confirmed Card-System Issue

The existing homepage classes duplicated a card system (`research-library-card`) alongside the site-wide `page-grid` system. The card dimensions are not governed by reusable size tokens, so card proportions vary across components. The correction should centralize card sizing into small, medium, and large variants and use the same grid geometry across authored pages and the homepage.

## Confirmed Stray Label Source

The legacy `custom.js` news fallback included a hard-coded `California Legislative Information` title. It has been removed. The associated news carousel, homepage search, and WebGL selectors target legacy markup that is not present on the active homepage, so those effects should remain dormant or be deliberately rebuilt later rather than retained as accidental page behavior.

## Direction

The next implementation will force a consistent dark Fern color mode at the document level, simplify the homepage into a full-width editorial hero plus a strict equal-card grid, and preserve WebGL only as a future, intentional enhancement after the static layout is stable.

## Dark-Class Experiment

Changing the root class from `light` to `dark` at runtime did not change the Fern header’s computed white background. The final correction must therefore style Fern’s header and navigation shell explicitly, rather than relying on the root class alone. It should also use a small initialization script to set the preferred theme before the page settles, avoiding a visible mixed-mode flash.

## Homepage-Only Chrome Targeting

The native Fern title is a separate `.fern-page-heading` before the homepage content. The active page’s custom content sits at `.fern-layout-guide article > .fern-prose > div > .research-landing`. Therefore, the page’s frontmatter can hide page actions and feedback, while a scoped CSS selector using `:has(.research-landing)` can hide the duplicated page-heading row only on the homepage without affecting article headings elsewhere.
