import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, Briefcase, Sparkles, Target, CheckCircle2, Clock, 
  TrendingUp, FileText, AlertCircle, ArrowRight, ShieldCheck 
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { api } from '../../api';

export const CareerDashboardView: React.FC = () => {
  const { setActiveSection, activeResume } = useApp();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const res = await api.getCareerDashboard();
      setData(res);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-gray-400">
        <Sparkles className="w-6 h-6 mx-auto mb-2 animate-spin text-blue-400" />
        <p>Loading Career Operating Dashboard...</p>
      </div>
    );
  }

  const stats = data?.stats || {};
  const pipeline = data?.pipeline || {};
  const readiness = data?.readiness || {};
  const attention = data?.needs_attention || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <LayoutDashboard className="w-3.5 h-3.5 text-blue-400" />
            <span>SAARTHI CAREER OPERATING SYSTEM</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Career Command Center
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Real-time pipeline metrics, upcoming deadlines, career readiness, and Master Resume health.
          </p>
        </div>

        <Badge variant="accent" size="md">
          Master Resume: {activeResume?.title || 'Active'}
        </Badge>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="default" padding="md" className="space-y-1">
          <span className="text-[10px] uppercase font-mono font-bold text-gray-400">Total Applications</span>
          <p className="text-2xl font-bold text-white">{stats.total_applications || 0}</p>
          <span className="text-[10px] text-emerald-400 font-mono">Response Rate: {stats.response_rate || '0%'}</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-1">
          <span className="text-[10px] uppercase font-mono font-bold text-gray-400">Active Interviews</span>
          <p className="text-2xl font-bold text-amber-400">{stats.interviews || 0}</p>
          <span className="text-[10px] text-gray-400 font-mono">Scheduled & Screening</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-1">
          <span className="text-[10px] uppercase font-mono font-bold text-gray-400">Job Offers</span>
          <p className="text-2xl font-bold text-emerald-400">{stats.offers || 0}</p>
          <span className="text-[10px] text-emerald-400 font-mono">Ready for Negotiation</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-1">
          <span className="text-[10px] uppercase font-mono font-bold text-gray-400">Upcoming Action Items</span>
          <p className="text-2xl font-bold text-blue-400">{stats.upcoming_followups || 0}</p>
          <span className="text-[10px] text-blue-400 font-mono">Follow-ups & Deadlines</span>
        </Card>
      </div>

      {/* Pipeline & Career Readiness */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 Cols): Application Pipeline Breakdown */}
        <div className="lg:col-span-7 space-y-4">
          <Card variant="default" padding="md" className="space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white font-display-title">Application Pipeline Breakdown</h3>
              <Button variant="outline" size="sm" onClick={() => setActiveSection('applications')}>
                View Applications
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-2">
              <div className="p-3 rounded bg-white/5 border border-white/10 text-center space-y-1">
                <span className="text-[10px] uppercase font-mono text-gray-400">Saved</span>
                <p className="text-lg font-bold text-white">{pipeline.SAVED || 0}</p>
              </div>
              <div className="p-3 rounded bg-white/5 border border-white/10 text-center space-y-1">
                <span className="text-[10px] uppercase font-mono text-gray-400">Applied</span>
                <p className="text-lg font-bold text-blue-400">{pipeline.APPLIED || 0}</p>
              </div>
              <div className="p-3 rounded bg-white/5 border border-white/10 text-center space-y-1">
                <span className="text-[10px] uppercase font-mono text-gray-400">Interviews</span>
                <p className="text-lg font-bold text-amber-400">{pipeline.INTERVIEW || 0}</p>
              </div>
            </div>
          </Card>

          {/* Needs Attention / Upcoming Deadlines */}
          <Card variant="subtle" padding="md" className="space-y-3 text-xs">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Needs Attention & Upcoming Deadlines</span>
            </h3>

            {attention.length === 0 ? (
              <p className="text-gray-400 font-mono text-[11px]">No immediate follow-up deadlines scheduled.</p>
            ) : (
              <div className="space-y-2">
                {attention.map((item: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded bg-white/5 border border-white/10 flex items-center justify-between font-mono text-[11px]">
                    <span className="text-gray-200">{item.title}</span>
                    <span className="text-amber-400">{item.date}</span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Column (5 Cols): Career Readiness */}
        <div className="lg:col-span-5 space-y-4">
          <Card variant="default" padding="md" className="space-y-3 text-xs">
            <h3 className="font-bold text-white font-display-title">Career Readiness Scores</h3>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-gray-300">Resume Readiness</span>
                  <span className="text-emerald-400 font-mono font-bold">{readiness.resume_readiness}%</span>
                </div>
                <Progress value={readiness.resume_readiness} max={100} variant="accent" showPercentage={false} size="sm" />
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-gray-300">ATS Alignment Score</span>
                  <span className="text-blue-400 font-mono font-bold">{readiness.ats_readiness}%</span>
                </div>
                <Progress value={readiness.ats_readiness} max={100} variant="accent" showPercentage={false} size="sm" />
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-gray-300">Interview Drills Preparedness</span>
                  <span className="text-amber-400 font-mono font-bold">{readiness.interview_readiness}%</span>
                </div>
                <Progress value={readiness.interview_readiness} max={100} variant="accent" showPercentage={false} size="sm" />
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
