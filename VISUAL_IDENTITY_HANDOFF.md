# Visual Identity Update: Vercel/Eve Reference Implementation

Based on the supplied mobile references, I have overhauled the Fern documentation site's homepage and shared visual system to align with an ultra-dark, high-contrast editorial aesthetic.

## 1. Theme Configuration (`docs.yml`)
- **Foundation**: Replaced the muted dark gray backgrounds (`#17191C`, `#1D2024`) with pure black (`#000000`) and ultra-dark surface grays (`#0A0A0A`) to match the Vercel reference.
- **Accents**: Updated the primary accent colors to a vibrant, high-contrast blue (`#0070F3` and `#3291FF`).
- **Borders**: Darkened the border tokens to a very subtle charcoal (`#2B2B2B`) to ensure they recede into the background, creating the requested "fine charcoal border" look.

## 2. Homepage Re-architecture (`welcome.mdx`)
- **Structure**: Abandoned the generic `page-skeleton` in favor of a bespoke `research-landing` structure that precisely mirrors the Vercel Security page's rhythm.
- **Hero Section**: Implemented a split-pane hero. The left pane contains high-contrast editorial typography (tight tracking, large font sizes) and stark black-on-white primary buttons. The right pane introduces a "Research index" instrument grid with a subtle grid-line background and gradient focus states.
- **Card Grid**: The library destinations (Research, Law, Legislation, etc.) are now presented in a disciplined card grid (`research-library-card`). These cards feature dark backgrounds, thin borders, and a subtle rotational hover effect that introduces a faint blue glow, echoing the Vercel/Eve motion system.

## 3. Responsive Styling (`styles.css`)
- **Typography**: Enforced Geist Sans with tight letter-spacing (`letter-spacing: -.078em` on main headings) and high-contrast text (`#ededed` for headings, `#a1a1aa` for body text).
- **Mobile Rhythm**: Added strict `@media (max-width: 640px)` rules to ensure the design degrades gracefully on mobile devices. The split hero collapses into a stacked layout, borders are removed at the edges to allow content to bleed, and font sizes are clamped to maintain readability without overwhelming the viewport.
- **Global Reset**: Enforced the pure black background globally via `.fern-layout-page { background: #000 !important; }` to override any lingering Fern default themes.

## Next Steps
The changes are currently staged in the local repository. You can review them by deploying the Fern preview environment or pushing to `main` if you are satisfied with the alignment to the reference images.
