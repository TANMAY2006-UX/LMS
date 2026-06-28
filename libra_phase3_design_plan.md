# LIBRA Phase 3 — UX/Frontend Architecture Plan

---

## Bug Fix Explanation (Before Phase 3)

**The Error:** `Could not find name 'user' — Did you mean 'User'?` at `notification_service.py:L36`

**What It Was:** An accidental bare method call sitting *inside the class body* but *outside any function*:

```python
class NotificationService:
    @staticmethod
    def send_overdue_reminder(user, book, transaction):
        ...

    NotificationService.send_reservation_ready(user, book)  # ← This was the bug
    
    @staticmethod
    def send_reservation_ready(user, book):
        ...
```

**Why It Crashed:** Python executes class-body statements *at import time*, when the module is loaded. The name `user` (lowercase) is a *local function parameter* — it only exists inside a function call. At class definition time, Python looks for a variable named `user` in the module scope, finds none, and raises a `NameError`.

The linter noticed the only `User` in scope was the imported SQLAlchemy model class (`User` with capital U), hence the suggestion.

**Status:** ✅ Already fixed — you removed that stray line. The file is now clean.

---

---

# PHASE 3 — UX/Frontend Architecture

---

## 1. Executive Summary

LIBRA's backend is production-grade. Its frontend is not.

The current UI communicates capability but not confidence. It looks like a well-structured Flowbite template — which is exactly what it is. Every component is legible. None of them are *felt*.

The gap is not features. It is craft.

This plan proposes a systematic design language — one that makes LIBRA feel like a deliberate product, not an assembled one. The benchmark is: **after seeing it once, a Frappe senior engineer should be able to demo it without a tutorial.**

Three principles govern every decision:
1. **Restraint over decoration.** Every element earns its presence.
2. **Role-aware layout.** Students and librarians have fundamentally different mental models. The interface should reflect that.
3. **Motion as communication.** Transitions tell the user what happened. They are not decoration.

---

## 2. UX Philosophy

### The Problem With the Current UI

| Current State | Root Cause | Effect |
|---|---|---|
| 250px sidebar with emoji text | Flowbite template default | Navigation dominates the content area |
| Dark mode is visually heavy | Tailwind dark classes applied globally | Feels like a dev tool, not a library |
| Generic stat cards | Copy-pasted dashboard pattern | No visual hierarchy — everything is equally important |
| Jinja `{% if %}` branches for role UI | No role-based layout strategy | Same chrome for everyone |
| Flash messages are basic alerts | Default HTML alert styling | Jarring, not elegant |
| HTMX swaps with no transitions | No CSS swap animations | Page feels like it jumps |

### The Standard We Are Building Toward

**Linear:** Narrow icon rail, content area always wins, keyboard-first, precise typography.

**Stripe Dashboard:** Data density without noise. Every number is surrounded by context. Strong visual hierarchy with subtle color.

**Notion:** Warm backgrounds, generous whitespace, typography does the heavy lifting.

**Raycast:** Role-specific flows feel handcrafted. Micro-interactions feel inevitable, not added.

---

## 3. Information Architecture

### Current Page Inventory

| Page | Route | Accessible By | Status |
|---|---|---|---|
| Login | `/login` | All | ✅ Working |
| Librarian/Admin Dashboard | `/` | Admin, Librarian | ✅ Working |
| Member Dashboard | `/my-dashboard` | Member | ✅ Working |
| Books Index | `/books/` | All (logged in) | ✅ Working |
| Book Detail | `/books/<id>` | All | ✅ Working |
| Add Book | `/books/add` | Admin, Librarian | ✅ Working |
| Issue Book | `/transactions/issue` | Admin, Librarian | ✅ Working |
| Return Book | `/transactions/return` | Admin, Librarian | ✅ Working |
| Members | `/members/` | Admin, Librarian | ✅ Working |
| Reservations / Waitlist | `/reservations/` | Admin, Librarian | ✅ Working |
| Fines Management | `/fines/` | Admin, Librarian | ✅ Working |
| Analytics Dashboard | `/admin/dashboard` | Admin only | ✅ Working |
| Fine Policies | `/admin/policies` | Admin only | ✅ Working |
| QR Code | `/qr/copy/<id>` | Admin, Librarian | ✅ Working |

