import React from 'react';
import { 
  Sparkles, 
  Orbit, 
  Compass, 
  ArrowUpRight, 
  FileText, 
  TrendingUp, 
  Bot, 
  Radio,
  Layers,
  ChevronRight
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';

export const AuroraHome: React.FC = () => {
  const { setActiveSection, applications, resumes, hardware } = useApp();

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. CENTRAL CAREER INTELLIGENCE SURFACE */}
      <section className="p-8 sm:p-10 rounded-3xl bg-[#11162a]/70 backdrop-blur-2xl border border-indigo-500/30 shadow-[0_0_50px_rgba(79,70,229,0.12)] text-center space-y-6 relative overflow-hidden">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 text-cyan-300 text-xs font-mono tracking-widest uppercase">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>CAREER INTELLIGENCE CORE &bull; LOCAL NEMOTRON-3 8B</span>
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-light text-white tracking-tight max-w-3xl mx-auto leading-tight">
          "Your strongest career alignment this week is the <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Staff Architect</span> role at Stripe."
        </h1>

        <p className="text-sm text-[#94a3b8] max-w-xl mx-auto leading-relaxed">
          High semantic resonance (94%) with your WebAssembly leadership credentials. Predicted interview-to-offer probability is 78%.
        </p>

        <div className="pt-2 flex flex-wrap items-center justify-center gap-4">
          <Button
            variant="ai"
            size="md"
            icon={Sparkles}
            onClick={() => setActiveSection('assistant')}
            className="shadow-[0_0_20px_rgba(6,182,212,0.3)]"
          >
            Engage Career Copilot
          </Button>
          <Button
            variant="outline"
            size="md"
            onClick={() => setActiveSection('applications')}
          >
            Explore Constellation
          </Button>
        </div>
      </section>

      {/* 2. SPATIAL ORBITS & AMBIENT INTELLIGENCE SURFACES */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Orbit 1: Resume Aura */}
        <div 
          onClick={() => setActiveSection('resumes')}
          className="p-6 rounded-3xl bg-[#11162a]/60 backdrop-blur-xl border border-indigo-500/20 hover:border-cyan-500/50 transition-all duration-300 cursor-pointer space-y-4 group shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-2xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/20 group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5" />
            </div>
            <span className="text-xs font-mono text-cyan-400 font-bold">94% ATS AURA</span>
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">Master Resume Aura</h3>
            <p className="text-xs text-[#94a3b8] mt-1 leading-relaxed">
              Staff Frontend Architect v4.2 holds zero structural ATS defects and 18 high-yield metrics.
            </p>
          </div>

          <div className="text-xs font-mono text-cyan-300 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
            <span>Inspect Resonance</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Orbit 2: Application Gravity Well */}
        <div 
          onClick={() => setActiveSection('applications')}
          className="p-6 rounded-3xl bg-[#11162a]/60 backdrop-blur-xl border border-indigo-500/20 hover:border-indigo-500/50 transition-all duration-300 cursor-pointer space-y-4 group shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-2xl bg-indigo-500/15 text-indigo-400 border border-indigo-500/20 group-hover:scale-110 transition-transform">
              <Orbit className="w-5 h-5" />
            </div>
            <span className="text-xs font-mono text-indigo-400 font-bold">{applications.length} ACTIVE NODES</span>
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">Application Gravity Well</h3>
            <p className="text-xs text-[#94a3b8] mt-1 leading-relaxed">
              4 opportunities in active interview loops. Stripe and Vercel represent highest conversion affinity.
            </p>
          </div>

          <div className="text-xs font-mono text-indigo-300 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
            <span>Open Spatial Cluster</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>

        {/* Orbit 3: Simulation Studio Horizon */}
        <div 
          onClick={() => setActiveSection('interviews')}
          className="p-6 rounded-3xl bg-[#11162a]/60 backdrop-blur-xl border border-indigo-500/20 hover:border-purple-500/50 transition-all duration-300 cursor-pointer space-y-4 group shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="p-3 rounded-2xl bg-purple-500/15 text-purple-400 border border-purple-500/20 group-hover:scale-110 transition-transform">
              <Radio className="w-5 h-5" />
            </div>
            <span className="text-xs font-mono text-purple-400 font-bold">SIMULATION READY</span>
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">Scenario Simulation Studio</h3>
            <p className="text-xs text-[#94a3b8] mt-1 leading-relaxed">
              Real-time conversational STAR drills with instant rubric grading executed in local VRAM.
            </p>
          </div>

          <div className="text-xs font-mono text-purple-300 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
            <span>Enter Simulation</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>
    </div>
  );
};
