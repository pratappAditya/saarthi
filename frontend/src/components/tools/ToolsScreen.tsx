import React from "react";
import {
  Wrench,
  Search,
  FileText,
  Terminal,
  CheckSquare,
  Brain,
} from "lucide-react";

export const ToolsScreen: React.FC = () => {
  const toolsCatalog = [
    {
      id: "tool-1",
      name: "File Search & Indexer",
      icon: Search,
      description: "Scans and semantic-indexes local text, PDF, Markdown, and source code files.",
      permission: "Always Allowed",
      risk: "Low",
      path: "E:\\Saarthi\\*",
      status: "Active",
    },
    {
      id: "tool-2",
      name: "PDF & Document Reader",
      icon: FileText,
      description: "Extracts textual content, drawings summaries, and tables from PDFs.",
      permission: "Always Allowed",
      risk: "Low",
      path: "E:\\Saarthi\\*",
      status: "Active",
    },
    {
      id: "tool-3",
      name: "Task Scheduler",
      icon: CheckSquare,
      description: "Creates, updates, and monitors local agent schedule items.",
      permission: "Always Allowed",
      risk: "Low",
      path: "Local Database",
      status: "Active",
    },
    {
      id: "tool-4",
      name: "System Shell Executor",
      icon: Terminal,
      description: "Executes PowerShell / Bash terminal commands on local computer.",
      permission: "Approval Required Per Run",
      risk: "High",
      path: "System Terminal",
      status: "Guarded",
    },
    {
      id: "tool-5",
      name: "Local Memory Core",
      icon: Brain,
      description: "Saves and queries long-term context, project rules, and contact info.",
      permission: "Always Allowed",
      risk: "Low",
      path: "E:\\Saarthi\\memory.db",
      status: "Active",
    },
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-y-auto select-none space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Wrench size={22} className="text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              AGENT TOOL CATALOG & PERMISSIONS
            </h2>
          </div>
          <p className="text-xs text-white/50">
            Registered local agent capabilities and granular security policy.
          </p>
        </div>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {toolsCatalog.map((tool) => {
          const Icon = tool.icon;
          const isHighRisk = tool.risk === "High";

          return (
            <div
              key={tool.id}
              className="p-5 rounded-2xl bg-[#141414] border border-white/5 hover:border-[#F59E0B]/30 transition-all flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-[#0D0D0D] border border-white/10 text-[#F59E0B]">
                      <Icon size={18} />
                    </div>
                    <span className="font-semibold text-sm text-white group-hover:text-[#F59E0B] transition-colors">
                      {tool.name}
                    </span>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
                      isHighRisk
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                        : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                    }`}
                  >
                    Risk: {tool.risk}
                  </span>
                </div>

                <p className="text-xs text-white/70 leading-relaxed font-sans">
                  {tool.description}
                </p>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono">
                <div className="text-white/40">
                  Target: <span className="text-white/70">{tool.path}</span>
                </div>

                <div
                  className={`px-2.5 py-1 rounded-lg border font-semibold ${
                    isHighRisk
                      ? "bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30"
                      : "bg-white/5 text-white/60 border-white/5"
                  }`}
                >
                  {tool.permission}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

