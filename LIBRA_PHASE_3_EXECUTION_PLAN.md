# LIBRA — Phase 3 Execution Plan
## The Definitive Implementation Roadmap

> **Status**: Awaiting final approval before any code is written.
> **Principle**: Components first. Pages never precede their dependencies.
> **Constraint**: No backend business logic is modified. Frontend only — unless explicitly flagged.

---

## Architecture Overview

```
base.html (Design System Foundation — COMPLETE)
     │
     ├── Phase 3.3 — Shared Components & System Pages
     │        └── All components, error pages, utilities
     │
     ├── Phase 3.4 — Auth Experience
     │        └── login.html (depends on: form-input, btn)
     │
     ├── Phase 3.5 — Dashboard Experiences
     │        ├── dashboard.html (depends on: card, card-dark, data-table, empty-state)
     │        └── my_dashboard.html (depends on: card, badge, progress component)
     │
     ├── Phase 3.6 — Book Ecosystem
     │        ├── books/partials/book_grid.html (depends on: book-card component)
     │        ├── books/index.html (depends on: book-card, form-input, filter-bar)
     │        ├── books/detail.html (depends on: card, badge, data-table, breadcrumb)
     │        └── books/form.html (depends on: form-input, form-label, card)
     │
     ├── Phase 3.7 — Operational Workflows
     │        ├── transactions/issue.html (depends on: typeahead, card, btn) [+backend routes]
     │        ├── transactions/return.html (depends on: data-table, badge, btn)
     │        ├── members/index.html (depends on: data-table, filter-bar, modal) [+backend routes]
     │        ├── members/<id>.html (depends on: card, data-table, badge, timeline) [+backend routes]
     │        ├── fines/index.html (depends on: data-table, slide-panel)
     │        └── reservations/index.html (depends on: data-table, badge, modal)
     │
     ├── Phase 3.8 — Analytics & Intelligence
     │        ├── admin/dashboard.html (depends on: card-dark, chart theming)
     │        └── admin/policies.html (depends on: card, form-input)
     │
     └── Phase 3.9 — Accessibility & Mobile Polish
              └── Global pass across all pages
```

---

## Phase 3.3 — Shared Components & System Pages
**Prerequisite for everything else. Do not begin Phase 3.4 until this is complete and verified.**

### Section A: CSS Component Additions to `base.html`

The following components do not yet exist in `base.html` and must be added before any page work begins. Each has zero page dependencies — they are pure CSS/HTML primitives.

---

#### A1 — Breadcrumb Component
**Class**: `.breadcrumb`, `.breadcrumb-item`, `.breadcrumb-sep`

```
Books  /  The Great Gatsby  /  Physical Copies
```

Specification:
- Container: `display: flex; align-items: center; gap: 6px; font-size: 12px;`
- Item links: `color: var(--text-muted); text-decoration: none;`
- Item links on hover: `color: var(--text-primary);`
- Active (last) item: `color: var(--text-secondary); font-weight: 500; cursor: default;`
- Separator `/`: `color: var(--border-strong);`

No dependency. Safe to add immediately.

---

#### A2 — Loading / Skeleton Component
**Class**: `.skeleton`, `.skeleton-text`, `.skeleton-card`

Specification:
- Base: `background: var(--surface-raised); border-radius: 6px; animation: skeleton-pulse 1.4s ease-in-out infinite;`
- `@keyframes skeleton-pulse`: `opacity: 1 → 0.4 → 1`
- `.skeleton-text`: `height: 12px; border-radius: 4px;`
- `.skeleton-card`: `height: 220px; border-radius: 12px;` (matches `.card` radius)

Used by: book grid HTMX load, return table, member list.

---

#### A3 — Modal / Overlay Component
**Class**: `.modal-overlay`, `.modal`, `.modal-header`, `.modal-body`, `.modal-footer`

Specification:
- `.modal-overlay`: `position: fixed; inset: 0; background: rgba(43, 33, 24, 0.45); z-index: 200; display: flex; align-items: center; justify-content: center;` — hidden by default via `display: none` toggled with `.modal-open` class on `<body>`.
- `.modal`: `background: var(--surface); border: 1px solid var(--border); border-radius: 16px; box-shadow: var(--shadow-md); width: 100%; max-width: 480px; padding: 0;`
- `.modal-header`: `padding: 20px 24px 0; font-size: 15px; font-weight: 600; color: var(--text-primary);`
- `.modal-body`: `padding: 16px 24px;`
- `.modal-footer`: `padding: 0 24px 20px; display: flex; justify-content: flex-end; gap: 8px;`

JavaScript required: `openModal(id)`, `closeModal(id)` — minimal, no framework dependency.

Accessibility required:
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Focus trap: Tab cycles within modal
- Escape key closes

Used by: waive fine, register member, add to waitlist.

---

#### A4 — Slide Panel Component (Side Sheet)
**Class**: `.slide-panel`, `.slide-panel-header`, `.slide-panel-body`, `.slide-panel-overlay`

A right-anchored drawer panel. Narrower use than modal — for contextual secondary actions.

Specification:
- `.slide-panel`: `position: fixed; top: 0; right: 0; bottom: 0; width: 400px; background: var(--surface); border-left: 1px solid var(--border); z-index: 200; transform: translateX(100%); transition: transform 250ms ease-out;`
- `.slide-panel.open`: `transform: translateX(0);`
- `.slide-panel-overlay`: Same as modal overlay — sits behind the panel.

Used by: fine waiver (where a reason must be entered with context).

---

#### A5 — Progress Bar Component
**Class**: `.progress-track`, `.progress-fill`, `.progress-label`

