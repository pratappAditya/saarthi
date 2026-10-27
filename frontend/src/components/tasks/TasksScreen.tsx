import React, { useState } from "react";
import {
  CheckSquare,
  Plus,
  Clock,
  AlertCircle,
  FileText,
  CheckCircle2,
  Calendar,
  Sparkles,
  Search,
} from "lucide-react";
import type { TaskItem } from "../../types";

interface TasksScreenProps {
  tasks: TaskItem[];
  onAddTask: (task: Partial<TaskItem>) => void;
  onToggleTaskComplete: (id: string) => void;
}

export const TasksScreen: React.FC<TasksScreenProps> = ({
  tasks,
  onAddTask,
  onToggleTaskComplete,
}) => {
  const [naturalInput, setNaturalInput] = useState("");
  const [activeTab, setActiveTab] = useState<"today" | "upcoming" | "completed">("today");

  const handleNaturalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalInput.trim()) return;

    onAddTask({
      title: naturalInput,
      dueDate: "Today, 18:00",
      priority: "medium",
      status: "today",
      createdBy: "user",
    });

    setNaturalInput("");
  };

  const filteredTasks = tasks.filter((t) => t.status === activeTab);

  const priorityColors: Record<string, string> = {
    high: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    medium: "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30",
    low: "bg-white/5 text-white/40 border-white/5",
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-y-auto select-none space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <CheckSquare size={22} className="text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              AGENT TASK SCHEDULE
            </h2>
          </div>
          <p className="text-xs text-white/50">
            Natural-language task creation synchronized with your local Saarthi companion.
          </p>
        </div>
      </div>

      {/* Natural Language Task Input Bar */}
      <form onSubmit={handleNaturalSubmit} className="relative">
        <div className="relative flex items-center rounded-2xl bg-[#141414] border border-white/10 focus-within:border-[#F59E0B] p-2.5 shadow-lg">
          <Sparkles size={18} className="ml-3 text-[#F59E0B] shrink-0" />
          <input
            type="text"
            value={naturalInput}
            onChange={(e) => setNaturalInput(e.target.value)}
            placeholder='Create a task, e.g. "Remind me to review site plan tomorrow at 5 PM"...'
            className="w-full px-3 py-2 bg-transparent text-white placeholder-white/20 text-xs focus:outline-none font-sans"
          />
          <button
            type="submit"
            disabled={!naturalInput.trim()}
            className="px-4 py-2 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 disabled:opacity-30 text-black font-bold text-xs flex items-center gap-1 transition-all cursor-pointer shadow-[0_0_12px_rgba(245,158,11,0.2)] shrink-0"
          >
            <Plus size={14} /> Add Task
          </button>
        </div>
      </form>

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-white/5 pb-2">
        {(["today", "upcoming", "completed"] as const).map((tab) => {
          const count = tasks.filter((t) => t.status === tab).length;
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === tab
                  ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40"
                  : "bg-[#141414] text-white/40 border border-white/5 hover:text-white"
              }`}
            >
              <span>{tab}</span>
              <span className="px-1.5 py-0.5 rounded-full bg-white/5 text-[10px] font-mono">
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {filteredTasks.map((task) => {
          const isCompleted = task.status === "completed";

          return (
            <div
              key={task.id}
              className={`p-4 rounded-2xl bg-[#141414] border transition-all flex items-start gap-3.5 group ${
                isCompleted
                  ? "border-white/5 opacity-50"
                  : "border-white/5 hover:border-[#F59E0B]/30"
              }`}
            >
              <button
                onClick={() => onToggleTaskComplete(task.id)}
                className={`mt-0.5 w-5 h-5 rounded-lg border flex items-center justify-center transition-all cursor-pointer shrink-0 ${
                  isCompleted
                    ? "bg-emerald-500 border-emerald-400 text-black"
                    : "border-white/20 hover:border-[#F59E0B] text-transparent"
                }`}
              >
                <CheckCircle2 size={14} />
              </button>

              <div className="flex-1 min-w-0 space-y-1.5">
                <div className="flex items-start justify-between gap-2">
                  <h4
                    className={`font-medium text-sm text-white/90 ${
                      isCompleted ? "line-through text-white/40" : ""
                    }`}
                  >
                    {task.title}
                  </h4>

                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase border ${
                      priorityColors[task.priority || 'medium']
                    }`}
                  >
                    {task.priority}
                  </span>
                </div>

                {task.description && (
                  <p className="text-xs text-white/60 leading-normal">
                    {task.description}
                  </p>
                )}

                {/* Task Metadata */}
                <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] font-mono text-white/40">
                  <span className="flex items-center gap-1 text-[#F59E0B]">
                    <Clock size={12} /> {task.dueDate}
                  </span>

                  <span className="px-1.5 py-0.5 rounded bg-[#0D0D0D] text-white/40 text-[10px]">
                    Created by: {task.createdBy}
                  </span>

                  {task.relatedFileNames && task.relatedFileNames.map((fn, i) => (
                    <span
                      key={i}
                      className="flex items-center gap-1 text-purple-300/80 bg-purple-950/30 px-2 py-0.5 rounded border border-purple-500/20"
                    >
                      <FileText size={11} /> {fn}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}

        {filteredTasks.length === 0 && (
          <div className="py-12 text-center text-white/30 text-xs space-y-2 font-mono">
            <CheckSquare size={32} className="mx-auto text-white/20" />
            <p className="font-semibold text-white/50">Your schedule is clear.</p>
            <p>No tasks found in {activeTab}.</p>
          </div>
        )}
      </div>
    </div>
  );
};
