import React from 'react';
import { 
  Sparkles, 
  Compass, 
  FileText, 
  Orbit, 
  Radio, 
  Bot, 
  Cpu, 
  ShieldCheck, 
  CreditCard, 
  Settings, 
  Palette,
  Eye
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { NavSection } from '../../../types';
import { WindowsTitleBar } from '../../layout/WindowsTitleBar';

interface AuroraShellProps {
  children: React.ReactNode;
}

export const AuroraShell: React.FC<AuroraShellProps> = ({ children }) => {
  const { activeSection, setActiveSection, hardware } = useApp();

  const spatialNav: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'home', label: 'Intelligence Core', icon: Sparkles },
    { id: 'career', label: 'Trajectory', icon: Compass },
    { id: 'resumes', label: 'Resume Aura', icon: FileText },
    { id: 'applications', label: 'Constellation', icon: Orbit },
    { id: 'interviews', label: 'Simulation Studio', icon: Radio },
    { id: 'assistant', label: 'Ubiquitous AI', icon: Bot },
  ];

  const utilityNav: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'ai-models', label: 'Nemotron', icon: Cpu },
    { id: 'privacy', label: 'Enclave', icon: ShieldCheck },
    { id: 'billing', label: 'Tiers', icon: CreditCard },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'design-system', label: 'Tokens', icon: Palette },
  ];

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#070913] text-[#e0e7ff] font-sans antialiased select-none relative">
      {/* Ambient Celestial Glow Orbs in Background */}
      <div className="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-indigo-900/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[15%] w-[600px] h-[600px] bg-cyan-900/15 rounded-full blur-[160px] pointer-events-none" />

      <WindowsTitleBar />

      {/* Floating Spatial Island Control Bar */}
      <div className="pt-3 px-6 pb-2 flex items-center justify-between z-20 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#12182c]/80 backdrop-blur-xl border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.15)]">
            <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="font-semibold tracking-wider text-xs uppercase text-white">
              AURORA <span className="text-cyan-400 font-mono">OS</span>
            </span>
          </div>
        </div>

        {/* Center Floating Navigation Capsule */}
        <nav className="flex items-center gap-1 p-1 rounded-full bg-[#12182c]/90 backdrop-blur-2xl border border-indigo-500/25 shadow-2xl">
          {spatialNav.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-300 cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]'
                    : 'text-[#94a3b8] hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-indigo-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Local Intelligence Telemetry Capsule */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs">
            {utilityNav.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`p-2 rounded-full transition-colors cursor-pointer ${
                    isActive ? 'bg-indigo-600/30 text-cyan-300' : 'text-[#64748b] hover:text-white hover:bg-white/5'
                  }`}
                  title={item.label}
                >
                  <Icon className="w-4 h-4" />
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#12182c]/80 backdrop-blur-xl border border-emerald-500/30 text-emerald-300 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span>LOCAL AI READY</span>
          </div>
        </div>
      </div>

      {/* Main Immersive Spatial Stage */}
      <main className="flex-1 overflow-y-auto p-6 sm:p-8 lg:p-10 z-10">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};
