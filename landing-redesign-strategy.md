# Landing Experience Redesign Strategy

## 1. Discovery Snapshot
- `HomePage`: strong primary hero with stats and benefits but lacks storytelling depth, social proof variety, and visual rhythm; sections feel homogeneous due to repeating card grids and gradient backgrounds.
- `MentorsPage`: functional filter system yet visually dense; filter drawer basic, mentor cards uniform, no contextual guidance or trust signals; empty/loading states minimal.
- `AboutPage`: text-heavy `prose` layout without visual segmentation, imagery, or calls-to-action; lacks timeline, team highlights, or platform differentiation.
- Shared layout uses `PublicHeader`/`PublicFooter`; navigation and footer stay as-is per requirements.

## 2. Visual Language Definition
- Palette: evolve current blues into dual-tone gradient (`#1C3FE3` → `#7A5CFF`) complemented by warm accent (`#FFB457`) and neutral slate (`#101828`, `#475467`, `#EAECF0`).
- Typography: adopt more expressive pairing — display (`Clash Display` or `Manrope` 700) for hero headings, `Inter`/`Manrope` 500-600 for body; introduce tighter scale (64 / 48 / 32 / 24 / 18 / 16).
- Grid: maintain `container-wide` but introduce alternating split layouts (text + illustration), 4-column subgrid for stats/testimonials, generous white space.
- Imagery: commission vector illustrations representing mentorship journey, incorporate student success photography with soft overlays.
- Iconography: shift to filled minimal icons (remix/lucide with custom background chips) using accent gradient rings.
- Motion: subtle parallax in hero, staggered fade-slide on cards, micro-interactions on buttons (glow border) and mentor hover states.

## 3. Home Page Concept
- Hero: full-width gradient sky with floating illustration; headline `Найди своего наставника для поступления мечты` over two-column layout (copy + CTA stack vs. hero art). Include quick trust badges (universities logos strip).
- Proof Bar: replace basic stat grid with horizontally scrolling pill metrics and press logos.
- Journey Highlights: alternating sections describing phases — `Диагностика`, `Подготовка`, `Поступление`, each with icon, copy, supporting imagery.
- Success Stories: carousel of student testimonials with avatar, university crest, quote, rating.
- Mentor Spotlight: auto-rotating cards of top mentors with CTA to view profile; integrate video intro option.
- Process Timeline: vertical or horizontal timeline with numbered steps plus microcopy and icons.
- Resource CTA: section promoting downloadable guide/lead magnet, capture email.
- Final CTA: gradient call-to-action with double button (`Подобрать ментора`, `Бесплатная консультация`).
- Responsive: stack hero columns, swap carousels for swipeable cards, ensure stats collapse into two-per-row.

## 4. Mentors Catalog Concept
- Header: persistent search bar with segmented controls (`Все`, `Популярные`, `Новые`) and contextual copy.
- Filters: convert drawer into sticky left sidebar on desktop; mobile bottom sheet with chips for active filters and quick clear.
- Sorting: introduce pill-based sorting toggles and badges for applied filters.
- Mentor Cards: larger photo, overlaying university crest, tag chips for subjects/languages, price comparison toggle (per 30/60 min), quick-view modal with testimonials snippet.
- Additional Content: top banner guiding new users to quiz/assistant; FAQ strip below grid answering matching questions; highlight `Запланируйте консультацию` CTA after grid.
- Loading: skeleton with animated gradient; empty state features illustration and quick filter suggestions.

## 5. About Page Narrative
- Intro: hero with mission statement and founder quote.
- Mission & Vision: two-column layout with supporting illustration.
- Impact Metrics: timeline milestones (founded date, number of students) with icons.
- Team Section: grid of key team members, linking to mentor story.
- Methodology: explain mentor vetting with infographic steps.
- Press & Partners: logos carousel.
- Call to Action: `Присоединиться как студент` / `Стать ментором` dual CTA.
- Footer Lead Capture: newsletter subscription aligned with platform updates.

## 6. Shared Component Guidelines
- Buttons: gradient primary with soft shadow, secondary outline with subtle glow on hover, retain `sm/md/lg` sizes.
- Cards: rounded `24px`, layered shadows, gradient headers; incorporate outline accent on hover.
- Badges: pill-shaped with gradient border, used for languages, specialties, stats.
- Stats Blocks: use icon glyph within glassmorphism container, number and label stacked.
- Typography tokens: define `display`, `headline`, `title`, `body`, `caption`; adjust letter-spacing for improved readability.
- Spacing system: base unit `8px`, with sections using `96-120px` vertical rhythm on desktop.

## 7. Deliverable Blueprint
- Low-fidelity wireframes (desktop/tablet/mobile) for `Home`, `Mentors`, `About`.
- UI kit updates: color palette, typography tokens, button/card/badge components in Figma.
- Interaction specs: hero animation, filter behavior, mentor card hover/quick-view flow.
- Content brief: copy outline for new sections, testimonial sourcing checklist.
- Review milestones: concept sign-off → wireframe review → visual design approval → implementation handoff.

