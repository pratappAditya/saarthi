import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import type { AdminTab } from './AdminSidebar';

interface BreadcrumbsProps {
  currentTab: AdminTab;
  onNavigateOverview: () => void;
}

const tabLabels: Record<AdminTab, { category: string; label: string }> = {
  overview: { category: 'Operations', label: 'Overview' },
  users: { category: 'Operations', label: 'Users' },
  organizations: { category: 'Operations', label: 'Organizations & Teams' },
  plans: { category: 'Operations', label: 'Plans & Entitlements' },
  'billing-subscriptions': { category: 'Billing Center', label: 'Subscriptions' },
  'billing-payments': { category: 'Billing Center', label: 'Payments' },
  'billing-invoices': { category: 'Billing Center', label: 'Invoices' },
  'billing-refunds': { category: 'Billing Center', label: 'Refunds' },
  'billing-webhooks': { category: 'Billing Center', label: 'Webhooks' },
  'audit-logs': { category: 'Governance', label: 'Audit Logs' },
  automations: { category: 'Intelligence', label: 'Automations & Routines' },
  agents: { category: 'Intelligence', label: 'Agent Tasks & Diagnostics' },
  mcp: { category: 'Intelligence', label: 'MCP Integrations' },
  research: { category: 'Intelligence', label: 'Research Operations' },
  system: { category: 'Governance', label: 'System Health' },
  ops: { category: 'Governance', label: 'Saarthi Ops' },
  settings: { category: 'Governance', label: 'Settings & Feature Flags' }
};

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ currentTab, onNavigateOverview }) => {
  const meta = tabLabels[currentTab] || { category: 'Control Plane', label: currentTab };

  return (
    <nav className="flex items-center gap-1.5 text-xs text-slate-400 mb-6">
      <button
        onClick={onNavigateOverview}
        className="flex items-center gap-1 hover:text-slate-200 transition-colors"
      >
        <Home className="w-3.5 h-3.5" />
        <span>Control Plane</span>
      </button>
      <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
      <span className="text-slate-400">{meta.category}</span>
      <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
      <span className="font-semibold text-slate-200">{meta.label}</span>
    </nav>
  );
};
