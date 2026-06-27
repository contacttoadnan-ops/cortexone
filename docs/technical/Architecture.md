# CortexOne — Architecture

> **Audience:** CTOs, Senior Engineers, DevOps, Security Architects  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Technology-Stack.md](Technology-Stack.md) · [Database.md](Database.md) · [API-Reference.md](API-Reference.md) · [Developer-Guide.md](Developer-Guide.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from codebase reverse-engineering |
| 1.1 | 2026-06-28 | Fixed "two-tier" terminology; flagged HMAC auth inconsistency for verification; corrected OAuth PKCE terminology; flagged ScreenshotEnabled default for verification |

---

## 1. Overall Architecture

CortexOne follows a **three-tier architecture** with two deployment components:

1. **Presentation tier** — Browser (Org Admin dashboard) and Windows Agent (employee endpoint)
2. **Application tier** — PHP 8.3 web application on Apache 2.4
3. **Data tier** — MySQL 8.4 database + local file storage

The two deployment components are the **server** (app + DB, co-located on WAMP) and the **client** (.NET 8 Windows Service agent on employee machines).

All communication is HTTPS. The agent authenticates with HMAC-SHA256 device tokens. Dashboard users authenticate via PHP sessions + JWT RS256.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Internet (HTTPS/TLS)                         │
└─────────────────────────────────────────────────────────────────────┘
         │                                          │
         ▼                                          ▼
┌─────────────────────┐                ┌─────────────────────────────┐
│  Browser (Org Admin)│                │  ProductivityAgent.exe      │
│  Vanilla JS +       │                │  .NET 8 Windows Service     │
│  PHP-rendered HTML  │                │  15 BackgroundService       │
│  dashboard/modules/ │                │  workers                    │
└────────┬────────────┘                └─────────────┬───────────────┘
         │ HTTPS + PS_SESS (cookie)                  │ HTTPS + Device Token
         ▼                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    app.aptus.global (Single Server)                 │
│                                                                     │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  Apache 2.4 / PHP 8.3        │  │  api/index.php               │ │
│  │  dashboard/index.php         │  │  Routes → api/v1/*.php       │ │
│  │  dashboard/modules/*.php     │  │  39 resource files           │ │
│  │  dashboard/templates/        │  │  ~150+ endpoint handlers     │ │
│  │  shell.php (layout)          │  │                              │ │
│  └──────────────┬───────────────┘  └──────────────┬───────────────┘ │
│                 │                                  │                │
│                 └──────────────┬───────────────────┘                │
│                                │                                    │
│                    ┌───────────▼────────────┐                       │
│                    │   api/helpers/          │                      │
│                    │   ├─ JWT.php           │                       │
│                    │   ├─ Database.php      │                       │
│                    │   ├─ Response.php      │                       │
│                    │   ├─ AuthMiddleware.php│                       │
│                    │   ├─ RBAC.php          │                       │
│                    │   ├─ RateLimiter.php   │                       │
│                    │   └─ AuditMiddleware.php│                      │
│                    └───────────┬────────────┘                       │
│                                │                                    │
│                    ┌───────────▼────────────┐                       │
│                    │   MySQL 8.4.7          │                       │
│                    │   DB: productivity_    │                       │
│                    │   suite                │                       │
│                    │   46 tables            │                       │
│                    │   heartbeats:          │                       │
│                    │   RANGE partitioned    │                       │
│                    └────────────────────────┘                       │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  /storage/screenshots/{org_id}/{device_id}/                   │ │
│  │  /storage/recordings/{device_id}/{date}/{recording_id}/       │ │
│  │  /storage/webcam/{device_id}/{date}/                          │ │
│  │  /reports/generated/                                          │ │
│  │  /downloads/ (agent binary + appsettings template)           │ │
│  │  /config/keys/ (jwt_private.pem, jwt_public.pem)             │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend

### Technology
- **Rendering:** Server-side PHP → HTML. No SPA framework (no React, Vue, Angular)
- **JavaScript:** Vanilla ES2020+
- **CSS:** Inline `<style>` blocks per module. CSS custom properties for theming
- **Icons:** Bootstrap Icons 1.x (local assets, not CDN)
- **Maps:** Leaflet.js 1.9.4 (loaded on-demand from unpkg.com CDN for location tab)

### Global JS Object: `PSApp`
The entire frontend communicates with the API through a global object defined in the shell template:

```javascript
PSApp.api.get(endpoint, params)     // GET /api/v1/{endpoint}?{params}
PSApp.api.post(endpoint, body)      // POST /api/v1/{endpoint}
PSApp.api.put(endpoint, body)       // PUT /api/v1/{endpoint}
PSApp.api.delete(endpoint)          // DELETE /api/v1/{endpoint}
PSApp.toast(message, type)          // Show notification toast
PSApp.esc(string)                   // HTML escape (XSS prevention)
PSApp.confirm(message, callback)    // Confirmation dialog
```

### Routing
All dashboard pages are served from a single entry point:
```
/dashboard/index.php?page={module_name}
```

The `$allowedPages` array in `dashboard/index.php` whitelists all valid page names:
```php
$allowedPages = [
    'overview', 'devices', 'device-detail',
    'users', 'departments', 'reports',
    'alerts', 'audit', 'config', 'profile',
    'timesheets', 'insights',
    'projects', 'webhooks', 'geofence', 'anomalies', 'network',
    'app-categories', 'productivity', 'scheduling', 'executive',
    'employee-productivity', 'manager',
    'organizations',
    'agent-download', 'identity', 'my-organization', 'billing',
    'screenshots', 'url-history', 'keystrokes', 'app-usage',
    'live', 'onboarding',
    'leave', 'holiday-calendar',
    'integrations',
    'recordings',
];
```

### Shell Template
`dashboard/templates/shell.php` renders the outer layout (sidebar, top navigation, content area). Individual module files are `require`d into the content area slot.

### Public Pages (No Auth Required)
- `?page=register` → `modules/register.php`
- `?page=sso-complete` → `modules/sso-complete.php`
- `?page=verify-email` → `modules/verify-email.php`
- `?page=forgot-password` → `modules/forgot-password.php`
- `?page=reset-password` → `modules/reset-password.php`

### CSS Design System
```css
:root {
    --surface: ...;        /* Card/panel background */
    --border: ...;         /* Dividers, input borders */
    --blue: ...;           /* Primary action color */
    --green: ...;          /* Success, active */
    --amber: ...;          /* Warning */
    --red: ...;            /* Error, critical */
    --tx-1: ...;           /* Primary text */
    --tx-2: ...;           /* Secondary text */
    --tx-3: ...;           /* Tertiary text */
    --tx-4: ...;           /* Disabled text */
    --r: ...;              /* Standard border-radius */
    --r-sm: ...;           /* Small border-radius */
}
```

---

## 3. Backend

### Entry Point and Routing
```
/api/index.php (API entry point)
    ├── Loads api/bootstrap.php (.env, config, DB, helpers)
    ├── Reads URI segments → maps to resource file
    ├── PUBLIC_ROUTES = ['auth', 'register', 'agent-download', 'oauth']
    │      (no auth required for these prefixes)
    │      NOTE: 'agent-update' is NOT in PUBLIC_ROUTES per this list but
    │      GET /agent-update/check is documented as public in API-Reference.
    │      Verify against actual api/index.php PUBLIC_ROUTES constant.
    ├── Rate limiting check (api_rate_limits table)
    ├── Auth middleware for protected routes
    └── Routes:
        'auth'           → api/v1/auth.php
        'register'       → api/v1/register.php
        'agent'          → api/v1/agent.php
        'agent-download' → api/v1/agent-download.php
        'agent-update'   → api/v1/agent-update.php
        'oauth'          → api/v1/oauth.php
        'devices'        → api/v1/devices.php
        'users'          → api/v1/users.php
        'productivity'   → api/v1/productivity.php
        'alerts'         → api/v1/alerts.php
        'anomalies'      → api/v1/anomalies.php
        'reports'        → api/v1/reports.php
        'leave'          → api/v1/leave.php
        'scheduling'     → api/v1/scheduling.php
        'payroll'        → api/v1/payroll.php
        'integrations'   → api/v1/integrations.php
        'webhooks'       → api/v1/webhooks.php
        'api-keys'       → api/v1/api-keys.php
        'recordings'     → api/v1/recordings.php
        'organizations'  → api/v1/organizations.php
        'billing'        → api/v1/billing.php
        ... (39 total)
