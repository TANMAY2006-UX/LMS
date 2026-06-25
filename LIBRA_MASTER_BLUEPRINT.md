# LIBRA — Library Operations Platform
## Master Project Blueprint v1.0
### The Single Source of Truth for All Agents & Contributors

---

## 0. CONTEXT & CONSTRAINTS

**What this is:** A production-grade Library Management System built as a Frappe internship assignment. The evaluators are senior engineers who will read the code and architecture decisions — not just demo the UI.

**Hard constraints:**
- Backend: Flask (mandatory)
- No AI/LLM features inside the app itself
- Timeline: 4–5 days
- Solo build with AI agent assistance (Antigravity/Gemini/Claude)
- Must be explainable line-by-line to evaluators
- Phase 2 will migrate to Frappe Framework — so mental models must align

**Agent instruction:** Write 50–60 lines of code per response. Never dump 300 lines at once. Each block must be explainable.

---

## 1. THE BIG DECISION — BookCopy vs. Lineage Table (Kankush's Question)

This was a genuine architectural debate. Here is the final answer with reasoning.

### Option A: Individual BookCopy Rows (what we originally planned)
Each physical copy is a separate database row with its own status.

```
book_copies
  id=1, book_id=5, status=AVAILABLE
  id=2, book_id=5, status=ISSUED
  id=3, book_id=5, status=DAMAGED
```

### Option B: Lineage / Counter Approach (Kankush's suggestion)
Just track counts on the Book itself. All audit lives in the transactions table.

```
books
  id=5, total_copies=3, available_copies=2

transactions
  book_id=5, member_id=12, action=ISSUE, timestamp=...
  book_id=5, member_id=12, action=RETURN, timestamp=...
```

### FINAL DECISION: Hybrid — Simple BookCopy + Lineage Records

**Why not pure Option B:** If you only have counters, you cannot answer:
- "Which specific copy is Rahul holding right now?"
- "How many times has copy #3 been issued?" (wear tracking)
- "This copy was reported damaged — which one exactly?"

Without individual copy rows, the librarian cannot manage physical objects — only abstract numbers.

**Why not over-engineered Option A (with condition lifecycle, maintenance states, etc.):** Kankush is right that for a 4–5 day build, condition tracking adds complexity without proportional value. The librarian will handle physical condition manually.

**The Hybrid:**
- Keep `book_copies` table but keep it SIMPLE (just `id`, `book_id`, `status`, `added_date`)
- Status is only: `AVAILABLE | ISSUED | RESERVED`
- Condition is NOT tracked in DB — librarian handles physically
- All history lives in `transactions` (the lineage table Kankush wanted)
- Damaged books: librarian simply deletes the copy row (or marks WITHDRAWN) with a note in the audit log

This gives you copy-level precision AND a clean audit trail. Best of both worlds.

---

## 2. ROLES — Final Definition

Three roles. Clean separation. No ambiguity.

| Role | What They Can Do |
|------|-----------------|
| **Admin** | Create/manage member accounts, set fine policies, view all reports, manage system configuration |
| **Librarian** | Add/edit/delete books and copies, issue books, process returns, manage reservations, view dashboards |
| **Member** | Browse books, view own transactions, reserve books, pay fines, set reading goals |

**Key rule:** Members cannot see other members' data. Librarians cannot change system configuration. Admin cannot issue books (they're not operational staff).

**Implementation:** Flask-Login for sessions. A `role` column on the `users` table. A `@role_required('librarian')` decorator that wraps protected routes.

---

## 3. FINAL TECH STACK — Locked, No More Debate

### Backend
```
Flask                    v3.x    — core framework
Flask-SQLAlchemy         v3.x    — ORM
Flask-Migrate                    — database migrations (Alembic wrapper)
Flask-Login                      — session auth (NOT JWT — explained below)
Flask-Mail                       — email notifications
Flask-WTF                        — form validation + CSRF protection
APScheduler                      — 2 scheduled jobs only (overdue check + reservation expiry)
psycopg2-binary                  — PostgreSQL driver
python-dotenv                    — environment variable management
requests                         — ISBN auto-fetch from OpenLibrary API
qrcode[pil]                      — QR code generation per book copy
```

