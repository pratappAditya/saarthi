import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, Lock, Cpu, Database, Eye, History, CheckCircle2, AlertTriangle 
} from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

export const TrustCenterView: React.FC = () => {
  const [trustSummary, setTrustSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrustSummary();
  }, []);

  const loadTrustSummary = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/trust/summary');
      if (res.ok) {
        const data = await res.json();
        setTrustSummary(data);
      }
    } catch (err) {
      console.error("Failed to load trust summary", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>SAARTHI TRUST & PRIVACY CENTER</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Security, Audit Trail & Data Controls
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Transparent breakdown of local AI execution, memory storage, risk-based permissions, and consequential action audit history.
          </p>
        </div>
      </div>

      {/* Trust Status Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="default" padding="md" className="space-y-2 font-mono text-xs">
          <div className="flex items-center gap-2 text-emerald-400">
            <Cpu className="w-4 h-4" />
            <span className="font-bold">Execution Engine</span>
          </div>
          <p className="text-white text-sm font-bold">100% Local Nemotron</p>
          <p className="text-[10px] text-gray-400">No data sent to cloud models.</p>
        </Card>

        <Card variant="default" padding="md" className="space-y-2 font-mono text-xs">
          <div className="flex items-center gap-2 text-purple-400">
            <Database className="w-4 h-4" />
            <span className="font-bold">Persistent Storage</span>
          </div>
          <p className="text-white text-sm font-bold">Local SQLite DB</p>
          <p className="text-[10px] text-gray-400">Encrypted local persistence.</p>
        </Card>

        <Card variant="default" padding="md" className="space-y-2 font-mono text-xs">
          <div className="flex items-center gap-2 text-blue-400">
            <Lock className="w-4 h-4" />
            <span className="font-bold">Permission Policy</span>
          </div>
          <p className="text-white text-sm font-bold">Risk-Based Approval</p>
          <p className="text-[10px] text-gray-400">Human-in-the-loop authorization.</p>
        </Card>

        <Card variant="default" padding="md" className="space-y-2 font-mono text-xs">
          <div className="flex items-center gap-2 text-amber-400">
            <History className="w-4 h-4" />
            <span className="font-bold">Action History</span>
          </div>
          <p className="text-white text-sm font-bold">{trustSummary?.recent_actions_count || 0} Audited Events</p>
          <p className="text-[10px] text-gray-400">Full audit logging.</p>
        </Card>
      </div>

      {/* Voice Privacy Center Section */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-950/30 via-blue-950/30 to-emerald-950/30 border border-purple-500/30 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-purple-400 font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>VOICE PRIVACY CENTER (Phase 5H)</span>
          </div>
          <Badge variant="success" size="xs">100% LOCAL STT/TTS</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px]">
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Microphone Access</span>
            <p className="text-emerald-400 font-bold">Explicit Consent Required</p>
            <p className="text-gray-500 text-[10px]">No background microphone listening</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">STT / TTS Processing</span>
            <p className="text-purple-300 font-bold">Local Saarthi Engine</p>
            <p className="text-gray-500 text-[10px]">Zero audio bytes sent to external cloud</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Wake-Word Policy</span>
            <p className="text-blue-300 font-bold">WakeWordProvider Boundary</p>
            <p className="text-gray-500 text-[10px]">Explicit user activation only</p>
          </div>
        </div>
      </div>

      {/* Deep Personalization Privacy Section */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-950/30 via-purple-950/30 to-indigo-950/30 border border-blue-500/30 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-400 font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>PERSONALIZATION PRIVACY & ISOLATION (Phase 5I)</span>
          </div>
          <Badge variant="accent" size="xs">NO SENSITIVE PROFILING</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px]">
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Inference Demarcation</span>
            <p className="text-purple-300 font-bold">Explicit vs Inferred</p>
            <p className="text-gray-500 text-[10px]">Inferences require evidence & can be rejected</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Team Isolation Policy</span>
            <p className="text-emerald-400 font-bold">Private User Profile</p>
            <p className="text-gray-500 text-[10px]">Personalization never exposed to teammates</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Safety & Permissions</span>
            <p className="text-amber-300 font-bold">Safety Supremacy</p>
            <p className="text-gray-500 text-[10px]">Personalization never bypasses risk policy</p>
          </div>
        </div>
      </div>

      {/* Routines & Automation Security Section */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/30 via-teal-950/30 to-cyan-950/30 border border-emerald-500/30 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400 font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>ROUTINES & AUTOMATION AUDIT (Phase 5J)</span>
          </div>
          <Badge variant="success" size="xs">PERMISSION BOUNDARIES</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px]">
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Execution Runtime</span>
            <p className="text-emerald-300 font-bold">AgentRuntime Sandboxed</p>
            <p className="text-gray-500 text-[10px]">Executes through verified TaskGraphs</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Human Approval Policy</span>
            <p className="text-purple-300 font-bold">High-Risk Enforcement</p>
            <p className="text-gray-500 text-[10px]">Consequential actions prompt for permission</p>
          </div>
          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Failure Recovery</span>
            <p className="text-blue-300 font-bold">Exponential Backoff</p>
            <p className="text-gray-500 text-[10px]">Auto-pauses after max retry limit</p>
          </div>
        </div>
      </div>

      {/* Audit History Timeline */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
          <History className="w-4 h-4 text-emerald-400" />
          <span>Consequential Action Audit Timeline</span>
        </h3>

        {loading ? (
          <div className="p-8 text-center text-xs text-gray-400">Loading audit history...</div>
        ) : !trustSummary?.audit_logs || trustSummary.audit_logs.length === 0 ? (
          <div className="p-8 text-center border border-dashed border-white/10 rounded-xl text-xs text-gray-400 font-mono">
            No audit records logged yet.
          </div>
        ) : (
          <div className="space-y-2 font-mono text-xs">
            {trustSummary.audit_logs.map((log: any) => (
              <div key={log.id} className="p-3 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge variant={log.risk_level === 'READ_ONLY' ? 'outline' : log.risk_level === 'HIGH_RISK' ? 'danger' : 'warning'} size="xs">
                      {log.risk_level}
                    </Badge>
                    <span className="text-white font-bold">{log.tool_name || 'System Orchestration'}</span>
                    <span className="text-gray-400 text-[10px]">({log.domain})</span>
                  </div>
                  <p className="text-gray-300 text-[11px]">{log.action_summary}</p>
                </div>
                <div className="text-right text-[10px] text-gray-400 space-y-1">
                  <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <Badge variant="accent" size="xs">{log.permission_status}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
