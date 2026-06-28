# LIBRA — Phase 3 Master Product Design & UX Plan

> **Status**: Awaiting approval. No code will be written until this plan is reviewed and locked.
> **Auditor role**: Lead Product Designer · Frontend Architect · UX Strategist · Information Architect

---

## Design North Star

Every decision must answer: *"Would this feel natural inside a beautiful century-old university library?"*

The answer is never "make it prettier." It is always about **calm**, **legibility**, **institutional trust**, and **purposeful restraint**.

---

# DELIVERABLE 1 — Complete HTML Audit

## AUTH

### `auth/login.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Entry point — email + password authentication |
| **Intended user** | All roles — first screen every user ever sees |
| **Current strengths** | Simple, no clutter, clean layout |
| **Critical weaknesses** | Generic Flowbite/Bootstrap card. White card on white/gray background — zero identity. The product could be any SaaS tool. |
| **UX problems** | No wordmark/brand moment. No "sign in as" context. No error display region (relies on flash only). Password field has no show/hide toggle. No keyboard trap management (a11y failure). |
| **Information hierarchy** | Flat. No hierarchy at all — just two inputs and a button. |
| **Visual inconsistencies** | Hard blue button (`bg-blue-600`) will clash with the new accent (`#5D7DBA`). Dark mode classes (`dark:*`) are orphaned — base.html no longer supports dark mode. |
| **Accessibility** | Missing `autocomplete` attributes. No `aria-describedby` for error messages. Focus ring uses browser default. |
| **Mobile** | Works but feels like a website, not a product. No visual delight. |
| **Opportunities for delight** | This is the institution's front door. It should feel like entering a prestigious library — warm, quiet, welcoming. A full-bleed parchment layout with the wordmark as a typographic hero would be memorable. |
| **Layout verdict** | Replace with a full-bleed two-panel layout: left panel = brand identity, right panel = form. On mobile: stacked, brand above. |

---

## CORE — Dashboards

### `dashboard.html` (Admin/Librarian)
| Attribute | Assessment |
|---|---|
| **Purpose** | Operational overview — stats, activity log |
| **Intended user** | Admin and Librarian |
| **Current strengths** | Stat cards are logically organized. Timeline is a genuine UX insight. Activity filtering by role is correctly implemented. |
| **Critical weaknesses** | **Every color hardcoded.** `text-gray-900`, `bg-blue-100`, `bg-purple-100`, `dark:*` — none of these exist in the new design system. The page will render visually broken against the parchment canvas. |
| **UX problems** | The "👋" emoji in `Welcome back` is at odds with institutional gravitas. The "Quick Issue Book" button only appears for certain endpoints — the `request.endpoint` condition is wrong (it will show `#` in most cases). 5 stat cards with no visual differentiation — all white, identical shape. The "overdue" stat has no click-through to the actual overdue list. Metrics are static — no trend indicators (up/down from yesterday). |
| **Information hierarchy** | Stats and activity have equal visual weight. The critical metric (Overdue) should dominate, not share space equally with Revenue. |
| **Visual inconsistencies** | Badge colors: `bg-blue-100`, `bg-green-100`, `bg-red-100`, `bg-yellow-100`, `bg-emerald-100` — 5 different non-system colors for 5 cards. |
| **Accessibility** | Stats have no `aria-label` or semantic description. Numbers are raw text with no units conveyed accessibly. |
| **Mobile** | Grid collapses correctly but 5 cards in a single column is 5 separate scroll events just to see KPIs. |
| **Opportunities** | The stat cards for Overdue and Revenue should be dark walnut `.card-dark` — visually commanding. Overdue number should link to filtered transactions. Activity log should show book titles, not just action strings. |
| **Layout verdict** | Keep dashboard layout. Redesign individual components — not structure. |

### `my_dashboard.html` (Member)
| Attribute | Assessment |
|---|---|
| **Purpose** | Member's personal reading hub — current borrows, fines, reading goal |
| **Intended user** | Student, Faculty, Staff |
| **Current strengths** | The reading goal concept is genuinely delightful. Co-borrowing is smart. Borrowed list with due dates is exactly the right data for a member. |
| **Critical weaknesses** | **Catastrophic visual mismatch with design system.** Dark gradient card (`from-gray-900 to-blue-900`), neon glow effects (`shadow-[0_0_10px_rgba(96,165,250,0.5)]`), rocket emoji 🚀, stripe progress bar, "Active Quests", "Grandmaster 👑" — this entire page was designed for a gaming app. It contradicts the institutional library philosophy at every point. |
| **UX problems** | "Active Quests (Borrowed)" is confusing to a faculty member. Copy IDs are shown without book titles — "Copy #14" is meaningless. Fines section says "Txn #{{ fine.transaction_id }}" — completely opaque to users. The goal form is a tiny `<input>` inside a dark glass panel — the affordance is nearly invisible. |
| **Design verdict** | The **data architecture is correct**. The **visual direction must be completely rebuilt.** Borrowed books should show actual titles. Fines should show book titles and dates. The reading goal should be a quiet, elegant annual tracker — not a leaderboard. |
| **Layout verdict** | Hybrid. Top: welcome + goal progress (calm, typographic). Below: two-column — borrowed books (left) + fines summary (right). |