Specification:
- `.progress-track`: `height: 6px; background: var(--surface-raised); border-radius: 9999px; overflow: hidden; border: 1px solid var(--border);`
- `.progress-fill`: `height: 100%; background: var(--accent); border-radius: 9999px; transition: width 600ms ease-out;`
- `.progress-label`: `font-size: 11px; color: var(--text-muted); margin-top: 4px;`

This replaces the athletic striped progress bar in `my_dashboard.html`. Calm, typographic, institutional.

---

#### A6 — Due Date Badge Component
**Class**: `.due-badge`, `.due-badge-safe`, `.due-badge-soon`, `.due-badge-overdue`

Specification:
- `.due-badge`: base pill — `font-size: 11px; font-weight: 500; padding: 2px 8px; border-radius: 9999px; border: 1px solid;`
- `.due-badge-safe`: `background: var(--success-soft); color: var(--success); border-color: var(--success-border);`
- `.due-badge-soon` (≤3 days): `background: var(--warning-soft); color: var(--warning); border-color: var(--warning-border);`
- `.due-badge-overdue`: `background: var(--danger-soft); color: var(--danger); border-color: var(--danger-border);`

A Jinja2 macro in `base.html` will emit the correct class based on `days_remaining`. This logic lives in the template layer, not the backend.

---

#### A7 — Stat Card Component (`.card-stat`)
**Class**: `.card-stat`, `.card-stat-dark`, `.card-stat-label`, `.card-stat-value`, `.card-stat-trend`

Specification:
- `.card-stat`: `background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 24px; box-shadow: var(--shadow-sm);`
- `.card-stat-dark`: Same but `background: var(--card-dark); border-color: rgba(255,255,255,0.06);`
- `.card-stat-label`: `font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted);` (on dark: `var(--text-on-dark-muted)`)
- `.card-stat-value`: `font-size: 32px; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--text-primary); line-height: 1;` (on dark: `var(--text-on-dark)`)
- `.card-stat-trend`: `font-size: 11px; color: var(--text-muted);` — used for "↑12 this week" indicators.

---

#### A8 — Timeline Component
**Class**: `.timeline`, `.timeline-item`, `.timeline-dot`, `.timeline-content`

Replaces the ad-hoc `<ol class="border-l...">` in `dashboard.html`.

Specification:
- `.timeline`: `display: flex; flex-direction: column; gap: 0; padding-left: 20px; border-left: 1px solid var(--border);`
- `.timeline-item`: `position: relative; padding: 0 0 20px 20px;`
- `.timeline-dot`: `position: absolute; left: -25px; top: 2px; width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--surface); background: var(--border-strong);`
  - Variants: `.timeline-dot-issue` (accent), `.timeline-dot-return` (success), `.timeline-dot-fine` (warning), `.timeline-dot-member` (muted)
- `.timeline-content`: `background: var(--surface-raised); border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px;`
- `.timeline-action`: `font-size: 12px; font-weight: 600; color: var(--text-primary);`
- `.timeline-meta`: `font-size: 11px; color: var(--text-muted); margin-top: 2px;`

**Humanized action strings**: A Jinja2 macro `humanize_action(action, description)` will translate:
- `BOOK_ISSUED` → "Issued"
- `BOOK_RETURNED` → "Returned"  
- `FINE_PAID` → "Fine paid"
- `FINE_WAIVED` → "Fine waived"
- `MEMBER_CREATED` → "New member"
- Everything else → `description` field value

The `description` field in `AuditLog` already contains a human-readable string. It should be the primary display text. The `action` field is for icons only.

---

#### A9 — Filter Bar Component
**Class**: `.filter-bar`, `.filter-pill`, `.filter-pill.active`

Specification:
- `.filter-bar`: `display: flex; flex-wrap: wrap; gap: 6px; align-items: center;`
- `.filter-pill`: `.btn` variant — `font-size: 11px; padding: 4px 12px; border-radius: 9999px; background: var(--surface); border: 1px solid var(--border); color: var(--text-secondary); cursor: pointer;`
- `.filter-pill:hover`: `background: var(--surface-raised); border-color: var(--border-strong);`
- `.filter-pill.active`: `background: var(--accent-soft); border-color: var(--accent-border); color: var(--accent); font-weight: 500;`

Used by: book catalog (category filter), member list (tier filter), fines (sort).

---

#### A10 — Confirmation Dialog Component (`LibraConfirm`)
**JavaScript**: A pure-JS confirmation component to replace all `confirm()` calls.

API:
```javascript
LibraConfirm.show({
  title: 'Mark Fine as Paid',
  body: 'Confirm receipt of ₹125.00 from Arjun Mehta?',
  confirmLabel: 'Confirm Payment',
  cancelLabel: 'Cancel',
  danger: false,  // true uses --danger color for confirm button
  onConfirm: () => { form.submit(); }
});
```

Implementation:
- Renders a `.modal` overlay (reuses A3 styles)
- Confirm button: `.btn-primary` (or `.btn-danger` if `danger: true`)
- Cancel button: `.btn-ghost`
- Accessible: `role="alertdialog"`, `aria-labelledby`, focus on confirm button on open, Escape to cancel

Replaces: all `onclick="return confirm(...)"` on fine payment, batch email, waive fine.

---

#### A11 — Undo Toast Extension
**Addition to existing toast system.**

New toast variant: `.toast-undoable`

API addition:
```javascript
showToastWithUndo(message, undoLabel, undoCallback, timeout = 8000)
```

Implementation:
- Shows a standard `.toast-success` with an additional "Undo" button (`.toast-close`-style, but labeled "Undo")
- `undoCallback()` is called if the user clicks Undo within `timeout` milliseconds
- If timeout expires without Undo: the primary action is considered committed

Used by: fine payment (undo → POST `/fines/<id>/undo`). Requires one new minimal backend route.