```

### Helper Layer (`api/helpers/`)

**`Database.php`** — PDO wrapper:
```php
Database::fetchOne($sql, $params)      // Returns single row or null
Database::fetchAll($sql, $params)      // Returns array of rows
Database::execute($sql, $params)       // INSERT/UPDATE/DELETE, returns lastInsertId
Database::getConnection()              // Raw PDO for transactions
```

**`JWT.php`** — RS256 JWT management:
```php
JWT::generate($claims)    // Signs with private PEM key, returns access/refresh tokens
JWT::verify($token)       // Verifies with public PEM key, returns claims or throws
JWT::revoke($jti)         // Marks token revoked in auth_tokens table
JWT::setConfig($config)   // Injects JWT config (called from bootstrap)
```

**`RBAC.php`** — Role-based access:
```php
RBAC::isAdmin($user)       // role_id <= 2
RBAC::isSuperAdmin($user)  // role_id === 1
RBAC::isManager($user)     // role_id <= 3
RBAC::hasPermission($user, $permission)  // Checks JSON permissions on role
```

**`AuthMiddleware.php`** — Authentication gate:
```php
AuthMiddleware::requireAuth()         // PHP session or Bearer JWT; throws 401
AuthMiddleware::requireAgent()        // HMAC device token validation; throws 401
AuthMiddleware::getOrgId($user)       // Returns effective org_id (SA context switch)
```

**`RateLimiter.php`** — Sliding window:
```php
RateLimiter::check($identifier, $endpoint, $limit, $windowSeconds)
// Reads/writes api_rate_limits table. Returns false if limit exceeded.
```

**`AuditMiddleware.php`** — Audit trail:
```php
AuditMiddleware::log($user, $action, $resourceType, $resourceId, $oldValues, $newValues)
// Inserts to audit_logs table. Called from mutation endpoints.
```

**`Response.php`** — Standardised output:
```php
Response::success($data, $code)     // { success: true, data: ... }
Response::error($message, $code)    // { success: false, error: ... }
Response::paginated($data, $meta)   // { data: [...], meta: { total, page, per_page } }
```

### Configuration (`config/app.php`)
Loaded on every request via `api/bootstrap.php`. Reads `.env` file into `$_ENV`. Key sections:
```php
$config = [
    'app'      => [ 'name', 'env', 'debug', 'url', 'tz' ],
    'db'       => [ 'host', 'port', 'name', 'user', 'pass' ],
    'jwt'      => [ 'private_key', 'public_key', 'access_ttl' (900s), 'refresh_ttl' (2592000s) ],
    'agent'    => [ 'secret' (HMAC key for device tokens) ],
    'cron'     => [ 'secret' ],
    'mail'     => [ 'driver', 'host', 'port', 'encryption', 'username', 'password', 'from' ],
    'oauth'    => [ 'google' => [...], 'microsoft' => [...], 'state_ttl_seconds' (600) ],
    'stripe'   => [ 'secret_key', 'publishable_key', 'webhook_secret', price_ids... ],
    'turnstile'=> [ 'secret', 'site_key', 'fail_open' (false) ],
];
```

---

## 4. Windows Agent

### Architecture Overview
```
ProductivityAgent.exe
│ Windows Service (ProductivityAgentSvc)
│ Account: LocalSystem
│ Startup: Automatic
│ Auto-restart: 3 actions (10s delay each)
│
├── Host: Microsoft.Extensions.Hosting.WorkerService
│
└── 15 BackgroundService Workers (all run in parallel):
    ├── RegistrationWorker       ← Gates all others via ManualResetEventSlim
    ├── HeartbeatWorker          ← PeriodicTimer, 60s interval
    ├── MetricsWorker            ← PeriodicTimer, 5min interval
    ├── AppUsageWorker           ← PeriodicTimer, 5min interval
    ├── ActivitySessionWorker    ← WTS session change events
    ├── KeystrokeWorker          ← SetWindowsHookEx, hourly aggregation
    ├── UrlHistoryWorker         ← Browser history files, 30min interval
    ├── ScreenshotWorker         ← PeriodicTimer, configurable (default 15min)
    ├── VideoRecordingWorker     ← Phase 3, configurable frame rate
    ├── WebcamWorker             ← Phase 3, WinRT MediaCapture
    ├── LocationWorker           ← Phase 3, WinRT Geolocator
    ├── UpdateWorker             ← PeriodicTimer, 6h interval
    ├── OfflineSyncWorker        ← Continuous, SQLite queue flush
    ├── TrayNotificationWorker   ← Event-driven, WTS_SESSION_CHANGE
    └── IpcServerWorker          ← Named pipe server (future IPC)
