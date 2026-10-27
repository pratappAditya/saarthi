import React from 'react';
import { useAdminAuth } from './AuthContext';
import type { AdminRole } from '../types/admin';
import { ShieldAlert, LogIn } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: AdminRole[];
  onNavigateToLogin: () => void;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
  onNavigateToLogin
}) => {
  const { isAuthenticated, isLoading, role } = useAdminAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#080a0f] flex flex-col items-center justify-center space-y-4">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs text-slate-400 font-mono tracking-wider uppercase">Verifying control plane session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#080a0f] flex flex-col items-center justify-center p-6 text-center">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full shadow-2xl space-y-4">
          <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl flex items-center justify-center mx-auto">
            <LogIn className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100">Authentication Required</h2>
            <p className="text-xs text-slate-400 mt-1">You must sign in with verified administrative credentials to access the control plane.</p>
          </div>
          <button
            onClick={onNavigateToLogin}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition-colors shadow-lg shadow-blue-600/20"
          >
            Go to Admin Login
          </button>
        </div>
      </div>
    );
  }

  if (allowedRoles && role && !allowedRoles.includes(role) && role !== 'SUPER_ADMIN') {
    return (
      <div className="min-h-screen bg-[#080a0f] flex flex-col items-center justify-center p-6 text-center">
        <div className="p-6 bg-slate-900 border border-red-500/20 rounded-2xl max-w-md w-full shadow-2xl space-y-4">
          <div className="w-12 h-12 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center justify-center mx-auto">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100">403 — Unauthorized Role</h2>
            <p className="text-xs text-slate-400 mt-1">
              Your role <span className="font-mono text-amber-400 font-semibold">{role}</span> does not have permission to view this section. Required: {allowedRoles.join(', ')}.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
