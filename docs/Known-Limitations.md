# CortexOne — Known Limitations

> **Audience:** Engineers, CTOs, Product Managers, Security Architects  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Roadmap.md](Roadmap.md) · [Architecture.md](Architecture.md) · [Developer-Guide.md](Developer-Guide.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from repository analysis |

---

## How to Read This Document

Every limitation listed here is supported by evidence from the repository. No limitations are inferred or invented. Where code is cited, the specific file or configuration key is provided.

**Severity classifications:**
- 🔴 **Critical** — Blocks production readiness or creates material security risk
- 🟠 **High** — Significant business or operational impact
- 🟡 **Medium** — Meaningful limitation, workaround exists
- 🟢 **Low** — Minor gap, minimal impact

---

## 1. Security Limitations

### 🔴 CAPTCHA Disabled in Production

**Evidence:** `.env` line: `TURNSTILE_SECRET=DISABLED`  
**Comment in .env:** `INTERNAL PILOT: CAPTCHA disabled intentionally — no public registration.`  
**Impact:** The registration endpoint (`POST /api/v1/register`) is unprotected against bot registration and credential stuffing. An attacker can create unlimited trial accounts, consume resources, and potentially abuse the trial period at scale.  
**Pre-condition to fix:** Replace `DISABLED` with a real Cloudflare Turnstile secret key and matching `TURNSTILE_SITE_KEY`.  
**Urgency:** Must be resolved before any public traffic is driven to the platform.

---

### 🟠 MFA Not Enforced

**Evidence:** `users.mfa_secret` and `users.mfa_enabled` columns exist in schema. No MFA verification step visible in `api/v1/auth.php` login flow. No MFA enrollment UI module confirmed in dashboard.  
**Impact:** Admin accounts with compromised passwords have no second factor protection. Enterprise and financial services buyers require MFA as a contractual or regulatory requirement.  
**Workaround:** Strong password policy and account lockout (10 attempts) provide partial protection.

---

### 🟡 Agent Offline Cache Unencrypted

**Evidence:** Agent uses `Microsoft.Data.Sqlite` (standard unencrypted SQLite). Offline cache stored at `C:\ProgramData\ProductivityAgent\Cache\offline.db`.  
**Impact:** A local administrator on the endpoint can read cached telemetry payloads (heartbeats, app usage, screenshots in base64) from the SQLite file before they sync. This is a local privilege issue, not a remote one.  
**Mitigation:** All data is encrypted in transit (HTTPS). The attack requires local admin access.  
**Fix:** Replace with SQLCipher-encrypted SQLite or use DPAPI to encrypt the database file.

---

### 🟡 Screenshots Stored on Application Server

**Evidence:** Screenshots saved to `/storage/screenshots/{org_id}/{device_id}/` on the same server as the PHP application.  
**Impact:** If the web server is compromised, all screenshot images are accessible. No access control layer beyond filesystem permissions. No CDN or separate storage isolation.  
**Workaround:** Filesystem permissions limit access to the Apache user.  
**Fix:** Move to S3/Azure Blob with pre-signed URLs. Implement content delivery via signed URL rather than `readfile()`.

---

### 🟡 JWT Keys Stored as Local PEM Files

**Evidence:** `JWT_PRIVATE_KEY=C:/wamp64/www/ProductivitySuite/config/keys/jwt_private.pem` in `.env`.  
**Impact:** PEM files on disk are accessible to anyone with filesystem access to the server. No key management service (HSM, AWS KMS, Azure Key Vault) in use.  
**Mitigation:** Files are outside the document root (config/keys/). Apache does not serve them directly.  
**Fix:** Consider AWS KMS or Azure Key Vault for key storage in production.

---

### 🟡 Webhook Delivery No Retry

**Evidence:** `webhook_logs` table stores `response_code` and `error_message` but no retry queue or re-delivery mechanism found in repository. Webhook delivery is fire-and-forget.  
**Impact:** Failed webhook deliveries (4xx/5xx from target) are lost permanently. Events like `leave_approved` or `alert_triggered` will not be re-sent.  
**Workaround:** Admins can query `webhook_logs` to identify failed deliveries.

---

## 2. Infrastructure Limitations

### 🔴 Single-Server Deployment (WAMP on Windows)

**Evidence:** `APP_URL=https://app.aptus.global`, WAMP stack, co-located MySQL on same machine.  
**Comment in .env:** No HA configuration. Single server.  
**Impact:**
- Zero redundancy — server failure = complete platform downtime
- Database on same host — cannot scale web and DB independently
- WAMP/Windows not production-grade (no process manager, no rolling restart, no health checks)
- Current setup cannot serve more than ~100–200 concurrent devices without performance degradation

**Fix:** Migrate to Windows Server 2022 with IIS or nginx, or Ubuntu 22.04 + nginx + PHP-FPM. Separate MySQL to dedicated instance or RDS. Add load balancer.

---

### 🟠 No Automated Backups Confirmed

**Evidence:** No backup scripts, mysqldump cron, or cloud backup configuration found in repository.  
**Impact:** Server failure would result in complete data loss — 46 tables of customer telemetry, audit logs, configurations.  
**Fix:** Daily mysqldump + offsite upload (S3 glacier, Azure Backup). Application file backup for screenshots/recordings.

---

### 🟠 Local File Storage — No Quota or Cleanup

**Evidence:** `/storage/screenshots/`, `/storage/recordings/`, `/storage/webcam/` — no quota enforcement code found. No cleanup/expiry job confirmed.  
**Impact:** Screenshot and recording storage will grow indefinitely. A single org with recordings enabled at 5-second intervals generates thousands of JPEG files per device per day. Disk full = data loss and service interruption.  
**Workaround:** Session recording and webcam are disabled by default.  
**Fix:** Implement per-org storage quotas. Add retention policy (configurable, default 90 days). Move to object storage.

---

### 🟡 Heartbeat Partitions Manual — Expire December 2026

**Evidence:** Schema.sql shows `heartbeats` RANGE partitions defined through `p2026_12` with `p_future` MAXVALUE catch-all.  
**Impact:** After December 2026, all new heartbeats route to the `p_future` catch-all partition. Without proper partitioning, queries against this catch-all will be unindexed table scans. Performance will degrade significantly for large fleets.  
**Fix:** Add stored procedure or cron job to auto-add monthly partitions. Script should run in November/December each year.

---

### 🟡 PHP Session Files on Local Filesystem

**Evidence:** `ini_set('session.save_path', dirname(__DIR__) . '/sessions')` in `dashboard/index.php`.  
**Impact:** Cannot run more than one PHP web server without shared session storage. Prevents horizontal scaling. Sessions survive server restarts but are lost on session directory deletion.  
**Fix:** Move to Redis session handler (`session.save_handler=redis`) for multi-server compatibility.

---

### 🟡 Scheduled Reports Depend on External Cron Caller

**Evidence:** `CRON_SECRET` in `.env`. Reports triggered by external HTTP call to `/api/v1/reports/run-scheduled` with `X-Cron-Secret` header.  
**Impact:** No built-in scheduling engine. If the external cron caller fails, scheduled reports are not delivered. No alerting on missed schedules.  
**Fix:** Implement background job queue (Redis + queue worker) with built-in retry.

---

## 3. Platform Limitations

### 🔴 Windows-Only Agent

**Evidence:** Agent `TargetFramework=net8.0-windows10.0.19041.0`. WinRT API usage (`Windows.Media.Capture`, `Windows.Devices.Geolocation`). `win-x64` publish target.  
**Impact:** ~40% of knowledge workers use Macs. Linux-based engineering teams are excluded entirely. Any organisation with mixed Windows/Mac fleet cannot monitor all devices.  
**Workaround:** None. Windows-only by design due to WinRT dependency for Phase 3 features.  
**Fix:** Build Go-based agent for Mac + Linux (separate binary, same API surface). Note: Phase 3 WinRT features would need platform-specific alternatives.

---

### 🟠 Agent Minimum OS: Windows 10 Build 19041

**Evidence:** `net8.0-windows10.0.19041.0` TFM. Required for WinRT MediaCapture and Geolocator API projections.  
**Impact:** Devices running Windows 10 versions earlier than 2004 (Build 19041, released May 2020) cannot run the agent. This affects organisations with unpatched or legacy Windows 10 devices.  
**Note:** Windows 7, 8, 8.1, Server 2012/2016 (without update) are all unsupported.

---

### 🟡 Agent Runs as LocalSystem — No Principle of Least Privilege

**Evidence:** `sc.exe config obj= LocalSystem` in install scripts.  
**Impact:** Agent runs with maximum system privileges. If the agent binary were compromised, it would have full system access. Standard security best practice is least-privilege service accounts.  
**Reason:** LocalSystem required for WMI queries, WTS session access, and service management. Specific privileges needed: `SeDebugPrivilege`, `SeTcbPrivilege` (for WTSQueryUserToken).  
**Mitigation:** Binary integrity verified by SHA-256 on each update. Defender exclusions applied only to specific paths.

---

### 🟡 URL History Read from Browser Files (Read-Only)

**Evidence:** `UrlHistoryWorker` reads browser SQLite history files directly. Chrome history at `%LOCALAPPDATA%\Google\Chrome\...`.  
**Impact:** 
- Does not work in incognito/private mode
- Browser may lock the history file; agent copies to temp — may occasionally fail
- HTTPS sites show domain but not full path in URL (only if in page title)
- Browser history is per-user profile — does not capture system-level DNS queries

---

### 🟡 Screenshot Capture: No Multi-Monitor Support Confirmed

**Evidence:** `BitBlt(GetDC(HWND_DESKTOP), ...)` captures the primary display. Multi-monitor stitching not confirmed from available code analysis.  
**Impact:** On multi-monitor setups, only the primary screen may be captured. Secondary monitors (which employees may use for non-work activity) may not appear.

---

## 4. Feature Incompleteness

### 🟠 Employee Self-Service Portal Incomplete

**Evidence:** `api/v1/portal.php` exists. Task #7 in repository: `in_progress`.  
**Impact:** Employees cannot view their own productivity scores. Managers must share data manually. Reduces employee adoption and transparency.

---

### 🟠 Billing UI Incomplete

**Evidence:** Stripe webhook handler and schema implemented. `billing.php` dashboard module exists. Plan change UI, invoice list, and subscription management UI completeness not confirmed.  
**Impact:** Customers cannot self-serve subscription changes. All billing changes require admin intervention.

---

### 🟡 Live Real-Time View Incomplete

**Evidence:** `dashboard/modules/live.php` and `api/v1/live.php` / `stream.php` exist. Task #8: `pending`.  
**Impact:** No true real-time push to dashboard. The fleet overview page must poll via JavaScript intervals.

---

### 🟡 Password Reset Table Not in Primary Schema

**Evidence:** `password_resets` table not found in `schema.sql`. `auth.php` references password reset flow. Likely uses `auth_tokens` with `token_type='reset'` — but this is not definitively confirmed.  
**Impact:** Low — password reset appears to function (referenced in frontend), but schema traceability is unclear.

---

### 🟡 Cloudflare Turnstile Fail-Open

**Evidence:** `CAPTCHA_FAIL_OPEN=false` in `.env` — good. But CAPTCHA is `DISABLED`, making this moot.  
**Impact:** When CAPTCHA is re-enabled, `CAPTCHA_FAIL_OPEN=false` means registration will fail if Cloudflare Turnstile is unreachable. This is the correct secure setting but may cause registration disruptions during Cloudflare outages.

---

## 5. Code Quality Observations

### 🟠 No Automated Test Suite

**Evidence:** No `/tests/` directory, no `phpunit.xml`, no `.xunit` project file found in repository.  
**Impact:** Changes cannot be automatically validated. Regressions are only caught manually or by users in production. Critical paths (auth, agent, billing webhook, productivity scoring) have no regression protection.  
**Risk:** As feature count grows, manual testing overhead becomes prohibitive and regression risk increases.

---

### 🟠 No OpenAPI Specification

**Evidence:** No `openapi.yaml`, `swagger.json`, or API schema file found.  
**Impact:** Integration developers cannot self-serve API documentation. Postman collections would need to be manually maintained. Internal engineers have no machine-readable contract.

---

### 🟡 Procedural PHP with No Framework

**Evidence:** All API files are procedural PHP functions. No Laravel, Symfony, or other framework.  
**Impact:** This is a deliberate architectural choice with both advantages (no framework CVE exposure, full control) and disadvantages (no ORM, no migration runner, no built-in queue, no testing framework integration, more boilerplate per endpoint).  
**Observation:** At current scale this is manageable. As the team grows and feature count increases, the lack of framework conventions may create inconsistency.

---

### 🟡 Stripe Keys Are Test Keys

**Evidence:** `.env`: `STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE`  
**Impact:** No live billing can be processed. Subscriptions are test mode only. Must be replaced with live keys before customer billing goes live.

---

### 🟡 Database Migration Runner is Manual

**Evidence:** No Flyway, Liquibase, or Laravel migration runner. Migrations are plain SQL files run manually.  
**Impact:** No automatic tracking of which migrations have been applied. No rollback tooling. In a multi-developer environment, migration conflicts can occur. In a CI/CD pipeline, manual migration steps are error-prone.  
**Fix:** Adopt a simple migration tracker (table with applied migration filenames) or introduce Flyway.

---

### 🟡 Inline Style Blocks Per Module

**Evidence:** Each `dashboard/modules/*.php` file contains its own `<style>` block.  
**Impact:** CSS is not minified or bundled. Duplicate style declarations may exist across modules. No build step means no tree-shaking or optimization. For current scale (43 modules) this is acceptable but will create maintenance overhead.

---

## 6. Performance Concerns

### 🟠 Report Generation is Synchronous

**Evidence:** `POST /reports` generates the file inline within the HTTP request. No async queue.  
**Impact:** Large reports (full org, 90-day date range) may time out on PHP's default `max_execution_time`. Users see no progress indicator during generation.  
**Fix:** Move to async job queue. Return job_id immediately, poll for completion.

---

### 🟡 Alert Evaluation Inline with Heartbeat Insert

**Evidence:** Alert rule evaluation triggered synchronously on each `POST /agent/heartbeat`.  
**Impact:** As org alert rule count grows, each heartbeat insert slows proportionally. For an org with 50 alert rules and 200 devices sending heartbeats every 60 seconds, this is ~167 evaluation calls per second.  
**Fix:** Move alert evaluation to a queue-based async processor.

---

### 🟡 No Database Connection Pooling

**Evidence:** `Database.php` creates a new PDO connection per request. PHP/Apache creates a new process per request (mod_php, not PHP-FPM).  
**Impact:** MySQL connection count grows linearly with concurrent PHP processes. Under load, MySQL connection limit may be reached.  
**Fix:** Switch to PHP-FPM + persistent connections, or add a connection pooler (ProxySQL, PgBouncer equivalent).

---

## 7. Maintainability Concerns

### 🟡 No Documentation of Alert Evaluation Algorithm

**Evidence:** Alert rule evaluation logic in `api/v1/alerts.php` or `api/v1/agent.php`. The exact logic for "sustained for duration_seconds" is not externally documented.  
**Impact:** Engineers making changes to alert timing may inadvertently introduce race conditions or change evaluation semantics.

---

### 🟡 No Defined Data Retention Policy

**Evidence:** `generated_reports` has `expires_at` (7 days). All other tables have no TTL or cleanup mechanism confirmed.  
**Impact:** `heartbeats`, `url_history`, `input_stats`, `webhook_logs`, `audit_logs`, `oauth_states`, `api_rate_limits` will grow indefinitely. No data retention policy means potential GDPR/compliance gaps.

---

### 🟡 Leaflet.js Loaded from External CDN

**Evidence:** `unpkg.com/leaflet@1.9.4` loaded at runtime in location tab.  
**Impact:** Requires internet connectivity for location map to render. In air-gapped environments, map will not load. External CDN dependency is a supply chain risk.  
**Fix:** Self-host Leaflet assets.

---

## 8. Testing Gaps

| Area | Test Coverage | Impact |
|---|---|---|
| Authentication (login/logout/session) | None confirmed | High — regression on auth breaks entire platform |
| Agent registration and token | None confirmed | High — broken agent registration = no telemetry |
| Productivity score algorithm | None confirmed | Medium — silent errors would corrupt scoring |
| Stripe webhook handler | None confirmed | High — billing failures go undetected |
| Leave balance deduction | None confirmed | Medium — incorrect balances create HR disputes |
| Alert rule evaluation | None confirmed | Medium — missed or duplicate alerts |
| OAuth flow | None confirmed | Medium — broken SSO blocks users |
| SQL injection surface | None confirmed | High — PDO is correct but no automated scanning |
| Rate limiting | None confirmed | Medium — bypass possible if logic has edge cases |

---

## 9. Summary Table

| # | Limitation | Severity | Effort to Fix |
|---|---|---|---|
| 1 | CAPTCHA disabled | 🔴 Critical | Low |
| 2 | MFA not enforced | 🟠 High | Medium |
| 3 | Single-server deployment | 🔴 Critical | High |
| 4 | Windows-only agent | 🔴 Critical | Very High |
| 5 | No automated tests | 🟠 High | High |
| 6 | No automated backups | 🟠 High | Low |
| 7 | Local file storage no quota | 🟠 High | Medium |
| 8 | Stripe test keys only | 🟠 High | Low |
| 9 | Heartbeat partition manual | 🟡 Medium | Low |
| 10 | Session files local | 🟡 Medium | Medium |
| 11 | Report generation synchronous | 🟡 Medium | High |
| 12 | Webhook no retry | 🟡 Medium | Medium |
| 13 | Employee portal incomplete | 🟠 High | Medium |
| 14 | Billing UI incomplete | 🟠 High | Medium |
| 15 | No OpenAPI spec | 🟡 Medium | Medium |
| 16 | Agent offline cache unencrypted | 🟡 Medium | Low |
| 17 | No data retention policy | 🟡 Medium | Medium |
| 18 | Agent LocalSystem privilege | 🟡 Medium | High (complex) |
