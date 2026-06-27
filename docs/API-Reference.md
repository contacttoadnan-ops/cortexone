# CortexOne — API Reference

> **Audience:** Engineers, Integration Developers, API Consumers  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Base URL:** `https://app.aptus.global/api/v1`  
> **Related Documents:** [Architecture.md](Architecture.md) · [Database.md](Database.md) · [Developer-Guide.md](Developer-Guide.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from source code reverse-engineering |

---

## General Notes

### Authentication Methods

| Method | Used By | Header/Cookie |
|---|---|---|
| PHP Session | Dashboard users | Cookie: `PS_SESS` |
| JWT Bearer | API consumers, Agent (for some endpoints) | `Authorization: Bearer {token}` |
| Device Token | Windows agent | `X-Device-Id: {id}`, `X-Device-Token: {token}` |
| None | Public endpoints (auth, register, agent-update/check, oauth) | — |

### Response Format

```json
// Success
{ "success": true, "data": { ... } }

// Error
{ "success": false, "error": "message", "code": 400 }

// Paginated
{ "success": true, "data": [...], "meta": { "total": 100, "page": 1, "per_page": 25 } }
```

### HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | No content (DELETE success) |
| 400 | Bad request / validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (RBAC) |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 429 | Rate limit exceeded |
| 500 | Server error |

### Rate Limits

| Endpoint | Limit | Window |
|---|---|---|
| All endpoints (default) | 60 req | 60s |
| `POST /auth/login` | 10 req | 60s |
| `POST /auth/refresh` | 10 req | 60s |
| `GET /agent-download/*` | 30 req | 60s |
| `POST /register` | 5 req | 3600s |

---

## Authentication Endpoints

### POST /auth/login
**Purpose:** Authenticate a dashboard user with username/password  
**Auth required:** None  
**Rate limit:** 10/min  

**Request:**
```json
{
  "username": "john.smith",
  "password": "MyPassword123!"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 42,
      "username": "john.smith",
      "full_name": "John Smith",
      "email": "john@company.com",
      "role_id": 2,
      "org_id": 7
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
}
```

**Response 401 (wrong password):**
```json
{ "success": false, "error": "Invalid credentials" }
```

**Response 423 (locked):**
```json
{ "success": false, "error": "Account locked. Try again in 12 minutes." }
```

**Related tables:** `users`, `auth_tokens`  
**Security notes:** bcrypt verify cost 12. Failed attempts increment `users.failed_attempts`. After 10 failures, account locked for 15 minutes.

---

### POST /auth/refresh
**Purpose:** Exchange refresh token for new access + refresh token pair  
**Auth required:** Refresh token (Bearer)  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
}
```

**Security notes:** Old refresh token is revoked on issue of new one (token rotation). Token JTI stored in `auth_tokens` table.

---

### POST /auth/logout
**Purpose:** Invalidate current session and tokens  
**Auth required:** Session or Bearer  

**Response 200:**
```json
{ "success": true }
```

---

### POST /auth/forgot-password
**Purpose:** Send password reset email  
**Auth required:** None  

**Request:**
```json
{ "email": "john@company.com" }
```

**Response 200:** Always returns 200 regardless of whether email exists (security by design).

---

### POST /auth/reset-password
**Purpose:** Set new password using reset token  
**Auth required:** Reset token (from email link)  

**Request:**
```json
{
  "token": "64-char-hex-token",
  "password": "NewPassword123!",
  "password_confirmation": "NewPassword123!"
}
```

**Response 200:**
```json
{ "success": true, "message": "Password updated successfully." }
```

---

## Registration Endpoints

### POST /register
**Purpose:** Begin new organisation registration  
**Auth required:** None (Cloudflare Turnstile when enabled)  
**Rate limit:** 5/hour per IP  

**Request:**
```json
{
  "org_name": "Acme Corp",
  "org_size": "51-200",
  "industry": "IT Services",
  "full_name": "Jane Admin",
  "email": "jane@acmecorp.com",
  "username": "jane.admin",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Check your email to verify your account."
}
```

**Related tables:** `pending_registrations`, `registration_attempts`

---

### POST /register/verify
**Purpose:** Confirm email and activate org + admin user  
**Auth required:** Verification token (from email link)  

**Request:**
```json
{ "token": "64-char-hex-verification-token" }
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "org_id": 8,
    "user": { "id": 50, "username": "jane.admin", ... }
  }
}
```

---

## OAuth / SSO Endpoints

### GET /oauth/redirect/{provider}
**Purpose:** Begin OAuth 2.0 SSO flow  
**Auth required:** None  
**Providers:** `google`, `microsoft`  
**Query params:** `intent=login|register`  

**Response:** HTTP 302 redirect to provider consent screen  
**Related tables:** `oauth_states` (CSRF state stored)

---

### GET /oauth/callback/{provider}
**Purpose:** OAuth callback — exchanges code, creates/updates user, sets session  
**Auth required:** None (verified by state token)  
**Query params:** `code`, `state`  

**Responses:**
- Existing user: HTTP 302 → `/dashboard/index.php`
- New user: HTTP 302 → `/dashboard/?page=sso-complete`

**Related tables:** `oauth_states`, `users`, `organizations`

---

### GET /oauth/providers
**Purpose:** Return which SSO providers are configured in this deployment  
**Auth required:** None  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "providers": {
      "google": false,
      "microsoft": false
    }
  }
}
```