---

#### A12 — Typeahead Input Component
**Class**: `.typeahead-wrap`, `.typeahead-input`, `.typeahead-results`, `.typeahead-result-item`

HTMX-powered. The input fires `hx-get` on keyup with debounce. Results appear in `.typeahead-results`.

Specification:
- `.typeahead-wrap`: `position: relative;`
- `.typeahead-input`: Extends `.form-input` — same styling
- `.typeahead-results`: `position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; box-shadow: var(--shadow-md); z-index: 50; overflow: hidden; max-height: 280px; overflow-y: auto;`
- `.typeahead-result-item`: `padding: 10px 14px; cursor: pointer; border-bottom: 1px solid var(--border); transition: background 100ms;`
- `.typeahead-result-item:hover`: `background: var(--surface-raised);`
- `.typeahead-result-item:last-child`: `border-bottom: none;`
- `.typeahead-result-name`: `font-size: 13px; font-weight: 500; color: var(--text-primary);`
- `.typeahead-result-meta`: `font-size: 11px; color: var(--text-muted); margin-top: 1px;`

Accessibility: `role="listbox"` on results, `role="option"` on items, `aria-selected`, keyboard navigation (↑↓ to navigate, Enter to select, Escape to close).

---

### Section B: System Pages (New Files)

#### B1 — `errors/404.html`
Full-width parchment. Centered content:
- Wordmark "libra" in `var(--accent)`, 18px, linked to `/`
- Large typographic number "404" in `var(--border-strong)` at ~80px, `font-weight: 700`
- Single sentence: "This page doesn't exist."
- Single link: "Go to dashboard →"
No nav rail. No top bar. Same `auth-layout` shell.

#### B2 — `errors/403.html`
Same structure. Text: "You don't have access to this page." Link: "Go to dashboard →"

#### B3 — `errors/500.html`
Same structure. Text: "Something went wrong on our end." Link: "Go to dashboard →"
Note: Register these in the Flask app factory with `@app.errorhandler(404)` etc.

---

### Section C: Global Template Utilities

#### C1 — Jinja2 Macros (`base.html` or `_macros.html`)

```
macro due_badge(due_date)
macro humanize_action(action_string)  
macro member_pill(user)
macro book_cover(book, size='sm')
macro breadcrumb(items)
```

The `book_cover` macro emits either an `<img>` (if `book.cover_url`) or a styled typographic fallback using the first letter of the title and a deterministic warm color derived from `book.id % 6` (cycling through 6 warm Libra palette variants).

#### C2 — `{% block extra_scripts %}` enforcement

Currently, `admin/dashboard.html` loads Chart.js from a CDN with a raw `<script>` tag in the content block — it pollutes the page. Add `{% block extra_scripts %}{% endblock %}` before the closing `</body>` in `base.html`. All page-specific scripts go there, not in `{% block content %}`.

#### C3 — `{% block page_title %}` enforcement

Every template must declare `{% block page_title %}Page Name{% endblock %}`. Currently missing from most templates. This will be verified during each page's implementation phase.

---

## Phase 3.4 — Auth Experience
**Dependencies**: A3 (modal), form-input, btn
**Parallelizable with**: Nothing — sets the product's first impression.
**Backend requirements**: None.
**Risk**: Low. Entirely self-contained.

### `auth/login.html`
Two-panel layout:

**Left panel** (40% width, desktop only, hidden on mobile):
- Background: `var(--sidebar-bg)` — warm parchment
- Centered vertically:
  - Wordmark "libra" — `font-size: 28px; font-weight: 600; color: var(--accent);`
  - Tagline: "Your institutional library." — `var(--text-muted); font-size: 13px;`
  - A subtle SVG motif (open book outline, single `stroke-width: 1`, `var(--border-strong)`) — NOT an icon — a quiet illustrative accent.

**Right panel** (60% width, full-width on mobile):
- Background: `var(--canvas)`
- Centered form:
  - Page heading: "Welcome back." — `font-size: 22px; font-weight: 600; color: var(--text-primary);`
  - Subtext: "Sign in to your Libra account." — `var(--text-muted); font-size: 13px;`
  - Email input: `.form-input` with `autocomplete="email"`
  - Password input: `.form-input` with `autocomplete="current-password"` + show/hide toggle button (`.btn-ghost .btn-sm` with eye SVG icon)
  - Error display: Inline `<div class="form-error">` — uses `var(--danger)` color, shown only when flash contains error
  - Submit: `.btn .btn-primary` full-width
  - Footer note: "Need help? Contact your librarian." — `var(--text-muted); font-size: 11px; text-align: center;`

Mobile: left panel hidden, right panel fills screen with top padding.

---

## Phase 3.5 — Dashboard Experiences
**Dependencies**: A1 (breadcrumb), A5 (progress), A6 (due-badge), A7 (card-stat), A8 (timeline)
**Parallelizable**: `dashboard.html` and `my_dashboard.html` can be worked simultaneously after 3.3.
**Backend requirements**: None. All data already provided by existing routes.
**Risk**: Medium. `my_dashboard.html` requires careful judgment on the scholarly gamification.

### `dashboard.html` (Admin + Librarian)
No breadcrumb (it is the root).

**Stat row** (5 cards):
| Metric | Component | Color treatment |
|---|---|---|
| Total Books | `.card-stat` | Standard — label + value |
| Active Members | `.card-stat` | Standard |
| Overdue | `.card-stat-dark` | Walnut — value in `var(--text-on-dark)`. Entire card is a link to return table. |
| Pending Fines ₹ | `.card-stat` | Value in `var(--warning)` |
| Revenue Collected ₹ | `.card-stat` | Value in `var(--success)` |