---

## BOOKS

### `books/index.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Book catalog — browse and search all books |
| **Intended user** | All roles |
| **Current strengths** | HTMX live search is genuinely excellent UX. The 300ms debounce is correct. The spinner indicator works. |
| **Critical weaknesses** | The search input uses `bg-gray-50`, `border-gray-300` — not the design system. The spinner is Tailwind `animate-spin` with `text-blue-600`. The page title uses `dark:text-white`. None of these map to the new palette. |
| **UX problems** | No filter controls (by category, availability, year). No sort controls. No result count. The search scope ("Title, Author, ISBN") is only in the placeholder — no visual label. |
| **Layout verdict** | Grid (card-based) layout is correct for books. The partial (`book_grid.html`) will need redesign. Filter bar should be added above results. |

### `books/detail.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Full book page — metadata, inventory, waitlist, recommendations |
| **Intended user** | All roles (content differs by role) |
| **Current strengths** | Three-section structure is logical. Role-gating staff-only inventory data is correct. Waitlist CTA is contextually placed. Recommendations section ("Readers Also Borrowed") is excellent for member experience. |
| **Critical weaknesses** | The cover placeholder is a gray box — could be a beautifully styled typographic book spine instead. Recommendation cards use `from-indigo-50 to-blue-50` gradient background — not in design system. All badge colors hardcoded. |
| **UX problems** | "No Cover Available" is shown as a centered gray placeholder — misses an opportunity for an elegant typographic cover (author initial + title). The "Physical Copies Inventory" heading says "(Staff View)" — that label is implementation detail leaking into UI. Breadcrumb is correct but unstyled. |
| **Accessibility** | `<img>` has alt text. Table has `scope="col"`. Acceptable baseline. |
| **Layout verdict** | Keep two-column layout (meta left, content right). Redesign surface styling. |

### `books/form.html` (Add Book)
| Attribute | Assessment |
|---|---|
| **Purpose** | Add a new book to inventory via ISBN or manual entry |
| **Intended user** | Admin, Librarian |
| **Current strengths** | The ISBN auto-fetch from OpenLibrary is a genuinely powerful feature. Cover preview before save is excellent. |
| **Critical weaknesses** | The auto-fetch card uses `from-blue-50 to-indigo-50` — not in design system. Success/error feedback uses `text-green-600` / `text-red-600` inline — should use the toast system. The JS uses `alert()` for empty ISBN — browser native alert is jarring and inaccessible. |
| **UX problems** | No "Edit Book" variant — the form title is always "Add New Book." There is no cancel/back navigation. The cover placeholder is a mountain icon — nonsensical for a book. The cover preview is `w-48 h-72` positioned left but receives no visual context of what it is. The submit button is green (`bg-green-600`) — inconsistent with the blue accent system. |
| **Layout verdict** | Keep two-column form layout. Redesign surface styling and feedback mechanisms. |

### `books/partials/book_grid.html`
*Not opened for full audit but inferred:* 4–5 column card grid. Cards likely contain cover image, title, author, availability badge. This is the visual center of the catalog and the highest-impact redesign target. Each card must feel like it belongs on a library shelf.

---

## MEMBERS

### `members/index.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Member roster + member creation form |
| **Intended user** | Admin, Librarian |
| **Current strengths** | The "High Velocity Risk" flag is a brilliant operational feature — it should be surfaced more prominently, not hidden as a tiny red pill. |
| **Critical weaknesses** | The registration form and the member table are on the **same page** as a two-column layout. This is an anti-pattern: CRUD operations should not share a screen with data display unless the dataset is inherently tiny. As the member list grows (50, 200, 500 members), this layout collapses. |
| **UX problems** | No search on the member table. No pagination indication. No click-through to a member profile. No filter by tier (Student/Faculty/Staff). "Joined Date" formatted as `YYYY-MM-DD` — should be `15 Jan 2025`. Status is a dot + text — the dot has no accessible label. |
| **Design recommendation — REJECT the form+table layout.** Registration should be a modal or a separate `/members/new` route. The main page should be a full-width, searchable, filterable member roster. |
| **Layout verdict** | Split into: (1) `members/index.html` — full-width roster with search/filter, (2) `members/new.html` or modal overlay for registration. |

---

## TRANSACTIONS

### `transactions/issue.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Issue a book to a member — core daily operation |
| **Intended user** | Librarian, Admin |
| **Current strengths** | Simple and unambiguous. Helper text explains dropdowns clearly. |
| **Critical weaknesses** | Two `<select>` dropdowns for 200+ members and 500+ books is operationally unusable. No search, no autocomplete. A librarian must scroll through every member to find the right one. This will be the most-used screen in the application — it must be the fastest. |
| **UX problems** | No confirmation step before issue. No display of the member's current borrow count or outstanding fines before issuing. No indication of the due date that will be set. Member dropdown shows `name (email) — tier` — correct data, bad formatting for scanning quickly. |
| **Design recommendation**: Replace dropdowns with typeahead search inputs (HTMX-powered). Show a member card (name, tier, current borrows, fines status) upon selection. Show the computed due date before submit. Add a single confirmation step. |
| **Layout verdict** | Redesign as a focused two-step workflow: (1) Select member (typeahead), (2) Select book (typeahead). Show a "transaction preview" panel before the final issue button. |

