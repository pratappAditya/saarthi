import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../api/adminApi';
import type { OverviewMetrics } from '../types/admin';
import { StatCard } from '../components/common/StatCard';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Users,
  DollarSign,
  Bot,
  Workflow,
  AlertTriangle,
  Layers,
  ArrowUpRight,
  RefreshCw
} from 'lucide-react';
import type { AdminTab } from '../components/layout/AdminSidebar';

interface OverviewPageProps {
  onNavigateTab?: (tab: AdminTab) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigateTab }) => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardApi.getOverview();
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch operational metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating control plane metrics..." size="lg" />;

  if (error || !metrics) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-xl text-center space-y-3">
        <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
        <h3 className="text-sm font-semibold text-rose-300">Metrics Unavailable</h3>
        <p className="text-xs text-rose-400/80">{error || 'Unknown error fetching backend overview.'}</p>
        <Button variant="secondary" size="sm" onClick={fetchOverview} leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
          Retry Connection
        </Button>
      </div>
    );
  }

  const planEntries = Object.entries(metrics.plan_breakdown || {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Operations Overview</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time health, monetization telemetry, and autonomous engine activity</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchOverview} leftIcon={<RefreshCw className="w-3 h-3" />}>
            Refresh
          </Button>
          <Button variant="primary" size="sm" onClick={() => onNavigateTab?.('users')} leftIcon={<Users className="w-3 h-3" />}>
            Manage Users
          </Button>
        </div>
      </div>

      {/* Top Stat Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Registered Users"
          value={metrics.total_users}
          icon={<Users className="w-4 h-4 text-blue-400" />}
          subtext={`${metrics.active_users} active · ${metrics.suspended_users} suspended`}
          badge={{ text: 'ACCOUNTS', variant: 'blue' }}
        />
        <StatCard
          label="Monthly Recurring Revenue"
          value={`₹${(metrics.billing?.mrr_inr || 0).toLocaleString('en-IN')}`}
          icon={<DollarSign className="w-4 h-4 text-emerald-400" />}
          subtext={`ARR: ₹${(metrics.billing?.arr_inr || 0).toLocaleString('en-IN')}`}
          badge={{ text: 'INR LOCKED', variant: 'emerald' }}
        />
        <StatCard
          label="Agent Tasks"
          value={metrics.total_agent_tasks}
          icon={<Bot className="w-4 h-4 text-purple-400" />}
          subtext={`${metrics.running_agent_tasks} running · ${metrics.failed_agent_tasks} failed`}
          badge={{
            text: metrics.running_agent_tasks > 0 ? 'ACTIVE' : 'IDLE',
            variant: metrics.running_agent_tasks > 0 ? 'emerald' : 'slate'
          }}
        />
        <StatCard
          label="Automations Active"
          value={metrics.active_routines}
          icon={<Workflow className="w-4 h-4 text-cyan-400" />}
          subtext={`${metrics.total_routines} total configured routines`}
          badge={{ text: 'ROUTINES', variant: 'cyan' }}
        />
      </div>

      {/* Second Row: Plan Breakdown & Teams Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plan Distribution */}
        <Card
          title="Plan Distribution"
          subtitle="Active consumer & organization subscriptions"
          className="lg:col-span-2"
          action={
            <Button variant="ghost" size="sm" onClick={() => onNavigateTab?.('plans')} rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>
              View Plans
            </Button>
          }
        >
          <div className="space-y-3">
            {planEntries.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No plan distribution data available.</p>
            ) : (
              planEntries.map(([planName, count]) => {
                const total = Math.max(1, metrics.total_users);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={planName} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-200 font-mono flex items-center gap-2">
                        <Layers className="w-3 h-3 text-slate-400" />
                        <span>{planName}</span>
                      </span>
                      <span className="font-mono text-slate-300">
                        {count} users <span className="text-slate-400 text-[11px]">({pct}%)</span>
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* System & Team Quick Health */}
        <div className="space-y-6">
          <Card title="System Readiness" subtitle="Core platform health check">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-white/6">
                <span className="text-xs text-slate-300">Overall Health</span>
                <Badge variant={metrics.system_status === 'healthy' ? 'emerald' : 'amber'} size="xs">
                  {metrics.system_status}
                </Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-white/6">
                <span className="text-xs text-slate-300">Active Subscriptions</span>
                <span className="font-mono text-xs font-semibold text-slate-200">
                  {metrics.billing?.active_subscriptions || 0}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-white/6">
                <span className="text-xs text-slate-300">Failed Payments</span>
                <span className="font-mono text-xs font-semibold text-rose-400">
                  {metrics.billing?.failed_payments || 0}
                </span>
              </div>

              <Button
                variant="outline"
                size="sm"
                className="w-full mt-2"
                onClick={() => onNavigateTab?.('system')}
                rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}
              >
                Inspect Health & DB Check
              </Button>
            </div>
          </Card>

          {metrics.billing?.teams_overview && (
            <Card title="Teams Utilization" subtitle="Multi-seat organization statistics">
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Active Teams:</span>
                  <span className="font-mono text-slate-200 font-semibold">{metrics.billing.teams_overview.active_teams}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Seats Used:</span>
                  <span className="font-mono text-slate-200">
                    {metrics.billing.teams_overview.used_seats} / {metrics.billing.teams_overview.allocated_seats}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Seat Utilization:</span>
                  <span className="font-mono text-emerald-400 font-semibold">
                    {metrics.billing.teams_overview.seat_utilization_pct}%
                  </span>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
