import React from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  Calendar, 
  FileText, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  TrendingUp, 
  Bot, 
  ShieldCheck, 
  Building2, 
  Zap, 
  ExternalLink,
  ChevronRight,
  Send,
  Plus
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';

export const HomeView: React.FC = () => {
  const { 
    setActiveSection, 
    applications, 
    resumes, 
    careerGoal, 
    hardware, 
    activeModel,
    setIsAssistantOpen,
    setActiveApplication,
    addToast,
    userProfile,
    isAuthenticated,
    isDemoMode,
    toggleDemoMode,
    setIsOnboardingOpen
  } = useApp();

  const activeApps = applications.filter(a => a.stage !== 'rejected' && a.stage !== 'withdrawn');
  const interviewApp = applications.find(a => a.stage === 'interview') || applications[0];
  const offerApp = applications.find(a => a.stage === 'offer');

  const greetingName = isAuthenticated && userProfile?.full_name 
    ? userProfile.full_name 
    : isDemoMode 
      ? 'Candidate (Demo Mode)' 
      : null;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Personalized Header & Career Target */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>SAARTHI COMMAND CENTER • LOCAL ENGINE ONLINE</span>
            {isDemoMode && (
              <span className="ml-2 text-[10px] bg-amber-500/20 text-amber-300 font-bold px-2 py-0.5 rounded border border-amber-500/30">
                ● DEMO MODE ACTIVE
              </span>
            )}
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            {greetingName ? `Good morning, ${greetingName}.` : 'Welcome to Saarthi.'}
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            {careerGoal.targetTitle ? (
              <>Targeting: <strong className="text-[var(--text-primary)] font-medium">{careerGoal.targetTitle}</strong> ({careerGoal.targetLevel}) • Goal: {careerGoal.timelineGoal}</>
            ) : (
              'Your Private AI Career Companion & Resume Workspace'
            )}
          </p>
        </div>

        {/* Quick Actions Bar */}
        <div className="flex items-center gap-2 flex-wrap">
          <Button 
            variant="ai" 
            size="sm" 
            icon={Sparkles}
            onClick={() => setActiveSection('tailor')}
          >
            Tailor Resume for Job
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            icon={Plus}
            onClick={() => setActiveSection('applications')}
          >
            Track Application
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            icon={Bot}
            onClick={() => setIsAssistantOpen(true)}
          >
            Ask Copilot
          </Button>
        </div>
      </div>

      {/* Fresh Clean Session Welcome Banner if no data & not in demo mode */}
      {!isDemoMode && applications.length === 0 && resumes.length === 0 && (
        <Card variant="default" padding="lg" className="border-blue-500/30 bg-blue-950/20">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-white text-base">Clean Workspace Initialized</h3>
              </div>
              <p className="text-sm text-slate-300 max-w-xl">
                No candidate data is loaded by default. You can create your local profile, import your resume, or enable Demo Mode to explore with sample data.
              </p>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {!isAuthenticated && (
                <Button 
                  variant="primary" 
                  size="sm" 
                  onClick={() => setIsOnboardingOpen(true)}
                >
                  Create Profile / Sign In
                </Button>
              )}
              <Button 
                variant="secondary" 
                size="sm" 
                onClick={() => setActiveSection('resumes')}
              >
                Import Resume
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={toggleDemoMode}
              >
                Activate Demo Mode
              </Button>
            </div>
          </div>
        </Card>
      )}


      {/* INTELLIGENT "NEXT BEST MOVE" CARD (Hero Action) */}
      <Card variant="ai" padding="lg" className="relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-blue-500/10 to-transparent pointer-events-none hidden md:block" />
        
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30">
                RECOMMENDED BEST MOVE
              </span>
              <span className="text-xs text-[var(--text-muted)] font-mono">
                Computed by {activeModel.name.split(' ')[0]} on-device
              </span>
            </div>

            <h2 className="text-lg sm:text-xl font-bold text-[var(--text-primary)] font-display-title">
              Follow up with Elena at Stripe & prepare for Thursday's Panel.
            </h2>

            <p className="text-xs sm:text-sm text-[var(--text-secondary)] leading-relaxed">
              Your technical round at <strong>Stripe</strong> received top marks. Sending a concise, context-rich follow-up today increases panel pass rates by 28%. You also have an active written offer from <strong>Vercel</strong> pending review.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <Button
              variant="primary"
              size="md"
              icon={Send}
              onClick={() => {
                setActiveApplication(interviewApp);
                setActiveSection('applications');
              }}
            >
              Draft Stripe Follow-up
            </Button>
            <Button
              variant="secondary"
              size="md"
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => setActiveSection('interviews')}
            >
              Practice Panel STAR Drills
            </Button>
          </div>
        </div>
      </Card>

      {/* Pipeline Summary Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Pipeline Active */}
        <Card variant="interactive" padding="md" onClick={() => setActiveSection('applications')}>
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-mono text-[var(--text-secondary)] uppercase">Active Pipeline</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-[var(--text-primary)] font-display-title">
              {activeApps.length}
            </span>
            <span className="text-xs text-emerald-400 font-medium">+2 this week</span>
          </div>
          <p className="text-[11px] text-[var(--text-muted)] mt-1 truncate">
            1 Offer Extended • 1 Interview • 1 Screen
          </p>
        </Card>

        {/* Metric 2: Master Resume Health */}
        <Card variant="interactive" padding="md" onClick={() => setActiveSection('resumes')}>
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-mono text-[var(--text-secondary)] uppercase">ATS Health Index</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-400 font-display-title">
              94%
            </span>
            <span className="text-xs text-[var(--text-secondary)]">Master v4.2</span>
          </div>
          <p className="text-[11px] text-[var(--text-muted)] mt-1 truncate">
            Top 2% readability across Taleo & Workday
          </p>
        </Card>

        {/* Metric 3: Upcoming Interview */}
        <Card variant="interactive" padding="md" onClick={() => setActiveSection('interviews')}>
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-mono text-[var(--text-secondary)] uppercase">Next Interview</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-sm font-bold text-[var(--text-primary)] truncate font-display-title">
              Stripe Panel
            </span>
            <span className="text-xs text-amber-400 font-mono">In 3 days</span>
          </div>
          <p className="text-[11px] text-[var(--text-muted)] mt-1 truncate">
            Aug 24 • System Architecture & Scale
          </p>
        </Card>

        {/* Metric 4: Local AI Health */}
        <Card variant="interactive" padding="md" onClick={() => setActiveSection('ai-models')}>
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-mono text-[var(--text-secondary)] uppercase">Local Nemotron</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-blue-400 font-display-title">
              {hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tok/sec` : 'Not benchmarked'}
            </span>
          </div>
          <p className="text-[11px] text-emerald-400 mt-1 truncate font-mono">
            ✓ 100% Private On-Device Execution
          </p>
        </Card>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Application Pipeline & Urgent Follow-ups */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Pipeline Card */}
          <Card variant="default" padding="lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
                  Active Applications Pipeline
                </h3>
                <p className="text-xs text-[var(--text-secondary)]">
                  Real-time status across active opportunities
                </p>
              </div>
              <Button 
                variant="ghost" 
                size="xs" 
                icon={ArrowRight} 
                iconPosition="right"
                onClick={() => setActiveSection('applications')}
              >
                View Full Kanban
              </Button>
            </div>

            <div className="space-y-2.5">
              {applications.slice(0, 4).map((app) => {
                const stageBadges: Record<string, { label: string; variant: 'success' | 'accent' | 'warning' | 'default' | 'danger' }> = {
                  offer: { label: 'Offer Extended', variant: 'success' },
                  interview: { label: 'Interview Scheduled', variant: 'warning' },
                  screening: { label: 'Technical Screening', variant: 'accent' },
                  applied: { label: 'Application Submitted', variant: 'default' },
                  saved: { label: 'Bookmarked', variant: 'default' }
                };
                const badgeInfo = stageBadges[app.stage] || { label: app.stage, variant: 'default' };

                return (
                  <div
                    key={app.id}
                    onClick={() => {
                      setActiveApplication(app);
                      setActiveSection('applications');
                    }}
                    className="p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] transition-all cursor-pointer flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-3 truncate">
                      <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--bg-surface-elevated)] border border-[var(--border-strong)] flex items-center justify-center font-bold text-xs text-blue-400 shrink-0">
                        {app.companyLogoText}
                      </div>
                      <div className="truncate">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                            {app.company}
                          </span>
                          <span className="text-[11px] text-[var(--text-muted)] truncate">
                            • {app.role}
                          </span>
                        </div>
                        <div className="text-[11px] text-[var(--text-secondary)] truncate">
                          {app.salaryRange} • {app.location}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <Badge variant={badgeInfo.variant} size="xs">
                        {badgeInfo.label}
                      </Badge>
                      <ChevronRight className="w-4 h-4 text-[var(--text-muted)]" />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Quick Resume Health & Tailor Promotion */}
          <Card variant="default" padding="lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <div>
                <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
                  Primary Resume: {resumes[0].title}
                </h3>
                <p className="text-xs text-[var(--text-secondary)]">
                  {resumes[0].version} • Last updated {resumes[0].lastModified}
                </p>
              </div>
              <Button
                variant="primary"
                size="sm"
                icon={Sparkles}
                onClick={() => setActiveSection('tailor')}
              >
                Tailor Against Job Description
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-3 p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-center text-xs">
              <div>
                <div className="text-[10px] text-[var(--text-muted)] font-mono uppercase">ATS Parse Rate</div>
                <div className="text-base font-bold text-emerald-400 font-display-title">98%</div>
              </div>
              <div>
                <div className="text-[10px] text-[var(--text-muted)] font-mono uppercase">Keyword Alignment</div>
                <div className="text-base font-bold text-blue-400 font-display-title">91%</div>
              </div>
              <div>
                <div className="text-[10px] text-[var(--text-muted)] font-mono uppercase">Metric Density</div>
                <div className="text-base font-bold text-purple-400 font-display-title">96%</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right 1 Column: Urgent Actions, Weekly Goal, Local Hardware */}
        <div className="space-y-6">
          {/* Weekly Application Momentum Goal */}
          <Card variant="default" padding="md" className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-[var(--text-secondary)] uppercase">
                Weekly Target
              </span>
              <span className="text-xs font-mono text-emerald-400 font-bold">
                {careerGoal.weeklyApplicationsDone} / {careerGoal.weeklyApplicationTarget} Done
              </span>
            </div>

            <Progress
              value={(careerGoal.weeklyApplicationsDone / careerGoal.weeklyApplicationTarget) * 100}
              size="sm"
              variant="accent"
              showPercentage={false}
            />

            <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">
              1 more tailored submission needed to hit your weekly velocity benchmark.
            </p>
          </Card>

          {/* Actionable Follow-up List */}
          <Card variant="default" padding="md" className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-[var(--text-primary)] font-display-title">
                Pending Follow-ups
              </h4>
              <Badge variant="warning" size="xs">
                2 Actions
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex items-start justify-between gap-2 text-xs">
                <div>
                  <div className="font-semibold text-[var(--text-primary)]">Stripe (Elena Rostova)</div>
                  <p className="text-[11px] text-[var(--text-secondary)]">Check panel interview schedule</p>
                </div>
                <Button 
                  variant="outline" 
                  size="xs"
                  onClick={() => setIsAssistantOpen(true)}
                >
                  Draft
                </Button>
              </div>

              <div className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex items-start justify-between gap-2 text-xs">
                <div>
                  <div className="font-semibold text-[var(--text-primary)]">Linear (Tuomas Artman)</div>
                  <p className="text-[11px] text-[var(--text-secondary)]">Take-home architecture submission</p>
                </div>
                <Button 
                  variant="outline" 
                  size="xs"
                  onClick={() => setIsAssistantOpen(true)}
                >
                  Review
                </Button>
              </div>
            </div>
          </Card>

          {/* Local AI Sandbox Telemetry Card */}
          <Card variant="subtle" padding="md" className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-mono font-bold text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                LOCAL AI SANDBOX
              </span>
              <span className="text-[10px] font-mono text-[var(--text-muted)]">
                127.0.0.1
              </span>
            </div>
            <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">
              No cloud AI fallback. Your resumes, compensation details, and notes remain on your SSD.
            </p>
            <div className="text-[10px] font-mono text-[var(--text-muted)] pt-1 flex justify-between border-t border-[var(--border-subtle)]">
              <span>Model: Nemotron-Mini 4B</span>
              <span className="text-emerald-400">0 KB Uploaded</span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
