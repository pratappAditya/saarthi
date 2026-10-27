import React, { useState, useEffect } from 'react';
import { 
  Shield, Users, CreditCard, Activity, Cpu, Wrench, Terminal, PlayCircle, 
  Lock, AlertTriangle, FileText, Settings, Flag, LifeBuoy, Building, 
  Slash, Info, RefreshCw, CheckCircle2, Search, Power, Trash2, Edit3, X, UserX, UserCheck, DollarSign,
  ShieldCheck, Sparkles
} from 'lucide-react';
import { api } from '../../api';
import { AdminAuthModal } from './AdminAuthModal';

export function AdminControlPanelView() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [loading, setLoading] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  // Section States
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [userQuery, setUserQuery] = useState('');
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [entitlements, setEntitlements] = useState<any>({});
  const [quotas, setQuotas] = useState<any[]>([]);
  const [aiConfig, setAiConfig] = useState<any>(null);
  const [domains, setDomains] = useState<any[]>([]);
  const [tools, setTools] = useState<any[]>([]);
  const [agentTasks, setAgentTasks] = useState<any[]>([]);
  const [routines, setRoutines] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [diagnostics, setDiagnostics] = useState<any>(null);
  const [featureFlags, setFeatureFlags] = useState<any[]>([]);
  const [maintenance, setMaintenance] = useState<any>(null);
  const [feedback, setFeedback] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [ipBans, setIpBans] = useState<any[]>([]);
  const [versionInfo, setVersionInfo] = useState<any>(null);

  // Ops Subsystem States
  const [opsHealth, setOpsHealth] = useState<any>(null);
  const [opsMetrics, setOpsMetrics] = useState<any>(null);
  const [opsServices, setOpsServices] = useState<any[]>([]);
  const [opsDiagnosis, setOpsDiagnosis] = useState<any>(null);
  const [opsDiagnosing, setOpsDiagnosing] = useState<boolean>(false);

  // Check initial admin auth
  useEffect(() => {
    const token = localStorage.getItem('saarthi_admin_token');
    if (token) {
      setIsAuthenticated(true);
      fetchDashboard();
    } else {
      setShowAuthModal(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadTabData(activeTab);
    }
  }, [activeTab, isAuthenticated]);

  const loadTabData = async (tab: string) => {
    setLoading(true);
    try {
      if (tab === 'dashboard') await fetchDashboard();
      else if (tab === 'users') await fetchUsers();
      else if (tab === 'subscriptions') await fetchSubscriptions();
      else if (tab === 'entitlements') await fetchEntitlements();
      else if (tab === 'quotas') await fetchQuotas();
      else if (tab === 'ai-config') await fetchAIConfig();
      else if (tab === 'domains') await fetchDomains();
      else if (tab === 'tools') await fetchTools();
      else if (tab === 'agents') await fetchAgentTasks();
      else if (tab === 'routines') await fetchRoutines();
      else if (tab === 'permissions') await fetchPermissions();
      else if (tab === 'audit') await fetchAuditLogs();
      else if (tab === 'health') await fetchDiagnostics();
      else if (tab === 'flags') await fetchFeatureFlags();
      else if (tab === 'maintenance') await fetchMaintenance();
      else if (tab === 'feedback') await fetchFeedback();
      else if (tab === 'orgs') await fetchOrganizations();
      else if (tab === 'security') await fetchIpBans();
      else if (tab === 'version') await fetchVersion();
      else if (tab === 'ops') await fetchOpsData();
    } catch (err) {
      console.error('Error fetching tab data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboard = async () => {
    const res = await api.getAdminDashboard();
    if (res.status === 'success') setDashboardData(res);
  };

  const fetchUsers = async () => {
    const res = await api.getAdminUsers(userQuery);
    if (res.status === 'success') setUsers(res.users);
  };

  const fetchSubscriptions = async () => {
    const res = await api.getAdminDashboard();
    if (res.status === 'success') setSubscriptions(Object.entries(res.metrics?.plan_breakdown || {}).map(([plan, count]) => ({ plan, count })));
  };

  const fetchEntitlements = async () => {
    const res = await api.getAdminEntitlements();
    if (res.status === 'success') setEntitlements(res.entitlement_matrix);
  };

  const fetchQuotas = async () => {
    const res = await api.getAdminQuotas();
    if (res.status === 'success') setQuotas(res.quotas);
  };

  const fetchAIConfig = async () => {
    const res = await api.getAdminAIConfig();
    if (res.status === 'success') setAiConfig(res.config);
  };

  const fetchDomains = async () => {
    const res = await api.getAdminDomains();
    if (res.status === 'success') setDomains(res.domains);
  };

  const fetchTools = async () => {
    const res = await api.getAdminTools();
    if (res.status === 'success') setTools(res.tools);
  };

  const fetchAgentTasks = async () => {
    const res = await api.getAdminAgentTasks();
    if (res.status === 'success') setAgentTasks(res.tasks);
  };

  const fetchRoutines = async () => {
    const res = await api.getAdminRoutines();
    if (res.status === 'success') setRoutines(res.routines);
  };

  const fetchPermissions = async () => {
    const res = await api.getAdminPendingPermissions();
    if (res.status === 'success') setPermissions(res.pending);
  };

  const fetchAuditLogs = async () => {
    const res = await api.getAdminAuditLogs();
    if (res.status === 'success') setAuditLogs(res.audit_logs);
  };

  const fetchDiagnostics = async () => {
    const res = await api.getAdminDiagnostics();
    if (res.status === 'success') setDiagnostics(res);
  };

  const fetchFeatureFlags = async () => {
    const res = await api.getAdminFeatureFlags();
    if (res.status === 'success') setFeatureFlags(res.flags);
  };

  const fetchMaintenance = async () => {
    const res = await api.getAdminMaintenanceMode();
    if (res.status === 'success') setMaintenance(res.maintenance);
  };

  const fetchFeedback = async () => {
    const res = await api.getAdminFeedback();
    if (res.status === 'success') setFeedback(res.feedback);
  };

  const fetchOrganizations = async () => {
    const res = await api.getAdminOrganizations();
    if (res.status === 'success') setOrganizations(res.organizations);
  };

  const fetchIpBans = async () => {
    const res = await api.getAdminIpBans();
    if (res.status === 'success') setIpBans(res.bans);
  };

  const fetchVersion = async () => {
    const res = await api.getAdminVersion();
    if (res.status === 'success') setVersionInfo(res);
  };

  const fetchOpsData = async () => {
    try {
      const [h, m, s] = await Promise.all([
        api.getOpsHealth().catch(() => null),
        api.getOpsMetrics().catch(() => null),
        api.getOpsServices().catch(() => [])
      ]);
      setOpsHealth(h);
      setOpsMetrics(m);
      setOpsServices(s || []);
    } catch (err) {
      console.error('Error fetching ops data:', err);
    }
  };

  const handleRunOpsDiagnosis = async () => {
    setOpsDiagnosing(true);
    try {
      const res = await api.triggerOpsDiagnosis();
      setOpsDiagnosis(res);
    } catch (err: any) {
      alert(`Ops diagnosis failed: ${err?.message || 'Unknown error'}`);
    } finally {
      setOpsDiagnosing(false);
    }
  };

  // Actions
  const handleUpdatePlan = async (userId: string, newPlan: string) => {
    const res = await api.updateAdminUserPlan(userId, newPlan);
    if (res.status === 'success') {
      setStatusMsg(`User ${userId} upgraded to ${newPlan}`);
      fetchUsers();
    }
  };

  const handleSuspendUser = async (userId: string) => {
    const res = await api.suspendAdminUser(userId, 'Admin Console Action');
    if (res.status === 'success') {
      setStatusMsg(`User ${userId} suspended.`);
      fetchUsers();
    }
  };

  const handleRestoreUser = async (userId: string) => {
    const res = await api.restoreAdminUser(userId, 'Admin Console Restore');
    if (res.status === 'success') {
      setStatusMsg(`User ${userId} restored.`);
      fetchUsers();
    }
  };

  const handleToggleFlag = async (key: string, enabled: boolean, rollout: number) => {
    const res = await api.updateAdminFeatureFlag(key, !enabled, rollout);
    if (res.status === 'success') {
      fetchFeatureFlags();
    }
  };

  const handleToggleMaintenance = async () => {
    if (!maintenance) return;
    const res = await api.toggleAdminMaintenanceMode(!maintenance.enabled, maintenance.message, maintenance.bypass_whitelist);
    if (res.status === 'success') {
      setMaintenance(res.maintenance);
      setStatusMsg(`Maintenance mode ${res.maintenance.enabled ? 'ENABLED' : 'DISABLED'}`);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] text-center p-8 bg-slate-950 text-slate-100 rounded-2xl border border-slate-800">
        <Shield className="w-16 h-16 text-amber-500 mb-4 animate-pulse" />
        <h2 className="text-2xl font-bold mb-2">Saarthi Privileged Control Plane</h2>
        <p className="text-sm text-slate-400 max-w-md mb-6">
          Access to this operational surface requires verified administrative credentials.
        </p>
        <button
          onClick={() => setShowAuthModal(true)}
          className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow-lg transition"
        >
          Authenticate Admin Session
        </button>
        <AdminAuthModal 
          isOpen={showAuthModal} 
          onClose={() => setShowAuthModal(false)}
          onSuccess={(admin) => {
            setIsAuthenticated(true);
            fetchDashboard();
          }}
        />
      </div>
    );
  }

  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: Activity },
    { id: 'users', label: 'User Directory', icon: Users },
    { id: 'subscriptions', label: 'Subscriptions', icon: CreditCard },
    { id: 'entitlements', label: 'Entitlements', icon: Shield },
    { id: 'quotas', label: 'Usage Quotas', icon: RefreshCw },
    { id: 'ai-config', label: 'AI & Models', icon: Cpu },
    { id: 'domains', label: 'Domain Packs', icon: Wrench },
    { id: 'tools', label: 'Tool Policies', icon: Terminal },
    { id: 'agents', label: 'Agent Tasks', icon: PlayCircle },
    { id: 'routines', label: 'Routines', icon: RefreshCw },
    { id: 'permissions', label: 'Risk Queue', icon: Lock },
    { id: 'audit', label: 'Audit Logs', icon: FileText },
    { id: 'health', label: 'System Health', icon: Activity },
    { id: 'ops', label: 'Saarthi Ops', icon: ShieldCheck },
    { id: 'flags', label: 'Feature Flags', icon: Flag },
    { id: 'maintenance', label: 'Maintenance', icon: Power },
    { id: 'feedback', label: 'User Feedback', icon: LifeBuoy },
    { id: 'orgs', label: 'Organizations', icon: Building },
    { id: 'security', label: 'Security & Bans', icon: Slash },
    { id: 'version', label: 'Build Info', icon: Info },
  ];

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-2xl border border-slate-800/80 overflow-hidden shadow-2xl">
      
      {/* Top Admin Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <img src="/saarthi-logo.png" alt="Saarthi — YOUR AI COMPANION" className="w-9 h-9 rounded-xl object-contain shadow-md" />
          <div>
            <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              Saarthi Admin Control Panel
              <span className="px-2 py-0.5 text-[10px] font-mono uppercase bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full">
                Privileged Surface
              </span>
            </h1>
            <p className="text-xs text-slate-400 font-mono">YOUR AI COMPANION &bull; Operational Control Plane &bull; v0.5.0-rc2</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {statusMsg && (
            <span className="text-xs text-emerald-400 font-medium px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
              {statusMsg}
            </span>
          )}
          <button 
            onClick={() => loadTabData(activeTab)} 
            className="p-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300 transition"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button 
            onClick={() => {
              localStorage.removeItem('saarthi_admin_token');
              setIsAuthenticated(false);
            }} 
            className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
          >
            Lock Session
          </button>
        </div>
      </div>

      {/* Main Container */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Admin Navigation Sidebar */}
        <div className="w-64 bg-slate-900/60 border-r border-slate-800 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition ${
                  isActive 
                    ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Area */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-950">

          {/* 1. DASHBOARD */}
          {activeTab === 'dashboard' && dashboardData && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-slate-100">System Overview & Operational Metrics</h2>
              
              <div className="grid grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Total Accounts</div>
                  <div className="text-2xl font-extrabold text-amber-400 mt-1">{dashboardData.metrics.total_users}</div>
                  <div className="text-[11px] text-slate-500 mt-1">{dashboardData.metrics.suspended_users} suspended</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Active Sessions</div>
                  <div className="text-2xl font-extrabold text-emerald-400 mt-1">{dashboardData.metrics.active_sessions}</div>
                  <div className="text-[11px] text-slate-500 mt-1">Active JWT sessions</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Running Agent Tasks</div>
                  <div className="text-2xl font-extrabold text-cyan-400 mt-1">{dashboardData.metrics.running_agent_tasks}</div>
                  <div className="text-[11px] text-slate-500 mt-1">Out of {dashboardData.metrics.total_agent_tasks} total graphs</div>
                </div>
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Maintenance Mode</div>
                  <div className={`text-2xl font-extrabold mt-1 ${dashboardData.metrics.maintenance_mode ? 'text-rose-400' : 'text-slate-400'}`}>
                    {dashboardData.metrics.maintenance_mode ? 'ENABLED' : 'OFF'}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">Operational state</div>
                </div>
              </div>

              {/* Plan Distribution */}
              <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl">
                <h3 className="text-sm font-bold text-slate-200 mb-3">Subscription Tier Distribution</h3>
                <div className="grid grid-cols-6 gap-3">
                  {Object.entries(dashboardData.metrics.plan_breakdown || {}).map(([plan, count]: any) => (
                    <div key={plan} className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-center">
                      <div className="text-xs font-mono font-bold text-amber-400">{plan}</div>
                      <div className="text-lg font-extrabold text-slate-100 mt-1">{count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 2. USER DIRECTORY */}
          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-100">User & Account Directory</h2>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Search by email, name, user_id..."
                    value={userQuery}
                    onChange={(e) => setUserQuery(e.target.value)}
                    className="px-3.5 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-amber-500/60"
                  />
                  <button onClick={fetchUsers} className="px-4 py-2 bg-amber-500 text-slate-950 font-bold text-xs rounded-xl">Search</button>
                </div>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase font-mono">
                    <tr>
                      <th className="p-3.5">User ID</th>
                      <th className="p-3.5">Email / Name</th>
                      <th className="p-3.5">Role</th>
                      <th className="p-3.5">Plan Tier</th>
                      <th className="p-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {users.map((u) => (
                      <tr key={u.user_id} className="hover:bg-slate-800/40">
                        <td className="p-3.5 font-mono text-amber-400/90">{u.user_id}</td>
                        <td className="p-3.5">
                          <div className="font-semibold text-slate-100">{u.full_name || 'Unnamed User'}</div>
                          <div className="text-[11px] text-slate-400">{u.email}</div>
                        </td>
                        <td className="p-3.5">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            u.role === 'SUSPENDED' ? 'bg-rose-500/20 text-rose-300' : 'bg-slate-800 text-slate-300'
                          }`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="p-3.5 font-mono font-bold text-amber-300">{u.subscription_plan}</td>
                        <td className="p-3.5 text-right space-x-2">
                          <select 
                            onChange={(e) => handleUpdatePlan(u.user_id, e.target.value)}
                            value={u.subscription_plan}
                            className="bg-slate-950 border border-slate-700 text-[11px] text-amber-300 rounded px-2 py-1"
                          >
                            <option value="FREE">FREE</option>
                            <option value="STUDENT">STUDENT</option>
                            <option value="PERSONAL">PERSONAL</option>
                            <option value="POWER">POWER</option>
                            <option value="TEAMS">TEAMS</option>
                            <option value="ENTERPRISE">ENTERPRISE</option>
                          </select>

                          {u.role === 'SUSPENDED' ? (
                            <button onClick={() => handleRestoreUser(u.user_id)} className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-[11px] font-bold">Restore</button>
                          ) : (
                            <button onClick={() => handleSuspendUser(u.user_id)} className="px-2 py-1 bg-rose-500/20 text-rose-300 rounded text-[11px] font-bold">Suspend</button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 3. FEATURE FLAGS */}
          {activeTab === 'flags' && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-slate-100">Feature Flags & Controlled Rollouts</h2>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
                {featureFlags.map((flag) => (
                  <div key={flag.key} className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800 rounded-xl">
                    <div>
                      <div className="font-bold text-slate-100 text-sm flex items-center gap-2">
                        {flag.name}
                        <code className="text-xs text-amber-400 font-mono">({flag.key})</code>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">{flag.description}</div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs text-slate-400 font-mono">{flag.rollout_percentage}% rollout</span>
                      <button
                        onClick={() => handleToggleFlag(flag.key, Boolean(flag.enabled), flag.rollout_percentage)}
                        className={`px-4 py-1.5 rounded-xl font-bold text-xs transition ${
                          flag.enabled ? 'bg-emerald-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {flag.enabled ? 'ENABLED' : 'DISABLED'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4. MAINTENANCE MODE */}
          {activeTab === 'maintenance' && maintenance && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-slate-100">System Maintenance Mode Controls</h2>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
                <div className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800 rounded-xl">
                  <div>
                    <div className="font-bold text-slate-100">Global Maintenance Override</div>
                    <div className="text-xs text-slate-400 mt-1">When enabled, non-whitelisted users are blocked from executing agent tasks.</div>
                  </div>
                  <button
                    onClick={handleToggleMaintenance}
                    className={`px-6 py-2.5 rounded-xl font-bold text-xs transition ${
                      maintenance.enabled ? 'bg-rose-500 text-slate-950' : 'bg-emerald-500 text-slate-950'
                    }`}
                  >
                    {maintenance.enabled ? 'MAINTENANCE ACTIVE (CLICK TO DISABLE)' : 'SYSTEM OPERATIONAL (CLICK TO ENABLE)'}
                  </button>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase">Maintenance Message</label>
                  <input
                    type="text"
                    value={maintenance.message || ''}
                    readOnly
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200"
                  />
                </div>
              </div>
            </div>
          )}

          {/* 5. SAARTHI OPS READ-ONLY MONITORING */}
          {activeTab === 'ops' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                    Saarthi Ops — Read-Only Monitoring & Diagnostics
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Passive system telemetry, strict allowlisted service probes, and AI diagnostic reasoning.
                  </p>
                </div>
                <button
                  onClick={handleRunOpsDiagnosis}
                  disabled={opsDiagnosing}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  {opsDiagnosing ? 'Analyzing...' : 'Run AI Diagnosis'}
                </button>
              </div>

              {/* Resource Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="text-[11px] font-mono uppercase text-slate-400">CPU Utilization</div>
                  <div className="text-2xl font-bold font-mono text-slate-100">
                    {opsMetrics?.cpu?.percent_used ?? 0}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {opsMetrics?.cpu?.logical_cores || 1} Logical Cores
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="text-[11px] font-mono uppercase text-slate-400">Memory (RAM)</div>
                  <div className="text-2xl font-bold font-mono text-slate-100">
                    {opsMetrics?.ram?.percent_used ?? 0}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {opsMetrics?.ram?.used_mb ? `${Math.round(opsMetrics.ram.used_mb)} MB` : 'N/A'} used
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                  <div className="text-[11px] font-mono uppercase text-slate-400">Disk Storage</div>
                  <div className="text-2xl font-bold font-mono text-slate-100">
                    {opsMetrics?.disk?.percent_used ?? 0}%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {opsMetrics?.disk?.used_gb ?? 'N/A'} / {opsMetrics?.disk?.total_gb ?? 'N/A'} GB
                  </div>
                </div>
              </div>

              {/* Allowlisted Services Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="px-5 py-3 border-b border-slate-800 text-xs font-semibold text-slate-300">
                  Allowlisted Saarthi Services
                </div>
                <div className="divide-y divide-slate-800">
                  {opsServices.map((svc: any) => (
                    <div key={svc.service_id} className="p-4 flex items-center justify-between text-xs">
                      <div>
                        <div className="font-mono font-medium text-slate-200">{svc.name}</div>
                        <div className="text-[10px] text-slate-500 font-mono">{svc.service_id}</div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[11px] font-mono text-slate-400">{svc.latency_ms} ms</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          svc.status === 'ONLINE' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        }`}>
                          {svc.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Diagnosis Output */}
              {opsDiagnosis && (
                <div className="p-5 bg-slate-900 border border-blue-500/30 rounded-2xl space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold uppercase text-blue-400">
                      AI Diagnostic Synthesis ({opsDiagnosis.diagnostic_mode})
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Confidence: <strong className="text-slate-200">{opsDiagnosis.confidence}</strong>
                    </span>
                  </div>
                  <div className="text-xs text-slate-200 font-medium">
                    {opsDiagnosis.problem_summary}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="p-3 bg-black/40 rounded-xl border border-white/5 space-y-1">
                      <div className="text-[10px] font-mono uppercase text-emerald-400 font-bold">Facts</div>
                      <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                        {opsDiagnosis.facts?.map((f: string, i: number) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="p-3 bg-black/40 rounded-xl border border-white/5 space-y-1">
                      <div className="text-[10px] font-mono uppercase text-amber-400 font-bold">Hypotheses</div>
                      <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                        {opsDiagnosis.hypotheses?.map((h: string, i: number) => (
                          <li key={i}>{h}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-200">
                    <div className="font-bold text-[10px] font-mono uppercase text-purple-300 mb-1">
                      Shared VPS (<HOST_IP>) & Co-located Services Impact
                    </div>
                    {opsDiagnosis.shared_infrastructure_impact?.join(' ')}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {opsDiagnosis.recommendations_disclaimer}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* FALLBACK DEFAULT VIEW FOR OTHER TABS */}
          {activeTab !== 'dashboard' && activeTab !== 'users' && activeTab !== 'flags' && activeTab !== 'maintenance' && activeTab !== 'ops' && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-slate-100 capitalize">{activeTab} Management</h2>
              <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl text-slate-400 text-sm">
                Administrative control plane active for <code className="text-amber-400 font-mono">/api/admin/{activeTab}</code>. Server-side role authorization validated.
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
