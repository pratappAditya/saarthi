import React from "react";
import { Search, Command, PanelRight, Sparkles } from "lucide-react";
import type { NavTab, SaarthiState } from "../../types";

interface HeaderProps {
  activeTab: NavTab;
  saarthiState: SaarthiState;
  onOpenCommandPalette: () => void;
  rightPanelOpen: boolean;
  setRightPanelOpen: (open: boolean) => void;
  onTriggerNewChat: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  saarthiState,
  onOpenCommandPalette,
  rightPanelOpen,
  setRightPanelOpen,
  onTriggerNewChat,
}) => {
  const titles: Record<NavTab, { title: string; subtitle: string }> = {
    home: { title: "Command Center", subtitle: "Your local AI operating system" },
    career: { title: "Career & Job Search Workspace", subtitle: "ATS match, resume tailoring & job application tracker" },
    chat: { title: "Agent Workspace", subtitle: "Interactive reasoning & tool canvas" },
    memory: { title: "Local Memory Core", subtitle: "Context, facts & projects stored locally" },
    files: { title: "File Workspace", subtitle: "Indexed documents & directory search" },
    tasks: { title: "Task Manager", subtitle: "Agent-integrated action schedule" },
    activity: { title: "Activity Center", subtitle: "Chronological local operation log" },
    tools: { title: "Agent Tool Catalog", subtitle: "Local capabilities & permissions" },
    settings: { title: "System Settings", subtitle: "Model, privacy & storage controls" },
  };

  const currentInfo = titles[activeTab] || { title: "Saarthi", subtitle: "Local AI Agent" };

  return (
    <header className="flex items-center justify-between h-16 px-6 md:px-10 bg-[#0D0D0D]/90 border-b border-white/5 z-20 select-none">
      {/* Title & Operational Context */}
      <div className="flex items-center gap-4">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono tracking-[0.2em] text-white/30 uppercase">
              Operational Context
            </span>
            <div className="w-1.5 h-1.5 bg-[#F59E0B] rounded-full animate-pulse" />
          </div>
          <h1 className="text-sm font-medium text-white tracking-wide">
            {currentInfo.title}
          </h1>
        </div>
      </div>

      {/* Center & Right Controls */}
      <div className="flex items-center gap-3">
        {/* Global Search & Command Palette Bar */}
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-3 px-3.5 py-1.5 rounded-xl bg-[#141414] border border-white/10 hover:border-[#F59E0B]/40 text-white/50 hover:text-white text-xs transition-all w-52 md:w-72 group"
        >
          <Search size={14} className="text-white/30 group-hover:text-[#F59E0B]" />
          <span className="flex-1 text-left truncate">Search memory or command Saarthi...</span>
          <div className="flex items-center gap-1">
            <span className="text-[10px] font-bold text-white/20 border border-white/10 rounded px-1.5 py-0.5 font-mono">
              CTRL
            </span>
            <span className="text-[10px] font-bold text-white/20 border border-white/10 rounded px-1.5 py-0.5 font-mono">
              K
            </span>
          </div>
        </button>

        {/* Status Badge Pill */}
        <div className="hidden lg:flex bg-white/5 border border-white/10 rounded-full px-4 py-1.5 items-center gap-3">
          <span className="text-[10px] font-bold text-[#F59E0B]">●</span>
          <span className="text-[11px] font-medium tracking-wide text-white">
            SAARTHI CORE 4B
          </span>
          <span className="text-white/20 text-[10px]">|</span>
          <span className="text-[11px] text-white/50 font-mono">LOCAL INSTANCE</span>
        </div>

        {/* Quick New Chat Action */}
        <button
          onClick={onTriggerNewChat}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#F59E0B]/15 hover:bg-[#F59E0B]/25 text-[#F59E0B] text-xs font-semibold border border-[#F59E0B]/30 transition-all cursor-pointer"
        >
          <Sparkles size={13} />
          <span>New Session</span>
        </button>

        {/* Toggle Right Context Panel */}
        <button
          onClick={() => setRightPanelOpen(!rightPanelOpen)}
          className={`p-2 rounded-xl border text-white/50 transition-colors ${
            rightPanelOpen
              ? "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30"
              : "bg-[#141414] border-white/10 hover:text-white"
          }`}
          title="Toggle Context & Activity Drawer"
        >
          <PanelRight size={16} />
        </button>
      </div>
    </header>
  );
};

