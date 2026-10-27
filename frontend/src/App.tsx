import React, { useState, useEffect } from 'react';
import { useApp } from './context/AppContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { WindowsTitleBar } from './components/layout/WindowsTitleBar';
import { Sidebar } from './components/layout/Sidebar';
import { CommandPalette } from './components/common/CommandPalette';
import { AIAssistantDrawer } from './components/ai/AIAssistantDrawer';
import { AIStatusPanel } from './components/ai/AIStatusPanel';
import { OnboardingModal } from './components/ai/OnboardingModal';

// 4 Distinct Experience Shells
import { SignatureShell } from './components/experiences/signature/SignatureShell';
import { SignatureHome } from './components/experiences/signature/SignatureHome';
import { SignatureResume } from './components/experiences/signature/SignatureResume';
import { SignatureApplications } from './components/experiences/signature/SignatureApplications';
import { SignatureInterviews } from './components/experiences/signature/SignatureInterviews';

import { ForgeShell } from './components/experiences/forge/ForgeShell';
import { ForgeHome } from './components/experiences/forge/ForgeHome';
import { ForgeResume } from './components/experiences/forge/ForgeResume';
import { ForgeApplications } from './components/experiences/forge/ForgeApplications';
import { ForgeInterviews } from './components/experiences/forge/ForgeInterviews';

import { PulseShell } from './components/experiences/pulse/PulseShell';
import { PulseHome } from './components/experiences/pulse/PulseHome';
import { PulseResume } from './components/experiences/pulse/PulseResume';
import { PulseApplications } from './components/experiences/pulse/PulseApplications';
import { PulseInterviews } from './components/experiences/pulse/PulseInterviews';

import { AuroraShell } from './components/experiences/aurora/AuroraShell';
import { AuroraHome } from './components/experiences/aurora/AuroraHome';
import { AuroraResume } from './components/experiences/aurora/AuroraResume';
import { AuroraApplications } from './components/experiences/aurora/AuroraApplications';
import { AuroraInterviews } from './components/experiences/aurora/AuroraInterviews';

// Shared Subsystem Views
import { CareerView } from './components/views/CareerView';
import { TailoringView } from './components/views/TailoringView';
import { CoverLetterView } from './components/views/CoverLetterView';
import { AssistantView } from './components/views/AssistantView';
import { NemotronModelView } from './components/views/NemotronModelView';
import { BillingView } from './components/views/BillingView';
import { PrivacyView } from './components/views/PrivacyView';
import { SettingsView } from './components/views/SettingsView';
import { DesignSystemView } from './components/views/DesignSystemView';
import { CareerDashboardView } from './components/views/CareerDashboardView';
import { SalaryCoachView } from './components/views/SalaryCoachView';
import { CareerGoalsView } from './components/views/CareerGoalsView';
import { CareerTrajectoryView } from './components/views/CareerTrajectoryView';
import { MemoryView } from './components/views/MemoryView';
import { ProjectsView } from './components/views/ProjectsView';
import { TrustCenterView } from './components/views/TrustCenterView';
import { AssistantProfileView } from './components/views/AssistantProfileView';
import { AgentActivityView } from './components/views/AgentActivityView';
import { VoiceConversationModal } from './components/voice/VoiceConversationModal';
import { VoiceWorkspaceView } from './components/voice/VoiceWorkspaceView';
import { PersonalizationView } from './components/personalization/PersonalizationView';
import { RoutineManagerView } from './components/routines/RoutineManagerView';
import { CrossDomainWorkflowView } from './components/views/CrossDomainWorkflowView';
import { GlobalCommandBar } from './components/common/GlobalCommandBar';
import { IntelligenceDebugPanel } from './components/debug/IntelligenceDebugPanel';
import { AdminControlPanelView } from './components/admin/AdminControlPanelView';
import { LegalView } from './components/views/LegalView';
import { BetaOnboardingModal } from './components/beta/BetaOnboardingModal';
import { BetaFeedbackModal } from './components/beta/BetaFeedbackModal';

// Toast icons
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

