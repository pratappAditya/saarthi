import React, { useState } from "react";
import confetti from "canvas-confetti";
import {
  Sparkles,
  Key,
  FileText,
  Target,
  FileSearch,
  Bot,
  UserCheck,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { SaarthiOrb } from "../common/SaarthiOrb";

interface FirstRunOnboardingProps {
  open: boolean;
  onComplete: () => void;
}

export const FirstRunOnboarding: React.FC<FirstRunOnboardingProps> = ({
  open,
  onComplete,
}) => {
  const [step, setStep] = useState(1);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [jobDescription, setJobDescription] = useState("");
  const [resumeUploaded, setResumeUploaded] = useState(false);

  if (!open) return null;

  const nextStep = () => {
    if (step < 5) {
      setStep(step + 1);
    } else {
      confetti({
        particleCount: 90,
        spread: 70,
        origin: { y: 0.6 },
        colors: ["#f59e0b", "#fbbf24", "#38bdf8"],
      });
      onComplete();
    }
  };

  const steps = [
    {
      step: 1,
      tag: "STEP 1 OF 5 • ACTIVATION & LICENSING",
      title: "Activate Your Saarthi License",
      subtitle: "Ed25519 Hardware-Bound License Active",
      icon: Key,
      render: () => (
        <div className="space-y-3 text-left w-full max-w-md bg-[#141414] p-4 rounded-2xl border border-white/10">
          <div className="flex items-center justify-between text-xs font-mono text-white/60">
            <span>LICENSE KEY</span>
            <span className="text-emerald-400 font-bold">VERIFIED</span>
          </div>
          <div className="text-sm font-mono text-[#F59E0B] bg-black/40 p-2.5 rounded-xl border border-white/5">
            SAARTHI-STU-8F392A11BC09
          </div>
          <p className="text-xs text-white/60">
            Bound to device fingerprint. Valid for Student Plan (₹149/mo). All job search data stored locally on your PC.
          </p>
        </div>
      ),
    },
    {
      step: 2,
      tag: "STEP 2 OF 5 • RESUME & TARGET ROLE",
      title: "Import Resume & Target Role",
      subtitle: "Build your baseline career profile",
      icon: FileText,
      render: () => (
        <div className="space-y-3 text-left w-full max-w-md">
          <div>
            <label className="block text-xs font-mono text-white/70 mb-1">Target Job Role</label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#141414] border border-white/10 text-white text-xs focus:outline-none focus:border-[#F59E0B]"
              placeholder="e.g. Full Stack Developer, Data Analyst"
            />
          </div>
          <div>
            <label className="block text-xs font-mono text-white/70 mb-1">Resume Document</label>
            <button
              onClick={() => setResumeUploaded(true)}
              className={`w-full py-3 rounded-xl border border-dashed text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
                resumeUploaded
                  ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-400"
                  : "bg-[#141414] border-white/20 text-white/70 hover:border-[#F59E0B]"
              }`}
            >
              <FileText size={16} />
              <span>{resumeUploaded ? "Resume Imported (Suresh_Mistry_CV.pdf)" : "Click to Upload PDF/Word Resume"}</span>
            </button>
          </div>
        </div>
      ),
    },
    {
      step: 3,
      tag: "STEP 3 OF 5 • ATS MATCH & TAILORING",
      title: "Paste Job Description & ATS Analysis",
      subtitle: "Extract key requirements & calculate match score",
      icon: FileSearch,
      render: () => (
        <div className="space-y-3 text-left w-full max-w-md">
          <div>
            <label className="block text-xs font-mono text-white/70 mb-1">Paste Job Description (JD)</label>
            <textarea
              rows={3}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste job requirements here to run ATS score matching..."
              className="w-full px-3.5 py-2 rounded-xl bg-[#141414] border border-white/10 text-white text-xs focus:outline-none focus:border-[#F59E0B]"
            />
          </div>
          <div className="p-3 rounded-xl bg-[#17140D] border border-[#F59E0B]/30 flex items-center justify-between text-xs font-mono">
            <span className="text-white/70">Estimated ATS Score:</span>
            <span className="text-[#F59E0B] font-bold">88% Match</span>
          </div>
        </div>
      ),
    },
    {
      step: 4,
      tag: "STEP 4 OF 5 • BROWSER ASSISTANT SAFETY",
      title: "Browser Assistant & User Review",
      subtitle: "Safe auto-fill with 100% explicit user confirmation",
      icon: Bot,
      render: () => (
        <div className="space-y-3 text-left w-full max-w-md bg-[#141414] p-4 rounded-2xl border border-white/10">
          <div className="flex items-center gap-2 text-xs font-mono text-[#F59E0B]">
            <ShieldCheck size={16} />
            <span>SAFETY INVARIANTS ENFORCED</span>
          </div>
          <ul className="space-y-1.5 text-xs text-white/70">
            <li className="flex items-center gap-2"><CheckCircle2 size={13} className="text-emerald-400"/> Detect form fields on target portal</li>
            <li className="flex items-center gap-2"><CheckCircle2 size={13} className="text-emerald-400"/> Suggest matching values from stored profile</li>
            <li className="flex items-center gap-2"><CheckCircle2 size={13} className="text-emerald-400"/> Require explicit user confirmation before fill</li>
            <li className="flex items-center gap-2"><CheckCircle2 size={13} className="text-emerald-400"/> 0 autonomous application submissions</li>
          </ul>
        </div>
      ),
    },
    {
      step: 5,
      tag: "STEP 5 OF 5 • FIRST APPLICATION READY",
      title: "Launch First Application Workflow",
      subtitle: "Ready to complete and track your first job application",
      icon: UserCheck,
      render: () => (
        <div className="space-y-3 text-center w-full max-w-md bg-[#17140D] p-5 rounded-2xl border border-[#F59E0B]/40">
          <CheckCircle2 className="mx-auto text-[#F59E0B]" size={36} />
          <h4 className="text-sm font-bold text-white">First Application Ready</h4>
          <p className="text-xs text-white/70">
            Your tailored resume and cover letter are saved to your local career workspace. Open Career Tracker to submit and log status.
          </p>
        </div>
      ),
    },
  ];

  const current = steps[step - 1];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl animate-fade-in select-none">
      <div className="relative w-full max-w-lg p-8 rounded-3xl bg-[#0D0D0D] border border-[#F59E0B]/40 shadow-[0_0_80px_rgba(245,158,11,0.25)] flex flex-col items-center text-center space-y-6">
        {/* Step Indicator Pills */}
        <div className="flex items-center gap-1.5">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all ${
                i === step
                  ? "w-8 bg-[#F59E0B] shadow-[0_0_10px_#f59e0b]"
                  : i < step
                  ? "w-3 bg-[#F59E0B]/40"
                  : "w-3 bg-white/10"
              }`}
            />
          ))}
        </div>

        {/* Saarthi Orb Graphic */}
        <SaarthiOrb state="idle" size="md" />

        {/* Text Header */}
        <div className="space-y-1">
          <span className="px-3 py-0.5 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[10px] font-mono font-semibold text-[#F59E0B] uppercase tracking-wider">
            {current.tag}
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight pt-1">
            {current.title}
          </h2>
          <p className="text-xs text-white/60">{current.subtitle}</p>
        </div>

        {/* Dynamic Interactive Body */}
        {current.render()}

        {/* Action Button */}
        <div className="w-full space-y-2">
          <button
            onClick={nextStep}
            className="w-full py-3 rounded-2xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-[0_0_25px_rgba(245,158,11,0.4)] cursor-pointer"
          >
            <span>{step === 5 ? "Complete & Open Career Workspace" : "Continue"}</span>
            <ArrowRight size={16} />
          </button>
          {step < 5 && (
            <button
              onClick={onComplete}
              className="text-xs text-white/40 hover:text-white/70 transition-colors py-1 cursor-pointer"
            >
              Skip setup
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
