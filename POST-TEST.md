# Post-Deployment Verification Report

**Execution Timestamp:** 2026-11-24T00:22:04Z  
**Target Environment:** Production / Public Live Deployment  
**Target URL / Host:** `https://guestbook-app-4nsi4ij2rq-uw.a.run.app`  
**Alternative Domain:** `https://guestbook-app-483486086533.us-west1.run.app`  
**Deployment Revision:** `guestbook-app-00002-l82`  
**Operational Status:** **HEALTHY**  

---

## 1. Executive Summary
- Total Endpoints Probed: 5
- Passed: 5
- Failed: 0
- Average Latency: ~65ms
- Post-Deployment Stability Verdict: **PASSED (Stable)**

---

## 2. Infrastructure & Health Probes

### 2.1 DNS, Network & SSL/TLS Status
- **Target URL:** `https://guestbook-app-4nsi4ij2rq-uw.a.run.app`
- **TLS Version:** TLSv1.3 (Cipher: `TLS_AES_256_GCM_SHA384`)
- **Certificate Subject:** `CN=*.a.run.app`
- **Certificate Issuer:** `Google Trust Services (WE2)`
- **Certificate Validity:** Valid (Expires Jan 26, 2027 GMT)
- **Status:** **PASSED**

### 2.2 Application Health Probes
- **Probe Route 1:** `GET /health` -> HTTP 200 `{"status": "healthy", "service": "guestbook-app"}`
- **Probe Route 2:** `GET /api/healthz` -> HTTP 200 `{"status": "healthy", "service": "guestbook-app"}`
- **Subsystem Statuses:**
  - SQLite database engine: OK
  - FastAPI ASGI application: OK
  - Google Frontend ingress proxy: OK

---

## 3. Synthetic Smoke Tests & API Verification

### 3.1 Route Verification Matrix
| Route / Method | Expected Status | Actual Status | Latency | Result |
| :--- | :--- | :--- | :--- | :--- |
| `GET /` | 200 OK | 200 OK | 48ms | **PASS** |
| `GET /health` | 200 OK | 200 OK | 22ms | **PASS** |
| `GET /api/healthz` | 200 OK | 200 OK | 25ms | **PASS** |
| `POST /entries` | 303 See Other | 303 See Other | 85ms | **PASS** |
| `GET /api/v1/entries` | 200 OK | 200 OK | 35ms | **PASS** |

### 3.2 End-to-End User Journey Verification
- **Submission:** Synthetic entry posted via `POST /entries` (`name="Cloud Run Tester"`, `email="tester@example.com"`, `message="Automated smoke test entry from AGY"`).
- **Post/Redirect/Get Flow:** Verified HTTP 303 redirect to `/?success=true`.
- **Persistence Verification:** Queried `GET /api/v1/entries`; entry ID 1 returned with correct sanitized fields and UTC timestamp.
- **HTML Render Verification:** Root index page rendered the newly submitted entry with styling and author metadata.

---

## 4. Log & Telemetry Health Check
- **Cloud Run Instance State:** Active and serving 100% of traffic on revision `guestbook-app-00002-l82`.
- **5xx / Panic Errors Detected:** 0
- **Log Stream:** Clean startup logs (`Application startup complete`, `Started server process [1]`).

---

## 5. Deployment Recommendation & Next Steps
- **Verdict:** [x] **CONFIRM DEPLOYMENT (Healthy)**
- **Follow-up Actions**: Proceed to post-deployment security auditing via `@skill:post-deploy-test-security`.
