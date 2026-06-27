# CortexOne — Technology Stack

> **Audience:** Engineers, DevOps, CTOs, Technical Evaluators  
> **Classification:** Internal Confidential  
> **Version:** 1.0 — 2026-06-28  
> **Related Documents:** [Architecture.md](Architecture.md) · [Developer-Guide.md](Developer-Guide.md) · [Known-Limitations.md](Known-Limitations.md)

---

## Revision History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-06-28 | Generated from codebase reverse-engineering |
| 1.1 | 2026-06-28 | Added unconfirmed library gaps (PDF, Excel, charting); clarified gd/imagick uncertainty |

---

## 1. Programming Languages

| Language | Version | Role | Confidence |
|---|---|---|---|
| PHP | 8.3.x | Backend API, server-side HTML rendering | Verified — declared in `bootstrap.php`, strict_types |
| C# | .NET 8.0 | Windows agent (ProductivityAgent.exe) | Verified — `net8.0-windows10.0.19041.0` TFM in project file |
| JavaScript | ES2020+ | Dashboard frontend interactivity | Verified — modern syntax used throughout modules |
| SQL | MySQL 8.4 dialect | Database schema, migrations, queries | Verified — all schema files |
| PowerShell | 5.1+ | Silent deployment scripts | Verified — `Deploy-Silent.ps1` |
| Windows Batch | cmd.exe | Silent deploy wrapper | Verified — `Deploy-Silent.bat` |
| HTML5 | — | Dashboard templates | Verified |
| CSS3 | — | Dashboard styling with custom properties | Verified |

---

## 2. Frameworks and Runtime

### Server Side

| Framework | Version | Purpose | Evidence |
|---|---|---|---|
| No PHP framework | — | Procedural PHP, custom routing | No composer.json Laravel/Symfony dependency |
| PDO | PHP built-in | Database abstraction | `Database.php` helper uses PDO exclusively |
| PHP Sessions | PHP built-in | Dashboard authentication | `PS_SESS` session cookie |

### Agent Side

| Framework | Version | Purpose | Evidence |
|---|---|---|---|
| Microsoft.Extensions.Hosting | .NET 8.0 | Worker service host | IHostedService / BackgroundService pattern |
| Microsoft.Extensions.Http | .NET 8.0 | HttpClient factory with retry | IHttpClientFactory usage |
| Microsoft.Extensions.Configuration | .NET 8.0 | appsettings.json binding | `AgentOptions` POCO binding |
| Microsoft.Extensions.DependencyInjection | .NET 8.0 | DI container | Service registration in Program.cs |

### Frontend

| Library | Version | Purpose | Evidence |
|---|---|---|---|
| Vanilla JavaScript | ES2020+ | All client-side logic | No npm/webpack; no SPA framework |
| Bootstrap Icons | 1.x | UI icons | Local asset in dashboard |
| Leaflet.js | 1.9.4 | Location route map | Loaded from `unpkg.com/leaflet@1.9.4` on location tab |

---

## 3. Libraries and SDKs

### .NET Agent Libraries

| Package | Version | Purpose |
|---|---|---|
| `System.Management` | 8.0.0 | WMI queries: CPU model, RAM total, disk info |
| `System.Diagnostics.PerformanceCounter` | 8.0.0 | CPU %, available memory, disk I/O |
| `Microsoft.Data.Sqlite` | 8.0.0 | Offline cache SQLite database |
| `Serilog` | Latest | Structured logging framework |
| `Serilog.Sinks.File` | 5.0.0 | Rolling daily log files |
| `Serilog.Sinks.EventLog` | 3.1.0 | Windows Event Log integration |
| `Windows.Foundation.UniversalApiContract` | SDK 10.0.19041 | WinRT API projections (webcam, location) |
| `Microsoft.Windows.CsWin32` | Latest | P/Invoke source generation (WTS, CreateProcess) |

