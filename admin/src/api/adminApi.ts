import { adminFetch } from './client';
import type {
  AdminUser,
  OverviewMetrics,
  UserRecord,
  UserDetails,
  OrganizationRecord,
  PlanDefinition,
  SubscriptionRecord,
  PaymentRecord,
  InvoiceRecord,
  RefundRecord,
  WebhookEventRecord,
  AuditLogEvent,
  AutomationRecord,
  RoutineRecord,
  AgentTaskRecord,
  ResearchOverview,
  ResearchRunRecord,
  SystemHealthData,
  ToolPolicyRecord,
  FeatureFlagRecord,
  MaintenanceModeRecord,
  OpsHealth,
  OpsMetrics,
  OpsService,
  OpsContainersResponse,
  OpsErrorLog,
  OpsIncident,
  OpsSnapshot,
  OpsDiagnosis
} from '../types/admin';

export const authApi = {
  login: (data: { email?: string; password?: string; admin_key?: string }) =>
    adminFetch<{ status: string; token: string; admin: AdminUser }>('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  verify: () =>
    adminFetch<{ status: string; authenticated: boolean; admin: AdminUser }>('/admin/auth/verify'),

  logout: () =>
    adminFetch<{ status: string; message: string }>('/admin/auth/logout', {
      method: 'POST'
    })
};

export const dashboardApi = {
  getOverview: async (): Promise<OverviewMetrics> => {
    const [dashRes, billRes] = await Promise.all([
      adminFetch<{ status: string; metrics: any; system_health: any }>('/admin/dashboard'),
      adminFetch<{ status: string; overview: any }>('/admin/billing/overview').catch(() => null)
    ]);

    return {
      ...dashRes.metrics,
      billing: billRes?.overview
    };
  }
};

export const usersApi = {
  list: (params?: { query?: string; role?: string; plan?: string }) => {
    const q = new URLSearchParams();
    if (params?.query) q.set('query', params.query);
    if (params?.role) q.set('role', params.role);
    if (params?.plan) q.set('plan', params.plan);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return adminFetch<{ status: string; users: UserRecord[] }>(`/admin/users${qs}`);
  },

  getDetails: (userId: string) =>
    adminFetch<UserDetails>(`/admin/users/${userId}/details`),

  updateRole: (userId: string, role: string, reason?: string) =>
    adminFetch<{ status: string; user_id: string; updated_role: string }>('/admin/users/update-role', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, role, reason })
    }),

  updatePlan: (userId: string, plan: string, reason?: string) =>
    adminFetch<{ status: string; user_id: string; updated_plan: string }>('/admin/users/update-plan', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, plan, reason })
    }),

  suspend: (userId: string, reason?: string) =>
    adminFetch<{ status: string }>('/admin/users/suspend', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, reason })
    }),

  restore: (userId: string, reason?: string) =>
    adminFetch<{ status: string }>('/admin/users/restore', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, reason })
    }),

  delete: (userId: string, reason?: string) => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return adminFetch<{ status: string }>(`/admin/users/${userId}${qs}`, {
      method: 'DELETE'
    });
  }
};

