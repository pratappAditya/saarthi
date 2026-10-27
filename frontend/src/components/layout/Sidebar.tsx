import React from 'react';
import { 
  Home, 
  Compass, 
  FileText, 
  Sparkles, 
  Mail, 
  Kanban, 
  MessagesSquare, 
  Bot, 
  Cpu, 
  ShieldCheck, 
  CreditCard, 
  Settings, 
  Palette,
  ChevronLeft,
  ChevronRight,
  UserCheck,
  Briefcase,
  LayoutDashboard,
  DollarSign,
  Target,
  GitCommit,
  GraduationCap,
  FolderKanban,
  Zap,
  Mic,
  Monitor,
  Terminal,
  Layers,
  BookOpen,
  Brain
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useEntitlements } from '../../context/EntitlementContext';
import type { NavSection } from '../../types';

interface NavItem {
  id: NavSection;
  label: string;
  icon: React.ElementType;
  badge?: string | number;
  badgeColor?: string;
  capabilityRequired?: string;
}

export const Sidebar: React.FC = () => {
  const { 
    activeSection, 
    setActiveSection, 
    isSidebarExpanded, 
    setIsSidebarExpanded,
    applications,
    resumes,
    hardware,
    setIsAIStatusDrawerOpen,
    setIsOnboardingOpen,
    userProfile,
    isAuthenticated,
    isDemoMode
  } = useApp();

  const { hasCapability, activePlanId, planName } = useEntitlements();

  const activeApplicationsCount = applications.filter(a => a.stage !== 'rejected' && a.stage !== 'withdrawn').length;

  // Compute initials and label dynamically
  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  };

  const userInitials = isAuthenticated && userProfile?.full_name 
    ? getInitials(userProfile.full_name) 
    : isDemoMode 
      ? 'DM' 
      : 'CU';

  const userNameDisplay = isAuthenticated && userProfile?.full_name 
    ? userProfile.full_name 
    : isDemoMode 
      ? 'Demo Candidate' 
      : 'Candidate Profile';

  const userStatusSubtitle = `${planName} (${activePlanId.toUpperCase()})`;

  // Master Capability-Filtered Navigation List
  const candidateNavItems: NavItem[] = [
    { id: 'dashboard', label: 'Career Dashboard', icon: LayoutDashboard, capabilityRequired: 'career.master_resume' },
    { id: 'home', label: 'Command Center', icon: Home },
    { id: 'cross-domain' as NavSection, label: 'Cross-Domain Workflows', icon: Layers },
    { id: 'projects', label: 'Projects', icon: FolderKanban, capabilityRequired: 'workspace.projects' },
    { id: 'agents', label: 'Agent Activity', icon: Bot, capabilityRequired: 'agents.custom' },
    { id: 'memory', label: 'Persistent Memory', icon: Brain, capabilityRequired: 'memory.session' },
    { id: 'trust', label: 'Trust & Audit Center', icon: ShieldCheck },
    { id: 'profile', label: 'Assistant Profile', icon: Bot },
    { id: 'resumes', label: 'Resume Workspace', icon: FileText, badge: resumes.length || undefined, capabilityRequired: 'career.master_resume' },
    { id: 'tailor', label: 'Job Tailoring Diffs', icon: Sparkles, capabilityRequired: 'career.resume_tailoring' },
    { id: 'applications', label: 'Application Tracker', icon: Kanban, badge: activeApplicationsCount || undefined, badgeColor: 'bg-blue-500/20 text-blue-300 border-blue-400/30', capabilityRequired: 'career.application_tracker' },
    { id: 'interviews', label: 'Interview Prep & STAR', icon: MessagesSquare, capabilityRequired: 'career.interview_prep' },
    { id: 'salary', label: 'Salary & Offer Coach', icon: DollarSign, capabilityRequired: 'career.salary_coach' },
    { id: 'goals', label: 'Career Goals', icon: Target, capabilityRequired: 'career.goals' },
    { id: 'trajectory', label: 'Career Trajectory', icon: GitCommit, capabilityRequired: 'career.trajectory' },
    { id: 'cover-letters', label: 'Cover Letters', icon: Mail, capabilityRequired: 'career.master_resume' },
  ];

  const primaryNavItems = candidateNavItems.filter(item => {
    if (!item.capabilityRequired) return true;
    return hasCapability(item.capabilityRequired);
  });

  const secondaryNavItems: NavItem[] = [
    { id: 'ai-models', label: 'Nemotron Models', icon: Cpu },
    { id: 'privacy', label: 'Privacy Sandbox', icon: ShieldCheck },
    { id: 'billing', label: 'Plans & Pricing', icon: CreditCard },
    { id: 'design-system', label: 'Design System', icon: Palette },
    { id: 'settings', label: 'Preferences', icon: Settings },
  ];

  return (
    <aside 
      className={`h-[calc(100vh-2.5rem)] bg-[var(--bg-surface)] border-r border-[var(--border-subtle)] flex flex-col justify-between transition-all duration-200 shrink-0 z-30 select-none ${
        isSidebarExpanded ? 'w-64' : 'w-16'
      }`}
    >
      {/* Top Workspace Identity */}
      <div className="p-3 border-b border-[var(--border-subtle)] flex items-center justify-between">
        {isSidebarExpanded ? (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-[var(--radius-md)] bg-[var(--bg-surface-elevated)] border border-[var(--border-strong)] flex items-center justify-center text-blue-400 font-bold text-sm shrink-0">
              {userInitials}
            </div>
            <div className="flex flex-col truncate">
              <span className="text-xs font-semibold text-[var(--text-primary)] truncate font-display-title">
                {userNameDisplay}
              </span>
              <span className="text-[10px] text-[var(--text-secondary)] truncate flex items-center gap-1">
                <Briefcase className="w-2.5 h-2.5 text-blue-400" />
                {userStatusSubtitle}
              </span>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 mx-auto rounded-[var(--radius-md)] bg-[var(--bg-surface-elevated)] border border-[var(--border-strong)] flex items-center justify-center text-blue-400 font-bold text-sm">
            {userInitials}
          </div>
        )}

        <button
          onClick={() => setIsSidebarExpanded(!isSidebarExpanded)}
          className="p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)] rounded-[var(--radius-sm)] transition-colors cursor-pointer hidden md:flex"
          title={isSidebarExpanded ? 'Collapse Sidebar' : 'Expand Sidebar'}
        >
          {isSidebarExpanded ? <ChevronLeft className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
        {/* Primary Group */}
        <div className="space-y-1">
          {isSidebarExpanded && (
            <div className="px-3 pb-1 text-[10px] uppercase font-mono font-semibold tracking-wider text-[var(--text-muted)]">
              Workspace
            </div>
          )}
          {primaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-xs font-medium transition-all group cursor-pointer select-none ${
                  isActive
                    ? 'bg-[var(--accent-subtle)] text-[var(--accent-text)] font-semibold shadow-xs border border-[var(--accent-primary)]/20'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)] border border-transparent'
                }`}
                title={!isSidebarExpanded ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 transition-colors ${isActive ? 'text-[var(--accent-text)]' : 'text-[var(--text-muted)] group-hover:text-[var(--text-primary)]'}`} />
                {isSidebarExpanded && (
                  <>
                    <span className="truncate text-left flex-1">{item.label}</span>
                    {item.badge !== undefined && (
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full border border-white/5 ${item.badgeColor || 'bg-neutral-800 text-[var(--text-secondary)]'}`}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </button>
            );
          })}
        </div>

        {/* Secondary Group */}
        <div className="space-y-1 pt-2 border-t border-[var(--border-subtle)]">
          {isSidebarExpanded && (
            <div className="px-3 pb-1 text-[10px] uppercase font-mono font-semibold tracking-wider text-[var(--text-muted)]">
              Local System
            </div>
          )}
          {secondaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-[var(--radius-md)] text-xs font-medium transition-all group cursor-pointer select-none ${
                  isActive
                    ? 'bg-[var(--accent-subtle)] text-[var(--accent-text)] font-semibold shadow-xs border border-[var(--accent-primary)]/20'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface-elevated)] border border-transparent'
                }`}
                title={!isSidebarExpanded ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 transition-colors ${isActive ? 'text-[var(--accent-text)]' : 'text-[var(--text-muted)] group-hover:text-[var(--text-primary)]'}`} />
                {isSidebarExpanded && (
                  <span className="truncate text-left flex-1">{item.label}</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom AI Status Banner */}
      <div className="p-3 border-t border-[var(--border-subtle)] bg-[var(--bg-subtle)]/60">
        {isSidebarExpanded ? (
          <div 
            onClick={() => setIsAIStatusDrawerOpen(true)}
            className="p-2.5 rounded-[var(--radius-md)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] transition-all cursor-pointer flex flex-col gap-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase font-bold text-emerald-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Local AI Engine
              </span>
              <span className="text-[10px] font-mono text-neutral-400">
                {hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} t/s` : 'Not benchmarked'}
              </span>
            </div>
            <div className="text-[11px] text-[var(--text-secondary)] truncate font-mono">
              Nemotron-Mini 4B (Q4)
            </div>
            <div className="w-full bg-neutral-800 h-1 rounded-full overflow-hidden">
              <div className="bg-emerald-500 h-full w-[42%]" />
            </div>
          </div>
        ) : (
          <button
            onClick={() => setIsAIStatusDrawerOpen(true)}
            className="w-full flex items-center justify-center p-2 rounded-[var(--radius-md)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] text-emerald-400 cursor-pointer"
            title="Local AI Engine: Online"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          </button>
        )}

        {isSidebarExpanded && (
          <button
            onClick={() => setIsOnboardingOpen(true)}
            className="mt-2 w-full text-center text-[10px] text-[var(--text-muted)] hover:text-blue-400 transition-colors py-1 cursor-pointer"
          >
            Run First-Time Setup Wizard
          </button>
        )}
      </div>
    </aside>
  );
};