### WinRT APIs Used
| API | Namespace | Purpose |
|---|---|---|
| `MediaCapture` | `Windows.Media.Capture` | Webcam snapshot capture |
| `Geolocator` | `Windows.Devices.Geolocation` | GPS/WiFi/IP location |
| `DeviceInformation` | `Windows.Devices.Enumeration` | Enumerate webcam devices |

### PHP Libraries
| Library | Source | Purpose |
|---|---|---|
| None (custom JWT) | `api/helpers/JWT.php` | RS256 JWT without external dependency |
| PDO MySql | PHP built-in extension | Database access |
| openssl_* functions | PHP built-in | RSA signing/verification |
| ZipArchive | PHP built-in | Agent package ZIP generation |
| curl / file_get_contents | PHP built-in | OAuth token exchange, webhook delivery |
| **PDF generation library** | **Not confirmed from repository** | **Required by `reports.php` for PDF export — investigate before environment setup** |
| **Excel generation library** | **Not confirmed from repository** | **Required by `reports.php` for XLSX export — investigate before environment setup** |
| **Charting library** | **Not confirmed from repository** | **Used in dashboard templates — inspect `shell.php` script includes to identify** |

---

## 4. Database

| Component | Product | Version |
|---|---|---|
| Database engine | MySQL | 8.4.7 |
| Driver | PDO MySQLi | PHP built-in |
| Character set | utf8mb4 | — |
| Collation | utf8mb4_unicode_ci | — |
| Storage engine | InnoDB | All tables |
| Partitioning | RANGE (heartbeats) | Month-based partitions |

> Full schema: [Database.md](Database.md)

---

## 5. Development Tools

| Tool | Purpose | Required |
|---|---|---|
| WAMP 3.x (Windows) | Local PHP + Apache + MySQL stack | Dev/current production |
| Visual Studio 2022 / VS Code | Agent C# development | Yes |
| .NET 8 SDK | Build agent | Yes |
| MySQL Workbench | Database management | Recommended |
| Postman / Insomnia | API testing | Recommended |
| PowerShell 5.1+ | Deploy script testing | Yes |
| Git | Version control | Yes |
| GitHub Actions (implied) | CI/CD for agent build | Implied by project structure |

---

## 6. Operating Systems

| Component | Supported OS | Notes |
|---|---|---|
| Server (current) | Windows 11 Home | WAMP stack — not production grade |
| Server (recommended) | Windows Server 2022 | IIS or Apache |
| Server (alternative) | Ubuntu 22.04 LTS | nginx + PHP-FPM + MySQL |
| Agent | Windows 10 1903+ (x64) | Minimum for WinRT APIs |
| Agent TFM | Windows 10.0.19041+ | Build target for WinRT API projections |
| Agent packaging | win-x64 self-contained | No .NET runtime required on endpoint |
| Developer machine | Windows 10/11, Windows Server | Agent must be built on Windows |

---

## 7. Third-Party Services

| Service | Tier | Purpose | Status |
|---|---|---|---|
| Stripe | Commercial | Subscription billing, invoices | Integrated, test keys in .env |
| Google OAuth 2.0 | Free (standard quotas) | User SSO login/register | Implemented, credentials empty |
| Microsoft Identity Platform | Free (standard quotas) | User SSO login/register | Implemented, credentials empty |
| Gmail SMTP | Free (app password) | Email delivery | Active — `contact.to.adnan@gmail.com` |
| Cloudflare Turnstile | Free tier | Registration CAPTCHA | Implemented, DISABLED |
| OpenStreetMap / Leaflet | Free | Location map tiles | Active for Phase 3 location tab |
| unpkg.com CDN | Free | Leaflet.js asset delivery | Used for Leaflet 1.9.4 |

---

## 8. Hosting and Infrastructure

### Current Infrastructure

| Component | Technology | Notes |
|---|---|---|
| Web server | Apache 2.4 | mod_rewrite enabled |
| PHP runtime | PHP 8.3 mod_php | Single-process per request |
| Database | MySQL 8.4.7 | Co-located on same server |
| File storage | Local filesystem | On same server as web app |
| TLS | SSL certificate on app.aptus.global | Provider not confirmed |
| DNS | app.aptus.global | Provider not confirmed |
| Sessions | Filesystem (`/sessions/`) | On web server |
| Backups | Not verified | No backup tooling confirmed in repo |