---

### GET /oauth/pending
**Purpose:** Return SSO pending user data (for sso-complete page)  
**Auth required:** PHP session with `sso_pending` key  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "email": "user@company.com",
    "full_name": "User Name",
    "provider": "google",
    "provider_id": "1234567890"
  }
}
```

---

### POST /oauth/complete
**Purpose:** Create new org and user after SSO registration  
**Auth required:** PHP session with `sso_pending` key  

**Request:**
```json
{
  "org_name": "Company Name",
  "org_size": "11-50"
}
```

**Response 200:**
```json
{ "success": true, "redirect": "/dashboard/index.php" }
```

---

## Agent Endpoints

All agent endpoints require `X-Device-Id` and `X-Device-Token` headers (except `/agent/register`).  
Registration requires `X-Org-Id` and `X-Registration-Secret` headers.

### POST /agent/register
**Purpose:** Register a new Windows device with the platform  
**Auth required:** `X-Registration-Secret` (from org's AGENT_SECRET)  

**Request:**
```json
{
  "device_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "hostname": "DESKTOP-ABC123",
  "os_name": "Windows 11 Pro",
  "os_version": "10.0.22621",
  "cpu_model": "Intel Core i7-12700H",
  "ram_total_gb": 16.0,
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "agent_version": "1.1.0"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "device_id": 123,
    "device_token": "hmac-sha256-token-string",
    "config": {
      "heartbeat_interval_sec": 60,
      "screenshot_interval_sec": 900,
      "screenshot_enabled": true,
      "recording_enabled": false,
      "webcam_enabled": false,
      "location_enabled": false
    }
  }
}
```

**Related tables:** `devices`, `agent_configs`

---

### POST /agent/heartbeat
**Purpose:** 60-second device vital signs upload  
**Auth required:** Device token  

**Request:**
```json
{
  "recorded_at": "2026-06-28T10:30:00Z",
  "cpu_usage_pct": 45.2,
  "ram_usage_pct": 67.8,
  "disk_usage_pct": 55.0,
  "active_user": "DESKTOP-ABC123\\john.smith",
  "uptime_seconds": 86400,
  "ip_address": "192.168.1.100"
}
```

**Response 200:**
```json
{ "success": true }
```

**Side effects:** Alert rule evaluation triggered after insert. Device `last_seen_at` updated.  
**Related tables:** `heartbeats`, `alert_rules`, `alerts`, `devices`

---

### POST /agent/app-usage
**Purpose:** Upload batch of application usage records for a day  
**Auth required:** Device token  

**Request:**
```json
[
  {
    "recorded_date": "2026-06-28",
    "app_name": "Microsoft Excel",
    "app_path": "C:\\Program Files\\Microsoft Office\\Excel.exe",
    "duration_seconds": 7200,
    "focus_count": 15,
    "active_user": "john.smith"
  }
]
```

**Response 200:**
```json
{ "success": true, "inserted": 5 }
```

**Related tables:** `app_usage`

---

### POST /agent/activity-session
**Purpose:** Upload an activity session (login → logout period)  
**Auth required:** Device token  

**Request:**
```json
{
  "active_user": "john.smith",
  "session_start": "2026-06-28T09:00:00Z",
  "session_end": "2026-06-28T17:30:00Z",
  "active_seconds": 24000,
  "idle_seconds": 6600
}
```

**Response 200:**
```json
{ "success": true }
```

---

### POST /agent/screenshot
**Purpose:** Upload a screenshot image  
**Auth required:** Device token  

**Request:**
```json
{
  "captured_at": "2026-06-28T10:15:00Z",
  "active_user": "john.smith",
  "image_base64": "/9j/4AAQSkZJRgAB...",
  "file_size": 45678
}
```

**Response 200:**
```json
{ "success": true, "screenshot_id": 9876 }
```

**Storage:** Saved to `/storage/screenshots/{org_id}/{device_id}/{timestamp}.jpg`  
**Related tables:** `screenshots`

---

### POST /agent/recording/start
**Purpose:** Begin a session recording  
**Auth required:** Device token  

**Request:**
```json
{ "started_at": "2026-06-28T09:00:00Z", "active_user": "john.smith" }
```

**Response 200:**
```json
{ "success": true, "recording_id": 42 }
```

---

### POST /agent/recording/frame
**Purpose:** Upload a single recording frame  
**Auth required:** Device token  

**Request:**
```json
{
  "recording_id": 42,
  "frame_index": 100,
  "captured_at": "2026-06-28T09:08:20Z",
  "image_base64": "/9j/4AAQ...",
  "file_size": 12345
}
```

---

### POST /agent/recording/end
**Purpose:** Close a session recording  
**Auth required:** Device token  

**Request:**
```json
{ "recording_id": 42, "ended_at": "2026-06-28T17:00:00Z", "frame_count": 2880 }
```

---

### POST /agent/webcam
**Purpose:** Upload a webcam snapshot (Phase 3)  
**Auth required:** Device token  

**Request:**
```json
{
  "captured_at": "2026-06-28T10:00:00Z",
  "active_user": "john.smith",
  "image_base64": "/9j/4AAQ...",
  "file_size": 89123
}
```

---

### POST /agent/location
**Purpose:** Upload a location ping (Phase 3)  
**Auth required:** Device token  

**Request:**
```json
{
  "pinged_at": "2026-06-28T10:00:00Z",
  "active_user": "john.smith",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "altitude_m": 15.0,
  "accuracy_m": 10.0,
  "source": "gps"
}
```

---

### GET /agent-update/check
**Purpose:** Check if a newer agent version is available  
**Auth required:** None (public endpoint)  
**Query params:** `version={current_version}`, `os_version={win_build}`  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "current_version": "1.1.0",
    "latest_version": "1.1.0",
    "is_mandatory": false,
    "update_available": false,
    "download_url": null,
    "sha256": null
  }
}
```

