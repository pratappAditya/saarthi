import React from 'react';
import { AdminHeader } from './AdminHeader';
import { AdminSidebar, type AdminTab } from './AdminSidebar';
import { Breadcrumbs } from './Breadcrumbs';

interface AdminLayoutProps {
  currentTab: AdminTab;
  onSelectTab: (tab: AdminTab) => void;
  children: React.ReactNode;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({
  currentTab,
  onSelectTab,
  children
}) => {
  return (
    <div className="min-h-screen bg-[#080a0f] flex flex-col">
      <AdminHeader />
      <div className="flex-1 flex overflow-hidden">
        <AdminSidebar currentTab={currentTab} onSelectTab={onSelectTab} />
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            <Breadcrumbs
              currentTab={currentTab}
              onNavigateOverview={() => onSelectTab('overview')}
            />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