```

### Session-0 Isolation
Windows Services run in Session 0 (SYSTEM context) with no access to the interactive user session. GUI-dependent operations (screen capture, webcam, WinRT) require a child process running in the user's session:

```
Service (Session 0) → WTSGetActiveConsoleSessionId()
                    → WTSQueryUserToken(sessionId) → userToken
                    → CreateProcessAsUser(userToken, exe, args)
                    → Child process runs in user session
                    → Child writes output to temp file
                    → Service reads output file
```

This pattern is used by `ScreenshotWorker` (--capture-screen flag) and `WebcamWorker` (--capture-webcam flag).

### Offline Queue
```
Network request fails
    → Serialize payload (JSON)
    → INSERT into SQLite offline.db (Microsoft.Data.Sqlite)
    → Path: C:\ProgramData\ProductivityAgent\Cache\offline.db

OfflineSyncWorker polls every 5s
    → SELECT oldest N rows from queue
    → Attempt HTTP upload
    → On success: DELETE from queue
    → On failure: increment retry_count, update next_retry (exponential backoff)
    → Max retries: 5 per payload
    → Queue overflow: DROP oldest rows (LRU eviction)
```

### Agent Configuration
Stored in `C:\Program Files\ProductivityAgent\appsettings.json`:
```json
{
  "AgentOptions": {
    "ServerUrl": "https://app.aptus.global",
    "OrgId": "...",
    "RegistrationSecret": "...",
    "DeviceId": "",
    "DeviceToken": "",
    "HeartbeatIntervalSeconds": 60,
    "MetricsIntervalSeconds": 300,
    "AppUsageIntervalSeconds": 300,
    "ScreenshotIntervalSeconds": 900,
    "ScreenshotQuality": 70,
    "ScreenshotEnabled": true,    ← Verify default against actual appsettings.json — Feature-Catalog states opt-in/disabled by default
    "RecordingEnabled": false,
    "WebcamEnabled": false,
    "LocationEnabled": false,
    "OfflineCacheMaxMb": 50,
    "LogLevel": "Warning"
  }
}
```

### Auto-Update Flow
```
UpdateWorker (every 6 hours)
    → GET /api/v1/agent-update/check (no auth required)
    ← { version, download_url, sha256, is_mandatory, min_os_version }
    
    If current_version < latest_stable:
        → Download new EXE to temp path
        → Verify SHA-256 hash (abort if mismatch)
        → sc stop ProductivityAgentSvc
        → Replace EXE at install path
        → sc start ProductivityAgentSvc
        → Log to agent_update_history table via API
