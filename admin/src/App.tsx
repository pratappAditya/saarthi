import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { AdminLayout } from './components/layout/AdminLayout';
import type { AdminTab } from './components/layout/AdminSidebar';
import { LoginPage } from './pages/LoginPage';
import { OverviewPage } from './pages/OverviewPage';
import { UsersPage } from './pages/UsersPage';
import { OrganizationsPage } from './pages/OrganizationsPage';
import { PlansPage } from './pages/PlansPage';
import { BillingPage } from './pages/BillingPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { AutomationsPage } from './pages/AutomationsPage';
import { AgentsPage } from './pages/AgentsPage';
import { ResearchPage } from './pages/ResearchPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { OpsDashboardPage } from './pages/OpsDashboardPage';
import { SettingsPage } from './pages/SettingsPage';
import { MCPIntegrationsPage } from './pages/MCPIntegrationsPage';
import { LoadingSpinner } from './components/common/LoadingSpinner';

const AdminApp: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState<AdminTab>(() => {
    const hash = window.location.hash.replace('#', '') as AdminTab;
    const validTabs: AdminTab[] = [
      'overview',
      'users',
      'organizations',
      'plans',
      'billing-subscriptions',
      'billing-payments',
      'billing-invoices',
      'billing-refunds',
      'billing-webhooks',
      'audit-logs',
      'automations',
      'agents',
      'mcp',
      'research',
      'system',
      'ops',
      'settings'
    ];
    return validTabs.includes(hash) ? hash : 'overview';
  });

  useEffect(() => {
    window.location.hash = currentTab;
  }, [currentTab]);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '') as AdminTab;
      if (hash && hash !== currentTab) {
        setCurrentTab(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [currentTab]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080a0f] flex flex-col items-center justify-center space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-sm text-slate-400 font-mono tracking-wider">
          INITIALIZING SAARTHI CONTROL PLANE...
        </span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <OverviewPage />;
      case 'users':
        return <UsersPage />;
      case 'organizations':
        return <OrganizationsPage />;
      case 'plans':
        return <PlansPage />;
      case 'billing-subscriptions':
      case 'billing-payments':
      case 'billing-invoices':
      case 'billing-refunds':
      case 'billing-webhooks':
        return <BillingPage />;
      case 'audit-logs':
        return <AuditLogsPage />;
      case 'automations':
        return <AutomationsPage />;
      case 'agents':
        return <AgentsPage />;
      case 'mcp':
        return <MCPIntegrationsPage />;
      case 'research':
        return <ResearchPage />;
      case 'system':
        return <SystemHealthPage />;
      case 'ops':
        return <OpsDashboardPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <AdminLayout currentTab={currentTab} onSelectTab={setCurrentTab}>
      {renderContent()}
    </AdminLayout>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AdminApp />
    </AuthProvider>
  );
}
