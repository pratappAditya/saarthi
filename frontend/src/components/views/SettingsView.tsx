import React from 'react';
import { 
  Settings, 
  Palette, 
  Monitor, 
  Cpu, 
  Volume2, 
  Sliders, 
  Sparkles, 
  Check, 
  ShieldCheck,
  Zap,
  Layers,
  HardDrive
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import type { ExperienceMode, ThemeMode, DensityMode, AccentColor } from '../../types';

export const SettingsView: React.FC = () => {
  const { 
    experienceMode, 
    setExperienceMode, 
    themeMode, 
    setThemeMode, 
    density, 
    setDensity, 
    accentColor, 
    setAccentColor, 
    reducedMotion, 
    setReducedMotion,
    hardware,
    addToast
  } = useApp();

  const experienceModes: { 
    id: ExperienceMode; 
    name: string; 
    tag: string; 
    desc: string;
    architecture: string;
    diagram: string;
  }[] = [
    { 
      id: 'signature', 
      name: 'SIGNATURE', 
      tag: 'Editorial & Executive Dossier', 
      desc: 'Editorial Chief-of-Staff architecture. Vertical strategic navigation, narrative career dossiers, and private executive coaching rooms.',
      architecture: 'Chief-of-Staff Vertical Rail + Executive Briefing Canvas',
      diagram: 'rail-left'
    },
    { 
      id: 'forge', 
      name: 'FORGE', 
      tag: 'Technical IDE & Workbench', 
      desc: '3-Pane developer workbench. Monospace precision, AST tree explorer, unified line diff buffer, and live telemetry terminal statusbar.',
      architecture: '3-Pane Split IDE + AST Tree + Diagnostic Telemetry Bar',
      diagram: 'ide-split'
    },
    { 
      id: 'pulse', 
      name: 'PULSE', 
      tag: 'Kinetic Momentum & Action', 
      desc: 'High-velocity action dock. Daily career sprint missions, 5-stage progression lanes, 1-click power verb studio, and rapid-fire STAR training arena.',
      architecture: 'Floating Kinetic Dock + 5-Stage Kanban Progression + Arena',
      diagram: 'floating-dock'
    },
    { 
      id: 'aurora', 
      name: 'AURORA', 
      tag: 'Spatial & AI-Native Ambient OS', 
      desc: 'Immersive spatial canvas. Central intelligence core, opportunity constellation gravity wells, floating semantic resonance aura, and neural dialogue studio.',
      architecture: 'Floating Capsule + Spatial Orbital Nodes + Holographic Canvas',
      diagram: 'spatial-orbit'
    }
  ];

  const accents: { id: AccentColor; label: string; bgClass: string }[] = [
    { id: 'sapphire', label: 'Sapphire Cobalt', bgClass: 'bg-blue-500' },
    { id: 'emerald', label: 'Emerald Mint', bgClass: 'bg-emerald-500' },
    { id: 'amethyst', label: 'Electric Amethyst', bgClass: 'bg-indigo-500' },
    { id: 'amber', label: 'Warm Amber', bgClass: 'bg-amber-500' },
    { id: 'rose', label: 'Nordic Rose', bgClass: 'bg-rose-500' },
    { id: 'cyan', label: 'Glacier Cyan', bgClass: 'bg-cyan-400' }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Settings className="w-3.5 h-3.5 text-blue-400" />
            <span>PREFERENCES & WORKSPACE CONFIGURATION</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Settings & Appearance
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Switch experience design languages, theme palettes, UI density, and local hardware allocation.
          </p>
        </div>
      </div>

      {/* 1. EXPERIENCE MODES SWITCHER */}
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-bold text-[var(--text-primary)] font-display-title">
            Experience Design Language
          </h3>
          <p className="text-xs text-[var(--text-secondary)]">
            Four distinct typographic and spatial philosophies sharing identical feature architecture.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {experienceModes.map((mode) => {
            const isCurrent = experienceMode === mode.id;
            return (
              <Card
                key={mode.id}
                variant={isCurrent ? 'ai' : 'interactive'}
                padding="lg"
                onClick={() => {
                  setExperienceMode(mode.id);
                  addToast({ type: 'success', title: `Experience Mode: ${mode.name} Activated` });
                }}
                className={`transition-all space-y-3 cursor-pointer ${isCurrent ? 'border-blue-500/60 shadow-lg ring-1 ring-blue-500/30' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-mono uppercase font-bold tracking-wider text-[var(--accent-text)]">
                      {mode.name}
                    </span>
                    <h4 className="text-sm font-bold text-[var(--text-primary)] font-display-title mt-0.5">
                      {mode.tag}
                    </h4>
                  </div>
                  {isCurrent && (
                    <Badge variant="accent" size="xs" dot>
                      ACTIVE
                    </Badge>
                  )}
                </div>

                {/* Miniature Architectural Blueprint Diagram */}
                <div className="p-2.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] space-y-1.5">
                  <div className="text-[10px] font-mono text-[var(--accent-text)] font-semibold flex items-center justify-between">
                    <span>ARCHITECTURE:</span>
                    <span className="text-[var(--text-muted)] text-[9px]">{mode.diagram}</span>
                  </div>

                  {/* Visual Wireframe Diagram Representation */}
                  <div className="h-16 w-full rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)] p-1.5 flex gap-1.5 overflow-hidden">
                    {mode.diagram === 'rail-left' && (
                      <>
                        <div className="w-1/4 h-full rounded bg-blue-500/20 border border-blue-500/30 flex flex-col justify-between p-1">
                          <div className="w-full h-1.5 rounded bg-blue-400/50" />
                          <div className="space-y-0.5">
                            <div className="w-3/4 h-1 rounded bg-blue-400/30" />
                            <div className="w-1/2 h-1 rounded bg-blue-400/30" />
                          </div>
                        </div>
                        <div className="flex-1 h-full rounded bg-[var(--bg-subtle)] p-1 flex flex-col gap-1">
                          <div className="w-full h-3 rounded bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)]" />
                          <div className="grid grid-cols-2 gap-1 flex-1">
                            <div className="rounded bg-[var(--bg-surface-elevated)]" />
                            <div className="rounded bg-[var(--bg-surface-elevated)]" />
                          </div>
                        </div>
                      </>
                    )}

                    {mode.diagram === 'ide-split' && (
                      <>
                        <div className="w-1/5 h-full rounded bg-emerald-500/20 border border-emerald-500/30 flex flex-col gap-1 p-0.5">
                          <div className="w-full h-1 rounded bg-emerald-400/40" />
                          <div className="w-2/3 h-1 rounded bg-emerald-400/30" />
                          <div className="w-3/4 h-1 rounded bg-emerald-400/30" />
                        </div>
                        <div className="w-1/2 h-full rounded bg-[var(--bg-subtle)] p-1 flex flex-col gap-1">
                          <div className="w-full h-2 rounded bg-rose-500/20" />
                          <div className="w-full h-2 rounded bg-emerald-500/20" />
                          <div className="w-3/4 h-2 rounded bg-blue-500/20" />
                        </div>
                        <div className="w-[30%] h-full rounded bg-blue-500/10 border border-blue-500/20 p-1">
                          <div className="w-full h-1.5 rounded bg-blue-400/40" />
                        </div>
                      </>
                    )}

                    {mode.diagram === 'floating-dock' && (
                      <div className="w-full h-full flex flex-col gap-1">
                        <div className="w-3/4 mx-auto h-3 rounded-full bg-indigo-500/30 border border-indigo-500/40 flex items-center justify-around px-2">
                          <div className="w-2 h-1 rounded bg-indigo-300" />
                          <div className="w-2 h-1 rounded bg-indigo-300" />
                          <div className="w-2 h-1 rounded bg-indigo-300" />
                        </div>
                        <div className="flex-1 grid grid-cols-3 gap-1">
                          <div className="rounded bg-amber-500/20 border border-amber-500/30" />
                          <div className="rounded bg-indigo-500/20 border border-indigo-500/30" />
                          <div className="rounded bg-emerald-500/20 border border-emerald-500/30" />
                        </div>
                      </div>
                    )}

                    {mode.diagram === 'spatial-orbit' && (
                      <div className="w-full h-full flex items-center justify-center relative">
                        <div className="w-8 h-8 rounded-full bg-cyan-500/30 border border-cyan-400 flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.5)]">
                          <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                        </div>
                        <div className="absolute w-4 h-4 rounded-full bg-indigo-500/40 -top-0.5 left-2" />
                        <div className="absolute w-5 h-5 rounded-full bg-purple-500/40 -bottom-0.5 right-3" />
                      </div>
                    )}
                  </div>

                  <div className="text-[10px] text-[var(--text-secondary)] font-mono">
                    {mode.architecture}
                  </div>
                </div>

                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                  {mode.desc}
                </p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 2. THEME, DENSITY, ACCENT */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Theme Mode */}
        <Card variant="default" padding="lg" className="space-y-3">
          <span className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
            Color Palette
          </span>
          <div className="grid grid-cols-2 gap-2">
            {(['dark', 'light'] as ThemeMode[]).map((t) => (
              <button
                key={t}
                onClick={() => setThemeMode(t)}
                className={`py-2 px-3 rounded-[var(--radius-md)] text-xs font-semibold uppercase tracking-wider font-mono border transition-all cursor-pointer ${
                  themeMode === t
                    ? 'bg-[var(--accent-primary)] text-white shadow-xs'
                    : 'bg-[var(--bg-subtle)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[var(--border-strong)]'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </Card>

        {/* UI Density */}
        <Card variant="default" padding="lg" className="space-y-3">
          <span className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
            Information Density
          </span>
          <div className="grid grid-cols-3 gap-1.5">
            {(['comfortable', 'compact', 'dense'] as DensityMode[]).map((d) => (
              <button
                key={d}
                onClick={() => setDensity(d)}
                className={`py-2 px-2 rounded-[var(--radius-md)] text-xs font-semibold capitalize font-mono border transition-all cursor-pointer ${
                  density === d
                    ? 'bg-[var(--accent-primary)] text-white shadow-xs'
                    : 'bg-[var(--bg-subtle)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[var(--border-strong)]'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </Card>

        {/* Accent Color */}
        <Card variant="default" padding="lg" className="space-y-3">
          <span className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
            Accent Highlight
          </span>
          <div className="flex items-center gap-2">
            {accents.map((acc) => (
              <button
                key={acc.id}
                onClick={() => setAccentColor(acc.id)}
                title={acc.label}
                className={`w-7 h-7 rounded-full ${acc.bgClass} flex items-center justify-center transition-all cursor-pointer ${
                  accentColor === acc.id ? 'ring-2 ring-white ring-offset-2 ring-offset-[var(--bg-surface)] scale-110' : 'opacity-80 hover:opacity-100'
                }`}
              >
                {accentColor === acc.id && <Check className="w-3.5 h-3.5 text-white" />}
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* 3. HARDWARE & DESKTOP INTEGRATION */}
      <Card variant="default" padding="lg" className="space-y-4">
        <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
          Desktop Environment & Windows Integration
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
            <div>
              <div className="font-semibold text-[var(--text-primary)]">Reduced Motion Animations</div>
              <p className="text-[11px] text-[var(--text-secondary)]">Minimize layout shifts and heavy transitions</p>
            </div>
            <input
              type="checkbox"
              checked={reducedMotion}
              onChange={(e) => setReducedMotion(e.target.checked)}
              className="w-4 h-4 accent-blue-600 rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
            <div>
              <div className="font-semibold text-[var(--text-primary)]">Hardware Accelerated WebGL / WebGPU</div>
              <p className="text-[11px] text-[var(--text-secondary)]">Direct GPU memory buffers for sub-200ms token rendering</p>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 font-bold">ENABLED</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
            <div>
              <div className="font-semibold text-[var(--text-primary)]">Windows 11 Mica Surface Effects</div>
              <p className="text-[11px] text-[var(--text-secondary)]">Native titlebar integration & window blur</p>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 font-bold">ACTIVE</span>
          </div>
        </div>
      </Card>
    </div>
  );
};
