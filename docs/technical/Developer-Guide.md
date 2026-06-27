# CortexOne — Developer Guide

> **Audience:** Software Engineers, New Hires, Contributors  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Architecture.md](Architecture.md) · [Technology-Stack.md](Technology-Stack.md) · [Database.md](Database.md) · [API-Reference.md](API-Reference.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from codebase reverse-engineering |
| 1.1 | 2026-06-28 | Fixed .env.example reference (file doesn't exist); added required directory creation steps; corrected integration count |

---

## 1. Repository Structure

```
ProductivitySuite/                  ← Web application root
├── .env                            ← Environment variables (never commit)
├── .htaccess                       ← Apache mod_rewrite rules
│
├── api/                            ← REST API
│   ├── index.php                   ← Entry point, routing, auth, rate limiting
│   ├── bootstrap.php               ← .env loading, config, helpers
│   ├── helpers/
│   │   ├── JWT.php                 ← RS256 JWT sign/verify/revoke
│   │   ├── Database.php            ← PDO wrapper (fetchOne, fetchAll, execute)
│   │   ├── Response.php            ← JSON response helpers
│   │   ├── AuthMiddleware.php      ← Session/JWT/device token auth
│   │   ├── RBAC.php                ← Role-based access control
│   │   ├── RateLimiter.php         ← Sliding window rate limiting
│   │   └── AuditMiddleware.php     ← Audit log writes
│   └── v1/                         ← 39 resource handler files
│       ├── auth.php                ← Login, logout, refresh, password reset
│       ├── register.php            ← Org registration, email verify
│       ├── oauth.php               ← Google/Microsoft SSO
│       ├── agent.php               ← All agent telemetry uploads
│       ├── agent-download.php      ← Agent package + script generation
│       ├── agent-update.php        ← Auto-update check endpoint
│       ├── devices.php             ← Device CRUD, fleet listing
│       ├── users.php               ← User CRUD
│       ├── departments.php         ← Department management
│       ├── productivity.php        ← Scoring, rules, summary
│       ├── alerts.php              ← Alert rules + alert instances
│       ├── anomalies.php           ← Anomaly list + acknowledge
│       ├── reports.php             ← Report generation, scheduling
│       ├── leave.php               ← Leave requests, types, balances
│       ├── scheduling.php          ├─ Shift scheduling
│       ├── payroll.php             ├─ Payroll + overtime
│       ├── timesheets.php          ├─ Timesheet module
│       ├── integrations.php        ├─ 9 verified platform integrations
│       ├── webhooks.php            ├─ Webhook config + logs
│       ├── api-keys.php            ├─ API key management
│       ├── recordings.php          ├─ Session recordings (Phase 3)
│       ├── screenshots.php         ├─ Screenshot gallery
│       ├── url-history.php         ├─ URL history
│       ├── keystrokes.php          ├─ Keystroke stats
│       ├── app-usage.php           ├─ App usage detail
│       ├── network.php             ├─ Network forensics
│       ├── organizations.php       ├─ Super admin org management
│       ├── billing.php             ├─ Stripe billing
│       ├── geofence.php            ├─ Geofence rules
│       ├── audit.php               ├─ Audit log query
│       ├── config.php              ├─ Org configuration
│       ├── identity.php            ├─ Identity mapping
│       ├── projects.php            ├─ Projects module
│       ├── insights.php            ├─ Insights module
│       ├── live.php / stream.php   └─ Live stream (partial)
│       └── portal.php             ← Employee portal (partial)
│
├── config/
│   ├── app.php                     ← Application config (reads .env)
│   └── keys/
│       ├── jwt_private.pem         ← RSA 2048 private key (never commit)
│       └── jwt_public.pem          ← RSA 2048 public key
│
├── dashboard/
│   ├── index.php                   ← Dashboard entry, routing, session
│   ├── modules/                    ← 43 dashboard page files
│   │   ├── login.php               ← Login page (SSO + password)
│   │   ├── register.php            ← Registration page
│   │   ├── sso-complete.php        ← SSO new user completion
│   │   ├── overview.php            ← Main dashboard
│   │   ├── devices.php             ← Fleet listing
│   │   ├── device-detail.php       ← Per-device deep dive
│   │   ├── executive.php           ← Executive dashboard
│   │   ├── productivity.php        ← Productivity scoring view
│   │   ├── alerts.php              ← Alert management
│   │   ├── anomalies.php           ← Anomaly detection view
│   │   ├── leave.php               ← Leave management
│   │   ├── scheduling.php          ├─ Shift scheduling
│   │   ├── timesheets.php          ├─ Timesheets
│   │   ├── payroll.php             ├─ Payroll export
│   │   ├── reports.php             ├─ Report generation
│   │   ├── integrations.php        ├─ Integration hub
│   │   ├── webhooks.php            ├─ Webhook config
│   │   ├── recordings.php          ├─ Session recordings (Phase 3)
│   │   ├── config.php              ├─ Org config
│   │   ├── agent-download.php      └─ Agent deployment
│   │   └── ... (43 total)
│   └── templates/
│       └── shell.php               ← Outer layout (sidebar, nav, content area)
│
├── database/
│   ├── schema.sql                  ← Full database schema
│   └── migrations/
│       ├── 001_initial.sql
│       ├── 002_add_leave_tables.sql
│       ├── ...
│       ├── sso_oauth.sql           ← SSO columns and tables
│       └── ... (17+ migrations)
│
├── downloads/
│   ├── ProductivityAgent.exe       ← Latest agent binary
│   ├── agent-meta.json             ← { version, sha256, size }
│   └── appsettings.json            ← Agent config template
│
├── storage/
│   ├── screenshots/                ← {org_id}/{device_id}/{file}.jpg
│   ├── recordings/                 ← {device_id}/{date}/{recording_id}/{frame}.jpg
│   └── webcam/                     ← {device_id}/{date}/{file}.jpg
│
├── reports/
│   └── generated/                  ← Report files (7-day TTL)
│
└── sessions/                       ← PHP session files
```

---

## 2. Development Environment Setup

### Prerequisites

| Software | Version | Purpose |
|---|---|---|
| WAMP | 3.x | PHP + Apache + MySQL stack on Windows |
| PHP | 8.3.x | Backend runtime |
| MySQL | 8.4.x | Database |
| Apache | 2.4.x | Web server |
| Git | Any | Version control |
| .NET 8 SDK | 8.0.x | Agent development |
| Visual Studio 2022 | Any | Agent development (preferred) |
| VS Code | Any | PHP development (preferred) |

### Installation (Web Application)

```bash
# 1. Clone repository to WAMP www directory
git clone <repo-url> C:/wamp64/www/ProductivitySuite

# 2. Create .env from the actual .env file (no .env.example template exists in repo)
cp .env .env.backup        # keep a backup of production values
# Then edit .env with your local development credentials

# 3. Edit .env with real credentials
# Required: DB_*, MAIL_*, AGENT_SECRET, CRON_SECRET
# Optional: GOOGLE_CLIENT_ID, MICROSOFT_CLIENT_ID, STRIPE_*

# 4. Generate JWT RSA key pair
mkdir config/keys
openssl genrsa -out config/keys/jwt_private.pem 2048
openssl rsa -in config/keys/jwt_private.pem -pubout -out config/keys/jwt_public.pem

# 5. Create MySQL database
mysql -u root -p -e "CREATE DATABASE productivity_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'ps_app'@'localhost' IDENTIFIED BY 'your_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON productivity_suite.* TO 'ps_app'@'localhost';"

# 6. Run migrations (in order)
mysql -u root -p productivity_suite < database/schema.sql
mysql -u root -p productivity_suite < database/migrations/sso_oauth.sql
# ... run all migration files in numerical order

# 7. Create required directories (these must exist — they are not created by the repo)
mkdir sessions
mkdir -p storage/screenshots storage/recordings storage/webcam
mkdir -p reports/generated
mkdir -p downloads
# Place ProductivityAgent.exe and agent-meta.json in downloads/ for the agent download endpoint to work
# Ensure these directories are writable by Apache (WAMP: right-click → properties → security)

# 8. Configure Apache vhost (WAMP vhosts.conf)
# DocumentRoot: C:/wamp64/www/ProductivitySuite
# AllowOverride All (enables mod_rewrite from .htaccess)
# Restart WAMP after changes
```

### Installation (Agent Development)

```bash
# 1. Open ProductivityAgent solution in Visual Studio 2022
# File: Agent/ProductivityAgent.sln

# 2. Restore NuGet packages (auto on open)

# 3. Set appsettings.json for local development
# {
#   "AgentOptions": {
#     "ServerUrl": "http://localhost",
#     "OrgId": "your-test-org-id",
#     "RegistrationSecret": "your-AGENT_SECRET-from-.env",
#     ...
#   }
# }

# 4. Build
dotnet build -c Debug

# 5. Run as console (not service) for development
dotnet run --project Agent/ProductivityAgent.csproj
```

---

## 3. Configuration

### .env File Structure

```ini
# Application
APP_NAME=ProductivitySuite
APP_ENV=local          # local | production
APP_DEBUG=true         # true for dev, false for prod
APP_URL=http://localhost
APP_TZ=UTC

# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=productivity_suite
DB_USER=ps_app
DB_PASSWORD=your_password

# JWT Keys (file paths)
JWT_PRIVATE_KEY=C:/wamp64/www/ProductivitySuite/config/keys/jwt_private.pem
JWT_PUBLIC_KEY=C:/wamp64/www/ProductivitySuite/config/keys/jwt_public.pem
JWT_ACCESS_TTL=900        # 15 minutes
JWT_REFRESH_TTL=2592000   # 30 days

# Agent
AGENT_SECRET=generate-32-bytes-random-hex
CRON_SECRET=generate-32-bytes-random-hex
LOG_LEVEL=debug           # warning in production

# Email (SMTP)
MAIL_DRIVER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_ENCRYPTION=tls
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_FROM=your@email.com
MAIL_FROM_NAME=CortexOne

# Google SSO (optional)
GOOGLE_CLIENT_ID=         # Leave empty to disable
GOOGLE_CLIENT_SECRET=

# Microsoft SSO (optional)
MICROSOFT_CLIENT_ID=      # Leave empty to disable
MICROSOFT_CLIENT_SECRET=
MICROSOFT_TENANT_ID=common

# CAPTCHA (IMPORTANT: replace before public launch)
TURNSTILE_SECRET=DISABLED   # Replace with real key from Cloudflare
TURNSTILE_SITE_KEY=
CAPTCHA_FAIL_OPEN=false

# Stripe (replace with live keys before billing goes live)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PLAN_1_MONTHLY=price_...
STRIPE_PRICE_PLAN_1_YEARLY=price_...
STRIPE_PRICE_PLAN_2_MONTHLY=price_...
STRIPE_PRICE_PLAN_2_YEARLY=price_...
STRIPE_PRICE_PLAN_3_MONTHLY=price_...
STRIPE_PRICE_PLAN_3_YEARLY=price_...
```

---

## 4. Coding Standards

### PHP (Backend)

**Style:** Procedural PHP with typed functions. No classes (except helper singletons). No framework.

```php
<?php
declare(strict_types=1);

// Always declare types
function getUserById(int $userId, int $orgId): ?array
{
    return Database::fetchOne(
        'SELECT id, username, email, role_id FROM users WHERE id = ? AND org_id = ? AND is_active = 1',
        [$userId, $orgId]
    );
}

// Always use prepared statements — never string interpolation in SQL
// BAD:  "SELECT * FROM users WHERE id = $userId"
// GOOD: "SELECT * FROM users WHERE id = ?" with [$userId]

// Always scope to org_id
function getDevices(int $orgId): array
{
    return Database::fetchAll(
        'SELECT * FROM devices WHERE org_id = ? ORDER BY hostname',
        [$orgId]
    );
}
```

**Response pattern:**
```php
// In every API handler:
$user = AuthMiddleware::requireAuth();       // Throws 401 if not authenticated
if (!RBAC::isAdmin($user)) {                // Role gate
    Response::error('Forbidden', 403);
}
$orgId = AuthMiddleware::getOrgId($user);   // Handles SA context switch

// Input validation
$input = json_decode(file_get_contents('php://input'), true) ?? [];
$name = trim($input['name'] ?? '');
if (empty($name)) {
    Response::error('Name is required', 400);
}

// Database operation
$id = Database::execute(
    'INSERT INTO departments (org_id, name) VALUES (?, ?)',
    [$orgId, $name]
);

// Audit log for mutations
AuditMiddleware::log($user, 'department.create', 'department', $id, null, ['name' => $name]);

// Success response
Response::success(['id' => $id, 'name' => $name], 201);
```

### JavaScript (Frontend)

```javascript
// Always use PSApp.api — never raw fetch
async function loadDevices() {
    const data = await PSApp.api.get('devices', { status: 'online' });
    // data is already parsed from Response::success wrapper

    // Always escape user-supplied content
    const html = data.map(d => `
        <div class="device-card">
            <span>${PSApp.esc(d.hostname)}</span>
            <span>${PSApp.esc(d.active_user)}</span>
        </div>
    `).join('');

    document.getElementById('device-list').innerHTML = html;
}

// Error handling
async function saveRule(payload) {
    try {
        const result = await PSApp.api.post('alerts/rules', payload);
        PSApp.toast('Alert rule saved', 'success');
    } catch (err) {
        PSApp.toast(err.message || 'Failed to save rule', 'error');
    }
}
```

### CSS

```css
/* Always use CSS custom properties — never hardcode colors or border-radius */
.my-component {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    color: var(--tx-1);
}

/* Secondary text */
.my-subtitle { color: var(--tx-2); }

/* Status colors */
.status-ok    { color: var(--green); }
.status-warn  { color: var(--amber); }
.status-error { color: var(--red); }
.status-info  { color: var(--blue); }
```

### Adding a New API Endpoint

1. Choose the correct resource file (e.g., `api/v1/devices.php`)
2. Add your route handler inside the file following existing pattern:
```php
// In devices.php
case 'GET:config':          // Parse from URI: GET /api/v1/devices/config
    $user = AuthMiddleware::requireAuth();
    if (!RBAC::isAdmin($user)) Response::error('Forbidden', 403);
    $orgId = AuthMiddleware::getOrgId($user);
    $config = Database::fetchOne('SELECT * FROM agent_configs WHERE org_id = ? AND device_id IS NULL', [$orgId]);
    Response::success($config);
    break;
```
3. If it's a new resource, create `api/v1/myresource.php` and add to `api/index.php` routes array
4. Update `API-Reference.md`

### Adding a New Dashboard Page

1. Create `dashboard/modules/mypage.php`
2. Add page name to `$allowedPages` in `dashboard/index.php`
3. If role-restricted, add to `$_adminOnly`, `$_superOnly`, or `$_managerPlus`
4. Add link to sidebar in `dashboard/templates/shell.php`
5. Update `Feature-Catalog.md`

### Adding a New Database Migration

```sql
-- File: database/migrations/NNN_description.sql
-- Date: YYYY-MM-DD
-- Description: What this migration does

-- MySQL 8.4 does not support IF NOT EXISTS for ADD COLUMN.
-- Use dynamic SQL:
SET @sql = IF(
    NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'productivity_suite'
        AND TABLE_NAME = 'users'
        AND COLUMN_NAME = 'new_column'
    ),
    'ALTER TABLE users ADD COLUMN new_column VARCHAR(255) NULL AFTER email',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
```

---

## 5. Architecture Overview (for New Engineers)

### The 3 Layers

```
1. Browser (vanilla JS)
   ↕ HTTPS JSON
2. PHP API (api/v1/*.php)
   ↕ PDO
3. MySQL (46 tables)
   ↑ (also: PHP dashboard renders HTML server-side)

Separately:
4. Windows Agent (.NET 8)
   ↕ HTTPS JSON to PHP API
   (same Layer 2)
```

### How Auth Works (Simplified)

- Dashboard: User logs in → gets JWT access token → JS stores in memory → sets PHP session via `/dashboard/index.php?action=set_session` → PHP reads `$_SESSION['user_id']` for subsequent page loads
- API: Every request needs either the PHP session cookie (PS_SESS) or an Authorization: Bearer {JWT} header
- Agent: Uses X-Device-Id + X-Device-Token headers (HMAC-SHA256 device token, not JWT)

### How Multi-Tenancy Works

Every table that contains customer data has an `org_id` column. Every query must include `WHERE org_id = ?`. The `AuthMiddleware::getOrgId($user)` function returns either `$user['org_id']` (normal user) or `$_SESSION['sa_org_id']` (super admin context switch). Never trust org_id from user input — always use the session/token value.

### How the Agent Works

15 workers run in parallel as .NET BackgroundService instances. Each has a `PeriodicTimer`. The `RegistrationWorker` runs first and sets a `ManualResetEventSlim` when complete — all other workers wait on this before starting. If the network is unavailable, failed uploads queue to SQLite (offline.db) via `OfflineSyncWorker`.

---

## 6. Debugging

### PHP / API Debugging

```php
// In .env: APP_DEBUG=true, LOG_LEVEL=debug

// View Apache error log (WAMP):
// C:/wamp64/logs/apache_error.log

// Add debug output to any PHP file:
error_log('Debug: ' . json_encode($variable));
// Output appears in apache_error.log

// Enable display_errors for a single file (dev only):
ini_set('display_errors', '1');
error_reporting(E_ALL);
```

### Agent Debugging

```
# Agent logs location:
C:\ProgramData\ProductivityAgent\Logs\agent_YYYYMMDD.log

# View in PowerShell:
Get-Content "C:\ProgramData\ProductivityAgent\Logs\agent_20260628.log" -Tail 100 -Wait

# Windows Event Log:
Get-EventLog -LogName Application -Source ProductivityAgentSvc -Newest 50

# Service status:
Get-Service ProductivityAgentSvc

# Run as console (not service) for interactive debugging:
cd "C:\Program Files\ProductivityAgent"
.\ProductivityAgent.exe --console
```

### Database Debugging

```sql
-- Check what's in heartbeats for a device:
SELECT * FROM heartbeats WHERE device_id = 123 ORDER BY recorded_at DESC LIMIT 10;

-- Check alert rules and recent firings:
SELECT r.*, a.triggered_at, a.status
FROM alert_rules r
LEFT JOIN alerts a ON a.rule_id = r.id AND a.triggered_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
WHERE r.org_id = 7;

-- Check productivity scores:
SELECT d.hostname, ps.score_date, ps.score, ps.grade
FROM productivity_scores ps
JOIN devices d ON d.id = ps.device_id
WHERE ps.org_id = 7
ORDER BY ps.score_date DESC, ps.score ASC;

-- Rate limit state:
SELECT * FROM api_rate_limits ORDER BY updated_at DESC LIMIT 20;
```

---

## 7. Security Checklist (Every PR)

- [ ] All SQL uses PDO prepared statements (no string concatenation with user data)
- [ ] All HTML output uses `PSApp.esc()` (JS) or `htmlspecialchars()` (PHP)
- [ ] Auth middleware called at the top of every protected handler
- [ ] org_id from session/token — never from user input
- [ ] RBAC check before any sensitive operation
- [ ] AuditMiddleware::log() called for all mutations
- [ ] No secrets in code (use .env)
- [ ] No new file uploads without extension validation
- [ ] Rate limiting in place for public endpoints

---

## 8. Logging

### PHP
```php
// Standard PHP error_log (goes to Apache error log)
error_log('[ProductivitySuite] ' . $message);

// Log levels (via LOG_LEVEL in .env)
// In production: LOG_LEVEL=warning → only log warnings and above
```

### Agent (Serilog)
```csharp
// Injected via DI
private readonly ILogger<HeartbeatWorker> _logger;

// Usage:
_logger.LogInformation("Heartbeat sent: CPU={Cpu}%, RAM={Ram}%", cpu, ram);
_logger.LogWarning("Heartbeat failed, queuing for offline sync");
_logger.LogError(ex, "Failed to register device");

// Output locations:
// File: C:\ProgramData\ProductivityAgent\Logs\agent_YYYYMMDD.log
// Windows Event Log: Application → ProductivityAgentSvc
```

---

## 9. Deployment

### Web Application

```bash
# 1. Pull latest code
git pull origin main

# 2. Run new migrations
mysql -u ps_app -p productivity_suite < database/migrations/NNN_new_migration.sql

# 3. Restart Apache to clear PHP opcache
net stop Apache2.4 && net start Apache2.4
# OR in WAMP: system tray → Restart All Services
```

### Agent Release

```bash
# 1. Build release binary
cd Agent/
dotnet publish -c Release -r win-x64 --self-contained true \
  -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true \
  -o publish/

# 2. Get SHA-256 hash
$hash = (Get-FileHash "publish\ProductivityAgent.exe" -Algorithm SHA256).Hash.ToLower()
Write-Host "SHA256: $hash"
Write-Host "Size: $((Get-Item 'publish\ProductivityAgent.exe').Length) bytes"

# 3. Update agent-meta.json
{
  "version": "1.2.0",
  "sha256": "<hash from step 2>",
  "size": <size from step 2>,
  "is_stable": true
}

# 4. Copy EXE to downloads/
cp publish/ProductivityAgent.exe ../../downloads/ProductivityAgent.exe

# 5. Insert new agent_versions row
INSERT INTO agent_versions (version, checksum_sha256, is_stable, is_mandatory, released_at)
VALUES ('1.2.0', '<sha256>', 1, 0, NOW());

# 6. Agents will self-update within 6 hours
```

---

## 10. Contribution Workflow

### Branching Strategy (Recommended — not enforced by repository)

```
main              ← Production-ready code
├── develop       ← Integration branch
├── feature/*     ← New features (feature/employee-portal)
├── fix/*         ← Bug fixes (fix/alert-cooldown-race)
└── hotfix/*      ← Production emergencies (hotfix/login-lockout)
```

### Pull Request Checklist

Before submitting a PR:

- [ ] Code follows PHP/JS/CSS standards in this guide
- [ ] No hardcoded secrets, credentials, or org_id values
- [ ] SQL uses PDO prepared statements
- [ ] HTML output escaped
- [ ] Auth middleware called
- [ ] AuditMiddleware called for mutations
- [ ] New API endpoint documented in API-Reference.md
- [ ] New feature documented in Feature-Catalog.md
- [ ] New page added to `$allowedPages` in dashboard/index.php
- [ ] Database migration written using dynamic SQL (IF NOT EXISTS pattern)
- [ ] .env.example updated if new env vars added

### Permanent Constraint

> **DO NOT MODIFY** (requires explicit owner approval):
> - Database schema for existing tables
> - API contracts (existing endpoint signatures, response shapes)
> - Authentication and authorisation logic
> - RBAC role definitions
> - Telemetry collection intervals and data structures
> - Productivity score calculation algorithm
> - Subscription pricing logic
> - Registration flow
> - Multi-tenant data isolation (org_id scoping)
> - Stripe billing integration
>
> **UI/UX changes to dashboard modules are safe.** New API endpoints are safe. New tables are safe (via migrations). Changing existing core logic is not.

---

## 11. Future Development Recommendations

Listed in priority order. See [Roadmap.md](Roadmap.md) for full details.

1. **Enable Cloudflare Turnstile** — 30 minutes of work; replace `DISABLED` with real key in .env
2. **Write automated tests** — PHPUnit for API endpoints; priority: auth, agent, productivity scoring
3. **Complete MFA flow** — Schema exists; build TOTP enrollment and verify UI
4. **Complete billing UI** — Stripe webhook handler exists; build plan change, invoice list UI
5. **Move to production infrastructure** — Off WAMP, onto Windows Server 2022 or Ubuntu + nginx
6. **Move file storage to S3** — Replace `/storage/` local paths with S3 SDK calls
7. **Mac OS agent** — New Go project; reuse same API surface as Windows agent
8. **OpenAPI spec** — Document all 39 resource files as OpenAPI 3.0