### Dead Ends Identified

1. **"My Profile" link** in the nav dropdown goes to `#`. There is no profile page.
2. **Issue Copy link** on Book Detail (`url_for('transactions.issue_book', prefill_copy=copy.id)`) — the `prefill_copy` parameter is passed but the `issue_book` route doesn't consume it. The copy pre-selection silently does nothing.
3. **Sidebar links** were `#` until very recently — now connected, but the `base.html` sidebar shows ALL nav items to ALL roles (a Librarian sees "Analytics & Bulk Mail" restricted items are only hidden for non-admins by `{% if role == 'admin' %}`; the Issue/Return/Members links remain visible to Members).
4. **No 404/403 custom pages.** Flask's default error pages will break the visual language.
5. **Members cannot navigate anywhere.** The member's `my_dashboard` has no navigation to the Books catalog — just a hardcoded link. The sidebar is identical for all roles.

### Proposed Sitemap (Redesigned)

```
LIBRA
├── [Unauthenticated]
│   └── /login                        (Login page — full screen Lottie + form)
│
├── [Member]
│   ├── / → /my-dashboard             (Reading progress, active loans, fines)
│   └── /books/                       (Browse catalog, search, join waitlist)
│       └── /books/<id>               (Book detail + waitlist action)
│
├── [Librarian]
│   ├── / → Dashboard                 (Today's stats: issues, returns, overdue count)
│   ├── /books/                       (Full catalog)
│   │   ├── /books/add                (Add book)
│   │   └── /books/<id>              (Detail + physical copies table + QR)
│   ├── /transactions/issue           (Issue workflow)
│   ├── /transactions/return          (Return workflow)
│   ├── /members/                     (Member roster + velocity flags)
│   ├── /reservations/                (Waitlist queue)
│   └── /fines/                       (Fine management)
│
└── [Admin]
    ├── / → Dashboard                 (Same as librarian + admin stats)
    ├── [All Librarian pages]
    ├── /admin/dashboard              (Analytics + Chart.js + Batch email)
    └── /admin/policies               (Fine policy management)
```

---

## 4. Navigation Strategy

> "The sidebar is the frame, not the painting."

### The Problem With the Current Sidebar

The current `<aside>` is 250px wide (256px with `w-64`), always visible on desktop, and takes up 20% of the horizontal screen on a 1280px monitor. Every page has this consistent chrome eating into the content area.

Worse: it is *identical for all roles*. A student sees "📤 Issue Book" and "⏳ Waitlist". These are meaningless to them.

### Proposed Navigation Architecture

**Primary Structure: 64px Icon Rail**

Replace the 250px sidebar with a 64px icon-only rail. No labels. No emoji. Pure SVG icons.

```
┌────┬─────────────────────────────────────────┐
│    │  Top bar: logo | page title | user avatar│
│ 64 │─────────────────────────────────────────│
│ px │                                          │
│    │           Content Area                   │
│icon│           (full 1216px available)        │
│rail│                                          │
│    │                                          │
└────┴─────────────────────────────────────────┘
```

Each icon expands a **tooltip label** on hover. Clicking opens the page. Active state: icon gets a soft indigo background pill, `2px` left border accent.

On mobile: bottom tab bar (4 most important items for that role).

**Role-Aware Icon Sets:**

