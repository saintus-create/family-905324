# Mobile Design Failure Criteria

Based on the provided screenshots of the live Fern site, the current bespoke homepage design fails several fundamental responsive design and information architecture (IA) principles:

## 1. Hierarchy & Redundancy
- **Failure**: The site title ("California Family Law Research") appears in the native Fern header, and then is immediately duplicated as a massive custom `<h1>` ("California family law research.") taking up half the viewport.
- **Principle**: Do not duplicate the global site title in the page content. The homepage should introduce the *purpose* or provide immediate utility, not just repeat the header.

## 2. Typography & Responsive Scaling
- **Failure**: The word "Legislation" breaks awkwardly across two lines ("Legislatio" / "n") because the custom font size clamp is too large for mobile viewports, and there is no word-break handling.
- **Principle**: Text must scale gracefully on narrow viewports without breaking words or causing horizontal scrolling.

## 3. Usability & Information Density
- **Failure**: The navigation tiles are enormous, solid blocks of color (Blue for Law, Red for Legislation, Green for Public Records). They push actual content below the fold and require excessive scrolling to see the available sections. They act as decorative elements rather than functional navigation.
- **Principle**: On mobile, navigation should be compact, scannable, and dense enough to show multiple options without scrolling. We should rely on standard Fern `<CardGroup>` which handles responsive grid collapse automatically.

## 4. Visual Cohesion
- **Failure**: The custom `.section-gallery` and `.section-tile` CSS classes clash with the standard Fern UI (which is visible in the top header and search bar).
- **Principle**: Use Fern's native primitives. A documentation site should look like a unified application, not a hybrid of a marketing page and a docs site.
