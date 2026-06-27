# CortexOne — Executive Summary

> **Audience:** Founders, Investors, C-Suite Executives  
> **Classification:** Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Product-Bible.md](Product-Bible.md) · [Architecture.md](Architecture.md) · [Marketing-Guide.md](Marketing-Guide.md) · [Roadmap.md](Roadmap.md)

---

## Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-06-28 | Documentation Team | Initial release from codebase reverse-engineering |

---

## 1. What CortexOne Is

CortexOne (internal codebase name: **ProductivitySuite**, live at **https://app.aptus.global**) is a multi-tenant, cloud-hosted **workforce monitoring and productivity intelligence platform**. It combines three disciplines into a single product:

- **IT Monitoring** — Real-time device telemetry (CPU, RAM, disk, network, application usage) from a lightweight Windows agent installed on every endpoint
- **Workforce Intelligence** — Algorithmic daily productivity scoring (0–100, A–F grade) per employee, anomaly detection, and risk segmentation
- **HR & Operations** — Leave management, shift scheduling, timesheet aggregation, payroll export, and integration with accounting and project management tools

The platform has two physical components: a **PHP 8.3 web dashboard** hosted at app.aptus.global and a **.NET 8 Windows service agent** (ProductivityAgent.exe, v1.1.0, 72 MB, self-contained) deployed silently on employee machines. No infrastructure is required at the customer site.

---

## 2. Business Problem Solved

The modern distributed workforce creates a fundamental visibility problem. Managers cannot see whether employees are actively working. IT teams cannot monitor device health without on-site access. HR departments track leave via email. Payroll requires manual timesheet reconciliation.

Existing tools are siloed: employee monitoring tools (Hubstaff, ActivTrak) do not include HR workflows. HR tools (BambooHR, Workday) do not include device monitoring. IT tools (SolarWinds, Ninja) do not include productivity intelligence.

CortexOne closes every gap in one platform:

| Gap | CortexOne Solution |
|---|---|
| No remote visibility | Agent collects 15+ data points per device every 60 seconds |
| Subjective performance reviews | Daily algorithmic score replaces opinion with data |
| IT blind spots | Threshold-based alert engine fires before failures escalate |
| Leave managed by email | Built-in request/approve/balance workflow |
| Payroll requires manual input | Actual device activity drives timesheet and payroll export |
| No audit trail | Immutable audit log on every admin action |
| Shadow IT, unknown apps | App categorisation and URL history per device |

---

## 3. Target Customers

**Ideal Customer Profile:**
- 20–500 employees on Windows devices
- Remote, hybrid, or distributed workforce
- Company-issued endpoints (not BYOD)
- Centralised IT management

**Primary Verticals:**
- Business Process Outsourcing (BPO) and call centres
- IT services and Managed Service Providers (MSPs)
- Professional services (legal, accounting, consulting)
- Financial services and insurance
- Logistics and field operations

**Buyer Personas:**
- **IT Manager** — needs fleet health, agent deployment, alert rules
- **Operations Director** — needs productivity scores, executive dashboard, payroll
- **HR Manager** — needs leave management, attendance, payroll export

---

## 4. Market Opportunity

The global employee monitoring and productivity software market exceeded **$5.9 billion in 2024** and is growing at approximately **12% CAGR**, driven by permanent shift to hybrid and remote work.

Primary competitors address sub-segments:

| Competitor | Focus | Gap |
|---|---|---|
| Hubstaff | Time tracking + payroll | No device monitoring, no anomaly detection |
| ActivTrak | Productivity analytics | No HR workflows, no payroll |
| Teramind | Security + monitoring | Enterprise-only pricing, complex deployment |
| Insightful | Workforce analytics | No HR, no payroll, no session recording |
| Time Doctor | Time tracking | No device monitoring, no alerting |

**CortexOne's market positioning:** The only platform to combine IT device monitoring + productivity intelligence + full HR workflows (leave, scheduling, payroll) in a single product at SMB-accessible pricing.

**Total Addressable Market (estimate):** 50 million Windows-based knowledge workers at companies of 20–500 employees in English-speaking markets.

**Serviceable Addressable Market (estimate):** 10 million seats in BPO, IT services, and professional services verticals — at $5/seat/month average, this represents $600M ARR potential.

---

## 5. Product Vision

> **To become the operating system for workforce intelligence** — the single platform through which every organisation understands how its people and devices work together, makes data-driven decisions about performance, and manages the entire employee lifecycle from login to payroll.

---

## 6. Competitive Positioning

CortexOne wins on **breadth** and **integration depth**:

**Category-unique features (verified from codebase):**
- Only monitoring platform with built-in **leave management, shift scheduling, and payroll export**
- Only platform with **RMM-compatible silent deployment** (Defender exclusions automated, compatible with NinjaOne, Datto, N-able, ConnectWise, Atera)
- **Phase 3 advanced monitoring** (session recording, webcam snapshots, GPS/WiFi location) available on opt-in — matched only by Teramind
- **11 webhook event types** across 10 integrations (QuickBooks, Xero, Jira, Asana, Trello, Slack, Teams, Zapier, Make) — more than any competitor

**Pricing advantage:**
- Starter: $3/seat/month
- Pro: $5/seat/month
- Enterprise: $8/seat/month

Compared to buying ActivTrak ($10) + Hubstaff ($7) + a leave management tool ($3) = **$20/seat/month**, CortexOne delivers the combined value at $8/seat/month maximum.

---

## 7. Core Value Proposition

**"Deploy in one command. See everything. Know who is working."**

1. **Zero-friction deployment** — One PowerShell command deploys the agent fleet-wide with Defender exclusions, firewall rules, and service registration automated
2. **Objective performance data** — Algorithmic daily score per employee eliminates guesswork from performance conversations
3. **Proactive operations** — Alert engine catches problems before they become incidents
4. **HR and IT in one** — Leave approvals, payroll exports, and device health from the same dashboard
5. **Complete integration** — Data flows to QuickBooks, Xero, Slack, Jira, Asana without manual export

---

## 8. Current Maturity

**Platform version:** 1.1.0 (agent) / Production  
**Live URL:** https://app.aptus.global  
**Infrastructure:** PHP 8.3 / Apache 2.4 / MySQL 8.4 / Windows (WAMP stack)

**Production-ready modules (verified):**
- Multi-tenant organisation management
- Device fleet monitoring (46 database tables, 150+ API endpoints)
- Real-time heartbeat telemetry at 60-second intervals
- Productivity scoring engine (0–100, four-component weighted algorithm)
- Anomaly detection (6 types, baseline-driven)
- Alert engine (threshold-based, cooldown, multi-channel)
- HR suite: leave management, holiday calendar, shift scheduling, timesheets, payroll export
- Integrations: 10 platforms, 11 webhook event types
- Phase 3 monitoring: session recording, webcam, GPS location (opt-in, disabled by default)
- Google OAuth 2.0 and Microsoft 365 SSO (code complete, credentials required)
- Silent deployment scripts (PowerShell + batch)
- Stripe billing (schema and webhook handler)

**Immediate pre-launch requirements:**
- Cloudflare Turnstile CAPTCHA is explicitly disabled (`TURNSTILE_SECRET=DISABLED`) — must be enabled before public traffic
- MFA enforcement UI is incomplete (schema present, flow not verified)
- Infrastructure requires upgrade from WAMP/single-server to production-grade hosting

---

## 9. Strategic Direction

**90-day priorities (recommendation):**
1. Enable Cloudflare Turnstile CAPTCHA before public launch
2. Complete MFA enforcement for enterprise buyers
3. Move file storage to S3/Azure Blob (screenshots and recordings)
4. Infrastructure: load balancer + second app server

**6-month priorities (recommendation):**
5. Mac OS agent — Go-based, same API surface — unlocks ~40% of knowledge worker market
6. Employee self-service portal — employees view their own scores
7. Complete billing UI — Stripe integration and invoices
8. API documentation (OpenAPI/Swagger spec)

**12-month vision (recommendation):**
9. Linux agent — DevOps/engineering teams
10. SAML 2.0 — enterprise Okta/OneLogin buyers
11. AI-powered weekly summaries — natural language workforce insight reports
12. Mobile manager app — iOS/Android for operations leaders

---

*For detailed technical architecture, see [Architecture.md](Architecture.md).*  
*For competitive analysis and sales tools, see [Marketing-Guide.md](Marketing-Guide.md).*  
*For full feature inventory, see [Feature-Catalog.md](Feature-Catalog.md).*  
*For roadmap detail, see [Roadmap.md](Roadmap.md).*
