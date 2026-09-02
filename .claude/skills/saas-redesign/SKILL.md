---
name: saas-redesign
description: Redesign the Vue 3 frontend into a modern SaaS-style interface with a left vertical navigation sidebar (replacing the top nav bar), a fresh design-token system, consistent spacing, and a polished professional look. Use this skill when asked to modernize the UI, move navigation into a sidebar, restyle the app shell, or apply the SaaS design system.
---

# SaaS Redesign — Left Sidebar + Fresh Design System

This skill converts the Factory Inventory Management client (`client/`) from a top
navigation bar to a modern SaaS layout: a fixed vertical sidebar on the left, a slim
top bar for account controls, a new design-token system with a fresh accent palette,
and a consistent spacing scale applied across every view.

It is **tailored to this repo**. It assumes:

- Vue 3, plain Composition API (`export default { name, setup() }`), Vite, `vue-router` with `createWebHistory`.
- Global (non-scoped) CSS lives in `client/src/App.vue`; views rely on those global classes (`.page-header`, `.card`, `.stats-grid`, `.stat-card`, `.badge`, `table`, `.loading`, `.error`).
- i18n via the custom `useI18n` composable (`t('key', params)`), with locale files `client/src/locales/en.js` and `ja.js`.
- Global filters via the `useFilters` composable singleton, surfaced by `client/src/components/FilterBar.vue`.
- Design rule: **no emojis in UI**. Icons are inline SVG.

## Non-negotiable workflow rules

1. **Delegate every `.vue` create/modify to the `vue-expert` subagent.** CLAUDE.md makes this mandatory. Hand `vue-expert` the specs and templates from this skill; do not edit `.vue` files directly.
2. **No backend changes.** This is a pure frontend/presentation task. `server/` and `tests/backend/` stay untouched.
3. **Update both locales.** Any new `t()` key goes into `en.js` *and* `ja.js`.
4. **Keep the Composition API style already in the file.** `App.vue` uses `export default { setup() }`; match it. Do not convert existing components to `<script setup>` (leave `ProfileMenu.vue` as-is — it already uses it).
5. **Preserve all existing behavior:** routing, `FilterBar`, `LanguageSwitcher`, `ProfileMenu` (profile + tasks events), and the `ProfileDetailsModal` / `TasksModal` wiring in `App.vue`.
6. **Verify with the Playwright MCP** (`mcp__playwright__*`) against `http://localhost:3000` before declaring done.

## Acceptance criteria

- [ ] Primary navigation is a vertical sidebar fixed to the left edge, full viewport height, dark surface. No top nav tab bar remains.
- [ ] Sidebar shows the brand block, one nav item per route (icon + label), and a clear active state.
- [ ] Sidebar collapses to an icon-only rail (desktop) and the choice persists across reloads (`localStorage`).
- [ ] Below 1024px the sidebar becomes an off-canvas drawer opened by a hamburger in the top bar, with a click-to-dismiss backdrop.
- [ ] A slim top bar holds the mobile hamburger, `LanguageSwitcher`, and `ProfileMenu`.
- [ ] All colors, spacing, radii, and shadows come from the design tokens in this skill — no ad-hoc hex values in new code.
- [ ] Every route renders with no horizontal page scroll at 1440px, 768px, and 375px widths.
- [ ] `npm run build` succeeds; no console errors on any route.

---

## 1. Design tokens (fresh modern palette)

Define these on `:root` in the **global** `<style>` block of `App.vue`. This is the
single source of truth — new code references `var(--…)` only.

