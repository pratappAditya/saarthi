# Saarthi Admin Control Plane

The **Saarthi Admin Control Plane** is a dedicated, production-grade operations console designed for platform operators, customer support, and financial analysts to manage users, organizations, canonical plans, billing lifecycles, autonomous agents, and system health.

It is architected as an isolated client application to later be hosted on its dedicated domain:
```
https://admin.saarthi.trovanetech.com
```

---

## 1. Architecture

```
                       Admin Operator Browser
                                 │
                                 ▼
                     Admin Control Plane UI
                  (React 19 + TypeScript + Vite)
                                 │
                     HTTPS / Admin Auth Bearer
                                 │
                                 ▼
                      Saarthi Backend Server
                 (/admin/* Routes with RBAC Guards)
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
SQLite WAL Engine /       Domain Intelligence      Billing Engine
Unified Schema Models    (17 Knowledge Packs)   (Quotas & Subscriptions)
```

### Architectural Principles & Boundaries
1. **Single Source of Truth**: The Admin Panel does **not** create a second backend or an independent database. It queries and orchestrates the existing Saarthi backend services and schema.
2. **No Direct Database Access**: No raw SQL, no database drivers, and no database credentials exist in the admin frontend bundle.
3. **Strict Privacy Boundary**: User private prompts, raw conversational transcripts, vector embeddings, uploaded documents, and voice audio are strictly separated and excluded from all administrative views.
4. **Server-Enforced RBAC**: Frontend route and action hiding is strictly an ergonomic feature. All administrative mutations are authorized server-side and recorded in an immutable audit trail.
5. **Zero Live Payment Capability**: Live payment collection remains strictly disabled. The control plane operates on billing lifecycle records and metadata.

---

## 2. Directory Structure

```
/admin
  ├── public/
  │   └── favicon.svg
  ├── src/
  │   ├── api/
  │   │   ├── client.ts             # Authenticated fetch wrapper with 401 handling
  │   │   └── adminApi.ts           # Modular client for all /admin backend endpoints
  │   ├── auth/
  │   │   ├── AuthContext.tsx       # Auth context, session storage, and role helpers
  │   │   └── ProtectedRoute.tsx    # Role-based route & view protection
  │   ├── components/
  │   │   ├── common/               # Design system components
  │   │   │   ├── Badge.tsx         # Semantic status indicators
  │   │   │   ├── Button.tsx        # Action buttons with loading states
  │   │   │   ├── Card.tsx          # Consistent container cards
  │   │   │   ├── ConfirmDialog.tsx # Destructive action confirmation dialogs
  │   │   │   ├── Drawer.tsx        # Slide-over record inspection drawers
  │   │   │   ├── EmptyState.tsx    # Fallback zero-data states
  │   │   │   ├── LoadingSpinner.tsx# Spinners and skeletons
  │   │   │   ├── Modal.tsx         # Accessible overlay modals
  │   │   │   ├── Pagination.tsx    # Offset and page controls
  │   │   │   ├── SearchInput.tsx   # Debounced filter inputs
  │   │   │   └── StatCard.tsx      # Top-level operational metric widgets
  │   │   └── layout/
  │   │       ├── AdminHeader.tsx   # Top banner, environment badge, profile & logout
  │   │       ├── AdminSidebar.tsx  # Grouped navigation with role-based filtering
  │   │       ├── Breadcrumbs.tsx   # Navigation hierarchy
  │   │       └── AdminLayout.tsx   # Shell layout wrapping pages
  │   ├── pages/
  │   │   ├── LoginPage.tsx         # Dual-mode key & credential login
  │   │   ├── OverviewPage.tsx      # High-level operational metrics & health
  │   │   ├── UsersPage.tsx         # User management, role updates, suspensions
  │   │   ├── OrganizationsPage.tsx # Multi-seat tenants, member inspection, seat limits
  │   │   ├── PlansPage.tsx         # Canonical plans catalog & entitlement overrides
  │   │   ├── BillingPage.tsx       # Subscriptions, Payments, Invoices, Refunds, Webhooks
  │   │   ├── AuditLogsPage.tsx     # Immutable security audit trail
  │   │   ├── AutomationsPage.tsx   # Phase 9 automations & routine schedules
  │   │   ├── AgentsPage.tsx        # Agent task graphs, step diagnostics, permissions
  │   │   ├── ResearchPage.tsx      # 17 domain packs, provider latency, run history
  │   │   ├── SystemHealthPage.tsx  # Subsystem status, DB integrity checks, diagnostics
  │   │   ├── SettingsPage.tsx      # Feature flags, maintenance mode, AI config, bans
  │   │   ├── UnauthorizedPage.tsx  # 403 Access Denied fallback
  │   │   └── NotFoundPage.tsx      # 404 View Not Found fallback
  │   ├── styles/
  │   │   └── index.css             # Tailwind v4 styles with dark operations theme
  │   ├── types/
  │   │   └── admin.ts              # Complete TypeScript interfaces for all admin data
  │   ├── App.tsx                   # Hash-synchronized routing and layout coordinator
  │   └── main.tsx                  # React 19 application entrypoint
  ├── index.html                    # HTML shell
  ├── package.json                  # Isolated npm scripts & dependencies
  ├── tsconfig.json                 # TypeScript project configuration
  ├── vite.config.ts                # Vite config with /admin & /api proxies on port 5174
  └── README.md                     # This documentation
```