### `transactions/return.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Process book returns — second most critical operation |
| **Intended user** | Librarian, Admin |
| **Current strengths** | Table is scannable. Overdue rows can be highlighted with red text. |
| **Critical weaknesses** | **"Member ID: {{ txn.member_id }}"** — the raw database integer is shown to users. This is a data leak of implementation detail. Member names must be shown. **"Copy #{{ txn.copy_id }}"** — the copy ID means nothing without the book title. |
| **UX problems** | The "Optional notes" field is a tiny `w-32` input inside a table cell — extremely cramped. Overdue rows are not visually distinguished from normal rows (only the date text turns red). No scan-by-QR option is present in the UI even though QR workflows exist in the backend. No bulk return capability. |
| **Layout verdict** | Table remains correct. Fix data display (show names and titles). Add QR scan affordance. Make overdue rows use `danger-soft` background. |

---

## FINES

### `fines/index.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Fine management — pay or waive outstanding fines |
| **Intended user** | Librarian, Admin |
| **Current strengths** | The "waiver reason" requirement is a correct enforcement of policy. The empty state copy is genuinely warm and human. |
| **Critical weaknesses** | The waive form is a tiny inline `<input>` and button crammed into a table cell. This is impossible to use comfortably. The waive reason field width (`w-48`) clips on mobile completely. |
| **UX problems** | Fine amount displayed as a yellow badge (`bg-yellow-100`) — this is a functional signal, not a warning. Yellow should be reserved for genuine warnings. No sort by amount, member name, or days overdue. No total amount showing at the top. No "bulk waive" capability. |
| **Layout verdict** | Table-based is correct. Waive action should open a slide-out panel or modal — not inline form. |

---

## RESERVATIONS

### `reservations/index.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Waitlist queue management — FIFO queue for out-of-stock books |
| **Intended user** | Librarian, Admin |
| **Current strengths** | FIFO semantics are clearly communicated in the subtitle. The "Notified (Ready)" status is an important state that IS represented. |
| **Critical weaknesses** | Same structural anti-pattern as `members/index.html` — form + table crammed side by side. |
| **UX problems** | The "Add to Waitlist" form has two dropdowns — member dropdown and book dropdown. Dropdowns for large datasets are unusable. The book dropdown shows `({{ book.available_copies }} available)` — why would a librarian add a book with available copies to the waitlist? Filter the dropdown server-side. "Queued Since" formatted as `YYYY-MM-DD HH:MM` — inconsistent with other date formats on the site. |
| **Layout verdict** | Same recommendation as members — separate the form into a modal or dedicated route. |

---

## ANALYTICS

### `admin/dashboard.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Analytics overview — borrowing by category, batch email, CSV export |
| **Intended user** | Admin only |
| **Current strengths** | Chart.js integration exists and works. Batch email preview-before-send is the correct UX pattern. CSV export is genuinely useful. |
| **Critical weaknesses** | **This is a critically underdeveloped page.** One doughnut chart showing "borrowing by category" is the entirety of the analytics. An institutional library generates far richer data: borrowing trends over time, most/least borrowed books, member engagement, fine collection rates, peak hours. None of this is visualized. |
| **UX problems** | The chart lives inside `max-w-7xl` but only takes `w-1/2` of space — it is visually abandoned in a half-width card that floats disconnectedly. The "Batch Overdue Communications" table appears outside the main container `<div>` — it breaks the page's max-width constraint. The two "Send Reminders" buttons (header area + table area) create duplicate actions with different contexts. The `confirm()` dialog for batch email is an inaccessible native browser dialog. |
| **Chart colors**: `['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']` — none of these are from the design system. |
| **Layout verdict** | Redesign as a proper analytics dashboard with multiple metrics. Chart theming must use `--accent`, `--success`, `--warning`, `--danger` values. |

---

## POLICIES

### `admin/policies.html`
| Attribute | Assessment |
|---|---|
| **Purpose** | Fine policy editor — rate, grace days, cap per member tier |
| **Intended user** | Admin only |
| **Current strengths** | Policy cards per tier is a clean conceptual model. Three fields per policy is unambiguous. |
| **Critical weaknesses** | The input fields use bare `rounded-md border-gray-300 shadow-sm focus:border-blue-500` — not in the design system. No `border-libra-border`, no `var(--form-input)` tokens. |
| **UX problems** | No "current effective values" display alongside the edit form — a librarian cannot see what the rates currently are without looking at the inputs (which ARE the current values, but visually they look like empty fields). No "last modified" timestamp. No confirmation or change preview before saving. |
| **Layout verdict** | Cards per tier is correct. Redesign form inputs to use design system. |

---

## PARTIALS

### `books/partials/book_grid.html`
The highest-priority partial in the application. Books are the product. How a book is presented in the grid determines whether LIBRA feels like a library or a spreadsheet. The card must show cover, title, author, category, availability — in a hierarchy that respects the visual weight of each element.

---

## ERROR STATES & MISSING PAGES