**Why Flask-Login NOT JWT:**
JWT is for stateless APIs consumed by separate frontends (React, mobile). We are rendering HTML on the server with Jinja2. Flask-Login uses a secure session cookie — one decorator `@login_required` protects any route. JWT here would add complexity with zero benefit. If an evaluator asks: "why not JWT?" — answer exactly this.

**Why APScheduler NOT Celery:**
Celery requires a separate broker process (Redis/RabbitMQ) and a separate worker process. That's 3 processes to manage instead of 1. APScheduler runs inside the Flask process. For 2 lightweight jobs (overdue check, reservation expiry) running once per day, APScheduler is correct. Celery would be right if we had thousands of users with heavy async tasks.

### Database
```
PostgreSQL
```

**Why NOT SQLite:** SQLite locks the entire file on writes. Two librarians issuing books simultaneously on SQLite causes one to wait or fail. PostgreSQL handles concurrent writes correctly with row-level locking. Also: you're targeting Frappe, which runs on MariaDB/PostgreSQL. Showing PostgreSQL shows production thinking. Setup is 5 minutes with `createdb libra`.

### Frontend
```
Jinja2           — server-side HTML rendering (Flask native)
HTMX   v1.9.x   — dynamic page updates without writing JavaScript
Alpine.js v3.x  — micro-interactions (modals, dropdowns, toggle states)
Tailwind CSS     — utility-first styling via CDN (no build pipeline needed)
Flowbite         — Tailwind component library (modals, tables, badges pre-built)
Chart.js         — analytics charts
```

**Why this stack produces a professional UI:**
- Tailwind + Flowbite gives you Linear/Notion-quality components without designing from scratch
- HTMX makes interactions feel instant — book search updates as you type, reservation queue updates without page reload
- No React, no npm, no webpack, no build step — pure HTML files that Flask renders
- This is EXACTLY how Frappe's frontend works (Python-driven HTML, targeted DOM updates). When evaluators see this, they recognize the pattern.

**Will this look professional?** Yes. Flowbite has production-quality table components, stat cards, sidebars, modals, badges, and alerts — all Tailwind-based. Many real SaaS products use this exact stack.

---

## 4. DATABASE DESIGN — Final Schema with Full Reasoning

### ERD Overview
```
users ──< transactions >── book_copies >── books >── categories
  |                              |
  └──< reservations >───────────┘
  |
  └──< reading_goals
  |
  └──< audit_log
  
fine_policies ──< fines >── transactions
```

### Table: `users`
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100) NOT NULL
email           VARCHAR(150) UNIQUE NOT NULL
password_hash   VARCHAR(256) NOT NULL
role            VARCHAR(20)  NOT NULL  -- 'admin', 'librarian', 'member'
tier            VARCHAR(20)  NOT NULL  DEFAULT 'student'  -- 'student', 'faculty', 'staff'
is_active       BOOLEAN      DEFAULT TRUE
joined_date     DATE         DEFAULT CURRENT_DATE
created_at      TIMESTAMP    DEFAULT NOW()
```

**Why `tier` separate from `role`:** Role controls what you CAN DO (permissions). Tier controls what rules APPLY TO YOU (fine rates, borrow limits). A faculty member has tier=faculty but role=member. An admin might have tier=staff. They are independent dimensions.

### Table: `books`
```sql
id              SERIAL PRIMARY KEY
isbn            VARCHAR(13)  UNIQUE NOT NULL
title           VARCHAR(255) NOT NULL
author          VARCHAR(255) NOT NULL
description     TEXT
cover_url       VARCHAR(500)
publisher       VARCHAR(150)
published_year  INTEGER
category_id     INTEGER REFERENCES categories(id)
total_copies    INTEGER DEFAULT 0          -- maintained by trigger/service
available_copies INTEGER DEFAULT 0        -- maintained by service on every issue/return
created_by      INTEGER REFERENCES users(id)
created_at      TIMESTAMP DEFAULT NOW()
```

**Why store `available_copies` denormalized:** You could always compute this with `SELECT COUNT(*) FROM book_copies WHERE book_id=X AND status='AVAILABLE'`. But this runs on EVERY book listing page. Denormalizing to a counter means the listing page is one fast query. The service layer is responsible for keeping this in sync on every issue/return. This is a deliberate performance trade-off.

### Table: `categories`
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100) UNIQUE NOT NULL
slug            VARCHAR(100) UNIQUE NOT NULL
description     TEXT
```

