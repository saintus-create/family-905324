# Typographic Homepage Update

Based on the feedback, the homepage has been completely redesigned to eliminate the "connected cards" and grid boxes in favor of a sparse, typography-led aesthetic.

## Changes Implemented

1. **Card Removal**: The `.research-card-grid` and all `.research-card` elements have been completely removed from the homepage (`welcome.mdx`).
2. **Centered Typographic Hero**: The hero section is now fully centered. The font size for the main `h1` has been significantly increased (`clamp(3.5rem, 9vw, 8.5rem)`), making it the dominant visual element on the page.
3. **Larger, Cleaner Actions**: The primary and secondary buttons have been enlarged (increased padding and font size) and centered directly beneath the hero lede, providing a much clearer and cleaner call to action.
4. **List-Based Navigation**: Instead of cards, the library sections (Primary Sources, Context & Analysis) are now presented as a clean, two-column list (`.research-home__links`). The links feature a subtle hover state that slides the text right and changes the color to the primary blue accent, maintaining interactivity without the visual weight of card borders.
5. **Mobile Optimization**: On mobile devices (`< 640px`), the buttons expand to full width, and the two-column link list collapses into a single column with increased vertical rhythm, ensuring the sparse aesthetic holds up on smaller screens.

The result is a much cleaner, airier landing page that relies on scale and whitespace rather than borders and boxes to establish hierarchy.