---

## 3. Role-Based Access Control (RBAC)

The control plane implements four conceptual roles:

| Role | Permissions & Scope |
| :--- | :--- |
| `SUPER_ADMIN` | Unrestricted access across all operational, financial, and security boundaries. Full configuration, user role mutations, tenant deletions, and maintenance toggles. |
| `ADMIN` | Day-to-day operations: User role and plan adjustments, organization seat quotas, routine toggling, agent task recovery/cancellation, and manual refund authorization. |
| `ANALYST` | Read-only inspection across telemetry, audit logs, billing records, research runs, and system health. Mutating actions are disabled. |
| `SUPPORT` | Customer diagnostic access: User lookup, quota inspections, and session troubleshooting. Cannot alter subscription plans or security policies. |

---

## 4. Local Development

### Prerequisites
- Node.js 18+ (tested on Node v20+)
- Python 3.11+ running the Saarthi backend on `http://127.0.0.1:8000`

### Installation & Execution
```bash
# Navigate to admin directory
cd admin

# Install dependencies (only required on first setup)
npm install

# Start development server on port 5174
npm run dev
```

The admin portal will open at:
```
http://localhost:5174
```

### Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Public backend URL | `http://127.0.0.1:8000` |
| `VITE_APP_ENV` | Environment identifier (`development`, `staging`, `production`) | `development` |

*Note: Never place database passwords, Razorpay secrets, or master admin keys in `VITE_*` variables.*

---

## 5. Verification Commands

Run the following commands inside `/admin`:

```bash
# Lint with oxlint (must produce 0 errors)
npm run lint

# Build production bundle with TypeScript check
npm run build
```

---

## 6. Backend Endpoints Reused & Extended

The Admin Panel interfaces with the existing Saarthi backend routes in `backend/app/api/admin.py`:

### Authentication & Session
- `POST /admin/auth/login`: Admin authentication via master key or admin credentials.
- `GET /admin/auth/verify`: Validates token and returns current admin role.
- `POST /admin/auth/logout`: Revokes active session.

### Operations & Dashboard
- `GET /admin/dashboard`: Platform counts (users, tasks, routines, system status).
- `GET /admin/version`: App version, active phase, and environment.

### Users & Entitlements
- `GET /admin/users`: Search, paginate, and filter users by plan/role.
- `GET /admin/users/{user_id}/details`: User quota evaluations, devices, and sessions.
- `POST /admin/users/update-role`: Server-audited role changes.
- `POST /admin/users/update-plan`: Server-audited plan adjustments.
- `POST /admin/users/suspend`: Account suspension.
- `POST /admin/users/restore`: Account restoration.

