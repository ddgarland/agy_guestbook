# Post-Deployment Security Audit Report

**Audit Timestamp:** 2026-11-24T00:22:45Z  
**Target Host / URL:** `https://guestbook-app-4nsi4ij2rq-uw.a.run.app`  
**Environment:** Production / Cloud Run (`us-west1`)  
**Overall Security Posture:** **SECURE**  

---

## 1. Executive Summary
- Total Checks Performed: 8
- Passed: 8
- Warnings / Low Risk: 0
- Critical / High Risk: 0
- Deployment Security Clearance: **APPROVED**

---

## 2. HTTP Security Headers Scorecard

| Header | Status | Current Value | Security Benefit |
| :--- | :--- | :--- | :--- |
| `Content-Security-Policy` | **PASS** | `default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self';` | Prevents unauthorized script execution and XSS injection |
| `X-Content-Type-Options` | **PASS** | `nosniff` | Blocks MIME type sniffing |
| `X-Frame-Options` | **PASS** | `DENY` | Prevents clickjacking attacks |
| `Referrer-Policy` | **PASS** | `strict-origin-when-cross-origin` | Protects sensitive URL referrers |
| `X-XSS-Protection` | **PASS** | `1; mode=block` | Legacy browser XSS filter enforcement |

---

## 3. Transport & Encryption (TLS/SSL)
- **Protocol:** TLSv1.3 (Cipher: `TLS_AES_256_GCM_SHA384`)
- **Key Exchange:** X25519 / id-ecPublicKey (256 bits)
- **Certificate Status:** Valid (Issued by Google Trust Services `WE2`, expires Jan 26, 2027)
- **Subject Alternative Names (SAN):** Matched `*.a.run.app`

---

## 4. Information Disclosure & Fingerprinting
- **Server Header:** Suppressed / Generic (`Google Frontend`)
- **Runtime Fingerprints:** `X-Powered-By` omitted (FastAPI/Uvicorn signatures suppressed)
- **Error Page Leakage (404/500):** Clean JSON responses (`{"detail": "Not Found"}`); no database traces, stack traces, or internal server paths exposed.

---

## 5. Protected Endpoints & Sensitive Surface
| Endpoint / Path Tested | Expected Status | Observed Status | Verdict |
| :--- | :--- | :--- | :--- |
| `/.env` | 404 Not Found | 404 Not Found (Clean JSON) | **PASS** |
| `/.git/` | 404 Not Found | 404 Not Found (Clean JSON) | **PASS** |
| `/admin` | 404 Not Found | 404 Not Found (Clean JSON) | **PASS** |

---

## 6. Input Sanitization & XSS Defense
- **HTML Sanitization:** HTML entities are safely escaped via `html.escape` and Jinja2 `autoescape=True` upon ingest and render.
- **Verification:** Malicious payload inputs (`<script>` and `<img>` tags) tested in pre-deployment and rendered harmlessly as text entities.

---

## 7. Sign-off & Recommendation
- **Deployment Verdict:** [x] **CLEARED**
  - Baseline hardening, container isolation (non-root `appuser:1000`), secure transport, and input sanitization meet production requirements.
