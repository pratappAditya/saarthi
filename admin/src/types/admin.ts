export type AdminRole = 'SUPER_ADMIN' | 'ADMIN' | 'ANALYST' | 'SUPPORT';

export interface AdminUser {
  admin_id: string;
  email: string;
  role: AdminRole;
  full_name?: string;
  auth_method?: string;
}

export interface AdminSession {
  token: string;
  admin: AdminUser;
}

export interface OverviewMetrics {
  total_users: number;
  active_users: number;
  suspended_users: number;
  plan_breakdown: Record<string, number>;
  running_agent_tasks: number;
  failed_agent_tasks: number;
  total_agent_tasks: number;
  active_routines: number;
  total_routines: number;
  system_status: string;
  billing?: {
    active_subscriptions: number;
    mrr_inr: number;
    arr_inr: number;
    failed_payments: number;
    refund_summary: {
      count: number;
      total_amount_inr: number;
    };
    teams_overview?: {
      active_teams: number;
      used_seats: number;
      allocated_seats: number;
      seat_utilization_pct: number;
    };
  };
}

export interface UserRecord {
  user_id: string;
  email: string;
  full_name: string;
  is_verified: number | boolean;
  role: string;
  subscription_plan: string;
  created_at: string;
  updated_at: string;
}

export interface UserDetails {
  user: UserRecord;
  devices: Array<{ device_id: string; last_seen_at?: string; created_at?: string }>;
  sessions: Array<{ session_token: string; created_at?: string; ip_address?: string }>;
  payment_orders: Array<{ order_id: string; amount: number; status: string; created_at: string }>;
  quota: {
    request_count?: number;
    token_count?: number;
    cooldown_until?: string | null;
  };
}

export interface OrganizationMember {
  org_id: string;
  user_id: string;
  role: string;
  status: string;
  joined_at: string;
  email?: string;
  full_name?: string;
}

export interface OrganizationRecord {
  id?: number;
  org_id: string;
  name: string;
  owner_id?: string;
  subscription_plan: string;
  seat_limit: number;
  status?: string;
  created_at: string;
  updated_at: string;
  member_count?: number;
  members?: OrganizationMember[];
}

export interface PlanDefinition {
  id: string;
  name: string;
  price_inr: number;
  currency: string;
  interval: string;
  badge: string;
  description: string;
  is_custom: boolean;
  version: string;
  capabilities: string[];
  limits: Record<string, any>;
}

export interface SubscriptionRecord {
  id?: number;
  subscription_id: string;
  user_id: string;
  org_id?: string | null;
  plan_name: string;
  plan_version?: string;
  provider: string;
  status: string;
  seat_count: number;
  price_per_unit: number;
  total_amount: number;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: number | boolean;
  canceled_at?: string | null;
  created_at: string;
  updated_at: string;
  user_email?: string;
}

export interface PaymentRecord {
  id?: number;
  payment_id: string;
  order_id: string;
  user_id: string;
  org_id?: string | null;
  provider: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
  user_email?: string;
  plan_name?: string;
  seats?: number;
}

export interface InvoiceRecord {
  id?: number;
  invoice_id: string;
  subscription_id: string;
  user_id: string;
  org_id?: string | null;
  amount: number;
  currency: string;
  status: string;
  billing_reason?: string;
  created_at: string;
  user_email?: string;
}

export interface RefundRecord {
  id?: number;
  refund_id: string;
  payment_id: string;
  user_id: string;
  amount: number;
  reason: string;
  status: string;
  created_at: string;
  user_email?: string;
}

export interface WebhookEventRecord {
  id?: number;
  event_id: string;
  provider: string;
  event_type: string;
  payload_json?: string;
  processed_at: string;
}

export interface AuditLogEvent {
  id?: number;
  audit_id?: string;
  admin_id: string;
  action: string;
  target?: string;
  reason?: string;
  previous_state_json?: string;
  resulting_state_json?: string;
  request_metadata_json?: string;
  timestamp: string;
}

