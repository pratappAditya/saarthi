import React, { useState, useEffect } from 'react';
import { Target, CheckSquare, Plus, Clock, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

export interface Milestone {
  id: string;
  title: string;
  status: string;
}

export interface Goal {
  id: string;
  title: string;
  domain: string;
  progress_percent: number;
  status: string;
  milestones: Milestone[];
  recommended_next_action: string;
}

export const GoalManagerView: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/proactive/goals')
      .then(res => res.json())
      .then(data => {
        if (data.goals) setGoals(data.goals);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handleCreateSampleGoal = async () => {
    try {
      const res = await fetch('/api/proactive/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'Complete Lead Security Architect Application Suite',
          domain: 'career',
          milestones: ['Tailor Master Resume', 'Extract Job Requirements', 'Prepare Technical Interview Questions'],
          recommended_next_action: 'Extract job requirements for target role'
        })
      });
      if (res.ok) {
        const data = await res.json();
        setGoals(prev => [data.goal, ...prev]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6 font-mono text-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-amber-400" />
            JARVIS GOAL & ROUTINE OPERATING MANAGER
          </h1>
          <p className="text-gray-400 text-xs mt-1">Cross-domain goal tracking, milestones, routines, and recommended next actions.</p>
        </div>
        <Button variant="primary" icon={Plus} onClick={handleCreateSampleGoal}>
          + Create Goal
        </Button>
      </div>

      {/* Goals Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-gray-400 py-8 text-center">Loading Goal & Routine State...</div>
        ) : goals.length === 0 ? (
          <div className="p-8 rounded-2xl bg-white/5 border border-white/10 text-center space-y-3">
            <Target className="w-8 h-8 text-gray-500 mx-auto" />
            <p className="text-gray-300">No active goals found. Create your first cross-domain goal to track progress.</p>
          </div>
        ) : (
          goals.map(goal => (
            <div key={goal.id} className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3 shadow-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-sm">{goal.title}</span>
                  <Badge variant="accent" size="xs">{goal.domain.toUpperCase()}</Badge>
                </div>
                <Badge variant="success" size="xs">{goal.status}</Badge>
              </div>

              {/* Milestones */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] text-gray-400">MILESTONES ({goal.milestones.length}):</span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {goal.milestones.map(m => (
                    <div key={m.id} className="p-2 rounded-xl bg-black/40 border border-white/10 flex items-center gap-2 text-gray-300 text-[11px]">
                      <CheckSquare className="w-3.5 h-3.5 text-amber-400" />
                      <span className="truncate">{m.title}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommended Action */}
              {goal.recommended_next_action && (
                <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span>Next Action: {goal.recommended_next_action}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
