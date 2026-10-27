import React, { useState, useEffect } from 'react';
import { 
  Brain, Plus, Search, Trash2, ShieldCheck, Sparkles, Tag, Eye,
  Edit3, RefreshCw, Send, CheckCircle2, AlertTriangle, Layers,
  Compass, HelpCircle, Lock, FolderKanban, Sliders
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';

interface MemoryItemAudit {
  id: number;
  what: string;
  why: string;
  source: string;
  scope: string;
  memory_class: string;
  confidence: number;
  importance: number;
  domain?: string;
  project_id?: string;
  goal_id?: string;
  retention_state?: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  can_edit: boolean;
  can_delete: boolean;
}

export const MemoryView: React.FC = () => {
  const { addToast } = useApp();
  const [memories, setMemories] = useState<MemoryItemAudit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Natural Command State
  const [naturalCommand, setNaturalCommand] = useState('');
  const [commandLoading, setCommandLoading] = useState(false);
  const [commandFeedback, setCommandFeedback] = useState<string | null>(null);

  // Filter State
  const [selectedScope, setSelectedScope] = useState<string>('all');
  const [selectedProvenance, setSelectedProvenance] = useState<string>('all');
  const [selectedProjectId, setSelectedProjectId] = useState<string>('');

  // Add Fact Form State
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newContent, setNewContent] = useState('');
  const [newScope, setNewScope] = useState('global_user');
  const [newClass, setNewClass] = useState('USER_MEMORY');
  const [newImportance, setNewImportance] = useState(7);
  const [newProjectId, setNewProjectId] = useState('');

  // Edit / Correction Modal State
  const [editingMemory, setEditingMemory] = useState<MemoryItemAudit | null>(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    loadMemories();
  }, [selectedScope, selectedProjectId]);

  const loadMemories = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedScope !== 'all') params.append('scope', selectedScope);
      if (selectedProjectId) params.append('project_id', selectedProjectId);

      const res = await fetch(`/api/personalization/what-saarthi-knows?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setMemories(data.items || []);
      } else {
        // Fallback to basic memory listing if endpoint differs
        const fbRes = await fetch('/api/memory');
        if (fbRes.ok) {
          const fbData = await fbRes.json();
          const mapped: MemoryItemAudit[] = (fbData.memories || []).map((m: any) => ({
            id: m.id,
            what: m.content,
            why: m.source === 'user_explicit' ? 'Explicitly provided by user.' : 'Recorded in context.',
            source: m.provenance || m.source || 'USER_EXPLICIT',
            scope: m.scope || 'global_user',
            memory_class: m.memory_class || m.type || 'USER_MEMORY',
            confidence: m.confidence || 1.0,
            importance: m.importance || 5,
            domain: m.domain || 'general',
            project_id: m.project_id,
            created_at: m.created_at || '',
            updated_at: m.updated_at || '',
            can_edit: true,
            can_delete: true
          }));
          setMemories(mapped);
        }
      }
    } catch (err) {
      console.error("Failed to load memories", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalCommand.trim()) return;

    try {
      setCommandLoading(true);
      const res = await fetch('/api/personalization/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: naturalCommand,
          project_id: selectedProjectId || undefined
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.processed && data.result) {
          setCommandFeedback(data.result.response || "Command executed successfully.");
          addToast({ type: 'success', title: 'Memory Updated', message: data.result.response });
          loadMemories();
        } else {
          setCommandFeedback(data.response || "Command could not be recognized as a directive.");
        }
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Command Failed', message: 'Could not process memory command.' });
    } finally {
      setCommandLoading(false);
      setNaturalCommand('');
    }
  };

  const handleCreateFact = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newContent,
          importance: Number(newImportance),
          domain: 'general',
          scope: newScope,
          project_id: newProjectId || undefined,
          provenance: 'USER_EXPLICIT'
        })
      });

      if (res.ok) {
        setNewContent('');
        setNewProjectId('');
        setIsAddOpen(false);
        addToast({ type: 'success', title: 'Memory Saved', message: 'Durable fact persisted with strict provenance.' });
        loadMemories();
      } else {
        const errData = await res.json();
        addToast({ type: 'error', title: 'Save Blocked', message: errData.detail || 'Could not create memory item.' });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Save Failed', message: 'Could not persist memory.' });
    }
  };

  const handleForget = async (id: number) => {
    try {
      const res = await fetch(`/api/memory/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setMemories(memories.filter(m => m.id !== id));
        addToast({ type: 'info', title: 'Memory Forgotten', message: 'Removed item and invalidated caches.' });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Delete Failed', message: 'Could not delete memory.' });
    }
  };

  const handleStartEdit = (m: MemoryItemAudit) => {
    setEditingMemory(m);
    setEditContent(m.what);
  };

  const handleSaveCorrection = async () => {
    if (!editingMemory) return;
    try {
      const res = await fetch('/api/personalization/correct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          memory_id: editingMemory.id,
          new_content: editContent
        })
      });

      if (res.ok) {
        addToast({ type: 'success', title: 'Memory Corrected', message: 'Updated memory with USER_EXPLICIT provenance.' });
        setEditingMemory(null);
        loadMemories();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Correction Failed', message: 'Could not update memory.' });
    }
  };

  const handleClearProjectMemory = async () => {
    if (!selectedProjectId) return;
    if (!window.confirm(`Clear all memories for project '${selectedProjectId}'?`)) return;

    try {
      const res = await fetch(`/api/personalization/project/${selectedProjectId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        const data = await res.json();
        addToast({ type: 'info', title: 'Project Memory Cleared', message: `Purged ${data.deleted_count} memories.` });
        loadMemories();
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Purge Failed', message: 'Could not clear project memory.' });
    }
  };

  const filteredMemories = memories.filter(m => {
    const matchesSearch = !searchQuery || 
      m.what.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.why.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesScope = selectedScope === 'all' || m.scope.toLowerCase() === selectedScope.toLowerCase();
    
    const matchesProv = selectedProvenance === 'all' || 
      m.source.toLowerCase().includes(selectedProvenance.toLowerCase());

    return matchesSearch && matchesScope && matchesProv;
  });

  const explicitCount = memories.filter(m => m.source.toUpperCase().includes('USER_EXPLICIT')).length;
  const inferredCount = memories.filter(m => m.source.toUpperCase().includes('MODEL_INFERENCE')).length;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Brain className="w-3.5 h-3.5 text-purple-400" />
            <span>SAARTHI DEEP MEMORY & PERSONAL INTELLIGENCE 2.0</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            "What Saarthi Knows" — Memory Inspector
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Transparently inspect, verify, correct, or forget durable facts, preferences, and project intelligence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={loadMemories}>
            Refresh
          </Button>
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsAddOpen(!isAddOpen)}>
            + Add Memory
          </Button>
        </div>
      </div>

      {/* Memory Intelligence Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card variant="default" padding="sm" className="space-y-1">
          <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Total Active Memories</span>
          <div className="text-xl font-bold text-white font-mono">{memories.length}</div>
        </Card>
        <Card variant="default" padding="sm" className="space-y-1">
          <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Explicit User Facts</span>
          <div className="text-xl font-bold text-emerald-400 font-mono">{explicitCount}</div>
        </Card>
        <Card variant="default" padding="sm" className="space-y-1">
          <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Learned Inferences</span>
          <div className="text-xl font-bold text-purple-400 font-mono">{inferredCount}</div>
        </Card>
        <Card variant="default" padding="sm" className="space-y-1">
          <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Tenant Isolation</span>
          <div className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 font-semibold mt-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Isolated User / Org</span>
          </div>
        </Card>
      </div>

      {/* Natural Language Memory Directive Bar */}
      <Card variant="default" padding="md" className="space-y-2 border-purple-500/20 bg-purple-950/10">
        <div className="flex items-center justify-between text-xs font-mono text-purple-300">
          <span className="flex items-center gap-1.5 font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            Natural Memory Directives
          </span>
          <span className="text-[10px] text-gray-400">e.g. "Remember that I prefer...", "Forget that", "What do you know..."</span>
        </div>

        <form onSubmit={handleExecuteCommand} className="flex gap-2">
          <input
            type="text"
            value={naturalCommand}
            onChange={(e) => setNaturalCommand(e.target.value)}
            placeholder="Tell Saarthi: 'Remember this project uses PostgreSQL' or 'Forget about my old email'..."
            className="flex-1 px-3 py-2 rounded-lg bg-black/40 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-purple-500"
          />
          <Button variant="primary" size="sm" type="submit" isLoading={commandLoading} icon={Send}>
            Direct
          </Button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {[
            "Remember that I prefer concise reports.",
            "Remember this project uses PostgreSQL.",
            "What do you remember about me?",
            "What do you know about this project?",
            "Forget that."
          ].map((chip) => (
            <button
              key={chip}
              type="button"
              onClick={() => setNaturalCommand(chip)}
              className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>

        {commandFeedback && (
          <div className="text-[11px] font-mono p-2 rounded bg-purple-900/30 border border-purple-500/30 text-purple-200 mt-2">
            <strong>Saarthi:</strong> {commandFeedback}
          </div>
        )}
      </Card>

      {/* Add Memory Modal / Box */}
      {isAddOpen && (
        <Card variant="default" padding="md" className="space-y-3 text-xs font-mono border-emerald-500/30">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-400" />
              Add Explicit Durable Memory
            </h3>
            <span className="text-[10px] text-emerald-400 font-mono">Provenance: USER_EXPLICIT</span>
          </div>

          <form onSubmit={handleCreateFact} className="space-y-3">
            <Input 
              label="Memory Content / Fact / Preference" 
              value={newContent} 
              onChange={(e) => setNewContent(e.target.value)} 
              placeholder="e.g. Prefers clean TypeScript code without any types." 
              required 
            />

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[10px] font-mono text-gray-400 mb-1">Scope</label>
                <select 
                  value={newScope} 
                  onChange={(e) => setNewScope(e.target.value)}
                  className="w-full px-2 py-1.5 rounded bg-black/40 border border-white/10 text-white text-xs font-mono"
                >
                  <option value="global_user">Global User</option>
                  <option value="project">Project</option>
                  <option value="goal">Goal</option>
                  <option value="domain">Domain</option>
                  <option value="workflow">Workflow</option>
                  <option value="task">Task</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-mono text-gray-400 mb-1">Memory Class</label>
                <select 
                  value={newClass} 
                  onChange={(e) => setNewClass(e.target.value)}
                  className="w-full px-2 py-1.5 rounded bg-black/40 border border-white/10 text-white text-xs font-mono"
                >
                  <option value="USER_MEMORY">User Memory</option>
                  <option value="PREFERENCE_MEMORY">Preference Memory</option>
                  <option value="PROJECT_MEMORY">Project Memory</option>
                  <option value="GOAL_MEMORY">Goal Memory</option>
                  <option value="DOMAIN_EXPERTISE">Domain Expertise</option>
                  <option value="VOICE_MEMORY">Voice Memory</option>
                </select>
              </div>

              <Input 
                label="Importance (1-10)" 
                type="number" 
                min="1" 
                max="10" 
                value={newImportance} 
                onChange={(e) => setNewImportance(Number(e.target.value))} 
              />
            </div>

            {newScope === 'project' && (
              <Input 
                label="Target Project ID" 
                value={newProjectId} 
                onChange={(e) => setNewProjectId(e.target.value)} 
                placeholder="e.g. saarthi-core or webapp" 
                required 
              />
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsAddOpen(false)}>Cancel</Button>
              <Button variant="primary" size="sm" type="submit">Persist Memory</Button>
            </div>
          </form>
        </Card>
      )}

      {/* Scope Filter Tabs & Search Bar */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          {/* Scope Pills */}
          <div className="flex flex-wrap gap-1.5">
            {[
              { id: 'all', label: 'All Scopes' },
              { id: 'global_user', label: 'Global User' },
              { id: 'project', label: 'Project' },
              { id: 'goal', label: 'Goal' },
              { id: 'domain', label: 'Domain' },
              { id: 'workflow', label: 'Workflow' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedScope(tab.id)}
                className={`text-xs font-mono px-3 py-1 rounded-lg border transition-all ${
                  selectedScope === tab.id
                    ? 'bg-purple-600/30 border-purple-500 text-white font-semibold'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Project Specific Purge Button */}
          {selectedScope === 'project' && (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={selectedProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                placeholder="Project ID..."
                className="px-2 py-1 rounded bg-black/40 border border-white/10 text-xs font-mono text-white w-32"
              />
              {selectedProjectId && (
                <Button variant="outline" size="xs" onClick={handleClearProjectMemory} className="text-rose-400 border-rose-500/30">
                  Purge Project
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Search Bar & Provenance Filter */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search what Saarthi knows, why it was remembered, or by scope..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-purple-500"
            />
          </div>

          <select
            value={selectedProvenance}
            onChange={(e) => setSelectedProvenance(e.target.value)}
            className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none"
          >
            <option value="all">All Provenances</option>
            <option value="USER_EXPLICIT">User Explicit</option>
            <option value="SOURCE_DERIVED">Source Derived</option>
            <option value="OBSERVED">Observed</option>
            <option value="MODEL_INFERENCE">Model Inference</option>
          </select>
        </div>
      </div>

      {/* Memory Audit Table / Cards */}
      {loading ? (
        <div className="p-12 text-center text-xs text-gray-400 font-mono">Loading Saarthi Knowledge Store...</div>
      ) : filteredMemories.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[var(--border-subtle)] rounded-xl space-y-2 text-xs text-gray-400 font-mono">
          <Brain className="w-8 h-8 mx-auto text-purple-400 opacity-60" />
          <p className="font-bold text-white text-sm">No Memories Found Matching Query</p>
          <p className="max-w-md mx-auto">Use the natural command bar or click "+ Add Memory" above to store transparent preferences or project facts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredMemories.map((m) => (
            <Card key={m.id} variant="default" padding="md" className="space-y-3 text-xs flex flex-col justify-between border-white/10 hover:border-purple-500/40 transition-colors">
              <div className="space-y-2.5">
                {/* Badges Bar */}
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-1.5">
                    <Badge variant="outline" size="xs">{m.scope.toUpperCase()}</Badge>
                    <Badge variant={m.source.toUpperCase().includes('USER_EXPLICIT') ? 'accent' : 'warning'} size="xs">
                      {m.source}
                    </Badge>
                  </div>
                  <span className="text-[10px] font-mono text-gray-400">
                    Confidence: <strong className="text-purple-300">{Math.round(m.confidence * 100)}%</strong>
                  </span>
                </div>

                {/* What Saarthi Knows */}
                <div>
                  <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider block mb-0.5">What Saarthi Knows</span>
                  <p className="text-gray-100 font-mono text-xs leading-relaxed bg-black/20 p-2 rounded border border-white/5">
                    {m.what}
                  </p>
                </div>

                {/* Why Saarthi Knows It */}
                <div>
                  <span className="text-[10px] font-mono text-gray-400 uppercase tracking-wider block mb-0.5">Why Saarthi Knows It</span>
                  <p className="text-gray-400 font-mono text-[11px] leading-relaxed">
                    {m.why}
                  </p>
                </div>
              </div>

              {/* Card Footer: Metadata & Controls */}
              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[10px] font-mono text-gray-400">
                <div className="space-x-2">
                  <span>Class: <strong className="text-gray-300">{m.memory_class}</strong></span>
                  {m.project_id && (
                    <span>Project: <strong className="text-cyan-400">{m.project_id}</strong></span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => handleStartEdit(m)} 
                    className="p-1 hover:text-purple-300 text-gray-400 transition-colors"
                    title="Correct this memory"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button 
                    onClick={() => handleForget(m.id)} 
                    className="p-1 hover:text-rose-400 text-gray-400 transition-colors"
                    title="Forget memory"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Edit / Correction Modal */}
      {editingMemory && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <Card variant="default" padding="lg" className="max-w-md w-full space-y-4 border-purple-500/40 bg-gray-950 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-purple-400" />
                Correct Remembered Information
              </h3>
              <Badge variant="accent" size="xs">Elevates to USER_EXPLICIT</Badge>
            </div>

            <div className="space-y-2">
              <label className="block text-[10px] text-gray-400 uppercase">Current Stored Fact</label>
              <div className="p-2 rounded bg-black/40 border border-white/10 text-gray-300 text-xs">
                {editingMemory.what}
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-[10px] text-purple-300 uppercase">Replacement / Corrected Fact</label>
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={3}
                className="w-full p-2.5 rounded bg-black/60 border border-purple-500/40 text-white text-xs font-mono focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-white/10">
              <Button variant="outline" size="sm" onClick={() => setEditingMemory(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleSaveCorrection}>
                Save Correction
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
