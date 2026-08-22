# Visual Identity Update: Vercel/Eve Reference

Based on the supplied mobile references (`IMG_8719`, `IMG_8720`, `IMG_8721`), the visual identity needs to shift to a specific ultra-dark, high-contrast aesthetic. The current `styles.css` already has a "Geist Sans" foundation and some dark mode colors, but the layout in `welcome.mdx` (`page-skeleton`) doesn't match the card styling and typography seen in the reference.

## Key Visual Characteristics to Implement

1. **Ultra-Dark Foundation**: The background is nearly pure black (`#000000` or `#0A0A0A`).
2. **Typography**: High-contrast white headings (Geist Sans), with a very tight letter spacing (tracking) on large titles. Body text is a muted gray (e.g., `#A1A1AA` or `--grayscale-a10`).
3. **Card Geometry**: 
   - Cards have thin, subtle borders (e.g., `1px solid #333` or `rgba(255,255,255,0.1)`).
   - Card backgrounds are very dark, slightly elevated from the pure black background (e.g., `#111` or `#141414`).
   - Inner padding is generous.
4. **Controls & Buttons**:
   - Primary buttons are bright white with black text (`background: white; color: black;`).
   - Secondary buttons have thin borders and transparent or very dark backgrounds.
5. **Accents**: Links and subtle accents use a specific blue (e.g., `#0070F3` or similar Vercel blue).
6. **Iconography**: Compact, geometric icons (like the Vercel triangle).
7. **Mobile Rhythm**: Stacked cards with consistent gaps, edge-to-edge content blocks where appropriate, and clear hierarchical typography.

## Implementation Plan

1. **Update `docs.yml` Colors**: Adjust the `dark` color palette to match the pure black aesthetic.
2. **Update `styles.css`**: 
   - Modify the `.page-skeleton` classes to match the card styles (thin borders, dark backgrounds).
   - Update button styles (`.page-skeleton__action--primary`) to be white with black text.
   - Adjust typography (letter-spacing, line-height) to match the editorial feel.
3. **Update `welcome.mdx`**: Refine the markup if necessary to better match the stacked card look seen in the reference images, specifically the "Related Templates" style.
