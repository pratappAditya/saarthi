import React from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  Calendar, 
  CheckCircle2, 
  Clock, 
  Building2, 
  FileText, 
  ShieldCheck,
  TrendingUp,
  Award,
  ChevronRight
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';

export const SignatureHome: React.FC = () => {
  const { setActiveSection, applications, resumes, hardware, isDemoMode, toggleDemoMode, userProfile, isAuthenticated } = useApp();

  const activeApps = applications.filter(a => a.stage !== 'rejected' && a.stage !== 'withdrawn');
  const interviews = applications.filter(a => a.stage === 'interview');
  const offers = applications.filter(a => a.stage === 'offer');

  const greetingName = isAuthenticated && userProfile?.full_name 
    ? userProfile.full_name 
    : isDemoMode 
      ? 'Candidate (Demo Mode)' 
      : null;

  return (
    <div className="max-w-6xl mx-auto space-y-10 animate-in fade-in duration-300">
      {/* Editorial Welcome Header */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3 text-xs font-mono text-[var(--text-secondary)]">
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            <span>SAARTHI EXECUTIVE SIGNATURE EXPERIENCE</span>
          </div>

          <button
            onClick={toggleDemoMode}
            className={`px-3 py-1 rounded-full text-xs font-mono font-semibold transition-all cursor-pointer border ${
              isDemoMode
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
            }`}
          >
            {isDemoMode ? '● DEMO MODE ACTIVE (Click to Clear)' : '✓ CLEAN USER STATE (Click for Demo Data)'}
          </button>
        </div>

        <h1 className="text-3xl lg:text-4xl font-serif font-medium text-white tracking-tight leading-tight">
          {greetingName ? `Good morning, ${greetingName}.` : 'Welcome to Saarthi.'}
        </h1>

        <div className="p-6 rounded-xl bg-[#12151c] border border-[#222630] space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-blue-400 font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Executive Career Synthesis</span>
          </div>

          <p className="text-base text-[#c9d1d9] leading-relaxed font-light">
            Your career trajectory requires deliberate attention in <strong className="font-semibold text-white">three strategic areas</strong> today:
          </p>

          <div className="space-y-2.5 pt-1 text-sm">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-[#161a23] border border-[#252c38] text-[#e1e4ea]">
              <span className="font-mono text-xs font-bold text-blue-400 px-1.5 py-0.5 rounded bg-blue-500/10 shrink-0 mt-0.5">01</span>
              <div className="flex-1">
                <strong className="font-medium text-white">Follow up with Stripe:</strong> Technical recruiter David Kim requested compensation alignment notes after Round 3 architecture.
              </div>
              <Button variant="ghost" size="xs" onClick={() => setActiveSection('applications')}>
                Review App <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-lg bg-[#161a23] border border-[#252c38] text-[#e1e4ea]">
              <span className="font-mono text-xs font-bold text-amber-400 px-1.5 py-0.5 rounded bg-amber-500/10 shrink-0 mt-0.5">02</span>
              <div className="flex-1">
                <strong className="font-medium text-white">Refine AI Systems Resume:</strong> Linear's Staff Frontend spec requires stronger WebAssembly & Distributed State impact metrics.
              </div>
              <Button variant="ghost" size="xs" onClick={() => setActiveSection('resumes')}>
                Polish Resume <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-lg bg-[#161a23] border border-[#252c38] text-[#e1e4ea]">
              <span className="font-mono text-xs font-bold text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-500/10 shrink-0 mt-0.5">03</span>
              <div className="flex-1">
                <strong className="font-medium text-white">Executive Interview Tomorrow:</strong> Final Round Presentation with Vercel VP of Engineering at 2:00 PM PST.
              </div>
              <Button variant="ghost" size="xs" onClick={() => setActiveSection('interviews')}>
                Start Prep <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 2. ASYMMETRIC SECTION: NARRATIVE CAREER TRAJECTORY & STRATEGIC PIPELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (7 cols): Strategic Narrative Timeline */}
        <div className="lg:col-span-7 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-serif font-medium text-white">
              Career Trajectory & Milestones
            </h2>
            <button
              onClick={() => setActiveSection('career')}
              className="text-xs text-blue-400 hover:text-blue-300 font-mono flex items-center gap-1 cursor-pointer"
            >
              Expand Plan <ChevronRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-4 relative before:absolute before:left-3 before:top-3 before:bottom-3 before:w-px before:bg-[#222630]">
            <div className="relative pl-8 space-y-1">
              <div className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-emerald-400 ring-4 ring-[#0c0e12]" />
              <div className="text-xs font-mono text-emerald-400 uppercase">Current Milestone</div>
              <h3 className="text-sm font-semibold text-white">Staff / Principal Level Interview Loop</h3>
              <p className="text-xs text-[#8b949e] leading-relaxed">
                4 active interview tracks in progress. ATS alignment across target specs is at 94%.
              </p>
            </div>

            <div className="relative pl-8 space-y-1">
              <div className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-blue-400 ring-4 ring-[#0c0e12]" />
              <div className="text-xs font-mono text-[#8b949e] uppercase">Target Q3 2026</div>
              <h3 className="text-sm font-semibold text-white">Compensation Target: $260k - $310k TC</h3>
              <p className="text-xs text-[#8b949e] leading-relaxed">
                Targeting tier-1 engineering organizations with high remote flexibility and equity grants.
              </p>
            </div>

            <div className="relative pl-8 space-y-1">
              <div className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-[#30363d] ring-4 ring-[#0c0e12]" />
              <div className="text-xs font-mono text-[#6e7681] uppercase">Next Horizon</div>
              <h3 className="text-sm font-semibold text-[#8b949e]">VP of Engineering / Tech Fellow Transition</h3>
              <p className="text-xs text-[#6e7681]">
                Long-term leadership governance and open-source system foundations.
              </p>
            </div>
          </div>

          {/* Master Resume Health Card */}
          <div className="p-5 rounded-xl bg-[#111318] border border-[#222630] space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-mono text-[#8b949e] uppercase">Master Resume Health</span>
              </div>
              <span className="text-xs font-mono text-emerald-400 font-bold">94% ATS Match</span>
            </div>
            <p className="text-xs text-[#c9d1d9] leading-relaxed">
              "Staff Frontend Architect v4.2" contains 18 high-impact quantifiable metrics and passes 100% of major enterprise ATS parse rules.
            </p>
            <div className="pt-2 flex gap-3">
              <Button variant="outline" size="xs" onClick={() => setActiveSection('resumes')}>
                Open Document Workspace
              </Button>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Restrained Key Metrics & Executive Follow-ups */}
        <div className="lg:col-span-5 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-serif font-medium text-white">
              Strategic Portfolio
            </h2>
            <button
              onClick={() => setActiveSection('applications')}
              className="text-xs text-blue-400 hover:text-blue-300 font-mono flex items-center gap-1 cursor-pointer"
            >
              All Roles ({applications.length}) <ChevronRight className="w-3 h-3" />
            </button>
          </div>

          {/* Key Executive Numbers */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-4 rounded-xl bg-[#111318] border border-[#222630] text-center space-y-1">
              <div className="text-2xl font-serif font-medium text-white">{activeApps.length}</div>
              <div className="text-[10px] font-mono text-[#8b949e] uppercase">Active Pipelines</div>
            </div>
            <div className="p-4 rounded-xl bg-[#111318] border border-[#222630] text-center space-y-1">
              <div className="text-2xl font-serif font-medium text-blue-400">{interviews.length}</div>
              <div className="text-[10px] font-mono text-[#8b949e] uppercase">In Interviews</div>
            </div>
            <div className="p-4 rounded-xl bg-[#111318] border border-[#222630] text-center space-y-1">
              <div className="text-2xl font-serif font-medium text-emerald-400">{offers.length}</div>
              <div className="text-[10px] font-mono text-[#8b949e] uppercase">Offers In Hand</div>
            </div>
          </div>

          {/* High Priority Roles */}
          <div className="p-5 rounded-xl bg-[#111318] border border-[#222630] space-y-3">
            <div className="text-xs font-mono text-[#8b949e] uppercase tracking-wider">
              Priority Opportunity Tracker
            </div>

            <div className="space-y-2.5">
              {activeApps.slice(0, 3).map((app) => (
                <div 
                  key={app.id}
                  onClick={() => setActiveSection('applications')}
                  className="p-3 rounded-lg bg-[#161a23] border border-[#222630] hover:border-blue-500/40 transition-all cursor-pointer flex items-center justify-between"
                >
                  <div>
                    <div className="text-xs font-semibold text-white">{app.company}</div>
                    <div className="text-[11px] text-[#8b949e]">{app.role}</div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 capitalize">
                      {app.stage}
                    </span>
                    <div className="text-[10px] text-[#6e7681] mt-0.5">{app.salaryRange}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chief-of-Staff Confidentiality Assurance */}
          <div className="p-4 rounded-xl bg-[#0e1713] border border-emerald-900/40 text-emerald-300 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-emerald-200">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero-Cloud Confidentiality</span>
            </div>
            <p className="text-[11px] text-emerald-300/80 leading-relaxed font-light">
              Executive compensation, recruiter notes, and interview simulations execute purely inside local VRAM. No analytics transmission.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
