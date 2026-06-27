# CortexOne — Product Bible
### Master Product Handbook

> **Audience:** All stakeholders — executives, engineers, product managers, marketing, investors, AI employees  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Purpose:** Single authoritative reference linking all CortexOne documentation

---

## Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-06-28 | Documentation Team | Generated from full codebase reverse-engineering |

---

## Documentation Map

| Document | Audience | Purpose |
|---|---|---|
| **[Executive-Summary.md](Executive-Summary.md)** | Investors, Founders, C-Suite | 3-page business overview |
| **[Architecture.md](Architecture.md)** | CTOs, Engineers | Full technical architecture |
| **[Technology-Stack.md](Technology-Stack.md)** | Engineers, DevOps | Stack, libraries, versions |
| **[Database.md](Database.md)** | Engineers, DBAs | 46-table schema analysis |
| **[API-Reference.md](API-Reference.md)** | Engineers, Integration Developers | All verified API endpoints |
| **[Feature-Catalog.md](Feature-Catalog.md)** | PMs, Engineers, Sales | Every implemented feature |
| **[Roadmap.md](Roadmap.md)** | PMs, Executives, Engineers | What is done and what is next |
| **[Marketing-Guide.md](Marketing-Guide.md)** | Sales, Marketing | ICP, messaging, objection handling |
| **[Developer-Guide.md](Developer-Guide.md)** | Engineers | Onboarding, standards, contribution |
| **[Known-Limitations.md](Known-Limitations.md)** | Engineers, PMs, CTOs | Verified gaps and technical debt |

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Mission and Vision](#2-mission-and-vision)
3. [Business Objectives](#3-business-objectives)
4. [User Roles](#4-user-roles)
5. [Functional Overview](#5-functional-overview)
6. [Architecture Summary](#6-architecture-summary)
7. [Feature Inventory](#7-feature-inventory)
8. [Executive Overview](#8-executive-overview)
9. [Future Direction](#9-future-direction)
10. [Documentation Cross-References](#10-documentation-cross-references)

---

## 1. Product Overview

### What It Is

CortexOne (internal codebase: **ProductivitySuite**, live: **https://app.aptus.global**, branding: **Aptus Workforce**) is a multi-tenant, cloud-hosted **workforce monitoring and productivity intelligence platform** for Windows-based organisations.

It consists of two components:

**Component 1 — Dashboard (Web Application)**
- PHP 8.3 server-side rendered application
- 43 dashboard modules behind `dashboard/modules/`
- 39 REST API resource files under `api/v1/`
- Apache 2.4 on WAMP stack (Windows)
- MySQL 8.4 database, 46 tables

**Component 2 — Agent (Windows Service)**
- .NET 8 self-contained Windows Service (ProductivityAgent.exe)
- 15 BackgroundService workers running in parallel
- Deployed on employee Windows 10 1903+ machines
- Phones home to app.aptus.global every 60 seconds

### What It Does

| Layer | Capability |
|---|---|
| **Monitor** | Real-time device telemetry: CPU, RAM, disk, network, apps, URLs, keystrokes, screenshots, location |
| **Score** | Daily productivity score (0–100, A–F) per employee using a four-component weighted algorithm |
| **Alert** | Threshold-based alert engine with cooldown, multi-channel notifications, and anomaly detection |
| **Manage** | Leave requests, shift scheduling, timesheets, payroll export, attendance records |
| **Integrate** | 10 platforms: QuickBooks, Xero, Jira, Asana, Trello, Slack, Teams, Zapier, Make, QuickBooks Payroll |
| **Comply** | Immutable audit log, RBAC, geofence rules, JWT RS256 authentication |

---

## 2. Mission and Vision

### Mission
**To give organisations complete, honest, and actionable visibility into how their workforce operates — without replacing the human judgment required to lead people well.**

### Vision
**To become the operating system for workforce intelligence** — the single platform through which every organisation understands its people, devices, and productivity, and manages the entire employee lifecycle from login to payroll.

### Values (derived from product design)
- **Privacy by design** — Phase 3 monitoring (recording, webcam, location) is disabled by default and employee-notified
- **Data integrity** — Offline-first agent ensures no telemetry is lost; RANGE-partitioned heartbeats for scale
- **Security first** — RS256 JWT, bcrypt cost 12, PDO prepared statements, immutable audit log
- **Zero-friction deployment** — One PowerShell command, Defender exclusions automated, RMM-compatible

---

## 3. Business Objectives

1. **Revenue:** Grow monthly recurring revenue through per-seat SaaS subscriptions (Starter $3 / Pro $5 / Enterprise $8 per seat/month)
2. **Market:** Achieve product-market fit in BPO, IT services, and professional services — initial English-speaking markets
3. **Deployment:** Deploy agents across thousands of Windows endpoints at customer organisations
4. **Differentiation:** Maintain the only monitoring platform that includes full HR workflows (leave, scheduling, payroll) in one product
5. **Expansion:** Build Mac and Linux agents to unlock the remaining addressable market
6. **Enterprise:** Complete MFA enforcement and SAML 2.0 for enterprise buyers

---

## 4. User Roles

| Role | role_id | Scope | Key Capabilities |
|---|---|---|---|
| Super Admin | 1 | Entire platform | All orgs, billing, impersonation, org CRUD |
| Admin | 2 | Single organisation | All users, all devices, all config, agent download, billing, audit log |
| Manager | 3 | Their department(s) | Team reports, productivity scores, leave approval, executive dashboard |
| Employee | 4 | Own data only | Submit leave, view own balance, self-service portal (partial) |
| Agent (Device) | n/a | Single device | POST telemetry, read config, check updates |

> RBAC is enforced via `RBAC::isAdmin()`, `RBAC::isSuperAdmin()`, and permission string arrays on the `roles` table. Every API endpoint and page route enforces role checks. See [Architecture.md](Architecture.md) for full RBAC implementation details.

---

## 5. Functional Overview

### Module 1: Fleet Monitoring
Real-time telemetry from all registered Windows endpoints. 60-second heartbeat with CPU, RAM, disk, network, active user. Partitioned `heartbeats` table for performance at scale.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-1-fleet-monitoring)*

### Module 2: Productivity Intelligence
Daily algorithmic score per device/user. Four weighted components: productive time ratio (40%), app quality (25%), active ratio (20%), focus score (15%). Risk matrix segments employees into Healthy/Watch/At-Risk.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-2-productivity-intelligence)*

### Module 3: Alert Engine
Configurable threshold rules: metric_type, condition_op, threshold_value, duration_seconds, cooldown_minutes. Five presets: CPU, RAM, disk, offline, idle. Severity: warning/error/critical. Multi-channel: email, Slack, Teams, webhook.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-3-alert-engine)*

### Module 4: Anomaly Detection
Six anomaly types built on historical per-device baselines: `activity_drop`, `after_hours`, `unknown_app`, `idle_surge`, `location_change`, `bandwidth_spike`. Results in `anomalies` table with severity.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-4-anomaly-detection)*

### Module 5: HR & Time Management
Complete leave workflow (request → approve → balance deduct). Holiday calendar. Shift scheduling. Timesheet module. Payroll export (QuickBooks/Xero CSV). Overtime rules with multipliers.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-5-hr--time-management)*

### Module 6: Advanced Monitoring (Phase 3)
Session recording (JPEG frames → video timeline), webcam snapshots (640×480 JPEG), GPS/WiFi location pings. All disabled by default. Employee notification on first activation. Separate `session_recordings`, `recording_frames`, `webcam_snapshots`, `location_pings` tables.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-6-advanced-monitoring-phase-3)*

### Module 7: Reporting
On-demand and scheduled reports. Formats: PDF, Excel, CSV. 7-day file retention. Delivery: email, Slack, download. Scheduled via cron + `CRON_SECRET`.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-7-reporting)*

### Module 8: Integration Hub
10 platform integrations. 11 webhook event types. API key management (scoped, hashed). Export pipelines: QuickBooks, Xero, Jira, Asana, Trello. Notification channels: Slack, Teams, Zapier, Make.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-8-integration-hub)*

### Module 9: Multi-Tenant Administration
Organisation CRUD (super_admin only). Subscription status tracking. Context switching for support sessions. `organisations` table is the root entity for all data isolation.
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-9-multi-tenant-administration)*

### Module 10: Billing & Subscription
Stripe-powered subscription lifecycle. Three pricing tiers. Monthly and annual billing. Stripe webhook handler. Invoice records. Trial management (`trial_ends_at`).
→ *See [Feature-Catalog.md](Feature-Catalog.md#module-10-billing--subscription)*

---

## 6. Architecture Summary

```
┌─────────────────────────────────────────────────────┐
│                 app.aptus.global                     │
│                                                     │
│  ┌─────────────────┐    ┌─────────────────────────┐ │
│  │  Dashboard       │    │  REST API (api/v1/)     │ │
│  │  PHP 8.3         │    │  PHP 8.3, 39 files      │ │
│  │  43 modules      │    │  ~150+ endpoints        │ │
│  │  Apache 2.4      │    │  JWT RS256 auth         │ │
│  └────────┬─────────┘    └──────────┬──────────────┘ │
│           │                         │                │
│           └──────────┬──────────────┘                │
│                      │                               │
│             ┌────────▼─────────┐                     │
│             │   MySQL 8.4.7    │                     │
│             │  46 tables       │                     │
│             │  productivity_   │                     │
│             │  suite           │                     │
│             └──────────────────┘                     │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ HTTPS (TLS)
                         │ POST telemetry every 60s
                         │
┌─────────────────────────────────────────────────────┐
│            Employee Windows Machine                  │
│                                                     │
│  ProductivityAgentSvc (Windows Service, LocalSystem)│
│  .NET 8 / 15 BackgroundService workers              │
│  ┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐  │
│  │Heartbeat │ │AppUsage │ │Screen- │ │Offline   │  │
│  │Worker    │ │Worker   │ │shot    │ │Sync      │  │
│  │(60s)     │ │(5 min)  │ │Worker  │ │(SQLite)  │  │
│  └──────────┘ └─────────┘ └────────┘ └──────────┘  │
└─────────────────────────────────────────────────────┘
```

**Frontend:** Vanilla JS + PHP server-side rendering. No SPA framework. Bootstrap Icons. CSS custom properties.

**Backend:** Procedural PHP 8.3. No framework. PDO prepared statements. Helpers: JWT, Database, Response, AuthMiddleware, RBAC, RateLimiter, AuditMiddleware.

**Auth:** PHP session (`PS_SESS`, SameSite=Strict) for dashboard. JWT RS256 (Bearer) for API and agent. OAuth 2.0 PKCE flow for Google/Microsoft SSO.

**Deployment:** WAMP stack on Windows. Single server currently. MySQL on same host. Local file storage for screenshots/recordings.

> Full architecture detail: [Architecture.md](Architecture.md)

---

## 7. Feature Inventory

A complete feature list grouped by module is in [Feature-Catalog.md](Feature-Catalog.md). Summary:

| Category | Features |
|---|---|
| Core Monitoring | Heartbeat, app usage, activity sessions, keystroke/mouse, URL history, screenshots, network stats, IP history |
| Productivity | Scoring engine, app categorisation rules, risk matrix, anomaly detection, baselines, executive dashboard |
| HR Suite | Leave workflow, leave types/balances, holiday calendar, shift scheduling, timesheets, payroll export, overtime, attendance |
| Alerts | Threshold rules, presets, severity, cooldown, acknowledge/resolve, email/Slack/Teams/webhook |
| Advanced (Phase 3) | Session recording, session playback, webcam snapshots, GPS/WiFi location, route map |
| Admin | User CRUD, department management, RBAC, audit log, geofence rules, identity mapping, agent config |
| Integrations | 10 platforms, 11 webhook events, API keys, scheduled reports, report download |
| SSO | Google OAuth 2.0, Microsoft 365, email/password, JWT, refresh rotation, account lockout |
| Deployment | Silent PS1 + BAT scripts, SHA-256 verify, Defender exclusions, auto-update, offline cache, RMM compatible |
| Billing | Stripe subscription, 3 tiers, monthly/annual, webhook handler, trial management |

---

## 8. Executive Overview

CortexOne is a **production-grade, multi-tenant SaaS platform** with 18+ months of engineering investment. The full feature set is comparable to ActivTrak + Hubstaff + a dedicated leave management tool — at a fraction of the combined price.

**What sets CortexOne apart:**
1. Only monitoring platform with built-in HR workflows (leave, payroll, scheduling)
2. Session recording and webcam monitoring matched only by Teramind (enterprise-only)
3. RMM-compatible silent deployment with automated Defender exclusion — unique in the category
4. 11 webhook event types across 10 platforms — deepest integration coverage in the SMB segment

**Current state:** Live in production. Agent v1.1.0 deployed. 46-table database schema complete. Pre-launch checklist: re-enable CAPTCHA, complete MFA UI, move to production infrastructure.

**Revenue model:** Per-seat SaaS ($3/$5/$8/month). Stripe billing integrated. Three tiers: Starter, Pro, Enterprise.

> For investor presentation material, see [Executive-Summary.md](Executive-Summary.md) and [Marketing-Guide.md](Marketing-Guide.md).

---

## 9. Future Direction

Priority recommendations (not yet implemented — see [Roadmap.md](Roadmap.md)):

**Immediate (pre-launch blockers):**
- Enable Cloudflare Turnstile CAPTCHA
- Complete MFA enforcement UI
- Production infrastructure (off WAMP, onto Windows Server or Linux)

**Near-term (3–6 months):**
- Mac OS agent (Go-based)
- Cloud file storage (S3/Azure Blob)
- Employee self-service portal
- Live real-time monitoring view (SSE stream completion)

**Medium-term (6–12 months):**
- Linux agent
- SAML 2.0 enterprise SSO
- Mobile manager app (iOS/Android)
- OpenAPI specification for API v1
- Background job queue (replace cron-triggered reports)

**Long-term vision:**
- AI-powered workforce summaries (GPT/Claude natural language reports)
- Predictive productivity — flag at-risk employees before they drop
- Industry benchmarks marketplace
- BambooHR, Workday, SAP SuccessFactors connectors

---

## 10. Documentation Cross-References

| If you need to know... | Read... |
|---|---|
| Business case and market opportunity | [Executive-Summary.md](Executive-Summary.md) |
| Full technical architecture | [Architecture.md](Architecture.md) |
| Technology versions and dependencies | [Technology-Stack.md](Technology-Stack.md) |
| Database schema and table analysis | [Database.md](Database.md) |
| How to call the API | [API-Reference.md](API-Reference.md) |
| What features are implemented | [Feature-Catalog.md](Feature-Catalog.md) |
| What is done vs what is next | [Roadmap.md](Roadmap.md) |
| How to sell CortexOne | [Marketing-Guide.md](Marketing-Guide.md) |
| How to contribute code | [Developer-Guide.md](Developer-Guide.md) |
| What is broken or incomplete | [Known-Limitations.md](Known-Limitations.md) |

---

*This document is the master reference. All other documents in the `docs/` directory are subordinate to this handbook and should be read in the context it establishes.*