**None exist.** No `404.html`, no `403.html`, no `500.html`, no maintenance page. This is a critical gap.

---

# DELIVERABLE 2 — Product Experience Vision

## The Core Insight

There are not one user type in LIBRA. There are two fundamentally different **operational contexts**:

1. **Operators** (Admin, Librarian): task-oriented, efficiency-driven, power users of daily workflows
2. **Patrons** (Student, Faculty, Staff): discovery-oriented, occasional users, need clarity not power

These two contexts should feel like different modes of the same product — not different products, but meaningfully differentiated experiences.

---

## ADMIN

**Daily reality**: Administrative oversight, strategic visibility, policy governance.

**Primary use cases** (in order of frequency):
1. Check dashboard KPIs — 60 seconds each morning
2. Run batch operations (reminders, exports)
3. Review analytics for acquisition decisions
4. Adjust fine policies (rare — monthly at most)
5. Register new librarian accounts

**What should be immediately visible**: Overdue count (with urgency), fine revenue, active member count, recent system events

**What should remain secondary**: Policy settings, analytics details, user management

**Navigation model**: Current nav rail is correct. Admin section is correctly separated.

**Key insight**: The Admin uses LIBRA strategically, not operationally. Their dashboard should answer "Is the library healthy?" not "What do I do next?"

---

## LIBRARIAN

**Daily reality**: Issuing and returning books, managing members, resolving waitlists, collecting fines.

**Primary use cases** (in order of frequency):
1. Issue a book — happens dozens of times daily
2. Process a return — happens dozens of times daily
3. Register a new member — happens occasionally
4. Process a fine payment or waiver
5. Manage waitlist

**What should be immediately visible**: Open issues that need action (overdue items, waitlist members to notify, fines pending)
**What should remain secondary**: Analytics, member history, catalog management

**Navigation model**: The Issue and Return flows are the librarian's primary workstation. These should be the fastest, most optimized flows in the product. Consider: a dedicated "Desk Mode" — a split-screen view showing Issue on the left and the return queue on the right. **This is a genuine alternative to the current sequential navigation model**.

**Rejected idea**: The current page layout forces librarians to navigate between Issue and Return as separate pages. At a busy circulation desk with 10 people in line, this is friction. Consider a unified "Circulation Desk" view.

---

## STUDENT (member tier)

**Daily reality**: Checking what they have borrowed, when it's due, whether they have fines.

**Primary use cases**:
1. Check current borrows + due dates
2. Browse the catalog
3. Join a waitlist for a book
4. Check fine status

**What should be immediately visible**: Due dates (especially anything due within 3 days), outstanding fines, reading goal progress

**What should remain secondary**: Library history, catalog browse

**Key insight**: Students visit LIBRA to check on their relationship with the library. The my_dashboard should feel like a personal account page — calm, informative, not gamified.

**Rejected design decision**: The existing "Grandmaster 👑", "2025 Quest", "Active Quests" gamification framing. A faculty member returning a book after 5 years should not feel like they are playing a mobile game. The reading goal should exist, but be presented as a quiet personal tracker — not a leaderboard rank.

---

## FACULTY

**Daily reality**: Longer loan periods, higher trust, occasional fine exemptions.

**Primary use cases**: Same as student but with longer time horizons. Faculty may have 10–15 books out simultaneously. The my_dashboard must handle this gracefully — a scrollable list of 15 books must not feel like a bug.

**Key difference from student**: Faculty care less about "gamification" and more about clear administrative visibility. Their dashboard should feel like a faculty account portal, not a student app.

---

## STAFF

**Daily reality**: Similar to faculty but less frequent usage. Staff members use the library occasionally and need clarity over features.

---

# DELIVERABLE 3 — Information Architecture

## What belongs on the dashboard?

**Admin Dashboard should answer**:
- How many books are overdue right now?
- How much revenue collected this month?
- What is the most borrowed category?
- Are there any system-level alerts (velocity flags)?

**Do NOT put on the admin dashboard**: Analytics charts (they belong in their own analytics page), policy settings, member management.

**Librarian Dashboard should answer**:
- What needs my attention right now? (overdue returns, waitlist notifications)
- How many transactions today?

**Member Dashboard should answer**:
- What do I currently have borrowed?
- When are things due?
- Do I have outstanding fines?
- How is my reading goal going?

## What deserves its own page?

- **Member Profile** — currently does not exist. Every member row should link to a member profile showing their full borrowing history, fine history, and current borrows.
- **Book Detail** — exists, correct decision.
- **Transaction History** — no dedicated page exists. There is no way to see all transactions.
- **Analytics** — exists but underdeveloped. Should be a full analytics dashboard.
- **Fine History** — no way to view resolved/waived fines.

## What should become a reusable component?

- **Stat card** (`.card-stat`) — number + label + optional trend indicator
- **Member pill** — avatar initial + name + tier badge (used in transactions, fines, waitlist)
- **Book row** — cover thumbnail + title + author + availability (used in issue form, return table)
- **Due date badge** — color-coded (green/amber/red) based on days remaining
- **Action confirmation sheet** — a bottom sheet or modal for destructive or irreversible actions

## Where are users likely to get lost?

