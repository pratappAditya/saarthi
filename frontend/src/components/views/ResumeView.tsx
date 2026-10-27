import React, { useState } from 'react';
import { 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  Download, 
  Copy, 
  Plus, 
  Edit3, 
  Trash2, 
  ShieldCheck,
  Eye,
  Check,
  ArrowRight
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { Tabs } from '../common/Tabs';

import { useDocumentImport } from '../../hooks/useDocumentImport';

export const ResumeView: React.FC = () => {
  const { 
    resumes, 
    activeResume, 
    setActiveResume, 
    deleteResume,
    atsAnalysis, 
    setActiveSection,
    addToast,
    activeModel,
    isDemoMode,
    userProfile,
    loginProfile,
    licensingState
  } = useApp();

  const { fileInputRef, openFilePicker, handleFileUpload } = useDocumentImport();
  const [activeTab, setActiveTab] = useState<'preview' | 'ats' | 'sections'>('ats');
  const [copied, setCopied] = useState(false);

  const handleCopyMarkdown = () => {
    if (!activeResume || !activeResume.summary) return;
    navigator.clipboard.writeText(activeResume.summary);
    setCopied(true);
    addToast({ type: 'success', title: 'Resume Content Copied to Clipboard' });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportPDF = () => {
    if (!activeResume) return;
    const isFree = licensingState?.entitlements?.requires_watermark ?? true;
    const watermarkText = isFree ? "\n\n--- WATERMARK ---\nExported with Saarthi FREE Tier (Private Local AI Engine)" : "";
    const resumeText = `NAME: ${userProfile?.full_name || 'Candidate'}\nEMAIL: ${userProfile?.email || ''}\nROLE: ${activeResume.targetRole}\n\nSUMMARY:\n${activeResume.summary}\n\nSKILLS:\n${(activeResume.skills || []).join(', ')}${watermarkText}`;
    
    const blob = new Blob([resumeText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(activeResume.title || 'Resume').replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    addToast({
      type: 'success',
      title: isFree ? 'Exported FREE Watermarked Document' : 'Exported Clean Resume Document',
      message: `Downloaded ${(activeResume.title || 'Resume').replace(/\s+/g, '_')}.txt`
    });
  };

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editName, setEditName] = useState(userProfile?.full_name || '');
  const [editRole, setEditRole] = useState(activeResume?.targetRole || '');
  const [editLocation, setEditLocation] = useState(userProfile?.location || '');
  const [editEmail, setEditEmail] = useState(userProfile?.email || '');
  const [editPhone, setEditPhone] = useState(userProfile?.phone || '');
  const [editSummary, setEditSummary] = useState(activeResume?.summary || '');

  const handleSaveProfile = async () => {
    try {
      await loginProfile({
        full_name: editName.trim(),
        target_role: editRole.trim(),
        location: editLocation.trim(),
        email: editEmail.trim(),
        phone: editPhone.trim(),
        summary: editSummary.trim()
      });
      if (activeResume) {
        activeResume.targetRole = editRole.trim() || activeResume.targetRole;
        activeResume.summary = editSummary.trim() || activeResume.summary;
      }
      setIsEditingProfile(false);
      addToast({
        type: 'success',
        title: 'Profile Updated',
        message: 'Candidate profile and resume details saved.'
      });
    } catch (e) {
      addToast({
        type: 'error',
        title: 'Save Failed',
        message: 'Could not update profile.'
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.doc,.md,.txt"
        className="hidden"
      />

      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <FileText className="w-3.5 h-3.5 text-blue-400" />
            <span>RESUME LIBRARY & ATS INTELLIGENCE</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Resumes & ATS Matrix
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Manage versioned resumes, inspect parser telemetry, and tailor bullets with on-device Nemotron intelligence.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={openFilePicker}
          >
            Upload Resume (.pdf, .docx)
          </Button>
          <Button
            variant="ai"
            size="sm"
            icon={Sparkles}
            onClick={() => setActiveSection('tailor')}
          >
            Tailor This Resume
          </Button>
          <Button
            variant="secondary"
            size="sm"
            icon={copied ? Check : Copy}
            onClick={handleCopyMarkdown}
          >
            {copied ? 'Copied' : 'Copy Text'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={handleExportPDF}
          >
            Export Document
          </Button>
        </div>
      </div>

      {/* Resume Version Selector Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {resumes.map((r) => {
          const isSelected = r.id === activeResume?.id;
          return (
            <button
              key={r.id}
              onClick={() => setActiveResume(r)}
              className={`px-4 py-2.5 rounded-[var(--radius-lg)] border transition-all cursor-pointer select-none text-left shrink-0 ${
                isSelected
                  ? 'bg-[var(--accent-subtle)] border-[var(--accent-primary)]/40 shadow-xs'
                  : 'bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border-[var(--border-subtle)]'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold font-display-title ${isSelected ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>
                  {r.title}
                </span>
                {r.isDefault && (
                  <Badge variant="accent" size="xs">
                    Primary
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-3 text-[11px] font-mono mt-1 text-[var(--text-muted)]">
                <span>ATS: <strong className="text-emerald-400">{r.atsScore}%</strong></span>
                <span>•</span>
                <span>{r.version}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Grid: View Switcher & Detailed Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Main Content / ATS Matrix / Preview */}
        <div className="lg:col-span-2 space-y-4">
          <Tabs
            tabs={[
              { id: 'ats', label: 'ATS Analysis & Keyword Radar', count: `${atsAnalysis.overallScore}%` },
              { id: 'preview', label: 'Resume Preview' },
              { id: 'sections', label: 'Work Experience Bullets', count: 5 }
            ]}
            activeTab={activeTab}
            onChange={(t) => setActiveTab(t as any)}
            variant="segmented"
          />

          {/* TAB 1: ATS ANALYSIS */}
          {activeTab === 'ats' && (
            <div className="space-y-4">
              {/* ATS Scores Gauge Row */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <Card variant="subtle" padding="md" className="space-y-1">
                  <div className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Overall ATS Score</div>
                  <div className="text-2xl font-bold text-emerald-400 font-display-title">
                    {atsAnalysis.overallScore} / 100
                  </div>
                  <Progress value={atsAnalysis.overallScore} size="xs" variant="success" showPercentage={false} />
                  <p className="text-[10px] text-[var(--text-secondary)] pt-1">Ranked in top 2% of candidates</p>
                </Card>

                <Card variant="subtle" padding="md" className="space-y-1">
                  <div className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Parser Readability</div>
                  <div className="text-2xl font-bold text-blue-400 font-display-title">
                    {atsAnalysis.parseRate}%
                  </div>
                  <Progress value={atsAnalysis.parseRate} size="xs" variant="accent" showPercentage={false} />
                  <p className="text-[10px] text-[var(--text-secondary)] pt-1">100% compliant section headers</p>
                </Card>

                <Card variant="subtle" padding="md" className="space-y-1">
                  <div className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Target Keyword Match</div>
                  <div className="text-2xl font-bold text-purple-400 font-display-title">
                    {atsAnalysis.keywordMatchRate}%
                  </div>
                  <Progress value={atsAnalysis.keywordMatchRate} size="xs" variant="ai" showPercentage={false} />
                  <p className="text-[10px] text-[var(--text-secondary)] pt-1">13 matched • 3 suggestions</p>
                </Card>
              </div>

              {/* Matched & Missing Keywords */}
              <Card variant="default" padding="lg" className="space-y-4">
                <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
                  ATS Keyword Radar Breakdown
                </h3>

                <div className="space-y-2">
                  <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Matched Keywords in Current Resume ({atsAnalysis.matchedKeywords.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {atsAnalysis.matchedKeywords.map((kw, i) => (
                      <Badge key={i} variant="success" size="xs">
                        {kw}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-[var(--border-subtle)]">
                  <div className="text-[11px] font-semibold text-amber-400 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>High-Priority Missing Keywords for Target Role ({atsAnalysis.missingKeywords.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {atsAnalysis.missingKeywords.map((kw, i) => (
                      <Badge key={i} variant="warning" size="xs">
                        + {kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Actionable Insights from Local Nemotron */}
              <Card variant="default" padding="lg" className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider font-mono">
                    Local Nemotron Recommendations
                  </h3>
                  <span className="text-[10px] text-[var(--text-muted)] font-mono">
                    On-Device Analysis
                  </span>
                </div>

                <div className="space-y-2.5">
                  {atsAnalysis.actionableInsights.map((ins, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-[var(--radius-md)] border text-xs ${
                        ins.category === 'critical'
                          ? 'bg-rose-950/20 border-rose-500/30 text-rose-200'
                          : ins.category === 'improvement'
                          ? 'bg-amber-950/20 border-amber-500/30 text-amber-200'
                          : 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200'
                      }`}
                    >
                      <div className="font-bold font-display-title mb-0.5">{ins.title}</div>
                      <p className="opacity-90 leading-relaxed text-[11px]">{ins.description}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* TAB 2: RESUME PREVIEW */}
          {activeTab === 'preview' && (
            <Card variant="default" padding="lg" className="space-y-6 font-sans relative">
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="xs"
                  icon={Edit3}
                  onClick={() => {
                    setEditName(userProfile?.full_name || '');
                    setEditRole(activeResume?.targetRole || '');
                    setEditLocation(userProfile?.location || '');
                    setEditEmail(userProfile?.email || '');
                    setEditPhone(userProfile?.phone || '');
                    setEditSummary(activeResume?.summary || '');
                    setIsEditingProfile(true);
                  }}
                >
                  Edit Candidate Profile
                </Button>
              </div>

              <div className="border-b border-[var(--border-subtle)] pb-4 text-center space-y-1">
                <h2 className="text-xl font-bold text-[var(--text-primary)] font-display-title">
                  {userProfile?.full_name 
                    ? userProfile.full_name.toUpperCase() 
                    : isDemoMode 
                      ? 'DEMO CANDIDATE' 
                      : 'CANDIDATE NAME (UNSET)'}
                </h2>
                <p className="text-xs text-[var(--text-secondary)]">
                  {userProfile
                    ? `${userProfile.location || 'Location Unset'} • ${userProfile.email || 'email@example.com'}`
                    : isDemoMode 
                      ? 'San Francisco, CA • demo.candidate@example.com' 
                      : 'Location Unset • email@example.com'}
                </p>
                <p className="text-xs text-blue-400 font-mono font-medium">
                  {activeResume?.targetRole || 'Target Role Unset'}
                </p>
              </div>

              {/* Summary */}
              <div className="space-y-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-primary)] font-mono border-b border-[var(--border-subtle)] pb-1">
                  Professional Summary
                </h3>
                <p className="text-xs text-[var(--text-secondary)] leading-relaxed pt-1">
                  {activeResume?.summary || 'No summary provided.'}
                </p>
              </div>

              {/* Work Experience */}
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-primary)] font-mono border-b border-[var(--border-subtle)] pb-1">
                  Experience
                </h3>

                {(activeResume?.sections || []).map((sec) => (
                  <div key={sec.id} className="space-y-2">
                    <div className="flex justify-between items-baseline text-xs">
                      <div>
                        <span className="font-bold text-[var(--text-primary)]">{sec.role}</span>
                        <span className="text-[var(--text-muted)]"> — {sec.company}</span>
                      </div>
                      <span className="text-[11px] font-mono text-[var(--text-muted)]">{sec.period}</span>
                    </div>

                    <ul className="space-y-1.5 pl-4 list-disc text-xs text-[var(--text-secondary)]">
                      {sec.bullets?.map((b) => (
                        <li key={b.id} className="leading-relaxed">
                          {b.text}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* TAB 3: BULLET OPTIMIZER */}
          {activeTab === 'sections' && (
            <div className="space-y-3">
              {(activeResume?.sections || []).map((sec) => (
                <Card key={sec.id} variant="default" padding="md" className="space-y-3">
                  <div className="flex justify-between items-center border-b border-[var(--border-subtle)] pb-2">
                    <div>
                      <span className="text-xs font-bold text-[var(--text-primary)]">{sec.role}</span>
                      <span className="text-xs text-[var(--text-muted)]"> • {sec.company}</span>
                    </div>
                    <Badge variant="default" size="xs">
                      {sec.period}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    {sec.bullets?.map((b) => (
                      <div
                        key={b.id}
                        className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-xs space-y-1.5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-[var(--text-primary)] leading-relaxed">{b.text}</p>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 shrink-0">
                            Impact: {b.impactScore}%
                          </span>
                        </div>

                        {b.suggestedImprovement && (
                          <div className="text-[11px] text-blue-400 bg-blue-500/10 p-2 rounded border border-blue-500/20">
                            💡 <strong>Nemotron Tip:</strong> {b.suggestedImprovement}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Right 1 Col: Quick Actions & Tailoring Promotion */}
        <div className="space-y-4">
          <Card variant="ai" padding="md" className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-blue-400">
              <Sparkles className="w-4 h-4" />
              <span>NEMOTRON TAILORING</span>
            </div>
            <h4 className="text-sm font-bold text-[var(--text-primary)] font-display-title">
              Match against a Specific Job Spec
            </h4>
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
              Paste any job description to automatically calculate keyword gaps, align terminology, and accept line-by-line diffs.
            </p>
            <Button
              variant="primary"
              size="sm"
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => setActiveSection('tailor')}
              className="w-full"
            >
              Open Tailoring Studio
            </Button>
          </Card>

          <Card variant="subtle" padding="md" className="space-y-2.5">
            <h4 className="text-xs font-semibold text-[var(--text-primary)] font-display-title">
              Resume Skills Ingested
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {(activeResume?.skills || []).map((skill, i) => (
                <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-surface)] text-[var(--text-secondary)] border border-[var(--border-subtle)]">
                  {skill}
                </span>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {isEditingProfile && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl animate-in zoom-in-95 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
              <div className="flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-white text-base font-display-title">Edit Candidate Profile</h3>
              </div>
              <button 
                onClick={() => setIsEditingProfile(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-mono text-slate-400 uppercase">Full Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="e.g. Alex Morgan"
                  className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-mono text-slate-400 uppercase">Target Role</label>
                  <input
                    type="text"
                    value={editRole}
                    onChange={(e) => setEditRole(e.target.value)}
                    placeholder="e.g. Senior Systems Engineer"
                    className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-400 uppercase">Location</label>
                  <input
                    type="text"
                    value={editLocation}
                    onChange={(e) => setEditLocation(e.target.value)}
                    placeholder="e.g. Remote / New York, NY"
                    className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-mono text-slate-400 uppercase">Email Address</label>
                  <input
                    type="email"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    placeholder="e.g. alex@example.com"
                    className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-mono text-slate-400 uppercase">Phone Number</label>
                  <input
                    type="text"
                    value={editPhone}
                    onChange={(e) => setEditPhone(e.target.value)}
                    placeholder="e.g. +1 (555) 019-2834"
                    className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 uppercase">Professional Summary</label>
                <textarea
                  rows={3}
                  value={editSummary}
                  onChange={(e) => setEditSummary(e.target.value)}
                  placeholder="Describe your executive trajectory and core engineering strengths..."
                  className="w-full px-3 py-2 text-xs bg-black/40 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="pt-3 border-t border-[var(--border-subtle)] flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditingProfile(false)}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleSaveProfile}
              >
                Save Profile Changes
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
