import React, { useState, useEffect } from 'react';
import { opsApi } from '../api/adminApi';
import type {
  OpsHealth,
  OpsMetrics,
  OpsService,
  OpsContainersResponse,
  OpsErrorLog,
  OpsIncident,
  OpsDiagnosis
} from '../types/admin';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import {
  ShieldCheck,
  Activity,
  Cpu,
  HardDrive,
  Clock,
  RefreshCw,
  AlertTriangle,
  Server,
  Layers,
  FileText,
  Search,
  Sparkles,
  Info,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ShieldAlert,
  Terminal,
  Lock
} from 'lucide-react';

export const OpsDashboardPage: React.FC = () => {
  const [health, setHealth] = useState<OpsHealth | null>(null);
  const [metrics, setMetrics] = useState<OpsMetrics | null>(null);
  const [services, setServices] = useState<OpsService[]>([]);
  const [containers, setContainers] = useState<OpsContainersResponse | null>(null);
  const [errors, setErrors] = useState<OpsErrorLog[]>([]);
  const [incidents, setIncidents] = useState<OpsIncident[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState<Date | null>(null);

  // AI Diagnostic State
  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnosis, setDiagnosis] = useState<OpsDiagnosis | null>(null);
  const [showDiagModal, setShowDiagModal] = useState(false);

  // Selected Incident Modal
  const [selectedIncident, setSelectedIncident] = useState<OpsIncident | null>(null);

  const fetchData = async () => {
    try {
      setFetchError(null);
      const [h, m, s, c, e, inc, aud] = await Promise.all([
        opsApi.getHealth().catch(() => null),
        opsApi.getMetrics().catch(() => null),
        opsApi.getServices().catch(() => []),
        opsApi.getContainers().catch(() => null),
        opsApi.getErrors(25).catch(() => []),
        opsApi.getIncidents().catch(() => []),
        opsApi.getAudit(20).catch(() => [])
      ]);

      setHealth(h);
      setMetrics(m);
      setServices(s);
      setContainers(c);
      setErrors(e);
      setIncidents(inc);
      setAuditLogs(aud);
      setLastFetchTime(new Date());
    } catch (err: any) {
      setFetchError(err?.message || 'Failed to load Ops telemetry.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(() => {
      fetchData();
    }, 30000); // 30s auto-refresh
    return () => clearInterval(timer);
  }, []);

  const handleManualRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleTriggerDiagnosis = async (incidentId?: string) => {
    setDiagnosing(true);
    setShowDiagModal(true);
    try {
      const res = await opsApi.diagnose({ incident_id: incidentId, include_recent_errors: true });
      setDiagnosis(res);
    } catch (err: any) {
      alert(`AI diagnosis failed: ${err?.message || 'Unknown error'}`);
      setShowDiagModal(false);
    } finally {
      setDiagnosing(false);
    }
  };

  // Stale data check (> 60s)
  const isStale = lastFetchTime && (Date.now() - lastFetchTime.getTime() > 60000);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-sm font-mono text-slate-400">Loading Saarthi Ops telemetry...</span>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'healthy' || s === 'online') {
      return <Badge variant="emerald"><span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>{status}</Badge>;
    }
    if (s === 'degraded' || s === 'warning') {
      return <Badge variant="amber"><span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 mr-1.5"></span>{status}</Badge>;
    }
    if (s === 'unhealthy' || s === 'offline' || s === 'critical') {
      return <Badge variant="rose"><span className="inline-block w-1.5 h-1.5 rounded-full bg-rose-400 mr-1.5"></span>{status}</Badge>;
    }
    return <Badge variant="slate">{status || 'UNAVAILABLE'}</Badge>;
  };

  const cpuPct = metrics?.cpu?.percent_used ?? 0;
  const ramPct = metrics?.ram?.percent_used ?? 0;
  const diskPct = metrics?.disk?.percent_used ?? 0;

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              Saarthi Ops — Infrastructure & Diagnostics
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Read-Only
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time passive telemetry, isolated service boundaries, and AI-assisted operational reasoning.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleManualRefresh}
            isLoading={refreshing}
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Refresh Telemetry
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => handleTriggerDiagnosis()}
            isLoading={diagnosing}
            leftIcon={<Sparkles className="w-3.5 h-3.5 text-blue-200" />}
          >
            Run AI Diagnosis
          </Button>
        </div>
      </div>

      {/* Stale Data Warning Banner */}
      {isStale && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 text-xs text-amber-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
            <span>Telemetry data is older than 60 seconds. Collector stream may be delayed or sleeping.</span>
          </div>
          <Button variant="outline" size="sm" onClick={handleManualRefresh} className="text-amber-300 border-amber-500/30">
            Fetch Fresh State
          </Button>
        </div>
      )}

      {/* Top Banner: Overall Status & Vital Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-[#0d1117] border-white/6">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Overall Ops Health</div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-lg font-bold text-slate-100 capitalize">
              {health?.status || 'Unknown'}
            </span>
            {getStatusBadge(health?.status || 'UNKNOWN')}
          </div>
          <div className="mt-2 text-[10px] text-slate-400 font-mono">
            Last collection: {health?.last_collection_timestamp ? new Date(health.last_collection_timestamp).toLocaleTimeString() : 'N/A'}
          </div>
        </Card>

        <Card className="p-4 bg-[#0d1117] border-white/6">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>CPU Utilization</span>
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">{cpuPct}%</span>
            <span className="text-xs text-slate-400 font-mono">{metrics?.cpu?.logical_cores || 1} Cores</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2">
            <div
              className={`h-1.5 rounded-full ${cpuPct > 85 ? 'bg-rose-500' : cpuPct > 70 ? 'bg-amber-500' : 'bg-blue-500'}`}
              style={{ width: `${Math.min(100, Math.max(0, cpuPct))}%` }}
            ></div>
          </div>
        </Card>

        <Card className="p-4 bg-[#0d1117] border-white/6">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Memory (RAM)</span>
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">{ramPct}%</span>
            <span className="text-xs text-slate-400 font-mono">
              {metrics?.ram?.used_mb ? `${Math.round(metrics.ram.used_mb)} MB` : 'N/A'} / {metrics?.ram?.total_mb ? `${Math.round(metrics.ram.total_mb)} MB` : 'N/A'}
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2">
            <div
              className={`h-1.5 rounded-full ${ramPct > 85 ? 'bg-rose-500' : ramPct > 70 ? 'bg-amber-500' : 'bg-emerald-500'}`}
              style={{ width: `${Math.min(100, Math.max(0, ramPct))}%` }}
            ></div>
          </div>
        </Card>

        <Card className="p-4 bg-[#0d1117] border-white/6">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Disk Storage</span>
            <HardDrive className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">{diskPct}%</span>
            <span className="text-xs text-slate-400 font-mono">
              {metrics?.disk?.used_gb ?? 'N/A'} / {metrics?.disk?.total_gb ?? 'N/A'} GB
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2">
            <div
              className={`h-1.5 rounded-full ${diskPct > 85 ? 'bg-rose-500' : diskPct > 70 ? 'bg-amber-500' : 'bg-purple-500'}`}
              style={{ width: `${Math.min(100, Math.max(0, diskPct))}%` }}
            ></div>
          </div>
        </Card>
      </div>

      {/* Configured Services & Container Isolation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Allowlisted Services Table */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Server className="w-4 h-4 text-blue-400" />
              Configured Saarthi Services (Strict Allowlist)
            </h2>
            <span className="text-xs text-slate-400 font-mono">
              {services.filter(s => s.status === 'ONLINE').length}/{services.length} Online
            </span>
          </div>

          <Card className="overflow-hidden bg-[#0d1117] border-white/6">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 border-b border-white/6 text-slate-400 font-mono uppercase text-[10px]">
                <tr>
                  <th className="px-4 py-2.5">Service ID</th>
                  <th className="px-4 py-2.5">Name</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5">Latency</th>
                  <th className="px-4 py-2.5">Last Checked</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/4">
                {services.map((svc) => (
                  <tr key={svc.service_id} className="hover:bg-white/[0.02]">
                    <td className="px-4 py-3 font-mono font-medium text-slate-300">
                      {svc.service_id}
                    </td>
                    <td className="px-4 py-3 text-slate-400">{svc.name}</td>
                    <td className="px-4 py-3">{getStatusBadge(svc.status)}</td>
                    <td className="px-4 py-3 font-mono text-slate-400">
                      {svc.latency_ms ? `${svc.latency_ms} ms` : '—'}
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-400 text-[11px]">
                      {svc.last_checked ? new Date(svc.last_checked).toLocaleTimeString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>

        {/* Container Isolation State */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Container Isolation State
            </h2>
            <span className="text-[10px] font-mono text-slate-400">Restricted Read-Only</span>
          </div>

          <Card className="p-4 bg-[#0d1117] border-white/6 space-y-3">
            {containers?.status === 'unavailable' ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-slate-300 font-medium text-xs">
                  <Info className="w-4 h-4 text-blue-400" />
                  <span>Local Development Environment</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Container runtime is detached in local mode. Ops reports <span className="font-mono text-slate-300">unavailable</span> instead of fabricating container states.
                </p>
                <div className="p-2.5 rounded bg-slate-900/80 border border-white/4 text-[11px] font-mono text-slate-400">
                  Target Staging Containers (Allowlisted):
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-slate-400">
                    <li>saarthi-staging-backend</li>
                    <li>saarthi-staging-db</li>
                    <li>saarthi-staging-frontend</li>
                    <li>saarthi-staging-admin</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                {containers?.containers?.map((c) => (
                  <div key={c.name} className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-white/4 text-xs">
                    <span className="font-mono text-slate-300">{c.name}</span>
                    <Badge variant="emerald">Running (RO)</Badge>
                  </div>
                ))}
              </div>
            )}

            <div className="pt-2 border-t border-white/4 flex items-center gap-2 text-[10px] text-slate-400 font-mono">
              <Lock className="w-3 h-3 text-emerald-400" />
              <span>/var/run/docker.sock mount blocked by design</span>
            </div>
          </Card>
        </div>
      </div>

      {/* Incidents & Active Alerts */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Detected Infrastructure Incidents
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            {incidents.length} Active Incident{incidents.length === 1 ? '' : 's'}
          </span>
        </div>

        {incidents.length === 0 ? (
          <Card className="p-4 bg-[#0d1117] border-white/6 text-center text-xs text-slate-400">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1.5" />
            No active infrastructure incidents detected. All allowlisted services and telemetry nominal.
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {incidents.map((inc) => (
              <Card key={inc.incident_id} className="p-4 bg-[#0d1117] border-white/6 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge variant={inc.severity === 'CRITICAL' ? 'rose' : 'amber'}>
                        {inc.severity}
                      </Badge>
                      <span className="text-xs font-semibold text-slate-100">{inc.title}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono mt-1">
                      Affected: <span className="text-slate-300">{inc.affected_service}</span> | Detected: {new Date(inc.detected_at).toLocaleTimeString()}
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTriggerDiagnosis(inc.incident_id)}
                    leftIcon={<Sparkles className="w-3 h-3 text-blue-400" />}
                  >
                    Diagnose
                  </Button>
                </div>
                <div className="p-2.5 rounded bg-slate-900/60 border border-white/4 text-xs font-mono text-slate-300">
                  Evidence: {inc.evidence}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Sanitized Error Stream & Secret Redaction Showcase */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-purple-400" />
              Recent Sanitized Application Errors
            </h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Secrets Redacted
            </span>
          </div>
          <span className="text-xs text-slate-400 font-mono">{errors.length} events logged</span>
        </div>

        <Card className="overflow-hidden bg-[#0d1117] border-white/6">
          {errors.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-400 font-mono">
              Zero unhandled application errors in current circular buffer window.
            </div>
          ) : (
            <div className="divide-y divide-white/4 max-h-72 overflow-y-auto font-mono text-xs">
              {errors.map((err, idx) => (
                <div key={idx} className="p-3 hover:bg-white/[0.02] space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <div className="flex items-center gap-2">
                      <span className="text-rose-400 font-bold">[{err.level}]</span>
                      <span className="text-slate-300">{err.source}</span>
                    </div>
                    <span>{new Date(err.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="text-slate-200 text-xs break-all leading-relaxed">
                    {err.message}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Ops Access Audit History */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            Ops Access Audit History
          </h2>
          <span className="text-xs text-slate-400 font-mono">Immutable Log Trail</span>
        </div>

        <Card className="overflow-hidden bg-[#0d1117] border-white/6">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-white/6 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="px-4 py-2.5">Timestamp</th>
                <th className="px-4 py-2.5">Admin ID</th>
                <th className="px-4 py-2.5">Action</th>
                <th className="px-4 py-2.5">Target</th>
                <th className="px-4 py-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/4">
              {auditLogs.slice(0, 10).map((a, i) => (
                <tr key={i} className="hover:bg-white/[0.02]">
                  <td className="px-4 py-2.5 font-mono text-slate-400 text-[11px]">
                    {new Date(a.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-slate-300">{a.admin_id}</td>
                  <td className="px-4 py-2.5 font-mono text-blue-400">{a.action}</td>
                  <td className="px-4 py-2.5 font-mono text-slate-400">{a.target || '—'}</td>
                  <td className="px-4 py-2.5">
                    <Badge variant="emerald" size="xs">{a.status || 'SUCCESS'}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      {/* AI DIAGNOSTIC MODAL */}
      {showDiagModal && (
        <Modal
          isOpen={showDiagModal}
          onClose={() => setShowDiagModal(false)}
          title="AI-Assisted Operational Diagnosis"
          maxWidth="2xl"
        >
          {diagnosing ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-4">
              <LoadingSpinner size="lg" />
              <span className="text-xs font-mono text-slate-400">
                Synthesizing sanitized telemetry, distinguishing facts from hypotheses...
              </span>
            </div>
          ) : diagnosis ? (
            <div className="space-y-5 text-xs">
              {/* Problem Summary Card */}
              <div className="p-3.5 rounded-lg bg-blue-500/10 border border-blue-500/20 space-y-1.5">
                <div className="text-[11px] font-mono font-semibold uppercase text-blue-400 flex items-center justify-between">
                  <span>Observed State Summary</span>
                  <Badge variant="blue" size="xs">{diagnosis.diagnostic_mode}</Badge>
                </div>
                <div className="text-slate-200 font-medium leading-relaxed">
                  {diagnosis.problem_summary}
                </div>
              </div>

              {/* Facts vs Hypotheses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-3.5 rounded-lg bg-slate-900 border border-white/6 space-y-2">
                  <div className="text-[11px] font-mono font-semibold uppercase text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verified Facts ({diagnosis.facts?.length || 0})</span>
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-slate-300">
                    {diagnosis.facts?.map((f, i) => (
                      <li key={i} className="leading-snug">{f}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-900 border border-white/6 space-y-2">
                  <div className="text-[11px] font-mono font-semibold uppercase text-amber-400 flex items-center gap-1.5">
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>Hypotheses ({diagnosis.hypotheses?.length || 0})</span>
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-slate-300">
                    {diagnosis.hypotheses?.map((h, i) => (
                      <li key={i} className="leading-snug">{h}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Supporting Evidence & Missing Telemetry */}
              <div className="p-3.5 rounded-lg bg-slate-900 border border-white/6 space-y-2">
                <div className="text-[11px] font-mono font-semibold uppercase text-slate-400 flex items-center justify-between">
                  <span>Evidence & Metric Citations</span>
                  <span className="text-slate-400 font-mono">Confidence: <span className="text-slate-200 font-bold">{diagnosis.confidence}</span></span>
                </div>
                <div className="space-y-1 text-slate-300 font-mono text-[11px]">
                  {diagnosis.evidence?.map((ev, i) => (
                    <div key={i} className="p-1.5 bg-black/40 rounded border border-white/4">
                      • {ev}
                    </div>
                  ))}
                </div>
                {diagnosis.missing_evidence && diagnosis.missing_evidence.length > 0 && (
                  <div className="pt-2 text-[11px] text-slate-400 font-mono">
                    Missing Evidence: {diagnosis.missing_evidence.join(', ')}
                  </div>
                )}
              </div>

              {/* Safe Investigation Steps */}
              <div className="p-3.5 rounded-lg bg-slate-900 border border-white/6 space-y-2">
                <div className="text-[11px] font-mono font-semibold uppercase text-cyan-400 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Recommended Safe Investigation Steps (Read-Only)</span>
                </div>
                <div className="space-y-1.5">
                  {diagnosis.safe_investigation_steps?.map((step, i) => (
                    <div key={i} className="p-2 rounded bg-black/30 border border-white/4 text-slate-200 flex items-start gap-2">
                      <span className="text-cyan-400 font-mono font-bold shrink-0">{i + 1}.</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Shared Host & MKS ERP Impact */}
              <div className="p-3.5 rounded-lg bg-purple-500/10 border border-purple-500/20 space-y-1.5">
                <div className="text-[11px] font-mono font-semibold uppercase text-purple-300 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Shared VPS Host & MKS ERP Impact Assessment</span>
                </div>
                <div className="space-y-1 text-slate-300 leading-relaxed">
                  {diagnosis.shared_infrastructure_impact?.map((impact, i) => (
                    <div key={i}>{impact}</div>
                  ))}
                </div>
              </div>

              {/* Advisory Disclaimer */}
              <div className="p-3 rounded bg-slate-950 border border-white/6 text-[10px] text-slate-400 font-mono flex items-center gap-2">
                <Lock className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{diagnosis.recommendations_disclaimer}</span>
              </div>
            </div>
          ) : (
            <div className="py-6 text-center text-xs text-slate-400">
              No diagnostic data generated.
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};
