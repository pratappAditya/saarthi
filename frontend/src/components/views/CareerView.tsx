import React, { useState } from 'react';
import { 
  Compass, 
  Target, 
  TrendingUp, 
  Award, 
  Building2, 
  DollarSign, 
  CheckCircle2, 
  Sparkles, 
  Bot,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { Input } from '../common/Input';

export const CareerView: React.FC = () => {
  const { careerGoal, setCareerGoal, setIsAssistantOpen, addToast } = useApp();
  const [isEditing, setIsEditing] = useState(false);

  const targetCompanies = [
    { name: 'Stripe', role: 'Staff Frontend Engineer', stage: 'Interview', match: '96%' },
    { name: 'Linear', role: 'Senior Product Engineer', stage: 'Screening', match: '92%' },
    { name: 'Anthropic', role: 'Frontend Systems Architect', stage: 'Applied', match: '94%' },
    { name: 'Vercel', role: 'Principal Design Technologist', stage: 'Offer Extended', match: '97%' },
    { name: 'Figma', role: 'Senior Staff Engineer (WASM)', stage: 'Saved', match: '88%' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Compass className="w-3.5 h-3.5 text-blue-400" />
            <span>CAREER ARCHITECTURE & STRATEGY</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Career Workspace
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Define target milestones, salary brackets, and skill competencies calibrated with local AI insights.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={isEditing ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => {
              if (isEditing) {
                addToast({ type: 'success', title: 'Career Goals Saved' });
              }
              setIsEditing(!isEditing);
            }}
          >
            {isEditing ? 'Save Objectives' : 'Edit Strategy'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={Bot}
            onClick={() => setIsAssistantOpen(true)}
          >
            Review Strategy with AI
          </Button>
        </div>
      </div>

      {/* Target Objectives Hero Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="default" padding="lg" className="space-y-2">
          <span className="text-[10px] font-mono uppercase text-[var(--text-muted)] tracking-wider">
            Primary Target Role
          </span>
          <div className="text-lg font-bold text-[var(--text-primary)] font-display-title">
            {careerGoal.targetTitle}
          </div>
          <div className="text-xs text-blue-400 font-mono">
            {careerGoal.targetLevel}
          </div>
          <p className="text-[11px] text-[var(--text-secondary)] pt-1">
            Focusing on distributed systems, edge rendering, and design token infrastructure.
          </p>
        </Card>

        <Card variant="default" padding="lg" className="space-y-2">
          <span className="text-[10px] font-mono uppercase text-[var(--text-muted)] tracking-wider">
            Target Total Compensation
          </span>
          <div className="text-lg font-bold text-emerald-400 font-display-title">
            {careerGoal.targetCompRange}
          </div>
          <div className="text-xs text-[var(--text-muted)] font-mono">
            Base + High-Growth Equity
          </div>
          <p className="text-[11px] text-[var(--text-secondary)] pt-1">
            Market benchmark: 90th percentile for Staff level in tier-1 tech.
          </p>
        </Card>

        <Card variant="default" padding="lg" className="space-y-2">
          <span className="text-[10px] font-mono uppercase text-[var(--text-muted)] tracking-wider">
            Milestone Target Date
          </span>
          <div className="text-lg font-bold text-[var(--text-primary)] font-display-title">
            {careerGoal.timelineGoal}
          </div>
          <div className="text-xs text-amber-400 font-mono">
            42 Days Remaining in Cycle
          </div>
          <p className="text-[11px] text-[var(--text-secondary)] pt-1">
            1 active offer pending review • 1 panel in progress.
          </p>
        </Card>
      </div>

      {/* Skills Matrix & Market Readiness Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card variant="default" padding="lg" className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
                Core Skill Readiness Matrix
              </h3>
              <p className="text-xs text-[var(--text-secondary)]">
                Evaluated against 40+ Staff Frontend Job Specifications by local Nemotron
              </p>
            </div>
            <Badge variant="accent" size="xs">
              93% Market Fit
            </Badge>
          </div>

          <div className="space-y-3.5">
            {careerGoal.coreSkills.map((skill, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[var(--text-primary)]">{skill.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-mono text-[var(--text-muted)]">
                      Demand: <strong className="text-blue-400">{skill.demand}</strong>
                    </span>
                    <span className="font-mono text-emerald-400 font-bold">{skill.proficiency}%</span>
                  </div>
                </div>
                <Progress value={skill.proficiency} size="xs" variant="accent" showPercentage={false} />
              </div>
            ))}
          </div>
        </Card>

        {/* Target Watchlist */}
        <Card variant="default" padding="lg" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
              Target Watchlist
            </h3>
            <span className="text-[10px] font-mono text-[var(--text-muted)]">
              5 Companies
            </span>
          </div>

          <div className="space-y-2">
            {targetCompanies.map((c, i) => (
              <div
                key={i}
                className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-semibold text-[var(--text-primary)] flex items-center gap-1.5">
                    <span>{c.name}</span>
                    <span className="text-[10px] font-mono text-emerald-400">({c.match})</span>
                  </div>
                  <div className="text-[11px] text-[var(--text-muted)] truncate max-w-[150px]">
                    {c.role}
                  </div>
                </div>
                <Badge variant={c.stage === 'Offer Extended' ? 'success' : c.stage === 'Interview' ? 'warning' : 'default'} size="xs">
                  {c.stage}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
