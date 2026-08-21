# Page Formulation

Use this as the shared visual formulation for every page in the research library.

## Structure

1. Frontmatter: `title` and a short `description` when useful.
2. Optional eyebrow for section/context.
3. One clear H1.
4. One short lede paragraph.
5. Optional compact metadata row.
6. Content organized into short sections with strong whitespace.
7. Use bordered cards, tables, code blocks, and link rows as reusable surfaces rather than bespoke page layouts.
8. Keep calls to action compact and secondary to the content.

## Visual rules

- Use the existing Fern shell; do not recreate the navigation or application chrome in MDX.
- Use the shared Geist font already loaded by `styles.css`.
- Prefer near-white / near-black surfaces, thin borders, restrained accent color, and no gradients.
- Prefer flat cards with subtle hover movement rather than shadows or decorative effects.
- Use large, tight display headings and generous vertical whitespace.
- Links should feel native to the content and reveal interaction through color/underline rather than large buttons.
- Tables and code blocks use the same border radius and border treatment as cards.
- Motion is short and purposeful: roughly 120–180ms for controls and 180ms for card movement.
- Respect `prefers-reduced-motion`.
- Do not add page-specific typography systems.

## Reusable MDX classes

- `.page-skeleton` — page wrapper
- `.page-skeleton__hero` — title/lede/action region
- `.page-skeleton__eyebrow` — compact context label
- `.page-skeleton__title` — display H1
- `.page-skeleton__lede` — introductory copy
- `.page-skeleton__actions` / `.page-skeleton__action` — compact actions
- `.page-skeleton__meta` — metadata row
- `.page-skeleton__grid` — bordered card grid
- `.page-skeleton__card` — navigation/content card
- `.page-skeleton__section` — two-column section shell
- `.page-skeleton__section-label` — section label
- `.page-skeleton__list` — compact link list

## Content rule

The skeleton controls presentation, not subject matter. Each page should retain its own research content while using the same structural vocabulary. The goal is for separate pages to feel authored as one library rather than as separate projects.
