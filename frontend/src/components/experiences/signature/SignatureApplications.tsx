import React, { useState } from 'react';
import { 
  Building2, 
  Send, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  ChevronRight, 
  DollarSign, 
  MapPin, 
  User, 
  MessageSquare,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { ApplicationItem } from '../../../types';

export const SignatureApplications: React.FC = () => {
  const { applications, setSelectedApplication, setActiveSection } = useApp();
  const [selectedApp, setSelectedApp] = useState<ApplicationItem | null>(null);

  const currentApp = selectedApp || applications[0];

  if (!currentApp || applications.length === 0) {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#222630]">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-[#8b949e] uppercase">
              <Send className="w-3.5 h-3.5 text-blue-400" />
              <span>Opportunity Portfolio &bull; Narrative Timeline</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-serif font-medium text-white tracking-tight mt-1">
              Application Trajectory & Context
            </h1>
            <p className="text-xs text-[#8b949e] mt-0.5">
              High-level executive timeline tracking key conversations, recruiter alignment, and strategic milestones.
            </p>
          </div>
        </div>

        <div className="p-12 text-center border border-[#222630] rounded-xl bg-[#111318] space-y-4">
          <Building2 className="w-12 h-12 text-[#8b949e] mx-auto opacity-50" />
          <h3 className="text-lg font-serif font-bold text-white">No Applications Tracked Yet</h3>
          <p className="text-xs text-[#8b949e] max-w-md mx-auto">
            Your application pipeline is completely empty. Create your first tracked opportunity or activate Demo Mode to explore with sample applications.
          </p>
          <div className="pt-2">
            <Button variant="primary" size="sm" onClick={() => setActiveSection('applications')}>
              Manage Applications
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#222630]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#8b949e] uppercase">
            <Send className="w-3.5 h-3.5 text-blue-400" />
            <span>Opportunity Portfolio &bull; Narrative Timeline</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-serif font-medium text-white tracking-tight mt-1">
            Application Trajectory & Context
          </h1>
          <p className="text-xs text-[#8b949e] mt-0.5">
            High-level executive timeline tracking key conversations, recruiter alignment, and strategic milestones.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button 
            variant="ai" 
            size="sm" 
            icon={Sparkles}
            onClick={() => setActiveSection('assistant')}
          >
            Synthesize Follow-ups
          </Button>
        </div>
      </div>

      {/* Main Narrative Split: Left Opportunity List, Right Narrative Dossier */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (5 cols): Elegant Opportunity Cards */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-mono uppercase tracking-wider text-[#8b949e] px-1 pb-1">
            Active Strategic Tracks ({applications.length})
          </div>

          {applications.map((app) => {
            const isSelected = currentApp?.id === app.id;
            return (
              <div
                key={app.id}
                onClick={() => setSelectedApp(app)}
                className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                  isSelected
                    ? 'bg-[#161a23] border-blue-500/60 shadow-lg'
                    : 'bg-[#111318] border-[#222630] hover:border-[#30363d]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white font-serif">{app.company}</h3>
                    <div className="text-xs text-[#8b949e]">{app.role}</div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 capitalize border border-blue-500/20">
                    {app.stage}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-[#6e7681] pt-1">
                  <span>{app.salaryRange}</span>
                  <span className="text-emerald-400 font-mono font-medium">{app.matchScore}% Match</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column (7 cols): Selected Opportunity Timeline & Executive Dossier */}
        <div className="lg:col-span-7 bg-[#111318] rounded-xl border border-[#222630] p-6 lg:p-8 space-y-6">
          {/* Header */}
          <div className="border-b border-[#222630] pb-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-blue-400 uppercase tracking-widest">
                Executive Dossier
              </span>
              <span className="text-xs font-mono text-[#8b949e]">
                Applied {currentApp.dateApplied}
              </span>
            </div>
            <h2 className="text-2xl font-serif font-bold text-white">
              {currentApp.company} &mdash; {currentApp.role}
            </h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-[#8b949e] pt-1">
              <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> {currentApp.location}</span>
              <span className="flex items-center gap-1.5"><DollarSign className="w-3.5 h-3.5" /> {currentApp.salaryRange}</span>
            </div>
          </div>

          {/* Key Contacts */}
          {currentApp.contacts && currentApp.contacts.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-mono uppercase text-[#8b949e]">Key Relationship Contacts</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {currentApp.contacts.map((c, i) => (
                  <div key={i} className="p-2.5 rounded-lg bg-[#161a23] border border-[#222630] text-xs">
                    <div className="font-semibold text-white">{c.name}</div>
                    <div className="text-[11px] text-[#8b949e]">{c.title}</div>
                    <div className="text-[10px] font-mono text-blue-400 mt-0.5">{c.email}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chronological Narrative Timeline */}
          {currentApp.timeline && currentApp.timeline.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase text-[#8b949e]">Timeline of Strategic Engagements</h4>
              <div className="space-y-4 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-[#222630] pl-6">
                {currentApp.timeline.map((item, idx) => (
                  <div key={idx} className="relative space-y-0.5">
                    <div className="absolute -left-6 top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-[#111318]" />
                    <div className="text-[10px] font-mono text-blue-400">{item.date}</div>
                    <div className="text-xs font-semibold text-white">{item.event}</div>
                    {item.details && (
                      <p className="text-xs text-[#8b949e] font-light leading-relaxed">
                        {item.details}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strategic Notes */}
          <div className="p-4 rounded-lg bg-[#161a23] border border-[#222630] space-y-2">
            <div className="flex items-center gap-2 text-xs font-mono uppercase text-[#8b949e]">
              <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
              <span>Executive Briefing Notes</span>
            </div>
            <p className="text-xs text-[#c9d1d9] leading-relaxed font-light">
              {currentApp.notes || 'No briefing notes available.'}
            </p>
          </div>

          {/* Action Footer */}
          <div className="pt-2 flex justify-end gap-3">
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => setActiveSection('interviews')}
            >
              Prepare for Next Round <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