Simple lookup table. Slug for clean URLs (`/books/category/fiction`).

### Table: `book_copies`
```sql
id              SERIAL PRIMARY KEY
book_id         INTEGER REFERENCES books(id) ON DELETE CASCADE
status          VARCHAR(20) DEFAULT 'available'  -- 'available', 'issued', 'reserved', 'withdrawn'
added_date      DATE DEFAULT CURRENT_DATE
notes           TEXT    -- librarian notes (e.g., "spine repaired")
```

**Why so simple:** Kankush was right. We don't need barcode, condition lifecycle, shelf location for this phase. The copy exists to give each physical book an identity so we can track exactly who has exactly which copy. Nothing more. The `notes` field lets a librarian record physical observations without us building a whole condition system.

**Why no `barcode` column:** Barcode scanning requires hardware integration. For this phase, copies are identified by their DB id. The QR code we generate IS effectively the barcode.

### Table: `transactions`
```sql
id              SERIAL PRIMARY KEY
copy_id         INTEGER REFERENCES book_copies(id)
member_id       INTEGER REFERENCES users(id)
issued_by       INTEGER REFERENCES users(id)     -- librarian who issued
issued_at       TIMESTAMP DEFAULT NOW()
due_date        DATE NOT NULL
returned_at     TIMESTAMP
returned_by     INTEGER REFERENCES users(id)     -- librarian who processed return
status          VARCHAR(20) DEFAULT 'active'     -- 'active', 'overdue', 'returned'
notes           TEXT
```

**This IS the lineage table Kankush wanted.** Every issue/return creates a row here. You never update a returned transaction's core data — you add `returned_at` and change `status`. The full history of any copy or member lives here.

### Table: `fines`
```sql
id              SERIAL PRIMARY KEY
transaction_id  INTEGER REFERENCES transactions(id)
amount          NUMERIC(8,2) NOT NULL
days_overdue    INTEGER
calculated_at   TIMESTAMP DEFAULT NOW()
paid_at         TIMESTAMP
waived_at       TIMESTAMP
waived_by       INTEGER REFERENCES users(id)
waiver_reason   TEXT
status          VARCHAR(20) DEFAULT 'pending'    -- 'pending', 'paid', 'waived'
```

**Why separate `fines` table not in `transactions`:** A transaction can have multiple fine events (partial payments, waivers, disputes). Putting fine data in `transactions` means either multiple columns or update conflicts. A separate table means each fine event is its own immutable record.