```

---

## 5. REST API

### Structure
```
/api/
├── index.php          ← Entry point, routing, auth, rate limiting
├── bootstrap.php      ← .env loading, config, DB, helper init
├── helpers/
│   ├── JWT.php
│   ├── Database.php
│   ├── Response.php
│   ├── AuthMiddleware.php
│   ├── RBAC.php
│   ├── RateLimiter.php
│   └── AuditMiddleware.php
└── v1/
    ├── auth.php
    ├── register.php
    ├── agent.php
    ├── agent-download.php
    ├── agent-update.php
    ├── oauth.php
    ├── devices.php
    ├── users.php
    ├── departments.php
    ├── productivity.php
    ├── alerts.php
    ├── anomalies.php
    ├── reports.php
    ├── leave.php
    ├── scheduling.php
    ├── payroll.php
    ├── timesheets.php
    ├── integrations.php
    ├── webhooks.php
    ├── api-keys.php
    ├── recordings.php
    ├── screenshots.php
    ├── url-history.php
    ├── keystrokes.php
    ├── app-usage.php
    ├── organizations.php
    ├── billing.php
    ├── geofence.php
    ├── audit.php
    ├── config.php
    ├── identity.php
    ├── network.php
    ├── projects.php
    ├── insights.php
    ├── live.php / stream.php
    ├── portal.php
    └── ... (39 total files)
