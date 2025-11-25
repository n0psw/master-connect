# Landing Page Wireframe & Content Blueprint

## Home Page
- Section order: Hero → Social Proof Strip → Journey Highlights → Success Stories → Mentor Spotlight → Process Timeline → Resource Lead Magnet → Final CTA.
- Hero (full viewport height): split layout with headline, subheadline, buttons (`Найти наставника`, `Бесплатная консультация`), quick stats chips; right side illustration with floating cards; add logos row of universities beneath fold; responsive stacking with centered CTAs.
- Social Proof Strip: horizontal marquee with metrics (`500+ наставников`, `95% довольных студентов`, `50+ стран`) and press badges; on mobile use swipeable carousel; background subtle glass panel.
- Journey Highlights: three alternating two-column sections each featuring stage title, icon badge, paragraph, bullet outcomes, supporting illustration (diagnostic call, roadmap session, application review); ensure vertical stacking on small screens.
- Success Stories: slider with student portraits, quote, university crest, rating, CTA `Читать историю`; include autoplay with manual controls; fallback list for mobile.
- Mentor Spotlight: grid of 2x3 cards showing mentor photo, university badge, languages, price range, quick action buttons (`Просмотреть профиль`, `Записаться`); include optional play icon for introduction video; on mobile convert to single-column swipe.
- Process Timeline: horizontal timeline with four steps, gradient connectors, icon buttons; annotate each step with headline and two bullet points; mobile becomes vertical stack.
- Resource Lead Magnet: light background block promoting downloadable гайд; include short form fields (`Имя`, `Email`), checkbox `Получать новости`, supportive imagery of ebook.
- Final CTA: dark gradient band with concise headline, subcopy, dual buttons linking to mentors catalog and registration; include reassurance text (`Безопасные платежи • Проверенные наставники`); mobile ensures buttons stacked.

## Mentors Catalog Page
- Header band: sticky top subheader with page title, descriptive copy, total mentors count; includes segmented control (`Все`, `Популярные`, `Новые`) and help link `Как выбрать наставника?`.
- Search + chips row: prominent search field with icon, typeahead suggestions, hot keyword chips; below display active filter chips with dismiss icons.
- Filters layout desktop: left sidebar sticky to viewport containing accordion groups (Языки, Направления, Университеты, Стоимость, Рейтинг, Доступность); each group features checkboxes or sliders; include quick `Сбросить` link.
- Filters mobile: bottom sheet triggered by `Фильтры` button, with summary at top and apply/clear buttons; active filters displayed as scrollable chips under search.
- Sort and view controls: right-aligned pill toggles for sort options plus switch between grid/list view; list view emphasises detailed descriptions.
- Mentor cards grid: card height approx 360px; hero image with overlay crest, favorite button; info stack with name, headline, languages (badge chips), availability tags (`Доступен на этой неделе`), rating, price dropdown showing 30/45/60 min; primary CTA `Перейти в профиль`, secondary `Быстро записаться`.
- Quick view modal: triggered by `Быстрый просмотр`; includes short bio, testimonials snippet, schedule preview, CTA buttons; ensures background blur.
- Supportive sections: informational banner under header inviting to quiz `Помочь подобрать наставника`; FAQ strip after grid with expanders answering top matching questions; finishing CTA panel linking to booking guide.
- Loading/Empty: skeleton placeholders with gradient shimmer; empty state combining illustration, message, and recommended filters; include `Связаться с поддержкой` link.
- Pagination: sticky footer bar on mobile with previous/next; desktop uses centered pagination controls showing up to 7 pages plus jump to start/end.

## About Page
- Hero introduction: split layout with headline `Платформа MasterConnect`, description, founder quote highlight with signature image, CTA buttons for students and mentors.
- Mission & Vision: dual-column blocks with icons, short copy lines, supportive illustration on opposite side; include bullet outcomes for each.
- Impact Timeline: horizontal timeline with key milestones (launch year, number of студентов, количество консультаций, глобальное присутствие); each node features icon chip and brief description; mobile pivot to vertical timeline.
- Values grid: 2x3 cards detailing `Качество`, `Доступность`, `Прозрачность`, `Поддержка`, `Инновации`, `Сообщество`; include icon, short paragraph, supporting stat.
- Mentor Vetting Process: infographic-style section with numbered steps (заявка, проверка достижений, интервью, обучение, мониторинг качества); add callout `Только 12% кандидатов становятся наставниками`.
- Team highlight: grid of leadership/основателей cards with photo, name, role, brief bio; optional modal for detailed story; on mobile use swipeable cards.
- Press & Partners: carousel of logos with captions; include CTA `Скачать медиакит`.
- Testimonials + Media: embed short video case study, include quotes from университетские партнеры; ensure accessible controls.
- Closing CTA: dual action area encouraging регистрацию и присоединение к менторской команде; add secondary link `Посмотреть вакансии`.
- Newsletter footer: subscription form with GDPR consent, promise of frequency; align with existing site footer.

## Shared Elements & Assets
- Reusable modules: stat badge (icon + number + label), testimonial card, FAQ accordion, CTA gradient block, chip-style filters, timeline step.
- Asset requirements: custom hero illustration, journey stage artwork, mentor crest overlays, success story photography, infographic icons, press logos in SVG.
- Animation cues: hero elements parallax on scroll, cards fade-slide on viewport entry, chips hover glow, timeline connectors animate on scroll progress, modal entry scale-fade.
- Implementation notes: maintain Tailwind utility approach; create reusable components under `apps/web/src/shared/components` for stats, testimonials, FAQ, timeline; ensure responsive breakpoints align with existing `md`/`lg`.

