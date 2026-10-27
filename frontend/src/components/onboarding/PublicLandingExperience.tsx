import React, { useState } from "react";
import {
  ShieldCheck,
  Zap,
  Lock,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  FileText,
  FileSearch,
  CheckSquare,
  Bot,
  UserCheck,
  XCircle,
  Clock,
} from "lucide-react";

interface PublicLandingExperienceProps {
  open: boolean;
  onClose: () => void;
  onStartOnboarding: () => void;
}

export const PublicLandingExperience: React.FC<PublicLandingExperienceProps> = ({
  open,
  onClose,
  onStartOnboarding,
}) => {
  const [selectedTier, setSelectedTier] = useState<"student" | "personal">("student");

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl animate-fade-in select-none overflow-y-auto">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 md:p-8 rounded-3xl bg-[#0D0D0D] border border-[#F59E0B]/40 shadow-[0_0_80px_rgba(245,158,11,0.25)] flex flex-col space-y-8">
        {/* Header Badge & Title */}
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-xs font-mono font-semibold text-[#F59E0B] uppercase tracking-wider">
            <Sparkles size={14} /> PUBLIC BETA AVAILABLE NOW
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Apply to jobs faster with an AI career assistant that keeps your job-search data on your PC.
          </h1>
          <p className="text-sm md:text-base text-white/70">
            Saarthi helps students and job seekers tailor resumes, pass ATS filters, draft cover letters, and fill job applications safely while keeping all your sensitive personal data 100% private on your computer.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-2xl bg-[#141414] border border-white/10 space-y-2">
            <div className="w-8 h-8 rounded-xl bg-[#F59E0B]/10 text-[#F59E0B] flex items-center justify-center">
              <FileSearch size={18} />
            </div>
            <h3 className="text-sm font-bold text-white">Instant ATS Analysis</h3>
            <p className="text-xs text-white/60">
              Match your resume against job descriptions, fix keyword gaps, and score 85%+ on recruiter ATS filters.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#141414] border border-white/10 space-y-2">
            <div className="w-8 h-8 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <Bot size={18} />
            </div>
            <h3 className="text-sm font-bold text-white">Browser Assistant Safety</h3>
            <p className="text-xs text-white/60">
              Auto-populates job forms with 100% explicit user review and confirmation before submission. Zero auto-submits.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#141414] border border-white/10 space-y-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Lock size={18} />
            </div>
            <h3 className="text-sm font-bold text-white">100% PC Privacy</h3>
            <p className="text-xs text-white/60">
              Your resume, cover letters, and job search history never leave your computer or get sold to third parties.
            </p>
          </div>
        </div>

        {/* Browser Assistant Invariants Banner */}
        <div className="p-4 rounded-2xl bg-[#17140D] border border-[#F59E0B]/30 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <ShieldCheck className="text-[#F59E0B] shrink-0" size={28} />
            <div>
              <h4 className="text-xs font-mono font-bold uppercase text-[#F59E0B] tracking-wider">
                SAFETY GUARANTEE: YOU ARE IN FULL CONTROL
              </h4>
              <p className="text-xs text-white/80">
                Detect → Suggest → User Review → Explicit Confirmation → Fill → User Submits.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-white/60">
            <span className="flex items-center gap-1 text-emerald-400"><CheckCircle2 size={12}/> 100% User Confirmation</span>
            <span className="flex items-center gap-1 text-rose-400"><XCircle size={12}/> 0 Auto-Submissions</span>
          </div>
        </div>

        {/* Pricing Tiers */}
        <div className="space-y-3">
          <h3 className="text-sm font-mono uppercase tracking-wider text-white/50 text-center">
            Transparent Pricing for Job Seekers
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
            {/* Student Plan */}
            <div
              onClick={() => setSelectedTier("student")}
              className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between space-y-4 ${
                selectedTier === "student"
                  ? "bg-[#1A160A] border-[#F59E0B] shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                  : "bg-[#141414] border-white/10 hover:border-white/20"
              }`}
            >
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-mono uppercase bg-[#F59E0B]/20 text-[#F59E0B] px-2 py-0.5 rounded font-bold">
                      POPULAR FOR STUDENTS
                    </span>
                    <h4 className="text-lg font-bold text-white mt-1">Student Plan</h4>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold text-white">₹149</span>
                    <span className="text-xs text-white/50">/month</span>
                    <div className="text-[10px] text-[#F59E0B]">₹1,299/year (Save 27%)</div>
                  </div>
                </div>
                <ul className="mt-3 space-y-1.5 text-xs text-white/70">
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-[#F59E0B]" /> Unlimited ATS Resume Tailoring</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-[#F59E0B]" /> Unlimited Job Cover Letter Generator</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-[#F59E0B]" /> Safe Browser Assistant Auto-fill</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-[#F59E0B]" /> 100% PC Local Processing</li>
                </ul>
              </div>
            </div>

            {/* Personal Plan */}
            <div
              onClick={() => setSelectedTier("personal")}
              className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between space-y-4 ${
                selectedTier === "personal"
                  ? "bg-[#1A160A] border-[#F59E0B] shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                  : "bg-[#141414] border-white/10 hover:border-white/20"
              }`}
            >
              <div>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-mono uppercase bg-sky-500/20 text-sky-400 px-2 py-0.5 rounded font-bold">
                      FOR PROFESSIONALS
                    </span>
                    <h4 className="text-lg font-bold text-white mt-1">Personal Plan</h4>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold text-white">₹399</span>
                    <span className="text-xs text-white/50">/month</span>
                    <div className="text-[10px] text-sky-400">₹3,499/year (Save 27%)</div>
                  </div>
                </div>
                <ul className="mt-3 space-y-1.5 text-xs text-white/70">
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-sky-400" /> Everything in Student Plan</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-sky-400" /> Priority Support & Fast Updates</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-sky-400" /> Advanced Interview STAR Prep</li>
                  <li className="flex items-center gap-1.5"><CheckCircle2 size={13} className="text-sky-400" /> Multi-device desktop sync (2 PCs)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <button
            onClick={() => {
              onClose();
              onStartOnboarding();
            }}
            className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-[0_0_25px_rgba(245,158,11,0.4)] cursor-pointer"
          >
            <span>Start First-Application Setup</span>
            <ArrowRight size={16} />
          </button>
          <button
            onClick={onClose}
            className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-white/5 hover:bg-white/10 text-white/70 text-sm font-semibold transition-all cursor-pointer"
          >
            Explore Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};