export interface AutomationRecord {
  automation_id: string;
  name: string;
  description?: string;
  user_id: string;
  organization_id?: string | null;
  scope: string;
  domain: string;
  status: string;
  enabled: number | boolean;
  created_at: number;
  updated_at: number;
  next_run_at?: number | null;
  last_run_at?: number | null;
}

export interface RoutineRecord {
  id: string;
  name: string;
  description?: string;
  owner_user_id: string;
  trigger_type: string;
  schedule?: string;
  timezone?: string;
  status: string;
}

export interface AgentTaskRecord {
  task_id: string;
  description: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  error?: string | null;
  steps?: any[];
}

export interface ResearchDomain {
  id: string;
  name: string;
  description: string;
  tier: string;
}

export interface ResearchOverview {
  total_domains: number;
  domains: ResearchDomain[];
  cache_entries_count: number;
  active_providers: string[];
}

export interface ResearchRunRecord {
  id: string;
  event_type: string;
  domain: string;
  status: string;
  sources_count: number;
  timestamp: string;
}

export interface SystemHealthData {
  status: string;
  services?: Record<string, { status: string; latency_ms?: number }>;
  database?: { status: string; driver?: string };
  timestamp?: string;
  version?: string;
  uptime_seconds?: number;
}

export interface ToolPolicyRecord {
  id: string;
  name: string;
  description: string;
  risk_classification: string;
  permission_level: string;
  enabled: boolean;
}

export interface FeatureFlagRecord {
  key: string;
  enabled: number | boolean;
  rollout_percentage: number;
  description?: string;
}

export interface MaintenanceModeRecord {
  enabled: boolean;
  message: string;
  bypass_whitelist: string;
}

// --- SAARTHI OPS TYPES ---

export interface OpsHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unavailable';
  timestamp: string;
  last_collection_timestamp: string | null;
  services_count: number;
  services_online: number;
  active_incidents_count: number;
  recent_errors_count: number;
}

export interface OpsMetrics {
  status: 'available' | 'unavailable';
  timestamp: string;
  reason?: string;
  cpu?: {
    percent_used: number;
    logical_cores: number;
  };
  ram?: {
    total_mb: number;
    available_mb: number;
    used_mb: number;
    percent_used: number;
  };
  disk?: {
    total_gb: number;
    free_gb: number;
    used_gb: number;
    percent_used: number;
  };
  uptime?: {
    process_seconds: number;
    system_seconds: number;
  };
  active_requests?: number;
  total_requests?: number;
}

export interface OpsService {
  service_id: string;
  name: string;
  status: 'ONLINE' | 'DEGRADED' | 'OFFLINE' | 'UNAVAILABLE';
  latency_ms: number;
  last_checked: string;
  endpoint?: string;
  integrity?: string;
}

export interface OpsContainer {
  name: string;
  service: string;
  status: string;
  read_only: boolean;
}

export interface OpsContainersResponse {
  status: 'available' | 'unavailable';
  reason?: string;
  timestamp: string;
  containers: OpsContainer[];
}

export interface OpsErrorLog {
  timestamp: string;
  level: string;
  source: string;
  message: string;
  details?: Record<string, any>;
}

export interface OpsIncident {
  incident_id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  affected_service: string;
  detected_at: string;
  evidence: string;
  status: 'ACTIVE' | 'RESOLVED';
}

export interface OpsSnapshot {
  snapshot_id: string;
  timestamp: string;
  overall_health: string;
  metrics: OpsMetrics;
  services: OpsService[];
  recent_errors_count: number;
  recent_errors_sample: OpsErrorLog[];
}

export interface OpsDiagnosis {
  problem_summary: string;
  overall_health: string;
  facts: string[];
  hypotheses: string[];
  evidence: string[];
  missing_evidence: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  safe_investigation_steps: string[];
  shared_infrastructure_impact: string[];
  recommendations_disclaimer: string;
  diagnostic_mode: string;
}