**Greeting** (replaces emoji header):
```html
<p class="page-meta">Good morning, {{ current_user.name }}.</p>
<h1 class="page-header-title">Library Overview</h1>
```

**Quick Actions bar** (new — admin/librarian only):
A horizontal row of 3 `.btn-secondary` links below the stat row:
- Issue Book → `transactions.issue_book`
- Process Return → `transactions.return_book`
- Export CSV → `admin.export_overdue_csv` (admin only)

**Activity Timeline**:
Uses `.timeline` component. Each item uses `humanize_action(log.action)` macro. Shows `log.description` as the primary text. Timestamp in relative format: "3 minutes ago", "Yesterday at 2:15 PM".

Relative time is a pure JavaScript function added to `base.html`'s script block — it converts absolute timestamps to human-readable relative strings. No library needed.

### `my_dashboard.html` (Member — all tiers)

**Scholarly progression system** (approved override):

| Books read | Title |
|---|---|
| 0–4 | Reader |
| 5–14 | Scholar |
| 15–29 | Researcher |
| 30–49 | Archivist |
| 50+ | Curator |

Faculty and Staff: No tier/rank displayed. No reading goal prominently featured (still available but secondary). The dashboard leads with their borrowed books and fine status.

**Student layout**:
- Greeting: "Good morning, Tanmay." (no emoji)
- Reading year: `{{ goal.year }} Reading Goal`
- Progress: `.progress-track` + `.progress-label` ("{{ goal.books_read }} of {{ goal.target_books }} books · {{ progress_pct }}%")
- Rank: `.badge-neutral` containing `Scholar` (or appropriate tier). Quiet, on the right side of the goal header.
- Goal setter: A small `<form>` below the progress bar — one `<input type="number">` + `.btn-ghost.btn-sm` "Update". Not a panel — just inline below the bar.
- Borrowed books: `.data-table` inside `.table-wrap`. Shows **book title** (from `txn.copy.book.title`), **due date** (`.due-badge` macro), **days remaining** text.
- Fines: If none — `.empty-state` with green checkmark. If present — a `.card` with a warning border at top. Shows book title (from fine → transaction → copy → book), amount, days overdue.

**Faculty/Staff layout**:
Same data. No goal section prominent. Slightly more compact. No rank badge.

**Data requirement note**: `active_txns` in `main.py` currently returns Transaction objects with only `copy_id` — not the book title. To show the title, the template must traverse: `txn.copy.book.title`. This works if the `BookCopy → Book` relationship is eagerly loaded. Verify with `joinedload` in the route if N+1 queries become a concern. No service layer change — only query annotation.

---

## Phase 3.6 — Book Ecosystem
**Dependencies**: A1 (breadcrumb), A9 (filter-bar), A12 (typeahead), book-cover macro, C1 macros
**Parallelizable**: `index.html` partial and `detail.html` can be done simultaneously.
**Backend requirements**: None for catalog. New route needed for category filter HTMX endpoint.
**Risk**: Low-Medium. The book grid is the most visible page.

### `books/partials/book_grid.html`
This is the highest-impact redesign in Phase 3.

Book card specification:
```
┌─────────────────────────────┐
│  [Cover image or typographic│
│   fallback — 3:4 ratio]    │
├─────────────────────────────┤
│  Title (2-line max)         │
│  Author · Year              │
│  [Available] badge          │
└─────────────────────────────┘
```

- Card: `var(--surface)`, `border: 1px solid var(--border)`, `border-radius: 10px`, subtle `box-shadow`.
- Cover: `aspect-ratio: 2/3`, `overflow: hidden`, `border-radius: 8px 8px 0 0`
- Typographic fallback: colored background (6 warm variants cycling on `book.id % 6`), first letter of title in large white text.
- Title: `13px, font-weight: 600, var(--text-primary), line-clamp: 2`
- Author: `12px, var(--text-muted)`
- Availability: `.due-badge-safe` or `.due-badge-overdue` (reusing due-date badge palette for availability)

Grid: `grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5` — unchanged from current.

No scale transform on hover. `box-shadow` elevation change only — `var(--shadow-md)`.

### `books/index.html`
- Remove all hardcoded color classes.
- Search bar: `.form-input` class, accent-colored spinner.
- Filter bar: Category pills using `.filter-pill` component. Powered by HTMX — clicking a pill adds `?category=<slug>` to the GET request.
- Sort dropdown: `.form-select` — "Title A–Z", "Most Borrowed", "Newest First".
- Result count: `<p class="section-title">{{ books|length }} books</p>` above the grid.
- Empty state (no results): `.empty-state` with message "No books match '{{ q }}'." + link "Clear search".
- Skeleton loader: Shown during HTMX request via `hx-indicator`.

### `books/detail.html`
- Remove all `dark:*`, `from-indigo-50 to-blue-50`.
- Breadcrumb: macro → `Books / {{ book.title }}`
- Cover: Use `book_cover(book, size='lg')` macro.
- Availability badge: `.badge-success` / `.badge-danger`.
- "Physical Copies" section: renamed to "Copies" in UI. Staff-only label removed — gate is still role-checked in Jinja, just labeled more naturally.
- Recommendations section: uses `.card` + `book_cover(rec_book, size='sm')`. No gradient backgrounds.
- Waitlist CTA: `.card` with `border-left: 3px solid var(--warning)` for out-of-stock state, `var(--success)` for already-on-waitlist state.

### `books/form.html`
- ISBN fetch card: `.card` background + `.badge-accent` label "Auto-fill from ISBN".
- All inputs: `.form-input`, `.form-label`, `.form-select`.
- `alert()` → inline validation message `<p class="form-hint text-danger">Please enter an ISBN first.</p>` + toast.
- Cover placeholder: `book_cover()` macro with no book data — shows the typographic placeholder template.
- Submit: `.btn .btn-primary`.
- Cancel: `.btn .btn-ghost` → back to books list.