| Icon | Member | Librarian | Admin |
|---|---|---|---|
| Home | ✅ (my dashboard) | ✅ (ops dashboard) | ✅ (ops dashboard) |
| Books | ✅ | ✅ | ✅ |
| Issue | ❌ hidden | ✅ | ✅ |
| Return | ❌ hidden | ✅ | ✅ |
| Members | ❌ hidden | ✅ | ✅ |
| Waitlist | ❌ hidden | ✅ | ✅ |
| Fines | ❌ hidden | ✅ | ✅ |
| Analytics | ❌ hidden | ❌ hidden | ✅ |
| Policies | ❌ hidden | ❌ hidden | ✅ |

**Top Bar (Persistent):**

```
[LIBRA wordmark]    [Page title — dynamic]    [Search]    [Notifications]    [Avatar dropdown]
```

- Wordmark: "libra" in lowercase, Inter font, indigo-700. No emoji. No book icon.
- Page title: changes per route (e.g., "Book Inventory", "Issue Workflow")
- Avatar: initials circle, dropdown has name, role badge, logout

---

## 5. Color Palette

### Primary Surface

| Token | Tailwind Class | Hex | Use |
|---|---|---|---|
| Background | `bg-stone-50` | `#FAFAF9` | Page background |
| Surface | `bg-white` | `#FFFFFF` | Cards, panels |
| Surface raised | `bg-stone-100` | `#F5F5F4` | Table headers, active states |
| Border | `border-stone-200` | `#E7E5E4` | All card and table borders |
| Border strong | `border-stone-300` | `#D6D3D1` | Input borders |

**Why stone, not gray?** Stone has a warm undertone (slightly yellow-tinted). Gray is cold blue. A library is a warm, scholarly space. This single palette decision makes the UI feel less digital and more intentional.

### Typography Colors

| Use | Class | Hex |
|---|---|---|
| Primary text | `text-stone-900` | `#1C1917` |
| Secondary text | `text-stone-600` | `#57534E` |
| Muted | `text-stone-400` | `#A8A29E` |
| Links | `text-indigo-600` | `#4F46E5` |

### Accent — Oxford Indigo

**Primary action:** `bg-indigo-600` `#4F46E5`
**Hover:** `bg-indigo-700` `#4338CA`
**Focus ring:** `ring-indigo-300`
**Active nav pill:** `bg-indigo-50 border-l-2 border-indigo-600`

**Why Indigo?**
- Indigo is the color of ink. Libraries are built around ink.
- It reads as authoritative and scholarly without being corporate-blue.
- It distinguishes well from red (fines, overdue), green (available, success), and amber (warnings).
- It is not Oxford Blue (too dark, too heavy for a light-mode-primary product).

### Semantic Colors (Unchanged)

| Meaning | Color | Example Use |
|---|---|---|
| Danger / Overdue | `red-600` | Overdue badge, fine amounts |
| Success / Available | `emerald-600` | Available copies, paid fine |
| Warning / Waitlist | `amber-600` | Notified reservation, pending |
| Info | `indigo-600` | Primary actions |
| Neutral | `stone-500` | Secondary badges |

---

## 6. Typography Rules

### Font Stack

```css
font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
```

**Load via:** `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">`

**Why Inter?** Variable weight, excellent screen rendering, used by Linear, Vercel, Stripe. It reads as precise without being clinical.

### Type Scale

| Role | Element | Class | Size |
|---|---|---|---|
| Page title | `<h1>` | `text-2xl font-semibold tracking-tight text-stone-900` | 24px |
| Section heading | `<h2>`, `<h3>` | `text-base font-semibold text-stone-800` | 16px |
| Table header | `<th>` | `text-xs font-medium uppercase tracking-wider text-stone-500` | 12px |
| Body text | `<p>` | `text-sm text-stone-700` | 14px |
| Caption / muted | metadata | `text-xs text-stone-400` | 12px |
| Metric number | stat card | `text-3xl font-bold tabular-nums text-stone-900` | 30px |
| Badge | status | `text-xs font-medium` | 12px |
| Button primary | `<button>` | `text-sm font-medium` | 14px |