export const orgsApi = {
  list: () =>
    adminFetch<{ status: string; organizations: OrganizationRecord[] }>('/admin/organizations'),

  getDetails: (orgId: string) =>
    adminFetch<{ status: string; organization: OrganizationRecord }>(`/admin/organizations/${orgId}`),

  create: (data: { name: string; plan?: string; max_seats?: number }) =>
    adminFetch<{ status: string; organization: OrganizationRecord }>('/admin/organizations', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateSeats: (orgId: string, maxSeats: number) =>
    adminFetch<{ status: string; org_id: string; max_seats: number }>(`/admin/organizations/${orgId}/seats`, {
      method: 'POST',
      body: JSON.stringify({ max_seats: maxSeats })
    })
};

export const plansApi = {
  getCatalog: () =>
    adminFetch<{ status: string; catalog: PlanDefinition[]; subscriptions: any[] }>('/admin/plans/catalog'),

  getEntitlements: () =>
    adminFetch<{ status: string; entitlement_matrix: any }>('/admin/entitlements'),

  inspectUser: (userId: string) =>
    adminFetch<{ status: string; plan: string; capabilities: any; limits: any }>(`/admin/entitlements/${userId}`),

  override: (data: {
    user_id: string;
    plan_override?: string;
    capabilities_override?: Record<string, any>;
    expires_at?: string;
    reason?: string;
  }) =>
    adminFetch<{ status: string; override: any }>('/admin/entitlements/override', {
      method: 'POST',
      body: JSON.stringify(data)
    })
};

export const billingApi = {
  getOverview: () =>
    adminFetch<{ status: string; overview: any }>('/admin/billing/overview'),

  listSubscriptions: () =>
    adminFetch<{ status: string; subscriptions: SubscriptionRecord[] }>('/admin/billing/subscriptions'),

  listPayments: () =>
    adminFetch<{ status: string; payments: PaymentRecord[] }>('/admin/billing/payments'),

  listInvoices: () =>
    adminFetch<{ status: string; invoices: InvoiceRecord[] }>('/admin/billing/invoices'),

  listRefunds: () =>
    adminFetch<{ status: string; refunds: RefundRecord[] }>('/admin/billing/refunds'),

  processRefund: (paymentId: string, reason: string) =>
    adminFetch<{ status: string; refund_id: string; message: string }>('/admin/billing/refunds/process', {
      method: 'POST',
      body: JSON.stringify({ payment_id: paymentId, reason })
    }),

  listWebhooks: () =>
    adminFetch<{ status: string; webhooks: WebhookEventRecord[] }>('/admin/billing/webhooks'),

  listAudit: () =>
    adminFetch<{ status: string; audit_events: any[] }>('/admin/billing/audit'),

  listTeams: () =>
    adminFetch<{ status: string; teams: any[] }>('/admin/billing/teams')
};

export const auditApi = {
  listLogs: (limit = 100) =>
    adminFetch<{ status: string; audit_logs: AuditLogEvent[] }>(`/admin/audit-logs?limit=${limit}`),

  listTrustEvents: (limit = 100, userId?: string) => {
    const qs = userId ? `?limit=${limit}&user_id=${encodeURIComponent(userId)}` : `?limit=${limit}`;
    return adminFetch<{ status: string; trust_events: any[] }>(`/admin/trust-events${qs}`);
  }
};

export const automationsApi = {
  list: () =>
    adminFetch<{ status: string; automations: AutomationRecord[]; routines: RoutineRecord[] }>('/admin/automations'),

  toggleRoutine: (routineId: string, reason?: string) => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return adminFetch<{ status: string; routine_id: string; active: boolean }>(`/admin/automation/routines/${routineId}/toggle${qs}`, {
      method: 'POST'
    });
  }
};

export const agentsApi = {
  listTasks: (status?: string) => {
    const qs = status ? `?status=${encodeURIComponent(status)}` : '';
    return adminFetch<{ status: string; tasks_count: number; tasks: AgentTaskRecord[] }>(`/admin/agents/tasks${qs}`);
  },

  getDiagnostics: (taskId: string) =>
    adminFetch<{ task: AgentTaskRecord; steps_count: number; steps: any[]; status: string; error_detail?: string }>(`/admin/agents/tasks/${taskId}`),

  cancelTask: (taskId: string, reason?: string) => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return adminFetch<{ status: string; task_id: string; cancelled: boolean }>(`/admin/agents/tasks/${taskId}/cancel${qs}`, {
      method: 'POST'
    });
  },

  recoverTask: (taskId: string, reason?: string) => {
    const qs = reason ? `?reason=${encodeURIComponent(reason)}` : '';
    return adminFetch<{ status: string; task_id: string; recovered: boolean }>(`/admin/agents/tasks/${taskId}/recover${qs}`, {
      method: 'POST'
    });
  },

  listPendingPermissions: () =>
    adminFetch<{ status: string; pending_count: number; pending: any[] }>('/admin/permissions/pending'),

  actionPermission: (reqId: string, action: 'approve' | 'reject', reason?: string) => {
    const q = new URLSearchParams({ action });
    if (reason) q.set('reason', reason);
    return adminFetch<{ status: string }>(`/admin/permissions/${reqId}/action?${q.toString()}`, {
      method: 'POST'
    });
  }
};

export const researchApi = {
  getOverview: () =>
    adminFetch<ResearchOverview>('/admin/research/overview'),

  listRuns: (limit = 50) =>
    adminFetch<{ status: string; runs_count: number; runs: ResearchRunRecord[] }>(`/admin/research/runs?limit=${limit}`)
};

export const systemApi = {
  getHealth: () =>
    adminFetch<SystemHealthData>('/admin/health'),

  runDbCheck: () =>
    adminFetch<{ status: string; integrity_check: string; tables_checked: number }>('/admin/health/db-check', {
      method: 'POST'
    }),

  userLookup: (query: string) =>
    adminFetch<any>(`/admin/diagnostics/user-lookup?user_id_or_email=${encodeURIComponent(query)}`),

  generateDiagnosticBundle: () =>
    adminFetch<{ status: string; bundle: any }>('/admin/diagnostics/bundle', {
      method: 'POST'
    }),

  getVersion: () =>
    adminFetch<{ status: string; app_name: string; version: string; phase: string; environment: string }>('/admin/version'),

  listFeedback: () =>
    adminFetch<{ status: string; feedback: any[] }>('/admin/feedback')
};

