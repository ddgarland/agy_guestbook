# Implementation Plan: Guestbook Application on Cloud Run

**Based on:** [SPECIFICATION.md](SPECIFICATION.md)  
**Status:** Ready for Execution via `@skill:specification-to-plan`  
**Target Service:** `guestbook-app` in `us-west1` (`hardy-messenger-510318-u4`)  

---

## Architecture & Work Breakdown Overview

This plan details the implementation, containerization, testing, and deployment of the `guestbook-app` service on Cloud Run.

### Target Project File Tree
```
├── Dockerfile                  # Container definition for Cloud Run
├── requirements.txt            # Python dependencies (FastAPI, uvicorn, jinja2, pydantic, etc.)
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application, routing, and lifecycle
│   ├── models.py               # SQLite database setup and Pydantic schemas
│   ├── templates/
│   │   └── index.html          # Responsive guestbook UI
│   └── static/
│       └── style.css           # Styling
├── tests/
│   ├── __init__.py
│   └── test_app.py             # Unit and integration test suite
├── SPECIFICATION.md
├── PLAN.md
├── PRE-TEST.md
├── POST-TEST.md
├── POST-SECURITY.md
└── LOG.md
```

---

## Phase 1: Environment, Dependencies & Scaffolding
- [ ] Task 1.1: Create project directories (`app/`, `app/templates/`, `app/static/`, `tests/`).
- [ ] Task 1.2: Define `requirements.txt` with `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`, `pydantic`, `pytest`, and `httpx`.
- [ ] Task 1.3: Set up virtual environment and install dependencies.
- **Verification:**
  - [ ] Virtualenv imports `fastapi` and `pytest` without errors.

---

## Phase 2: Data Models & Persistence Layer
- [ ] Task 2.1: Implement `app/models.py` with SQLite table schema (`entries`: `id`, `name`, `email`, `message`, `created_at`).
- [ ] Task 2.2: Add repository helper functions: `init_db()`, `get_entries()`, `add_entry(name, email, message)`.
- [ ] Task 2.3: Implement Pydantic validation models for payload validation.
- **Verification:**
  - [ ] Test helper functions against a temporary SQLite database.

---

## Phase 3: Core Business Logic, API & Web UI
- [ ] Task 3.1: Build `app/templates/index.html` with responsive form and entry feed.
- [ ] Task 3.2: Build `app/static/style.css` with clean modern layout.
- [ ] Task 3.3: Implement `app/main.py` with:
  - `GET /`: Renders guestbook page with entries.
  - `POST /entries`: Accepts form submissions, sanitizes inputs, and redirects.
  - `GET /api/v1/entries`: JSON API for headless queries.
  - `GET /healthz`: Health check endpoint returning `{"status": "healthy"}`.
  - Security headers middleware (nosniff, X-Frame-Options).
- **Verification:**
  - [ ] Start server locally and verify HTTP 200 on `/healthz` and `/`.

---

## Phase 4: Containerization Setup
- [ ] Task 4.1: Write `Dockerfile` optimized for Cloud Run:
  - Multi-stage or lean `python:3.11-slim` image.
  - Non-root user execution for security.
  - Dynamically binds to `0.0.0.0:$PORT` (defaults to 8080).
- [ ] Task 4.2: Create `.dockerignore` to prevent uploading tests and virtual environments.
- **Verification:**
  - [ ] Validate Dockerfile syntax.

---

## Phase 5: Pre-Deployment Testing (`pre-deploy-test-application`)
- [ ] Task 5.1: Implement unit and integration tests in `tests/test_app.py`:
  - Health check verification (`GET /healthz`).
  - Form submission test with valid data (`POST /entries`).
  - Validation rejection for invalid emails or missing fields (HTTP 422).
  - XSS payload sanitization verification.
  - JSON API endpoint verification (`GET /api/v1/entries`).
- [ ] Task 5.2: Execute `pytest` and linting suite.
- [ ] Task 5.3: Generate and emit `PRE-TEST.md` with pass/fail verdict.
- **Verification:**
  - [ ] 100% test pass rate recorded in `PRE-TEST.md`.

---

## Phase 6: Cloud Run Deployment
- [ ] Task 6.1: Build and deploy service using `gcloud run deploy guestbook-app --source . --region us-west1 --allow-unauthenticated`.
- [ ] Task 6.2: Retrieve deployed live service URL.
- **Verification:**
  - [ ] `gcloud run services describe guestbook-app` reports `Ready` status.

---

## Phase 7: Post-Deployment Functional & Security Verification
- [ ] Task 7.1: Run `@skill:post-deploy-test-application` against live service URL:
  - Probe `/healthz`, `/`, `/api/v1/entries`.
  - Perform live submission smoke test.
  - Emit results to `POST-TEST.md`.
- [ ] Task 7.2: Run `@skill:post-deploy-test-security` against live service URL:
  - Inspect HTTPS and TLS certificate.
  - Verify HTTP security headers (nosniff, X-Frame-Options, CSP, HSTS).
  - Probe sensitive paths (`/.env`, `/.git`).
  - Emit results to `POST-SECURITY.md`.

---

## Phase 8: Execution Logging
- [ ] Task 8.1: Finalize `LOG.md` recording all skill invocations, commands, and deployment links.