export function AppContent() {
  const { activeSection, experienceMode, toasts, removeToast } = useApp();
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false);

  const renderActiveExperienceView = () => {
    if (activeSection === 'admin') {
      return <AdminControlPanelView />;
    }

    // 1. SIGNATURE: Editorial + Executive + Calm
    if (experienceMode === 'signature') {
      switch (activeSection) {
        case 'home':
          return <SignatureHome />;
        case 'dashboard':
          return <CareerDashboardView />;
        case 'memory':
          return <MemoryView />;
        case 'projects':
          return <ProjectsView />;
        case 'trust':
          return <TrustCenterView />;
        case 'profile':
          return <AssistantProfileView />;
        case 'agents':
          return <AgentActivityView />;
        case 'resumes':
          return <SignatureResume />;
        case 'applications':
          return <SignatureApplications />;
        case 'interviews':
          return <SignatureInterviews />;
        case 'tailor':
          return <TailoringView />;
        case 'salary':
          return <SalaryCoachView />;
        case 'goals':
          return <CareerGoalsView />;
        case 'trajectory':
          return <CareerTrajectoryView />;
        case 'career':
          return <CareerView />;
        case 'cover-letters':
          return <CoverLetterView />;
        case 'assistant':
          return <AssistantView />;
        case 'ai-models':
          return <NemotronModelView />;
        case 'billing':
          return <BillingView />;
        case 'privacy':
          return <PrivacyView />;
        case 'legal':
          return <LegalView />;
        case 'voice':
          return <VoiceWorkspaceView />;
        case 'personalization':
          return <PersonalizationView />;
        case 'routines':
          return <RoutineManagerView />;
        case 'cross-domain':
        case 'workflow':
          return <CrossDomainWorkflowView />;
        case 'settings':
          return <SettingsView />;
        case 'design-system':
          return <DesignSystemView />;
        default:
          return <SignatureHome />;
      }
    }

    // 2. FORGE: Technical IDE Workbench + Precision
    if (experienceMode === 'forge') {
      switch (activeSection) {
        case 'home':
          return <ForgeHome />;
        case 'dashboard':
          return <CareerDashboardView />;
        case 'memory':
          return <MemoryView />;
        case 'projects':
          return <ProjectsView />;
        case 'trust':
          return <TrustCenterView />;
        case 'profile':
          return <AssistantProfileView />;
        case 'agents':
          return <AgentActivityView />;
        case 'resumes':
        case 'tailor':
          return <ForgeResume />;
        case 'applications':
          return <ForgeApplications />;
        case 'interviews':
          return <ForgeInterviews />;
        case 'salary':
          return <SalaryCoachView />;
        case 'goals':
          return <CareerGoalsView />;
        case 'trajectory':
          return <CareerTrajectoryView />;
        case 'career':
          return <CareerView />;
        case 'cover-letters':
          return <CoverLetterView />;
        case 'assistant':
          return <AssistantView />;
        case 'ai-models':
          return <NemotronModelView />;
        case 'billing':
          return <BillingView />;
        case 'privacy':
          return <PrivacyView />;
        case 'voice':
          return <VoiceWorkspaceView />;
        case 'personalization':
          return <PersonalizationView />;
        case 'routines':
          return <RoutineManagerView />;
        case 'cross-domain':
        case 'workflow':
          return <CrossDomainWorkflowView />;
        case 'settings':
          return <SettingsView />;
        case 'design-system':
          return <DesignSystemView />;
        default:
          return <ForgeHome />;
      }
    }

    // 3. PULSE: Energy + Action + Momentum
    if (experienceMode === 'pulse') {
      switch (activeSection) {
        case 'home':
          return <PulseHome />;
        case 'dashboard':
          return <CareerDashboardView />;
        case 'memory':
          return <MemoryView />;
        case 'projects':
          return <ProjectsView />;
        case 'trust':
          return <TrustCenterView />;
        case 'profile':
          return <AssistantProfileView />;
        case 'agents':
          return <AgentActivityView />;
        case 'resumes':
        case 'tailor':
          return <PulseResume />;
        case 'applications':
          return <PulseApplications />;
        case 'interviews':
          return <PulseInterviews />;
        case 'salary':
          return <SalaryCoachView />;
        case 'goals':
          return <CareerGoalsView />;
        case 'trajectory':
          return <CareerTrajectoryView />;
        case 'career':
          return <CareerView />;
        case 'cover-letters':
          return <CoverLetterView />;
        case 'assistant':
          return <AssistantView />;
        case 'ai-models':
          return <NemotronModelView />;
        case 'billing':
          return <BillingView />;
        case 'privacy':
          return <PrivacyView />;
        case 'voice':
          return <VoiceWorkspaceView />;
        case 'personalization':
          return <PersonalizationView />;
        case 'routines':
          return <RoutineManagerView />;
        case 'cross-domain':
        case 'workflow':
          return <CrossDomainWorkflowView />;
        case 'settings':
          return <SettingsView />;
        case 'design-system':
          return <DesignSystemView />;
        default:
          return <PulseHome />;
      }
    }

    // 4. AURORA: Spatial + AI-Native + Immersive
    if (experienceMode === 'aurora') {
      switch (activeSection) {
        case 'home':
          return <AuroraHome />;
        case 'dashboard':
          return <CareerDashboardView />;
        case 'memory':
          return <MemoryView />;
        case 'projects':
          return <ProjectsView />;
        case 'trust':
          return <TrustCenterView />;
        case 'profile':
          return <AssistantProfileView />;
        case 'agents':
          return <AgentActivityView />;
        case 'resumes':
        case 'tailor':
          return <AuroraResume />;
        case 'applications':
          return <AuroraApplications />;
        case 'interviews':
          return <AuroraInterviews />;
        case 'salary':
          return <SalaryCoachView />;
        case 'goals':
          return <CareerGoalsView />;
        case 'trajectory':
          return <CareerTrajectoryView />;
        case 'career':
          return <CareerView />;
        case 'cover-letters':
          return <CoverLetterView />;
        case 'assistant':
          return <AssistantView />;
        case 'ai-models':
          return <NemotronModelView />;
        case 'billing':
          return <BillingView />;
        case 'privacy':
          return <PrivacyView />;
        case 'voice':
          return <VoiceWorkspaceView />;
        case 'personalization':
          return <PersonalizationView />;
        case 'routines':
          return <RoutineManagerView />;
        case 'cross-domain':
        case 'workflow':
          return <CrossDomainWorkflowView />;
        case 'settings':
          return <SettingsView />;
        case 'design-system':
          return <DesignSystemView />;
        default:
          return <AuroraHome />;
      }
    }

    return <SignatureHome />;
  };

  const renderShell = () => {
    const content = renderActiveExperienceView();

    switch (experienceMode) {
      case 'signature':
        return <SignatureShell>{content}</SignatureShell>;
      case 'forge':
        return <ForgeShell>{content}</ForgeShell>;
      case 'pulse':
        return <PulseShell>{content}</PulseShell>;
      case 'aurora':
        return <AuroraShell>{content}</AuroraShell>;
      default:
        return <SignatureShell>{content}</SignatureShell>;
    }
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden select-none">
      {/* Active Shell & Content */}
      <ErrorBoundary>
        {renderShell()}
      </ErrorBoundary>

      {/* Global AI Modals & Drawers */}
      <CommandPalette />
      <AIAssistantDrawer />
      <AIStatusPanel />
      <OnboardingModal />
      <BetaOnboardingModal />
      <VoiceConversationModal isOpen={isVoiceModalOpen} onClose={() => setIsVoiceModalOpen(false)} />

      {/* Global Toast Notifications Stack */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-sm w-full">
        {toasts.map((toast) => {
          const icons = {
            success: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />,
            warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />,
            error: <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />,
            info: <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          };

          return (
            <div
              key={toast.id}
              className="pointer-events-auto p-3 rounded-xl bg-[#161c2c] border border-[#2b354f] text-white shadow-2xl flex items-start gap-2.5 animate-in slide-in-from-bottom-2 fade-in duration-200"
            >
              {icons[toast.type]}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-white">
                  {toast.title}
                </div>
                {toast.message && (
                  <p className="text-[11px] text-[#94a3b8] mt-0.5 leading-tight">
                    {toast.message}
                  </p>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-[#64748b] hover:text-white p-0.5 rounded cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

import { EntitlementProvider } from './context/EntitlementContext';
import { UpgradeModal } from './components/common/UpgradeModal';
import { FloatingSaarthiUI } from './components/desktop/FloatingSaarthiUI';

export function App() {
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [isDesktopCompanionOpen, setIsDesktopCompanionOpen] = useState(false);

  // If launched with ?mode=floating or ?mode=desktop, render the dedicated floating desktop companion shell
  const isFloatingMode =
    typeof window !== 'undefined' &&
    (window.location.search.includes('mode=floating') ||
      window.location.search.includes('mode=desktop') ||
      window.location.hash.includes('floating'));

  if (isFloatingMode) {
    return (
      <div className="min-h-screen bg-slate-950/90 flex items-center justify-center p-4">
        <FloatingSaarthiUI standalone />
      </div>
    );
  }

  return (
    <EntitlementProvider>
      <AppContent />
      <UpgradeModal />
      <IntelligenceDebugPanel />
      <GlobalCommandBar />
      <VoiceConversationModal isOpen={isVoiceOpen} onClose={() => setIsVoiceOpen(false)} />
      {isDesktopCompanionOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <FloatingSaarthiUI onClose={() => setIsDesktopCompanionOpen(false)} />
        </div>
      )}
    </EntitlementProvider>
  );
}

export default App;