1. **After issuing a book** — success flash disappears in 4s, then back to the empty issue form. Users have no confirmation receipt, no link to the transaction, no summary.
2. **Return page with no book titles** — "Copy #14" creates confusion about what is being returned.
3. **Fines page** — "Txn #{{ fine.transaction_id }}" makes it impossible to identify which fine belongs to which book without cross-referencing other pages.

## What should be discoverable?

- QR code links from book copies (currently exist but have no visual entry point in the main UI)
- Member profile (does not yet exist)
- Transaction receipt after issue

## What should remain intentionally hidden?

- System log raw action strings (`USER_LOGGED_IN`, `BOOK_ISSUED`) — these are already filtered by role correctly
- Internal IDs (copy ID, transaction ID) should never be the primary identifier shown to users — they are acceptable as secondary reference IDs but should never lead

## Breadcrumbs

Every non-dashboard page should have a breadcrumb:
- `Books` → `The Great Gatsby` (book detail)
- `Members` → `Arjun Mehta` (member profile)
- `Admin` → `Analytics` (analytics page)
- `Admin` → `Policies` (policies page)

The current `books/detail.html` has a breadcrumb — it is the only one. Every other page starts orphaned without navigation context.

## Should command palettes exist?

**Yes — but not yet.** This is a Phase 3.7+ feature. A `Cmd+K` command palette that lets librarians quickly jump to "Issue book", "Return book", "Find member [name]" would be a premium touch. It should not be built until all base pages are solid. Flag for Phase 3.8.

## Should quick actions exist?

**Yes.** The admin dashboard should have a "Quick Actions" row:
- Issue Book (→ issue form)
- Process Return (→ return table)
- Add Member (→ member registration)
- Export CSV (→ direct action)

The librarian daily workflow starts here.

## Should dashboards become role-specific?

**Yes. They already are — but the routing is fragile.** The `main.dashboard` route dispatches to different templates based on role. This is the correct pattern. It must remain. The admin sees `dashboard.html`, members see `my_dashboard.html`. This split should be made more explicit in the code, and the `my_dashboard.html` should be renamed to `member_dashboard.html` for clarity.

---

# DELIVERABLE 4 — Missing Experiences

## Error Pages (None exist — Critical)

| Page | Status | What it must communicate |
|---|---|---|
| `errors/404.html` | **MISSING** | "This page doesn't exist." — with navigation back to dashboard |
| `errors/403.html` | **MISSING** | "You don't have permission." — with role context |
| `errors/500.html` | **MISSING** | "Something went wrong on our end." — calm, not technical |
| `errors/maintenance.html` | **MISSING** | "We'll be back shortly." — with estimated time if possible |

All error pages should share the Libra visual language — parchment background, typographic wordmark, a single calm sentence, and a single action link. No stack traces. No technical jargon. No apology emojis.

## Empty States (Partially exists — Inconsistent)

| Context | Current state | Required |
|---|---|---|
| Fines table — no fines | ✅ Has empty state (warm copy) | Needs design system styling |
| Return table — no borrows | Weak: "No active borrows found. The library is fully stocked!" | Redesign with icon + action |
| Members table — no members | Weak: "Register your first student using the form!" | Redesign |
| Books grid — no search results | **MISSING** — HTMX returns empty grid silently | Must add "No books found for '{{ query }}'" state |
| Reservations queue — empty | Has icon + copy | Needs design system styling |
| Member dashboard — no borrows | Has empty state | Needs redesign |

Every empty state must follow the `.empty-state` component pattern established in `base.html`.

## Loading States

| Context | Current state | Required |
|---|---|---|
| Book search (HTMX) | ✅ Spinner indicator exists | Redesign spinner to match design system color |
| Issue form submission | None — button stays enabled | Button must show loading state + disable |
| Return form submission | None | Same |
| Fine pay/waive submission | None | Same |
| ISBN auto-fetch | ✅ Button state handled in JS | Improve — show skeleton in cover preview area |

## Skeleton Screens

Currently absent everywhere. For the books grid (the highest-traffic HTMX endpoint), a skeleton loader grid of 10 placeholder cards would prevent layout shift and communicate "loading" state more gracefully than a spinner alone.

## Confirmation Flows — Currently Broken

| Action | Current behavior | Required behavior |
|---|---|---|
| Pay fine | `onclick="return confirm(...)"` — native browser dialog | Replace with a designed confirmation panel showing the amount and member name |
| Batch email | `onclick="return confirm(...)"` — native browser dialog | Replace with a confirmation modal showing the preview list count |
| Issue book | No confirmation | Add a transaction preview step |
| Waive fine | Inline form without visual confirmation | Replace with a slide-out panel |

Native browser `confirm()` dialogs are inaccessible, unbranded, and cannot be styled. They must be replaced entirely.

## Undo Actions

Currently absent. The most critical undo scenario: **accidental fine payment**. A "Mark Paid" button with no undo leaves no recovery path if the wrong fine is paid. A 5-second toast with an "Undo" action (that calls a reverse endpoint) would solve this.

## Missing Pages — Not Just States