```css
:root {
  /* Accent — indigo */
  --accent: #4f46e5;
  --accent-hover: #4338ca;
  --accent-pressed: #3730a3;
  --accent-subtle: #eef2ff;
  --accent-border: #c7d2fe;

  /* App neutrals */
  --bg-app: #f6f7f9;
  --bg-surface: #ffffff;
  --bg-subtle: #f2f4f7;
  --bg-hover: #f9fafb;

  /* Sidebar (dark) */
  --sidebar-bg: #0d1117;
  --sidebar-fg: #c9d1d9;
  --sidebar-fg-muted: #8b949e;
  --sidebar-active-bg: rgba(99, 102, 241, 0.16);
  --sidebar-active-fg: #ffffff;
  --sidebar-border: #21262d;

  /* Text */
  --text-primary: #101828;
  --text-secondary: #475467;
  --text-tertiary: #667085;
  --text-inverse: #ffffff;

  /* Borders */
  --border: #e4e7ec;
  --border-strong: #d0d5dd;

  /* Semantic (fg + tint) */
  --success-fg: #067647;  --success-bg: #ecfdf3;
  --warning-fg: #b54708;  --warning-bg: #fffaeb;
  --danger-fg:  #b42318;  --danger-bg:  #fef3f2;
  --info-fg:    #175cd3;  --info-bg:    #eff8ff;

  /* Spacing scale — 4px base */
  --space-1: 0.25rem;  --space-2: 0.5rem;  --space-3: 0.75rem;
  --space-4: 1rem;      --space-5: 1.25rem; --space-6: 1.5rem;
  --space-8: 2rem;      --space-10: 2.5rem; --space-12: 3rem;

  /* Radius */
  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px;
  --radius-xl: 16px; --radius-full: 999px;

  /* Elevation */
  --shadow-xs: 0 1px 2px rgba(16,24,40,0.05);
  --shadow-sm: 0 1px 3px rgba(16,24,40,0.10), 0 1px 2px rgba(16,24,40,0.06);
  --shadow-md: 0 4px 8px -2px rgba(16,24,40,0.10), 0 2px 4px -2px rgba(16,24,40,0.06);
  --shadow-lg: 0 12px 16px -4px rgba(16,24,40,0.08), 0 4px 6px -2px rgba(16,24,40,0.03);

  /* Layout */
  --sidebar-w: 264px;
  --sidebar-w-collapsed: 76px;
  --topbar-h: 60px;
  --content-max: 1440px;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### Type scale

| Role | size / line-height | weight |
|---|---|---|
| Page title (`.page-header h2`) | 1.5rem / 2rem | 700 |
| Section / card title | 1.0625rem / 1.5rem | 600 |
| Stat value | 1.75rem / 2.25rem | 700 |
| Body / table cell | 0.875rem / 1.25rem | 400–500 |
| Label / caption | 0.8125rem / 1.125rem | 500 |
| Micro (table head, badges) | 0.75rem / 1rem | 600, `letter-spacing: 0.04em` |

Keep Inter. Set `body { background: var(--bg-app); color: var(--text-primary); font-family: var(--font-sans); }`.

### Spacing discipline

- Card padding: `var(--space-5)`. Card-to-card gap / section gap: `var(--space-6)`.
- Grid gaps (`.stats-grid`, dashboard grids): `var(--space-5)`.
- Content gutter: `var(--space-8)` desktop, `var(--space-4)` on mobile.
- Never use raw px margins in new code; step through the scale.

---

## 2. Layout architecture

Replace the stacked `header → FilterBar → main` structure with a sidebar shell:

```
.app-shell  (min-height:100vh; --sidebar-w drives everything)
├── <AppSidebar>            position:fixed; left:0; top:0; bottom:0; width:var(--sidebar-w)
│   ├── .sidebar-brand      brand mark + name/subtitle (hidden when collapsed)
│   ├── .sidebar-nav        one .nav-item per route (icon + label)
│   └── .sidebar-collapse   toggle rail  <->  full
└── .app-main               margin-left:var(--sidebar-w); display:flex; flex-direction:column
    ├── .app-topbar         sticky; top:0; height:var(--topbar-h)
    │                       [hamburger (mobile)]  · · · spacer · · ·  LanguageSwitcher  ProfileMenu
    ├── <FilterBar>          sticky; top:var(--topbar-h)
    └── <main class="app-content">   max-width:var(--content-max); margin-inline:auto;
        └── <router-view />          padding:var(--space-6) var(--space-8)
```

Width is driven by one variable so collapse/expand is a single class flip:

```css
.app-shell { --sidebar-w: 264px; }
.app-shell.sidebar-collapsed { --sidebar-w: 76px; }
.app-sidebar { width: var(--sidebar-w); transition: width .18s ease; }
.app-main    { margin-left: var(--sidebar-w); transition: margin-left .18s ease; }

