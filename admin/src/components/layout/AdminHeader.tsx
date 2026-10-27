import React from 'react';
import { useAdminAuth } from '../../auth/AuthContext';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { Shield, LogOut, Activity } from 'lucide-react';

interface AdminHeaderProps {
  onToggleSidebar?: () => void;
}

export const AdminHeader: React.FC<AdminHeaderProps> = () => {
  const { admin, logout } = useAdminAuth();
  const env = import.meta.env.VITE_APP_ENV || 'development';

  const envVariants: Record<string, 'emerald' | 'amber' | 'rose' | 'slate'> = {
    production: 'rose',
    staging: 'amber',
    development: 'emerald'
  };

  return (
    <header className="h-14 border-b border-white/8 bg-[#0d1118]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center font-bold font-mono text-xs">
            S
          </div>
          <span className="font-bold text-sm tracking-tight text-slate-100 flex items-center gap-2">
            <span>Saarthi</span>
            <span className="text-slate-400 font-normal text-xs">Control Plane</span>
          </span>
        </div>

        <Badge variant={envVariants[env.toLowerCase()] || 'slate'} size="xs" className="ml-2">
          {env}
        </Badge>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-white/6 text-[11px] text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <Activity className="w-3 h-3 text-slate-400 ml-0.5" />
          <span>API Connected</span>
        </div>

        <div className="h-4 w-px bg-white/10" />

        {admin && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-right">
              <div className="hidden md:block">
                <div className="text-xs font-medium text-slate-200 leading-tight">
                  {admin.full_name || admin.email}
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  {admin.role}
                </div>
              </div>
              <div className="w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 text-xs font-semibold">
                <Shield className="w-3.5 h-3.5" />
              </div>
            </div>

            <Button
              id="btn-admin-logout"
              variant="ghost"
              size="sm"
              onClick={logout}
              title="Sign Out"
              className="text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 p-1.5"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};