**Rule:** Never use `font-black` or `font-extrabold` on body text. Reserve ultra-weights for the member's gamified reading goal card only (intentional contrast).

**Empty states:** Use `text-stone-400` with a short, single sentence. No exclamation points. "No members yet." not "No members found. Register your first student using the form!" — that reads like a tutorial.

---

## 7. Motion System

### Principles

1. **Duration:** 150ms for micro (hover, badge), 200ms for state changes, 300ms for page-level transitions. Never above 350ms.
2. **Easing:** `ease-out` for things entering. `ease-in` for things leaving. `ease-in-out` for shared transitions.
3. **No bounce.** No spring physics. Scholarly, composed.
4. **HTMX swaps must animate.** Currently they are instantaneous (jarring).

### HTMX Swap Animations

Add to `<style>` in `base.html`:

```css
/* Applied when HTMX inserts new content */
.htmx-added {
    opacity: 0;
    transform: translateY(4px);
}
.htmx-settling {
    opacity: 0;
    transform: translateY(4px);
}
/* The "settle" transition: content fades up into place */
.htmx-request #search-results,
.htmx-request .htmx-swap-target {
    opacity: 0.4;
    transition: opacity 150ms ease-out;
}
```

### Lottie Loading Screen

**File:** `Loading 7 _ Book.json`

**Strategy:** Full-screen splash that plays once on first navigation, then fades out.

```
┌────────────────────────────────────┐
│                                    │
│         [warm stone-50 bg]         │
│                                    │
│           [Lottie: book]           │
│              (128px)               │
│                                    │
│          libra                     │
│    (Inter, indigo-700, 24px)       │
│                                    │
│    [subtle progress line]          │
│                                    │
└────────────────────────────────────┘
```

Play the animation for one loop (≈2.5s), then CSS `opacity: 0` transition over 400ms, then `display: none`.

**Implementation:** A `<div id="splash-screen">` in `base.html` above `<main>`, hidden via localStorage after first visit, controlled by a small `<script>` block. No external dependencies needed — just the Lottie player CDN.

### Page Transitions (HTMX-based)

For full page navigations (sidebar link clicks), use HTMX `hx-boost` on `<a>` tags combined with a CSS class swap:

```html
<body hx-boost="true" hx-swap="innerHTML transition:true" hx-target="main">
```

This makes ALL sidebar links behave like HTMX partial swaps — only the `<main>` content changes, the sidebar stays still. Paired with:

```css
main {
    view-transition-name: content;
}
@keyframes fade-slide-in {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
::view-transition-new(content) {
    animation: fade-slide-in 200ms ease-out;
}
```

> [!IMPORTANT]
> `hx-boost` changes navigation behavior globally. It must be tested against all routes, especially POST forms, before applying. Some forms may need `hx-boost="false"` explicitly.

### Hover States

All interactive elements: `transition-colors duration-150`

Table rows: `hover:bg-stone-50 transition-colors duration-100`

Buttons: scale on click — `active:scale-[0.98] transition-transform duration-100`

---

## 8. Component System

### Buttons

**Hierarchy:**

```
Primary   → solid indigo    → "Issue Book", "Save", "Process Return"
Secondary → white + border  → "Cancel", "Add Copy"
Danger    → solid red       → "Withdraw Copy"
Ghost     → text only       → sidebar actions
```

**Sizes:**
- Default: `px-4 py-2 text-sm`
- Small: `px-3 py-1.5 text-xs` (table actions)
- Large: `px-6 py-3 text-sm` (primary page CTAs)

**Rule:** Never more than ONE primary button per page section.

### Cards

```
bg-white rounded-xl border border-stone-200 shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6
```

