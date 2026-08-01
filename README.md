# BluePark — AI Restaurant Operations Platform

BluePark started as a student restaurant-ordering project (`Backend/`, `Frontend/`) and was rebuilt in four phases into a full operations platform: role-based ordering, a real-time kitchen queue, inventory and staff management, an analytics dashboard, and an AI operations copilot — all on a single Django codebase.

The runnable application lives at **`Backend/bluepark/`**. All commands below assume you've `cd`'d into that directory.

## Architecture

**Stack**: Django 6 + Django REST Framework (API) + Django Channels/Daphne (WebSockets) + Tailwind CSS v4 + Alpine.js + Chart.js. SQLite in development, Postgres + Redis in production — swapped via environment variables, never code changes.

```
                             BluePark Ops Architecture

                                    🌐 Browser
                                         │
                     ┌───────────────────┴───────────────────┐
                     │                                       │
          Server-Rendered Pages                     REST APIs (DRF)
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         │
                              Django Service Layer
                                         │
 ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
 │              │              │              │              │              │
Accounts      Orders        Inventory      Kitchen      Analytics    Notifications
 │              │              │              │              │              │
 └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                         │
                              PostgreSQL / SQLite
                                         │
                               Django Channels
                                         │
                                Redis (Production)
                                         │
                               WebSocket Clients

                          🤖 AI Operations Copilot
                                         │
                                Context Builder
                                         │
                               AI Service Layer
                                         │
                              Google Gemini API
```

**App layout** — one Django app per domain, each following the same internal shape: `models.py` → `services.py` (business logic, the only thing views/API call) → `api.py` + `serializers.py` (DRF) → `views.py` (server-rendered pages) → `signals.py` where one app needs to react to another without a direct dependency (e.g. `inventory` deducting stock when `orders` fires its `order_placed` signal, without `orders` needing to know `inventory` exists):

| App | Owns |
|---|---|
| `core` | Shared base model, role-based DRF permission classes, the Phase 2 "Overview" snapshot dashboard |
| `accounts` | Auth, roles (customer/waiter/chef/manager/admin via `Profile.role`) |
| `menu` | Categories, menu items |
| `orders` | Cart, Order, OrderItem, OrderStatusHistory — the pipeline everything else sits on |
| `kitchen` | Kitchen queue (Kanban board) + real-time WebSocket updates |
| `inventory` | Ingredients, suppliers, recipe BOM, stock movements, auto-deduction on order |
| `staff` | Employees, shifts, attendance/clock-in |
| `notifications` | In-app notifications, signal-driven (new order, low stock) |
| `analytics` | Filterable (today/7d/30d/custom) revenue/orders/menu/inventory/staff/kitchen analytics |
| `ai_copilot` | AI Operations Copilot — see [AI setup](#ai-copilot-setup) below |

**Roles**: Customer, Waiter, Chef, Manager, Admin (`accounts.models.Profile.role`) — separate from Django's own `is_staff`/`is_superuser`, which gate the Django Admin (`/admin/`) instead. See `core/permissions.py` for the DRF permission classes every API view uses.

**Design system**: `templates/base.html` (shared head, dark-mode boot script) → `base_public.html` (customer-facing nav/footer) or `base_dashboard.html` (staff sidebar shell) → per-page templates. Tailwind tokens live in `tailwind_src/input.css` (kept outside `static/` so its `@import "tailwindcss"` build directive never gets swept into `collectstatic`); compiled output (`static/css/tailwind.css`) is committed so a fresh clone works without Node.

## Installation (local development)

Requires Python 3.11+. No Postgres/Redis/Docker needed for local dev.

```bash
cd Backend/bluepark
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # for /admin/
python manage.py runserver
```

That's it — `bluepark.settings.dev` (the default) has safe fallbacks for `SECRET_KEY` and uses SQLite + Channels' in-memory layer, so no `.env` file is required to get started.

To work on the Tailwind CSS (optional, only if you're changing styles):

```bash
npm install
npm run watch:css   # rebuilds static/css/tailwind.css on change
```

### Creating role accounts

Customers self-register at `/accounts/register`. Staff accounts (waiter/chef/manager/admin) are created by a Manager/Admin — either via the Django Admin (`/admin/`, add a user, set their role in the inline Profile section) or `POST /api/v1/accounts/staff/`.

## Running tests

```bash
python manage.py test
```

30 tests covering the cart→order pipeline, analytics aggregation (including date-range edge cases), role-permission gating, and the AI copilot (provider mocked — no live API key needed to run the suite).

## Deployment (Docker)

```bash
cd Backend/bluepark
cp .env.example .env   # fill in SECRET_KEY, ALLOWED_HOSTS, etc.
docker compose up --build
```

This brings up three containers: `web` (Django via Daphne, so WebSockets work the same as local dev), `db` (Postgres 16), `redis` (for the production channel layer). Migrations run automatically on `web` startup.

**Known limitation**: media (uploaded images) and static files are baked into the `web` image at build time, not volume-mounted — a genuinely persistent setup needs object storage (S3 or similar) wired into Django's file storage, which isn't set up here. See the Dockerfile/docker-compose.yml comments for why (an empty named volume would otherwise shadow the seed data and `collectstatic` output on first run).

**Note**: no Docker daemon was available in the environment this was built in — the Dockerfile and docker-compose.yml were written and reviewed carefully but not build-tested. Please run a real `docker compose up --build` before depending on it.

## AI Copilot setup

The AI Operations Copilot (`/ai-copilot/`, Manager/Admin only) answers natural-language questions about revenue, orders, menu performance, inventory, staff, and customer feedback, using Google Gemini.

1. Get a free API key at **https://aistudio.google.com/apikey**.
2. Add it to your `.env` (or export it directly for local dev):
   ```
   GEMINI_API_KEY=your-key-here
   ```
3. That's it — `AI_PROVIDER=gemini` and `GEMINI_MODEL=gemini-2.0-flash` are the defaults (see `.env.example`).

If the key is missing or invalid, the copilot returns a clear error message (HTTP 503, shown in the chat UI) instead of crashing — the rest of the application is entirely unaffected either way.

**How it works**: `ai_copilot/context.py` gathers real data by calling `analytics.services`' existing aggregation functions directly (no duplicated logic) plus a small customer-feedback aggregator, `ai_copilot/services.py` builds one prompt from that data and the user's question, and `ai_copilot/providers.py` sends it to whichever provider `AI_PROVIDER` selects. Views and API code never call Gemini (or any provider) directly — they only ever call `ai_copilot.services.answer_question()`. Adding a second provider (OpenAI, Claude, ...) means adding one class to `providers.py`; nothing else in the codebase changes.

## Known limitations

- **No browser/visual verification.** Every phase of this project was verified at the HTTP/JSON/template/query-count level (curl, Django's test client, `CaptureQueriesContext`) rather than in an actual browser — no browser automation tool was available in the environment this was built in. Please do a visual pass, especially on mobile widths, before considering the UI final.
- **No live Gemini call verified.** No API key was available in the build environment; the AI copilot's provider layer, context assembly, and error handling are covered by mocked tests, not a real model response.
- **Docker not build-tested**, per above.
- **Real-time updates use Django Channels' in-memory layer in development** — fine for one process, but production must use `channels_redis` (already wired in `settings/prod.py`, via `REDIS_URL`).
- **`Survey_feedback` (customer feedback) has no timestamp field** — a limitation from the project's original design, intentionally left as-is rather than changed mid-project. The AI copilot's feedback data is therefore an all-time snapshot, not scoped to the selected date range, same as a couple of other "current state" metrics (low-stock count, staff currently on shift).
