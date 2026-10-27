import React from "react";
import {
  Cpu,
  ShieldCheck,
  X,
  Server,
} from "lucide-react";
import type { SystemStatusInfo } from "../../types";

interface SystemStatusModalProps {
  open: boolean;
  onClose: () => void;
  status: SystemStatusInfo;
}

export const SystemStatusModal: React.FC<SystemStatusModalProps> = ({
  open,
  onClose,
  status,
}) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in select-none">
      <div className="relative w-full max-w-xl rounded-2xl bg-[#0D0D0D] border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.9)] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-[#141414] border-b border-white/5">
          <div className="flex items-center gap-2">
            <Cpu size={18} className="text-sky-400" />
            <h3 className="text-sm font-semibold text-white tracking-wide font-mono">
              SYSTEM HARDWARE & LOCAL AI DIAGNOSTICS
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-white/50 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          >
            <X size={16} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4 text-xs font-mono">
          {/* Air gapped callout */}
          <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck size={18} className="text-emerald-400" />
              <span className="font-semibold">CONNECTION: LOCAL ONLY</span>
            </div>
            <span className="text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded uppercase">
              100% Air-Gapped Ready
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-[#141414] border border-white/5 space-y-1">
              <span className="text-[10px] text-white/40 uppercase">Local AI Model</span>
              <div className="text-[#F59E0B] font-bold text-sm">{status.modelName}</div>
              <div className="text-[10px] text-white/40">{status.provider}</div>
            </div>

            <div className="p-3 rounded-xl bg-[#141414] border border-white/5 space-y-1">
              <span className="text-[10px] text-white/40 uppercase">GPU Accelerator</span>
              <div className="text-sky-300 font-bold text-xs truncate">{status.gpuName}</div>
              <div className="text-[10px] text-white/40">Utilization: {status.gpuUsage}%</div>
            </div>

            <div className="p-3 rounded-xl bg-[#141414] border border-white/5 space-y-1">
              <span className="text-[10px] text-white/40 uppercase">System RAM</span>
              <div className="text-purple-300 font-bold text-sm">
                {status.ramUsageGb} / {status.ramTotalGb} GB DDR4
              </div>
              <div className="text-[10px] text-white/40">Active memory cache clean</div>
            </div>

            <div className="p-3 rounded-xl bg-[#141414] border border-white/5 space-y-1">
              <span className="text-[10px] text-white/40 uppercase">Storage Path</span>
              <div className="text-white/80 font-bold text-xs">{status.storagePath}</div>
              <div className="text-[10px] text-white/40">
                {status.storageUsageGb} GB / {status.storageTotalGb} GB used
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#141414] border border-white/5 space-y-2">
            <div className="flex items-center justify-between text-white/90 font-bold">
              <span className="flex items-center gap-1.5">
                <Server size={14} className="text-[#F59E0B]" /> OLLAMA LOCAL BINDING
              </span>
              <span className="text-[#F59E0B]">Port {status.ollamaPort}</span>
            </div>
            <p className="text-[11px] text-white/60 font-sans leading-normal">
              Saarthi communicates directly with local port <code className="text-[#F59E0B]">127.0.0.1:{status.ollamaPort}</code> via direct IPC socket. Your files never leave your computer.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

