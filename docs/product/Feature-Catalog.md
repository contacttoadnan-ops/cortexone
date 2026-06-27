# CortexOne — Feature Catalog

> **Audience:** Product Managers, Engineers, Sales Engineers, CTOs  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Product-Bible.md](Product-Bible.md) · [API-Reference.md](API-Reference.md) · [Roadmap.md](Roadmap.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from codebase reverse-engineering |
| 1.1 | 2026-06-28 | Corrected OAuth terminology (PKCE → state-based CSRF) |

---

## How to Read This Catalog

Each feature entry includes:
- **Status:** `Implemented` / `Partial` / `Not Implemented`
- **Business Value:** What problem it solves
- **Technical Implementation:** How it works (verified from code)
- **Related APIs:** Relevant endpoints
- **Related Tables:** Database tables involved
- **Limitations:** Known gaps or constraints

---

## Module 1: Fleet Monitoring

The foundation of CortexOne — all monitoring starts here.

---

### 1.1 Device Registration

**Status:** Implemented  
**Business Value:** Enrolls a Windows machine into the platform. Without registration, no monitoring occurs.  
**Implementation:** Agent RegistrationWorker POSTs hardware fingerprint to `/api/v1/agent/register`. Server creates `devices` row, returns `device_id` + HMAC-SHA256 `device_token`. Agent stores both in `appsettings.json`. ManualResetEventSlim released — all other 14 workers can start.  
**Related APIs:** `POST /agent/register`, `GET /devices`  
**Related Tables:** `devices`, `agent_configs`  
**Limitations:** Windows x64 only. Re-registration creates a duplicate device row if `device_uuid` changes (e.g. VM clone).

---

### 1.2 Real-Time Heartbeat Monitoring (60s)

**Status:** Implemented  
**Business Value:** Provides live device health — IT knows in under 60 seconds if a machine goes offline, spikes in CPU, or fills disk.  
**Implementation:** HeartbeatWorker uses `PeriodicTimer(60s)`. Collects: CPU % via `PerformanceCounter("Processor", "% Processor Time")`, RAM via WMI `Win32_OperatingSystem`, disk via `DriveInfo`, active user via WTS API, uptime via `Environment.TickCount64`. POSTs to `/agent/heartbeat`. Server inserts to RANGE-partitioned `heartbeats` table, evaluates alert rules.  
**Related APIs:** `POST /agent/heartbeat`  
**Related Tables:** `heartbeats`, `devices` (last_seen_at update)  
**Limitations:** Heartbeat interval is configurable per device (agent_configs) but defaults to 60s. RANGE partitions require manual monthly addition.

---

### 1.3 Application Usage Tracking

**Status:** Implemented  
**Business Value:** Shows which applications employees spend time in. Foundation for productivity scoring, shadow IT detection, and app categorisation.  
**Implementation:** AppUsageWorker monitors foreground window every 5 seconds using `GetForegroundWindow()` + `GetWindowThreadProcessId()`. Aggregates per-app duration and focus count. Uploads batch to `/agent/app-usage` every 5 minutes.  
**Related APIs:** `POST /agent/app-usage`, `GET /app-usage`  
**Related Tables:** `app_usage`, `productivity_scores`, `productivity_rules`  
**Limitations:** Only tracks foreground (focused) app. Background processes not tracked. App identification is by executable name — renames break history continuity.

---

### 1.4 Activity Session Tracking

**Status:** Implemented  
**Business Value:** Provides login/logout timestamps and active vs. idle time — the basis for attendance records and active time productivity calculation.  
**Implementation:** ActivitySessionWorker listens for WTS_SESSION_CHANGE events (logon, logoff, lock, unlock, disconnect, reconnect). Tracks session_start, session_end, active_seconds (keyboard/mouse detected), idle_seconds. POSTs to `/agent/activity-session`.  
**Related APIs:** `POST /agent/activity-session`, `GET /timesheets`  
**Related Tables:** `activity_sessions`, `attendance_records`  
**Limitations:** Multiple users on the same machine create multiple session rows — identity mapping may be needed for shared devices.

---

### 1.5 URL / Web History Tracking

**Status:** Implemented  
**Business Value:** Shows what websites employees visit and for how long. Identifies time wasted on non-work sites. Works without browser extension.  
**Implementation:** UrlHistoryWorker reads browser SQLite history files directly every 30 minutes:
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History`
- Firefox: `%APPDATA%\Mozilla\Firefox\Profiles\*.default\places.sqlite`
- Internet Explorer: registry-based history  
**Related APIs:** `POST /agent/url-history`, `GET /url-history`  
**Related Tables:** `url_history`  
**Limitations:** Does not work with private/incognito mode. History files may be locked by browser — agent copies to temp before reading. HTTPS sites show domain but not page path unless in title.

---

### 1.6 Keystroke and Mouse Tracking

**Status:** Implemented  
**Business Value:** Measures physical input activity as a proxy for engagement. Combined with idle detection. Privacy-preserving — counts only, no content captured.  
**Implementation:** KeystrokeWorker installs a low-level keyboard hook (`SetWindowsHookEx(WH_KEYBOARD_LL)`) in the user session (child process). Counts keystrokes and mouse clicks hourly. Aggregates to `input_stats` table.  
**Related APIs:** `POST /agent/keystrokes`, `GET /keystrokes`  
**Related Tables:** `input_stats`  
**Limitations:** Requires child process in user session (Session-0 isolation). Hook may be affected by other security software intercepting the hook chain.

---

### 1.7 Network Monitoring

**Status:** Implemented  
**Business Value:** Tracks IP address history (useful for detecting VPN usage, location changes, unusual ISPs) and per-adapter bandwidth usage.  
**Implementation:** MetricsWorker queries network adapters via `NetworkInterface.GetAllNetworkInterfaces()`. Reads BytesSent/BytesReceived from Statistics. IP changes detected on each heartbeat. GeoIP lookup on new IPs (library/provider not confirmed from repo).  
**Related APIs:** `GET /network`  
**Related Tables:** `ip_history`, `network_stats`  
**Limitations:** Bandwidth figures are cumulative counters — delta calculation needed for usage per interval. GeoIP accuracy varies for mobile/VPN users.

---

### 1.8 Screenshot Capture

**Status:** Implemented (opt-in)  
**Business Value:** Visual evidence of what was on the employee's screen. Used for compliance, remote audit, dispute resolution, and coaching.  
**Implementation:** ScreenshotWorker fires at configurable interval (default 15 min if enabled). In Session 0: spawns child process via `CreateProcessAsUser` with flag `--capture-screen {output_path} {quality}`. Child: `BitBlt(GetDC(HWND_DESKTOP), ...)` with `CAPTUREBLT`. Saved as JPEG at configurable quality (default 70%). Uploaded as base64 to `/agent/screenshot`. Stored at `/storage/screenshots/{org_id}/{device_id}/{timestamp}.jpg`.  
**Related APIs:** `POST /agent/screenshot`, `GET /screenshots`  
**Related Tables:** `screenshots`  
**Limitations:** Disabled by default. JPEG quality 70 balances size vs. readability. No multi-monitor stitching confirmed. Storage grows indefinitely — no automatic cleanup.

---

## Module 2: Productivity Intelligence

CortexOne's differentiating intelligence layer.

---

### 2.1 Productivity Scoring Engine (0–100, A–F)

**Status:** Implemented  
**Business Value:** Replaces subjective performance opinions with objective daily data. Managers get an A–F grade without manual input.  
**Implementation:** Four-component weighted algorithm:

| Component | Weight | Source |
|---|---|---|
| Productive time ratio | 40% | `app_usage` + `productivity_rules` |
| App quality score | 25% | `app_categories` (productivity_weight) |
| Active time ratio | 20% | `activity_sessions` (active_sec / expected_sec) |
| Focus score | 15% | Longest uninterrupted productive block ÷ 60 |

Score clamped 0–100. Grade: A(80+), B(65+), C(50+), D(35+), F(<35). Upserted to `productivity_scores` daily.  
**Related APIs:** `GET /productivity/scores`, `GET /productivity/summary`  
**Related Tables:** `productivity_scores`, `app_usage`, `productivity_rules`, `app_categories`, `activity_sessions`  
**Limitations:** Score quality depends on accurate `productivity_rules` being configured per org. Default rules (if any) are global — new orgs may have uncategorised apps.

---

### 2.2 App Categorisation Rules

**Status:** Implemented  
**Business Value:** Allows each organisation to define what "productive" means for their team. Coding tools = productive for developers; social media = unproductive for BPO agents.  
**Implementation:** `productivity_rules` table: `rule_type` (app/domain), `pattern` (wildcards), `category` (productive/neutral/unproductive), `priority`. Scoring engine evaluates rules in priority order for each app. App categories table stores `productivity_weight` (0.0–1.0) for granular scoring.  
**Related APIs:** `GET/POST/PUT/DELETE /productivity/rules`  
**Related Tables:** `productivity_rules`, `app_categories`  
**Limitations:** Pattern matching is string-based. No regex confirmed. Priority conflicts may produce unexpected results if rules overlap.

---

### 2.3 Risk Matrix (Healthy / Watch / At-Risk)

**Status:** Implemented  
**Business Value:** At-a-glance segmentation for managers. Instead of reviewing 200 individual scores, the risk matrix shows which employees need attention today.  
**Implementation:** Frontend segments employees into three groups based on `productivity_scores.score`:
- Healthy: score ≥ 65 (B or above)
- Watch: 35 ≤ score < 65 (C or D)
- At-Risk: score < 35 (F)

Displayed on executive dashboard and manager view.  
**Related APIs:** `GET /productivity/summary`  
**Related Tables:** `productivity_scores`

---

### 2.4 Executive Dashboard

**Status:** Implemented  
**Business Value:** Single-page KPI summary for operations directors and C-suite. No drill-down needed for daily monitoring.  
**Implementation:** `dashboard/modules/executive.php`. Aggregates: fleet health counts (online/offline/idle), productivity averages, alert counts by severity, anomaly counts, leave pending count, top productive/unproductive employees.  
**Related APIs:** Multiple read endpoints  
**Related Tables:** `devices`, `productivity_scores`, `alerts`, `anomalies`, `leave_requests`

---

## Module 3: Alert Engine

---

### 3.1 Threshold-Based Alert Rules

**Status:** Implemented  
**Business Value:** Proactive incident response. IT is notified before disk fills, CPU overloads, or machines go offline — before users call the helpdesk.  
**Implementation:** `alert_rules` defines: metric_type, condition_op (gt/lt/gte/lte/eq), threshold_value, duration_seconds, cooldown_minutes, severity, notify_emails, webhook_id. After each heartbeat insert, server evaluates all active rules for that org. If threshold exceeded for duration_seconds and cooldown passed: INSERT alert, dispatch notifications.  
**Related APIs:** `GET/POST/PUT/DELETE /alerts/rules`, `GET /alerts`  
**Related Tables:** `alert_rules`, `alerts`  
**Limitations:** Alert evaluation is synchronous with heartbeat insert — may slow inserts if org has many rules. No confirmed deduplication if same metric fires multiple rules simultaneously.

---

### 3.2 Alert Presets

**Status:** Implemented  
**Business Value:** Reduces setup time. New orgs can activate monitoring in minutes with one-click presets.  
**Implementation:** Five presets in the UI: CPU > 90% for 5 min, RAM > 90% for 5 min, Disk > 95%, Device offline > 30 min, Idle > 120 min. Each creates an `alert_rules` row with sensible defaults.  
**Related APIs:** `POST /alerts/rules` (presets use same endpoint)

---

### 3.3 Alert Lifecycle Management

**Status:** Implemented  
**Business Value:** Tracks which alerts have been acknowledged and resolved. Creates accountability in the IT team.  
**Implementation:** `alerts.status` ENUM: `open` → `acknowledged` → `resolved`. Status transitions via `PUT /alerts/{id}`. `acknowledged_at` and `resolved_at` timestamps recorded. Alert history queryable with filters.  
**Related APIs:** `PUT /alerts/{id}`  
**Related Tables:** `alerts`

---

### 3.4 Multi-Channel Notifications

**Status:** Implemented  
**Business Value:** Reaches the right person in the right channel — email for formal incidents, Slack/Teams for instant awareness.  
**Implementation:** On alert insert: iterate `notify_emails` JSON array → SMTP email. If `webhook_id` set: POST to `webhooks.url` with event payload → log to `webhook_logs`.  
**Related Tables:** `webhooks`, `webhook_logs`  
**Limitations:** No automatic retry on failed webhook deliveries. Failed deliveries logged but not re-queued.

---

## Module 4: Anomaly Detection

---

### 4.1 Behavioural Baseline Engine

**Status:** Implemented  
**Business Value:** Personalised anomaly detection. Instead of a global threshold, each device has its own normal — reducing false positives for power users vs. occasional users.  
**Implementation:** `anomaly_baselines` table stores per-device rolling averages: avg_active_sec, avg_keystrokes, first_seen_time, last_seen_time, top_apps (JSON), avg_bandwidth_bytes. Baselines are updated daily.  
**Related Tables:** `anomaly_baselines`

---

### 4.2 Six Anomaly Types

**Status:** Implemented  
**Business Value:** Covers the most common risk scenarios: productivity drops, out-of-hours work, unknown applications, extended idle, location changes, and bandwidth spikes.

| Type | Trigger | Risk |
|---|---|---|
| `activity_drop` | Active seconds < 50% of baseline | Productivity / wellness concern |
| `after_hours` | Activity outside normal hours (± baseline) | Security / overwork |
| `unknown_app` | App not seen in last 30 days | Shadow IT / malware |
| `idle_surge` | Idle ratio > 2× baseline | Productivity concern |
| `location_change` | New country/city in ip_history | Security / compliance |
| `bandwidth_spike` | Bytes transferred > 3× baseline | Data exfiltration risk |

**Related APIs:** `GET /anomalies`, `PUT /anomalies/{id}`  
**Related Tables:** `anomalies`, `anomaly_baselines`  
**Limitations:** `unknown_app` threshold (30 days) is not per-org configurable from verified evidence. `location_change` depends on GeoIP accuracy.

---

## Module 5: HR & Time Management

CortexOne's unique differentiator — no other monitoring platform includes this.

---

### 5.1 Leave Request Workflow

**Status:** Implemented  
**Business Value:** Eliminates email-based leave tracking. One platform for employees to submit, managers to approve, HR to report.  
**Implementation:** Employee submits `POST /leave/requests` with leave_type_id, from_date, to_date, reason. Server validates dates against existing requests and balance. Creates `leave_requests` row (status=pending). Webhook event `leave_requested` fires. Manager reviews via `PUT /leave/requests/{id}` (status=approved/rejected). On approval: `leave_balances.used_days` decremented.  
**Related APIs:** `GET/POST/PUT /leave/requests`  
**Related Tables:** `leave_requests`, `leave_types`, `leave_balances`  
**Limitations:** Multi-day leave crossing month boundary validation not verified. No half-day leave type confirmed in schema.

---

### 5.2 Leave Types and Balances

**Status:** Implemented  
**Business Value:** Different leave types (annual, sick, unpaid, compassionate) have different entitlements and rules. Balances auto-track throughout the year.  
**Implementation:** Per-org `leave_types` with `default_days_per_year` and `is_paid`. Per-user/type/year `leave_balances` with `total_days`, `used_days`, `carried_forward`. Admin can adjust balances manually.  
**Related APIs:** `GET/POST/PUT/DELETE /leave/types`, `GET /leave/balances`  
**Related Tables:** `leave_types`, `leave_balances`

---

### 5.3 Holiday Calendar

**Status:** Implemented  
**Business Value:** Public holidays excluded from leave day counts. Accurate attendance baseline.  
**Implementation:** `dashboard/modules/holiday-calendar.php`. Per-org holiday dates stored in `system_config` or dedicated table. Leave day calculation skips holidays and weekends.  
**Related APIs:** `GET /leave/holidays` (implied)  
**Limitations:** Public holiday source (manual entry vs. API) not confirmed from verified evidence.

---

### 5.4 Shift Scheduling

**Status:** Implemented  
**Business Value:** Defines expected work hours per device. Without schedules, productivity scoring uses organisation defaults. With schedules, scoring uses the actual expected hours for each employee's role.  
**Implementation:** `work_schedules` (name, timezone, is_default) → `schedule_shifts` (per-day start/end time, is_working_day) → `device_schedules` (device→schedule mapping). Expected hours used in active_ratio component of productivity score.  
**Related APIs:** `GET/POST/PUT/DELETE /scheduling/schedules`, `POST /scheduling/assignments`  
**Related Tables:** `work_schedules`, `schedule_shifts`, `device_schedules`

---

### 5.5 Timesheet Module

**Status:** Implemented  
**Business Value:** Replaces manual timesheet entry with device activity data. Actual keyboard/mouse active time becomes the timesheet.  
**Implementation:** `dashboard/modules/timesheets.php`. Aggregates `activity_sessions.active_seconds` per device per day per user. Displays as timesheet grid. Manual adjustments via `timesheets` API.  
**Related APIs:** `GET /timesheets`  
**Related Tables:** `activity_sessions`, `attendance_records`

---

### 5.6 Payroll Export

**Status:** Implemented  
**Business Value:** Eliminates manual payroll preparation. One click exports QuickBooks or Xero formatted CSV.  
**Implementation:** `GET /payroll/export` with `format=quickbooks|xero|csv` parameter. Server queries timesheet data for the requested period, formats as CSV per target system's import spec. Returns as file download.  
**Related APIs:** `GET /payroll`, `GET /payroll/export`  
**Related Tables:** `activity_sessions`, `attendance_records`  
**Limitations:** Export format tested against QuickBooks/Xero import format at development time — may need updating if platforms change their import schema.

---

### 5.7 Overtime Tracking

**Status:** Implemented  
**Business Value:** Automatically calculates overtime based on daily/weekly limits. Ensures accurate pay and compliance with labour laws.  
**Implementation:** `GET /payroll/overtime`. Org-level overtime rules (daily limit hours, weekly limit hours, overtime multiplier) stored in `system_config`. Active seconds vs. scheduled hours compared; excess flagged and multiplied.  
**Related APIs:** `GET /payroll/overtime`  
**Related Tables:** `attendance_records`, `system_config`

---

## Module 6: Advanced Monitoring (Phase 3)

All features in this module are disabled by default. Require explicit admin activation per device. Employee notification occurs on first capture.

---

### 6.1 Session Recording

**Status:** Implemented (disabled by default)  
**Business Value:** Full session replay for compliance-heavy industries (financial services, healthcare, legal). Audit trail beyond screenshots — managers can see the full working session as a video timeline.  
**Implementation:** VideoRecordingWorker captures JPEG frames at configurable intervals (default 5s). Per-session recording: `session_recordings` row created on logon, `recording_frames` row per JPEG, recording closed on logoff. Playback UI: `dashboard/modules/recordings.php` shows timeline with frame scrubber and speed control (0.5x/1x/2x/4x).  
**Related APIs:** `POST /agent/recording/start|frame|end`, `GET /recordings`, `GET /recordings/{id}/frames`  
**Related Tables:** `session_recordings`, `recording_frames`  
**Storage:** `/storage/recordings/{device_id}/{date}/{recording_id}/{frame}.jpg`  
**Limitations:** Storage grows rapidly at 5s intervals. No video encoding — individual JPEGs stored. No confirmed retention/deletion policy.

---

### 6.2 Webcam Snapshots

**Status:** Implemented (disabled by default)  
**Business Value:** Identity verification — confirms the registered employee is physically present at the workstation.  
**Implementation:** WebcamWorker uses WinRT `MediaCapture` + `MediaFrameReader`. Requires user-session child process (`--capture-webcam` flag). Captures 640×480 JPEG. Uploads to `/agent/webcam`. Gallery view in UI.  
**Related APIs:** `POST /agent/webcam`, `GET /webcam-snapshots`  
**Related Tables:** `webcam_snapshots`  
**Limitations:** Requires physical webcam on device. WinRT requires Windows 10 1903+ (already the minimum OS). Privacy regulations vary by jurisdiction — consult legal before enabling.

---

### 6.3 Location Tracking (GPS/WiFi/IP)

**Status:** Implemented (disabled by default)  
**Business Value:** Field workforce route tracking, proof of attendance at customer sites, compliance with location-based work requirements.  
**Implementation:** LocationWorker uses WinRT `Geolocator` API (GPS and WiFi triangulation). Fallback: IP-based geolocation. Pings every 15 minutes (configurable). Route displayed on Leaflet.js map (OpenStreetMap tiles).  
**Related APIs:** `POST /agent/location`, `GET /location-pings`  
**Related Tables:** `location_pings`  
**Limitations:** GPS accuracy depends on hardware. Laptops may lack GPS — WiFi triangulation is less accurate. WinRT Geolocator requires user consent prompt on Windows 11.

---

## Module 7: Reporting

---

### 7.1 On-Demand Report Generation

**Status:** Implemented  
**Business Value:** Management needs evidence for decisions. Reports provide the data snapshot at any point in time.  
**Implementation:** `POST /reports` with type, date range, filters, format. Server queries relevant tables, generates file (PDF/Excel/CSV), stores at `/reports/generated/` with 7-day expiry. Response includes download URL.  
**Related APIs:** `POST /reports`, `GET /reports/download/{id}`  
**Related Tables:** `generated_reports`  
**Limitations:** Report generation is synchronous — large date ranges may time out. No async job queue for report generation.

---

### 7.2 Scheduled Reports

**Status:** Implemented  
**Business Value:** Weekly productivity summary delivered to manager inbox every Monday without manual action.  
**Implementation:** `scheduled_reports` table with `schedule_cron` expression. External cron caller hits `/api/v1/reports/run-scheduled` with `X-Cron-Secret`. Server finds due reports, generates, updates `next_run_at`, delivers.  
**Related APIs:** `GET/POST/PUT/DELETE /reports/scheduled`  
**Related Tables:** `scheduled_reports`, `generated_reports`  
**Limitations:** Delivery reliability depends on external cron caller uptime. No delivery confirmation receipt tracking beyond `last_run_at`.

---

## Module 8: Integration Hub

---

### 8.1 Webhook Engine

**Status:** Implemented  
**Business Value:** CortexOne events push data to any system — no polling required. Real-time integration with Slack, Teams, Zapier, Make.  
**Implementation:** `webhooks` table: platform, url, events JSON array. On any of 11 event types: query all org webhooks matching the event, POST JSON payload to each URL, log result to `webhook_logs`.  
**Related APIs:** `GET/POST/PUT/DELETE /webhooks`, `GET /webhooks/logs`  
**Related Tables:** `webhooks`, `webhook_logs`  
**Event types:** `alert_triggered`, `anomaly_detected`, `device_offline`, `device_online`, `leave_requested`, `leave_approved`, `leave_rejected`, `overtime_detected`, `task_completed`, `recording_completed`, `location_updated`  
**Limitations:** No automatic retry on delivery failure. Failed deliveries logged in `webhook_logs` with response code.

---

### 8.2 Accounting Integrations (QuickBooks, Xero)

**Status:** Implemented  
**Business Value:** Timesheet data → accounting system without manual re-entry.  
**Implementation:** Export via `POST /integrations/export/timesheet?format=quickbooks|xero`. Configured via `integration_configs` table (org-level credentials). Export logged to `export_logs`.  
**Limitations:** Format is CSV export, not live API sync (no OAuth to QuickBooks/Xero confirmed). Manual import step still required at accounting system.

---

### 8.3 Project Tool Exports (Jira, Asana, Trello)

**Status:** Implemented  
**Business Value:** Device activity and time linked to project work items.  
**Implementation:** Export task/activity data in platform-compatible format. Logged to `export_logs`.  
**Limitations:** Same as accounting — CSV/JSON export, not live two-way sync.

---

### 8.4 API Key Management

**Status:** Implemented  
**Business Value:** Third-party systems (custom dashboards, BI tools) can pull data programmatically.  
**Implementation:** `api_keys` table: `key_hash` (SHA-256 of raw key), `scopes` (JSON array), `is_active`, `expires_at`. Key shown once at creation. Scope enforcement on each API request.  
**Related APIs:** `GET/POST/DELETE /api-keys`  
**Related Tables:** `api_keys`

---

## Module 9: Multi-Tenant Administration

---

### 9.1 Organisation Management

**Status:** Implemented  
**Business Value:** Allows the Aptus Workforce team to manage all customer organisations from a single super_admin login.  
**Implementation:** `GET/POST/PUT/DELETE /organizations` restricted to `role_id = 1` (super_admin). Context switch: `?action=sa_set_org` stores `$_SESSION['sa_org_id']` — all subsequent queries use this org instead of the super_admin's own org.  
**Related Tables:** `organizations`

---

### 9.2 RBAC and Permission Management

**Status:** Implemented  
**Business Value:** Least-privilege access. IT manager can see all devices. HR manager can approve leave but cannot deploy agents.  
**Implementation:** `roles.permissions` JSON array. `RBAC::isAdmin()`, `RBAC::isSuperAdmin()`, `RBAC::isManager()`, `RBAC::hasPermission()`. Every page route and API endpoint enforces role check. `$_adminOnly`, `$_superOnly`, `$_managerPlus` arrays in `dashboard/index.php`.

---

### 9.3 Audit Log

**Status:** Implemented  
**Business Value:** Immutable compliance trail. Every admin action recorded — who did what, when, from where, before and after values.  
**Implementation:** `AuditMiddleware::log()` called from every mutation endpoint. Stores: user_id, action string, resource_type, resource_id, old_values (JSON), new_values (JSON), ip_address, user_agent, result, occurred_at. Never updated or deleted.  
**Related APIs:** `GET /audit`  
**Related Tables:** `audit_logs`

---

### 9.4 Identity Mapping

**Status:** Implemented  
**Business Value:** Shared Windows machines used by multiple employees need OS username → system user mapping for accurate attribution.  
**Implementation:** `dashboard/modules/identity.php`. `device_assignments` table maps `device_id` → `user_id`. `is_primary` flag marks the primary assigned user.  
**Related Tables:** `device_assignments`

---

### 9.5 Geofence Rules (IP-Based)

**Status:** Implemented  
**Business Value:** Block or alert when access comes from unexpected locations. Useful for financial services compliance and corporate policy enforcement.  
**Implementation:** `geofence_rules`: rule_type (allow/block), match_type (ip/cidr/country), value, action (alert/block/log), is_enabled.  
**Related APIs:** `GET/POST/PUT/DELETE /geofence`  
**Related Tables:** `geofence_rules`  
**Limitations:** Enforcement happens at the API/dashboard layer. Agent telemetry uploads are not geofence-gated (agent token auth only).

---

## Module 10: Billing & Subscription

---

### 10.1 Stripe Subscription

**Status:** Implemented (test keys only)  
**Business Value:** Revenue collection. Automatic seat-based recurring billing.  
**Implementation:** `billing.php` API. Stripe price IDs in `.env` for 6 plans (3 tiers × monthly/annual). `organizations.stripe_customer_id`. Stripe webhook handler: `POST /billing/stripe-webhook` with signature verification via `STRIPE_WEBHOOK_SECRET`. Handles: `payment_intent.succeeded`, `invoice.paid`, `customer.subscription.updated`, `customer.subscription.deleted`.  
**Related APIs:** `GET /billing`, `POST /billing/stripe-webhook`, `GET /billing/invoices`  
**Related Tables:** `organizations` (subscription_status, paid_until, seat_count), `subscription_events`  
**Limitations:** Stripe keys are test keys in `.env` (`sk_test_YOUR_SECRET_KEY_HERE`). Billing UI completeness not fully verified. Live keys must be configured before customer billing begins.

---

## Module 11: Deployment

---

### 11.1 Agent Install Package

**Status:** Implemented  
**Business Value:** Admins get a pre-configured agent ready to install — no manual configuration needed.  
**Implementation:** `GET /agent-download` generates a ZIP containing `ProductivityAgent.exe` (72 MB, SHA-256 verified), `appsettings.json` (pre-filled with OrgId, ServerUrl, RegistrationSecret), `install.ps1`, `README.txt`. Org-specific — every org's package has unique RegistrationSecret.  
**Related APIs:** `GET /agent-download`

---

### 11.2 Silent Deploy Script (PowerShell)

**Status:** Implemented  
**Business Value:** IT admins deploy to entire fleet with one command. Compatible with all major RMM platforms.  
**Implementation:** `Deploy-Silent.ps1` generated server-side with org credentials embedded. Script: stops existing service, downloads EXE from server, verifies SHA-256, copies to `C:\Program Files\ProductivityAgent\`, adds Defender exclusions (`Add-MpPreference -ExclusionPath`, `-ExclusionProcess`), adds outbound firewall rule (`New-NetFirewallRule`), creates Windows Service (`sc.exe create`), sets auto-restart (3 actions), starts service. Supports `-Uninstall` flag. `Deploy-Silent.bat` wrapper for non-PS admins.  
**RMM Compatibility:** NinjaOne, Datto, N-able, ConnectWise, Atera — paste deploy script into RMM agent script field.  
**Related APIs:** `GET /agent-download/scripts`

---

### 11.3 Agent Auto-Update

**Status:** Implemented  
**Business Value:** Agents stay current without manual IT intervention. Security patches and new features delivered automatically.  
**Implementation:** UpdateWorker polls `GET /agent-update/check` every 6 hours. If `update_available: true`: downloads new EXE, verifies SHA-256 (abort if mismatch), replaces binary, restarts service. Update history in `agent_update_history` table.  
**Related APIs:** `GET /agent-update/check`  
**Related Tables:** `agent_versions`, `agent_update_history`

---

## Module 12: SSO Authentication

---

### 12.1 Google OAuth 2.0

**Status:** Implemented (credentials required)  
**Business Value:** Frictionless registration and login for Google Workspace organisations. No separate password to manage.  
**Implementation:** OAuth 2.0 with state-based CSRF protection via `oauth.php`. Scopes: `openid email profile`. Userinfo: `googleapis.com/oauth2/v3/userinfo`. CSRF state stored in `oauth_states` table (64-char random token, 10-min TTL, single-use). On new user: redirect to `sso-complete` page. On existing user: create PHP session.  
**Related Tables:** `oauth_states`, `sso_configs`, `users` (auth_provider, auth_provider_id)  
**Limitations:** `GOOGLE_CLIENT_ID` is empty in `.env` — buttons show "Setup Required" badge. Requires Google Cloud Console setup.

---

### 12.2 Microsoft 365 SSO

**Status:** Implemented (credentials required)  
**Business Value:** Enterprise SSO for Microsoft 365 / Azure AD organisations.  
**Implementation:** Same OAuth flow, Microsoft Identity Platform. Graph API: `graph.microsoft.com/v1.0/me`. Tenant: configurable (default `common` — accepts any Microsoft account).  
**Limitations:** `MICROSOFT_CLIENT_ID` is empty in `.env`. Requires Azure App Registration.
