# AGENTS.md

> **Notice for Future AI Agents & Pair Programmers**: This document provides architectural context, implementation patterns, deployment parameters, testing runbooks, and conventions for the **Guestbook Application**. Consult this file first before making changes or extending features.

---

## 1. System Overview & Core Capabilities

The **Guestbook Application** is a production-tested, containerized web service deployed to Google Cloud Run. It allows web visitors to browse existing messages and sign the guestbook with their name, email, and message.

- **Production URL**: `https://guestbook-app-4nsi4ij2rq-uw.a.run.app`
- **Alternative URL**: `https://guestbook-app-483486086533.us-west1.run.app`
- **GCP Project**: `hardy-messenger-510318-u4`
- **Cloud Run Region**: `us-west1`
- **Service Name**: `guestbook-app`
- **Ingress Policy**: Public unauthenticated (`--allow-unauthenticated`)

---

## 2. Codebase Architecture & File Map

```
/home/dgarland/antigravity/
├── Dockerfile                  # Production container definition (Python 3.12-slim, non-root user)
├── .dockerignore               # Ignores .venv, tests, git, cache, and db files
├── requirements.txt            # FastAPI, Uvicorn, Jinja2, Pydantic, Pytest, HTTPX
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application, route handlers, security headers middleware
│   ├── models.py               # SQLite connection, WAL mode, Pydantic schema, CRUD operations
│   ├── templates/
│   │   └── index.html          # Jinja2 template with responsive UI & form feedback
│   └── static/
│       └── style.css           # Clean modern styles (desktop & mobile responsive)
├── tests/
│   ├── __init__.py
│   └── test_app.py             # Pytest async test suite (unit, integration, XSS sanitization)
├── SPECIFICATION.md            # Technical specification & architectural trade-offs
├── PLAN.md                     # Phased implementation & verification plan
├── PRE-TEST.md                 # Pre-deployment verification audit (all 6 suites passed)
├── POST-TEST.md                # Post-deployment live smoke & probe verification (Healthy)
├── POST-SECURITY.md            # Post-deployment security audit & header scorecard (Secure)
├── LOG.md                      # Chronological execution log of all skills, tools & steps
└── AGENTS.md                   # This instruction guide for future agents
```

---

## 3. Technology Stack & Key Patterns

### Backend
- **FastAPI** (`app/main.py`): Handles async HTTP routing, dependency injection, and static/template mounting.
- **Uvicorn**: Production ASGI web server running with `CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`.
- **Pydantic V2** (`app/models.py`): Validates incoming form input (`name`: 1-50 chars, `email`: validated email format, `message`: 1-500 chars).
- **SQLite3** (`app/models.py`): Local database configured with `PRAGMA journal_mode=WAL;` for concurrency. Defaults to `guestbook.db` locally or `/app/data/guestbook.db` in Docker.

### Security Defenses
- **Input Sanitization**: All incoming text is sanitized with `html.escape` and template auto-escaping is enforced to prevent XSS.
- **HTTP Security Middleware**: Injected on all requests via `add_security_headers` middleware:
  - `Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self';`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `X-XSS-Protection: 1; mode=block`
- **Least Privilege Container**: Runs as unprivileged user `appuser:1000` inside the container.

---

## 4. API & Route Reference

| Method | Path | Description | Response Type |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Guestbook homepage with recent signatures form | `text/html` |
| `POST` | `/entries` | Form submit; validates and saves entry, redirects to `/?success=true` | `303 See Other` (or `422` on error) |
| `GET` | `/api/v1/entries` | Headless JSON endpoint returning up to 50 latest entries | `application/json` |
| `GET` | `/health` | Container health probe | `application/json` (`{"status": "healthy"}`) |
| `GET` | `/api/healthz` | Container health probe alias | `application/json` (`{"status": "healthy"}`) |
| `GET` | `/healthz` | Legacy container health check | `application/json` |

---

## 5. Development & Testing Runbook

### Local Environment Setup
```bash
# Activate existing virtualenv
source .venv/bin/activate

# Or recreate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
All tests are implemented using `pytest` and `httpx.AsyncClient` with isolated temporary SQLite databases:
```bash
.venv/bin/pytest -v tests/
```

### Running Locally
```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

---

## 6. Cloud Run Deployment Runbook

Deploying changes or a new revision to Cloud Run:

```bash
gcloud run deploy guestbook-app \
    --source . \
    --region us-west1 \
    --project hardy-messenger-510318-u4 \
    --allow-unauthenticated \
    --quiet
```

### Post-Deployment Verification Steps
1. Verify health check:
   ```bash
   curl -s -i "https://guestbook-app-4nsi4ij2rq-uw.a.run.app/health"
   ```
2. Verify public entries:
   ```bash
   curl -s "https://guestbook-app-4nsi4ij2rq-uw.a.run.app/api/v1/entries"
   ```
3. Update `POST-TEST.md` and `POST-SECURITY.md` if routes or security policies change.

---

## 7. Guidelines for Future Agent Sessions
- **Preserve Documentation**: Always keep `SPECIFICATION.md`, `PLAN.md`, and test verification documents synchronized when adding features.
- **Do Not Break Non-Root Container Execution**: Keep `USER appuser` in `Dockerfile` and ensure file permissions in `/app/data` permit writing SQLite databases.
- **Input Validation Rule**: All new models must be validated using Pydantic and sanitized for HTML entities before rendering or persistence.
