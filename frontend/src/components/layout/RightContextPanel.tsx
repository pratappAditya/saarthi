import React from "react";
import {
  X,
  Activity,
  Cpu,
  Brain,
  HardDrive,
  ExternalLink,
  Wrench,
  Terminal,
  FileText,
  ShieldAlert,
} from "lucide-react";
import type { ActivityLog, MemoryItem, SystemStatusInfo, Message, SaarthiState } from "../../types";

interface RightContextPanelProps {
  open: boolean;
  onClose: () => void;
  activities: ActivityLog[];
  memories: MemoryItem[];
  systemStatus: SystemStatusInfo;
  onSelectMemory: (memory: MemoryItem) => void;
  saarthiState: SaarthiState;
  messages: Message[];
}

export const RightContextPanel: React.FC<RightContextPanelProps> = ({
  open,
  onClose,
  activities,
  memories,
  systemStatus,
  onSelectMemory,
  saarthiState,
  messages,
}) => {
  if (!open) return null;

  // Detect latest tool execution from message history
  const activeToolMessage = [...messages]
    .reverse()
    .find((m) => m.sender === "saarthi" && m.toolExecution);
  const activeTool = activeToolMessage?.toolExecution;

  const isThinking = String(saarthiState) === "thinking" || String(saarthiState) === "tool_executing";
  const isWaitingPermission = String(saarthiState) === "waiting_permission";

  // Check if active tool relates to file system or memory core
  const isMemoryTool = activeTool?.name.includes("memory") || activeTool?.name.includes("remember");
  const isFileTool = activeTool?.name.includes("file") || activeTool?.name.includes("list") || activeTool?.name.includes("read");

  return (
    <aside className="w-80 h-full bg-[#0D0D0D] border-l border-white/5 flex flex-col z-20 select-none overflow-hidden backdrop-blur-md">
      {/* Drawer Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Activity size={15} className="text-[#F59E0B]" />
          <span className="text-[11px] font-mono tracking-[0.2em] text-white/50 uppercase">
            AGENT COCKPIT DIAGNOSTICS
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <X size={15} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 text-xs scrollbar-thin">
        {/* SYSTEM STATUS — GPU/CPU/Ollama status */}
        <div className="relative p-3.5 rounded-xl bg-[#141414] border border-white/5 space-y-3 overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#F59E0B]" />
          <div className="flex items-center justify-between font-mono text-[10px] text-white/60 pl-1">
            <span className="flex items-center gap-1.5 font-bold text-white/80">
              <Cpu size={14} className="text-[#F59E0B]" /> HARDWARE STATUS
            </span>
            <span className="text-emerald-400 font-bold">● ONLINE</span>
          </div>

          <div className="space-y-2.5 font-mono text-[10px] pl-1">
            <div>
              <div className="flex justify-between text-white/40 mb-1">
                <span>GPU ({((systemStatus.gpuName || "")).split(" ")[0] || "GPU"})</span>
                <span className="text-[#F59E0B] font-bold">{systemStatus.gpuUsage}%</span>
              </div>
              <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-[#F59E0B] h-full rounded-full"
                  style={{ width: `${systemStatus.gpuUsage}%` }}
                />
              </div>
            </div>

            <div className="flex justify-between text-white/40 text-[9px] pt-1 border-t border-white/5">
              <span>MODEL PROVIDER:</span>
              <span className="text-white/85 uppercase">{systemStatus.provider}</span>
            </div>
            <div className="flex justify-between text-white/40 text-[9px]">
              <span>ACTIVE MODEL:</span>
              <span className="text-[#F59E0B] font-bold">{systemStatus.modelName}</span>
            </div>
          </div>
        </div>

        {/* PERMISSION STATE */}
        {isWaitingPermission && (
          <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-2.5">
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-rose-400 uppercase font-bold">
              <ShieldAlert size={14} /> SECURITY CLEARANCE PENDING
            </div>
            <p className="text-[11px] text-white/70 leading-relaxed font-sans">
              Saarthi has requested permission to run an external tool action. Approve or deny this action in the main canvas.
            </p>
          </div>
        )}

        {/* MEMORY PIPELINE STATE */}
        {isThinking && isMemoryTool && activeTool && (
          <div className="p-3.5 rounded-xl bg-[#141414] border border-[#F59E0B]/30 space-y-2.5">
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#F59E0B] uppercase font-bold">
              <Brain size={14} /> MEMORY CORE ACCESS
            </div>
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-white/30 uppercase">Active Action:</span>
              <div className="font-mono text-[10px] bg-black/60 p-2 rounded text-zinc-300">
                {activeTool.name}
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-white/30 uppercase">Operation target:</span>
              <div className="text-[11px] text-white/80 italic font-sans leading-relaxed">
                Reading facts matching localized query vectors.
              </div>
            </div>
          </div>
        )}

        {/* FILE PIPELINE STATE */}
        {isThinking && isFileTool && activeTool && (
          <div className="p-3.5 rounded-xl bg-[#141414] border border-[#F59E0B]/30 space-y-2.5">
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-sky-400 uppercase font-bold">
              <HardDrive size={14} /> WORKSPACE FILE PIPELINE
            </div>
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-white/30 uppercase">Active Tool:</span>
              <div className="font-mono text-[10px] bg-black/60 p-2 rounded text-zinc-300">
                {activeTool.name}
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-white/30 uppercase">Path:</span>
              <div className="text-[11px] text-[#F59E0B] font-mono truncate select-all">
                {activeTool.command}
              </div>
            </div>
          </div>
        )}

        {/* OTHER TOOLS PIPELINE STATE */}
        {isThinking && !isMemoryTool && !isFileTool && activeTool && (
          <div className="p-3.5 rounded-xl bg-[#141414] border border-white/10 space-y-2.5">
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-zinc-300 uppercase font-bold">
              <Wrench size={14} className="text-[#F59E0B]" /> ACTIVE TOOL EXECUTION
            </div>
            <div className="space-y-1">
              <div className="font-semibold text-white text-xs font-mono">{activeTool.name}</div>
              <div className="font-mono text-[10px] bg-black/60 p-2 rounded text-zinc-300 break-all select-all leading-normal">
                $ {activeTool.command}
              </div>
            </div>
            {activeTool.resultSummary && (
              <div className="space-y-1">
                <span className="text-[9px] font-mono text-white/30 uppercase">Payload preview:</span>
                <div className="text-[11px] text-white/60 line-clamp-3 font-mono leading-relaxed bg-black/30 p-2 rounded border border-white/5">
                  {activeTool.resultSummary}
                </div>
              </div>
            )}
          </div>
        )}

        {/* IDLE STATE: System & Workspace Overview */}
        {!isThinking && !isWaitingPermission && (
          <div className="space-y-4">
            {/* Workspace Cockpit Profile */}
            <div className="p-3.5 rounded-xl bg-[#141414] border border-white/5 space-y-2.5">
              <div className="text-[10px] font-mono text-white/40 uppercase tracking-[0.15em]">
                WORKSPACE COCKPIT
              </div>
              <div className="space-y-1.5 text-[11px] font-mono">
                <div className="flex justify-between">
                  <span className="text-white/30">Sandbox Root:</span>
                  <span className="text-[#F59E0B] font-semibold">E:\Saarthi</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/30">SQLite Memory:</span>
                  <span className="text-zinc-400">saarthi.db</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/30">Saved Memories:</span>
                  <span className="text-emerald-400">{memories.length} facts</span>
                </div>
              </div>
            </div>

            {/* Pinned Memories */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-[10px] font-mono text-white/40 uppercase tracking-[0.15em]">
                <span className="flex items-center gap-1.5">
                  <Brain size={13} className="text-[#F59E0B]" /> Pinned Memories
                </span>
                <span className="text-[#F59E0B] font-mono">{memories.filter((m) => m.pinned).length}</span>
              </div>
              <div className="space-y-2">
                {memories.filter((m) => m.pinned).slice(0, 2).map((mem) => (
                  <div
                    key={mem.id}
                    onClick={() => onSelectMemory(mem)}
                    className="p-3 rounded-xl bg-[#141414] border border-white/5 hover:border-[#F59E0B]/30 cursor-pointer transition-all group"
                  >
                    <div className="flex items-center justify-between font-medium text-white/95 group-hover:text-[#F59E0B] truncate">
                      <span>{mem.title}</span>
                      <ExternalLink size={10} className="text-white/35 group-hover:text-[#F59E0B]" />
                    </div>
                    <p className="text-[10px] text-white/40 line-clamp-2 mt-1 leading-normal">
                      {mem.content}
                    </p>
                  </div>
                ))}
                {memories.filter((m) => m.pinned).length === 0 && (
                  <div className="p-3 text-center text-white/20 font-mono text-[9px] bg-white/5 border border-dashed border-white/10 rounded-xl">
                    No memories pinned.
                  </div>
                )}
              </div>
            </div>

            {/* Actions Log */}
            <div className="space-y-2.5">
              <div className="text-[10px] font-mono text-white/40 uppercase tracking-[0.15em]">
                CHRONO ACTION LOG
              </div>
              <div className="relative pl-3.5 border-l border-white/10 space-y-3">
                {activities.slice(0, 3).map((act) => (
                  <div key={act.id} className="relative space-y-0.5">
                    <div className="absolute -left-[19px] top-1 w-2 h-2 rounded-full bg-[#F59E0B] shadow-[0_0_6px_#F59E0B]" />
                    <div className="flex items-center justify-between font-mono text-[9px] text-white/30">
                      <span>{act.timeFormatted}</span>
                      <span className="text-[#F59E0B] font-sans">{act.toolName}</span>
                    </div>
                    <div className="font-semibold text-white/80 leading-snug text-xs truncate">
                      {act.title}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

