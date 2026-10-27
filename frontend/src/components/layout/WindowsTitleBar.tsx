import React from 'react';
import { 
  Sparkles, 
  Search, 
  Minus, 
  Square, 
  X, 
  ShieldCheck, 
  Palette, 
  Bot,
  Zap
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import type { ExperienceMode } from '../../types';

export const WindowsTitleBar: React.FC = () => {
  const { 
    experienceMode, 
    setExperienceMode, 
    hardware, 
    activeSection,
    setIsCommandPaletteOpen,
    setIsAIStatusDrawerOpen,
    setIsAssistantOpen,
    setIsDesignInspectorOpen
  } = useApp();

  const getSectionTitle = () => {
    switch (activeSection) {
      case 'home': return 'Home Command Center';
      case 'career': return 'Career Architecture & Goals';
      case 'resumes': return 'Resume Library & ATS Matrix';
      case 'tailor': return 'Nemotron Job Tailoring Studio';
      case 'cover-letters': return 'Cover Letter Generator';
      case 'applications': return 'Application Pipeline Tracker';
      case 'interviews': return 'STAR Interview Training Ground';
      case 'assistant': return 'Saarthi Local Career Copilot';
      case 'ai-models': return 'Local Nemotron Model Manager';
      case 'settings': return 'System Preferences';
      case 'billing': return 'Subscription & Plans';
      case 'privacy': return 'Zero-Cloud Privacy Sandbox';
      case 'design-system': return 'Saarthi Design System & 4 Experience Modes';
      default: return 'Career Workspace';
    }
  };

  const experienceModeLabels: Record<ExperienceMode, { name: string; color: string; icon: string }> = {
    signature: { name: 'Signature', color: 'text-blue-400', icon: '✦' },
    forge: { name: 'Forge', color: 'text-amber-400', icon: '⬢' },
    pulse: { name: 'Pulse', color: 'text-emerald-400', icon: '▲' },
    aurora: { name: 'Aurora', color: 'text-purple-400', icon: '◈' }
  };

  return (
    <div className="h-10 bg-[var(--bg-app)] border-b border-[var(--border-subtle)] flex items-center justify-between px-3 select-none z-40 shrink-0">
      {/* Left: Saarthi Logo & App Name */}
      <div className="flex items-center gap-2.5">
        <img 
          src="/saarthi-logo.png" 
          alt="Saarthi — YOUR AI COMPANION" 
          className="w-6 h-6 rounded object-contain shrink-0" 
        />
        <span className="font-bold text-xs tracking-wider text-[var(--text-primary)] font-display-title">
          Saarthi
        </span>
        <span className="text-[var(--text-muted)] text-xs">/</span>
        <span className="text-xs text-[var(--text-secondary)] font-medium">
          {getSectionTitle()}
        </span>
      </div>

      {/* Middle: Global Search / Command Bar Trigger */}
      <div className="flex items-center gap-3 max-w-md w-full justify-center">
        <button
          onClick={() => setIsCommandPaletteOpen(true)}
          className="flex items-center justify-between gap-3 px-3 py-1 bg-[var(--bg-subtle)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] rounded-full text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all cursor-pointer w-72"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-[var(--text-muted)]" />
            <span className="text-xs font-normal">Search or jump to...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono uppercase bg-black/30 rounded border border-white/10 text-neutral-400">
            Ctrl K
          </kbd>
        </button>
      </div>

      {/* Right: Mode Switcher, Privacy/AI Telemetry pill & Window Controls */}
      <div className="flex items-center gap-2">
        {/* Design System Inspector Trigger */}
        <button
          onClick={() => setIsDesignInspectorOpen(true)}
          className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] rounded-full transition-all cursor-pointer"
          title="Open Design System & Experience Mode Inspector"
        >
          <Palette className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Design System</span>
        </button>

        {/* Experience Mode Switcher Pill */}
        <div className="flex items-center bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-full p-0.5">
          {(['signature', 'forge', 'pulse', 'aurora'] as ExperienceMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setExperienceMode(mode)}
              className={`px-2 py-0.5 text-[10px] font-medium rounded-full transition-all cursor-pointer capitalize ${
                experienceMode === mode
                  ? 'bg-[var(--accent-primary)] text-white font-semibold shadow-xs'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
              title={`Switch to ${experienceModeLabels[mode].name} visual experience mode`}
            >
              {experienceModeLabels[mode].name}
            </button>
          ))}
        </div>

        {/* AI Status & Local Privacy Pill */}
        <button
          onClick={() => setIsAIStatusDrawerOpen(true)}
          className="flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono bg-emerald-500/10 hover:bg-emerald-500/15 border border-emerald-500/20 text-emerald-400 rounded-full transition-all cursor-pointer"
          title="View Local Nemotron Hardware & Inference Telemetry"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-semibold">NEMOTRON</span>
          <span className="text-[10px] text-emerald-300/80">
            ({hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} t/s` : 'Not benchmarked'})
          </span>
        </button>

        {/* AI Copilot Drawer Trigger */}
        <button
          onClick={() => setIsAssistantOpen(true)}
          className="p-1.5 text-[var(--text-secondary)] hover:text-white hover:bg-blue-600/20 rounded-[var(--radius-sm)] border border-transparent hover:border-blue-500/30 transition-all cursor-pointer"
          title="Toggle Saarthi Career Copilot (Ctrl + J)"
        >
          <Bot className="w-4 h-4 text-blue-400" />
        </button>
      </div>
    </div>
  );
};