### Table: `fine_policies`
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(100)
applies_to_tier VARCHAR(20)           -- 'student', 'faculty', 'staff', 'default'
grace_days      INTEGER DEFAULT 0
rate_per_day    NUMERIC(6,2) NOT NULL
max_fine_cap    NUMERIC(8,2)
exclude_weekends BOOLEAN DEFAULT TRUE
is_active       BOOLEAN DEFAULT TRUE
```

**Why a table and not hardcoded:** If the library decides faculty get 2 extra grace days, the admin changes a row in this table from the UI. No code change, no deployment. This is policy-as-data. It's also directly analogous to how Frappe stores configuration — in DocType records, not in Python code.

### Table: `reservations`
```sql
id              SERIAL PRIMARY KEY
book_id         INTEGER REFERENCES books(id)
member_id       INTEGER REFERENCES users(id)
queued_at       TIMESTAMP DEFAULT NOW()
queue_position  INTEGER
status          VARCHAR(20) DEFAULT 'waiting'   -- 'waiting', 'notified', 'fulfilled', 'expired', 'cancelled'
notified_at     TIMESTAMP
expires_at      TIMESTAMP                        -- set when notified (48hr window)
fairness_score  INTEGER DEFAULT 0               -- incremented each time bumped
```

**Why `fairness_score`:** FIFO alone creates a problem — if the first person in queue is away when notified, they expire and go to the back. If they keep getting unlucky, they never get the book. Fairness score increments every time a reservation expires. When sorting the queue, it's `ORDER BY fairness_score DESC, queued_at ASC` — people who've been bumped more get priority.

### Table: `audit_log`
```sql
id              SERIAL PRIMARY KEY
action          VARCHAR(100) NOT NULL    -- 'BOOK_ADDED', 'COPY_WITHDRAWN', 'FINE_WAIVED', etc.
entity_type     VARCHAR(50)             -- 'book', 'member', 'transaction'
entity_id       INTEGER
description     TEXT NOT NULL           -- human-readable: "Fine of ₹50 waived for member Rahul by Librarian Priya"
actor_id        INTEGER REFERENCES users(id)
timestamp       TIMESTAMP DEFAULT NOW()
```

**Why NOT JSONB for old/new values:** Gemini suggested JSONB diffs. That's fine for large-scale audit systems, but it adds complexity here. A human-readable `description` string serves the evaluator demo perfectly — you can display a timeline feed that any non-technical person understands. Keep it simple.

### Table: `reading_goals`
```sql
id              SERIAL PRIMARY KEY
member_id       INTEGER REFERENCES users(id)
year            INTEGER
target_books    INTEGER
books_read      INTEGER DEFAULT 0       -- updated on each return
created_at      TIMESTAMP DEFAULT NOW()
```

Simple. One row per member per year.

---

## 5. FEATURES — Complete List, Phased

### Phase 0 — Foundation (Day 1, ~6 hours)
*Goal: Running app with auth and basic data models*

- [ ] Project structure setup (app factory, extensions, blueprints)
- [ ] PostgreSQL connection + all migrations
- [ ] User model + Flask-Login setup
- [ ] Login / Logout / Session management
- [ ] Role-based route decorators
- [ ] Base HTML template with Tailwind + Flowbite sidebar layout
- [ ] Category CRUD (Admin only)
- [ ] Book CRUD with ISBN auto-fetch from OpenLibrary API
- [ ] BookCopy management (add copies to a book, mark withdrawn)
- [ ] Member management (Admin creates accounts, assigns roles/tiers)

**End of Phase 0:** You can log in as three roles. Books and copies exist in the database. UI has the sidebar layout working.

### Phase 1 — MVP Core Operations (Day 2, ~8 hours)
*Goal: A working library — issue, return, fine, reserve*

- [ ] Issue workflow: Librarian selects member → selects book → system picks available copy → creates transaction → decrements `available_copies`
- [ ] Return workflow: Librarian scans/selects copy → marks returned → triggers fine calculation → increments `available_copies` → checks reservation queue
- [ ] Fine calculation service: reads `fine_policies`, calculates days overdue excluding weekends if set, applies cap
- [ ] Fine payment: Member pays fine, librarian marks paid
- [ ] Fine waiver: Librarian can waive with mandatory reason (logged in audit)
- [ ] Reservation: Member reserves a book → joins queue → gets position
- [ ] Reservation queue management: On return, system auto-notifies next in queue
- [ ] APScheduler job 1: Daily overdue check — marks active transactions past due_date as 'overdue'
- [ ] APScheduler job 2: Daily reservation expiry — expires notified reservations older than 48hrs, moves queue
- [ ] Member dashboard: My active books, due dates, fines, reservations
- [ ] Librarian dashboard: Today's issues, returns, overdue count, pending fines

**End of Phase 1:** This is the MVP. A library can actually run on this.

### Phase 2 — Product Depth (Days 3–4, the differentiators)
*Goal: Features that show product thinking, not just CRUD*

- [ ] QR codes: Generate QR per book copy (links to copy detail page). Display on book detail. Librarian can print.
- [ ] Co-borrowing recommendations: SQL query on transactions table — "Members who borrowed this also borrowed..." Displayed on book detail page.
- [ ] Reading goals: Member sets yearly target. Progress bar. Simple milestone check on each return.
- [ ] Activity timeline: Per-member chronological feed of all actions from audit_log.
- [ ] Overdue email reminders: Flask-Mail sends reminder to overdue members (triggered by APScheduler job 1).
- [ ] Reservation notification emails: Flask-Mail notifies member when their reservation is ready.
- [ ] Batch operations: Librarian selects multiple overdue members → send bulk reminder.
- [ ] Book search with live HTMX: As-you-type search updates book list without page reload.
- [ ] Analytics dashboard: Chart.js charts — most borrowed books, borrowing by category, monthly trends, member activity.
- [ ] CSV report export: Overdue report, fine collection summary, popular books report.
- [ ] Fine policy management UI: Admin can edit fine policies from the UI.
- [ ] Borrowing velocity flag: If a member issues 3x their monthly average in one week, flag on their profile.

### Phase 3 — Polish (Day 5, if time allows)
*Goal: Make it feel finished*

- [ ] Responsive mobile layout check
- [ ] Empty states for all list views (no books, no transactions, etc.)
- [ ] Success/error toast notifications via HTMX + Alpine
- [ ] Pagination on all list views
- [ ] Keyboard shortcuts for common librarian actions
- [ ] `ARCHITECTURE.md` — write this last, once you've built it

---

## 6. PROJECT FOLDER STRUCTURE

```
libra/
├── app/
│   ├── __init__.py              # App factory: create_app()
│   ├── config.py                # Config classes: DevelopmentConfig, ProductionConfig
│   ├── extensions.py            # db, login_manager, mail, scheduler, migrate
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── book.py              # Book, BookCopy, Category models
│   │   ├── transaction.py       # Transaction, Fine, FinePolicy models
│   │   ├── reservation.py       # Reservation model
│   │   └── audit.py             # AuditLog, ReadingGoal models
│   │
│   ├── services/                # ALL business logic lives here
│   │   ├── __init__.py
│   │   ├── book_service.py      # ISBN fetch, book/copy CRUD
│   │   ├── issue_service.py     # issue_book(), return_book() — the core
│   │   ├── fine_service.py      # calculate_fine(), waive_fine()
│   │   ├── reservation_service.py  # add_to_queue(), notify_next(), expire_reservations()
│   │   ├── analytics_service.py    # co_borrowing(), velocity_check(), report generation
│   │   └── notification_service.py # email sending wrappers
│   │
│   ├── routes/                  # THIN routes: validate → call service → return response
│   │   ├── __init__.py
│   │   ├── auth.py              # /login, /logout
│   │   ├── books.py             # /books, /books/<id>, /books/add
│   │   ├── members.py           # /members, /members/<id>
│   │   ├── transactions.py      # /issue, /return, /transactions
│   │   ├── reservations.py      # /reserve, /reservations
│   │   ├── fines.py             # /fines, /fines/pay, /fines/waive
│   │   ├── admin.py             # /admin/*, /admin/reports
│   │   └── api.py               # /api/* — HTMX partial responses
│   │
│   ├── tasks/
│   │   └── scheduler.py         # overdue_check(), reservation_expiry_check()
│   │
│   ├── templates/
│   │   ├── base.html            # Sidebar layout, nav, flash messages
│   │   ├── partials/            # HTMX partial templates (book list, search results)
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── books/
│   │   │   ├── index.html
│   │   │   ├── detail.html
│   │   │   └── form.html
│   │   ├── members/
│   │   ├── transactions/
│   │   ├── fines/
│   │   ├── reservations/
│   │   └── admin/
│   │       ├── dashboard.html
│   │       └── reports.html
│   │
│   └── static/
│       ├── css/
│       │   └── custom.css       # Minimal overrides on Tailwind
│       └── js/
│           └── app.js           # Minimal JS for Chart.js init
│
├── migrations/                  # Auto-generated by Flask-Migrate
├── tests/
│   ├── test_issue_service.py
│   ├── test_fine_service.py
│   └── test_reservation_service.py
├── .env                         # Never commit this
├── .env.example                 # Commit this
├── requirements.txt
├── run.py
└── ARCHITECTURE.md              # Written last
```

**The single most important rule:** If you find yourself writing business logic inside a `routes/` file — stop. Move it to `services/`. Routes should be 10–15 lines max. Services can be 100+ lines.

---

## 7. STEP-BY-STEP BUILD SEQUENCE

### Step 1: Project Init (2 hours)
```bash
mkdir libra && cd libra
python -m venv venv
source venv/bin/activate

pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login \
    Flask-Mail Flask-WTF APScheduler psycopg2-binary \
    python-dotenv requests qrcode[pil]

pip freeze > requirements.txt
```

Create `.env`:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://localhost/libra
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-app-password
```

Create `run.py`:
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### Step 2: App Factory + Extensions (1 hour)
Build `app/__init__.py` (app factory pattern). Build `app/extensions.py`. This is the foundation everything else plugs into.

### Step 3: Models (2 hours)
Build models in this order: User → Category → Book → BookCopy → FinePolicy → Transaction → Fine → Reservation → AuditLog → ReadingGoal.

Run `flask db init`, `flask db migrate`, `flask db upgrade` after each model file.

### Step 4: Auth (1 hour)
Login form, login route, logout route, `@login_required`, `@role_required` decorator. Seed one admin user via a `flask seed` CLI command.

### Step 5: Base Template (1 hour)
Build `base.html` with Tailwind + Flowbite sidebar. This is where the UI impression starts. Use Flowbite's sidebar component as your base.

### Step 6: Book CRUD + ISBN Fetch (2 hours)
Books index, add book (with live ISBN fetch via HTMX), book detail page, copy management.

### Step 7: Issue Service (2 hours)
This is the core. `issue_book(member_id, book_id, librarian_id)` in `services/issue_service.py`. It must: find an available copy, create a transaction, update `available_copies`, log to audit, return success/failure.

