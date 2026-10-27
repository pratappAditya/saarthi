import React, { useState, useEffect } from 'react';
import { 
  Bot, Play, CheckCircle2, AlertTriangle, RefreshCw, XCircle, Clock, 
  ShieldCheck, Layers, ArrowRight, PauseCircle, Check, X, ShieldAlert, 
  Eye, Zap, FileCheck, ArrowDown, Database, Terminal, Globe, Laptop
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { useApp } from '../../context/AppContext';

export const AgentActivityView: React.FC = () => {
  const { addToast } = useApp();
  const [tasks, setTasks] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [permissions, setPermissions] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('career_architect');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [selectedTask, setSelectedTask] = useState<any | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tRes, aRes, pRes] = await Promise.all([
        fetch('/api/agents/tasks'),
        fetch('/api/agents'),
        fetch('/api/permissions')
      ]);
      if (tRes.ok) {
        const tData = await tRes.json();
        const loadedTasks = tData.tasks || [];
        setTasks(loadedTasks);
        if (loadedTasks.length > 0 && !selectedTask) {
          setSelectedTask(loadedTasks[0]);
        }
      }
      if (aRes.ok) {
        const aData = await aRes.json();
        setAgents(aData.agents || []);
      }
      if (pRes.ok) {
        const pData = await pRes.json();
        setPermissions(pData.permissions || []);
      }
    } catch (err) {
      console.error("Failed to load agent activity data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    try {
      setRunning(true);
      const res = await fetch(`/api/agent/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, agent_id: selectedAgent })
      });
      if (res.ok) {
        const data = await res.json();
        addToast({ 
          type: 'success', 
          title: 'Agent Executed', 
          message: `Agent workflow completed. ${data.steps_executed} steps executed.` 
        });
        setPrompt('');
        await loadData();
      } else {
        const errData = await res.json();
        addToast({ type: 'error', title: 'Execution Blocked', message: errData.detail || 'Could not run agent.' });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Execution Error', message: 'Failed to invoke agent.' });
    } finally {
      setRunning(false);
    }
  };

  const handlePauseTask = async (taskId: string) => {
    try {
      const res = await fetch(`/api/agent/tasks/${taskId}/pause`, { method: 'POST' });
      if (res.ok) {
        addToast({ type: 'info', title: 'Task Paused', message: `Paused task '${taskId}'.` });
        loadData();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Pause Failed', message: 'Could not pause task.' });
    }
  };

  const handleResumeTask = async (taskId: string) => {
    try {
      const res = await fetch(`/api/agent/tasks/${taskId}/resume`, { method: 'POST' });
      if (res.ok) {
        addToast({ type: 'success', title: 'Task Resumed', message: `Resumed task '${taskId}'.` });
        loadData();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Resume Failed', message: 'Could not resume task.' });
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      const res = await fetch(`/api/agent/tasks/${taskId}/cancel`, { method: 'POST' });
      if (res.ok) {
        addToast({ type: 'info', title: 'Task Cancelled', message: `Cancelled task '${taskId}'.` });
        loadData();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Cancel Failed', message: 'Could not cancel task.' });
    }
  };

  const handleApprovePermission = async (reqId: string) => {
    try {
      const res = await fetch(`/api/agent/approvals/${reqId}`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true })
      });
      if (res.ok) {
        addToast({ type: 'success', title: 'Permission Granted', message: 'Action approved.' });
        loadData();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Approval Failed', message: 'Could not approve permission.' });
    }
  };

  const handleDenyPermission = async (reqId: string) => {
    try {
      const res = await fetch(`/api/agent/approvals/${reqId}`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: false })
      });
      if (res.ok) {
        addToast({ type: 'info', title: 'Permission Denied', message: 'Action rejected.' });
        loadData();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Rejection Failed', message: 'Could not deny permission.' });
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200 font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Bot className="w-3.5 h-3.5 text-[#F59E0B]" />
            <span>SAARTHI CENTRAL AUTONOMOUS INTELLIGENCE</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Agent Activity: Observe → Plan → Act → Verify
          </h1>
        </div>
        <Button variant="outline" size="sm" icon={RefreshCw} onClick={loadData}>
          Refresh Activity
        </Button>
      </div>

      {/* Launch Agent Form */}
      <Card variant="default" padding="md" className="space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Play className="w-4 h-4 text-[#F59E0B]" />
          <span>Launch Autonomous Execution Objective</span>
        </h3>
        <form onSubmit={handleRunAgent} className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-mono text-gray-400 mb-1">Execution Domain</label>
              <select 
                value={selectedAgent} 
                onChange={(e) => setSelectedAgent(e.target.value)} 
                className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs"
              >
                <option value="general">Universal Intelligence Core (General)</option>
                <option value="career_architect">Career Architect (Resume & Tailoring)</option>
                <option value="research_assistant">Deep Research & Academic Literature</option>
                <option value="software_engineer">Software & Systems Engineering</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-mono text-gray-400 mb-1">Multi-Step Objective / Goal</label>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. Research latest information on AI models, compare sources, create report, save to workspace, and prepare email draft"
                className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-[#F59E0B]"
                required
              />
            </div>
          </div>
          <div className="flex justify-end pt-1">
            <Button variant="primary" size="sm" icon={Play} type="submit" disabled={running}>
              {running ? 'Executing Autonomous Pipeline...' : 'Execute Objective'}
            </Button>
          </div>
        </form>
      </Card>

      {/* Human Approval Required Banner */}
      {permissions.length > 0 && (
        <Card variant="default" padding="md" className="space-y-3 border-amber-500/40 bg-amber-500/5">
          <h3 className="text-sm font-bold text-amber-400 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Human Approval Required ({permissions.length})</span>
          </h3>
          <div className="space-y-2">
            {permissions.map((p) => (
              <div key={p.request_id} className="p-3 rounded-xl bg-black/40 border border-amber-500/30 flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="warning" size="xs">{p.risk_level}</Badge>
                    <span className="text-white font-bold">{p.tool_id}</span>
                  </div>
                  <p className="text-gray-300 text-xs">{p.action_description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="xs" icon={X} onClick={() => handleDenyPermission(p.request_id)}>
                    Reject
                  </Button>
                  <Button variant="primary" size="xs" icon={Check} onClick={() => handleApprovePermission(p.request_id)}>
                    Approve Action
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Main Execution Pipeline View: Goal -> Plan -> Current step -> Tool -> Permission -> Result -> Verification */}
      {selectedTask && (
        <Card variant="default" padding="md" className="space-y-4 border-[#F59E0B]/30 bg-[#0E0E0E]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-white/10 gap-2">
            <div>
              <span className="text-[10px] uppercase font-bold text-[#F59E0B]">ACTIVE AGENT WORKFLOW</span>
              <h2 className="text-base font-bold text-white flex items-center gap-2 mt-0.5">
                <span>Goal: {selectedTask.goal || selectedTask.objective}</span>
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={selectedTask.status === 'completed' ? 'success' : selectedTask.status === 'waiting_approval' ? 'warning' : 'accent'} size="sm">
                {selectedTask.status?.toUpperCase()}
              </Badge>
              {selectedTask.status === 'in_progress' && (
                <Button variant="outline" size="xs" icon={PauseCircle} onClick={() => handlePauseTask(selectedTask.task_id)}>
                  Pause
                </Button>
              )}
              {selectedTask.status === 'paused' && (
                <Button variant="primary" size="xs" icon={Play} onClick={() => handleResumeTask(selectedTask.task_id)}>
                  Resume
                </Button>
              )}
              {selectedTask.status !== 'cancelled' && selectedTask.status !== 'completed' && (
                <Button variant="outline" size="xs" icon={XCircle} onClick={() => handleCancelTask(selectedTask.task_id)}>
                  Cancel
                </Button>
              )}
            </div>
          </div>

          {/* Stepper Pipeline */}
          <div className="space-y-4">
            {selectedTask.steps?.map((step: any, idx: number) => {
              const isCompleted = step.status === 'completed' || step.status === 'verified';
              const isFailed = step.status === 'failed';
              const isWaiting = step.status === 'waiting_approval' || step.approval_state === 'pending';
              const isPending = step.status === 'pending';
              const opType = step.step_type || (step.tool_id?.startsWith('file.write') || step.tool_id?.startsWith('desktop.insert') ? 'ACTION' : 'OBSERVATION');

              return (
                <div 
                  key={step.step_id || idx}
                  className={`p-4 rounded-xl border transition-all ${
                    isCompleted 
                      ? 'bg-emerald-950/20 border-emerald-500/30' 
                      : isWaiting 
                        ? 'bg-amber-950/20 border-amber-500/40 shadow-[0_0_12px_rgba(245,158,11,0.15)]' 
                        : isFailed 
                          ? 'bg-rose-950/20 border-rose-500/40' 
                          : 'bg-white/5 border-white/10'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-white/5">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center font-bold text-[10px]">
                        {idx + 1}
                      </span>
                      <h4 className="font-bold text-white text-xs">{step.title}</h4>
                      <Badge variant={opType === 'ACTION' ? 'warning' : 'accent'} size="xs">
                        {opType}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-gray-400 font-mono">Tool: {step.tool_id || 'system'}</span>
                      <Badge variant={isCompleted ? 'success' : isFailed ? 'danger' : isWaiting ? 'warning' : 'default'} size="xs">
                        {isCompleted ? 'VERIFIED' : isFailed ? 'FAILED' : isWaiting ? 'NEEDS APPROVAL' : 'PENDING'}
                      </Badge>
                    </div>
                  </div>

                  <p className="text-gray-300 text-xs py-2">{step.description}</p>

                  {/* Observable Verification Proof */}
                  {step.verification_reason && (
                    <div className="mt-2 p-2 rounded-lg bg-black/40 border border-white/5 flex items-center gap-2 text-[11px]">
                      <FileCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span className="text-gray-400">Observable Verification:</span>
                      <span className="text-emerald-300 font-semibold">{step.verification_reason}</span>
                    </div>
                  )}

                  {/* Error & Diagnosis */}
                  {step.error && (
                    <div className="mt-2 p-2 rounded-lg bg-rose-950/30 border border-rose-500/30 flex items-center gap-2 text-[11px] text-rose-300">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                      <span>{step.error}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Task List Selector */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-400" />
          <span>Execution History & Trajectories</span>
        </h3>

        {loading ? (
          <div className="py-8 text-center text-gray-400">Loading Agent Tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="p-8 text-center border border-dashed border-white/10 rounded-xl text-gray-400">
            No agent tasks executed yet. Launch an objective above.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {tasks.map((t) => (
              <div 
                key={t.task_id}
                onClick={() => setSelectedTask(t)}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  selectedTask?.task_id === t.task_id 
                    ? 'bg-[#1a1a1a] border-[#F59E0B]' 
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <Badge variant={t.status === 'completed' ? 'success' : t.status === 'waiting_approval' ? 'warning' : 'accent'} size="xs">
                    {t.status?.toUpperCase()}
                  </Badge>
                  <span className="text-[10px] text-gray-400">{t.domain}</span>
                </div>
                <h4 className="font-bold text-white text-xs truncate">{t.goal || t.objective || 'Task'}</h4>
                <p className="text-[10px] text-gray-400 mt-1">Steps: {t.steps?.length || 0} | Updated: {new Date(t.updated_at).toLocaleTimeString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