```

### Request Flow
```
Browser/Agent → Apache 2.4
    → mod_rewrite → /api/index.php
    → api/bootstrap.php (env, config, DB)
    → Route parsing (URI segments)
    → PUBLIC_ROUTES check
    → Rate limiter (api_rate_limits table)
    → Auth middleware (session or JWT or device token)
    → RBAC check
    → Resource handler (api/v1/*.php)
        → Input validation
        → PDO prepared statement
        → Business logic
        → AuditMiddleware::log() if mutation
        → Response::success() or Response::error()
    → JSON response
```

### Rate Limits
| Endpoint Group | Limit | Window |
|---|---|---|
| Default (all endpoints) | 60 req | 60 seconds |
| Auth (login, refresh) | 10 req | 60 seconds |
| Agent download | 30 req | 60 seconds |
| Registration | 5 req | 3600 seconds |

Rate limits enforced via `api_rate_limits` table (sliding window). Identifier = IP address (or device_uuid for agent).

### CORS Policy
Whitelist: `https://app.aptus.global`, `https://www.app.aptus.global`  
Methods: `GET, POST, PUT, DELETE, OPTIONS`  
Headers: `Content-Type, Authorization`

> Full endpoint documentation: [API-Reference.md](API-Reference.md)

---

## 6. Authentication Architecture

### Dashboard Authentication Flow
```
1. POST /api/v1/auth/login { username, password }
2. Server: bcrypt_verify(password, hash) — cost 12
3. Check: failed_attempts < 10 AND (locked_until IS NULL OR locked_until < NOW())
4. On success:
   a. JWT::generate({ sub: user_id, org: org_id, role: role_id, name, type: 'access' })
      TTL: 900 seconds
   b. JWT::generate({ sub: user_id, type: 'refresh' })
      TTL: 2,592,000 seconds
   c. INSERT auth_tokens (token_hash SHA-256, expires_at)
5. Response: { user, access_token, refresh_token }
6. JS: POST /dashboard/index.php?action=set_session { token: access_token }
7. Server: JWT::verify(token) → extract claims → $_SESSION['user_id', 'org_id', 'role_id']
8. Session cookie: PS_SESS, HttpOnly=true, SameSite=Strict, Secure=true
```

### Agent Authentication Flow
```
1. POST /api/v1/agent/register { device_uuid, hostname, ...hardware }
   Header: X-Org-Id: {org_id}, X-Registration-Secret: {AGENT_SECRET}
2. Server generates device_token — exact HMAC inputs must be verified from agent.php
3. INSERT devices row → return { device_id, device_token }
4. Agent stores device_id + device_token in appsettings.json

Subsequent requests:
   Header: X-Device-Id: {device_id}, X-Device-Token: {token}
   Server: validates token via HMAC — verify exact construction from AuthMiddleware.php
```

> **TODO (ISSUE-003):** Verify the exact HMAC inputs for token generation and verification against `api/v1/agent.php` and `api/helpers/AuthMiddleware.php`. The generation and verification descriptions must use identical inputs.

### OAuth 2.0 / SSO Flow (Standard State-Based CSRF Protection)
```
1. User clicks "Continue with Google/Microsoft"
2. GET /api/v1/oauth/redirect/{provider}?intent=login
3. Server: INSERT oauth_states (state=64-char random, provider, intent, TTL=600s)
4. HTTP 302 → provider consent screen (scope: openid email profile)

5. Provider callback → GET /api/v1/oauth/callback/{provider}?code=...&state=...
6. Server:
   a. SELECT oauth_states WHERE state=? (verify CSRF, check TTL)
   b. DELETE oauth_states row (one-time use)
   c. POST to provider token endpoint (exchange code for access_token)
   d. GET provider userinfo endpoint (Google: googleapis.com/oauth2/v3/userinfo)
                                     (Microsoft: graph.microsoft.com/v1.0/me)
   e. Look up user by auth_provider + auth_provider_id OR email
   f. Existing user → loginUser() → PHP session → redirect dashboard
   g. New user → store in $_SESSION['sso_pending'] → redirect sso-complete page
   h. New user completes org form → POST /api/v1/oauth/complete → create org + user
```

### JWT Token Structure
```json
{
  "sub": "123",
  "org": "456",
  "role": "2",
  "name": "John Smith",
  "type": "access",
  "iss": "productivity-suite",
  "iat": 1735000000,
  "exp": 1735000900,
  "jti": "uuid-v4"
}
```

Algorithm: RS256 (RSASSA-PKCS1-v1_5 + SHA-256)  
Keys: 2048-bit RSA. Private: `config/keys/jwt_private.pem`. Public: `config/keys/jwt_public.pem`.

---

## 7. Scheduling Architecture

### Server-side Scheduling
Scheduled reports are triggered by an external cron caller using a `CRON_SECRET`:
```bash
# Called by Windows Task Scheduler or external cron
curl -X POST https://app.aptus.global/api/v1/reports/run-scheduled \
  -H "X-Cron-Secret: {CRON_SECRET}"
```

The `/api/v1/reports/run-scheduled` handler:
1. Queries `scheduled_reports` WHERE `next_run_at <= NOW()` AND `is_active = 1`
2. For each: generates report, saves file, updates `next_run_at` per cron expression
3. Delivers: email (with PDF attachment), Slack webhook, or saves to `generated_reports`

### Agent-side Scheduling
All timing in the agent uses `System.Threading.PeriodicTimer` (C# .NET 8):
```csharp
// Example: HeartbeatWorker
using var timer = new PeriodicTimer(TimeSpan.FromSeconds(_options.HeartbeatIntervalSeconds));
while (await timer.WaitForNextTickAsync(stoppingToken))
{
    await SendHeartbeatAsync();
}
```

Intervals are per-device configurable via `agent_configs` table. Overrides fetched on registration.

---

## 8. Reporting Architecture

```
On-demand report request:
POST /api/v1/reports
{ report_type, date_from, date_to, department_id, format, filters }
    → Validate parameters
    → Query relevant tables (varies by report_type)
    → Generate file:
        PDF  → (library not confirmed; writes to /reports/generated/)
        Excel → (library not confirmed)
        CSV  → native PHP fputcsv
    → INSERT generated_reports (file_path, expires_at = NOW() + 7 days)
    → Response: { report_id, download_url }

Scheduled report:
    → Defined via POST /api/v1/reports/scheduled
    → Stored in scheduled_reports (schedule_cron, format, recipients)
    → Cron caller triggers run-scheduled endpoint
    → Same generation pipeline
    → Delivers via email or Slack webhook
```

---

## 9. Background Jobs and Services

| Job | Trigger | Location |
|---|---|---|
| Heartbeat insert | Agent push (60s) | `api/v1/agent.php` |
| Alert evaluation | After each heartbeat insert | `api/v1/agent.php` or `api/v1/alerts.php` |
| Productivity scoring | Cron / on-demand | `api/v1/productivity.php` |
| Anomaly detection | Cron / on-demand | `api/v1/anomalies.php` |
| Scheduled reports | Cron via CRON_SECRET | `api/v1/reports.php` |
| Agent auto-update | UpdateWorker (6h, agent-side) | Agent EXE |
| Offline sync | OfflineSyncWorker (continuous, agent) | Agent EXE |
| Token expiry cleanup | [Not verified — likely cron] | Unknown |
| Partition maintenance | [Not verified — manual or cron] | MySQL |

---

## 10. External Integrations

### Notification Channels
| Platform | Method | Trigger |
|---|---|---|
| Email | SMTP (Gmail, TLS 587) | Alerts, reports, registration, reset password |
| Slack | Incoming Webhook URL | Alerts, anomalies, leave events, custom webhook events |
| Microsoft Teams | Incoming Webhook URL | Same as Slack |
| Zapier | Webhook POST | Any of 11 event types |
| Make (Integromat) | Webhook POST | Any of 11 event types |

### Data Export
| Platform | Format | Direction |
|---|---|---|
| QuickBooks | CSV (QB format) | Export timesheet/payroll data |
| Xero | CSV (Xero format) | Export timesheet/payroll data |
| Jira | JSON/CSV | Export task data |
| Asana | JSON/CSV | Export task data |
| Trello | JSON/CSV | Export task data |

### Webhook Event Types (11)
`alert_triggered`, `anomaly_detected`, `device_offline`, `device_online`, `leave_requested`, `leave_approved`, `leave_rejected`, `overtime_detected`, `task_completed`, `recording_completed`, `location_updated`

### Third-Party Auth
| Service | SDK | Purpose |
|---|---|---|
| Google Identity | OAuth 2.0 OIDC, v3/userinfo | User SSO login/register |
| Microsoft Identity Platform | OAuth 2.0 OIDC, Graph API /v1.0/me | User SSO login/register |
| Stripe | REST API + Webhook | Subscription billing |
| Cloudflare Turnstile | REST verification API | Registration CAPTCHA (disabled) |

---

## 11. Communication Flow Diagrams

### Alert Flow
```
Agent HeartbeatWorker (60s)
    → POST /api/v1/agent/heartbeat { cpu: 95, ... }
    → INSERT heartbeats
    → SELECT alert_rules WHERE org_id = ? AND metric_type = 'cpu'
    → Evaluate: 95 > threshold (90) for duration (300s)?
    → Check cooldown: last_fired + cooldown_minutes > NOW() ?
    → INSERT alerts (status='open', severity='critical')
    → Dispatch:
        email   → SMTP → IT admin inbox
        slack   → POST webhook_url { text: "CPU critical on LAPTOP-01" }
        teams   → POST teams_webhook_url
        webhook → POST custom_url (webhook_logs row)
```

### Productivity Score Flow
```
Cron / on-demand
    → For each device × date:
        SELECT app_usage JOIN productivity_rules → categorised minutes
        SELECT activity_sessions → active_seconds, idle_seconds
        SELECT input_stats → keystroke_count
        
        productive_ratio = productive_min / total_active_min × 40
        app_quality      = weighted_avg(app_categories) × 25
        active_ratio     = active_sec / expected_sec × 20
        focus_score      = max_uninterrupted_productive_min / 60 × 15
        
        score = sum, clamp(0, 100)
        grade = A(80+) B(65+) C(50+) D(35+) F(<35)
        
        UPSERT productivity_scores
```

---

## 12. Deployment Architecture

### Current State
```
Single Windows Server (WAMP)
├── Apache 2.4 (port 443 → TLS)
│   └── PHP 8.3 (mod_php)
│       └── C:/wamp64/www/ProductivitySuite/
├── MySQL 8.4.7 (port 3306, localhost only)
├── File storage (local disk)
│   └── /storage/ (screenshots, recordings, webcam)
│   └── /reports/generated/
└── Sessions stored in /sessions/ directory
```

### Recommended Production Architecture
```
Load Balancer (Cloudflare / AWS ALB)
    ├── App Server 1 (Windows Server 2022 + IIS/nginx + PHP)
    └── App Server 2 (Windows Server 2022 + IIS/nginx + PHP)
         ↓
    MySQL 8.4 (dedicated server, RDS, or Azure Database)
         ↓
    Object Storage (AWS S3 / Azure Blob)
    (screenshots, recordings, webcam, reports)
         ↓
    Shared session store (Redis) for multi-server sessions
```

---

## 13. Security Architecture

### Defence-in-Depth Layers

| Layer | Control | Implementation |
|---|---|---|
| Network | TLS encryption | HTTPS enforced, app.aptus.global |
| Application | Authentication | PHP session + JWT RS256 + HMAC device token |
| Application | Authorisation | RBAC (role_id gates) + org-scope on all queries |
| Application | Input validation | PHP filter_var, type casting, PDO prepared statements |
| Application | Output encoding | PSApp.esc() (JS), htmlspecialchars() (PHP) |
| Application | CSRF protection | SameSite=Strict session cookie; OAuth state token |
| Application | Rate limiting | Sliding window per IP + endpoint (api_rate_limits) |
| Application | Account lockout | 10 failed attempts → 15 min lockout |
| Application | Audit trail | audit_logs: every mutation logged with old/new values |
| Data | SQL injection | PDO prepared statements throughout (no string concatenation) |
| Data | Password hashing | bcrypt, cost factor 12 |
| Data | Token security | JWT RS256, refresh rotation, revocation via jti |
| Agent | Binary integrity | SHA-256 verified before execution on download |
| Agent | Auth token | HMAC-SHA256 device token, not replayable |
| Agent | Privacy | Phase 3 features opt-in, employee notification on first activation |

### Security Gaps (Current)
1. Cloudflare Turnstile CAPTCHA explicitly disabled (`TURNSTILE_SECRET=DISABLED`)
2. MFA (TOTP) schema present but UI enforcement not verified complete
3. Agent offline SQLite cache is not encrypted at rest
4. Local file storage (screenshots) has no access control beyond filesystem permissions
5. Single-server deployment — no WAF, no DDoS protection beyond Cloudflare (if configured)

> See [Known-Limitations.md](Known-Limitations.md) for full limitation details.

---

## 14. Data Flow

### Agent → Server (Primary Path)
```
Employee Windows Machine
    ProductivityAgent.exe
    [Collect telemetry every 60s]
    [Try HTTPS POST to app.aptus.global]
        Success → Server inserts to MySQL
        Failure → Queue to local SQLite (offline.db)
                  OfflineSyncWorker retries when online
```

### Server → Third Party (Events)
```
MySQL mutation event (alert, anomaly, leave, etc.)
    → Webhook engine queries webhooks table (WHERE org_id = ? AND events JSON contains event_type)
    → HTTP POST to webhook_url
    → Log to webhook_logs (response_code, fired_at)
    → If 4xx/5xx: log failure (no automatic retry currently)
```

### Dashboard ↔ API (Interactive)
```
Browser (logged-in admin)
    JS fetch → GET/POST /api/v1/{resource}
    API validates session
    API queries MySQL (all queries WHERE org_id = ?)
    API returns JSON
    JS updates DOM
```