### Step 8: Return + Fine Service (2 hours)
`return_book(transaction_id, librarian_id)`. `calculate_fine(transaction_id)`. These work together. Fine calculation reads from `fine_policies`.

### Step 9: Reservation Service (2 hours)
Queue management, notification trigger on return, expiry logic.

### Step 10: Dashboards + Scheduler (2 hours)
Librarian dashboard. APScheduler two jobs. Member dashboard.

### Step 11: Phase 2 Features (Day 3–4)
QR codes → Co-borrowing → Analytics → Reading goals → Emails → CSV exports.

---

## 8. KEY PATTERNS FOR THE AGENT TO FOLLOW

### Pattern 1: The Service Call Pattern
```python
# routes/transactions.py — CORRECT
@transactions_bp.route('/issue', methods=['POST'])
@login_required
@role_required('librarian')
def issue():
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    
    result = issue_service.issue_book(
        member_id=member_id,
        book_id=book_id,
        librarian_id=current_user.id
    )
    
    if result.success:
        flash('Book issued successfully', 'success')
    else:
        flash(result.error_message, 'error')
    
    return redirect(url_for('transactions.index'))
```

### Pattern 2: HTMX Partial Response
```python
# routes/api.py — for live search
@api_bp.route('/books/search')
def search_books():
    query = request.args.get('q', '')
    books = Book.query.filter(Book.title.ilike(f'%{query}%')).limit(10).all()
    # Return PARTIAL template, not full page
    return render_template('partials/book_list.html', books=books)
```

```html
<!-- In the search input -->
<input
  type="text"
  hx-get="/api/books/search"
  hx-trigger="keyup changed delay:300ms"
  hx-target="#book-results"
  placeholder="Search books..."
/>
<div id="book-results"></div>
```

### Pattern 3: Audit Logging
```python
# In every service function, after a significant action:
AuditLog.log(
    action='BOOK_ISSUED',
    entity_type='transaction',
    entity_id=transaction.id,
    description=f'"{book.title}" issued to {member.name} by {librarian.name}. Due: {due_date}',
    actor_id=librarian_id
)
```

