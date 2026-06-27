# CortexOne — Marketing Guide

> **Audience:** Sales Representatives, Marketing, Business Development  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Executive-Summary.md](Executive-Summary.md) · [Feature-Catalog.md](Feature-Catalog.md) · [Product-Bible.md](Product-Bible.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from verified product features |

---

> ⚠️ **Important:** All capabilities described in this guide are verified as implemented in the product. Do not invent or exaggerate capabilities. Do not market Mac/Linux agent support — it is not implemented. Do not market public launch until Cloudflare Turnstile CAPTCHA is re-enabled.

---

## 1. Ideal Customer Profile (ICP)

### Primary ICP

| Attribute | Value |
|---|---|
| Company size | 20–500 employees |
| Device type | Company-issued Windows PCs and laptops |
| Workforce type | Remote, hybrid, or distributed |
| Management style | Centralised IT department |
| Tech maturity | IT team uses some tooling (antivirus, MDM) but no unified monitoring |
| Pain state | Manual timesheets, leave via email, no visibility into remote workers |

### Secondary ICP (MSP Channel)

| Attribute | Value |
|---|---|
| Company type | Managed Service Provider (MSP) |
| Clients managed | 5–50 organisations, each 10–200 seats |
| Tooling | NinjaOne, Datto, N-able, ConnectWise, Atera (all RMM-compatible) |
| Pain state | Clients asking for productivity visibility; current tools don't provide it |
| Opportunity | White-label or reseller agreement for CortexOne |

---

## 2. Target Industries

| Industry | Why CortexOne Fits |
|---|---|
| **Business Process Outsourcing (BPO)** | High agent count, remote teams, compliance monitoring required, shift scheduling critical |
| **IT Services & MSPs** | RMM integration, fleet management, can resell to their own clients |
| **Professional Services** | Billable time tracking, QuickBooks/Xero payroll integration, leave management |
| **Financial Services** | Compliance audit trail, session recording for FSA/SEC requirements, anomaly detection |
| **Logistics & Operations** | Shift scheduling, GPS location for field workers, attendance records |
| **Healthcare Administration** | Compliance logging, role-based access, device security monitoring |
| **Staffing Agencies** | Monitor workers placed at client sites, productivity reports as proof of performance |
| **Legal** | Billable time tracking, document work monitoring, audit trail |

---

## 3. Buyer Personas

### Persona 1: The IT Manager

**Name:** "Technical Tom"  
**Role:** IT Manager / IT Director  
**Company size:** 50–300 employees  
**Age:** 35–50

**Responsibilities:**
- Manages all company Windows devices
- Responds to helpdesk tickets
- Deploys and maintains software
- Responsible for security incidents

**Pain points:**
- "I have no idea what's running on half our devices."
- "When a laptop fails, I only find out when the user calls me."
- "Deploying monitoring tools takes days of configuration."
- "Our antivirus keeps flagging monitoring agents as malware."

**What he cares about:**
- Fast, silent deployment (one command, no manual steps)
- Automatic Defender whitelisting
- Real-time alerts before problems escalate
- Works with our RMM (NinjaOne/Datto/N-able)

**CortexOne answers:**
- Deploy to 200 devices in 30 minutes with Deploy-Silent.ps1
- Defender exclusions are automated in the deployment script
- Alert rules fire within 60 seconds of a threshold breach
- RMM-compatible deployment scripts included

**Conversation starter:** "How long does it take your team to know a machine is offline?"

---

### Persona 2: The Operations Director

**Name:** "Operations Olivia"  
**Role:** VP Operations / Operations Director  
**Company size:** 50–500 employees  
**Age:** 38–55

**Responsibilities:**
- Team output and efficiency
- Cost control
- Headcount decisions
- Reports to CEO/CFO

**Pain points:**
- "I have 80 remote employees and I have no idea who's actually working."
- "Performance reviews are pure guesswork — my managers just go by gut feel."
- "We pay for ActivTrak, Hubstaff, and BambooHR — three invoices for things one tool should do."
- "I need a number I can show the CEO about team productivity."

**What she cares about:**
- Objective productivity data she can act on
- A single dashboard, not 3 tabs in 3 tools
- Cost per seat vs. the stack she currently pays for
- Executive-ready summary reports

**CortexOne answers:**
- Daily A–F productivity grade per employee — objective, algorithmic, no opinions
- Fleet health + productivity + HR leave approvals in one dashboard
- Replaces ActivTrak + Hubstaff + leave tool at a fraction of the combined price
- Executive dashboard and scheduled PDF reports built-in

**Conversation starter:** "If you had to grade your team's productivity today on a scale of A to F, what would you give them — and how confident are you in that answer?"

---

### Persona 3: The HR Manager

**Name:** "HR Helen"  
**Role:** HR Manager / People Operations Manager  
**Company size:** 30–200 employees  
**Age:** 30–50

**Responsibilities:**
- Leave management and approval
- Payroll preparation
- Attendance and time tracking
- Compliance documentation

**Pain points:**
- "Leave requests come to me by WhatsApp, email, and Teams message. It's chaos."
- "Every payroll week I spend two hours reconciling timesheets manually."
- "I have no way to see if someone's attendance pattern is changing."
- "Our HR system doesn't integrate with how people actually work."

**What she cares about:**
- Leave requests in one place with automatic balance tracking
- Payroll export that works with QuickBooks/Xero
- Attendance records without manual entry
- Scheduled reports she can send to the CFO

**CortexOne answers:**
- Full leave workflow: submit → approve → balance automatically deducted
- One-click payroll CSV export in QuickBooks or Xero format
- Actual device active time drives attendance records automatically
- Weekly attendance and leave summary report scheduled to her inbox

**Conversation starter:** "How do you currently handle a leave request — walk me through what happens from the moment an employee tells you they're taking time off."

---

## 4. Pain Points and Business Benefits

| Pain Point | Business Benefit | CortexOne Feature |
|---|---|---|
| No remote visibility | Know who is working, when, and on what | 60-second heartbeat + app usage |
| Subjective performance reviews | Objective A–F grade per employee, no opinions | Productivity scoring engine |
| IT alerts only when users complain | 60-second early warning system | Alert engine with cooldown |
| Unusual behaviour undetected | Automatic anomaly detection with 6 types | Anomaly detection + baselines |
| Leave managed by email | One platform: request, approve, balance | Leave workflow |
| Manual payroll reconciliation | Device activity → payroll export in one click | Payroll export (QuickBooks/Xero) |
| Shadow IT and unknown apps | Complete app usage history per device | URL history + app usage |
| No compliance audit trail | Every admin action logged immutably | Audit log |
| Agent deployment takes days | One PowerShell command, entire fleet | Deploy-Silent.ps1 |
| Monitoring tools flagged as virus | Defender exclusions automated in deploy script | Defender exclusion automation |
| Three tools for three problems | One platform: IT + Intelligence + HR | CortexOne all-in-one |
| Scattered integrations | 10 platforms, 11 webhook events, API keys | Integration hub |

---

## 5. Competitive Advantages

### Advantage 1: The Only Platform with Full HR + IT + Intelligence

No competitor in the monitoring space includes leave management, shift scheduling, and payroll export in their product:

| Capability | CortexOne | Hubstaff | ActivTrak | Teramind | Insightful |
|---|---|---|---|---|---|
| App usage + productivity scoring | ✅ | ✅ | ✅ | ✅ | ✅ |
| Leave management | ✅ | ❌ | ❌ | ❌ | ❌ |
| Payroll export | ✅ | ✅ | ❌ | ❌ | ❌ |
| Shift scheduling | ✅ | ✅ | ❌ | ❌ | ❌ |
| Session recording | ✅ | ❌ | ❌ | ✅ | ❌ |
| Webcam snapshots | ✅ | ❌ | ❌ | ✅ | ❌ |
| RMM silent deploy | ✅ | ❌ | ❌ | ❌ | ❌ |
| 10-platform integrations | ✅ | ✅ | ❌ | ⚠️ | ❌ |
| Geofence rules | ✅ | ✅ | ❌ | ❌ | ❌ |
| Audit log | ✅ | ❌ | ✅ | ✅ | ❌ |

### Advantage 2: Cost

A typical operations-heavy company of 100 employees pays:

| Tool | Monthly Cost |
|---|---|
| ActivTrak Business | $1,000/mo ($10/seat) |
| Hubstaff Team | $700/mo ($7/seat) |
| Leave management (Personio, etc.) | $300/mo ($3/seat) |
| **Total** | **$2,000/mo** |
| **CortexOne Enterprise** | **$800/mo ($8/seat)** |
| **Savings** | **$1,200/mo ($14,400/yr)** |

### Advantage 3: Deployment Speed

Deploy to 100 machines in the time it takes competitors to finish onboarding:
- Competitors: Manual install, configure per machine, no Defender exclusion → days of IT time
- CortexOne: Paste one PowerShell command into NinjaOne → 100 machines in 30 minutes, Defender exclusions automated

### Advantage 4: RMM Integration

No major competitor ships pre-built RMM scripts compatible with NinjaOne, Datto, N-able, ConnectWise, and Atera. For MSP customers, this is a decisive differentiator.

### Advantage 5: Advanced Monitoring (Opt-In)

Session recording and webcam capture — matched only by Teramind (enterprise-only, 10× the price). For compliance-heavy industries, this is often a legal requirement.

---

## 6. Unique Selling Propositions (USPs)

1. **"Three tools replaced by one"** — IT monitoring + productivity intelligence + HR management in a single platform
2. **"From signup to monitoring in 30 minutes"** — fastest deployment in the category
3. **"An A to F grade for every employee, every day — no opinions"** — algorithmic, objective, automated
4. **"Your RMM already works with us"** — NinjaOne, Datto, N-able, ConnectWise, Atera compatible
5. **"Pay $8 to replace $20"** — replace the ActivTrak + Hubstaff + leave tool stack for 60% less

---

## 7. Product Positioning

### Positioning Statement
For **IT managers and operations directors at 20–500 person companies** who **need complete workforce visibility without managing three separate tools**, CortexOne is **the all-in-one workforce monitoring platform** that provides **real-time device health, objective daily productivity scores, HR leave management, and payroll export in a single product**, unlike **ActivTrak (no HR) or Hubstaff (no device monitoring)**, CortexOne **combines all three disciplines so organisations never need to switch tabs**.

### Category
**Workforce Intelligence Platform** (not just "employee monitoring" — the intelligence and HR layers elevate it above surveillance tools)

### Brand Personality
- **Precise** — algorithmic scores, not gut feel
- **Trusted** — privacy-first design, opt-in advanced monitoring
- **Efficient** — 30-minute deployment, one dashboard
- **Complete** — no tool sprawl, no integrations required for core value

---

## 8. Example Sales Pitch (15 Minutes)

**Minute 0–2: Open with a question**
"How many tools do you currently use to answer the question: is my team working right now, are they productive, and are they taking leave accurately?"

*[Let them list: monitoring tool, time tracker, leave management, maybe HR system]*

"What if one platform answered all of that?"

**Minute 2–5: Show the dashboard**
Open the executive dashboard. Show: fleet health summary, productivity risk matrix (Healthy/Watch/At-Risk), top alert. "This is everything your operations director needs in one screen — updated every 60 seconds."

**Minute 5–8: Show the deployment**
"Here's how long it takes to add a new machine." Show agent download page. Show Deploy-Silent.ps1. "Paste this into NinjaOne — or run it manually — and in 60 seconds this machine is in the dashboard."

**Minute 8–11: Show productivity scoring**
Click into a device. Show day's score: 74/B. Show app usage breakdown. "This score is automatic. No manager had to grade anyone. The algorithm looks at what apps were used, how long, versus expected hours, versus their historical baseline."

**Minute 11–13: Show HR integration**
Click to Leave. Show pending requests. Approve one. Show balance updated. "Same platform. No separate HR tool."

**Minute 13–15: Show the price**
"You're currently paying [their number]. CortexOne at [seat count] seats is $[price]/month. That's [savings]/month back in your budget."

**Close:** "We can have your first devices monitored in under an hour. When would you want to start?"

---

## 9. Website Messaging

### Hero Section
**Headline:** See everything. Score automatically. Manage in one place.  
**Sub-headline:** The workforce monitoring platform that combines real-time device health, daily productivity scoring, and complete HR management — so you never need three tools again.  
**CTA:** Start Free Trial — No credit card required

### Feature Section 1: Monitor
**Headline:** Every device, every minute.  
**Body:** Real-time CPU, RAM, disk, and network across your entire Windows fleet. Know what's running, who's active, and how healthy every machine is — before problems start.

### Feature Section 2: Score
**Headline:** An A to F grade. Automatic. Every day.  
**Body:** CortexOne calculates a daily productivity score (0–100, A–F grade) for every employee based on app usage, active time, focus, and browsing habits. No manager input required.

### Feature Section 3: Manage
**Headline:** Leave, payroll, and scheduling — in the same platform.  
**Body:** Your team submits leave requests. Managers approve in one click. Balances update automatically. Export to QuickBooks or Xero with one click. The HR tasks your team does every week, simplified.

### Pricing Section
| Starter | Pro | Enterprise |
|---|---|---|
| $3/seat/month | $5/seat/month | $8/seat/month |
| Monitoring + alerts | + HR workflows + integrations | + Session recording + location |
| 14-day free trial | 14-day free trial | 14-day free trial |

### Social Proof Placeholder
*[Customer testimonials to be added after launch]*

---

## 10. Landing Page Copy (Short Form)

**Headline:** Stop guessing. Start knowing.

Your team is remote. You can't see who's working. You can't tell if productivity is dropping. You can't track leave without chasing emails. You're using three tools and still don't have a clear picture.

**CortexOne changes that.**

Install the agent on your Windows machines in under 30 minutes. Within the hour, you'll see:
- Every device: online, offline, idle, or at risk
- Every employee: their daily productivity score (A to F)
- Every leave request: submitted, approved, balanced — automatically

No more spreadsheets. No more chasing timesheets. No more guessing.

**Deploy today. See everything tomorrow.**

[Start Free Trial — 14 Days, No Credit Card]

---

## 11. Frequently Asked Questions

**Q: Does it work on Mac or Linux?**  
A: Currently, the agent runs on Windows 10 (version 1903+) and Windows 11. Mac and Linux support are on the roadmap.

**Q: Will antivirus flag the agent?**  
A: The deployment script automatically adds Windows Defender exclusions for the agent path and process. For other antivirus products, you may need to add exclusions manually — we provide the paths.

**Q: Do employees know they're being monitored?**  
A: Yes. We recommend transparent deployment — employees should know a monitoring agent is installed. For advanced features (screenshots, webcam, location), the agent displays a system tray notification the first time these are activated.

**Q: Can employees see their own scores?**  
A: The employee self-service portal is currently in development. Admins and managers can share individual scores.

**Q: Is the data secure?**  
A: All data is encrypted in transit (TLS). Dashboard access uses JWT RS256 authentication. Every admin action is logged immutably. Data is isolated per organisation — no org can access another's data.

**Q: What happens to the data if I cancel?**  
A: You retain access for the remainder of your paid period. Data export is available via the reports and API. After account closure, data is deleted per our retention policy.

**Q: How do integrations work?**  
A: CortexOne sends events to Slack, Teams, Zapier, and Make via webhooks. You can export timesheet data to QuickBooks or Xero with one click. Full API access with API keys for custom integrations.

**Q: Does it require any infrastructure at our site?**  
A: No. The agent on employee machines phones home to our cloud servers. No server, no VPN, no on-premises installation.

**Q: How is it priced?**  
A: Per seat per month. Starter ($3), Pro ($5), Enterprise ($8). Annual billing available at 2 months free.

**Q: What's included in the free trial?**  
A: Full platform access including Pro features for 14 days. No credit card required. Deploy as many devices as you need during the trial.

---

## 12. Objection Handling

**"We already use ActivTrak."**  
ActivTrak doesn't include leave management, payroll export, or shift scheduling. If you have a separate tool for those — or you're doing them manually — CortexOne replaces both at a lower combined cost. How much are you spending on ActivTrak + your current leave/HR tool?

**"We already use Hubstaff."**  
Hubstaff is a time tracker. CortexOne provides real-time device monitoring, anomaly detection, alert rules, and session recording on top of everything Hubstaff does — at a comparable price. What do you do when a device goes offline or a CPU spikes?

**"Our employees won't like being monitored."**  
Every world-class company monitors its network and devices — that's standard IT practice. CortexOne makes monitoring transparent: employees know the agent is installed, and advanced features require explicit opt-in. The alternative — no visibility — hurts both the company and hard-working employees who deserve recognition.

**"We only use Macs."**  
Currently, CortexOne's agent runs on Windows. If your team uses Windows even partially, you can start monitoring those devices immediately. Mac support is on our near-term roadmap.

**"We're too small for this."**  
We work with companies as small as 20 employees. At $3/seat/month, monitoring 20 devices costs $60/month. The first time you catch a productivity issue or prevent a device failure, it pays for itself.

**"Security won't approve an agent on our machines."**  
The agent is a standard Windows Service running under LocalSystem. The deployment script adds Defender exclusions automatically. We provide full documentation for your security review, including the binary SHA-256 hash for integrity verification.

**"We tried a monitoring tool before and employees revolted."**  
That was probably a surveillance tool, not a productivity platform. CortexOne is transparent by design — no keylogging content capture, no hidden screenshots by default, employee notification on all advanced features. We help you build a culture of accountability, not suspicion.

**"We don't want to store employee data in the cloud."**  
All data is isolated per organisation, encrypted in transit, and never shared with other customers. For enterprise customers with specific data residency requirements, contact us to discuss options.

**"What's the ROI?"**  
A team of 50 that improves average productivity by 10% effectively adds the equivalent of 5 additional full-time employees without hiring. At an average salary of $50K, that's $250K/year of recovered output — for $3,000/year in CortexOne fees.
