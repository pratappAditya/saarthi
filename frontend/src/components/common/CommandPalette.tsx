import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Sparkles, 
  FileText, 
  Briefcase, 
  Cpu, 
  Palette, 
  Settings, 
  ArrowRight, 
  ShieldCheck,
  CreditCard,
  MessagesSquare,
  Bot
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import type { NavSection, ExperienceMode } from '../../types';

interface CommandItem {
  id: string;
  title: string;
  category: 'Navigation' | 'Actions' | 'Resumes' | 'Applications' | 'Experience Modes';
  icon: React.ElementType;
  shortcut?: string;
  action: () => void;
}

export const CommandPalette: React.FC = () => {
  const { 
    isCommandPaletteOpen, 
    setIsCommandPaletteOpen, 
    setActiveSection,
    setExperienceMode,
    applications,
    resumes,
    setIsAssistantOpen,
    setIsAIStatusDrawerOpen,
    runLocalTailoring,
    addToast
  } = useApp();

  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (isCommandPaletteOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const allCommands: CommandItem[] = [
    // Fast Navigation
    {
      id: 'nav-home',
      title: 'Go to Command Center (Home)',
      category: 'Navigation',
      icon: Briefcase,
      action: () => { setActiveSection('home'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-tailor',
      title: 'Open Job Tailoring Studio',
      category: 'Navigation',
      icon: Sparkles,
      shortcut: 'T',
      action: () => { setActiveSection('tailor'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-resumes',
      title: 'View Resume Library & ATS Matrix',
      category: 'Navigation',
      icon: FileText,
      shortcut: 'R',
      action: () => { setActiveSection('resumes'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-apps',
      title: 'View Application Pipeline (Kanban)',
      category: 'Navigation',
      icon: Briefcase,
      shortcut: 'A',
      action: () => { setActiveSection('applications'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-interviews',
      title: 'Practice STAR Interview Questions',
      category: 'Navigation',
      icon: MessagesSquare,
      shortcut: 'I',
      action: () => { setActiveSection('interviews'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-assistant',
      title: 'Open Local AI Career Copilot',
      category: 'Navigation',
      icon: Bot,
      shortcut: 'Ctrl+J',
      action: () => { setIsAssistantOpen(true); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-models',
      title: 'Manage Local Nemotron Models & Weights',
      category: 'Navigation',
      icon: Cpu,
      action: () => { setActiveSection('ai-models'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-pricing',
      title: 'View Plans & Pricing (Student/Personal/Power)',
      category: 'Navigation',
      icon: CreditCard,
      action: () => { setActiveSection('billing'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-privacy',
      title: 'Audit Zero-Cloud Privacy Sandbox',
      category: 'Navigation',
      icon: ShieldCheck,
      action: () => { setActiveSection('privacy'); setIsCommandPaletteOpen(false); }
    },
    {
      id: 'nav-settings',
      title: 'Open System Preferences & Appearance',
      category: 'Navigation',
      icon: Settings,
      action: () => { setActiveSection('settings'); setIsCommandPaletteOpen(false); }
    },

    // AI Actions
    {
      id: 'act-tailor',
      title: 'Run Local Nemotron Tailoring on Current Resume',
      category: 'Actions',
      icon: Sparkles,
      action: () => {
        runLocalTailoring('Stripe Staff Engineer');
        setIsCommandPaletteOpen(false);
      }
    },
    {
      id: 'act-bench',
      title: 'Run Local GPU Inference Benchmark',
      category: 'Actions',
      icon: Cpu,
      action: () => {
        setIsAIStatusDrawerOpen(true);
        setIsCommandPaletteOpen(false);
      }
    },

    // Experience Modes
    {
      id: 'mode-sig',
      title: 'Switch Experience Mode to SIGNATURE (Refined & Editorial)',
      category: 'Experience Modes',
      icon: Palette,
      action: () => {
        setExperienceMode('signature');
        addToast({ type: 'success', title: 'Experience Mode: Signature Active' });
        setIsCommandPaletteOpen(false);
      }
    },
    {
      id: 'mode-forge',
      title: 'Switch Experience Mode to FORGE (Technical Monospace & Sharp)',
      category: 'Experience Modes',
      icon: Palette,
      action: () => {
        setExperienceMode('forge');
        addToast({ type: 'success', title: 'Experience Mode: Forge Active' });
        setIsCommandPaletteOpen(false);
      }
    },
    {
      id: 'mode-pulse',
      title: 'Switch Experience Mode to PULSE (Dynamic & High Energy)',
      category: 'Experience Modes',
      icon: Palette,
      action: () => {
        setExperienceMode('pulse');
        addToast({ type: 'success', title: 'Experience Mode: Pulse Active' });
        setIsCommandPaletteOpen(false);
      }
    },
    {
      id: 'mode-aurora',
      title: 'Switch Experience Mode to AURORA (Atmospheric & Luminous)',
      category: 'Experience Modes',
      icon: Palette,
      action: () => {
        setExperienceMode('aurora');
        addToast({ type: 'success', title: 'Experience Mode: Aurora Active' });
        setIsCommandPaletteOpen(false);
      }
    },

    // Resumes
    ...resumes.map(r => ({
      id: `res-${r.id}`,
      title: `Resume: ${r.title} (ATS: ${r.atsScore}%)`,
      category: 'Resumes' as const,
      icon: FileText,
      action: () => {
        setActiveSection('resumes');
        setIsCommandPaletteOpen(false);
      }
    })),

    // Applications
    ...applications.map(a => ({
      id: `app-${a.id}`,
      title: `Application: ${a.company} — ${a.role} [${a.stage.toUpperCase()}]`,
      category: 'Applications' as const,
      icon: Briefcase,
      action: () => {
        setActiveSection('applications');
        setIsCommandPaletteOpen(false);
      }
    }))
  ];

  const filteredCommands = allCommands.filter(c => 
    c.title.toLowerCase().includes(query.toLowerCase()) ||
    c.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < filteredCommands.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : filteredCommands.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4">
      <div 
        className="fixed inset-0 bg-black/75 backdrop-blur-sm"
        onClick={() => setIsCommandPaletteOpen(false)}
      />
      <div 
        className="relative w-full max-w-xl bg-[var(--bg-surface)] border border-[var(--border-strong)] rounded-[var(--radius-xl)] shadow-2xl z-10 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={e => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-[var(--border-subtle)] bg-[var(--bg-surface-elevated)]/40 gap-3">
          <Search className="w-4 h-4 text-[var(--text-muted)] shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
            onKeyDown={handleKeyDown}
            autoFocus
            placeholder="Type a command, resume, application, or mode..."
            className="w-full bg-transparent text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none"
          />
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono uppercase bg-black/40 rounded border border-white/10 text-neutral-400">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = cmd.icon;
              return (
                <div
                  key={cmd.id}
                  onClick={cmd.action}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3 py-2 rounded-[var(--radius-md)] text-xs cursor-pointer select-none transition-all ${
                    isSelected
                      ? 'bg-[var(--accent-subtle)] text-[var(--text-primary)] border border-[var(--accent-primary)]/30 font-medium'
                      : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-elevated)] border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-[var(--accent-text)]' : 'text-[var(--text-muted)]'}`} />
                    <span className="truncate">{cmd.title}</span>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 ml-2">
                    <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase px-1.5 py-0.5 rounded bg-black/20">
                      {cmd.category}
                    </span>
                    {cmd.shortcut && (
                      <kbd className="text-[10px] font-mono text-neutral-400 px-1.5 py-0.5 bg-white/5 rounded border border-white/10">
                        {cmd.shortcut}
                      </kbd>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-[var(--text-muted)]">
              No matching commands or resources found for "{query}".
            </div>
          )}
        </div>

        {/* Bottom Helper Bar */}
        <div className="px-4 py-2 border-t border-[var(--border-subtle)] bg-[var(--bg-subtle)] flex items-center justify-between text-[11px] text-[var(--text-muted)] font-mono">
          <div className="flex items-center gap-3">
            <span>↑↓ Navigate</span>
            <span>↵ Select</span>
          </div>
          <span>Local Nemotron • Private</span>
        </div>
      </div>
    </div>
  );
};
