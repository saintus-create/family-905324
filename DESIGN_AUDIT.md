# Design Audit & Remediation Plan

This document establishes the baseline for the current Fern implementation and defines the target design principles to resolve ongoing visual and maintainability issues.

## 1. Current Baseline & Issues

The current site is suffering from **visual fragmentation and CSS drift**. Multiple overlapping layout systems and scripts are competing with Fern's native primitives.

### Identified Anti-Patterns:
1.  **CSS Bloat & Specificity Wars**: `styles.css` is nearly 1,000 lines long. It introduces two entirely separate layout systems (`.page-skeleton` and `.research-landing`) that bypass Fern's Markdown layout. It also contains hardcoded media queries and overrides for Fern primitives.
2.  **Orphaned JavaScript**: `custom.js` is globally injecting behaviors (e.g., a WebGL ambient canvas, a dummy "research assistant", a legacy news feed) that are not actually present or functional on the pages being served.
3.  **Inconsistent Information Architecture (IA)**: The new `public-records.mdx` page uses Fern `<CardGroup>` components, while the homepage (`welcome.mdx`) uses raw HTML with custom CSS classes (`<div className="section-gallery">`). This creates a maintenance burden where new content authors must know which CSS class to use rather than relying on standard MDX.
4.  **Forced Theming**: `custom.js` forcibly removes the `light` class and injects `dark` on load. This causes a flash of unstyled content (FOUC) and fights Fern's built-in theme toggle.

## 2. Target Design Principles

To achieve a "zero-micromanagement" interface (similar to Fumadocs/Vercel) within the constraints of Fern, we must adhere to the following principles:

*   **Principle 1: Content-Driven Layout (No HTML in MDX)**: Authors should write standard Markdown and use standard Fern components (`<Card>`, `<Callout>`, `<Tabs>`). All custom HTML grids (`<div className="page-skeleton">`) must be removed from content files.
*   **Principle 2: Native Theming**: We will configure Fern's `docs.yml` to strictly enforce dark mode natively, rather than fighting it with JavaScript injections.
*   **Principle 3: Minimal CSS Surface Area**: `styles.css` will be stripped down to *only* CSS variables (colors, fonts, border radii) that map to Fern's expected CSS variables. We will not write custom class names.
*   **Principle 4: Script Hygiene**: `custom.js` will be stripped of all orphaned initializers (WebGL, dummy assistant, legacy news) to improve page load performance and reduce errors.

## 3. Prioritized Remediation Backlog

The following steps must be executed to stabilize the visual system:

1.  **Configure Native Dark Mode**: Update `docs.yml` to remove the light mode color palette and set the default theme to dark.
2.  **Cleanse JavaScript**: Edit `custom.js` to remove `initAmbient`, `initNews`, `initResearchAssistant`, and the theme-forcing hack. Retain only `initBillCatalog` (as it is actively used on `bills-and-measures.mdx`).
3.  **Refactor Homepage (`welcome.mdx`)**: Replace the custom HTML `<div className="section-gallery">` with a standard Fern `<CardGroup>`.
4.  **Purge CSS (`styles.css`)**: Delete the `.page-skeleton`, `.research-landing`, and `.section-gallery` CSS blocks. Rely entirely on Fern's default rendering engine, overriding only the root CSS variables to match the desired Vercel-like aesthetic (Geist font, minimal borders, high contrast).

*By executing this plan, we will eliminate the need for ongoing design micromanagement, ensuring that all future corpus expansions automatically inherit a clean, professional layout.*
