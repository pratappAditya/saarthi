import React, { useState } from "react";
import {
  Wrench,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Terminal,
} from "lucide-react";
import type { ToolExecution } from "../../types";

interface ToolCardProps {
  tool: ToolExecution;
  onApprove?: (toolId: string) => void;
  onDeny?: (toolId: string) => void;
}

export const ToolCard: React.FC<ToolCardProps> = ({
  tool,
  onApprove,
  onDeny,
}) => {
  const [expanded, setExpanded] = useState(false);

  const statusMap = {
    queued: {
      color: "border-white/10 bg-[#141414] text-white/50",
      icon: Clock,
      label: "QUEUED",
    },
    running: {
      color: "border-[#F59E0B]/40 bg-[#141414] text-[#F59E0B] animate-pulse",
      icon: Clock,
      label: "RUNNING...",
    },
    success: {
      color: "border-emerald-500/30 bg-[#141414] text-emerald-400",
      icon: CheckCircle2,
      label: "SUCCESS",
    },
    failed: {
      color: "border-rose-500/40 bg-[#141414] text-rose-400",
      icon: XCircle,
      label: "FAILED",
    },
    approval_required: {
      color: "border-[#F59E0B]/50 bg-[#141414] text-[#F59E0B]",
      icon: ShieldAlert,
      label: "APPROVAL REQUIRED",
    },
  };

  const currentStatus = statusMap[tool.status as keyof typeof statusMap] || statusMap.queued;
  const StatusIcon = currentStatus.icon;

  return (
    <div
      className={`my-3 rounded-xl border ${currentStatus.color} p-4 transition-all select-none text-xs space-y-2.5 shadow-lg`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-[#0D0D0D] border border-white/10">
            <Wrench size={14} className="text-[#F59E0B]" />
          </div>
          <span className="font-semibold text-white/90 font-mono">
            {tool.name}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2.5 py-0.5 rounded-full font-mono text-[10px] uppercase font-medium tracking-wider flex items-center gap-1 bg-[#0D0D0D] border border-white/10">
            <StatusIcon size={12} /> {currentStatus.label}
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 rounded text-white/40 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
            title="Inspect technical execution details"
          >
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>
      </div>

      {/* Executed Command & Target */}
      <div className="font-mono text-[11px] bg-[#0D0D0D] p-2.5 rounded-lg border border-white/5 text-white/80 flex items-center justify-between gap-2 overflow-x-auto">
        <span className="text-[#F59E0B] font-bold">$</span>
        <span className="flex-1 truncate">{tool.command}</span>
        {tool.timestamp && (
          <span className="text-white/30 text-[10px]">{tool.timestamp}</span>
        )}
      </div>

      {/* Result summary */}
      {tool.resultSummary && (
        <div className="text-white/70 font-sans leading-relaxed">
          {tool.resultSummary}
        </div>
      )}

      {/* Approval Buttons if waiting approval */}
      {tool.status === "approval_required" && (
        <div className="pt-2 border-t border-[#F59E0B]/20 flex items-center justify-end gap-2">
          <button
            onClick={() => onDeny && onDeny(tool.id)}
            className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 font-medium text-xs transition-colors cursor-pointer"
          >
            Deny Execution
          </button>
          <button
            onClick={() => onApprove && onApprove(tool.id)}
            className="px-3 py-1.5 rounded-lg bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-semibold text-xs transition-colors shadow-[0_0_12px_rgba(245,158,11,0.3)] cursor-pointer"
          >
            Approve & Execute
          </button>
        </div>
      )}

      {/* Expanded Technical Details */}
      {expanded && tool.techDetails && (
        <div className="pt-2 border-t border-white/10 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-white/40 uppercase">
            <Terminal size={12} className="text-[#F59E0B]" /> Technical Payload & Execution Log
          </div>
          <pre className="p-2.5 rounded-lg bg-[#0D0D0D] text-[#F59E0B]/90 font-mono text-[10px] overflow-x-auto border border-white/5 leading-tight">
            {tool.techDetails}
          </pre>
        </div>
      )}
    </div>
  );
};

