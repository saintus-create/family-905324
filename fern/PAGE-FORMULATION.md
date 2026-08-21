# Page Formulation

The documentation site uses a shared grid language so pages read as one system rather than a collection of unrelated layouts.

## Grid rules

- Use a 12-column mental grid for page composition.
- Use equal-width cells for cards and callouts whenever they share a row.
- Keep shared rows equal-height; let the tallest content determine the row height rather than allowing one card to visually dominate.
- Prefer two-, three-, and four-column arrangements that collapse cleanly at responsive breakpoints.
- Keep internal card padding, borders, radii, and vertical rhythm identical within a group.
- Balance copy length across sibling cards. If one card needs substantially more explanation, move that material below the grid instead of stretching a single card.
- Callouts in the same group use the same component and height treatment.
- Use `page-grid`, `page-grid--two`, `page-grid--four`, and `page-grid--callouts` from `grid.css` for authored grid groups.

## Content density

Write to the available cell, not against it. Sibling cards should have roughly comparable heading length, paragraph density, and metadata. Do not pad a short card with meaningless prose; instead shorten or redistribute the neighboring content.

For intentionally strict rows, use `data-balance="strict"` on the card. This caps copy so the row remains visually controlled. Important detail should then live in the page section beneath the grid.

## Page rhythm

A typical page follows this sequence:

1. Eyebrow or section marker.
2. Strong page heading.
3. Short balanced lede.
4. Primary actions, when needed.
5. Grid of equal-weight destinations or concepts.
6. Full-width sections for deeper material.
7. Supporting lists, references, or source notes.

The visual hierarchy should remain quiet: thin rules, restrained borders, consistent whitespace, and small controlled accents. Motion should clarify interaction rather than decorate the page.

## Responsive behavior

Three columns become two and then one. Four columns become two and then one. No card should be stranded at a breakpoint, and no fixed height should cause text to be clipped on narrow screens.

## Markdown formulation

Markdown remains the source of truth for meaning. CSS controls the visual system. Authors should not create page-specific spacing or arbitrary card dimensions when a shared grid primitive can express the same structure.
