import React, { useState, useEffect } from 'react';
import { plansApi } from '../api/adminApi';
import type { PlanDefinition } from '../types/admin';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { 
  CreditCard, 
  CheckCircle2, 
  Zap, 
  Sliders, 
  RefreshCw, 
  Search
} from 'lucide-react';

export const PlansPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [plans, setPlans] = useState<PlanDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Entitlement Inspection State
  const [inspectUserId, setInspectUserId] = useState('');
  const [inspectResult, setInspectResult] = useState<any | null>(null);
  const [inspectLoading, setInspectLoading] = useState(false);
  const [inspectError, setInspectError] = useState<string | null>(null);

  // Override Modal State
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [overrideUserId, setOverrideUserId] = useState('');
  const [overridePlan, setOverridePlan] = useState('POWER');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSubmitting, setOverrideSubmitting] = useState(false);

  const fetchPlans = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await plansApi.getCatalog();
      setPlans(res.catalog || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch plan catalog from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleInspectUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inspectUserId.trim()) return;
    setInspectLoading(true);
    setInspectError(null);
    try {
      const res = await plansApi.inspectUser(inspectUserId.trim());
      setInspectResult(res);
    } catch (err: any) {
      setInspectError(err?.message || 'Failed to inspect user entitlements.');
      setInspectResult(null);
    } finally {
      setInspectLoading(false);
    }
  };

  const handleApplyOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideUserId.trim()) return;
    setOverrideSubmitting(true);
    try {
      await plansApi.override({
        user_id: overrideUserId.trim(),
        plan_override: overridePlan,
        reason: overrideReason.trim() || 'Manual administrative entitlement override'
      });
      alert(`Entitlement override applied successfully for user ${overrideUserId}`);
      setOverrideModalOpen(false);
      // Refresh inspection if inspected
      if (inspectUserId.trim() === overrideUserId.trim()) {
        const res = await plansApi.inspectUser(overrideUserId.trim());
        setInspectResult(res);
      }
    } catch (err: any) {
      alert(`Failed to apply override: ${err?.message || 'Unknown error'}`);
    } finally {
      setOverrideSubmitting(false);
    }
  };

  const canManage = hasRole(['SUPER_ADMIN', 'ADMIN']);

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <CreditCard className="w-6 h-6 text-indigo-400" />
            Plan Registry & Entitlements
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Canonical backend Plan Catalog, tier quotas, capabilities matrix, and user entitlement overrides.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchPlans} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Catalog
          </Button>
          {canManage && (
            <Button size="sm" onClick={() => setOverrideModalOpen(true)}>
              <Sliders className="w-4 h-4 mr-2" />
              Entitlement Override
            </Button>
          )}
        </div>
      </div>

      {/* Plan Catalog Grid */}
      {loading ? (
        <Card className="p-12 flex justify-center items-center">
          <LoadingSpinner size="lg" />
        </Card>
      ) : error ? (
        <Card className="p-8 text-center border-rose-900/40 bg-rose-950/20 text-rose-300">
          <p className="font-semibold">{error}</p>
          <Button variant="outline" size="sm" onClick={fetchPlans} className="mt-4">
            Retry
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((p) => {
            const isTeams = p.id.toUpperCase() === 'TEAMS' || p.id.toUpperCase() === 'ENTERPRISE';
            return (
              <Card
                key={p.id}
                orientation="none"
                className={`flex flex-col justify-between p-6 border ${
                  isTeams ? 'border-indigo-600/40 bg-indigo-950/10' : 'border-slate-800 bg-slate-900/60'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-lg font-bold text-slate-100">{p.name}</span>
                    <Badge variant={isTeams ? 'purple' : 'indigo'}>
                      v{p.version || '2.0'}
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-400 min-h-[32px]">{p.description}</p>

                  <div className="mt-4 mb-6">
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-extrabold text-slate-100">
                        {p.is_custom ? 'Custom' : `₹${p.price_inr?.toLocaleString()}`}
                      </span>
                      {!p.is_custom && (
                        <span className="text-xs text-slate-400">/{p.interval}</span>
                      )}
                    </div>
                    {p.badge && (
                      <span className="inline-block mt-1 text-[11px] font-semibold tracking-wider text-indigo-400 uppercase">
                        {p.badge}
                      </span>
                    )}
                  </div>

                  {/* Quotas & Limits */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 mb-4 space-y-1.5 text-xs">
                    <div className="font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      Usage & Capacity Limits
                    </div>
                    {p.limits && Object.entries(p.limits).map(([key, val]) => (
                      <div key={key} className="flex justify-between text-slate-400">
                        <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-mono text-slate-200">
                          {typeof val === 'number' && val >= 999999 ? 'Unlimited' : String(val)}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Capabilities */}
                  <div className="space-y-1.5 mb-6 text-xs text-slate-300">
                    <div className="font-semibold text-slate-400 mb-2">Capabilities Included:</div>
                    {p.capabilities?.slice(0, 6).map((cap, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span className="truncate">{cap}</span>
                      </div>
                    ))}
                    {p.capabilities && p.capabilities.length > 6 && (
                      <span className="text-[11px] text-slate-500 italic block pl-5">
                        +{p.capabilities.length - 6} more capabilities
                      </span>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>Plan ID: {p.id}</span>
                  <Badge variant="neutral">Active</Badge>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* User Entitlements Inspector */}
      <Card orientation="none" className="p-6 border border-slate-800 bg-slate-900/60">
        <div className="max-w-2xl">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Search className="w-5 h-5 text-indigo-400" />
            Inspect User Entitlements
          </h2>
          <p className="text-xs text-slate-400 mt-1 mb-4">
            Verify actual resolved capabilities, active plan tier, and real-time quota evaluations for a specific user ID.
          </p>

          <form onSubmit={handleInspectUser} className="flex gap-3">
            <input
              type="text"
              required
              value={inspectUserId}
              onChange={(e) => setInspectUserId(e.target.value)}
              placeholder="Enter User ID (e.g. usr_123 or user-uuid)..."
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
            />
            <Button type="submit" disabled={inspectLoading}>
              {inspectLoading ? 'Evaluating...' : 'Inspect Entitlements'}
            </Button>
          </form>

          {inspectError && (
            <div className="mt-4 p-3 bg-rose-950/30 border border-rose-900/50 rounded-lg text-xs text-rose-300">
              {inspectError}
            </div>
          )}

          {inspectResult && (
            <div className="mt-6 p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="text-xs text-slate-400">Resolved Plan Tier:</span>
                  <div className="text-base font-bold text-slate-100 mt-0.5">{inspectResult.plan}</div>
                </div>
                {canManage && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setOverrideUserId(inspectUserId);
                      setOverridePlan(inspectResult.plan);
                      setOverrideModalOpen(true);
                    }}
                  >
                    Override Entitlements
                  </Button>
                )}
              </div>

              {inspectResult.limits && (
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Current Limits
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {Object.entries(inspectResult.limits).map(([k, v]) => (
                      <div key={k} className="p-2 bg-slate-900 rounded border border-slate-800 text-xs">
                        <div className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}</div>
                        <div className="font-mono text-slate-100 font-semibold mt-0.5">{String(v)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {inspectResult.capabilities && (
                <div>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Resolved Capabilities
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {Array.isArray(inspectResult.capabilities) ? (
                      inspectResult.capabilities.map((c: string, idx: number) => (
                        <Badge key={idx} variant="indigo">
                          {c}
                        </Badge>
                      ))
                    ) : (
                      <pre className="text-[11px] font-mono text-slate-300">
                        {JSON.stringify(inspectResult.capabilities, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Override Modal */}
      <Modal
        isOpen={overrideModalOpen}
        onClose={() => setOverrideModalOpen(false)}
        title="Override User Entitlements"
      >
        <form onSubmit={handleApplyOverride} className="space-y-4">
          <p className="text-xs text-slate-300">
            Applying an entitlement override immediately updates the user's effective capabilities and limits
            without requiring a financial transaction. All overrides are logged in the Admin Audit Trail.
          </p>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              User ID
            </label>
            <input
              type="text"
              required
              value={overrideUserId}
              onChange={(e) => setOverrideUserId(e.target.value)}
              placeholder="e.g. usr_123..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Effective Plan Override
            </label>
            <select
              value={overridePlan}
              onChange={(e) => setOverridePlan(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="FREE">Free</option>
              <option value="STUDENT">Student</option>
              <option value="PERSONAL">Personal</option>
              <option value="POWER">Power</option>
              <option value="TEAMS">Teams</option>
              <option value="ENTERPRISE">Enterprise</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
              Audit Reason
            </label>
            <textarea
              required
              rows={2}
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              placeholder="Provide justification for manual override..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <Button variant="ghost" type="button" onClick={() => setOverrideModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={overrideSubmitting}>
              {overrideSubmitting ? 'Applying...' : 'Confirm Override'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
