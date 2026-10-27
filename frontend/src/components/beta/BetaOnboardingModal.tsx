import React, { useState, useEffect } from 'react';
import { Sparkles, Shield, Cpu, Zap, CheckCircle2, ArrowRight, X } from 'lucide-react';

interface BetaOnboardingModalProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function BetaOnboardingModal({ isOpen: overrideOpen, onClose }: BetaOnboardingModalProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (overrideOpen !== undefined) {
      setIsOpen(overrideOpen);
      return;
    }
    const hasSeenOnboarding = localStorage.getItem('saarthi_beta_onboarded_v050');
    if (!hasSeenOnboarding) {
      setIsOpen(true);
    }
  }, [overrideOpen]);

  const handleDismiss = () => {
    localStorage.setItem('saarthi_beta_onboarded_v050', 'true');
    setIsOpen(false);
    if (onClose) onClose();
  };

  if (!isOpen) return null;

  const slides = [
    {
      title: "Welcome to Saarthi External Public Beta",
      subtitle: "Your Universal AI Operating Companion",
      description: "Saarthi integrates memory, tools, routines, career intelligence, and multi-modal voice into one unified companion running on your local device.",
      icon: Sparkles,
      color: "from-amber-500 to-amber-600",
      badge: "V0.5.0-RC2 BETA"
    },
    {
      title: "100% Local Zero-Leak Privacy",
      subtitle: "Air-Gapped Local Memory & Data Security",
      description: "Your files, notes, credentials, and personal memory facts remain stored locally in SQLite database vaults. Zero data is sold or transmitted to third parties.",
      icon: Shield,
      color: "from-emerald-500 to-teal-600",
      badge: "PRIVACY GUARANTEED"
    },
    {
      title: "17 Autonomous Domain Packs & Hardware Engine",
      subtitle: "Adapts to Your Hardware (NVIDIA, AMD, Apple, CPU)",
      description: "From research to software engineering, career coaching to routine automation—Saarthi detects your system hardware and optimizes model execution automatically.",
      icon: Cpu,
      color: "from-cyan-500 to-blue-600",
      badge: "HARDWARE ADAPTIVE"
    }
  ];

  const currentSlide = slides[step];
  const Icon = currentSlide.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-950 border-b border-slate-800">
          <span className="px-2.5 py-0.5 text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full">
            {currentSlide.badge}
          </span>
          <button 
            onClick={handleDismiss}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Slide Body */}
        <div className="p-8 flex flex-col items-center text-center space-y-5">
          <div className={`p-4 rounded-2xl bg-gradient-to-br ${currentSlide.color} text-slate-950 shadow-xl shadow-amber-500/10`}>
            <Icon className="w-10 h-10" />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl font-extrabold text-slate-100">{currentSlide.title}</h3>
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider">{currentSlide.subtitle}</p>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed max-w-md">
            {currentSlide.description}
          </p>

          {/* Indicators */}
          <div className="flex items-center gap-1.5 pt-2">
            {slides.map((_, i) => (
              <div 
                key={i} 
                className={`h-1.5 rounded-full transition-all ${i === step ? 'w-6 bg-amber-400' : 'w-1.5 bg-slate-700'}`} 
              />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-950 border-t border-slate-800">
          <button
            onClick={handleDismiss}
            className="text-xs text-slate-400 hover:text-slate-200 font-semibold px-3 py-2"
          >
            Skip Tour
          </button>

          {step < slides.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl shadow-lg transition"
            >
              <span>Next</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleDismiss}
              className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Get Started with Saarthi</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
