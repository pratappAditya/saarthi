import React, { useState } from "react";
import {
  Search,
  FileText,
  CheckSquare,
  FileSearch,
  Code2,
  Cpu,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { SaarthiOrb } from "../common/SaarthiOrb";
import type { SaarthiState, TaskItem, MemoryItem, FileItem } from "../../types";

interface HomeScreenProps {
  onSendMessage: (text: string) => void;
  saarthiState: SaarthiState;
  tasks: TaskItem[];
  files: FileItem[];
  memories: MemoryItem[];
  onNavigateTab: (tab: any) => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({
  onSendMessage,
  saarthiState,
  tasks,
  files,
  memories,
  onNavigateTab,
}) => {
  const [inputQuery, setInputQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim()) return;
    onSendMessage(inputQuery);
    setInputQuery("");
  };

  const quickActions = [
    {
      icon: FileText,
      label: "Import Resume",
      prompt: "Import my resume and extract core skill profile",
    },
    {
      icon: FileSearch,
      label: "ATS Analysis",
      prompt: "Analyze job description and give ATS match score",
    },
    {
      icon: Sparkles,
      label: "Tailor Resume",
      prompt: "Tailor my resume keywords for target Software Engineer position",
    },
    {
      icon: CheckSquare,
      label: "Cover Letter",
      prompt: "Generate custom cover letter for target role",
    },
    {
      icon: ShieldCheck,
      label: "Browser Assistant Safety",
      prompt: "Explain Browser Assistant auto-fill and explicit confirmation rules",
    },
  ];
  // Resolve precise orb state
  let resolvedOrbState: any = "idle";
  const st = String(saarthiState);
  if (st === "error") resolvedOrbState = "error";
  else if (st === "listening") resolvedOrbState = "listening";
  else if (st === "waiting_permission") resolvedOrbState = "waiting_permission";
  else if (st === "generating") resolvedOrbState = "responding";
  else if (st === "thinking" || st === "tool_executing") resolvedOrbState = "thinking";

  return (
    <div className="relative flex-1 flex flex-col items-center justify-between p-6 overflow-y-auto select-none bg-[#0A0A0A]">
      {/* Background Ambient Glowing Auras */}
      <div className="absolute top-[-20%] left-[30%] w-[500px] h-[500px] bg-[#F59E0B]/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[10%] w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Top Banner - Air-Gapped Local Status */}
      <div className="w-full max-w-4xl flex items-center justify-between py-2 px-4 rounded-xl bg-[#0D0D0D] border border-white/5 backdrop-blur-md z-10">
        <div className="flex items-center gap-2 text-xs font-mono text-white/50">
          <ShieldCheck size={14} className="text-[#F59E0B]" />
          <span>SAARTHI CAREER ASSISTANT: 100% Local Private Processing on PC</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Student Plan Active (₹149/mo)</span>
        </div>
      </div>

      {/* Center Intelligence Hero Section */}
      <div className="w-full max-w-3xl my-auto flex flex-col items-center text-center py-6 space-y-8 z-10">
        <SaarthiOrb state={resolvedOrbState} size="lg" />

        <div className="space-y-2 max-w-lg">
          <p className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#F59E0B] flex items-center justify-center gap-1.5">
            <Sparkles size={12} /> YOUR AI COMPANION
          </p>
          <h2 className="text-3xl font-semibold text-white tracking-tight">
            Good afternoon.
          </h2>
          <p className="text-white/40 text-sm">
            What are we working on today?
          </p>
        </div>

        {/* Command Input Field with Gradient Border Glow */}
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-2xl relative group transition-all"
        >
          <div className="absolute -inset-0.5 bg-gradient-to-r from-[#F59E0B]/20 to-transparent rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-500" />

          <div className="relative flex items-center rounded-2xl bg-[#141414] border border-white/10 group-hover:border-[#F59E0B]/50 focus-within:border-[#F59E0B] shadow-2xl p-2.5 transition-all">
            <Search className="ml-3 text-white/30 group-hover:text-[#F59E0B] transition-colors" size={18} />
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask Saarthi anything, search files, or launch a task..."
              className="w-full px-4 py-2 bg-transparent text-white placeholder-white/20 text-sm focus:outline-none font-sans"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim()}
              className="px-4 py-2 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 disabled:opacity-30 text-black font-semibold text-xs flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
            >
              <span>Ask</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </form>

        {/* Quick Action Suggestion Pills */}
        <div className="w-full max-w-2xl flex flex-wrap items-center justify-center gap-2.5 pt-2">
          {quickActions.map((act, idx) => {
            const Icon = act.icon;
            return (
              <button
                key={idx}
                onClick={() => onSendMessage(act.prompt)}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/5 text-xs text-white/70 hover:text-white hover:bg-white/10 hover:border-white/10 transition-all cursor-pointer backdrop-blur-md"
              >
                <Icon size={13} className="text-[#F59E0B]" />
                <span>{act.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom Summary Grid Cards */}
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-white/5 z-10">
        {/* Today's Tasks Card */}
        <div
          onClick={() => onNavigateTab("tasks")}
          className="p-4 rounded-xl bg-[#0D0D0D] border border-white/5 hover:border-[#F59E0B]/30 cursor-pointer transition-all group"
        >
          <div className="flex items-center justify-between text-xs font-mono text-white/40 mb-2">
            <span className="flex items-center gap-1.5 group-hover:text-[#F59E0B]">
              <CheckSquare size={14} className="text-[#F59E0B]" /> SCHEDULE
            </span>
            <span className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded text-white/60">
              {tasks.filter((t) => t.status === "today").length} today
            </span>
          </div>
          <div className="text-xs font-medium text-white/90 line-clamp-1">
            {tasks.find((t) => t.status === "today")?.title || "No pending tasks for today"}
          </div>
          <p className="text-[11px] text-white/30 mt-1">
            Saarthi monitors and reminds you automatically
          </p>
        </div>

        {/* Local Memory Highlights Card */}
        <div
          onClick={() => onNavigateTab("memory")}
          className="p-4 rounded-xl bg-[#0D0D0D] border border-white/5 hover:border-[#F59E0B]/30 cursor-pointer transition-all group"
        >
          <div className="flex items-center justify-between text-xs font-mono text-white/40 mb-2">
            <span className="flex items-center gap-1.5 group-hover:text-[#F59E0B]">
              <Zap size={14} className="text-sky-400" /> LOCAL MEMORY
            </span>
            <span className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded text-white/60">
              {memories.length} facts
            </span>
          </div>
          <div className="text-xs font-medium text-white/90 line-clamp-1">
            {memories[0]?.title || "Preferences stored on computer"}
          </div>
          <p className="text-[11px] text-white/30 mt-1">
            100% private and stored inside E:\Saarthi
          </p>
        </div>

        {/* Indexed Files Workspace Card */}
        <div
          onClick={() => onNavigateTab("files")}
          className="p-4 rounded-xl bg-[#0D0D0D] border border-white/5 hover:border-[#F59E0B]/30 cursor-pointer transition-all group"
        >
          <div className="flex items-center justify-between text-xs font-mono text-white/40 mb-2">
            <span className="flex items-center gap-1.5 group-hover:text-[#F59E0B]">
              <FileSearch size={14} className="text-purple-400" /> FILE WORKSPACE
            </span>
            <span className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded text-white/60">
              {files.length} indexed
            </span>
          </div>
          <div className="text-xs font-medium text-white/90 line-clamp-1">
            {files[0]?.name || "Architecture_Spec_v2.pdf"}
          </div>
          <p className="text-[11px] text-white/30 mt-1">
            Drag and drop documents to analyze
          </p>
        </div>
      </div>
    </div>
  );
};

