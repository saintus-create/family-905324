# Visual System Corrections

The site's visual identity has been repaired to eliminate the light/dark theme mixup, remove stray labels, and enforce a strict grid system with standardized card sizes.

## 1. Theme Leakage & Stray Labels
- **Light/Dark Mixup**: The root cause of the white header above the black canvas was Fern rendering a `light` HTML shell. I added an initialization script to `custom.js` that forces the document to `dark` mode and overrides `color-scheme` before the page renders, ensuring a seamless, pure-black experience from top to bottom.
- **Stray "California Legislative Information" Label**: This was traced to a hardcoded fallback array in `custom.js` for a dormant news carousel. The label has been removed from the script.
- **Duplicate Homepage Title**: Fern automatically generates a page title row that was rendering above the custom homepage hero. I updated the `welcome.mdx` frontmatter to suppress page actions and used a scoped CSS rule (`.fern-layout-guide:has(.research-landing) .fern-page-heading`) to hide the duplicate title without affecting other pages.

## 2. Card Size Standardization
- **The Problem**: The previous iteration used bespoke, one-off card dimensions (`.research-library-card`) that were not reusable and did not align with the site's authored grid system (`.page-grid`).
- **The Fix**: I introduced a strict, three-size card scale in `styles.css` and `grid.css`:
  - `--research-card-small`: 12rem (used for callouts and dense grids)
  - `--research-card-medium`: 17rem (used for the homepage library destinations)
  - `--research-card-large`: 24rem (available for featured content)
- All cards now share the same `.research-card` primitive, ensuring identical padding, borders, hover states, and responsive collapse behavior across the entire site.

## 3. Homepage Layout Simplification
- The compressed, two-column hero layout was causing excessive line breaks on desktop screens. 
- I simplified the homepage into a clean, full-width editorial hero that spans the entire grid, followed by a separate, strict medium-card grid for the library destinations. This provides the requested minimal, airy aesthetic while keeping everything firmly "on a grid."

These changes have been validated locally and committed. The visual foundation is now stable enough to support the corpus expansions outlined in the roadmap.
