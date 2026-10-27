import React, { useState } from 'react';
import { 
  Send, 
  Flame, 
  Target, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Calendar, 
  Building2, 
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { ApplicationItem } from '../../../types';

export const PulseApplications: React.FC = () => {
  const { applications, setActiveSection } = useApp();

  const stages = [
    { id: 'saved', label: 'DISCOVERED', count: applications.filter(a => a.stage === 'saved').length },
    { id: 'applied', label: 'APPLIED', count: applications.filter(a => a.stage === 'applied').length },
    { id: 'screening', label: 'SCREENING', count: applications.filter(a => a.stage === 'screening').length },
    { id: 'interview', label: 'INTERVIEW LOOP', count: applications.filter(a => a.stage === 'interview').length },
    { id: 'offer', label: 'OFFER WON', count: applications.filter(a => a.stage === 'offer').length },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-[#101524] border border-[#1c2438] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase">
            <Send className="w-4 h-4" />
            <span>Visual Progression Pipeline &bull; Journey Map</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Application Velocity Journey
          </h1>
          <p className="text-xs text-[#94a3b8] mt-0.5">
            Track momentum across all 5 career conversion milestones.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button 
            variant="ai" 
            size="sm" 
            icon={Sparkles}
            onClick={() => setActiveSection('assistant')}
          >
            Generate Follow-up Sprint
          </Button>
        </div>
      </div>

      {/* 5-STAGE KINETIC PROGRESSION LANES */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {stages.map((stage, idx) => {
          const appsInStage = applications.filter(a => a.stage === stage.id);
          return (
            <div key={stage.id} className="bg-[#101524] border border-[#1c2438] rounded-2xl p-4 flex flex-col justify-between space-y-3">
              <div className="flex items-center justify-between border-b border-[#1c2438] pb-2">
                <span className="text-[11px] font-extrabold text-indigo-400 tracking-wider">
                  {stage.label}
                </span>
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-[10px] font-bold">
                  {stage.count}
                </span>
              </div>

              <div className="space-y-2 flex-1">
                {appsInStage.map((app) => (
                  <div
                    key={app.id}
                    onClick={() => setActiveSection('interviews')}
                    className="p-3 rounded-xl bg-[#151c30] border border-[#242e47] hover:border-indigo-500 transition-all cursor-pointer space-y-1.5"
                  >
                    <div className="text-xs font-bold text-white">{app.company}</div>
                    <div className="text-[11px] text-[#94a3b8] truncate">{app.role}</div>
                    <div className="flex items-center justify-between pt-1 text-[10px] font-mono">
                      <span className="text-emerald-400 font-bold">{app.matchScore}% Match</span>
                      <span className="text-[#64748b]">{app.salaryRange}</span>
                    </div>
                  </div>
                ))}

                {appsInStage.length === 0 && (
                  <div className="p-4 text-center text-xs text-[#64748b] border border-dashed border-[#1c2438] rounded-xl">
                    No active roles
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
