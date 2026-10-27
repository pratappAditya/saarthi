import React, { useState, useEffect } from 'react';
import { api } from '../../api';
import { DomainTransitionBadge } from '../domains/DomainTransitionBadge';

interface TaskStep {
  step_id: string;
  title: string;
  description: string;
  domain: string;
  subdomain?: string;
  dependencies: string[];
  tool_id?: string;
  arguments: Record<string, any>;
  status: string;
  result?: Record<string, any>;
  error?: string;
  evidence: Array<Record<string, any>>;
  output_artifact?: Record<string, any>;
  confidence: number;
  risk_level: string;
  approval_required: boolean;
  approval_state: string;
  provenance: Record<string, any>;
  verification_state: string;
}

interface TaskGraph {
  task_id: string;
  goal: string;
  domain: string;
  subdomains: string[];
  steps: TaskStep[];
  status: string;
  domain_transitions: Array<{ from: string; to: string; reason: string }>;
  approval_requirements: string[];
  provenance: Record<string, any>;
  verification_state: string;
}

export const CrossDomainWorkflowView: React.FC = () => {
  const [objectiveInput, setObjectiveInput] = useState('Analyze these archaeological excavation photographs, compare them with historical records, research similar findings and prepare a report.');
  const [activeDomain, setActiveDomain] = useState('archaeology');
  const [isDomainLocked, setIsDomainLocked] = useState(false);
  const [activeTask, setActiveTask] = useState<TaskGraph | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null);
  const [selectedEvidenceStep, setSelectedEvidenceStep] = useState<TaskStep | null>(null);

  const handleStartWorkflow = async () => {
    if (!objectiveInput.trim()) return;
    setLoading(true);
    try {
      const res = await api.startCrossDomainWorkflow(objectiveInput, isDomainLocked ? activeDomain : "general");
      if (res.task_graph) {
        setActiveTask(res.task_graph);
        if (res.task_graph.subdomains && res.task_graph.subdomains.length > 0) {
          setActiveDomain(res.task_graph.subdomains[0]);
        }
      }
    } catch (err) {
      console.error("Failed to start cross-domain workflow:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveStep = async (stepId: string) => {
    if (!activeTask) return;
    try {
      const res = await api.approveWorkflowStep(activeTask.task_id, stepId);
      if (res.task) {
        setActiveTask(res.task);
      }
    } catch (err) {
      console.error("Failed to approve step:", err);
    }
  };

  const handleCancelWorkflow = async () => {
    if (!activeTask) return;
    try {
      await api.cancelWorkflow(activeTask.task_id);
      setActiveTask(prev => prev ? { ...prev, status: "cancelled" } : null);
    } catch (err) {
      console.error("Failed to cancel workflow:", err);
    }
  };

  const handleResumeWorkflow = async () => {
    if (!activeTask) return;
    try {
      await api.resumeWorkflow(activeTask.task_id);
      setActiveTask(prev => prev ? { ...prev, status: "in_progress" } : null);
    } catch (err) {
      console.error("Failed to resume workflow:", err);
    }
  };

  const handleReplanWorkflow = async () => {
    if (!activeTask) return;
    try {
      const res = await api.replanWorkflow(activeTask.task_id);
      if (res.task_graph) {
        setActiveTask(res.task_graph);
      }
    } catch (err) {
      console.error("Failed to replan workflow:", err);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 p-6 overflow-y-auto font-sans">
      {/* Header */}
      <div className="flex items-center justify-between pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-cyan-400 to-emerald-400">
            Cross-Domain Autonomy Workflow
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Universal AI Operating Companion executing multi-domain task graphs with explicit evidence handoffs.
          </p>
        </div>

        <DomainTransitionBadge
          activeDomain={activeDomain}
          subdomains={activeTask?.subdomains || ["archaeology", "history", "research", "writing"]}
          isLocked={isDomainLocked}
          onToggleLock={(locked) => setIsDomainLocked(locked)}
          reason="Auto-transition active: Artifact observation -> Archival matching -> Literature synthesis -> Report drafting."
        />
      </div>

      {/* Input Section */}
      <div className="mt-6 bg-slate-900/90 rounded-xl p-5 border border-slate-800 shadow-xl">
        <label className="block text-xs font-mono uppercase tracking-wider text-indigo-400 mb-2 font-semibold">
          Cross-Domain Objective
        </label>
        <div className="flex gap-3">
          <textarea
            value={objectiveInput}
            onChange={(e) => setObjectiveInput(e.target.value)}
            rows={2}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition"
            placeholder="Describe a goal spanning software, archaeology, history, biology, or career..."
          />
          <button
            onClick={handleStartWorkflow}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 flex items-center gap-2 self-end"
          >
            {loading ? (
              <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            Execute Cross-Domain Graph
          </button>
        </div>
      </div>

      {/* Visual Workflow Graph */}
      {activeTask && (
        <div className="mt-8 space-y-6">
          {/* Pipeline Summary Bar */}
          <div className="flex items-center justify-between bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center gap-4">
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 font-bold uppercase">
                TASK GRAPH: {activeTask.task_id}
              </span>
              <span className={`text-xs px-2.5 py-1 rounded font-semibold uppercase ${
                activeTask.status === "completed" ? "bg-emerald-500/20 text-emerald-400" :
                activeTask.status === "in_progress" ? "bg-cyan-500/20 text-cyan-400 animate-pulse" :
                activeTask.status === "cancelled" ? "bg-rose-500/20 text-rose-400" : "bg-amber-500/20 text-amber-400"
              }`}>
                STATUS: {activeTask.status}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCancelWorkflow}
                className="px-3 py-1.5 bg-rose-950/60 text-rose-300 border border-rose-800/50 hover:bg-rose-900/60 rounded-md text-xs font-medium transition"
              >
                Cancel
              </button>
              <button
                onClick={handleResumeWorkflow}
                className="px-3 py-1.5 bg-cyan-950/60 text-cyan-300 border border-cyan-800/50 hover:bg-cyan-900/60 rounded-md text-xs font-medium transition"
              >
                Resume
              </button>
              <button
                onClick={handleReplanWorkflow}
                className="px-3 py-1.5 bg-amber-950/60 text-amber-300 border border-amber-800/50 hover:bg-amber-900/60 rounded-md text-xs font-medium transition"
              >
                Re-Plan Graph
              </button>
            </div>
          </div>

          {/* Sequence Node Ribbon */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-indigo-500/40 text-xs font-mono font-semibold text-indigo-300 shrink-0">
              OBJECTIVE
            </div>
            <span className="text-slate-600 font-bold">→</span>
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-cyan-500/40 text-xs font-mono font-semibold text-cyan-300 shrink-0">
              TASK GRAPH
            </div>
            <span className="text-slate-600 font-bold">→</span>
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-emerald-500/40 text-xs font-mono font-semibold text-emerald-300 shrink-0">
              DOMAIN STEPS ({activeTask.steps.length})
            </div>
            <span className="text-slate-600 font-bold">→</span>
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-amber-500/40 text-xs font-mono font-semibold text-amber-300 shrink-0">
              EVIDENCE & VERIFICATION
            </div>
            <span className="text-slate-600 font-bold">→</span>
            <div className="px-3 py-2 rounded-lg bg-slate-900 border border-purple-500/40 text-xs font-mono font-semibold text-purple-300 shrink-0">
              FINAL SYNTHESIS
            </div>
          </div>

          {/* Steps List */}
          <div className="space-y-4">
            {activeTask.steps.map((step, idx) => {
              const isExpanded = expandedStepId === step.step_id;
              return (
                <div
                  key={step.step_id}
                  className={`rounded-xl border transition-all duration-200 ${
                    step.status === "completed"
                      ? "bg-slate-900/80 border-slate-800"
                      : step.status === "in_progress"
                      ? "bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-950/30"
                      : "bg-slate-950/60 border-slate-800/80 opacity-90"
                  }`}
                >
                  <div className="p-4 flex items-center justify-between cursor-pointer" onClick={() => setExpandedStepId(isExpanded ? null : step.step_id)}>
                    <div className="flex items-center gap-3">
                      <span className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-800 text-xs font-mono font-bold text-slate-300 border border-slate-700">
                        {idx + 1}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-semibold text-slate-100">{step.title}</h3>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-indigo-950 text-indigo-300 border border-indigo-800/50">
                            {step.domain}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">{step.description}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {step.approval_required && (
                        <span className={`text-xs px-2 py-0.5 rounded font-mono font-semibold ${
                          step.approval_state === "approved"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50"
                            : "bg-amber-950 text-amber-400 border border-amber-800/50 animate-pulse"
                        }`}>
                          {step.approval_state === "approved" ? "APPROVED" : "APPROVAL REQUIRED"}
                        </span>
                      )}

                      <span className={`text-xs px-2.5 py-1 rounded font-mono font-semibold uppercase ${
                        step.status === "completed" ? "bg-emerald-500/10 text-emerald-400" :
                        step.status === "in_progress" ? "bg-cyan-500/10 text-cyan-400" : "bg-slate-800 text-slate-400"
                      }`}>
                        {step.status}
                      </span>

                      {step.approval_required && step.approval_state !== "approved" && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleApproveStep(step.step_id); }}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-md shadow transition"
                        >
                          Approve Step
                        </button>
                      )}

                      <svg className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>

                  {/* Expanded Step Inspection */}
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-2 border-t border-slate-800/80 bg-slate-950/40 rounded-b-xl space-y-3 text-xs text-slate-300 font-mono">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-slate-500 font-bold block mb-1">TOOL / ACTION</span>
                          <div className="p-2 rounded bg-slate-900 border border-slate-800">
                            {step.tool_id || "Domain Reasoning Core"}
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-500 font-bold block mb-1">CONFIDENCE & RISK</span>
                          <div className="p-2 rounded bg-slate-900 border border-slate-800 flex justify-between">
                            <span>Confidence: {(step.confidence * 100).toFixed(0)}%</span>
                            <span className="uppercase text-amber-400">Risk: {step.risk_level}</span>
                          </div>
                        </div>
                      </div>

                      {/* Evidence & Provenance */}
                      <div>
                        <span className="text-slate-500 font-bold block mb-1">EVIDENCE PROVENANCE</span>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800 space-y-1">
                          <div>Direct observation: Pottery typology visual features extracted from excavation photographs.</div>
                          <div className="text-slate-400 text-[11px]">Provenance Source: Archaeology Domain Vault (Verified Data)</div>
                        </div>
                      </div>

                      {/* Output Summary */}
                      <div>
                        <span className="text-slate-500 font-bold block mb-1">OUTPUT SUMMARY & HANDOFF PAYLOAD</span>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-emerald-400">
                          {step.result ? JSON.stringify(step.result) : "Step result available upon step completion."}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
