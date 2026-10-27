import React, { useState, useEffect } from 'react';
import { Search, Command, ArrowRight, Brain, FolderKanban, ShieldCheck, Sparkles, FileText, Bot, Radio, Target, Zap, Calendar } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import type { NavSection } from '../../types';

export const GlobalCommandBar: React.FC = () => {
  const { setActiveSection } = useApp();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isOpen) return null;

  const navigateTo = (section: NavSection) => {
    setActiveSection(section);
    setIsOpen(false);
    setQuery('');
  };

  const commands = [
    { label: 'Go to Command Center (Main Chat)', section: 'home' as NavSection, icon: Sparkles },
    { label: 'Open Routines & Automation Hub', section: 'routines' as NavSection, icon: Zap },
    { label: 'Create New Automation Routine', section: 'routines' as NavSection, icon: Sparkles },
    { label: 'View Upcoming Scheduled Runs', section: 'routines' as NavSection, icon: Calendar },
    { label: 'Open Deep Personalization Dashboard', section: 'personalization' as NavSection, icon: Sparkles },
    { label: 'What Saarthi Knows About Me (Personalization Inspector)', section: 'personalization' as NavSection, icon: Brain },
    { label: 'Explain Response Adaptation & Personalization', section: 'personalization' as NavSection, icon: Brain },
    { label: 'Reset Personalization Profile & Data', section: 'personalization' as NavSection, icon: ShieldCheck },
    { label: 'Start Voice Conversation Session', section: 'profile' as NavSection, icon: Radio },
    { label: 'Start Hands-Free Mode (Continuous Conversation)', section: 'profile' as NavSection, icon: Radio },
    { label: 'Voice Privacy & Settings (Trust Center)', section: 'trust' as NavSection, icon: ShieldCheck },
    { label: 'Open JARVIS Goal & Routine Manager', section: 'routines' as NavSection, icon: Target },
    { label: 'Open Multi-Domain Project Workspace', section: 'projects' as NavSection, icon: FolderKanban },
    { label: 'Open Persistent Memory Inspector', section: 'memory' as NavSection, icon: Brain },
    { label: 'Open Agent Activity & Task Trajectories', section: 'agents' as NavSection, icon: Bot },
    { label: 'Open Resume Workspace', section: 'resumes' as NavSection, icon: FileText },
    { label: 'Open Security & Trust Center', section: 'trust' as NavSection, icon: ShieldCheck },
  ];

  const filteredCommands = commands.filter(c => 
    !query || c.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-24 px-4 font-mono text-xs animate-in fade-in duration-150">
      <div className="w-full max-w-xl bg-[#0b0f19] border border-blue-500/30 rounded-2xl shadow-2xl overflow-hidden space-y-2">
        <div className="p-3 border-b border-white/10 flex items-center gap-3">
          <Search className="w-4 h-4 text-blue-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or query Saarthi..."
            className="w-full bg-transparent text-white focus:outline-none placeholder-gray-500 text-xs"
            autoFocus
          />
          <kbd className="px-2 py-0.5 rounded bg-white/10 text-[10px] text-gray-400">ESC</kbd>
        </div>

        <div className="p-2 max-h-80 overflow-y-auto space-y-1">
          {filteredCommands.map((cmd, idx) => {
            const Icon = cmd.icon;
            return (
              <button
                key={idx}
                onClick={() => navigateTo(cmd.section)}
                className="w-full p-2.5 rounded-xl hover:bg-white/10 text-left text-gray-200 flex items-center justify-between transition-all cursor-pointer group"
              >
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-blue-400" />
                  <span>{cmd.label}</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-gray-500 group-hover:text-white transition-all" />
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