### Required PHP Extensions

| Extension | Purpose |
|---|---|
| `pdo_mysql` | Database connectivity |
| `openssl` | JWT signing, HTTPS |
| `curl` | OAuth token exchange, webhook delivery |
| `zip` | Agent package ZIP generation |
| `gd` or `imagick` | Image processing (screenshots) — exact extension required not confirmed from repository |
| `json` | API request/response |
| `mbstring` | Multi-byte string handling |
| `fileinfo` | MIME type detection |

---

## 9. Build Process

### PHP (Server)
No build process. PHP files are deployed directly. No compilation step.

```
Deployment:
1. Copy /ProductivitySuite/ to server document root
2. Configure .env with credentials
3. Run database migrations in /database/migrations/
4. Ensure /sessions/, /storage/, /reports/generated/ have write permissions
5. Configure Apache vhost with mod_rewrite
```

### .NET Agent
```
Build command:
dotnet publish -c Release -r win-x64 --self-contained true \
  -p:PublishSingleFile=true \
  -p:IncludeNativeLibrariesForSelfExtract=true

Output: ProductivityAgent.exe (~72 MB self-contained)

Signed with SHA-256: 1d2233ab26cd5dd14b8dff0a3feab7191327be41e0cf5ab1e53d08c2542fdf1e
Size: 75,332,344 bytes
Version: 1.1.0
```

---

## 10. Version Requirements Summary

| Requirement | Minimum | Recommended |
|---|---|---|
| PHP | 8.3.0 | 8.3.latest |
| MySQL | 8.0 | 8.4.latest |
| .NET SDK (build) | 8.0 | 8.0.latest |
| .NET Runtime (agent) | Self-contained — none required on endpoint | — |
| Windows (agent endpoint) | 10 1903 (Build 18362) | 10/11 latest |
| Windows Server (production) | 2019 | 2022 |
| Apache | 2.4 | 2.4.latest |
| PowerShell (deploy) | 5.1 | 5.1 or 7.x |

---

## 11. Dependency Security Notes

| Component | Note |
|---|---|
| No PHP framework | Reduces attack surface; no framework CVE exposure — but requires manual security diligence |
| No npm/node_modules | No JavaScript supply chain risk (no build step) |
| Leaflet from unpkg.com CDN | External CDN dependency — consider self-hosting for air-gapped environments |
| Gmail SMTP with app password | App password visible in .env — must be in .gitignore; rotate if exposed |
| Stripe test keys in .env | Must be replaced with live keys; .env must never be committed |
| JWT PEM keys in config/keys/ | Not in database — stored as files; must be backed up and access-controlled |

---

## 12. Recommended Upgrades

| Item | Current | Recommendation | Priority |
|---|---|---|---|
| Server OS | Windows 11 Home | Windows Server 2022 or Ubuntu 22.04 | High |
| File storage | Local filesystem | AWS S3 or Azure Blob Storage | High |
| Session storage | Filesystem | Redis (for multi-server scaling) | High |
| Email delivery | Gmail SMTP | SendGrid or SES (rate limits, bounce management) | Medium |
| PHP runtime | mod_php | PHP-FPM (better performance) | Medium |
| Database | Co-located MySQL | Dedicated MySQL or RDS (availability) | High |
| Job queue | Cron + CRON_SECRET | Redis + job queue (Beanstalkd, Laravel Horizon if PHP framework added) | Medium |
| Agent offline storage | SQLite plaintext | SQLite with SQLCipher encryption | Medium |
| CDN | None | Cloudflare or AWS CloudFront (static assets, DDoS) | Medium |
| OpenAPI spec | None | OpenAPI 3.0 / Swagger UI | Medium |
| Test suite | Not verified | PHPUnit (backend), xUnit (agent) | High |
