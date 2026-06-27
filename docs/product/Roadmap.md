# CortexOne — Product Roadmap

> **Audience:** Product Managers, Executives, Engineers, Investors  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Feature-Catalog.md](Feature-Catalog.md) · [Known-Limitations.md](Known-Limitations.md) · [Product-Bible.md](Product-Bible.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from repository analysis |
| 1.1 | 2026-06-28 | Added Stripe live keys as Immediate pre-launch blocker; corrected Stripe priority from Informational to Critical |

---

## How to Read This Document

> **Evidence key:**  
> ✅ = Verified as implemented in repository  
> ⚠️ = Partially implemented (schema or UI present but incomplete)  
> 🔲 = Not found in repository  
> 💡 = Recommendation based on analysis (not from repository)

Items marked 💡 are recommendations — they represent opportunities, not commitments.

---

## 1. Completed ✅

All of the following are verified as implemented in the codebase.

### Core Platform
- ✅ Multi-tenant organisation management with full data isolation (org_id FK everywhere)
- ✅ Role-based access control (RBAC) — 4 roles, permission JSON array
- ✅ JWT RS256 authentication (asymmetric keys, 15-min access TTL, 30-day refresh)
- ✅ Refresh token rotation with revocation
- ✅ Account lockout (10 failures → 15-min lockout)
- ✅ Immutable audit log on all mutations
- ✅ Sliding window rate limiting (api_rate_limits table)
- ✅ PHP session management (PS_SESS, HttpOnly, SameSite=Strict)

### Device Monitoring
- ✅ Windows agent v1.1.0 (72 MB, self-contained .NET 8 EXE)
- ✅ 15 BackgroundService workers in parallel
- ✅ 60-second heartbeat (CPU, RAM, disk, network, active user, uptime)
- ✅ Application usage tracking (foreground window, duration, focus count)
- ✅ Activity session tracking (login/logout, active/idle seconds)
- ✅ Keystroke and mouse click aggregation (counts only, privacy-safe)
- ✅ URL/web browsing history (Chrome, Edge, Firefox, IE)
- ✅ Network monitoring (IP history, bandwidth per adapter)
- ✅ Generic device metrics store
- ✅ Device event log

### Intelligence
- ✅ Productivity scoring engine (0–100, A–F, 4-component algorithm)
- ✅ App categorisation rules (productive/neutral/unproductive)
- ✅ App categories with productivity weight
- ✅ Risk matrix (Healthy/Watch/At-Risk segmentation)
- ✅ Anomaly detection — 6 types (activity_drop, after_hours, unknown_app, idle_surge, location_change, bandwidth_spike)
- ✅ Anomaly baselines (per-device rolling historical averages)
- ✅ Anomaly acknowledgement workflow
- ✅ Executive dashboard (fleet health + productivity summary)

### Alert Engine
- ✅ Threshold-based alert rules (5 metric types, cooldown, duration)
- ✅ Alert presets (CPU, RAM, disk, offline, idle)
- ✅ Alert severity levels (warning, error, critical)
- ✅ Alert lifecycle (open → acknowledged → resolved)
- ✅ Multi-channel notifications (email, Slack, Teams, webhook)

### HR Suite
- ✅ Leave request workflow (submit → approve → balance deduct)
- ✅ Leave types per organisation
- ✅ Leave balances per user/type/year with carry-forward
- ✅ Holiday calendar
- ✅ Shift scheduling (work_schedules → schedule_shifts → device_schedules)
- ✅ Timesheet module (device activity → timesheet)
- ✅ Payroll export (QuickBooks/Xero/CSV format)
- ✅ Overtime tracking with multiplier rules
- ✅ Attendance records

### Advanced Monitoring (Phase 3 — disabled by default)
- ✅ Screenshot capture (JPEG, configurable quality/interval)
- ✅ Session recording (JPEG frame capture, timeline playback)
- ✅ Session recording playback UI (scrubber, speed control)
- ✅ Webcam snapshots (WinRT MediaCapture, 640×480 JPEG)
- ✅ Location tracking (GPS/WiFi/IP via WinRT Geolocator)
- ✅ Location route map (Leaflet.js / OpenStreetMap)

### Integrations
- ✅ Webhook engine (11 event types, delivery logging)
- ✅ Slack notifications
- ✅ Microsoft Teams notifications
- ✅ Zapier webhook support
- ✅ Make (Integromat) webhook support
- ✅ QuickBooks export
- ✅ Xero export
- ✅ Jira export
- ✅ Asana export
- ✅ Trello export
- ✅ API key management (scoped, SHA-256 hashed)

### SSO / Auth
- ✅ Email/password login
- ✅ Google OAuth 2.0 / OIDC (code complete, credentials needed)
- ✅ Microsoft 365 SSO (code complete, credentials needed)
- ✅ SSO new user registration flow (sso-complete.php)
- ✅ OAuth CSRF state protection (oauth_states table)
- ✅ Password reset via email

### Deployment
- ✅ Agent install package (org-specific ZIP)
- ✅ Deploy-Silent.ps1 (SHA-256 verify, Defender exclusions, firewall rule)
- ✅ Deploy-Silent.bat (wrapper for non-PS admins)
- ✅ Agent auto-update (UpdateWorker, SHA-256 verification)
- ✅ Agent offline cache (SQLite queue, retry backoff)
- ✅ RMM-compatible deployment (NinjaOne, Datto, N-able, ConnectWise, Atera)

### Billing
- ✅ Stripe billing integration (webhook handler, schema)
- ✅ Three pricing tiers (Starter $3, Pro $5, Enterprise $8)
- ✅ Monthly and annual billing price IDs
- ✅ Trial management (trial_ends_at)
- ✅ Subscription events log

### Database
- ✅ 46-table schema with full multi-tenant isolation
- ✅ RANGE-partitioned heartbeats table (monthly partitions)
- ✅ All 17 migration files applied

---

## 2. In Progress ⚠️

### Employee Self-Service Portal
**Evidence:** `api/v1/portal.php` exists. Task #7 in repository task list: `in_progress`.  
**What's missing:** Full UI for employee self-service — employees viewing own productivity scores, submitting their own leave through a simplified interface.  
**Priority:** High — required for full employee adoption.

### MFA (TOTP)
**Evidence:** `users.mfa_secret` and `users.mfa_enabled` columns present. `sso_oauth.sql` migration includes `mfa_secret` field.  
**What's missing:** Full MFA enrollment UI, TOTP verification flow during login, enforcement toggle per org.  
**Priority:** High — required for enterprise buyers.

### Live Real-Time View
**Evidence:** `dashboard/modules/live.php` and `api/v1/live.php`/`stream.php` exist. Task #8: `pending`.  
**What's missing:** SSE (Server-Sent Events) stream implementation for real-time metric push to dashboard without polling.  
**Priority:** Medium — strong sales differentiator for operations-heavy customers.

### Billing UI
**Evidence:** Stripe schema and webhook handler implemented. `dashboard/modules/billing.php` exists.  
**What's missing:** Subscription management UI (plan change, seat increase/decrease), invoice list UI, payment method management.  
**Priority:** High — required before public launch.

---

## 3. Not Implemented 🔲

Items where no evidence was found in the repository.

### Mac OS Agent
**Evidence:** No macOS agent code found. Agent project TFM is `net8.0-windows10.0.19041.0` (Windows-only).  
**Status:** Not implemented.  
**Impact:** ~40% of knowledge workers use Macs — this is the single largest market exclusion.  
**Note:** Task #11: `pending` — "Mac & Linux agent (Go cross-platform)"

### Linux Agent
**Evidence:** No Linux agent code found.  
**Status:** Not implemented.  
**Impact:** DevOps, engineering, and server admin teams.

### SAML 2.0
**Evidence:** No SAML code found. Only OAuth 2.0 / OIDC implemented.  
**Status:** Not implemented.  
**Impact:** Enterprise organisations using Okta, OneLogin, Ping Identity require SAML.

### OpenAPI / Swagger Specification
**Evidence:** No openapi.yaml or swagger.json found in repository.  
**Status:** Not implemented.  
**Impact:** Partner integrations, developer onboarding friction.

### Automated Test Suite
**Evidence:** No `/tests/` directory found. No PHPUnit configuration. No xUnit project for agent.  
**Status:** Not implemented.  
**Impact:** High risk — changes cannot be validated automatically.

### Mobile Manager App
**Evidence:** No React Native, Flutter, or mobile project found.  
**Status:** Not implemented.

### Background Job Queue
**Evidence:** No Redis, Beanstalkd, or equivalent queue found. Reports use synchronous generation + cron caller.  
**Status:** Not implemented.

### Agent Encrypted Offline Cache
**Evidence:** SQLite dependency is unencrypted `Microsoft.Data.Sqlite`.  
**Status:** Not implemented.

### Object Storage Integration (S3/Blob)
**Evidence:** All file storage is local filesystem (`/storage/`, `/reports/generated/`).  
**Status:** Not implemented.

### AI-Powered Workforce Insights
**Evidence:** No LLM/AI integration found.  
**Status:** Not implemented.

### Custom Report Builder
**Evidence:** Reports use fixed templates per report_type.  
**Status:** Not implemented.

### Partition Maintenance Automation
**Evidence:** Heartbeat table partitions defined through 2026-12 with catch-all. No stored procedure for auto-adding future months.  
**Status:** Not implemented.

---

## 4. Technical Debt

All items below have supporting evidence from the repository.

| Item | Evidence | Risk | Priority |
|---|---|---|---|
| CAPTCHA disabled | `TURNSTILE_SECRET=DISABLED` in .env | Critical — open to bot registration before public launch | Immediate |
| No automated tests | No /tests/ directory | High — regressions will not be caught | High |
| WAMP/single-server | Single-server deployment, no redundancy | High — single point of failure | High |
| Local file storage | Screenshots/recordings on app server | High — disk full = data loss, no redundancy | High |
| No partition maintenance | heartbeats partitioned only through 2026-12 | Medium — queries hit catch-all after Dec 2026 | Medium |
| Webhook no retry | webhook_logs shows failures; no re-queue | Medium — missed events lost | Medium |
| No OpenAPI spec | No API documentation contract | Medium — integration developer friction | Medium |
| SQLite unencrypted | agent offline.db in plaintext | Medium — local admin can read cached telemetry | Medium |
| No cleanup jobs | oauth_states, api_rate_limits, generated_reports accumulate | Low — table bloat over time | Low |
| Stripe test keys | `sk_test_YOUR_SECRET_KEY_HERE` in .env | **Critical launch blocker** — zero revenue can be collected until replaced with live Stripe keys | Immediate |

---

## 5. Future Opportunities

All items below are recommendations (💡) — none found in repository.

### Near-Term (3–6 months)

💡 **Mac OS Agent (Go)** — Go allows a single codebase for Mac + Linux. Highest market impact item.

💡 **Cloud Object Storage** — Move screenshots/recordings to S3 or Azure Blob. Required for scale and resilience.

💡 **Complete Employee Self-Service Portal** — Employees view their own scores without admin access. Improves transparency and adoption.

💡 **Enable Cloudflare Turnstile CAPTCHA** — Replace `DISABLED` with real site key. Required before public launch.

💡 **Complete MFA Enforcement** — TOTP flow + enforcement toggle. Required for enterprise buyers.

💡 **Horizontal Scaling** — Load balancer + second app server + Redis session store. Required for reliability SLA.

### Medium-Term (6–12 months)

💡 **Linux Agent** — Same Go codebase as Mac. Covers DevOps, server admin, WSL2 environments.

💡 **SAML 2.0** — Enterprise SSO for Okta, OneLogin, Ping Identity, Azure AD SAML customers.

💡 **OpenAPI 3.0 Specification** — Machine-readable API contract for integration partners and developer onboarding.

💡 **Background Job Queue (Redis)** — Replace synchronous report generation with proper async queue.

💡 **Mobile Manager App (iOS/Android)** — Operations leads need leave approvals and alert management on their phones.

💡 **Webhook Retry with Exponential Backoff** — Guaranteed delivery for events. Critical for financial and compliance use cases.

💡 **Automated Test Suite** — PHPUnit for API + integration tests. xUnit for agent. Minimum 80% coverage on critical paths.

### Long-Term (12–24 months)

💡 **AI Workforce Summaries** — GPT/Claude integration: "Here is your team's week in one paragraph."

💡 **Predictive Analytics** — Flag employees trending toward at-risk before they drop below threshold.

💡 **Industry Benchmarks** — Anonymised opt-in benchmark data: "Your team's productivity is in the 72nd percentile for BPO companies of your size."

💡 **HRIS Integrations** — BambooHR, Workday, SAP SuccessFactors — two-way employee data sync.

💡 **Dedicated Agent Hosting** — Separate agent API servers for high-volume customers (500+ devices).

💡 **Multi-Region Deployment** — EU (GDPR), US, APAC isolated data residency.

---

## 6. Priority Matrix

### Immediate (Pre-Launch Blockers)
| Item | Type | Effort | Impact |
|---|---|---|---|
| Enable Cloudflare Turnstile | Technical debt | Low | Critical security — open bot registration until fixed |
| Replace Stripe test keys with live keys | Technical debt | Low | Revenue blocker — no billing possible until fixed |
| Complete billing UI | In Progress | Medium | Revenue enablement |
| Complete MFA flow | In Progress | Medium | Enterprise requirement |
| Production hosting | Technical debt | High | Reliability / SLA |

### High Priority (Next 90 Days)
| Item | Type | Effort | Impact |
|---|---|---|---|
| Object storage (S3/Blob) | New capability | Medium | Scalability + resilience |
| Complete employee portal | In Progress | Medium | Customer adoption |
| Automated test suite | Technical debt | High | Risk reduction |
| Live real-time view | In Progress | Medium | Sales differentiator |

### Medium Priority (3–6 Months)
| Item | Type | Effort | Impact |
|---|---|---|---|
| Mac OS agent (Go) | New capability | Very High | Market expansion +40% |
| Webhook retry logic | Technical debt | Low | Integration reliability |
| OpenAPI specification | Technical debt | Medium | Developer experience |
| Partition maintenance automation | Technical debt | Low | Operational safety |
| Background job queue | New capability | Medium | Performance |

### Low Priority (6–12 Months)
| Item | Type | Effort | Impact |
|---|---|---|---|
| Linux agent | New capability | Medium (shares Go codebase with Mac) | Engineering teams |
| SAML 2.0 | New capability | High | Enterprise deals |
| Mobile app | New capability | Very High | Manager accessibility |
| Encrypted agent cache | Security improvement | Low | Security posture |
