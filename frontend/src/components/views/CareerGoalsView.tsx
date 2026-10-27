import React, { useState, useEffect } from 'react';
import { 
  Target, Plus, CheckCircle2, Clock, AlertTriangle, Trash2, Edit3, Sparkles 
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { Input, Textarea } from '../common/Input';
import { api } from '../../api';

export const CareerGoalsView: React.FC = () => {
  const { addToast } = useApp();
  const [goals, setGoals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('SKILLS');
  const [priority, setPriority] = useState('MEDIUM');
  const [targetDate, setTargetDate] = useState('2026-12-31');
  const [progress, setProgress] = useState(25);

  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      setLoading(true);
      const res = await api.listCareerGoals();
      setGoals(res.goals || []);
    } catch (err) {
      console.error("Failed to load goals", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.createCareerGoal({
        title,
        description,
        category,
        priority,
        target_date: targetDate,
        progress: Number(progress),
        status: 'IN_PROGRESS'
      });
      setGoals([res.goal, ...goals]);
      setIsModalOpen(false);
      setTitle('');
      setDescription('');
      addToast({ type: 'success', title: 'Goal Created', message: `Saved goal '${title}' to SQLite DB.` });
    } catch (err) {
      addToast({ type: 'error', title: 'Creation Failed', message: 'Could not create career goal.' });
    }
  };

  const handleDeleteGoal = async (id: number) => {
    try {
      await api.deleteCareerGoal(id);
      setGoals(goals.filter(g => g.id !== id));
      addToast({ type: 'info', title: 'Goal Deleted', message: 'Removed goal from database.' });
    } catch (err) {
      addToast({ type: 'error', title: 'Delete Failed', message: 'Could not delete goal.' });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'COMPLETED': return <Badge variant="success" size="sm">Completed</Badge>;
      case 'BLOCKED': return <Badge variant="danger" size="sm">Blocked</Badge>;
      default: return <Badge variant="accent" size="sm">In Progress</Badge>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Target className="w-3.5 h-3.5 text-blue-400" />
            <span>CAREER GOALS & MILESTONES WORKSPACE</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Career Goals & Progress Tracker
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Track persistent target roles, skill acquisitions, certifications, and target compensation goals.
          </p>
        </div>

        <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsModalOpen(!isModalOpen)}>
          + Add Career Goal
        </Button>
      </div>

      {/* Goal Creation Form */}
      {isModalOpen && (
        <Card variant="default" padding="md" className="space-y-3 text-xs">
          <h3 className="font-bold text-white font-display-title">New Career Goal</h3>
          <form onSubmit={handleCreateGoal} className="space-y-3">
            <Input label="Goal Title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Master Rust for Security Engineering" required />
            <Textarea label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Action items & milestones..." rows={2} />
            <div className="grid grid-cols-3 gap-2">
              <Input label="Category" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="SKILLS / ROLE / CERT" />
              <Input label="Priority" value={priority} onChange={(e) => setPriority(e.target.value)} placeholder="HIGH / MEDIUM / LOW" />
              <Input label="Target Date" type="date" value={targetDate} onChange={(e) => setTargetDate(e.target.value)} />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button variant="primary" size="sm" type="submit">Save Goal</Button>
            </div>
          </form>
        </Card>
      )}

      {/* Goals Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-gray-400">Loading Career Goals...</div>
      ) : goals.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-[var(--border-subtle)] rounded-xl space-y-2 text-xs text-gray-400">
          <Target className="w-8 h-8 mx-auto text-blue-400 opacity-60" />
          <p className="font-bold text-white">No Career Goals Tracked Yet</p>
          <p className="max-w-xs mx-auto">Click "+ Add Career Goal" above to create target roles, skills to learn, or certification milestones.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {goals.map((g) => (
            <Card key={g.id} variant="default" padding="md" className="space-y-3 text-xs flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" size="xs">{g.category}</Badge>
                  {getStatusBadge(g.status)}
                </div>
                <h3 className="font-bold text-white text-sm">{g.title}</h3>
                <p className="text-gray-400 font-mono text-[11px] leading-relaxed">{g.description || 'No detailed notes.'}</p>
              </div>

              <div className="space-y-2 pt-2 border-t border-white/10">
                <Progress value={g.progress || 0} max={100} variant="accent" showPercentage size="sm" />
                <div className="flex items-center justify-between text-[10px] text-gray-400 font-mono">
                  <span>Target: {g.target_date || 'No Date'}</span>
                  <button onClick={() => handleDeleteGoal(g.id)} className="text-rose-400 hover:text-rose-300 transition-all cursor-pointer">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