---

### GET /agent-download
**Purpose:** Download org-specific agent install package (ZIP)  
**Auth required:** JWT Bearer (admin+)  
**Rate limit:** 30/min  

**Response:** `application/zip` file stream  
**Contents:** `ProductivityAgent.exe`, `appsettings.json` (org-prefilled), `install.ps1`, `README.txt`

---

### GET /agent-download/scripts
**Purpose:** Download deployment scripts package (no binary)  
**Auth required:** JWT Bearer (admin+)  

**Response:** `application/zip` file stream  
**Contents:** `Deploy-Silent.ps1`, `Deploy-Silent.bat`, `README-scripts.txt`

---

## Device Endpoints

### GET /devices
**Purpose:** List all devices in the organisation  
**Auth required:** Admin+ (manager can view)  
**Query params:** `page`, `per_page`, `status`, `department_id`, `search`  

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "hostname": "DESKTOP-ABC123",
      "status": "online",
      "last_seen_at": "2026-06-28T10:30:00Z",
      "active_user": "john.smith",
      "cpu_usage_pct": 45.2,
      "ram_usage_pct": 67.8,
      "agent_version": "1.1.0"
    }
  ],
  "meta": { "total": 47, "page": 1, "per_page": 25 }
}
```

---

### GET /devices/{id}
**Purpose:** Get full device detail including latest telemetry  
**Auth required:** Admin+  

**Response 200:** Full device object including hardware specs, current metrics, assigned user.

---

### PUT /devices/{id}
**Purpose:** Update device (assign department, rename label)  
**Auth required:** Admin  

**Request:**
```json
{ "department_id": 3, "label": "Finance Laptop" }
```

---

### DELETE /devices/{id}
**Purpose:** Remove device from organisation  
**Auth required:** Admin  

**Security notes:** Does not delete telemetry history. Device token invalidated.

---

## Productivity Endpoints

### GET /productivity/scores
**Purpose:** Get daily productivity scores  
**Auth required:** Manager+  
**Query params:** `date_from`, `date_to`, `device_id`, `department_id`, `grade`  

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "device_id": 123,
      "hostname": "DESKTOP-ABC123",
      "user": "john.smith",
      "score_date": "2026-06-28",
      "score": 78.5,
      "grade": "B",
      "productive_minutes": 312,
      "idle_minutes": 48
    }
  ]
}
```