1. **Member Profile page** (`/members/<id>`) — completely absent. Every member row in the table is a dead link. A member profile should show: name, email, tier, join date, current borrows, fine history, borrowing history.
2. **Transaction History page** — no page to see all historical transactions. The only transaction view is the "active borrows" return table.
3. **Book edit page** — `books/form.html` is titled "Add New Book" but there is likely no edit route (the form `action=""` posts to the current URL). Editing an existing book's metadata is currently impossible from the UI.

## Keyboard Shortcuts

None exist. Minimum viable set for Phase 3.8:
- `Escape` to close modals/dropdowns (partially implemented for dropdown)
- `?` to show keyboard shortcut reference
- `Cmd+K` for command palette (Phase 3.8)

## Accessibility Improvements Required

1. All form inputs missing `id`/`for` label association in many templates
2. Color alone used to convey status (overdue = red text) — needs text label as well
3. Activity timeline in `dashboard.html` has `<ol>` but timeline items are complex — need `aria-label` on each item
4. `<button>` elements inside forms have no `type="button"` guard where appropriate — can cause accidental form submissions
5. Focus management when modals open/close (not yet relevant — no modals exist yet)

## Mobile-Specific Gaps

1. The book grid is 5 columns on desktop — on mobile it becomes 1 column with very tall cards. Cards are not optimized for portrait mobile reading.
2. The Issue and Return forms use full-width dropdowns — correct for mobile but without typeahead, unusable on a phone.
3. The waitlist and fines forms are cramped even on desktop — on mobile they are unusable.

## Premium Experiences Not Yet Imagined

These are forward-looking ideas for Phase 3.8–3.9. Not required for the initial implementation:

1. **Circulation receipt** — after issuing, a printable/shareable receipt showing member name, book title, due date, fine rate.
2. **QR scan workflow** — a `/scan` page with a camera input that reads a QR code and pre-fills the return form.
3. **Fine breakdown tooltip** — hover on a fine amount to see the daily rate × days calculation.
4. **Due-soon banner** — members approaching due dates should see a non-intrusive banner on every page: "2 books due in 3 days."
5. **Overdue acknowledgement** — when a librarian is about to issue a book to a member with outstanding fines, a warning panel appears before proceeding.

---

# DELIVERABLE 5 — Phase 3 Master Implementation Plan

## Why this structure?

The roadmap is organized by **blast radius**. We build from the inside out — the components that everything else depends on first, then the pages that use them.

Phase 3.2 (Foundation) → Phase 3.3 (Auth + Navigation) → Phase 3.4 (Dashboards) → Phase 3.5 (Catalog) → Phase 3.6 (Operations) → Phase 3.7 (Analytics) → Phase 3.8 (Edge Cases + System Pages) → Phase 3.9 (Accessibility + Refinement)

The principle: **never build a page before its components exist.**

---

## Phase 3.2 — Foundation (COMPLETED)
**Goal**: Establish the visual operating system. Every future page inherits from this.

- [x] CSS custom properties (`:root` design tokens)
- [x] Tailwind palette extension (`libra.*` colors)
- [x] Inter typography
- [x] Global component library (`.card`, `.btn`, `.badge`, `.form-input`, `.data-table`, `.empty-state`, `.page-header`)
- [x] Hybrid nav rail (72px → 180px on hover)
- [x] Top bar
- [x] Toast notification system
- [x] Splash screen
- [x] Mobile bottom nav
- [x] HTMX transition hooks

**Status**: COMPLETE. Design system is locked and verified.

---

## Phase 3.3 — Auth & Navigation
**Goal**: The front door should feel like the institution.

### `auth/login.html`
- Full-bleed two-panel layout on desktop. Left panel: parchment + Libra wordmark (large, typographic) + tagline. Right panel: clean login form using `.form-input`, `.form-label`, `.btn-primary`.
- Flash errors rendered as inline alert below the form — not external toast.
- Password show/hide toggle button.
- `autocomplete="email"` and `autocomplete="current-password"` on inputs.
- On mobile: single column, wordmark at top, form below.

### Navigation (base.html cleanup)
- Migrate all remaining hardcoded inline colors in the HTML body (not CSS) to use design system classes.
- Update active nav item detection for edge cases (e.g., when on `books.book_detail`, the Books nav item should still be active).

---

## Phase 3.4 — Dashboard Experiences
**Goal**: The most-visited pages must feel most polished.

### `dashboard.html` (Admin/Librarian)
- Remove all `dark:*`, `text-gray-*`, `bg-blue-*` classes.
- Stat card redesign:
  - `total_books` → `.card` (white, standard)
  - `active_members` → `.card` (white, standard)
  - `overdue_books` → `.card-dark` (walnut, commanding). Number links to filtered return table.
  - `pending_fines` → `.card` with danger accent. Number in `var(--danger)`.
  - `total_fines_paid` → `.card` with success accent.
- Add trend arrows (↑↓) if `stats` object can provide delta values — flag as a backend request if data isn't available.
- Activity timeline:
  - Replace `text-gray-*` with `var(--text-*)` variables
  - Show book title in log description, not just raw action string
  - Remove action strings like `BOOK_ISSUED` — show humanized labels
- "Quick Issue Book" button: fix the broken `request.endpoint` condition. Always show for librarian/admin roles.
- Remove the 👋 emoji. Replace with a quiet secondary text: "Good morning, {{ current_user.name }}."

