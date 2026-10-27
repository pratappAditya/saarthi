import React from 'react';
import { 
  Palette, 
  Layers, 
  Sparkles, 
  Type, 
  ShieldCheck, 
  Sliders, 
  Box, 
  Check, 
  Terminal,
  Zap,
  Star,
  Activity,
  Bot
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import type { ExperienceMode } from '../../types';

export const DesignSystemView: React.FC = () => {
  const { experienceMode, setExperienceMode, addToast } = useApp();

  const modes: { id: ExperienceMode; title: string; subtitle: string; fontTitle: string; fontBody: string; radius: string; philosophy: string }[] = [
    {
      id: 'signature',
      title: 'SIGNATURE',
      subtitle: 'Refined Editorial Elegance',
      fontTitle: 'Newsreader / Editorial Serif',
      fontBody: 'Plus Jakarta Sans',
      radius: '12px (Smooth curves)',
      philosophy: 'Harmonious balance of timeless editorial typography, soft neutral surfaces, and calculated micro-interactions. Designed for thoughtful executives and career strategists.'
    },
    {
      id: 'forge',
      title: 'FORGE',
      subtitle: 'Technical Precision & Monospace',
      fontTitle: 'JetBrains Mono Bold',
      fontBody: 'JetBrains Mono Regular',
      radius: '4px (Sharp brutalist)',
      philosophy: 'Zero visual noise, high-density terminal aesthetics, and razor-sharp borders. Designed for systems engineers, kernel architects, and builders who live in terminals.'
    },
    {
      id: 'pulse',
      title: 'PULSE',
      subtitle: 'Kinetic & High Energy',
      fontTitle: 'Space Grotesk Bold',
      fontBody: 'Plus Jakarta Sans',
      radius: '16px (Fluid geometry)',
      philosophy: 'Punchy electric indigo and emerald contrasts, vibrant pipeline velocity telemetry, and active feedback loops. Designed for fast-moving founders and engineers.'
    },
    {
      id: 'aurora',
      title: 'AURORA',
      subtitle: 'Atmospheric & Luminous Luxury',
      fontTitle: 'Syne / Display Extended',
      fontBody: 'Plus Jakarta Sans',
      radius: '20px (Organic pill)',
      philosophy: 'Deep midnight indigo backgrounds, soft celestial glows, and luxury surface elevation. Designed for creators who want an immersive, calming career canvas.'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Palette className="w-3.5 h-3.5 text-blue-400" />
            <span>SAARTHI DESIGN SYSTEM & 4 EXPERIENCE MODES</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Design System & Rationale
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Mathematical tokens, typography scales, zero-cloud privacy principles, and 4 interchangeable experience modes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="ai" size="sm">
            Current Mode: {experienceMode.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* 1. THE 4 EXPERIENCE MODES SHOWCASE */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold text-[var(--text-primary)] uppercase tracking-wider font-mono">
          The 4 Experience Modes (Single Information Architecture, Four Visual Dialects)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {modes.map((m) => {
            const isCurrent = experienceMode === m.id;
            return (
              <Card
                key={m.id}
                variant={isCurrent ? 'ai' : 'default'}
                padding="lg"
                className={`space-y-4 cursor-pointer transition-all ${isCurrent ? 'border-blue-500 ring-1 ring-blue-500/40' : ''}`}
                onClick={() => {
                  setExperienceMode(m.id);
                  addToast({ type: 'success', title: `Experience Mode: ${m.title} Activated` });
                }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-mono font-bold tracking-widest text-[var(--accent-text)]">
                      {m.title}
                    </span>
                    <h3 className="text-base font-bold text-[var(--text-primary)] font-display-title mt-0.5">
                      {m.subtitle}
                    </h3>
                  </div>

                  {isCurrent ? (
                    <Badge variant="accent" size="xs" dot>
                      ACTIVE
                    </Badge>
                  ) : (
                    <Button variant="ghost" size="xs">
                      Switch
                    </Button>
                  )}
                </div>

                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                  {m.philosophy}
                </p>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono p-2.5 rounded bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
                  <div>Display: <strong className="text-[var(--text-primary)]">{m.fontTitle}</strong></div>
                  <div>Geometry: <strong className="text-blue-400">{m.radius}</strong></div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 2. LIVE DESIGN TOKENS & COMPONENT ATOMS */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold text-[var(--text-primary)] uppercase tracking-wider font-mono">
          Live Design Token & Component Matrix
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Column 1: Buttons & Interactive Elements */}
          <Card variant="default" padding="lg" className="space-y-4">
            <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
              Button Hierarchy
            </h3>

            <div className="space-y-2">
              <Button variant="primary" size="sm" className="w-full">
                Primary Button
              </Button>
              <Button variant="secondary" size="sm" className="w-full">
                Secondary Button
              </Button>
              <Button variant="outline" size="sm" className="w-full">
                Outline Button
              </Button>
              <Button variant="ghost" size="sm" className="w-full">
                Ghost Button
              </Button>
              <Button variant="ai" size="sm" icon={Sparkles} className="w-full">
                Local Nemotron Button
              </Button>
              <Button variant="danger" size="sm" className="w-full">
                Destructive Button
              </Button>
            </div>
          </Card>

          {/* Column 2: Badges & Status Indicators */}
          <Card variant="default" padding="lg" className="space-y-4">
            <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
              Badges & Status Micro-Tokens
            </h3>

            <div className="flex flex-wrap gap-2">
              <Badge variant="default" size="sm">Default</Badge>
              <Badge variant="accent" size="sm" dot>Active</Badge>
              <Badge variant="success" size="sm" dot>Offer Ready</Badge>
              <Badge variant="warning" size="sm" dot>Follow-up</Badge>
              <Badge variant="danger" size="sm" dot>Archived</Badge>
              <Badge variant="ai" size="sm">Nemotron 4B</Badge>
              <Badge variant="purple" size="sm">Principal Level</Badge>
            </div>

            <div className="space-y-2 pt-2 border-t border-[var(--border-subtle)]">
              <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Progress Bar Styles</span>
              <Progress value={94} size="sm" variant="success" label="ATS Readability" />
              <Progress value={68} size="sm" variant="accent" label="Weekly Velocity" />
              <Progress value={45} size="sm" variant="ai" label="Local Inference Buffer" />
            </div>
          </Card>

          {/* Column 3: Mathematical Spacing & Radii */}
          <Card variant="default" padding="lg" className="space-y-4">
            <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
              Mathematical Tokens
            </h3>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
                <span>Card Outer Radius:</span>
                <span className="text-[var(--text-primary)] font-bold">var(--radius-xl)</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
                <span>Inner Element Radius:</span>
                <span className="text-[var(--text-primary)] font-bold">var(--radius-md)</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
                <span>Base Neutral Saturation:</span>
                <span className="text-emerald-400 font-bold">&lt; 3% Tinted</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
                <span>WCAG Contrast Ratio:</span>
                <span className="text-emerald-400 font-bold">&gt; 7:1 AAA</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