---

### GET /productivity/summary
**Purpose:** Organisation-wide productivity summary (for executive dashboard)  
**Auth required:** Manager+  
**Query params:** `date_from`, `date_to`, `department_id`  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "avg_score": 71.3,
    "healthy_count": 28,
    "watch_count": 12,
    "at_risk_count": 7,
    "total_devices": 47
  }
}
```

---

### GET /productivity/rules
### POST /productivity/rules
### PUT /productivity/rules/{id}
### DELETE /productivity/rules/{id}
**Purpose:** CRUD for app/domain categorisation rules  
**Auth required:** Admin  

**Rule object:**
```json
{
  "rule_type": "app",
  "pattern": "microsoft excel",
  "category": "productive",
  "priority": 10
}
```

---

## Alert Endpoints

### GET /alerts
**Purpose:** List fired alerts  
**Auth required:** Admin+  
**Query params:** `status`, `severity`, `device_id`, `date_from`, `date_to`  

### POST /alerts/rules
**Purpose:** Create an alert rule  
**Auth required:** Admin  

**Request:**
```json
{
  "name": "High CPU Alert",
  "metric_type": "cpu_usage_pct",
  "condition_op": "gt",
  "threshold_value": 90,
  "duration_seconds": 300,
  "cooldown_minutes": 60,
  "severity": "critical",
  "notify_emails": ["it@company.com"]
}
```

### PUT /alerts/{id}
**Purpose:** Acknowledge or resolve an alert  
**Auth required:** Admin+  

**Request:**
```json
{ "status": "acknowledged" }
```

### GET /alerts/rules
### PUT /alerts/rules/{id}
### DELETE /alerts/rules/{id}
**Purpose:** CRUD for alert rules. Auth: Admin.

---

## Anomaly Endpoints

### GET /anomalies
**Purpose:** List detected anomalies  
**Auth required:** Admin+  
**Query params:** `type`, `severity`, `device_id`, `acknowledged`, `date_from`, `date_to`  

### PUT /anomalies/{id}
**Purpose:** Acknowledge an anomaly  
**Auth required:** Admin+  

**Request:**
```json
{ "acknowledged": true, "note": "Investigated — false positive, employee was presenting" }
```

---

## Leave Management Endpoints

### GET /leave/requests
**Purpose:** List leave requests  
**Auth required:** Manager+ (sees team); Employee (sees own)  

### POST /leave/requests
**Purpose:** Submit a leave request  
**Auth required:** Authenticated user  

**Request:**
```json
{
  "leave_type_id": 1,
  "from_date": "2026-07-10",
  "to_date": "2026-07-14",
  "reason": "Family holiday"
}
```

### PUT /leave/requests/{id}
**Purpose:** Approve or reject a leave request  
**Auth required:** Manager+  

**Request:**
```json
{ "status": "approved" }
```

### GET /leave/types
### POST /leave/types
### PUT /leave/types/{id}
### DELETE /leave/types/{id}
**Purpose:** CRUD for leave type definitions. Auth: Admin.

### GET /leave/balances
**Purpose:** Get leave balances for users  
**Auth required:** Manager+ (all); Employee (own only)  

---

## Scheduling Endpoints

### GET /scheduling/schedules
### POST /scheduling/schedules
### PUT /scheduling/schedules/{id}
### DELETE /scheduling/schedules/{id}
**Purpose:** CRUD for work schedules and shifts. Auth: Admin.

### POST /scheduling/assignments
**Purpose:** Assign a device to a schedule  
**Auth required:** Admin  

---

## Payroll Endpoints

### GET /payroll
**Purpose:** Get payroll summary for a period  
**Auth required:** Admin  
**Query params:** `period_start`, `period_end`, `department_id`  

### GET /payroll/export
**Purpose:** Download payroll CSV (QuickBooks/Xero format)  
**Auth required:** Admin  
**Query params:** `period_start`, `period_end`, `format=quickbooks|xero|csv`  
**Response:** `text/csv` file download

### GET /payroll/overtime
**Purpose:** Get overtime records  
**Auth required:** Admin  

---

## Reports Endpoints

### POST /reports
**Purpose:** Generate a report  
**Auth required:** Admin+  

**Request:**
```json
{
  "report_type": "productivity_summary",
  "date_from": "2026-06-01",
  "date_to": "2026-06-28",
  "department_id": null,
  "format": "pdf"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "report_id": 55,
    "download_url": "/api/v1/reports/download/55"
  }
}
```

### GET /reports/download/{id}
**Purpose:** Download a generated report file  
**Auth required:** Admin+  
**Response:** File stream (PDF, CSV, or XLSX)

### GET /reports/scheduled
### POST /reports/scheduled
### PUT /reports/scheduled/{id}
### DELETE /reports/scheduled/{id}
**Purpose:** CRUD for scheduled reports. Auth: Admin.

---

## Integration Endpoints

### GET /integrations/config/{platform}
**Purpose:** Get integration configuration  
**Auth required:** Admin  
**Platforms:** `quickbooks`, `xero`, `jira`, `asana`, `trello`, `slack`, `teams`, `zapier`, `make`

### PUT /integrations/config/{platform}
**Purpose:** Save integration credentials/settings  
**Auth required:** Admin  

### POST /integrations/export/{type}
**Purpose:** Export data to a platform  
**Auth required:** Admin  
**Types:** `timesheet`, `tasks`, `payroll`  

### POST /integrations/zapier/test
**Purpose:** Test Zapier webhook connection  
**Auth required:** Admin  

---

## Webhook Endpoints

### GET /webhooks
### POST /webhooks
### PUT /webhooks/{id}
### DELETE /webhooks/{id}
**Purpose:** CRUD for outbound webhook configurations. Auth: Admin.

**Webhook object:**
```json
{
  "platform": "slack",
  "url": "https://hooks.slack.com/services/...",
  "events": ["alert_triggered", "device_offline", "anomaly_detected"],
  "enabled": true
}
```

### GET /webhooks/logs
**Purpose:** View webhook delivery history  
**Auth required:** Admin  

---

## API Key Endpoints

### GET /api-keys
### POST /api-keys
### DELETE /api-keys/{id}
**Purpose:** Manage API keys for external system access. Auth: Admin.

**Create request:**
```json
{
  "name": "Zapier Integration Key",
  "scopes": ["read:devices", "read:productivity", "read:alerts"],
  "expires_at": "2027-06-28"
}
```

**Response includes key value (shown only once at creation).**

---

## Recording Endpoints (Phase 3)

### GET /recordings
**Purpose:** List session recordings  
**Auth required:** Admin  
**Query params:** `device_id`, `date_from`, `date_to`, `active_user`  

### GET /recordings/{id}
**Purpose:** Get recording metadata and frame list  
**Auth required:** Admin  

### GET /recordings/{id}/frames/{index}
**Purpose:** Stream a recording frame JPEG  
**Auth required:** Admin  
**Response:** `image/jpeg`

### GET /webcam-snapshots
**Purpose:** List webcam snapshot metadata  
**Auth required:** Admin  

### GET /location-pings
**Purpose:** List location ping history  
**Auth required:** Admin  
**Query params:** `device_id`, `date_from`, `date_to`  

---

## Organisation Management (Super Admin Only)

### GET /organizations
### POST /organizations
### GET /organizations/{id}
### PUT /organizations/{id}
### DELETE /organizations/{id}
**Purpose:** CRUD for customer organisations. Auth: Super Admin (role_id = 1) only.

---

## Billing Endpoints

### GET /billing
**Purpose:** Get current subscription status  
**Auth required:** Admin  

**Response 200:**
```json
{
  "success": true,
  "data": {
    "plan_id": 2,
    "plan_name": "Pro",
    "status": "active",
    "seat_count": 25,
    "price_per_seat": 5.00,
    "paid_until": "2026-07-28",
    "stripe_customer_id": "cus_..."
  }
}
```

### POST /billing/stripe-webhook
**Purpose:** Receive Stripe events (payment_intent, invoice, subscription)  
**Auth required:** Stripe webhook signature (`STRIPE_WEBHOOK_SECRET`)  

### GET /billing/invoices
**Purpose:** List historical invoices  
**Auth required:** Admin  

---

## User Management Endpoints

### GET /users
### POST /users
### GET /users/{id}
### PUT /users/{id}
### DELETE /users/{id}
**Purpose:** CRUD for dashboard users within the organisation. Auth: Admin.

**Create request:**
```json
{
  "full_name": "New Manager",
  "email": "newmanager@company.com",
  "username": "new.manager",
  "role_id": 3,
  "department_id": 4,
  "password": "TempPass123!"
}
```

---

## Audit Log Endpoints

### GET /audit
**Purpose:** Query the immutable audit log  
**Auth required:** Admin  
**Query params:** `action`, `user_id`, `resource_type`, `date_from`, `date_to`, `page`  

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1001,
      "user_id": 42,
      "username": "john.smith",
      "action": "user.create",
      "resource_type": "user",
      "resource_id": 55,
      "old_values": null,
      "new_values": { "email": "new@company.com", "role_id": 3 },
      "ip_address": "203.0.113.5",
      "occurred_at": "2026-06-28T10:00:00Z"
    }
  ]
}
```

---

## Example Workflow: Deploy Agent and See First Productivity Score

```
1. Authenticate:
   POST /auth/login { username, password }
   ← access_token

2. Download agent package:
   GET /agent-download
   Authorization: Bearer {access_token}
   ← ZIP file

3. Install on endpoint:
   Run install.ps1 on Windows machine

4. Agent registers automatically:
   POST /agent/register (from agent)
   ← device_id, device_token

5. Monitor device appearing:
   GET /devices
   ← device with status: "online"

6. View first heartbeat data:
   GET /devices/{id}
   ← current cpu, ram, disk, active_user

7. Next day — check productivity score:
   GET /productivity/scores?date_from=2026-06-28&date_to=2026-06-28
   ← score: 74.2, grade: "B"

8. Set up CPU alert:
   POST /alerts/rules
   { metric_type: "cpu_usage_pct", condition_op: "gt", threshold_value: 85,
     duration_seconds: 300, severity: "warning" }

9. Configure Slack notifications:
   POST /webhooks
   { platform: "slack", url: "https://hooks.slack.com/...", events: ["alert_triggered"] }
```
