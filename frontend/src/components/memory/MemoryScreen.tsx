import React, { useState } from "react";
import {
  Brain,
  Plus,
  Search,
  Pin,
  Trash2,
  Clock,
  Sparkles,
} from "lucide-react";
import type { MemoryCategory, MemoryItem } from "../../types";

interface MemoryScreenProps {
  memories: MemoryItem[];
  onAddMemory: (memory: Partial<MemoryItem>) => void;
  onUpdateMemory: (id: string, updates: Partial<MemoryItem>) => void;
  onDeleteMemory: (id: string) => void;
}

export const MemoryScreen: React.FC<MemoryScreenProps> = ({
  memories,
  onAddMemory,
  onUpdateMemory,
  onDeleteMemory,
}) => {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newCategory, setNewCategory] = useState<MemoryCategory>("preference");
  const [newTags, setNewTags] = useState("");

  const categories: { id: string; label: string }[] = [
    { id: "all", label: "All Memory" },
    { id: "preference", label: "Preferences" },
    { id: "project", label: "Projects" },
    { id: "people", label: "People" },
    { id: "fact", label: "Facts" },
    { id: "long_term", label: "Long-term" },
  ];

  const filtered = memories.filter((m) => {
    const matchesCat =
      selectedCategory === "all" || m.category === selectedCategory;
    const titleText = m.title || m.key || '';
    const matchesSearch =
      titleText.toLowerCase().includes(search.toLowerCase()) ||
      m.content.toLowerCase().includes(search.toLowerCase()) ||
      (m.tags || []).some((t) => t.toLowerCase().includes(search.toLowerCase()));
    return matchesCat && matchesSearch;
  });

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    onAddMemory({
      title: newTitle,
      content: newContent,
      category: newCategory,
      tags: newTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
      pinned: false,
    });

    setNewTitle("");
    setNewContent("");
    setNewTags("");
    setShowAddModal(false);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-y-auto select-none space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Brain size={22} className="text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              LOCAL MEMORY CORE
            </h2>
            <span className="px-2.5 py-0.5 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[10px] font-mono font-semibold text-[#F59E0B]">
              AIR-GAPPED STORAGE
            </span>
          </div>
          <p className="text-xs text-white/50">
            Stored completely on this computer inside <code className="text-[#F59E0B]">E:\Saarthi</code>.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
        >
          <Plus size={16} />
          <span>Remember Something</span>
        </button>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search memory titles, facts, projects, or tags..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-[#141414] border border-white/10 text-white placeholder-white/20 text-xs focus:outline-none focus:border-[#F59E0B]/80 font-sans"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                selectedCategory === cat.id
                  ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40"
                  : "bg-[#141414] text-white/50 border border-white/5 hover:text-white"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Memory Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((mem) => (
          <div
            key={mem.id}
            className={`p-5 rounded-2xl bg-[#141414] border ${
              mem.pinned
                ? "border-[#F59E0B]/40 shadow-[0_0_15px_rgba(245,158,11,0.1)]"
                : "border-white/5"
            } flex flex-col justify-between gap-3 hover:border-[#F59E0B]/30 transition-all group`}
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold text-sm text-white group-hover:text-[#F59E0B] transition-colors">
                  {mem.title || mem.key || 'Untitled Memory'}
                </span>
                <button
                  onClick={() =>
                    onUpdateMemory(String(mem.id), { pinned: !mem.pinned })
                  }
                  className={`p-1 rounded transition-colors cursor-pointer ${
                    mem.pinned
                      ? "text-[#F59E0B]"
                      : "text-white/30 hover:text-white/60"
                  }`}
                  title={mem.pinned ? "Unpin memory" : "Pin memory"}
                >
                  <Pin size={14} className={mem.pinned ? "fill-[#F59E0B]" : ""} />
                </button>
              </div>

              <p className="text-xs text-white/70 leading-relaxed font-sans">
                {mem.content}
              </p>
            </div>

            <div className="pt-3 border-t border-white/5 space-y-2 text-[11px]">
              {/* Tags */}
              <div className="flex flex-wrap items-center gap-1">
                <span className="px-2 py-0.5 rounded bg-white/5 text-[#F59E0B] font-mono text-[10px] uppercase font-medium">
                  {mem.category}
                </span>
                {(mem.tags || []).map((t, i) => (
                  <span
                    key={i}
                    className="px-1.5 py-0.5 rounded bg-[#0D0D0D] text-white/40 text-[10px] font-mono border border-white/5"
                  >
                    #{t}
                  </span>
                ))}
              </div>

              {/* Footer Controls */}
              <div className="flex items-center justify-between text-white/30 font-mono text-[10px] pt-1">
                <span className="flex items-center gap-1">
                  <Clock size={11} /> Updated {mem.updatedAt}
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => onDeleteMemory(String(mem.id))}
                    className="p-1 rounded text-white/30 hover:text-rose-400 transition-colors cursor-pointer"
                    title="Forget memory"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="py-12 text-center text-white/30 text-xs space-y-2 font-mono">
          <Brain size={32} className="mx-auto text-white/20" />
          <p>No local memory cards match this filter.</p>
        </div>
      )}

      {/* Add Memory Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-lg p-6 rounded-2xl bg-[#0D0D0D] border border-white/10 space-y-4 shadow-2xl">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Sparkles size={16} className="text-[#F59E0B]" /> Save Fact To Local Memory
            </h3>

            <form onSubmit={handleAddSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-white/50 mb-1">Memory Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. User Preferred Framework: React 19"
                  className="w-full px-3 py-2 rounded-xl bg-[#141414] border border-white/10 text-white focus:outline-none focus:border-[#F59E0B]"
                />
              </div>

              <div>
                <label className="block text-white/50 mb-1">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value as MemoryCategory)}
                  className="w-full px-3 py-2 rounded-xl bg-[#141414] border border-white/10 text-white focus:outline-none focus:border-[#F59E0B]"
                >
                  <option value="preference">Preference</option>
                  <option value="project">Project</option>
                  <option value="people">People</option>
                  <option value="fact">Fact</option>
                  <option value="long_term">Long-term</option>
                </select>
              </div>

              <div>
                <label className="block text-white/50 mb-1">Content / Details</label>
                <textarea
                  rows={3}
                  required
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  placeholder="Details Saarthi should permanently remember during conversations..."
                  className="w-full px-3 py-2 rounded-xl bg-[#141414] border border-white/10 text-white focus:outline-none focus:border-[#F59E0B] resize-none"
                />
              </div>

              <div>
                <label className="block text-white/50 mb-1">Tags (comma separated)</label>
                <input
                  type="text"
                  value={newTags}
                  onChange={(e) => setNewTags(e.target.value)}
                  placeholder="e.g. react, tailwind, coding"
                  className="w-full px-3 py-2 rounded-xl bg-[#141414] border border-white/10 text-white focus:outline-none focus:border-[#F59E0B]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold cursor-pointer shadow-[0_0_12px_rgba(245,158,11,0.3)]"
                >
                  Save Fact
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