### `my_dashboard.html` → renamed `member_dashboard.html`
- **Completely rebuilt visually.** Data architecture preserved.
- Welcome section: simple `<h1>Good morning, {{ current_user.name }}</h1>` with date.
- Reading goal: becomes a quiet `.card` component — a thin progress bar at natural height (not 4px athletic bar), `{{ goal.books_read }} of {{ goal.target_books }} books this year`. The rank system stays but replaces `Grandmaster 👑` with: `Scholar · 20+ books`.
- Borrowed books: becomes a `.data-table` inside `.table-wrap`. Shows: book title (not copy ID), due date, status badge using `.badge-success` / `.badge-danger`.
- Fines: becomes a `.card` with total amount as a `.card-dark` headline stat if fines > 0. Each fine shows book title, not transaction ID. Shows "No outstanding fines." with `.empty-state` when clear.

---

## Phase 3.5 — Catalog (Book Ecosystem)
**Goal**: Books are the product. Every surface that touches a book should feel curated.

### `books/partials/book_grid.html` — Highest priority redesign
- Book card: `var(--surface)` background, `var(--border)` border, 12px radius.
- Cover image area: fixed aspect ratio (2:3). If no cover: typographic fallback showing first letter of title in a warm colored background derived from the title string (deterministic color, not random).
- Title: 13px, `font-weight: 600`, `var(--text-primary)`, max 2 lines with `line-clamp-2`.
- Author: 12px, `var(--text-muted)`.
- Availability badge: `.badge-success` (copies > 0) or `.badge-danger` (out of stock).
- Hover: subtle `box-shadow` elevation. No scale transform — it's a library, not a shopping app.

### `books/index.html`
- Remove all hardcoded gray/blue classes.
- Add filter bar: Category pills (HTMX-powered) + Sort dropdown (Most borrowed, Title A–Z, Newest).
- Add result count: "Showing 24 of 147 books" above the grid.
- Search input: use `.form-input` class. Replace `text-blue-600` spinner with one styled using `var(--accent)`.

### `books/detail.html`
- Remove all `dark:*`, `from-indigo-50 to-blue-50` gradients.
- Typographic book cover fallback for no-cover books.
- "Physical Copies Inventory" section: relabel to "Availability" for staff. Use `.data-table`.
- Breadcrumb: use a standardized breadcrumb component.
- Waitlist/recommendation sections: use design system surfaces.

### `books/form.html`
- ISBN auto-fetch card: use `.card` + `badge-accent` label. Replace inline alert with toast.
- All form inputs: use `.form-input`, `.form-label`, `.form-select`.
- Remove `alert()` — replace with inline validation message.
- Submit button: use `.btn.btn-primary` (blue accent, not green).
- Add cancel/back navigation button (`.btn.btn-ghost`).

---

## Phase 3.6 — Operational Workflows
**Goal**: The librarian's workstation must be fast. Every extra click costs a patron in the queue.

### `transactions/issue.html` — Most impactful redesign
- Replace `<select>` dropdowns with HTMX typeahead search inputs:
  - Member search: `hx-get="/members/search?q=..."`, shows name + tier + current borrow count + fine status.
  - Book search: `hx-get="/books/search?q=..."`, shows title + author + available copies.
- Add **transaction preview panel** that appears after both selections are made (HTMX swap): shows member name, book title, due date, fine rate.
- Submit button: "Confirm Issue" — only enabled after both fields are selected.
- Loading state on submit: button disabled + spinner.
- Requires **new HTMX search endpoints** on the backend — flag for backend team (this is a frontend architecture decision, not a backend logic change).

### `transactions/return.html`
- Show member names (not "Member ID: 42").
- Show book titles (not "Copy #14").
- Overdue rows: use `background: var(--danger-soft)` on the entire `<tr>`.
- Add QR scan button in the page header: "Scan QR" → `/scan` page (Phase 3.8).
- Processing loading state on return button.
- Replace bare `<input>` notes field with a styled `.form-input`.

### `members/index.html` — Split into two concerns
1. **Members roster** (`/members`): Full-width searchable table using `.data-table`. HTMX search bar at top. Tier filter pills. Each row links to member profile.
2. **Registration**: Modal overlay triggered by "Register Member" button. Uses the same form fields, but in a focused modal context.

### `fines/index.html`
- Inline waive form → becomes a "Waive Fine" action button that opens a confirmation/reason panel.
- Fine amount: use `.badge-warning` (not `.badge-danger` — a fine is not a system error).
- Add summary bar at top: "₹{{ total_pending }} outstanding across {{ count }} members."
- Sort controls: by amount (desc), by days overdue (desc).