### Pattern 4: Role Decorator
```python
# app/utils.py
from functools import wraps
from flask_login import current_user
from flask import abort

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 9. WHICH AGENT TO USE WHEN

**Antigravity (primary code agent):**
Use for all implementation. Share this document at the start of every session. Instruction: "Read this entire document. Write 50–60 lines at a time. Explain each decision in comments."

**Claude (this session):**
Use for architectural decisions, debugging when stuck, reviewing service logic, writing ARCHITECTURE.md.

**Gemini:**
Use for research — "How does HTMX trigger work with form validation?", "What's the best way to calculate weekday-only days in Python?" — quick reference questions.

**ChatGPT:**
Use for boilerplate — "Write a Tailwind CSS sidebar component", "Give me a Chart.js bar chart template." Quick UI scaffolding.

**Rule:** Never ask two agents the same code question and try to merge their answers. Pick one for each task. Conflicting code will break things.

---

## 10. WHAT TO SAY TO EVALUATORS

For each major decision, here is your one-sentence justification:

**"Why BookCopy table?"**
> "Each physical copy needs an identity so I can track exactly which copy is with which member, and each copy can have independent notes without affecting the book's master record."

**"Why Flask-Login instead of JWT?"**
> "JWT is for stateless APIs consumed by mobile apps or React SPAs. Since we're server-rendering HTML with Jinja2, session cookies via Flask-Login are the correct and simpler choice."

**"Why the service layer pattern?"**
> "Routes should only handle HTTP — parse the request, call a service, return a response. Business logic belongs in services so it's testable without HTTP and reusable across different routes."

**"Why fine_policies as a database table?"**
> "If the library changes its fine rates, an admin updates a row. No code change, no deployment. Configuration belongs in data, not in code."

**"Why PostgreSQL not SQLite?"**
> "SQLite file-locks on concurrent writes. Two librarians issuing books simultaneously would cause one to fail. PostgreSQL handles concurrent transactions correctly."

**"Why HTMX?"**
> "Frappe Framework uses server-driven HTML with targeted DOM updates — the same pattern HTMX implements. Using HTMX prepares the mental model for the Frappe transition in Phase 2."

**"Why APScheduler only for 2 jobs?"**
> "I only need two lightweight daily jobs — overdue checking and reservation expiry. Celery would require a separate broker process and worker process for the same result. APScheduler runs in-process and is sufficient."

---

## 11. THINGS THAT WILL TEMPT YOU — DON'T DO THEM

| Temptation | Why to resist |
|------------|---------------|
| Add AI/LLM features | CEO explicitly said no. Also: calling an API proves nothing about engineering skill. |
| Switch to React for "better UI" | Wrong mental model for Frappe. Flowbite + HTMX is enough. |
| Add barcode scanner integration | Hardware dependency outside scope. |
| Build a mobile app | Wrong phase. |
| Use Docker | Adds complexity on Day 4 when you need to be shipping features. |
| JWT | Wrong tool for this stack. |
| Celery | Wrong tool for 2 lightweight jobs. |
| Add more scheduled jobs | Scope creep. Keep APScheduler for exactly 2 jobs. |
| Build an admin panel with django-admin style auto-generation | You need to understand and explain every screen. Build them yourself. |

---

## 12. SUCCESS CRITERIA

At the end of Day 5, you should be able to:

1. **Demo the full issue/return cycle** with fine calculation in under 3 minutes
2. **Show the reservation queue** with a book that has 0 available copies
3. **Explain why every table exists** and why each column is there
4. **Show the audit log** and explain the lineage of any transaction
5. **Point to the service layer** and explain why business logic lives there
6. **Show a Chart.js analytics dashboard** with real data from your transactions
7. **Deploy it** to Railway/Render so there's a live URL

If you can do all 7 — this project will impress a Frappe senior engineer.

---

*Last updated: Project start*
*Version: 1.0 — share with all agents as context at session start*
