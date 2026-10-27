import React from "react";
import {
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  Search,
  FileText,
  CheckSquare,
  Wrench,
  Brain,
  Cpu,
} from "lucide-react";
import type { ActivityLog } from "../../types";

interface ActivityScreenProps {
  activities: ActivityLog[];
}

export const ActivityScreen: React.FC<ActivityScreenProps> = ({
  activities,
}) => {
  const getActionIcon = (type: ActivityLog["actionType"]) => {
    switch (type) {
      case "search":
        return <Search className="text-[#F59E0B]" size={16} />;
      case "file":
        return <FileText className="text-sky-400" size={16} />;
      case "task":
        return <CheckSquare className="text-emerald-400" size={16} />;
      case "tool":
        return <Wrench className="text-purple-400" size={16} />;
      case "memory":
        return <Brain className="text-rose-400" size={16} />;
      case "permission":
        return <ShieldAlert className="text-[#F59E0B]" size={16} />;
      default:
        return <Cpu className="text-blue-400" size={16} />;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-y-auto select-none space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Activity size={22} className="text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              AGENT ACTIVITY AUDIT TRAIL
            </h2>
          </div>
          <p className="text-xs text-white/50">
            Chronological audit log of every operation executed locally by Saarthi.
          </p>
        </div>
      </div>

      {/* Chronological Timeline */}
      <div className="relative pl-6 border-l border-white/10 space-y-6 my-2">
        {activities.map((act) => (
          <div
            key={act.id}
            className="relative p-4 rounded-2xl bg-[#141414] border border-white/5 space-y-2 hover:border-[#F59E0B]/30 transition-all group"
          >
            {/* Timeline Node Badge */}
            <div className="absolute -left-[35px] top-4 w-7 h-7 rounded-xl bg-[#0D0D0D] border border-[#F59E0B]/40 flex items-center justify-center shadow-[0_0_10px_rgba(245,158,11,0.2)]">
              {getActionIcon(act.actionType)}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
              <span className="text-[#F59E0B] font-semibold flex items-center gap-1.5">
                <Clock size={12} /> {act.timestamp} ({act.timeFormatted})
              </span>

              <div className="flex items-center gap-2">
                {act.toolName && (
                  <span className="px-2 py-0.5 rounded bg-white/5 text-white/60 text-[10px]">
                    {act.toolName}
                  </span>
                )}

                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold flex items-center gap-1 border ${
                    act.status === "completed"
                      ? "bg-emerald-950/40 text-emerald-300 border-emerald-500/30"
                      : "bg-rose-950/40 text-rose-300 border-rose-500/30"
                  }`}
                >
                  {act.status === "completed" ? (
                    <CheckCircle2 size={11} />
                  ) : (
                    <XCircle size={11} />
                  )}
                  {act.status}
                </span>
              </div>
            </div>

            <h4 className="text-sm font-semibold text-white group-hover:text-[#F59E0B] transition-colors">
              {act.title}
            </h4>

            <p className="text-xs text-white/70 leading-relaxed font-sans">
              {act.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

