import React, { useState } from 'react';
import { Shield, Key, Lock, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { api } from '../../api';

interface AdminAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (admin: any) => void;
}

export function AdminAuthModal({ isOpen, onClose, onSuccess }: AdminAuthModalProps) {
  const [authMode, setAuthMode] = useState<'key' | 'credentials'>('key');
  const [adminKey, setAdminKey] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = authMode === 'key' 
        ? { admin_key: adminKey }
        : { email, password };

      const res = await api.adminLogin(payload);
      if (res.status === 'success' && res.token) {
        localStorage.setItem('saarthi_admin_token', res.token);
        onSuccess(res.admin);
        onClose();
      } else {
        setError(res.detail || res.message || 'Authentication failed.');
      }
    } catch (err: any) {
      setError(err.message || 'Server connection error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-slate-900 border border-amber-500/30 rounded-2xl shadow-2xl overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border-b border-amber-500/20">
          <div className="flex items-center gap-3">
            <img src="/saarthi-logo.png" alt="Saarthi — YOUR AI COMPANION" className="w-10 h-10 rounded-xl object-contain shadow-md" />
            <div>
              <h3 className="text-lg font-bold text-slate-100">Saarthi Admin Control Plane</h3>
              <p className="text-xs text-amber-400/80 font-mono">YOUR AI COMPANION — PRIVILEGED SURFACE</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleLogin} className="p-6 space-y-5">
          {error && (
            <div className="flex items-start gap-3 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Mode Switcher */}
          <div className="grid grid-cols-2 p-1 bg-slate-950 border border-slate-800 rounded-xl text-xs font-medium">
            <button
              type="button"
              onClick={() => setAuthMode('key')}
              className={`py-2 rounded-lg transition ${authMode === 'key' ? 'bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Secret Key
            </button>
            <button
              type="button"
              onClick={() => setAuthMode('credentials')}
              className={`py-2 rounded-lg transition ${authMode === 'credentials' ? 'bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/40' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Admin Account
            </button>
          </div>

          {authMode === 'key' ? (
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-amber-400" />
                Vendor Admin Key
              </label>
              <input
                type="password"
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
                placeholder="Enter secret vendor admin key..."
                required
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-amber-300 focus:outline-none focus:border-amber-500/60 placeholder:text-slate-600"
              />
            </div>
          ) : (
            <>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Admin Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@saarthi.ai"
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-amber-500/60 placeholder:text-slate-600"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-amber-400" />
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-amber-500/60 placeholder:text-slate-600"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-sm rounded-xl shadow-lg shadow-amber-500/20 transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Authenticating...</span>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                <span>Authenticate Admin Session</span>
              </>
            )}
          </button>
        </form>

        <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 text-[11px] text-slate-500 text-center">
          Strict Audit Trail Enabled &bull; All administrative actions logged to <code className="text-amber-400/80">admin_audit_log</code>
        </div>
      </div>
    </div>
  );
}
