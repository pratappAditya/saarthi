import React, { useState, useEffect } from 'react';
import { 
  Building2, Briefcase, FileText, CheckCircle2, AlertTriangle, 
  Sparkles, Calendar, DollarSign, ArrowLeft, Download, FileCode 
} from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { api } from '../../api';

interface ApplicationDossierViewProps {
  appId: number;
  onBack?: () => void;
}

export const ApplicationDossierView: React.FC<ApplicationDossierViewProps> = ({ appId, onBack }) => {
  const [dossier, setDossier] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDossier();
  }, [appId]);

  const loadDossier = async () => {
    try {
      setLoading(true);
      const res = await api.getApplicationDossier(appId);
      setDossier(res);
    } catch (err) {
      console.error("Failed to load dossier", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-gray-400">
        <Sparkles className="w-6 h-6 mx-auto mb-2 animate-spin text-blue-400" />
        <p>Loading Application Dossier...</p>
      </div>
    );
  }

  if (!dossier || !dossier.application) {
    return (
      <div className="p-12 text-center text-xs text-rose-400 space-y-2">
        <p>Application Dossier Not Found</p>
        {onBack && <Button variant="outline" size="sm" onClick={onBack}>Back to Applications</Button>}
      </div>
    );
  }

  const app = dossier.application;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
        <div className="flex items-center gap-3">
          {onBack && (
            <button onClick={onBack} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 transition-all cursor-pointer">
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)]">
              <Building2 className="w-3.5 h-3.5 text-blue-400" />
              <span>APPLICATION DOSSIER WORKSPACE</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{app.company} — {app.role}</h1>
            <p className="text-xs text-gray-400 mt-0.5">{app.location || 'Remote'} • Stage: <strong className="text-blue-400">{app.status}</strong></p>
          </div>
        </div>

        <Badge variant="accent" size="md">
          {dossier.ats_score}% ATS Match
        </Badge>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (7 Cols): Job Description & ATS Analysis */}
        <div className="lg:col-span-7 space-y-4">
          <Card variant="default" padding="md" className="space-y-3">
            <h3 className="font-bold text-white text-xs font-display-title flex items-center justify-between">
              <span>Job Description</span>
              <span className="text-[10px] font-mono text-gray-400">{app.job_url ? <a href={app.job_url} target="_blank" rel="noreferrer" className="text-blue-400 underline">View URL</a> : 'Pasted Text'}</span>
            </h3>
            <div className="p-3 rounded bg-[#101524] border border-[#1c2438] font-mono text-xs text-gray-300 leading-relaxed max-h-64 overflow-y-auto">
              {app.job_description || 'No raw job description text stored for this application.'}
            </div>
          </Card>

          {/* Evidence Matching & Gaps */}
          <Card variant="subtle" padding="md" className="space-y-3">
            <h3 className="font-bold text-white text-xs flex items-center justify-between">
              <span>Candidate Evidence Match & Skill Gaps</span>
              <span className="text-emerald-400 font-mono text-xs">{dossier.ats_score}% Match Score</span>
            </h3>
            <Progress value={dossier.ats_score} max={100} variant="accent" showPercentage size="md" />

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded bg-emerald-950/20 border border-emerald-500/25 text-emerald-200">
                <strong>Verified Matched Skills:</strong>
                <p className="mt-1 font-mono text-[11px]">{dossier.evidence_match?.matched_skills?.join(', ') || 'None'}</p>
              </div>

              {dossier.gap_analysis?.hard_gaps?.length > 0 && (
                <div className="p-2.5 rounded bg-amber-950/30 border border-amber-500/30 text-amber-200">
                  <strong className="flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Hard Skill Gaps (Zero Fabrication):</strong>
                  <ul className="list-disc list-inside mt-1 font-mono text-[11px] space-y-0.5">
                    {dossier.gap_analysis.hard_gaps.map((g: any, i: number) => (
                      <li key={i}>{g.skill} — {g.action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right Column (5 Cols): Preparation, Recruiter & Actions */}
        <div className="lg:col-span-5 space-y-4">
          <Card variant="default" padding="md" className="space-y-3 text-xs">
            <h3 className="font-bold text-white font-display-title">Application Metadata</h3>
            <div className="space-y-2 text-gray-300">
              <p><strong>Salary Range:</strong> {app.salary || 'Not specified'}</p>
              <p><strong>Work Mode:</strong> {app.work_mode || 'Remote'}</p>
              <p><strong>Date Applied:</strong> {app.date_applied}</p>
              <p><strong>Recruiter Contact:</strong> {app.recruiter_contact || 'None added'}</p>
              <p><strong>Next Action:</strong> {app.next_action || 'Review interview preparation'}</p>
              {app.follow_up_date && <p className="text-amber-400 font-mono"><strong>Follow Up Date:</strong> {app.follow_up_date}</p>}
            </div>
          </Card>

          {/* Notes */}
          <Card variant="subtle" padding="md" className="space-y-2 text-xs">
            <h3 className="font-bold text-white">Application Notes</h3>
            <p className="text-gray-300 font-mono text-[11px] leading-relaxed">{app.notes || 'No notes added for this application.'}</p>
          </Card>
        </div>
      </div>
    </div>
  );
};
