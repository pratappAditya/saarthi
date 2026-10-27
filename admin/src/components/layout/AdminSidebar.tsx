import React from 'react';
import { useAdminAuth } from '../../auth/AuthContext';
import {
  LayoutDashboard,
  Users,
  Building2,
  Layers,
  CreditCard,
  FileText,
  RotateCcw,
  Webhook,
  History,
  Workflow,
  Bot,
  Search,
  Activity,
  ShieldCheck,
  Settings,
  ChevronDown
} from 'lucide-react';

export type AdminTab =
  | 'overview'
  | 'users'
  | 'organizations'
  | 'plans'
  | 'billing-subscriptions'
  | 'billing-payments'
  | 'billing-invoices'
  | 'billing-refunds'
  | 'billing-webhooks'
  | 'audit-logs'
  | 'automations'
  | 'agents'
  | 'mcp'
  | 'research'
  | 'system'
  | 'ops'
  | 'settings';

interface AdminSidebarProps {
  currentTab: AdminTab;
  onSelectTab: (tab: AdminTab) => void;
}

export const AdminSidebar: React.FC<AdminSidebarProps> = ({ currentTab, onSelectTab }) => {
  const { role } = useAdminAuth();
  const [billingOpen, setBillingOpen] = React.useState(true);

  const isBillingActive = currentTab.startsWith('billing-');

  const navItem = (
    tab: AdminTab,
    label: string,
    icon: React.ReactNode,
    badge?: string,
    minRole?: 'SUPER_ADMIN' | 'ADMIN'
  ) => {
    if (minRole && role !== 'SUPER_ADMIN' && role !== minRole) {
      return null;
    }

    const isActive = currentTab === tab;
    return (
      <button
        onClick={() => onSelectTab(tab)}
        className={`w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-lg transition-colors text-left ${
          isActive
            ? 'bg-blue-600/15 text-blue-400 font-semibold border border-blue-500/30'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
        }`}
      >
        <span className="flex items-center gap-2.5">
          <span className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400'}`}>
            {icon}
          </span>
          <span>{label}</span>
        </span>
        {badge && (
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-white/5">
            {badge}
          </span>
        )}
      </button>
    );
  };

  return (
    <aside className="w-60 shrink-0 border-r border-white/8 bg-[#090c12] p-3 flex flex-col justify-between h-[calc(100vh-3.5rem)] sticky top-14 overflow-y-auto">
      <div className="space-y-6">
        {/* Core Operations */}
        <div className="space-y-1">
          <div className="px-3 pb-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
            Operations
          </div>
          {navItem('overview', 'Overview', <LayoutDashboard className="w-4 h-4" />)}
          {navItem('users', 'Users', <Users className="w-4 h-4" />)}
          {navItem('organizations', 'Organizations', <Building2 className="w-4 h-4" />)}
          {navItem('plans', 'Plans & Tiers', <Layers className="w-4 h-4" />)}
        </div>

        {/* Financial & Billing */}
        <div className="space-y-1">
          <button
            onClick={() => setBillingOpen(!billingOpen)}
            className={`w-full flex items-center justify-between px-3 pb-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider ${
              isBillingActive ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-300'
            }`}
          >
            <span>Billing Center</span>
            <ChevronDown className={`w-3 h-3 transition-transform ${billingOpen ? '' : '-rotate-90'}`} />
          </button>

          {billingOpen && (
            <div className="pl-2 space-y-0.5 border-l border-white/6 ml-2">
              {navItem('billing-subscriptions', 'Subscriptions', <CreditCard className="w-3.5 h-3.5" />)}
              {navItem('billing-payments', 'Payments', <CreditCard className="w-3.5 h-3.5" />)}
              {navItem('billing-invoices', 'Invoices', <FileText className="w-3.5 h-3.5" />)}
              {navItem('billing-refunds', 'Refunds', <RotateCcw className="w-3.5 h-3.5" />)}
              {navItem('billing-webhooks', 'Webhooks', <Webhook className="w-3.5 h-3.5" />)}
            </div>
          )}
        </div>

        {/* Intelligence & Automation */}
        <div className="space-y-1">
          <div className="px-3 pb-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
            Intelligence Engine
          </div>
          {navItem('automations', 'Automations', <Workflow className="w-4 h-4" />)}
          {navItem('agents', 'Agent Tasks', <Bot className="w-4 h-4" />)}
          {navItem('mcp', 'MCP Integrations', <Layers className="w-4 h-4 text-indigo-400" />)}
          {navItem('research', 'Research Operations', <Search className="w-4 h-4" />)}
        </div>

        {/* Governance & System */}
        <div className="space-y-1">
          <div className="px-3 pb-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400">
            Governance
          </div>
          {navItem('audit-logs', 'Audit Logs', <History className="w-4 h-4" />)}
          {navItem('system', 'System Health', <Activity className="w-4 h-4" />)}
          {navItem('ops', 'Saarthi Ops', <ShieldCheck className="w-4 h-4 text-emerald-400" />)}
          {navItem('settings', 'Settings & Flags', <Settings className="w-4 h-4" />, undefined, 'ADMIN')}
        </div>
      </div>

      <div className="pt-4 border-t border-white/6 px-3 text-[11px] text-slate-400 font-mono">
        <div>Saarthi OS v0.5.0</div>
        <div className="text-[10px] text-slate-400 mt-0.5">Control Plane Ready</div>
      </div>
    </aside>
  );
};