---

## Phase 3.7 — Operational Workflows
**Dependencies**: All of 3.3, A3 (modal), A4 (slide-panel), A10 (LibraConfirm), A12 (typeahead)
**Parallelizable**: `fines/index.html` and `reservations/index.html` can run in parallel. `members/` profile requires backend first.
**Risk**: HIGH for `issue.html` (new HTMX endpoints). LOW for return/fines/reservations.

### Backend routes required (UX-enabling only, no business logic)

#### `GET /members/search?q=<str>`
Returns HTML partial: list of `.typeahead-result-item` elements.
Each item: member name (primary), `{{ member.tier | title }} · {{ active_borrow_count }} active borrows{{ ' · ⚠ Fines pending' if has_pending_fines else '' }}` (meta).
Clicking an item fills a hidden `member_id` input and shows a member context card.

Query: `User.query.filter(User.role=='member', User.is_active==True, User.name.ilike(f'%{q}%')).limit(10).all()`

#### `GET /books/search?q=<str>` 
Returns HTML partial: list of `.typeahead-result-item` elements.
Each item: book title (primary), `{{ book.author }} · {{ book.available_copies }} available` (meta).

Query: `Book.query.filter(Book.available_copies > 0, Book.title.ilike(f'%{q}%')).limit(10).all()`

#### `GET /members/<id>` (Member Profile)
Returns full member profile template.
Data: `User` object, `Transaction.query.filter_by(member_id=id).order_by(Transaction.issued_at.desc()).all()`, `Fine.query.join(Transaction).filter(Transaction.member_id==id).all()`, `ReadingGoal.query.filter_by(member_id=id).all()`.

#### `POST /fines/<id>/undo` (Undo fine payment)
Only usable within 8 seconds of payment (enforced client-side — the undo button disappears after timeout). Backend: reverses `Fine.status` from `paid` to `pending`, clears `paid_at`.

---

### `transactions/issue.html`
**Redesigned as a two-step typeahead workflow.**

Step 1: Member search typeahead → on selection, a "Member context card" appears below the input showing: name, tier badge, active borrow count, and a warning if they have pending fines.

Step 2: Book search typeahead → on selection, a "Transaction preview" panel appears: "Issuing [Book Title] to [Member Name] · Due [date] · Fine rate: ₹X/day"

Confirm button: `.btn .btn-primary` "Confirm Issue" — submits the form. Disabled until both fields filled.

Loading state: Button shows spinner + "Issuing..." text, disabled.

### `transactions/return.html`
- Show `txn.copy.book.title` as the book identifier, `txn.member.name` as member — **requires joining the query in `transactions.py`**. Add `joinedload` or compute names in the route before passing to template.
- Overdue rows: `<tr style="background: var(--danger-soft);">` for `txn.status == 'overdue'`.
- Notes field: `.form-input` full width below the table row button — not cramped inline.
- Return button: `.btn .btn-primary .btn-sm`. After click: loading state.
- QR scan button in page header (links to `/qr` page).

### `members/index.html`
**Full-width roster, registration moved to modal.**

- Page header with "Register Member" button (`.btn .btn-primary`) → triggers `openModal('register-member')`.
- Modal: Registration form with `.form-input`, `.form-label`, `.form-select`. Same form logic, same POST endpoint.
- Full-width `.data-table`: Name + tier badge + joined date + status dot + velocity flag (if true — `.badge-danger` "High Velocity").
- Each name is a link to `/members/<id>` (member profile).
- HTMX search bar above the table (same pattern as book search).
- Tier filter pills: All / Student / Faculty / Staff.
- "Joined Date" formatted: `{{ member.joined_date.strftime('%d %b %Y') }}`.

### `members/<id>.html` — Member Profile (New Page)
Design concept: **A library card, not a database record.**

```
┌──────────────────────────────────────────────────────┐
│  [Avatar initial]  Tanmay Gupta                      │
│                    Scholar · Faculty · Active         │
│                    Member since January 2024           │
├──────────────────────────────────────────────────────┤
│  Active Borrows (3)   Fines (₹125)   Books Read (14) │
├──────────────────────────────────────────────────────┤
│  Current Borrows table                               │
├──────────────────────────────────────────────────────┤
│  Fine History table                                  │
├──────────────────────────────────────────────────────┤
│  Borrowing History table                             │
└──────────────────────────────────────────────────────┘
```

Avatar: Large circle with member's name initial, background derived from `member.id % 6` color variants (same deterministic palette as book covers).

Three-stat summary row: `.card-stat` components for active borrows, outstanding fines, total books read this year.

Tables: all use `.data-table` inside `.table-wrap`. Borrowing history is the most important — shows book title, issue date, return date, fine status.

### `fines/index.html`
- Remove waive inline form from table.
- Each row: "Waive" button → `openPanel('waive-fine-panel')`. Slide panel contains: member name, book title (from txn → copy → book), amount, reason input (`.form-input`), submit button.
- Fine amounts: `.badge-warning` removed — show as plain text in `var(--warning)` weight 600.
- Summary bar: `<div class="fine-summary">₹{{ total }} outstanding across {{ count }} fines</div>` — above the table.
- Pay button: `.btn .btn-primary .btn-sm` → calls `LibraConfirm.show()`, on confirm submits form.
- After payment: `showToastWithUndo()`.