### `reservations/index.html`
- Same pattern as members — move Add to Waitlist form into a modal/sheet.
- Full-width queue table with `.data-table`.
- Show queue position number as the first column (#1, #2, #3 in line).
- Replace `YYYY-MM-DD HH:MM` with relative time: "3 days ago."

### `admin/policies.html`
- All inputs: use `.form-input`.
- Show "currently effective" values as read-only display next to inputs (so a librarian can see what will change before editing).
- Add "Last modified: [date]" to each policy card.
- Save button: `.btn.btn-primary`.

---

## Phase 3.7 — Analytics & Intelligence
**Goal**: Give the Admin genuine strategic visibility.

### `admin/dashboard.html` — Full rebuild
- Move the orphaned `<div>` outside the max-width container back inside the page container (structural bug fix).
- Remove duplicate "Send Reminders" buttons — keep only the table-area button with proper confirmation.
- Replace `confirm()` with a designed confirmation modal.
- Add metrics:
  - Borrowing trend chart (last 30 days, line chart)
  - Top 5 most borrowed books (horizontal bar chart)
  - Fine collection this month vs. last month
- All chart colors: use `var(--accent)`, `var(--success)`, `var(--warning)`, `var(--danger)`.
- Chart.js loaded in `{% block extra_scripts %}` — not globally.

---

## Phase 3.8 — Error States, Edge Cases & System Pages
**Goal**: The moments of failure must be as considered as the moments of success.

### Error pages (all new)
- `errors/404.html`: Parchment background. Wordmark. "Page not found." One sentence. One link back to dashboard.
- `errors/403.html`: Same structure. "You don't have access to this page."
- `errors/500.html`: Same structure. "Something went wrong. Our team has been notified." (even if that's aspirational)

### Skeleton loaders
- Book grid skeleton: 10 placeholder cards using `var(--surface-raised)` with pulse animation via `@keyframes`.
- Transaction table skeleton for return page.

### Confirmation components
- `LibraConfirm` — a JavaScript function that shows a designed confirmation dialog (HTML overlay, not `confirm()`). Takes: `{title, body, confirmLabel, cancelLabel, onConfirm}`. Used for: fine payment, batch email, waive fine.

### Undo toasts
- After "Mark Paid" on a fine: toast includes "Undo" button that POST to `/fines/<id>/unpay` within 8 seconds.

### Due-soon banner
- A persistent thin banner (not a toast) injected into every authenticated page for members with books due ≤ 3 days: "2 books due in 3 days — view your account."

### QR Scan page (`/scan`)
- A simple page with a camera input using the browser's `capture="environment"` or a QR library.
- Decodes QR → looks up copy → pre-fills the return form.
- This requires a backend `/scan` route — flag for backend team.

### Command palette (`Cmd+K`)
- Lightweight implementation: a full-screen overlay with a single search input. Results: pages (issue, return, members), books by title, members by name. All client-side for page navigation, HTMX for data.

---

## Phase 3.9 — Accessibility & Mobile Polish
**Goal**: The product works for everyone, not just sighted users on a laptop.

### Accessibility audit
- All form inputs: verify `id`/`for` pairing.
- All interactive elements: verify keyboard focus rings use `var(--accent)`.
- All color-coded states: verify text labels accompany color (WCAG 1.4.1).
- All tables: verify `scope` attributes on `<th>` elements.
- All toast notifications: verify `role="alert"` and `aria-live="polite"`.
- All modals/overlays: focus trap, `aria-modal`, Escape to close.
- All icon-only buttons: verify `aria-label`.

### Mobile polish
- Book grid on mobile: switch from cards to a compact horizontal list format on screen width < 480px.
- Issue/Return: typeahead inputs must have good touch targets (min 44px height).
- Bottom nav: review active state contrast on the parchment/border palette.
- Test splash screen on mobile Safari (lottie-player rendering).

---

## Execution Principles

1. **One page at a time.** Complete `auth/login.html` fully before touching `dashboard.html`.
2. **Verify after every page.** Run template parse check. Confirm Flask renders without error.
3. **Never hardcode a color.** Every value must reference a CSS variable from `:root` or a Tailwind `libra.*` utility.
4. **Preserve all backend behavior.** Form `action` URLs, HTMX endpoints, and method attributes are never changed.
5. **Page title block.** Every template must set `{% block title %}Page Name{% endblock %}` and `{% block page_title %}Page Name{% endblock %}`.

---

## Open Questions for Review

> [!IMPORTANT]
> **Q1 — Typeahead search in Issue form**: The Issue form redesign (Phase 3.6) requires two new backend endpoints: `GET /members/search?q=` and `GET /books/search?q=`. These are not backend logic changes (no business rules touched) — they are query endpoints that return JSON or HTML partials. Do you approve adding these routes?

> [!IMPORTANT]
> **Q2 — Member Profile page**: A `/members/<id>` page requires a backend route. It would query the member's transaction history and fine history. Do you want this in scope?

> [!IMPORTANT]
> **Q3 — Librarian "Desk Mode"**: I proposed a unified Circulation Desk view (Issue + Return on one screen). This is a significant UX departure from the current navigation model. Do you want to explore this, or maintain the current separate pages?

> [!WARNING]
> **Q4 — `my_dashboard.html` gamification**: I've proposed removing the gaming language (Quests, Grandmaster) and replacing with institutional vocabulary. The data (reading goal, borrowed books, fines) stays. Only the framing changes. This is a strong recommendation. Do you want to override it?

> [!NOTE]
> **Q5 — Execution order**: I propose starting with Phase 3.3 (login page) immediately upon approval. It is a contained, high-impact win with zero risk to existing functionality.
