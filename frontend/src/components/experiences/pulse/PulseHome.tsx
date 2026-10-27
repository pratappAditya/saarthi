import React, { useState } from 'react';
import { 
  Flame, 
  Zap, 
  Target, 
  CheckCircle2, 
  ArrowRight, 
  Play, 
  TrendingUp, 
  Clock, 
  Sparkles,
  Trophy,
  Rocket
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';

export const PulseHome: React.FC = () => {
  const { setActiveSection, applications, addToast } = useApp();
  const [missions, setMissions] = useState([
    { id: '1', title: 'Apply to Stripe & Vercel Staff roles', points: '+50 XP', done: true, target: 'applications' },
    { id: '2', title: 'Tailor AI Systems resume for Linear', points: '+35 XP', done: false, target: 'tailor' },
    { id: '3', title: 'Complete STAR Drill for System Architecture', points: '+40 XP', done: false, target: 'interviews' },
    { id: '4', title: 'Follow up with recruiter David Kim', points: '+20 XP', done: false, target: 'applications' },
  ]);

  const toggleMission = (id: string) => {
    setMissions(prev => prev.map(m => m.id === id ? { ...m, done: !m.done } : m));
    addToast({ type: 'success', title: 'Mission Progress Updated', message: 'Momentum multiplier +1.2x active.' });
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. HERO MOMENTUM RADAR */}
      <section className="p-6 sm:p-8 rounded-2xl bg-gradient-to-br from-[#13192c] via-[#101524] to-[#0d101a] border border-[#232c45] shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-bold">
              <Flame className="w-4 h-4 fill-amber-400" />
              <span>5-DAY CAREER SPRINT ACTIVE</span>
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              High Pipeline Velocity: <span className="text-indigo-400">88% Momentum</span>
            </h1>

            <p className="text-xs sm:text-sm text-[#94a3b8] max-w-xl leading-relaxed">
              You are outpacing 92% of active engineering applicants this month. Complete today's 3 remaining missions to maintain interview conversion velocity.
            </p>
          </div>

          {/* Quick Launch CTA */}
          <div className="flex items-center gap-3">
            <Button
              variant="ai"
              size="lg"
              icon={Rocket}
              onClick={() => setActiveSection('tailor')}
              className="shadow-lg shadow-indigo-600/30"
            >
              Boost Next Application
            </Button>
          </div>
        </div>

        {/* 3 Momentum Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 mt-6 border-t border-[#1f273d]">
          <div className="p-4 rounded-xl bg-[#161c2e] border border-[#26314d] flex items-center gap-3">
            <div className="p-3 rounded-xl bg-amber-500/20 text-amber-400">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white">7 Applied</div>
              <div className="text-xs text-[#94a3b8]">This sprint week</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#161c2e] border border-[#26314d] flex items-center gap-3">
            <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400">
              <Target className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-indigo-400">3 Interviews</div>
              <div className="text-xs text-[#94a3b8]">Live panels active</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[#161c2e] border border-[#26314d] flex items-center gap-3">
            <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-emerald-400">94% ATS</div>
              <div className="text-xs text-[#94a3b8]">Master resume health</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. TODAY'S MISSIONS & ACTION LAUNCHER */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left (7 cols): Today's Active Missions */}
        <div className="lg:col-span-7 bg-[#101524] border border-[#1c2438] rounded-2xl p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-400" />
              <h2 className="text-base font-bold text-white">Today's Action Missions</h2>
            </div>
            <span className="text-xs font-mono text-indigo-400 font-bold">1/4 COMPLETED</span>
          </div>

          <div className="space-y-2.5">
            {missions.map((m) => (
              <div
                key={m.id}
                className={`p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                  m.done 
                    ? 'bg-[#131a2c] border-emerald-500/30 opacity-75' 
                    : 'bg-[#151c30] border-[#242e47] hover:border-indigo-500/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleMission(m.id)}
                    className={`w-5 h-5 rounded-md flex items-center justify-center cursor-pointer ${
                      m.done ? 'bg-emerald-500 text-white' : 'border border-[#384568]'
                    }`}
                  >
                    {m.done && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </button>
                  <span className={`text-xs font-semibold ${m.done ? 'line-through text-[#64748b]' : 'text-white'}`}>
                    {m.title}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold text-amber-400">{m.points}</span>
                  <button
                    onClick={() => setActiveSection(m.target as any)}
                    className="p-1.5 rounded-lg bg-indigo-600/30 text-indigo-300 hover:bg-indigo-600 hover:text-white transition-colors cursor-pointer text-xs"
                    title="Launch action"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right (5 cols): Dynamic Pipeline Velocity */}
        <div className="lg:col-span-5 bg-[#101524] border border-[#1c2438] rounded-2xl p-6 space-y-4 shadow-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">Pipeline Velocity</h2>
            </div>
            <Button variant="ghost" size="xs" onClick={() => setActiveSection('applications')}>
              View All
            </Button>
          </div>

          <div className="space-y-3">
            {applications.slice(0, 3).map((app) => (
              <div 
                key={app.id}
                onClick={() => setActiveSection('applications')}
                className="p-3 rounded-xl bg-[#151c30] border border-[#242e47] hover:border-indigo-500/50 transition-all cursor-pointer flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-bold text-white">{app.company}</div>
                  <div className="text-[11px] text-[#94a3b8]">{app.role}</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300">
                    {app.stage.toUpperCase()}
                  </span>
                  <div className="text-[10px] font-mono text-emerald-400 font-bold mt-0.5">
                    {app.matchScore}% Match
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