@media (max-width: 1024px) {
  .app-shell { --sidebar-w: 0px; }
  .app-sidebar { transform: translateX(-100%); transition: transform .2s ease; width: 264px; }
  .app-shell.sidebar-open .app-sidebar { transform: none; box-shadow: var(--shadow-lg); }
  .app-main { margin-left: 0; }
}
```

State ownership: **`App.vue` owns two refs** — `sidebarCollapsed` (desktop rail,
persisted to `localStorage` key `sidebar-collapsed`) and `sidebarOpen` (mobile drawer,
never persisted, closed on route change). Pass both to `<AppSidebar>` as props; the
sidebar emits `toggle-collapse` and `close`.

---

## 3. Files to change

| File | Change | Who |
|---|---|---|
| `client/src/components/AppSidebar.vue` | **New.** Vertical nav. Use `templates/AppSidebar.vue` as the starting point. | vue-expert |
| `client/src/App.vue` | Restructure template to the sidebar shell; move `LanguageSwitcher` + `ProfileMenu` into `.app-topbar`; add `sidebarCollapsed` / `sidebarOpen` state; replace the global `<style>` nav rules with tokens + shell + restyled primitives. Use `templates/App.vue`. Keep all task/modal script logic verbatim. | vue-expert |
| `client/src/components/FilterBar.vue` | Change sticky offset `top: 70px` → `top: var(--topbar-h)`; swap hex values for tokens; make `.filters-container` honor `--content-max` and the new gutter; let it wrap on narrow widths. | vue-expert |
| `client/src/locales/en.js` | Add `nav.reports` (`'Reports'`). Add any sidebar strings (`nav.collapseSidebar`, `nav.expandSidebar`, `nav.openMenu`). | main agent (plain JS) |
| `client/src/locales/ja.js` | Mirror the same keys in Japanese (`nav.reports: 'レポート'`, etc.). | main agent |
| `client/src/views/*.vue` (all 8) | Spot-check only. They inherit global classes, so most need nothing. Fix any view with its own hardcoded page-width, its own top-bar assumption, or raw-hex chrome that now clashes. Dashboard/Reports/Spending have the densest grids — verify gaps use the scale. | vue-expert if a `.vue` edit is needed |
| `client/src/main.js` | No change (routes stay the same). | — |

Do **not** touch: `useI18n.js`, `useFilters.js`, `useAuth.js`, the modal components, `api.js`.

---

## 4. AppSidebar component spec

Start from `templates/AppSidebar.vue`. Requirements:

- **Props:** `collapsed: Boolean`, `open: Boolean`. **Emits:** `close`, `toggle-collapse`.
- **Brand:** a square mark (initials from `t('nav.companyName')`) always visible; name + `t('nav.subtitle')` hidden when `collapsed`.
- **Nav items** (order matters — matches current top nav):

  | route | label key | 
  |---|---|
  | `/` | `nav.overview` |
  | `/inventory` | `nav.inventory` |
  | `/orders` | `nav.orders` |
  | `/restocking` | `nav.restocking` |
  | `/spending` | `nav.finance` |
  | `/demand` | `nav.demandForecast` |
  | `/reports` | `nav.reports` |

- **Active state:** use `useRoute()`. `/` matches exactly; others match `route.path.startsWith(to)`. Active item = `--sidebar-active-bg` fill, `--sidebar-active-fg` text, a 3px `--accent` left border (or left inset bar), icon inherits color.
- **Icons:** inline SVG, `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="1.75"`, 20px box. Render from a `paths` array per item (`<path v-for>`), so no `v-html`. Template ships a simple correct set — swap for Heroicons later if desired.
- **Collapsed behavior:** icon-only, labels removed from flow (not just visually hidden), each `.nav-item` gets `:title` = label for hover tooltip. Rail width `--sidebar-w-collapsed`.
- **Collapse toggle:** pinned to sidebar bottom; chevron rotates; emits `toggle-collapse`.
- **Mobile drawer:** when `open`, render a `.sidebar-backdrop` sibling (fixed, semi-opaque, `@click="$emit('close')"`); tapping any nav link also emits `close`. Add `@keydown.esc` on the shell (handled in `App.vue`) to close.
- **A11y:** `<nav aria-label="Primary">`; active link gets `aria-current="page"`; toggle buttons have `aria-label` from i18n; drawer backdrop `aria-hidden`.

---

## 5. Global CSS migration (`App.vue` `<style>`)

Remove: `.top-nav`, `.nav-container`, `.nav-container > *` overrides, `.logo`, `.subtitle`,
`.nav-tabs`, `.nav-tabs a` (+ `:hover` / `.active` / `.active::after`), and the old
`.main-content` block.

Add: the `:root` tokens (§1), `.app-shell` / `.app-sidebar` / `.app-main` / `.app-topbar`
/ `.app-content` shell rules (§2), `.sidebar-backdrop`.

Restyle the shared primitives with tokens (keep the class names — views depend on them):

- `.card` → `background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-5); box-shadow: var(--shadow-xs);`
- `.card-header` → bottom border `var(--border)`, `padding-bottom: var(--space-4)`, `margin-bottom: var(--space-4)`.
- `.card-title` → 1.0625rem / 600 / `var(--text-primary)`.
- `.stats-grid` → `gap: var(--space-5)`; `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))`.
- `.stat-card` → surface + `var(--border)` + `--radius-lg` + `--shadow-xs`; hover raises to `--shadow-sm`. `.stat-label` = micro caps `var(--text-tertiary)`. `.stat-value` = 1.75rem / 700. Modifier colors map to `--info-fg` / `--success-fg` / `--warning-fg` / `--danger-fg`.
- `.badge` + `.badge.*` → each variant uses its `--*-bg` / `--*-fg` pair. Map the trend/priority aliases: `increasing`→success, `decreasing`→danger, `stable`→info tint; `high`→danger, `medium`→warning, `low`→info.
- `table` / `thead` / `th` / `td` / `tbody tr:hover` → `th` micro caps on `var(--bg-subtle)`; row divider `var(--border)`; hover `var(--bg-hover)`.
- `.page-header h2` → 1.5rem / 700; `.page-header p` → `var(--text-secondary)`; margin-bottom `var(--space-6)`.
- `.loading` / `.error` → tokens; `.error` uses `--danger-bg` / `--danger-fg`.

---

## 6. Build order

1. **main agent:** add i18n keys to `en.js` + `ja.js` (`nav.reports`, sidebar labels).
2. **vue-expert:** create `AppSidebar.vue` from the template.
3. **vue-expert:** rewrite `App.vue` (shell + state + global style migration).
4. **vue-expert:** update `FilterBar.vue` (sticky offset + tokens + width).
5. **main agent:** `cd client && npm run build` — must pass.
6. **QA pass** (§7). Fix regressions (route back to vue-expert for any `.vue` fix).
7. Report the diff. Do not commit unless the user asks.

---

## 7. QA checklist (Playwright MCP)

Start the app (`/start` or `cd client && npm run dev`). Then for **each** route
(`/`, `/inventory`, `/orders`, `/restocking`, `/spending`, `/demand`, `/reports`):

- [ ] `mcp__playwright__browser_navigate` to the route; `browser_console_messages` shows no errors.
- [ ] Sidebar item for the route shows the active state; others don't.
- [ ] At 1440px: no horizontal scrollbar on `document`; content respects `--content-max` and is centered.
- [ ] At 768px: sidebar is hidden; hamburger visible; clicking it opens the drawer + backdrop; clicking backdrop or a link closes it.
- [ ] At 375px: cards stack; tables scroll inside `.table-container`, not the page.
- [ ] Collapse the rail, reload — it stays collapsed. Expand, reload — stays expanded.
- [ ] `LanguageSwitcher` still toggles EN/JA; sidebar labels + `nav.reports` translate.
- [ ] `ProfileMenu` dropdown still opens; "Profile Details" and "My Tasks" modals still open.
- [ ] `FilterBar` selects still drive the views; sticky under the top bar with no gap/overlap.

Screenshot `/` and one dense view (`/spending` or `/`) at desktop + mobile for the report.

---

## 8. Templates

- `templates/App.vue` — the sidebar-shell `App.vue` (script logic preserved, style block with tokens + shell + restyled primitives). Adapt, don't blind-copy — reconcile against the current file in case it changed.
- `templates/AppSidebar.vue` — the sidebar component (nav array, icons, active state, collapse, mobile drawer, a11y).

Both are references for `vue-expert`. Pass them along with §4 and §5.
