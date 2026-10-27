import React from 'react';
import { 
  Home, 
  Briefcase, 
  FileText, 
  Sparkles, 
  Send, 
  Mic2, 
  Bot, 
  Cpu, 
  CreditCard, 
  ShieldCheck, 
  Settings, 
  Palette,
  ChevronRight,
  LogOut,
  Bell
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { NavSection } from '../../../types';
import { WindowsTitleBar } from '../../layout/WindowsTitleBar';

interface SignatureShellProps {
  children: React.ReactNode;
}

export const SignatureShell: React.FC<SignatureShellProps> = ({ children }) => {
  const { activeSection, setActiveSection, hardware } = useApp();

  const mainNav: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'home', label: 'Executive Briefing', icon: Home },
    { id: 'career', label: 'Career Trajectory', icon: Briefcase },
    { id: 'resumes', label: 'Resume Portfolio', icon: FileText },
    { id: 'applications', label: 'Application Pipeline', icon: Send },
    { id: 'interviews', label: 'Executive Coaching', icon: Mic2 },
    { id: 'assistant', label: 'Chief of Staff AI', icon: Bot },
  ];

  const secondaryNav: { id: NavSection; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'ai-models', label: 'Nemotron Models', icon: Cpu },
    { id: 'privacy', label: 'Local Security Vault', icon: ShieldCheck },
    { id: 'billing', label: 'Subscription', icon: CreditCard },
    { id: 'settings', label: 'Preferences', icon: Settings },
    { id: 'design-system', label: 'Design System', icon: Palette },
  ];

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0c0e12] text-[#e1e4ea] font-sans antialiased select-none">
      <WindowsTitleBar />

      <div className="flex flex-1 overflow-hidden">
        {/* Editorial Vertical Navigation Bar */}
        <aside className="w-64 bg-[#111318] border-r border-[#222630] flex flex-col justify-between p-5 select-none shrink-0">
          <div className="space-y-6">
            {/* Executive Brand Header */}
            <div className="px-2 pt-1 pb-3 border-b border-[#222630]/70 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                  <span className="font-serif italic text-lg tracking-tight font-medium text-white">
                    Saarthi
                  </span>
                </div>
                <p className="text-[10px] tracking-widest uppercase font-mono text-[#8b949e] mt-0.5">
                  Signature Executive
                </p>
              </div>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                LOCAL
              </span>
            </div>

            {/* Primary Nav Menu */}
            <div className="space-y-1">
              <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-[#6e7681]">
                Workspace
              </div>
              {mainNav.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all duration-150 cursor-pointer ${
                      isActive
                        ? 'bg-blue-600/15 text-blue-300 font-semibold border-l-2 border-blue-500 pl-2.5'
                        : 'text-[#8b949e] hover:text-[#e1e4ea] hover:bg-[#161b22]'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-[#6e7681]'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-blue-400/70" />}
                  </button>
                );
              })}
            </div>

            {/* Secondary Nav Menu */}
            <div className="space-y-1 pt-3 border-t border-[#222630]/70">
              <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-[#6e7681]">
                Platform
              </div>
              {secondaryNav.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all cursor-pointer ${
                      isActive
                        ? 'bg-blue-600/15 text-blue-300 font-semibold'
                        : 'text-[#8b949e] hover:text-[#e1e4ea] hover:bg-[#161b22]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-400' : 'text-[#6e7681]'}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Chief-of-Staff Hardware Pill */}
          <div className="pt-4 border-t border-[#222630]/70">
            <div className="p-2.5 rounded-lg bg-[#161b22] border border-[#262c36] space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-[#8b949e] font-serif italic">Nemotron Chief-of-Staff</span>
                <span className="flex items-center gap-1 text-emerald-400 font-mono text-[10px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Ready
                </span>
              </div>
              <div className="text-[10px] font-mono text-[#6e7681] truncate">
                4B Instruct • 127.0.0.1
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-8 lg:p-12 bg-[#0c0e12]">
          <div className="max-w-5xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
