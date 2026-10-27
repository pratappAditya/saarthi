import React from "react";
import {
  ShieldAlert,
  AlertTriangle,
  X,
  Check,
  Terminal,
  FileCode,
  HardDrive,
} from "lucide-react";
import type { PermissionRequest } from "../../types";

interface PermissionModalProps {
  request: PermissionRequest | null;
  onAllowOnce: (id: string) => void;
  onAlwaysAllow: (id: string) => void;
  onDeny: (id: string) => void;
}

export const PermissionModal: React.FC<PermissionModalProps> = ({
  request,
  onAllowOnce,
  onAlwaysAllow,
  onDeny,
}) => {
  if (!request) return null;

  const isHighRisk = request.riskLevel === "high";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in select-none">
      <div
        className={`relative w-full max-w-lg rounded-2xl bg-[#0D0D0D] border transition-all duration-300 ${
          isHighRisk
            ? "border-rose-500/50 shadow-[0_0_50px_rgba(244,63,94,0.25)]"
            : "border-[#F59E0B]/40 shadow-[0_0_50px_rgba(245,158,11,0.2)]"
        } overflow-hidden`}
      >
        {/* Top Warning Banner */}
        <div
          className={`flex items-center justify-between p-4 border-b ${
            isHighRisk
              ? "bg-gradient-to-r from-rose-500/20 via-rose-500/10 to-transparent border-rose-500/20"
              : "bg-gradient-to-r from-[#F59E0B]/20 via-[#F59E0B]/10 to-transparent border-[#F59E0B]/20"
          }`}
        >
          <div className="flex items-center gap-2.5">
            <div
              className={`p-2 rounded-xl border ${
                isHighRisk
                  ? "bg-rose-500/20 border-rose-500/40 text-rose-400"
                  : "bg-[#F59E0B]/20 border-[#F59E0B]/40 text-[#F59E0B]"
              }`}
            >
              <ShieldAlert size={20} className={isHighRisk ? "animate-pulse" : ""} />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white tracking-widest font-mono">
                SAARTHI ELEVATED PRIVILEGE
              </h3>
              <p className="text-[10px] text-white/40 font-mono">
                Verification required for local action
              </p>
            </div>
          </div>

          <span
            className={`px-2.5 py-0.5 rounded-full text-[9px] font-mono uppercase font-bold border tracking-wider ${
              isHighRisk
                ? "bg-rose-500/25 text-rose-300 border-rose-500/40"
                : "bg-[#F59E0B]/25 text-[#F59E0B] border-[#F59E0B]/40"
            }`}
          >
            RISK: {request.riskLevel}
          </span>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4 text-xs font-sans">
          {/* WHAT */}
          <div className="space-y-1">
            <span className="text-[9px] font-mono text-white/30 uppercase tracking-widest flex items-center gap-1">
              <Terminal size={11} className="text-[#F59E0B]" /> EXECUTABLE COMMAND:
            </span>
            <div className="p-3 rounded-xl bg-black border border-white/5 font-mono text-[#F59E0B] text-[11px] break-all select-all leading-normal">
              {request.command}
            </div>
          </div>

          {/* WHY */}
          <div className="space-y-1">
            <span className="text-[9px] font-mono text-white/30 uppercase tracking-widest flex items-center gap-1">
              <AlertTriangle size={11} className="text-sky-400" /> SYSTEM REASONING / PURPOSE:
            </span>
            <p className="p-3 rounded-xl bg-[#141414] border border-white/5 text-white/80 leading-relaxed text-xs">
              {request.purpose}
            </p>
          </div>

          {/* AFFECTED RESOURCES */}
          {request.affectedResources && request.affectedResources.length > 0 && (
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-white/30 uppercase tracking-widest flex items-center gap-1">
                <HardDrive size={11} className="text-purple-400" /> AFFECTED DIRECTORIES:
              </span>
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {request.affectedResources.map((res, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded-lg bg-[#141414] border border-white/10 font-mono text-[10px] text-white/70 flex items-center gap-1"
                  >
                    <FileCode size={11} className="text-white/40" /> {res}
                  </span>
                ))}
              </div>
            </div>
          )}

          <p className="text-[10px] text-white/30 italic pt-1 font-mono">
            Note: Execution remains local to the sandboxed path inside E:\Saarthi.
          </p>
        </div>

        {/* Actions Footer */}
        <div className="p-4 bg-[#141414] border-t border-white/5 flex items-center justify-between gap-2">
          <button
            onClick={() => onDeny(request.id)}
            className="px-4 py-2 rounded-xl bg-white/5 hover:bg-rose-500/10 hover:text-rose-400 text-white/70 font-medium text-xs flex items-center gap-1.5 transition-colors cursor-pointer border border-transparent hover:border-rose-500/20"
          >
            <X size={14} /> Reject Command
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onAllowOnce(request.id)}
              className="px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium text-xs border border-white/10 transition-colors cursor-pointer"
            >
              Allow once
            </button>
            <button
              onClick={() => onAlwaysAllow(request.id)}
              className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer ${
                isHighRisk
                  ? "bg-rose-500 hover:bg-rose-600 text-white shadow-[0_0_15px_rgba(244,63,94,0.4)]"
                  : "bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black shadow-[0_0_15px_rgba(245,158,11,0.3)]"
              }`}
            >
              <Check size={14} /> Authorize Execution
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

