# INDEX NEWS — HTML Structure Reference

## File Location
`D:\\projetos\\TOP OF THE HOUR — IA\\index.html` — single self-contained file (CSS + JS inline)

## Architecture
```
masthead (sticky, position:sticky, top:0, z-index:100)
├── masthead-top (edition #, title, date)
├── masthead-brand (TOP OF THE HOUR — IA logo + subtitle + rule)
├── tab-bar (tab buttons for each edition)
└── cascade-nav (Hardware / Arquitetura / Apps / Estratégia links)

tabContainer
└── tab-content#ed-NNN (one per day)
    ├── radar-bar (sources status grid)
    ├── hero-card (gancho técnico + meta stats)
    ├── cascade-section.sec-hardware
    │   ├── section-header (icon + title + count)
    │   └── news-grid
    │       └── article.news-card × N
    ├── cascade-section.sec-arch (...)
    ├── cascade-section.sec-apps (...)
    ├── cascade-section.sec-strategy (...)
    ├── stats-bar (counters per section)
    └── footer

.back-to-top (fixed, bottom-right, appears on scroll)

.ticker-wrap (fixed, bottom:0, z-index:9999)
├── .ticker-label (gold background, "AO VIVO" + live dot)
├── .ticker-track-wrap (overflow:hidden, flex:1)
│   └── .ticker-track (absolute, white-space:nowrap, animation: scrollTicker)
│       ├── ◆ 🔴 HARDWARE ◆ (section divider)
│       ├── .ticker-item × N (clickable, scrolls to card)
│       ├── ◆ 🟠 ARQUITETURA ◆
│       ├── .ticker-item × N
│       └── ... (content duplicated 2× for seamless loop)
└── .ticker-nav
    ├── ⏸ pause button
    └── ↓ scroll-to-next-section button
```

## CSS Variables (Cores da Cascata)
```css
--cascade-hardware: #ff4d4d;     /* red */
--cascade-arch:    #ff9f43;     /* orange */
--cascade-apps:    #00d2d3;     /* teal */
--cascade-strategy:#5b86e5;     /* blue */
--accent-gold:     #ffd700;     /* gold highlights */
```

## Key CSS Classes

### Card Structure
- `.news-card` — container, has `position:relative`, 3px left border via `::before`
- `.news-card-top` — flex row for badges + date
- `.news-card-badges` — flex wrap container for `.imp-badge` + `.news-card-source-tag`
- `.news-card-fact` — left-bordered fact text
- `.news-card-impact` — accent-backgrounded impact box
- `.card-terms` — flex wrap container for 🔑 glossary tags
- `.detail-toggle` + `.detail-content` — expandable section (JS toggled)

### Importance Badges
- `.imp-badge.imp-critico` — 🔥 Crítico (red)
- `.imp-badge.imp-alto` — ⚡ Alto (orange)
- `.imp-badge.imp-medio` — 📌 Médio (gold)
- `.imp-badge.imp-baixo` — ℹ️ Baixo (gray)

### Images
- `.person-row` — flex row for brand logo + CEO photo side by side
- `.brand-logo` — height:24px, object-fit:contain, filter:brightness(0)invert(0.8)
- `.person-photo` — 36×36 rounded circle with border
- `.news-card-img` — full-width 160px height banner, border-radius:8px
- ALL images MUST have `onerror="this.style.display='none'"` and CSS gradient fallback on parent

## JavaScript Functions
```javascript
// Checklist — saves to localStorage with key 'indexnews-{data-key}'
function initChecklist() — reads all .read-check, restores state, binds change handler
function updateReadCount() — updates stats counters + hero meta

// Expandable detail
function toggleDetail(btn) — toggles .open on button and sibling .detail-content

// Ticker bar
function initTicker() — collects all h3 titles organized by 4 sections,
  builds duplicated (2×) track HTML with clickable items + section dividers,
  binds pause/resume (animationPlayState) and scroll-to-section buttons
window.scrollToCard(cardId) — scrollIntoView smooth + gold glow for 2s

// Back to top
window.addEventListener('scroll') — toggles .visible on #backToTop
```

## data-id Naming Convention
Cada card recebe um `data-id` único no formato `secao-edicao-sequencial`:
- Hardware: `hw-001-1`, `hw-001-2`, `hw-001-3`, ...
- Arquitetura: `arc-001-1`, `arc-001-2`, ...
- Apps: `app-001-1`, `app-001-2`, ...
- Estratégia: `str-001-1`, `str-001-2`, ...

O mesmo valor vai no `data-key` do checkbox para localStorage, e é referenciado pelo ticker para scroll.

## localStorage Schema
- Key: `indexnews-{data-key}` (e.g., `indexnews-hw-001-1`)
- Value: `"true"` or `"false"` (string, set by checkbox change)
- Scope: per-origin (same file:// path)

## Adding a New Edition
1. Copy one existing `<div class="tab-content" id="ed-NNN">` block
2. Increment the edition number in all IDs (`ed-002`, `hw-002`, etc.)
3. Update: radar, hero title/hook/meta, all card contents, stats numbers
4. Add a new `<button class="tab-btn" data-ed="002">` to the tab-bar
5. Re-scan all sources from scratch (do NOT reuse old data)
