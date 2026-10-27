import React, { useState } from 'react';
import { 
  Mail, 
  Sparkles, 
  Copy, 
  Check, 
  Download, 
  FileText, 
  RefreshCw, 
  Sliders,
  Send,
  Building2
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input, Textarea } from '../common/Input';
import type { CoverLetterItem } from '../../types';

export const CoverLetterView: React.FC = () => {
  const { 
    coverLetters, 
    activeCoverLetter, 
    setActiveCoverLetter, 
    generateCoverLetter, 
    isGeneratingCoverLetter, 
    addToast,
    activeResume
  } = useApp();

  const [company, setCompany] = useState('Stripe');
  const [role, setRole] = useState('Staff Frontend Engineer — Developer Platform');
  const [tone, setTone] = useState<CoverLetterItem['tone']>('Confident');
  const [copied, setCopied] = useState(false);
  const [letterContent, setLetterContent] = useState(activeCoverLetter?.content || '');

  const tones: CoverLetterItem['tone'][] = ['Confident', 'Technical', 'Executive', 'Conversational'];

  const handleCopy = () => {
    navigator.clipboard.writeText(letterContent);
    setCopied(true);
    addToast({ type: 'success', title: 'Cover Letter Copied' });
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Mail className="w-3.5 h-3.5 text-blue-400" />
            <span>COVER LETTER STUDIO</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Cover Letter Generator
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Synthesize high-converting, metric-aligned cover letters mapped to your resume and tailored tone on-device.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={copied ? Check : Copy}
            onClick={handleCopy}
          >
            {copied ? 'Copied' : 'Copy Text'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={() => addToast({ type: 'success', title: 'Cover Letter PDF Exported' })}
          >
            Export PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 Cols): Context & Tone Settings */}
        <div className="lg:col-span-5 space-y-4">
          <Card variant="default" padding="md" className="space-y-4">
            <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
              Job Context & Target
            </h3>

            <Input
              label="Target Company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Stripe, Linear, Anthropic"
              icon={Building2}
            />

            <Input
              label="Target Role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Staff Frontend Architect"
            />

            {/* Tone Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--text-secondary)]">
                Voice & Tone
              </label>
              <div className="grid grid-cols-2 gap-2">
                {tones.map((t) => (
                  <button
                    key={t}
                    onClick={() => setTone(t)}
                    className={`px-3 py-2 rounded-[var(--radius-md)] text-xs font-semibold border transition-all cursor-pointer select-none text-left ${
                      tone === t
                        ? 'bg-[var(--accent-subtle)] text-[var(--accent-text)] border-[var(--accent-primary)]/40 shadow-xs'
                        : 'bg-[var(--bg-subtle)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[var(--border-strong)]'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <Button
              variant="ai"
              size="md"
              icon={Sparkles}
              isLoading={isGeneratingCoverLetter}
              onClick={() => generateCoverLetter(company, role, tone)}
              className="w-full"
            >
              {isGeneratingCoverLetter ? 'Synthesizing with Nemotron...' : `Generate ${tone} Letter`}
            </Button>
          </Card>

          {/* Master Resume Context Badge */}
          <div className="p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-xs font-mono text-[var(--text-muted)] space-y-1">
            <div className="flex justify-between text-[var(--text-secondary)]">
              <span>Source Resume:</span>
              <strong className="text-[var(--text-primary)]">{(activeResume?.title || 'Resume').split(' ')[0]}</strong>
            </div>
            <div className="flex justify-between">
              <span>Metrics Injected:</span>
              <span className="text-emerald-400">42% TTI, $180k saved</span>
            </div>
          </div>
        </div>

        {/* Right Column (7 Cols): Editable Generated Document */}
        <div className="lg:col-span-7 space-y-4">
          <Card variant="default" padding="lg" className="space-y-4 font-sans">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
              <div>
                <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                  {company} — {role}
                </span>
                <div className="text-[11px] text-[var(--text-muted)] font-mono">
                  Tone: {tone} • 94% Alignment
                </div>
              </div>

              <Badge variant="accent" size="xs">
                Ready to Send
              </Badge>
            </div>

            <textarea
              value={letterContent || activeCoverLetter?.content}
              onChange={(e) => setLetterContent(e.target.value)}
              rows={16}
              className="w-full bg-transparent text-xs text-[var(--text-primary)] leading-relaxed resize-y focus:outline-none font-sans"
            />
          </Card>
        </div>
      </div>
    </div>
  );
};
