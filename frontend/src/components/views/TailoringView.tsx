import React, { useState } from 'react';
import { 
  Sparkles, 
  Check, 
  X, 
  ArrowRight, 
  Copy, 
  Download, 
  FileText, 
  CheckCircle2, 
  ShieldCheck, 
  RotateCcw,
  Zap,
  AlertTriangle,
  FileCode
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { Textarea, Input } from '../common/Input';
import { api } from '../../api';

export const TailoringView: React.FC = () => {
  const { 
    activeModel,
    hardware,
    activeResume,
    resumes,
    addToast
  } = useApp();

  const [company, setCompany] = useState('Stripe');
  const [targetRole, setTargetRole] = useState('Staff Frontend Engineer');
  const [jobDescription, setJobDescription] = useState(`Stripe is seeking a Staff Frontend Engineer to lead our Core Dashboard & Developer Platform. 

Key Requirements:
• 8+ years experience building mission-critical web applications with TypeScript, React, and modern micro-frontends.
• Deep understanding of Web Performance, Core Web Vitals (INP/LCP), and OpenTelemetry distributed tracing instrumentation.
• Proven track record designing enterprise Design System token architectures used by hundreds of engineers.
• Experience leading large cross-functional initiatives and mentoring senior engineers.`);

  const [analyzing, setAnalyzing] = useState(false);
  const [generatingDiffs, setGeneratingDiffs] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [diffs, setDiffs] = useState<any[]>([]);

  const handleAnalyzeJD = async () => {
    try {
      setAnalyzing(true);
      const res = await api.analyzeJD(jobDescription, company, targetRole, activeResume?.id);
      setAnalysisResult(res);
      addToast({
        type: 'success',
        title: 'JD Analysis Complete',
        message: `Match Score: ${res.ats_score}%. Extracted ${res.requirements?.required_skills?.length || 0} core skills.`
      });
    } catch (err) {
      addToast({ type: 'error', title: 'Analysis Failed', message: 'Could not extract JD requirements.' });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGenerateDiffs = async () => {
    try {
      setGeneratingDiffs(true);
      const res = await api.generateJDTailorDiffs(jobDescription, company, targetRole, activeResume?.id);
      setDiffs(res.diffs || []);
      addToast({
        type: 'success',
        title: 'Truthful Diffs Generated',
        message: `Calculated ${res.diffs?.length || 0} bullet patches. Zero fabricated facts.`
      });
    } catch (err) {
      addToast({ type: 'error', title: 'Diff Generation Failed', message: 'Could not calculate bullet patches.' });
    } finally {
      setGeneratingDiffs(false);
    }
  };

  const toggleDiffAccepted = (diffId: string) => {
    setDiffs(prev => prev.map(d => d.id === diffId ? { ...d, accepted: !d.accepted } : d));
  };

  const handleApplyAndSaveVersion = async () => {
    if (!activeResume || !activeResume.id) {
      addToast({ type: 'error', title: 'No Resume Selected', message: 'Please upload or select a master resume first.' });
      return;
    }
    const acceptedDiffs = diffs.filter(d => d.accepted);
    if (acceptedDiffs.length === 0) {
      addToast({ type: 'warning', title: 'No Accepted Diffs', message: 'Please accept at least one diff patch to save version.' });
      return;
    }
    try {
      const versionTag = `v2.0 — ${company} (${targetRole})`;
      const res = await api.applyTailoredVersion(activeResume.id, versionTag, company, targetRole, acceptedDiffs);
      addToast({
        type: 'success',
        title: 'Version Snapshot Saved',
        message: `Saved '${versionTag}' to SQLite database vault.`
      });
    } catch (err) {
      addToast({ type: 'error', title: 'Save Failed', message: 'Could not persist tailored version.' });
    }
  };

  const handleExport = async (fmt: 'pdf' | 'docx') => {
    const resumeText = activeResume?.summary || activeResume?.title || 'Tailored Candidate Resume';
    const content = `# TAILORED RESUME: ${targetRole}\nCompany: ${company}\n\n${resumeText}\n\n## ACCEPTED BULLET ENHANCEMENTS\n` +
      diffs.filter(d => d.accepted).map(d => `- ${d.suggestedText}`).join('\n');
    try {
      const res = await api.exportDocument(`Tailored_${company}_Resume`, content, fmt);
      if (res?.file_base64) {
        const binaryString = atob(res.file_base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const mimeType = fmt === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
        const blob = new Blob([bytes], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Tailored_${company}_Resume.${fmt}`;
        a.click();
        URL.revokeObjectURL(url);
        addToast({ type: 'success', title: `${fmt.toUpperCase()} Exported`, message: `Downloaded Tailored_${company}_Resume.${fmt}` });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Export Failed', message: `Could not export ${fmt.toUpperCase()}` });
    }
  };

  const acceptedCount = diffs.filter(d => d.accepted).length;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>NEMOTRON JOB TAILORING & GAP ANALYSIS STUDIO</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Phase 3: JD → Tailored Resume Workbench
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Extract requirements, perform candidate evidence matching, identify hard skill gaps, and review truthful diff patches.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="ai" size="sm" dot>
            {activeModel.name.split(' ')[0]} Active
          </Badge>
          <Button variant="outline" size="sm" icon={Download} onClick={() => handleExport('pdf')}>
            Export PDF
          </Button>
          <Button variant="outline" size="sm" icon={FileCode} onClick={() => handleExport('docx')}>
            Export DOCX
          </Button>
        </div>
      </div>

      {/* Target Company & Role Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          label="Target Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          placeholder="e.g. Stripe, OpenAI, Anthropic"
        />
        <Input
          label="Target Role"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          placeholder="e.g. Staff Frontend Engineer"
        />
      </div>

      {/* Split Studio Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 Cols): Job Description Input & Action Buttons */}
        <div className="lg:col-span-5 space-y-4">
          <Card variant="default" padding="md" className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[var(--text-primary)] font-display-title">
                Target Job Description
              </span>
              <span className="text-[10px] font-mono text-[var(--text-muted)]">
                Pasted Job Description
              </span>
            </div>

            <Textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={9}
              className="font-mono text-xs leading-relaxed"
              placeholder="Paste raw job description here..."
            />

            <div className="flex flex-col gap-2">
              <Button
                variant="primary"
                size="md"
                icon={Zap}
                isLoading={analyzing}
                onClick={handleAnalyzeJD}
                className="w-full"
              >
                {analyzing ? 'Extracting Requirements...' : '1. Analyze JD & Match Evidence'}
              </Button>

              <Button
                variant="ai"
                size="md"
                icon={Sparkles}
                isLoading={generatingDiffs}
                onClick={handleGenerateDiffs}
                className="w-full"
              >
                {generatingDiffs ? 'Calculating Truthful Diffs...' : '2. Generate Truthful Bullet Diffs'}
              </Button>
            </div>
          </Card>

          {/* Master Resume Context Badge */}
          <div className="p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Master Resume: <strong>{activeResume?.title || 'No Resume Uploaded'}</strong></span>
            </div>
            <span className="text-emerald-400 font-bold">
              {analysisResult ? `${analysisResult.ats_score}% ATS Match` : 'Ready'}
            </span>
          </div>

          {/* Gap Analysis Summary Card */}
          {analysisResult && (
            <Card variant="subtle" padding="md" className="space-y-3 font-sans text-xs">
              <h3 className="font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Evidence Match & Gap Analysis</span>
              </h3>
              <Progress value={analysisResult.ats_score} max={100} variant="accent" showPercentage size="md" />
              <div className="space-y-1.5 text-[11px] text-gray-300">
                <p><strong>Seniority Alignment:</strong> {analysisResult.requirements?.seniority_level}</p>
                <p><strong>Domain Context:</strong> {analysisResult.requirements?.domain_context}</p>
                <p><strong>Matched Skills:</strong> {analysisResult.evidence_match?.matched_skills?.join(', ') || 'None'}</p>
                {analysisResult.gap_analysis?.hard_gaps?.length > 0 && (
                  <div className="p-2 rounded bg-amber-950/30 border border-amber-500/30 text-amber-200 mt-2">
                    <strong>Hard Skill Gaps (Never Fabricated):</strong>
                    <ul className="list-disc list-inside mt-1">
                      {analysisResult.gap_analysis.hard_gaps.map((g: any, i: number) => (
                        <li key={i}>{g.skill} — {g.action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column (7 Cols): Diff Review & Version Saving */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between bg-[var(--bg-surface)] p-3 rounded-[var(--radius-md)] border border-[var(--border-subtle)]">
            <div>
              <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                Proposed Enhancements ({diffs.length})
              </span>
              <p className="text-[11px] text-[var(--text-secondary)]">
                {acceptedCount} of {diffs.length} accepted • Truthfulness Guaranteed
              </p>
            </div>

            <Button
              variant="primary"
              size="sm"
              icon={Check}
              onClick={handleApplyAndSaveVersion}
              disabled={acceptedCount === 0}
            >
              Save Version Snapshot ({acceptedCount})
            </Button>
          </div>

          {/* Diffs List */}
          <div className="space-y-3">
            {diffs.length === 0 ? (
              <div className="p-12 text-center border border-dashed border-[var(--border-subtle)] rounded-xl space-y-2 text-xs text-[#8b949e]">
                <Sparkles className="w-8 h-8 mx-auto text-blue-400 opacity-60" />
                <p className="font-bold text-white">No Diff Patches Generated Yet</p>
                <p className="max-w-xs mx-auto">Click "2. Generate Truthful Bullet Diffs" to calculate line-by-line bullet enhancements aligned with the job description.</p>
              </div>
            ) : (
              diffs.map((diff) => (
                <Card 
                  key={diff.id} 
                  variant={diff.accepted ? 'default' : 'subtle'} 
                  padding="md" 
                  className={`space-y-3 transition-all ${
                    diff.accepted ? 'border-blue-500/40 shadow-xs' : 'opacity-70 border-[var(--border-subtle)]'
                  }`}
                >
                  <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-2">
                    <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                      Bullet Patch #{diff.id}
                    </span>

                    <button
                      onClick={() => toggleDiffAccepted(diff.id)}
                      className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                        diff.accepted
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-neutral-800 text-neutral-400 hover:text-white border border-neutral-700'
                      }`}
                    >
                      {diff.accepted ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                      <span>{diff.accepted ? 'Accepted' : 'Rejected'}</span>
                    </button>
                  </div>

                  {/* Original vs Tailored */}
                  <div className="space-y-2 text-xs">
                    <div className="p-2.5 rounded bg-rose-950/20 border border-rose-500/20 text-rose-200/90 leading-relaxed">
                      <span className="text-[10px] uppercase font-mono font-bold text-rose-400 block mb-1">
                        − Master Resume Bullet
                      </span>
                      {diff.originalText}
                    </div>

                    <div className="p-2.5 rounded bg-emerald-950/20 border border-emerald-500/25 text-emerald-200 leading-relaxed">
                      <span className="text-[10px] uppercase font-mono font-bold text-emerald-400 block mb-1">
                        + Truthful Tailored Bullet
                      </span>
                      {diff.suggestedText}
                    </div>
                  </div>

                  {/* Rationale */}
                  <div className="text-[11px] text-blue-400/90 font-mono bg-blue-500/10 p-2 rounded border border-blue-500/20">
                    🎯 <strong>Truthful Rationale:</strong> {diff.rationale}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