### Organizations & Teams
- `GET /admin/organizations`: Lists multi-seat organizations.
- `GET /admin/organizations/{org_id}`: Fetches tenant details with active members list.
- `POST /admin/organizations`: Creates new tenant organization.
- `POST /admin/organizations/{org_id}/seats`: Updates seat allocation with audit entry.

### Plans & Monetization
- `GET /admin/plans/catalog`: Canonical plan definitions from backend Plan Registry.
- `GET /admin/entitlements/{user_id}`: Real-time resolved user quotas & capabilities.
- `POST /admin/entitlements/override`: Manual entitlement override with audit reason.
- `GET /admin/billing/overview`: Aggregated MRR, ARR, and payment counts.
- `GET /admin/billing/subscriptions`: Full subscription lifecycle list.
- `GET /admin/billing/payments`: Payment events audit.
- `GET /admin/billing/invoices`: Invoices registry.
- `GET /admin/billing/refunds`: Processed refunds log.
- `POST /admin/billing/refunds/process`: Server-validated refund execution.
- `GET /admin/billing/webhooks`: Sanitized incoming webhook event monitor.

### Intelligence, Agents & Research
- `GET /admin/automations`: Phase 9 unified automations and routines.
- `POST /admin/automation/routines/{routine_id}/toggle`: Routine state toggle.
- `GET /admin/agents/tasks`: Running, completed, and failed agent runs.
- `GET /admin/agents/tasks/{task_id}`: Execution step breakdown & error diagnostics.
- `POST /admin/agents/tasks/{task_id}/cancel`: Safely cancels running agent.
- `POST /admin/agents/tasks/{task_id}/recover`: Triggers recovery for failed tasks.
- `GET /admin/permissions/pending`: High-risk tool execution requests awaiting approval.
- `POST /admin/permissions/{req_id}/action`: Approve or reject tool execution.
- `GET /admin/research/overview`: 17 domain intelligence packs & cache statistics.
- `GET /admin/research/runs`: Privacy-redacted research synthesis runs.

### System Diagnostics & Settings
- `GET /admin/health`: Database and subsystem health checks.
- `POST /admin/health/db-check`: SQLite integrity verification.
- `POST /admin/diagnostics/bundle`: Non-sensitive diagnostic bundle snapshot.
- `GET /admin/feature-flags`: Real-time feature toggle flags.
- `POST /admin/feature-flags/update`: Dynamic rollout percentage and state update.
- `GET /admin/maintenance`: Maintenance mode configuration.
- `POST /admin/maintenance/toggle`: Global maintenance window toggle with bypass whitelist.
- `GET /admin/ai/config`: Default LLM model and parameter configuration.
- `POST /admin/ai/config`: Administrative model adjustments.
- `GET /admin/tools`: Tool security risk classifications and permission bounds.
- `POST /admin/tools/policy`: Modifies tool risk level and enablement.
- `GET /admin/security/bans`: Blocked IP addresses and accounts.
- `POST /admin/security/ban`: Adds security ban.
- `POST /admin/security/unban`: Lifts security ban.
- `GET /admin/audit-logs`: Immutable audit log query.

---

## 7. Staging Deployment Checklist

When deploying to `https://admin.saarthi.trovanetech.com`:
1. **DNS**: Point `admin.saarthi.trovanetech.com` CNAME to the static hosting edge (e.g. Cloudflare Pages, Vercel, or AWS CloudFront/S3).
2. **Environment**: Configure `VITE_API_BASE_URL=https://api.saarthi.trovanetech.com` and `VITE_APP_ENV=staging`.
3. **CORS**: Verify backend CORS allows `https://admin.saarthi.trovanetech.com` with `allow_credentials=True`.
4. **Security Headers**: Ensure HTTP response headers include `Content-Security-Policy`, `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.
