import React from 'react';
import { 
  Flame, 
  Zap, 
  Target, 
  FileText, 
  Send, 
  Swords, 
  Bot, 
  Settings, 
  ShieldCheck, 
  CreditCard, 
  Palette,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { NavSection } from '../../../types';
import { WindowsTitleBar } from '../../layout/WindowsTitleBar';

interface PulseShellProps {
  children: React.ReactNode;
}

export const PulseShell: React.FC<PulseShellProps> = ({ children }) => {
  const { activeSection, setActiveSection, applications } = useApp();

  const kineticTabs: { id: NavSection; label: string; icon: React.FC<{ className?: string }>; badge?: string }[] = [
    { id: 'home', label: 'Momentum', icon: Flame, badge: '🔥 5 Streak' },
    { id: 'career', label: 'Targets', icon: Target },
    { id: 'resumes', label: 'Resume Studio', icon: FileText, badge: '94%' },
    { id: 'tailor', label: 'Bullet Booster', icon: Zap },
    { id: 'applications', label: 'Journey Pipeline', icon: Send, badge: `${applications.length}` },
    { id: 'interviews', label: 'Training Arena', icon: Swords, badge: 'Round 3' },
    { id: 'assistant', label: 'Copilot', icon: Bot },
  ];

  const utilityTabs: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'ai-models', label: 'Nemotron AI', icon: Zap },
    { id: 'privacy', label: 'Vault', icon: ShieldCheck },
    { id: 'billing', label: 'Plans', icon: CreditCard },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'design-system', label: 'Tokens', icon: Palette },
  ];

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0a0d14] text-[#f0f4fc] font-sans antialiased select-none">
      <WindowsTitleBar />

      {/* Kinetic Dynamic Top Header Navigation */}
      <header className="bg-[#101524] border-b border-[#1c2438] px-4 py-2.5 flex items-center justify-between shadow-md shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-gradient-to-r from-amber-500/20 to-indigo-500/20 border border-indigo-500/30">
            <Flame className="w-4 h-4 text-amber-400 fill-amber-400" />
            <span className="font-extrabold tracking-tight text-white text-sm">
              SAARTHI <span className="text-indigo-400">PULSE</span>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-1 bg-[#161d31] p-1 rounded-xl border border-[#242e47]">
            {kineticTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeSection === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSection(tab.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-[0_0_12px_rgba(79,70,229,0.5)]'
                      : 'text-[#94a3b8] hover:text-white hover:bg-[#1f2942]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-indigo-400'}`} />
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                      isActive ? 'bg-white/20 text-white' : 'bg-[#242e47] text-[#94a3b8]'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Action Utilities */}
        <div className="flex items-center gap-2">
          <div className="hidden lg:flex items-center gap-1 text-xs">
            {utilityTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeSection === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSection(tab.id)}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    isActive ? 'bg-indigo-600/30 text-indigo-300' : 'text-[#64748b] hover:text-white hover:bg-[#161d31]'
                  }`}
                  title={tab.label}
                >
                  <Icon className="w-4 h-4" />
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>ACCELERATOR ACTIVE</span>
          </div>
        </div>
      </header>

      {/* Main Kinetic Content Stage */}
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[#0a0d14]">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};
