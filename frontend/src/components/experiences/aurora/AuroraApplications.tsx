import React, { useState } from 'react';
import { 
  Orbit, 
  Sparkles, 
  Compass, 
  MapPin, 
  DollarSign, 
  Calendar, 
  Clock, 
  ChevronRight, 
  ArrowRight,
  Bot
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { ApplicationItem } from '../../../types';

export const AuroraApplications: React.FC = () => {
  const { applications, setActiveSection } = useApp();
  const [activeNode, setActiveNode] = useState<ApplicationItem>(applications[0]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-[#11162a]/70 backdrop-blur-2xl border border-indigo-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest">
            <Orbit className="w-3.5 h-3.5 animate-spin" />
            <span>Opportunity Constellation &bull; Spatial Clusters</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-light text-white tracking-tight mt-1">
            Application Orbit Horizon
          </h1>
          <p className="text-xs text-[#94a3b8] mt-0.5">
            Spatial representation of opportunities organized by gravitational pull and interview conversion affinity.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button 
            variant="ai" 
            size="sm" 
            icon={Sparkles}
            onClick={() => setActiveSection('assistant')}
          >
            Synthesize Horizon Strategy
          </Button>
        </div>
      </div>

      {/* Spatial Constellation Field */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left (5 cols): Spatial Nodes */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-wider px-1">
            Gravitational Nodes ({applications.length})
          </div>

          <div className="space-y-2.5">
            {applications.map((app) => {
              const isSelected = activeNode.id === app.id;
              return (
                <div
                  key={app.id}
                  onClick={() => setActiveNode(app)}
                  className={`p-4 rounded-2xl backdrop-blur-xl border transition-all duration-300 cursor-pointer space-y-2 ${
                    isSelected
                      ? 'bg-[#182142]/80 border-cyan-500/60 shadow-[0_0_20px_rgba(6,182,212,0.2)]'
                      : 'bg-[#11162a]/60 border-indigo-500/20 hover:border-indigo-500/50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-white">{app.company}</h3>
                      <div className="text-xs text-[#94a3b8]">{app.role}</div>
                    </div>
                    <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-cyan-300 border border-indigo-500/30 uppercase font-bold">
                      {app.stage}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-xs font-mono pt-1">
                    <span className="text-cyan-400 font-bold">{app.matchScore}% Resonance</span>
                    <span className="text-[#64748b]">{app.salaryRange}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right (7 cols): Selected Orbital Node Intelligence */}
        <div className="lg:col-span-7 bg-[#11162a]/70 backdrop-blur-2xl border border-indigo-500/30 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl">
          <div className="border-b border-indigo-500/20 pb-5 space-y-2">
            <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest">
              Active Orbit Node Intelligence
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {activeNode.company} &mdash; {activeNode.role}
            </h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-[#94a3b8] pt-1">
              <span>{activeNode.location}</span>
              <span>&bull;</span>
              <span>{activeNode.salaryRange}</span>
            </div>
          </div>

          {/* Spatial Trajectory Notes */}
          <div className="p-4 rounded-2xl bg-[#0d1224]/80 border border-indigo-500/20 space-y-2">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-300 uppercase">
              <Bot className="w-4 h-4" />
              <span>Career Trajectory Context</span>
            </div>
            <p className="text-xs text-[#cbd5e1] leading-relaxed">
              {activeNode.notes || 'Strong positive signals from HM panel regarding team scaling leadership. Awaiting final offer formulation.'}
            </p>
          </div>

          {/* Action CTA */}
          <div className="pt-2 flex justify-end gap-3">
            <Button
              variant="ai"
              size="md"
              icon={ArrowRight}
              onClick={() => setActiveSection('interviews')}
            >
              Enter Scenario Simulation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
