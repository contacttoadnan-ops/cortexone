# CortexOne — Database Reference

> **Audience:** Engineers, Database Architects, CTOs  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Architecture.md](Architecture.md) · [API-Reference.md](API-Reference.md) · [Developer-Guide.md](Developer-Guide.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from schema.sql + migrations + DESCRIBE queries |
| 1.1 | 2026-06-28 | Added caveat on table count; added §2.1 listing tables referenced but not individually documented |

---

## Overview

| Property | Value |
|---|---|
| Database name | `productivity_suite` |
| Engine | MySQL 8.4.7 |
| Storage engine | InnoDB (all tables) |
| Character set | utf8mb4 |
| Collation | utf8mb4_unicode_ci |
| Total tables | 46 (verified from schema.sql; ERD section may list additional tables from migrations — reconcile against `SHOW TABLES` if count differs) |
| Partitioned tables | 1 (`heartbeats`, RANGE by month) |
| Root entity | `organizations` |
| Multi-tenancy | `org_id` FK on all customer-scoped tables |

---

## 1. Entity-Relationship Diagram (Markdown)

```
organizations (root)
│  id, name, slug, subscription_status, trial_ends_at, paid_until,
│  seat_count, plan_id, stripe_customer_id
│
├─► users (org_id FK)
│     id, org_id, role_id, department_id,
│     username, email, full_name, password_hash (nullable),
│     auth_provider, auth_provider_id,
│     failed_attempts, locked_until,
│     mfa_secret, mfa_enabled,
│     last_login_at, created_at
│     │
│     ├─► roles (role_id FK) ─────────────────────────────────────────┐
│     │     id, name, permissions (JSON)                              │
│     │                                                               │
│     └─► leave_requests (user_id FK)                                 │
│           id, org_id, user_id, leave_type_id,                      │
│           from_date, to_date, status, reason                       │
│           ├─► leave_types (leave_type_id FK)                       │
│           └─► leave_balances (user_id + leave_type_id FK)          │
│
├─► departments (org_id FK)
│     id, org_id, name, manager_user_id (FK → users.id)
│
├─► devices (org_id FK)
│     id, org_id, device_uuid, hostname, os_name, os_version,
│     cpu_model, ram_total_gb, agent_version, status,
│     last_seen_at, registered_at
│     │
│     ├─► heartbeats (device_id FK) [RANGE PARTITIONED by month]
│     │     id, device_id, recorded_at, cpu_usage_pct, ram_usage_pct,
│     │     disk_usage_pct, active_user, uptime_seconds, ip_address
│     │
│     ├─► app_usage (device_id FK)
│     │     id, device_id, recorded_date, app_name, app_path,
│     │     duration_seconds, focus_count, active_user
│     │
│     ├─► activity_sessions (device_id FK)
│     │     id, device_id, active_user, session_start, session_end,
│     │     active_seconds, idle_seconds
│     │
│     ├─► screenshots (device_id FK)
│     │     id, device_id, captured_at, file_path, file_size,
│     │     active_user
│     │
│     ├─► url_history (device_id FK)
│     │     id, device_id, url, domain, page_title, browser,
│     │     visited_at, duration_seconds, active_user
│     │
│     ├─► input_stats (device_id FK)
│     │     id, device_id, recorded_hour, keystroke_count,
│     │     mouse_click_count, words_typed
│     │
│     ├─► ip_history (device_id FK)
│     │     id, device_id, ip_address, ip_type, country, city,
│     │     isp, recorded_at
│     │
│     ├─► network_stats (device_id FK)
│     │     id, device_id, adapter, bytes_sent, bytes_recv,
│     │     recorded_at
│     │
│     ├─► device_metrics (device_id FK)
│     │     id, device_id, metric_type, metric_value, metric_unit,
│     │     recorded_at
│     │
│     ├─► device_events (device_id FK)
│     │     id, device_id, event_type, severity, title, description,
│     │     occurred_at
│     │
│     ├─► anomalies (device_id FK)
│     │     id, device_id, anomaly_type, severity, baseline_value,
│     │     actual_value, detected_at, acknowledged_at
│     │     └─► anomaly_baselines (device_id FK)
│     │           id, device_id, baseline_date,
│     │           avg_active_sec, top_apps (JSON)
│     │
│     ├─► session_recordings (device_id FK) [Phase 3]
│     │     id, device_id, started_at, ended_at, frame_count,
│     │     active_user
│     │     └─► recording_frames (recording_id FK)
│     │           id, recording_id, frame_index, file_path,
│     │           file_size, captured_at
│     │
│     ├─► webcam_snapshots (device_id FK) [Phase 3]
│     │     id, device_id, captured_at, file_path, file_size,
│     │     active_user
│     │
│     ├─► location_pings (device_id FK) [Phase 3]
│     │     id, device_id, pinged_at, latitude, longitude,
│     │     altitude_m, accuracy_m, source, active_user
│     │
│     ├─► agent_configs (device_id FK, nullable for org-level)
│     │     id, org_id, device_id (nullable),
│     │     heartbeat_interval_sec, screenshot_interval_sec,
│     │     recording_enabled, webcam_enabled, location_enabled
│     │
│     └─► device_assignments (device_id FK)
│           id, device_id, user_id, is_primary
│
├─► alert_rules (org_id FK)
│     id, org_id, name, metric_type, condition_op,
│     threshold_value, duration_seconds, cooldown_minutes,
│     severity, notify_emails, webhook_id, is_enabled
│     └─► alerts (rule_id + device_id FK)
│           id, rule_id, device_id, severity, status,
│           triggered_at, acknowledged_at, resolved_at,
│           message
│
├─► productivity_rules (org_id FK)
│     id, org_id, rule_type, pattern, category, priority
│
├─► productivity_scores (org_id + device_id FK)
│     id, org_id, device_id, score_date, score, grade,
│     productive_minutes, idle_minutes, active_seconds,
│     calculated_at
│
├─► app_categories (org_id FK)
│     id, org_id, app_name, category, productivity_weight
│
├─► work_schedules (org_id FK)
│     id, org_id, name, timezone, is_default
│     └─► schedule_shifts (schedule_id FK)
│           id, schedule_id, day_of_week, start_time, end_time
│     └─► device_schedules (device_id FK)
│           device_id (PK), schedule_id
│
├─► attendance_records (org_id + device_id FK)
│     id, org_id, device_id, user_id, date,
│     first_seen_at, last_seen_at, total_active_sec
│
├─► projects (org_id FK)
│     id, org_id, name, status, start_date, end_date,
│     description
│     └─► project_devices (project_id + device_id FK)
│           id, project_id, device_id
│
├─► webhooks (org_id FK)
│     id, org_id, platform, url, events (JSON),
│     enabled, created_at
│     └─► webhook_logs (webhook_id FK)
│           id, webhook_id, event_type, payload (JSON),
│           response_code, fired_at, error_message
│
├─► scheduled_reports (org_id FK)
│     id, org_id, report_type, schedule_cron, format,
│     recipients (JSON), filters (JSON),
│     next_run_at, last_run_at, is_active
│     └─► generated_reports (org_id FK)
│           id, org_id, report_type, filename, file_path,
│           file_size, format, created_at, expires_at
│
├─► geofence_rules (org_id FK)
│     id, org_id, rule_type, match_type, value,
│     action, is_enabled
│
├─► api_keys (org_id FK)
│     id, org_id, name, key_hash, key_prefix,
│     scopes (JSON), is_active, last_used_at,
│     created_at, expires_at
│
├─► integration_configs (org_id FK)
│     id, org_id, platform, config (JSON), is_enabled,
│     created_at, updated_at
│
├─► export_logs (org_id FK)
│     id, org_id, export_type, platform, period,
│     record_count, exported_at, exported_by
│
├─► sso_configs (org_id FK)
│     id, org_id, provider, allowed_domains (JSON),
│     is_enabled
│
├─► audit_logs (org_id + user_id FK)
│     id, org_id, user_id, action, resource_type,
│     resource_id, old_values (JSON), new_values (JSON),
│     ip_address, user_agent, result, occurred_at
│
├─► system_config (org_id FK)
│     id, org_id, config_key, config_value, updated_at
│
└─► [Auth / Platform tables - no org_id]
      ├─► auth_tokens (user_id FK)
      │     id, user_id, token_hash, token_type,
      │     expires_at, revoked, created_at
      │
      ├─► pending_registrations
      │     id, token (UNIQUE), email, org_name,
      │     org_size, industry, full_name, username,
      │     password_hash, expires_at, created_at
      │
      ├─► registration_attempts
      │     id, ip_address, email_domain, status, created_at
      │
      ├─► oauth_states
      │     id, state (CHAR(64) UNIQUE), provider,
      │     intent, return_to, ip, created_at
      │
      ├─► agent_versions
      │     id, version, checksum_sha256, download_url,
      │     is_stable, is_mandatory, min_os_version,
      │     release_notes, released_at
      │
      ├─► agent_update_history
      │     id, device_id, from_version, to_version,
      │     status, started_at, completed_at
      │
      └─► api_rate_limits
            identifier, endpoint, request_count,
            window_start, updated_at
```

---

## 2. Table-by-Table Analysis

### `organizations`
**Purpose:** Root multi-tenant entity. Every other table with `org_id` FK descends from this.

| Column | Type | Notes |
|---|---|---|
| `id` | INT UNSIGNED PK | Auto-increment |
| `name` | VARCHAR(255) | Display name |
| `slug` | VARCHAR(100) UNIQUE | URL-safe identifier |
| `subscription_status` | ENUM | `trial`, `active`, `past_due`, `cancelled`, `suspended` |
| `trial_ends_at` | DATETIME NULL | Trial expiry |
| `paid_until` | DATETIME NULL | Last paid period end |
| `seat_count` | INT | Licensed seats |
| `plan_id` | INT | 1=Starter, 2=Pro, 3=Enterprise |
| `stripe_customer_id` | VARCHAR(255) NULL | Stripe customer object |
| `created_at` | DATETIME | Registration timestamp |

---

### `users`
**Purpose:** All dashboard staff (admins, managers, employees). Nullable `password_hash` supports SSO-only accounts.

| Column | Type | Notes |
|---|---|---|
| `id` | INT UNSIGNED PK | |
| `org_id` | INT FK → organizations | Multi-tenant scope |
| `role_id` | INT FK → roles | 1=super_admin, 2=admin, 3=manager, 4=employee |
| `department_id` | INT NULL FK → departments | |
| `username` | VARCHAR(100) | Unique per org |
| `email` | VARCHAR(255) | Unique globally |
| `full_name` | VARCHAR(255) | Display name |
| `password_hash` | VARCHAR(255) NULL | bcrypt cost 12; NULL for SSO-only accounts |
| `auth_provider` | ENUM | `local`, `google`, `microsoft` |
| `auth_provider_id` | VARCHAR(255) NULL | Provider's user ID (fast lookup) |
| `failed_attempts` | INT DEFAULT 0 | Incremented on wrong password |
| `locked_until` | DATETIME NULL | Set to NOW()+15min after 10 failures |
| `mfa_secret` | VARCHAR(255) NULL | TOTP base32 secret |
| `mfa_enabled` | TINYINT(1) | Default 0 |
| `last_login_at` | DATETIME NULL | |
| `is_active` | TINYINT(1) | Soft deactivation |
| `created_at` | DATETIME | |

**Indexes:** `(org_id, username)` UNIQUE, `(email)` UNIQUE, `(auth_provider, auth_provider_id)` (from migration `sso_oauth.sql`)

---

### `roles`
**Purpose:** RBAC role definitions with JSON permission arrays.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | 1=super_admin, 2=admin, 3=manager, 4=employee |
| `name` | VARCHAR(50) | Display name |
| `permissions` | JSON | Array of permission strings e.g. `["view_reports", "manage_users"]` |

---

### `departments`
**Purpose:** Organisational structure. Manager assigned per department.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `name` | VARCHAR(255) | |
| `manager_user_id` | INT NULL FK → users | Department manager |
| `created_at` | DATETIME | |

---

### `devices`
**Purpose:** All registered Windows endpoints. Central FK source for all telemetry tables.

| Column | Type | Notes |
|---|---|---|
| `id` | INT UNSIGNED PK | |
| `org_id` | INT FK → organizations | |
| `device_uuid` | VARCHAR(36) UNIQUE | Windows machine GUID |
| `hostname` | VARCHAR(255) | Computer name |
| `os_name` | VARCHAR(100) | e.g. "Windows 11 Pro" |
| `os_version` | VARCHAR(50) | e.g. "10.0.22621" |
| `cpu_model` | VARCHAR(255) | e.g. "Intel Core i7-12700" |
| `ram_total_gb` | DECIMAL(6,2) | |
| `mac_address` | VARCHAR(17) | Primary adapter |
| `agent_version` | VARCHAR(20) | e.g. "1.1.0" |
| `status` | ENUM | `online`, `offline`, `idle` |
| `last_seen_at` | DATETIME NULL | Updated on each heartbeat |
| `registered_at` | DATETIME | First registration |

---

### `heartbeats`
**Purpose:** 60-second telemetry snapshot per device. Most high-volume table. RANGE partitioned by year×100+month.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `recorded_at` | DATETIME | Timestamp from agent |
| `cpu_usage_pct` | DECIMAL(5,2) | 0.00–100.00 |
| `ram_usage_pct` | DECIMAL(5,2) | 0.00–100.00 |
| `disk_usage_pct` | DECIMAL(5,2) | Primary disk |
| `active_user` | VARCHAR(255) | Windows username |
| `uptime_seconds` | BIGINT | Seconds since boot |
| `ip_address` | VARCHAR(45) | IPv4 or IPv6 |

**Partitions:** `p2026_01` through `p2026_12`, plus `p_future` MAXVALUE catch-all.  
**Index:** `(device_id, recorded_at)` for time-range queries.

⚠️ **Maintenance required:** Monthly RANGE partitions must be added each year. No automation confirmed in repository.

---

### `app_usage`
**Purpose:** Per-device, per-day, per-application focus tracking. Used for productivity scoring.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `recorded_date` | DATE | Aggregation date |
| `app_name` | VARCHAR(255) | Executable name or window title |
| `app_path` | VARCHAR(500) NULL | Full executable path |
| `duration_seconds` | INT UNSIGNED | Total focus time |
| `focus_count` | INT UNSIGNED | Number of times brought to foreground |
| `active_user` | VARCHAR(255) | Windows username |

**Index:** `(device_id, recorded_date)`

---

### `activity_sessions`
**Purpose:** Login/logout activity periods per device/user. Basis for attendance records.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `active_user` | VARCHAR(255) | |
| `session_start` | DATETIME | WTS logon event |
| `session_end` | DATETIME NULL | WTS logoff or end-of-day |
| `active_seconds` | INT UNSIGNED | Keyboard/mouse active time |
| `idle_seconds` | INT UNSIGNED | No input detected |

---

### `screenshots`
**Purpose:** Metadata for screenshot files. Actual JPEGs stored at `/storage/screenshots/{org_id}/{device_id}/`.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `captured_at` | DATETIME | |
| `file_path` | VARCHAR(500) | Relative path under /storage/ |
| `file_size` | INT UNSIGNED | Bytes |
| `active_user` | VARCHAR(255) | |

---

### `url_history`
**Purpose:** Web browsing activity from browser history files.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `url` | TEXT | Full URL |
| `domain` | VARCHAR(255) | Extracted domain |
| `page_title` | VARCHAR(500) NULL | |
| `browser` | VARCHAR(50) | chrome, edge, firefox, ie |
| `visited_at` | DATETIME | |
| `duration_seconds` | INT UNSIGNED NULL | Time on page |
| `active_user` | VARCHAR(255) | |

---

### `input_stats`
**Purpose:** Hourly keyboard and mouse input aggregation. Privacy-preserving — counts only, no content.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `recorded_hour` | DATETIME | Truncated to hour |
| `keystroke_count` | INT UNSIGNED | Total key presses |
| `mouse_click_count` | INT UNSIGNED | Total mouse clicks |
| `words_typed` | INT UNSIGNED NULL | Estimated word count |

---

### `ip_history`
**Purpose:** Track IP address changes per device. Network forensics.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `ip_address` | VARCHAR(45) | IPv4 or IPv6 |
| `ip_type` | VARCHAR(20) | `public`, `private`, `vpn` |
| `country` | VARCHAR(100) NULL | GeoIP |
| `city` | VARCHAR(100) NULL | GeoIP |
| `isp` | VARCHAR(255) NULL | GeoIP |
| `recorded_at` | DATETIME | |

---

### `network_stats`
**Purpose:** Per-adapter bandwidth usage snapshots.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `adapter` | VARCHAR(255) | Network adapter name |
| `bytes_sent` | BIGINT UNSIGNED | Cumulative bytes sent |
| `bytes_recv` | BIGINT UNSIGNED | Cumulative bytes received |
| `recorded_at` | DATETIME | |

---

### `device_metrics`
**Purpose:** Generic key-value metric store for extensible device telemetry.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `metric_type` | VARCHAR(100) | e.g. `disk_io_read`, `network_latency` |
| `metric_value` | DECIMAL(15,4) | |
| `metric_unit` | VARCHAR(50) | e.g. `MB/s`, `ms` |
| `recorded_at` | DATETIME | |

---

### `device_events`
**Purpose:** Discrete events on a device (error, warning, info incidents).

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `event_type` | VARCHAR(100) | e.g. `disk_full`, `cpu_spike`, `agent_restart` |
| `severity` | ENUM | `info`, `warning`, `error`, `critical` |
| `title` | VARCHAR(255) | |
| `description` | TEXT NULL | |
| `occurred_at` | DATETIME | |

---

### `productivity_scores`
**Purpose:** Daily productivity score per device/user. Computed and cached here.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `org_id` | INT FK → organizations | |
| `device_id` | INT UNSIGNED FK → devices | |
| `score_date` | DATE | |
| `score` | DECIMAL(5,2) | 0.00–100.00 |
| `grade` | CHAR(1) | A/B/C/D/F |
| `productive_minutes` | INT UNSIGNED | |
| `idle_minutes` | INT UNSIGNED | |
| `active_seconds` | INT UNSIGNED | |
| `calculated_at` | DATETIME | |

**Index:** `(org_id, score_date)`, `UNIQUE (device_id, score_date)` (upsert target)

---

### `productivity_rules`
**Purpose:** Per-org app/domain categorisation rules for scoring engine.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `rule_type` | ENUM | `app`, `domain` |
| `pattern` | VARCHAR(255) | App name or domain pattern (wildcards) |
| `category` | ENUM | `productive`, `neutral`, `unproductive` |
| `priority` | INT | Rule evaluation order |

---

### `app_categories`
**Purpose:** Per-org productivity weight per application.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `app_name` | VARCHAR(255) | |
| `category` | VARCHAR(50) | |
| `productivity_weight` | DECIMAL(3,2) | 0.00–1.00 |

---

### `anomaly_baselines`
**Purpose:** Historical per-device behavioural baseline used for anomaly detection comparison.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `baseline_date` | DATE | Date of this baseline snapshot |
| `avg_active_sec` | INT UNSIGNED | Average daily active seconds (rolling) |
| `avg_keystrokes` | INT UNSIGNED NULL | |
| `first_seen_time` | TIME NULL | Typical first activity |
| `last_seen_time` | TIME NULL | Typical last activity |
| `top_apps` | JSON | Array of { app_name, avg_seconds } |
| `avg_bandwidth_bytes` | BIGINT NULL | |

---

### `anomalies`
**Purpose:** Detected anomaly instances with severity and acknowledgement lifecycle.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `anomaly_type` | ENUM | `activity_drop`, `after_hours`, `unknown_app`, `idle_surge`, `location_change`, `bandwidth_spike` |
| `severity` | ENUM | `low`, `medium`, `high`, `critical` |
| `baseline_value` | DECIMAL(15,4) | Expected value |
| `actual_value` | DECIMAL(15,4) | Observed value |
| `detected_at` | DATETIME | |
| `acknowledged_at` | DATETIME NULL | |
| `acknowledged_by` | INT NULL FK → users | |

---

### `alert_rules`
**Purpose:** Threshold rule definitions per organisation.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `name` | VARCHAR(255) | Rule display name |
| `metric_type` | VARCHAR(100) | `cpu_usage_pct`, `ram_usage_pct`, `disk_usage_pct`, `idle_minutes`, `offline_minutes` |
| `condition_op` | ENUM | `gt`, `lt`, `gte`, `lte`, `eq` |
| `threshold_value` | DECIMAL(15,4) | |
| `duration_seconds` | INT UNSIGNED | Sustained duration before firing |
| `cooldown_minutes` | INT UNSIGNED | Min time between firings |
| `severity` | ENUM | `warning`, `error`, `critical` |
| `notify_emails` | JSON NULL | Array of email addresses |
| `webhook_id` | INT NULL FK → webhooks | |
| `is_enabled` | TINYINT(1) DEFAULT 1 | |

---

### `alerts`
**Purpose:** Fired alert instances with lifecycle status.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `rule_id` | INT FK → alert_rules | |
| `device_id` | INT UNSIGNED FK → devices | |
| `severity` | ENUM | Copied from rule at fire time |
| `status` | ENUM | `open`, `acknowledged`, `resolved` |
| `message` | TEXT NULL | Human-readable alert message |
| `triggered_at` | DATETIME | |
| `acknowledged_at` | DATETIME NULL | |
| `resolved_at` | DATETIME NULL | |

---

### `geofence_rules`
**Purpose:** IP address allow/block rules for network-based access control.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `rule_type` | ENUM | `allow`, `block` |
| `match_type` | ENUM | `ip`, `cidr`, `country` |
| `value` | VARCHAR(100) | IP, CIDR range, or country code |
| `action` | ENUM | `alert`, `block`, `log` |
| `is_enabled` | TINYINT(1) | |

---

### `leave_types`
**Purpose:** Per-org leave categories.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `name` | VARCHAR(100) | e.g. "Annual Leave", "Sick Leave" |
| `default_days_per_year` | INT | |
| `is_paid` | TINYINT(1) | |

---

### `leave_requests`
**Purpose:** Individual leave request instances with approval workflow.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `user_id` | INT FK → users | Requester |
| `leave_type_id` | INT FK → leave_types | |
| `from_date` | DATE | |
| `to_date` | DATE | |
| `total_days` | DECIMAL(4,1) | Computed (excludes weekends/holidays) |
| `status` | ENUM | `pending`, `approved`, `rejected`, `cancelled` |
| `reason` | TEXT NULL | |
| `reviewed_by` | INT NULL FK → users | Manager who acted |
| `reviewed_at` | DATETIME NULL | |
| `created_at` | DATETIME | |

---

### `leave_balances`
**Purpose:** Per-user, per-type, per-year leave entitlement tracking.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `user_id` | INT FK → users | |
| `leave_type_id` | INT FK → leave_types | |
| `year` | YEAR | |
| `total_days` | DECIMAL(5,1) | Entitlement |
| `used_days` | DECIMAL(5,1) | Deducted on approval |
| `carried_forward` | DECIMAL(5,1) DEFAULT 0 | |

**Index:** `UNIQUE (user_id, leave_type_id, year)`

---

### `work_schedules`
**Purpose:** Shift schedule definitions per organisation.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK → organizations | |
| `name` | VARCHAR(255) | e.g. "Standard 9-5", "Night Shift" |
| `timezone` | VARCHAR(50) | IANA timezone string |
| `is_default` | TINYINT(1) | Applied to unassigned devices |

---

### `schedule_shifts`
**Purpose:** Per-day shift times for a schedule.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `schedule_id` | INT FK → work_schedules | |
| `day_of_week` | TINYINT | 0=Sunday ... 6=Saturday |
| `start_time` | TIME | |
| `end_time` | TIME | |
| `is_working_day` | TINYINT(1) DEFAULT 1 | |

---

### `device_schedules`
**Purpose:** Maps a device to a schedule. One device, one schedule.

| Column | Type | Notes |
|---|---|---|
| `device_id` | INT UNSIGNED PK (FK → devices) | |
| `schedule_id` | INT FK → work_schedules | |

---

### `attendance_records`
**Purpose:** Daily attendance summary per device/user derived from activity sessions.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `org_id` | INT FK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `user_id` | INT NULL FK → users | |
| `date` | DATE | |
| `first_seen_at` | DATETIME | |
| `last_seen_at` | DATETIME | |
| `total_active_sec` | INT UNSIGNED | |

**Index:** `UNIQUE (device_id, date)`

---

### `session_recordings` / `recording_frames`
**Purpose:** Phase 3 video session capture. Recordings are metadata; frames are individual JPEG file pointers.

`session_recordings`: `(id, device_id, started_at, ended_at, frame_count, active_user)`  
`recording_frames`: `(id, recording_id FK, frame_index, file_path, file_size, captured_at)`

Storage: `/storage/recordings/{device_id}/{date}/{recording_id}/{frame_index}.jpg`

---

### `webcam_snapshots`
**Purpose:** Phase 3 periodic webcam image metadata.

`(id, device_id FK, captured_at, file_path, file_size, active_user)`

Storage: `/storage/webcam/{device_id}/{date}/{filename}.jpg`

---

### `location_pings`
**Purpose:** Phase 3 GPS/WiFi/IP location per device.

| Column | Type | Notes |
|---|---|---|
| `id` | BIGINT UNSIGNED PK | |
| `device_id` | INT UNSIGNED FK → devices | |
| `pinged_at` | DATETIME | |
| `latitude` | DECIMAL(10,7) NULL | |
| `longitude` | DECIMAL(10,7) NULL | |
| `altitude_m` | DECIMAL(8,2) NULL | |
| `accuracy_m` | DECIMAL(8,2) NULL | |
| `source` | ENUM | `gps`, `wifi`, `ip` |
| `active_user` | VARCHAR(255) | |

---

### `webhooks` / `webhook_logs`
**Purpose:** Outbound webhook configuration and delivery audit.

`webhooks`: `(id, org_id, platform, url, events JSON, enabled, created_at)`  
`webhook_logs`: `(id, webhook_id FK, event_type, payload JSON, response_code, fired_at, error_message)`

---

### `auth_tokens`
**Purpose:** JWT token registry for revocation.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `user_id` | INT FK → users | |
| `token_hash` | VARCHAR(64) | SHA-256 of token |
| `token_type` | ENUM | `access`, `refresh` |
| `expires_at` | DATETIME | |
| `revoked` | TINYINT(1) DEFAULT 0 | |
| `created_at` | DATETIME | |

---

### `oauth_states`
**Purpose:** CSRF state tokens for OAuth 2.0 flow. One-time use, 10-minute TTL.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `state` | CHAR(64) UNIQUE | Cryptographically random |
| `provider` | ENUM | `google`, `microsoft` |
| `intent` | ENUM | `login`, `register` |
| `return_to` | VARCHAR(255) NULL | |
| `ip` | VARCHAR(45) | Client IP |
| `created_at` | DATETIME | TTL checked as created_at + 600s |

---

### `agent_versions`
**Purpose:** Agent release registry.

| Column | Type | Notes |
|---|---|---|
| `id` | INT PK | |
| `version` | VARCHAR(20) UNIQUE | e.g. "1.1.0" |
| `checksum_sha256` | CHAR(64) | Binary integrity check |
| `download_url` | VARCHAR(500) | Full URL or path |
| `is_stable` | TINYINT(1) | |
| `is_mandatory` | TINYINT(1) | Force update |
| `min_os_version` | VARCHAR(20) NULL | Minimum Windows build |
| `release_notes` | TEXT NULL | |
| `released_at` | DATETIME | |

**Current record:** version=`1.1.0`, checksum=`1d2233ab26cd5dd14b8dff0a3feab7191327be41e0cf5ab1e53d08c2542fdf1e`, size=75,332,344 bytes

---

### `api_rate_limits`
**Purpose:** Sliding window rate limiting state.

| Column | Type | Notes |
|---|---|---|
| `identifier` | VARCHAR(255) | IP or device_uuid |
| `endpoint` | VARCHAR(100) | API endpoint prefix |
| `request_count` | INT UNSIGNED | Requests in current window |
| `window_start` | DATETIME | Window start time |
| `updated_at` | DATETIME | |

**PK:** `(identifier, endpoint)`

---

## 2.1 Tables Referenced But Not Individually Documented

The following tables appear in Feature-Catalog.md or Roadmap.md but do not have dedicated entries in the Table-by-Table Analysis above. They should be verified against `SHOW TABLES` and documented if present:

| Table | Referenced In | Action Required |
|---|---|---|
| `subscription_events` | Feature-Catalog.md §10.1, Roadmap.md | Verify existence; add analysis entry |
| `device_assignments` | ERD Section 1 | Verify existence; add analysis entry |
| `attendance_records` | ERD Section 1, Feature-Catalog §1.4 | Verify existence; add analysis entry |
| `project_devices` | ERD Section 1 | Verify existence; add analysis entry |
| `sso_configs` | ERD Section 1, Feature-Catalog §12 | Verify existence; add analysis entry |
| `integration_configs` | ERD Section 1, Feature-Catalog §8 | Verify existence; add analysis entry |
| `export_logs` | ERD Section 1 | Verify existence; add analysis entry |
| `agent_update_history` | Auto-update flow | Verify existence; add analysis entry |

> Run `SHOW TABLES IN productivity_suite;` to confirm exact table list and resolve any ERD vs. schema.sql discrepancies.

---

## 3. Storage Strategy

| Data Type | Storage | Retention |
|---|---|---|
| Heartbeat telemetry | MySQL (partitioned) | Long-term (partition drops older) |
| App usage | MySQL | Indefinite |
| Screenshots | Filesystem `/storage/screenshots/` | Indefinite (manual cleanup) |
| Session recordings | Filesystem `/storage/recordings/` | Indefinite (manual cleanup) |
| Webcam snapshots | Filesystem `/storage/webcam/` | Indefinite (manual cleanup) |
| Reports | Filesystem `/reports/generated/` | 7 days (`expires_at`) |
| Audit logs | MySQL | Indefinite |
| OAuth state tokens | MySQL | 10 minutes (TTL checked on use) |
| Agent offline queue | SQLite on endpoint | Until synced or max 50 MB |

---

## 4. Potential Improvements

| Issue | Table(s) | Recommendation |
|---|---|---|
| Heartbeat partition maintenance is manual | `heartbeats` | Add stored procedure or cron to auto-add monthly partitions |
| No automatic cleanup of expired OAuth states | `oauth_states` | Scheduled DELETE WHERE created_at < NOW() - 600 |
| Screenshots stored locally with no quota | `screenshots` | Move to S3/Blob; add per-org storage quotas |
| `webhook_logs` has no automatic expiry | `webhook_logs` | Add `expires_at` and cleanup job (logs can grow unbounded) |
| `api_rate_limits` stale rows never cleaned | `api_rate_limits` | Scheduled DELETE WHERE window_start < NOW() - 3600 |
| `generated_reports` files not auto-deleted | `generated_reports` | Cron checks `expires_at` and deletes file + row |
| No FK on `recording_frames.recording_id` cascade | `recording_frames` | Add `ON DELETE CASCADE` |
| MFA `mfa_secret` stored in users table | `users` | Consider separate `mfa_credentials` table for security audit separation |
