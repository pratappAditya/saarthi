import React, { useState } from "react";
import {
  MessageSquare,
  Brain,
  FolderKanban,
  Wrench,
  Settings,
  Plus,
  Trash2,
  Edit2,
  Search,
  Cpu,
  ShieldCheck,
  Menu,
  Briefcase,
} from "lucide-react";
import type { NavTab, SystemStatusInfo } from "../../types";
import { SaarthiLogo } from "../common/SaarthiLogo";

interface NavigationRailProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  systemStatus: SystemStatusInfo;
  onOpenSystemStatus: () => void;
  memoryCount: number;
  filesCount: number;
  sessions: { id: string; title: string; timestamp: string }[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onNewConversation: () => void;
}

export const NavigationRail: React.FC<NavigationRailProps> = ({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  systemStatus,
  onOpenSystemStatus,
  memoryCount,
  filesCount,
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
  onRenameSession,
  onNewConversation,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const startRename = (e: React.MouseEvent, id: string, title: string) => {
    e.stopPropagation();
    setEditingSessionId(id);
    setRenameValue(title);
  };

  const handleRenameSubmit = (id: string) => {
    if (renameValue.trim()) {
      onRenameSession(id, renameValue.trim());
    }
    setEditingSessionId(null);
  };

  return (
    <aside
      className={`relative flex flex-col justify-between h-full bg-[#0D0D0D] border-r border-white/5 transition-all duration-300 z-30 select-none ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Top Brand Logo Area */}
      <div className="flex flex-col min-h-0 flex-1">
        <div className="flex items-center justify-between p-4 border-b border-white/5">
          <div
            onClick={() => setActiveTab("home")}
            className="cursor-pointer overflow-hidden transition-opacity hover:opacity-90 flex items-center gap-2"
          >
            <SaarthiLogo showText={!collapsed} size={30} />
          </div>

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <Menu size={16} />
          </button>
        </div>

        {/* Air-Gapped / Connection Status Badge */}
        {!collapsed && (
          <div className="mx-3 my-3 px-3 py-2 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} className="text-[#F59E0B]" />
              <span className="text-[10px] font-mono tracking-wider text-white/70">
                AIR-GAPPED
              </span>
            </div>
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
          </div>
        )}

        {/* "New Conversation" Button */}
        {!collapsed && (
          <div className="px-3 mb-2">
            <button
              onClick={onNewConversation}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black text-xs font-semibold font-mono tracking-wide transition-all shadow-[0_0_15px_rgba(245,158,11,0.2)] cursor-pointer"
            >
              <Plus size={15} />
              <span>NEW SESSION</span>
            </button>
          </div>
        )}

        {/* Search Conversations */}
        {!collapsed && (
          <div className="px-3 mb-3 relative">
            <Search size={13} className="absolute left-6 top-1/2 -translate-y-1/2 text-white/40" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-8 pr-3 py-2 rounded-xl bg-[#141414] border border-white/5 text-white placeholder-white/20 text-[11px] focus:outline-none focus:border-[#F59E0B]/50 font-sans"
            />
          </div>
        )}

        {/* Conversation History (Scrollable List) */}
        {!collapsed ? (
          <div className="flex-1 overflow-y-auto px-3 space-y-1 scrollbar-thin">
            <div className="text-[9px] font-mono uppercase tracking-wider text-white/30 px-2 pb-1.5">
              CHATS HISTORY
            </div>
            {filteredSessions.map((sess) => {
              const isActive = activeSessionId === sess.id && activeTab === "chat";
              const isEditing = editingSessionId === sess.id;

              return (
                <div
                  key={sess.id}
                  onClick={() => {
                    onSelectSession(sess.id);
                    setActiveTab("chat");
                  }}
                  className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition-all border ${
                    isActive
                      ? "bg-[#141414] border-white/10 text-white shadow-lg"
                      : "border-transparent text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {/* Left saffron active bar */}
                  {isActive && (
                    <span className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r-full bg-[#F59E0B]" />
                  )}

                  <div className="flex items-center gap-2 min-w-0 flex-1 pr-4">
                    <MessageSquare size={13} className={isActive ? "text-[#F59E0B]" : "text-white/30"} />
                    {isEditing ? (
                      <input
                        type="text"
                        autoFocus
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        onBlur={() => handleRenameSubmit(sess.id)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") handleRenameSubmit(sess.id);
                          if (e.key === "Escape") setEditingSessionId(null);
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-zinc-800 text-white border border-[#F59E0B] text-xs px-1 rounded w-full focus:outline-none"
                      />
                    ) : (
                      <span className="text-xs truncate">{sess.title}</span>
                    )}
                  </div>

                  {/* Actions overlay */}
                  {!isEditing && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                      <button
                        onClick={(e) => startRename(e, sess.id, sess.title)}
                        className="p-1 rounded text-white/30 hover:text-white hover:bg-white/5"
                        title="Rename Session"
                      >
                        <Edit2 size={11} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteSession(sess.id);
                        }}
                        className="p-1 rounded text-white/30 hover:text-rose-400 hover:bg-white/5"
                        title="Delete Session"
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })}

            {filteredSessions.length === 0 && (
              <div className="text-[10px] text-white/20 text-center font-mono py-6">
                No sessions found.
              </div>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center gap-3 pt-4">
            <button
              onClick={onNewConversation}
              className="p-2 rounded-xl bg-[#F59E0B] text-black hover:bg-[#F59E0B]/90 shadow-lg cursor-pointer"
              title="New Conversation"
            >
              <Plus size={16} />
            </button>
            <button
              onClick={() => {
                setActiveTab("chat");
              }}
              className={`p-2 rounded-xl border ${
                activeTab === "chat" ? "bg-[#141414] border-white/10 text-[#F59E0B]" : "border-transparent text-white/40 hover:text-white hover:bg-white/5"
              } cursor-pointer`}
              title="Active Chat Workspace"
            >
              <MessageSquare size={16} />
            </button>
          </div>
        )}
      </div>

      {/* Bottom Footer Section */}
      <div className="p-2 border-t border-white/5 flex flex-col gap-1 shrink-0">
        {/* Navigation Rail for other tabs */}
        {!collapsed && (
          <div className="py-2 border-b border-white/5 space-y-0.5">
            <button
              onClick={() => setActiveTab("career")}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "career"
                  ? "bg-gradient-to-r from-cyan-500/20 to-blue-600/20 border border-cyan-500/40 text-cyan-300 shadow-md"
                  : "text-slate-300 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2">
                <Briefcase size={15} className={activeTab === "career" ? "text-cyan-400" : "text-cyan-500"} />
                <span className="font-bold tracking-tight">Career & Job Search</span>
              </div>
              <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-[9px] font-mono text-cyan-300 font-bold">
                PROD
              </span>
            </button>

            <button
              onClick={() => setActiveTab("memory")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                activeTab === "memory"
                  ? "bg-[#141414] border border-white/10 text-white"
                  : "text-white/50 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2">
                <Brain size={14} className={activeTab === "memory" ? "text-[#F59E0B]" : ""} />
                <span>Memory Core</span>
              </div>
              <span className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] font-mono text-white/40">
                {memoryCount}
              </span>
            </button>

            <button
              onClick={() => setActiveTab("files")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                activeTab === "files"
                  ? "bg-[#141414] border border-white/10 text-white"
                  : "text-white/50 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2">
                <FolderKanban size={14} className={activeTab === "files" ? "text-[#F59E0B]" : ""} />
                <span>Workspace Files</span>
              </div>
              <span className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] font-mono text-white/40">
                {filesCount}
              </span>
            </button>

            <button
              onClick={() => setActiveTab("tools")}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                activeTab === "tools"
                  ? "bg-[#141414] border border-white/10 text-white"
                  : "text-white/50 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <Wrench size={14} className={activeTab === "tools" ? "text-[#F59E0B]" : ""} />
              <span>Agent Tools</span>
            </button>
          </div>
        )}

        {/* Hardware Status Button */}
        <button
          onClick={onOpenSystemStatus}
          className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-mono transition-all ${
            collapsed ? "justify-center" : "justify-between"
          } bg-[#141414] hover:bg-white/10 text-white/70 border border-white/5 cursor-pointer`}
          title="System Hardware Diagnostics"
        >
          <div className="flex items-center gap-2 min-w-0">
            <Cpu size={15} className="text-[#F59E0B]" />
            {!collapsed && <span className="text-[11px] truncate">GPU utilization</span>}
          </div>
          {!collapsed && (
            <span className="text-[10px] text-[#F59E0B] font-sans shrink-0 animate-pulse">
              ● Connected
            </span>
          )}
        </button>

        {/* Settings Button */}
        <button
          onClick={() => setActiveTab("settings")}
          className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer ${
            activeTab === "settings"
              ? "bg-[#141414] text-white border border-white/10"
              : "text-white/40 hover:text-white hover:bg-white/5 border border-transparent"
          }`}
          title={collapsed ? "Settings" : undefined}
        >
          <Settings size={15} className={activeTab === "settings" ? "text-[#F59E0B]" : ""} />
          {!collapsed && <span>Settings</span>}
        </button>
      </div>
    </aside>
  );
};

