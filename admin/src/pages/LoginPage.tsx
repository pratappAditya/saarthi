import React, { useState } from 'react';
import { useAdminAuth } from '../auth/AuthContext';
import { Shield, Key, Mail, Lock, AlertCircle } from 'lucide-react';
import { Button } from '../components/common/Button';

interface LoginPageProps {
  onSuccess?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess }) => {
  const { loginWithKey, loginWithCredentials, isLoading } = useAdminAuth();
  const [authMode, setAuthMode] = useState<'key' | 'credentials'>('key');

  const [adminKey, setAdminKey] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (authMode === 'key') {
        if (!adminKey.trim()) {
          setError('Admin Secret Key is required.');
          return;
        }
        await loginWithKey(adminKey.trim());
      } else {
        if (!email.trim() || !password.trim()) {
          setError('Email and password are required.');
          return;
        }
        await loginWithCredentials(email.trim(), password.trim());
      }
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    }
  };

  return (
    <div className="min-h-screen bg-[#080a0f] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#0d1118] border border-white/10 rounded-2xl shadow-2xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-blue-600/15 border border-blue-500/30 text-blue-400 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-blue-500/10">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Saarthi Control Plane</h1>
          <p className="text-xs text-slate-400">Restricted administrative access for authorized operators only</p>
        </div>

        {/* Tab selection */}
        <div className="flex p-1 bg-slate-900 border border-white/6 rounded-lg text-xs">
          <button
            id="tab-secret-key"
            type="button"
            onClick={() => { setAuthMode('key'); setError(null); }}
            className={`flex-1 py-1.5 rounded-md font-medium transition-colors ${
              authMode === 'key'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Secret Key
          </button>
          <button
            id="tab-credentials"
            type="button"
            onClick={() => { setAuthMode('credentials'); setError(null); }}
            className={`flex-1 py-1.5 rounded-md font-medium transition-colors ${
              authMode === 'credentials'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Email & Password
          </button>
        </div>

        {error && (
          <div id="admin-login-error" className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-start gap-2 text-rose-400 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {authMode === 'key' ? (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Admin Master Secret Key
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-2.5 text-slate-500 pointer-events-none" />
                <input
                  id="input-admin-key"
                  type="password"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  placeholder="Enter administrator key..."
                  className="w-full pl-9 pr-3 py-2 text-xs bg-slate-900 border border-white/10 rounded-lg text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
                  autoFocus
                />
              </div>
            </div>
          ) : (
            <>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Admin Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-2.5 text-slate-500 pointer-events-none" />
                  <input
                    id="input-admin-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@saarthi.local"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-900 border border-white/10 rounded-lg text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500 pointer-events-none" />
                  <input
                    id="input-admin-password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full pl-9 pr-3 py-2 text-xs bg-slate-900 border border-white/10 rounded-lg text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono"
                  />
                </div>
              </div>
            </>
          )}

          <Button
            id="btn-admin-submit"
            type="submit"
            variant="primary"
            size="lg"
            className="w-full mt-2"
            isLoading={isLoading}
          >
            Authenticate Control Plane
          </Button>
        </form>

        <div className="pt-4 border-t border-white/6 text-center text-[11px] text-slate-400 font-mono">
          Immutable audit trails active on all admin operations.
        </div>
      </div>
    </div>
  );
};
