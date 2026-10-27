import React, { useState, useEffect } from "react";
import {
  Search,
  Home,
  MessageSquare,
  Brain,
  FolderKanban,
  CheckSquare,
  Activity,
  Wrench,
  Settings,
  Cpu,
  Sparkles,
  ArrowRight,
  Shield,
} from "lucide-react";
import type { NavTab } from "../../types";

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onNavigateTab: (tab: NavTab) => void;
  onSendMessage: (query: string) => void;
  onOpenSystemStatus: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  open,
  onClose,
  onNavigateTab,
  onSendMessage,
  onOpenSystemStatus,
}) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (open) onClose();
        else setQuery("");
      } else if (e.key === "Escape" && open) {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const options = [
    {
      id: "ask",
      title: `Ask Saarthi: "${query || "..."}"`,
      category: "Prompt",
      icon: Sparkles,
      action: () => {
        if (query.trim()) {
          onSendMessage(query);
          onClose();
        }
      },
    },
    {
      id: "nav-home",
      title: "Open Command Center (Home)",
      category: "Navigation",
      icon: Home,
      action: () => {
        onNavigateTab("home");
        onClose();
      },
    },
    {
      id: "nav-chat",
      title: "Open Agent Workspace (Chat)",
      category: "Navigation",
      icon: MessageSquare,
      action: () => {
        onNavigateTab("chat");
        onClose();
      },
    },
    {
      id: "nav-memory",
      title: "Open Local Memory Core",
      category: "Navigation",
      icon: Brain,
      action: () => {
        onNavigateTab("memory");
        onClose();
      },
    },
    {
      id: "nav-files",
      title: "Open File Workspace (E:\\Saarthi)",
      category: "Navigation",
      icon: FolderKanban,
      action: () => {
        onNavigateTab("files");
        onClose();
      },
    },
    {
      id: "nav-admin",
      title: "Open Admin Control Panel (Privileged Surface)",
      category: "Administration",
      icon: Shield,
      action: () => {
        onNavigateTab("admin" as any);
        onClose();
      },
    },
    {
      id: "nav-tasks",
      title: "Open Task Manager",
      category: "Navigation",
      icon: CheckSquare,
      action: () => {
        onNavigateTab("tasks");
        onClose();
      },
    },
    {
      id: "nav-activity",
      title: "View Activity Audit Log",
      category: "Navigation",
      icon: Activity,
      action: () => {
        onNavigateTab("activity");
        onClose();
      },
    },
    {
      id: "nav-tools",
      title: "View Agent Tool Catalog & Permissions",
      category: "Navigation",
      icon: Wrench,
      action: () => {
        onNavigateTab("tools");
        onClose();
      },
    },
    {
      id: "nav-system",
      title: "Check System Hardware & GPU Utilization",
      category: "System",
      icon: Cpu,
      action: () => {
        onOpenSystemStatus();
        onClose();
      },
    },
    {
      id: "nav-cross-domain",
      title: "Start Cross-Domain Workflow",
      category: "Cross-Domain",
      icon: Sparkles,
      action: () => {
        onNavigateTab("cross-domain" as any);
        onClose();
      },
    },
    {
      id: "cd-approve",
      title: "Approve Next Cross-Domain Step",
      category: "Cross-Domain",
      icon: CheckSquare,
      action: () => {
        onSendMessage("approve current step");
        onClose();
      },
    },
    {
      id: "cd-transitions",
      title: "Show Domain Transitions & Evidence",
      category: "Cross-Domain",
      icon: Activity,
      action: () => {
        onNavigateTab("cross-domain" as any);
        onClose();
      },
    },
    {
      id: "nav-settings",
      title: "Open System Settings",
      category: "Navigation",
      icon: Settings,
      action: () => {
        onNavigateTab("settings");
        onClose();
      },
    },
  ];

  const filtered = options.filter(
    (opt) =>
      opt.title.toLowerCase().includes(query.toLowerCase()) ||
      opt.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-black/80 backdrop-blur-md animate-fade-in select-none">
      <div className="w-full max-w-xl rounded-2xl bg-[#0D0D0D] border border-[#F59E0B]/30 shadow-[0_0_50px_rgba(245,158,11,0.2)] overflow-hidden">
        {/* Input Header */}
        <div className="flex items-center gap-3 p-4 bg-[#141414] border-b border-white/5">
          <Search size={18} className="text-[#F59E0B] shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && filtered[selectedIndex]) {
                filtered[selectedIndex].action();
              } else if (e.key === "ArrowDown") {
                setSelectedIndex((prev) => (prev + 1) % filtered.length);
              } else if (e.key === "ArrowUp") {
                setSelectedIndex(
                  (prev) => (prev - 1 + filtered.length) % filtered.length
                );
              }
            }}
            placeholder="Type a command, ask Saarthi, or jump to view..."
            className="w-full bg-transparent text-white placeholder-white/20 text-sm focus:outline-none font-sans"
          />
          <kbd className="px-2 py-0.5 text-[10px] font-mono bg-white/5 text-white/40 rounded border border-white/10 shrink-0">
            ESC
          </kbd>
        </div>

        {/* Options List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.map((item, idx) => {
            const Icon = item.icon;
            const isSelected = idx === selectedIndex;

            return (
              <div
                key={item.id}
                onClick={item.action}
                onMouseEnter={() => setSelectedIndex(idx)}
                className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all ${
                  isSelected
                    ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40"
                    : "text-white/80 hover:bg-[#141414] border border-transparent"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    size={16}
                    className={isSelected ? "text-[#F59E0B]" : "text-white/40"}
                  />
                  <span className="text-xs font-medium">{item.title}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-[#0D0D0D] border border-white/5 text-white/40">
                    {item.category}
                  </span>
                  {isSelected && <ArrowRight size={14} className="text-[#F59E0B]" />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