export const settingsApi = {
  listFeatureFlags: () =>
    adminFetch<{ status: string; flags: FeatureFlagRecord[] }>('/admin/feature-flags'),

  updateFeatureFlag: (key: string, enabled: boolean, rolloutPercentage = 100) =>
    adminFetch<{ status: string; flag: FeatureFlagRecord }>('/admin/feature-flags/update', {
      method: 'POST',
      body: JSON.stringify({ key, enabled, rollout_percentage: rolloutPercentage })
    }),

  getMaintenance: () =>
    adminFetch<{ status: string; maintenance: MaintenanceModeRecord }>('/admin/maintenance'),

  toggleMaintenance: (enabled: boolean, message?: string, bypassWhitelist?: string) =>
    adminFetch<{ status: string; maintenance: MaintenanceModeRecord }>('/admin/maintenance/toggle', {
      method: 'POST',
      body: JSON.stringify({
        enabled,
        message: message || 'Saarthi is undergoing scheduled system maintenance.',
        bypass_whitelist: bypassWhitelist || '127.0.0.1,admin@saarthi.ai'
      })
    }),

  getAiConfig: () =>
    adminFetch<{ status: string; config: any }>('/admin/ai/config'),

  updateAiConfig: (data: { provider?: string; model_name?: string; temperature?: number; max_tokens?: number; reason?: string }) =>
    adminFetch<{ status: string; config: any }>('/admin/ai/config', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  listToolPolicies: () =>
    adminFetch<{ status: string; tools: ToolPolicyRecord[] }>('/admin/tools'),

  setToolPolicy: (data: { tool_id: string; risk_classification: string; permission_level: string; enabled: boolean }) =>
    adminFetch<{ status: string; policy: any }>('/admin/tools/policy', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  listBans: () =>
    adminFetch<{ status: string; bans: any[] }>('/admin/security/bans'),

  addBan: (data: { identifier: string; ban_type?: string; reason?: string }) =>
    adminFetch<{ status: string; ban: any }>('/admin/security/ban', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  removeBan: (identifier: string) =>
    adminFetch<{ status: string }>('/admin/security/unban', {
      method: 'POST',
      body: JSON.stringify({ identifier })
    })
};

export const opsApi = {
  getHealth: () =>
    adminFetch<OpsHealth>('/ops/health'),

  getMetrics: () =>
    adminFetch<OpsMetrics>('/ops/metrics'),

  getServices: () =>
    adminFetch<OpsService[]>('/ops/services'),

  getServiceDetail: (serviceId: string) =>
    adminFetch<OpsService>(`/ops/services/${serviceId}`),

  getContainers: () =>
    adminFetch<OpsContainersResponse>('/ops/containers'),

  getErrors: (limit: number = 20) =>
    adminFetch<OpsErrorLog[]>(`/ops/errors?limit=${limit}`),

  getSnapshots: (limit: number = 10) =>
    adminFetch<OpsSnapshot[]>(`/ops/snapshots?limit=${limit}`),

  getIncidents: () =>
    adminFetch<OpsIncident[]>('/ops/incidents'),

  diagnose: (data?: { snapshot_id?: string; incident_id?: string; include_recent_errors?: boolean }) =>
    adminFetch<OpsDiagnosis>('/ops/diagnose', {
      method: 'POST',
      body: JSON.stringify(data || {})
    }),

  getAudit: (limit: number = 25) =>
    adminFetch<any[]>(`/ops/audit?limit=${limit}`)
};

export const mcpApi = {
  listServers: () =>
    adminFetch<{ servers: any[] }>('/api/mcp/servers'),

  registerServer: (serverData: any) =>
    adminFetch<{ status: string; server: any }>('/api/mcp/servers', {
      method: 'POST',
      body: JSON.stringify(serverData)
    }),

  deleteServer: (serverId: string) =>
    adminFetch<{ status: string; server_id: string }>(`/api/mcp/servers/${serverId}`, {
      method: 'DELETE'
    }),

  toggleServer: (serverId: string, enabled: boolean) =>
    adminFetch<{ status: string; server_id: string; enabled: boolean }>(`/api/mcp/servers/${serverId}/toggle?enabled=${enabled}`, {
      method: 'POST'
    }),

  testServer: (serverId: string) =>
    adminFetch<{ status: string; server_id: string; tools_discovered: number; tools: any[] }>(`/api/mcp/servers/${serverId}/test`, {
      method: 'POST'
    }),

  listTools: () =>
    adminFetch<{ mcp_tools: any[]; total: number }>('/api/mcp/tools')
};