No gradients on functional cards. Gradients only on the Member Reading Goal card (intentional exception — it's gamified, it earns the gradient).

### Tables

```
Outer: bg-white rounded-xl border border-stone-200 overflow-hidden
Header: bg-stone-50 border-b border-stone-200 text-xs uppercase tracking-wider text-stone-500
Rows: hover:bg-stone-50 transition-colors duration-100 border-b border-stone-100
```

Remove `shadow-sm` from individual rows. The card's `shadow` handles depth.

### Badges / Status Pills

```
Available:  bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200
Overdue:    bg-red-50 text-red-700 ring-1 ring-red-200
Active:     bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200
Pending:    bg-amber-50 text-amber-700 ring-1 ring-amber-200
Withdrawn:  bg-stone-100 text-stone-600 ring-1 ring-stone-200
```

No filled backgrounds (`bg-red-100`). Use `ring` (outline) versions — softer, more refined.

### Form Inputs

```
bg-white border border-stone-300 rounded-lg px-3 py-2 text-sm text-stone-900
focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none
transition-shadow duration-150
```

Labels: `text-xs font-medium text-stone-600 mb-1.5` (smaller than current)

### Empty States

**Rule:** One icon, one sentence, one optional action. No paragraph text.

```
[SVG icon — 32px, stone-300]
No active borrows.
[Browse catalog →]  (link, not button)
```

### Flash Notifications

Replace Tailwind alert blocks with a **toast system**: fixed bottom-right, auto-dismiss at 4s, slide-in from the right.

```
position: fixed; bottom: 24px; right: 24px;
transform: translateX(0); /* slide in from translateX(120%) */
transition: transform 250ms ease-out;
```

Three variants: success (emerald), error (red), info (indigo).

---

## 9. Role-Based Experiences

### Students

**Mental model:** "This is my reading life. It should feel personal."

**Dashboard layout:**
```
┌──────────────────────────────────────────────────────┐
│  [Reading Quest card — full width, the hero element] │
│  Year target, progress bar, rank badge               │
├─────────────────────────┬────────────────────────────┤
│  Active Borrows         │  Fines (if any)            │
│  (loan cards w/ due     │  (red if present,          │
│   date, status)         │   green "clean" if not)    │
└─────────────────────────┴────────────────────────────┘
```

The Reading Goal card should have a distinct aesthetic: warm gradient (`from-stone-900 to-indigo-950`), white text. Everything else on the page is light. This contrast makes the goal the anchor of the experience.

Navigation: just 2 items — Home, Browse Books.

### Faculty

**Mental model:** "I need to know what I have out and when it is due. Nothing else."

Same layout as student dashboard but stripped of the gamification. No rank badge. No animated progress. Just a clean table of borrowed books with due dates. Calm.

### Librarians

**Mental model:** "I process 30 transactions a day. Every click costs me."

**Dashboard layout:**
```
┌────────────┬────────────┬────────────┬────────────┐
│ Issues     │ Returns    │ Overdue    │ Pending    │
│ Today      │ Today      │ Total      │ Fines      │
│ (stat)     │ (stat)     │ (stat/red) │ (₹ amount) │
└────────────┴────────────┴────────────┴────────────┘
┌─────────────────────────────────────────┐
│  Quick Actions (3 buttons, always visible):      │
│  [📤 Issue Book]  [📥 Return Book]  [🔍 Find Member] │
└──────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  Recent Activity Timeline (last 10)     │
└─────────────────────────────────────────┘
```

**Quick Actions bar** is the most critical addition for librarians. Currently, they must navigate via the sidebar for every action. A persistent action bar above the timeline puts the two most frequent operations one click from anywhere on the dashboard.

**Issue/Return pages** should have a search-first design: type member name to filter the dropdown inline (HTMX), not scroll a full list. Same for book selection.

### Admins

**Mental model:** "I need to understand the health of the library at a glance."

**Dashboard layout:**
```
┌────────────┬────────────┬────────────┬────────────┬────────────┐
│ Total Books│ Members    │ Overdue    │ Receivables│ Revenue    │
└────────────┴────────────┴────────────┴────────────┴────────────┘
┌───────────────────────────┬────────────────────────────────────┐
│  Borrowing by Category    │  Activity Timeline                 │
│  (doughnut chart)         │  (last 15 events)                  │
└───────────────────────────┴────────────────────────────────────┘
```

Stat cards use **tabular numerics** (`font-variant-numeric: tabular-nums`) — numbers should not shift width as they update.

---

## 10. Identified Problems (Current UI)

| Problem | File | Severity |
|---|---|---|
| Sidebar visible to Members showing librarian-only links | `base.html` | High |
| `prefill_copy` param on issue_book route silently ignored | `books/detail.html` + `transactions.py` | Medium |
| "My Profile" link goes to `#` — broken UX expectation | `base.html` | Medium |
| All stat cards have equal visual weight | `dashboard.html` | Medium |
| Flash messages are inline alerts, not dismissible toasts | `base.html` | Medium |
| HTMX swaps have no transition — content jumps | `books/index.html` | Medium |
| `books/index.html` uses `{% include "books/partials/book_grid.html" %}` but the file is actually at `books/partials/book_grid.html` not `partials/book_grid.html` | `books/index.html:L40` | High — will 500 |
| No 403 or 404 error pages | N/A | Medium |
| Member can see "⏳ Waitlist (Queue)" sidebar link | `base.html` | Low |
| `books.py:L1` imports `from app import db` (should be `from app.extensions import db`) | `books.py` | High — may circular import |

> [!CAUTION]
> The import `from app import db` in `app/routes/books.py` line 1 is a likely circular import. `app/__init__.py` imports `books_bp` from `app/routes/books.py`, and `books.py` importing `from app` creates a circular dependency. It should be `from app.extensions import db`. Verify this does not crash on startup.

---

## 11. Clarifying Questions

Before choosing the first page to implement, I need your answers:

**Q1 — Lottie file location:**
Where is `Loading 7 _ Book.json` stored? Is it in `app/static/` already, or do I need to place it? Does it play on every page load or only on the initial app load?

**Q2 — Navigation:**
The 64px icon rail I proposed replaces the 250px sidebar. This is a significant structural change to `base.html`. Are you comfortable with this, or do you prefer a **slim 200px sidebar with labels but no emoji**, which is less radical?

**Q3 — Light mode only:**
You said light mode is primary. Should dark mode be removed entirely from the codebase, or preserved as an opt-in (via a toggle in the user dropdown)?

**Q4 — Member navigation:**
Currently, members land on `/my-dashboard`. They have no sidebar navigation to reach `/books/`. Should the member experience get a **completely different base template** (top navigation, no sidebar), or should the icon rail simply show 2 items for members?

**Q5 — Which page first?**
Based on my analysis, I recommend we start with `base.html`. It controls:
- Chrome (sidebar → icon rail)
- Colors (gray → stone)
- Font (system → Inter)
- Flash notifications (inline → toasts)
- HTMX transitions

Once `base.html` is right, every page inherits the improvement automatically. Do you agree, or do you want to start with `dashboard.html` instead?

**Q6 — `hx-boost` approval:**
Using `hx-boost="true"` on `<body>` enables SPA-like navigation for all internal links. It will make navigating LIBRA feel significantly faster. However, it requires careful testing — particularly on POST forms. Are you comfortable with this being part of `base.html`?

---

## Proposed Implementation Order (Pending Approval)

1. `base.html` — icon rail, stone palette, Inter font, toast system, HTMX transitions
2. `dashboard.html` (librarian/admin) — stat cards, quick actions bar, timeline
3. `my_dashboard.html` (member) — reading goal hero card, clean loan list
4. `books/index.html` + `books/partials/book_grid.html` — search + grid
5. Remaining operational pages (issue, return, members, fines, reservations)

---

*Awaiting your answers to the 6 questions above before any code is written.*
