# CRUD App — FastAPI + Alpine.js Scaffold

A production-ready scaffold for a full-stack CRUD application using **FastAPI** (Python async), **SQLAlchemy 2**, **Alpine.js**, and a Tailwind-inspired vanilla CSS UI.

---

## Tech Stack

| Layer       | Technology                                     |
|-------------|------------------------------------------------|
| API         | FastAPI, Pydantic v2                           |
| ORM         | SQLAlchemy 2 (async)                           |
| Migrations  | Alembic                                        |
| DB          | SQLite (dev & prod) · MySQL (production)       |
| UI          | Alpine.js, Jinja2, vanilla CSS (Tailwind-style)|
| Tests       | pytest, pytest-asyncio, pytest-cov, httpx      |

---

## Project Structure

```
crud_app/
├── app/
│   ├── config.py          # Pydantic-settings configuration
│   ├── database.py        # Async engine, session factory, Base
│   ├── main.py            # FastAPI application factory + lifespan
│   ├── models/
│   │   └── item.py        # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── item.py        # Pydantic request/response schemas
│   ├── services/
│   │   └── item_service.py # Business logic / repository layer
│   ├── routes/
│   │   ├── items.py       # REST API router (/api/items)
│   │   └── ui.py          # HTML UI router (/)
│   ├── templates/
│   │   └── index.html     # Alpine.js single-page UI
│   └── static/            # Static assets (CSS, JS)
├── tests/
│   ├── conftest.py        # In-memory SQLite fixtures, client, factories
│   ├── unit/
│   │   ├── test_item_service.py
│   │   └── test_schemas.py
│   └── integration/
│       └── test_api_items.py
├── migrations/
│   └── env.py             # Alembic async configuration
├── scripts/
│   └── seed.py            # Sample data seeder
├── alembic.ini
├── pytest.ini
├── .coveragerc
├── .env.example
├── Makefile
├── requirements.txt
└── main.py                # Entry point
```

---

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# or
make install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — the default SQLite URL works out of the box
```

### 3. Run the dev server

```bash
make dev
# or
uvicorn app.main:app --reload
```

Open http://localhost:8000

### 4. Seed sample data (optional)

```bash
make seed
```

---

## Database Configuration

Switch databases by changing `DATABASE_URL` in `.env`:

```bash
# SQLite (default – built in, zero config)
DATABASE_URL=sqlite+aiosqlite:///./crud_app.db

# MySQL
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/crud_db
```

### Migrations (Alembic)

```bash
# Apply existing migrations
make migrate

# Generate a new migration after model changes
make migration          # prompts for a message
```

---

## Testing & Coverage

```bash
# Run all tests with coverage
make test-cov

# Run tests quickly (stop on first failure)
make test

# Open HTML coverage report
open htmlcov/index.html
```

Tests use an **in-memory SQLite** database so they run fast and require no external services.

Coverage is enforced at **≥ 80%** (configured in `pytest.ini`).

---

## REST API

| Method | Path              | Description          |
|--------|-------------------|----------------------|
| GET    | /api/items        | List items (paginated, filterable) |
| POST   | /api/items        | Create item          |
| GET    | /api/items/{id}   | Get single item      |
| PATCH  | /api/items/{id}   | Partial update       |
| DELETE | /api/items/{id}   | Delete item          |

**Query params for `GET /api/items`:** `page`, `page_size`, `search`, `status`

Interactive docs: http://localhost:8000/docs

---

## Adding a New Resource

1. Add a model in `app/models/`
2. Add schemas in `app/schemas/`
3. Add a service in `app/services/`
4. Add routes in `app/routes/` and register them in `app/main.py`
5. Generate a migration: `make migration`
6. Add unit + integration tests in `tests/`

---

## Deploying to Render

This project ships with a `render.yaml` [Blueprint](https://render.com/docs/blueprint-spec) that provisions:
- A **web service** (Python, free tier)

### Steps

1. Push the project to a GitHub / GitLab repository.
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint**.
3. Connect your repo — Render will detect `render.yaml` automatically.
4. Click **Apply**.

> **Note on Persistent Storage:** By default, SQLite files are wiped on every deploy on Render. To persist your data, follow Render's [Persistent Disks](https://render.com/docs/disks) guide to mount a volume at `/data` and update your `DATABASE_URL` to `sqlite+aiosqlite:////data/crud_app.db`.

### After first deploy

Copy your `.onrender.com` URL and update `ALLOWED_ORIGINS` in the Render dashboard (or in `render.yaml` before deploying):

```yaml
- key: ALLOWED_ORIGINS
  value: '["https://your-app-name.onrender.com"]'
```