### `reservations/index.html`
- "Add to Waitlist" form → modal. Button in page header.
- Full-width queue table.
- New first column: Queue position number (#1, #2, #3).
- "Queued Since": relative time format ("3 days ago").
- Status badge: `.badge-warning` "Waiting" / `.badge-success` "Ready to Collect".

### `admin/policies.html`
- Each policy card: `.card`.
- All inputs: `.form-input`.
- Show current effective value as read-only display above each input: `<p class="form-label">Current rate: ₹{{ policy.rate_per_day }}/day</p>`.
- Submit: `.btn .btn-primary`.
- No save confirmation needed — flash toast on redirect is sufficient.

---

## Phase 3.8 — Analytics & Intelligence
**Dependencies**: All 3.7. Chart.js already available.
**Parallelizable with**: 3.9 accessibility work.
**Backend requirements**: None — all data via existing `AnalyticsService`.
**Risk**: Medium. Chart design requires careful color mapping.

### `admin/dashboard.html`
**Structural fix first**: Move the orphaned overdue table inside the page's max-width container.

**Remove**: One of the two "Send Reminders" buttons. Keep only the table-area one. Replace `confirm()` with `LibraConfirm.show()`.

**Chart theming**: Pass a JavaScript color object `LIBRA_COLORS` from the `:root` CSS variables:
```javascript
const LIBRA_COLORS = {
  accent: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim(),
  success: getComputedStyle(document.documentElement).getPropertyValue('--success').trim(),
  warning: getComputedStyle(document.documentElement).getPropertyValue('--warning').trim(),
  danger: getComputedStyle(document.documentElement).getPropertyValue('--danger').trim(),
  muted: getComputedStyle(document.documentElement).getPropertyValue('--border-strong').trim(),
};
```

Chart.js config uses `LIBRA_COLORS` exclusively. No hardcoded hex values in chart config.

**Extended metrics** (all data already computed by `AnalyticsService.get_dashboard_chart_data()`):
- Doughnut: "Borrowing by Category" — existing, restyled.
- If `AnalyticsService` has time-series data: add a line chart "Borrowing trend (30 days)".
- Fine summary: Two `.card-stat` cards — "Pending" / "Collected this month". These duplicate the main dashboard stats intentionally — the admin analytics page is standalone.

Chart.js loaded in `{% block extra_scripts %}`.

---

## Phase 3.9 — Accessibility & Mobile Polish
**Dependencies**: All pages complete.
**Parallelizable with**: Nothing — this is a global review pass.
**Risk**: Low. No new functionality — only corrections.

### Accessibility Checklist (per-page verification)

#### Forms
- [ ] Every `<input>` and `<select>` has a matching `<label for="...">` with correct `id`
- [ ] `autocomplete` attributes on all login, name, email fields
- [ ] `aria-required="true"` on all required inputs
- [ ] `aria-describedby` pointing to error messages when errors exist
- [ ] Fieldset/legend for grouped inputs (tier selection)
- [ ] Focus rings: `outline: 2px solid var(--accent); outline-offset: 2px;` — override browser default

#### Interactive Elements
- [ ] All `.btn` elements: `type` attribute present (`type="submit"` or `type="button"`)
- [ ] Icon-only buttons: `aria-label` present
- [ ] Avatar button: `aria-haspopup`, `aria-expanded`, `aria-controls`
- [ ] Dropdown: `role="menu"`, items have `role="menuitem"`, focus managed on open/close
- [ ] Modals: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus trap, Escape closes

#### Tables
- [ ] All `<th>` elements: `scope="col"` or `scope="row"`
- [ ] Empty table states: `<td colspan="n">` with `.empty-state` content
- [ ] Sortable columns (future): `aria-sort` attribute

#### Color & Contrast
- [ ] All text on `var(--canvas)` (#EFE8DC) meets WCAG AA (4.5:1 for body text)
  - `var(--text-primary)` (#2B2118 on #EFE8DC): **Passes** (~9:1)
  - `var(--text-secondary)` (#5D5146 on #EFE8DC): **Passes** (~4.7:1)
  - `var(--text-muted)` (#7E7062 on #EFE8DC): **Borderline** — verify with tool
- [ ] All text on `var(--card-dark)` (#4A3B2F): `var(--text-on-dark)` (#F8F4EE) — **Passes** (~10:1)
- [ ] `var(--accent)` (#5D7DBA) on white: verify 3:1 minimum for non-text UI (WCAG 1.4.11)
- [ ] All status colors communicated with BOTH color AND text/icon (not color alone)

#### Navigation
- [ ] Skip-to-content link at top of every authenticated page: `<a class="skip-link" href="#main-content">Skip to main content</a>`
- [ ] `aria-current="page"` on active nav item
- [ ] `aria-label` on both `<nav>` elements ("Primary navigation", "Mobile navigation")

#### Live Regions
- [ ] Toast container: `role="region" aria-live="polite"` — **already implemented**
- [ ] HTMX swap targets: `aria-live="polite"` on `#search-results` (book grid)
- [ ] Activity timeline auto-refresh (if added): `aria-live="polite"`

#### Mobile
- [ ] All touch targets: minimum 44×44px
- [ ] Book grid on mobile < 480px: Switch from 2-column cards to list rows
- [ ] Typeahead inputs: works with virtual keyboard (no `position:fixed` elements obscuring input)
- [ ] Bottom nav active state contrast: verify against `var(--canvas)`

---

## Page Dependency Graph

```
Phase  │ Template                        │ Depends on components
───────┼─────────────────────────────────┼──────────────────────────────────────
3.3    │ errors/404, 403, 500            │ auth-layout (already in base.html)
3.3    │ base.html component additions   │ Standalone CSS
3.4    │ auth/login.html                 │ form-input, btn, form-error
3.5    │ dashboard.html                  │ card-stat, card-stat-dark, timeline, quick-actions
3.5    │ my_dashboard.html               │ card, progress-track, due-badge, badge
3.6    │ books/partials/book_grid.html   │ book-card (new), book-cover macro
3.6    │ books/index.html                │ book_grid partial, form-input, filter-bar
3.6    │ books/detail.html               │ breadcrumb, card, badge, data-table, book-cover
3.6    │ books/form.html                 │ form-input, form-label, form-select, card, btn
3.7    │ transactions/issue.html         │ typeahead, card, btn, LibraConfirm [+backend]
3.7    │ transactions/return.html        │ data-table, badge, due-badge, btn [+backend join]
3.7    │ members/index.html              │ data-table, filter-bar, modal, badge [+backend]
3.7    │ members/<id>.html               │ card, card-stat, data-table, badge, timeline [+backend]
3.7    │ fines/index.html                │ data-table, slide-panel, LibraConfirm, toast-undo [+backend]
3.7    │ reservations/index.html         │ data-table, badge, modal
3.7    │ admin/policies.html             │ card, form-input, form-label, btn
3.8    │ admin/dashboard.html            │ card-stat-dark, LibraConfirm, Chart.js theming
```

---

## Parallelization Map

The following pairs can be worked simultaneously by two contributors if needed:

| Parallel Group | Template A | Template B |
|---|---|---|
| Group 1 (3.5) | `dashboard.html` | `my_dashboard.html` |
| Group 2 (3.6) | `books/index.html` + `book_grid.html` | `books/detail.html` |
| Group 3 (3.7) | `fines/index.html` | `reservations/index.html` |
| Group 4 (3.7) | `members/index.html` | `admin/policies.html` |

**Cannot be parallelized**:
- Phase 3.3 components must be complete before any page work
- `members/<id>.html` cannot start until the backend profile route exists
- `transactions/issue.html` cannot start until the two typeahead endpoints exist

---

## Backend Support Requirements

| Route | Method | Purpose | Phase | Complexity |
|---|---|---|---|---|
| `GET /members/search?q=` | GET | Typeahead for issue form | 3.7 | Low — simple `ilike` query |
| `GET /books/search?q=` | GET | Typeahead for issue form | 3.7 | Low — simple `ilike` query |
| `GET /members/<id>` | GET | Member profile page | 3.7 | Medium — join multiple tables |
| `POST /fines/<id>/undo` | POST | Undo fine payment | 3.7 | Low — reverse status |
| `app.errorhandler(404/403/500)` | — | Register error pages | 3.3 | Low — one line each |
| `GET /books/?category=<slug>` | GET | Category filter | 3.6 | Low — add filter to existing query |

All routes: UX-enabling only. No business logic changes. No model alterations.

---

## Risk Analysis

### Risk 1: `active_txns` data in `return.html` shows raw IDs
**Severity**: High (poor UX, actively confusing)
**Fix**: Add `joinedload(Transaction.copy)` in the `transactions.py` route. The template can then access `txn.copy.book.title` and `txn.member.name` without additional queries.
**Impact**: Route file edit. Estimated effort: 5 minutes. No service layer change.

### Risk 2: `my_dashboard.html` pending_fines shows `txn.transaction_id`
**Severity**: Medium (confusing to users)
**Fix**: The template traversal `fine.transaction.copy.book.title` should work if relationships are configured. Verify SQLAlchemy relationship chain: `Fine → Transaction → BookCopy → Book`. Add `lazy='joined'` or `joinedload` if N+1 occurs.
**Impact**: Template only. Low risk.

### Risk 3: Typeahead endpoints return partial HTML vs JSON
**Decision**: Return HTML partials, not JSON. HTMX is already in the project — partial HTML is consistent with the existing `books/index.html` HTMX pattern. JSON would require client-side rendering JS.

### Risk 4: Modal focus trap breaks on some browsers
**Severity**: Low (edge case)
**Mitigation**: Use a minimal, well-tested focus trap implementation. Test on Chrome, Firefox, Safari.

### Risk 5: Chart.js color extraction from CSS variables
**Severity**: Low — the `getComputedStyle` approach works reliably in all modern browsers.
**Mitigation**: Add a fallback hex value in the JavaScript for each color in case CSS parsing fails.

### Risk 6: `book_cover` macro — deterministic color palette
**Design decision**: 6 warm background colors drawn from the Libra palette for typographic fallbacks:
- `#C4A882` (warm sand)
- `#8B7355` (walnut)
- `#A0876B` (cognac)
- `#7A6558` (umber)
- `#B89A7A` (parchment dark)
- `#967060` (terracotta)

All have sufficient contrast for a white letter on top (WCAG AA compliant).

---

## Migration Concerns

### Concern 1: `dark:*` classes
All `dark:*` Tailwind classes in child templates will silently fail — they will not break rendering, but they apply no styles since `base.html` does not set a dark theme. They are dead code. They should be removed during each page's redesign pass to keep templates clean. **No functional impact if left in.**

### Concern 2: Non-system Tailwind colors
`text-gray-*`, `bg-blue-*`, `bg-green-*` etc. — these will continue rendering because Tailwind's default palette is still in the config alongside the `libra.*` additions. They will produce visual inconsistency but no errors. The redesign pass on each page replaces them with `libra.*` utilities or direct `style="color: var(--...)"` attributes where Tailwind doesn't have the right token.

### Concern 3: `my_dashboard.html` data
`active_txns` currently returns `Transaction` objects. The template accesses `txn.copy_id` and `txn.due_date`. For the redesigned template to show book titles, it needs `txn.copy.book.title`. The `BookCopy` → `Book` relationship exists in `book.py` (`copies = db.relationship`). Traversal will work. If performance becomes a concern with many active transactions, add `db.session.query(Transaction).options(joinedload(Transaction.copy).joinedload(BookCopy.book))`.

### Concern 4: `dashboard.html` `prefill_copy` parameter
The detail page has `url_for('transactions.issue_book', prefill_copy=copy.id)` — a `prefill_copy` GET parameter. The current `transactions/issue.html` does not use this parameter. It exists in the URL but goes unused. When the issue form is redesigned with typeahead, this parameter should pre-fill the book search. This is a nice detail — add it to the typeahead init JavaScript.

---

## Architectural Note: Global Search (Cmd+K)

Per the directive: design for it, don't implement it yet.

**Reserved structure**:
- A `#command-palette` div is to be added to `base.html` (hidden, `display: none`) during Phase 3.3. It has `role="dialog"` and `aria-label="Command palette"` — semantically correct and ready for later activation.
- The shortcut listener: `document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 'k') { ... } })` — registered but the `{ ... }` block fires `openCommandPalette()` which is a no-op stub until Phase 4.
- The palette will reuse: `.typeahead-results` CSS for its result list.
- Data sources will be: `/members/search`, `/books/search`, and a hardcoded `PAGES` array in JS with all navigable routes.

This costs nothing now and means Phase 4's command palette implementation drops in cleanly.

---

## Notification System Design

Per the directive: think beyond flash messages.

**Current state**: Toast notifications (session-scoped flash) only.

**Proposed notification layers**:

### Layer 1: Toasts (already built)
Transient, action-confirming. "Book issued successfully." Gone in 4 seconds.

### Layer 2: Due-Soon Banner
A persistent top banner injected into the authenticated layout for members. Sits below the top bar, above the main content. Shows only when the authenticated user has borrows due in ≤3 days.

```html
{% if current_user.is_authenticated and current_user.role == 'member' %}
  {% if due_soon_count %}
    <div class="due-soon-banner">
      {{ due_soon_count }} book{{ 's' if due_soon_count > 1 }} due within 3 days.
      <a href="{{ url_for('main.my_dashboard') }}">View your account →</a>
    </div>
  {% endif %}
{% endif %}
```

The `due_soon_count` would be injected via a Jinja2 context processor in `__init__.py` — queried once per request for authenticated members. This is a read-only query: `Transaction.query.filter_by(member_id=current_user.id, status='active').filter(Transaction.due_date <= date.today() + timedelta(days=3)).count()`.

Styling: `background: var(--warning-soft); border-bottom: 1px solid var(--warning-border); color: var(--warning); padding: 8px 32px; font-size: 12px; text-align: center;`

### Layer 3: Notification Dot on Avatar
For librarians: a small indicator dot on the avatar button when there are unacknowledged overdue books or waitlist members to notify. Computed once on page load. This is aspirational — Phase 3.9 if time allows, Phase 4 otherwise.

### Layer 4: Email (Backend — already implemented)
`NotificationService.send_overdue_reminder()` already exists. Batch send exists. This is Phase 4 territory (automated scheduling, individual triggers). Do not expand in Phase 3.

---

## Empty State Philosophy

Every empty state must answer: **"What should you do next?"**

| Page | Empty state message | Action provided |
|---|---|---|
| Book grid (no results) | "No books match '{{ q }}'." | Clear search link |
| Book grid (no books at all) | "Your library catalog is empty." | "Add your first book →" (staff only) |
| Return table (no borrows) | "All books are in the library. Nothing to return." | Link to issue form |
| Fines (no fines) | "No outstanding fines. Members are returning books on time." | No action needed — success state |
| Waitlist (empty) | "The waitlist is clear. Members can borrow freely." | No action needed |
| Member borrows (empty) | "You don't have any books checked out." | "Browse the catalog →" |
| Member fines (none) | "You're all clear. No outstanding fines." | No action — positive reinforcement |
| Activity timeline (no logs) | "No activity recorded yet." | No action — informational |
| Member profile (no history) | "No borrowing history yet." | No action — informational |

No dead ends. No orphaned empty screens.

---

## Final Execution Order

```
Week 1
  Day 1–2:  Phase 3.3 — All shared CSS components (A1–A12) added to base.html
  Day 2–3:  Phase 3.3 — Error pages (B1–B3), registered in app factory
  Day 3:    Phase 3.3 — Jinja2 macros (C1), extra_scripts block (C2), page_title enforcement (C3)
  Day 3:    Phase 3.3 — Global Search placeholder, Due-Soon Banner context processor (Notification Layer 2)

Week 1–2
  Day 4:    Phase 3.4 — auth/login.html
  Day 5–6:  Phase 3.5 — dashboard.html + my_dashboard.html (parallel)

Week 2
  Day 7:    Phase 3.6 — books/partials/book_grid.html (highest visual impact)
  Day 8:    Phase 3.6 — books/index.html + books/detail.html (parallel)
  Day 9:    Phase 3.6 — books/form.html

Week 2–3
  Day 10:   Backend routes: /members/search, /books/search, /members/<id>, /fines/<id>/undo
  Day 11:   Phase 3.7 — transactions/issue.html (depends on typeahead endpoints)
  Day 12:   Phase 3.7 — transactions/return.html (route join fix)
  Day 13:   Phase 3.7 — members/index.html + admin/policies.html (parallel)
  Day 14:   Phase 3.7 — members/<id>.html (depends on backend route)
  Day 15:   Phase 3.7 — fines/index.html + reservations/index.html (parallel)

Week 3
  Day 16:   Phase 3.8 — admin/dashboard.html
  Day 17–18: Phase 3.9 — Full accessibility pass (checklist above)
  Day 19:   Phase 3.9 — Mobile polish pass
  Day 20:   Final review, smoke test all routes, template parse verification
```

---

> **Awaiting approval to begin Phase 3.3 implementation.**
