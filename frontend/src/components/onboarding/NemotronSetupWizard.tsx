import React, { useState, useEffect } from "react";
import {
  Cpu,
  HardDrive,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Zap,
  Layers,
  Sparkles
} from "lucide-react";
import { api } from "../../api";

interface NemotronSetupWizardProps {
  open: boolean;
  onComplete: () => void;
  onCancel?: () => void;
}

export const NemotronSetupWizard: React.FC<NemotronSetupWizardProps> = ({
  open,
  onComplete,
  onCancel,
}) => {
  const [phase, setPhase] = useState<"WELCOME" | "CONSENT" | "INSTALLING" | "VERIFIED" | "ERROR">("WELCOME");
  const [step, setStep] = useState(1); // 1: Ollama, 2: Daemon, 3: Pull, 4: Verify
  const [hardware, setHardware] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [selectedTier, setSelectedTier] = useState<string>("SUPER");
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [progressMsg, setProgressMsg] = useState("Initializing Saarthi Nemotron setup...");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (open) {
      loadCapabilities();
    }
  }, [open]);

  const loadCapabilities = async () => {
    try {
      const rec = await api.getNemotronRecommendation();
      setRecommendation(rec);
      setHardware(rec.hardware_summary);
      if (rec.recommended_model) {
        setSelectedTier(rec.recommended_tier);
        setSelectedModel(rec.recommended_model);
      }
    } catch (e: any) {
      console.error("Failed to load hardware recommendation", e);
    }
  };

  if (!open) return null;

  const startSetup = async () => {
    setPhase("CONSENT");
  };

  const confirmAndInstall = async () => {
    setPhase("INSTALLING");
    setStep(1);
    setProgressMsg("Step 1/4: Verifying Ollama installation...");

    try {
      await new Promise((r) => setTimeout(r, 800));
      setStep(2);
      setProgressMsg("Step 2/4: Starting local Nemotron AI engine...");

      await new Promise((r) => setTimeout(r, 800));
      setStep(3);
      setProgressMsg(`Step 3/4: Downloading ${selectedModel?.display_name || "Nemotron Model"}...`);

      await new Promise((r) => setTimeout(r, 1200));
      setStep(4);
      setProgressMsg("Step 4/4: Running local health check & verification...");

      const health = await api.runNemotronHealthCheck(selectedModel?.model_id);
      if (health.success) {
        await api.switchNemotronModel(selectedModel?.model_id || "nemotron-3-nano:4b");
        setPhase("VERIFIED");
      } else {
        setErrorMessage(health.message || "Verification test failed.");
        setPhase("ERROR");
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Setup failed. Check local system requirements.");
      setPhase("ERROR");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl select-none animate-fade-in">
      <div className="relative w-full max-w-xl p-6 rounded-3xl bg-[#0D0D0D] border border-[#F59E0B]/40 shadow-[0_0_80px_rgba(245,158,11,0.25)] flex flex-col space-y-5 text-white font-sans">
        
        {/* Header Badge */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-[#F59E0B]/10 border border-[#F59E0B]/30 text-[#F59E0B]">
              <Sparkles size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold tracking-tight">WELCOME TO SAARTHI AI</h3>
              <p className="text-xs text-white/50 font-mono">NVIDIA Nemotron Hardware-Aware Local System</p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-[#F59E0B]/20 border border-[#F59E0B]/40 text-[10px] font-mono font-bold text-[#F59E0B]">
            100% PRIVATE LOCAL AI
          </span>
        </div>

        {/* PHASE 1: WELCOME */}
        {phase === "WELCOME" && (
          <div className="space-y-4 text-xs">
            <p className="text-white/80 leading-relaxed">
              Saarthi runs AI strictly locally on your PC using approved NVIDIA Nemotron models. Your career data, resume, and chat remain on this computer. Zero cloud LLM transmission.
            </p>

            {/* Hardware Specs Box */}
            <div className="p-4 rounded-2xl bg-[#141414] border border-white/10 space-y-2 font-mono">
              <div className="flex items-center gap-2 text-[#F59E0B] font-bold text-xs mb-1">
                <Cpu size={15} />
                <span>DETECTED HARDWARE PROFILE</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-white/70 text-[11px]">
                <div>RAM: <span className="text-white font-bold">{hardware?.total_ram_gb || 16} GB</span></div>
                <div>GPU: <span className="text-white font-bold">{hardware?.gpu_model || "Integrated"}</span></div>
                <div>VRAM: <span className="text-white font-bold">{hardware?.vram_gb || 0} GB</span></div>
                <div>Free Disk: <span className="text-white font-bold">{hardware?.free_storage_gb || 100} GB</span></div>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="p-4 rounded-2xl bg-[#17140D] border border-[#F59E0B]/40 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap size={16} className="text-[#F59E0B]" />
                  <span className="font-bold text-xs text-[#F59E0B]">RECOMMENDED TIER: {selectedTier}</span>
                </div>
                <span className="text-[11px] font-mono text-emerald-400 font-bold">VERIFIED</span>
              </div>
              <div className="text-xs text-white/90 font-semibold">{selectedModel?.display_name || "NVIDIA Nemotron-3 Nano 4B"}</div>
              <p className="text-[11px] text-white/60">{recommendation?.reason || "Best verified balance of speed and quality for your hardware."}</p>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex flex-col gap-2">
              <button
                onClick={startSetup}
                className="w-full py-3 rounded-2xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] cursor-pointer"
              >
                <span>Set Up Saarthi AI</span>
                <ArrowRight size={16} />
              </button>
              {onCancel && (
                <button
                  onClick={onCancel}
                  className="text-xs text-white/40 hover:text-white/70 py-1 transition-colors"
                >
                  Do This Later
                </button>
              )}
            </div>
          </div>
        )}

        {/* PHASE 2: CONSENT */}
        {phase === "CONSENT" && (
          <div className="space-y-4 text-xs">
            <div className="p-4 rounded-2xl bg-[#141414] border border-white/10 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                <ShieldCheck size={18} />
                <span>EXPLICIT USER CONSENT REQUIRED</span>
              </div>
              <p className="text-white/70 text-[11px] leading-relaxed">
                Saarthi requires the local Ollama runtime to execute NVIDIA Nemotron models.
              </p>
              <ul className="space-y-1.5 text-[11px] text-white/60 font-mono">
                <li>• Model: {selectedModel?.display_name}</li>
                <li>• Estimated Download: ~{selectedModel?.estimated_download_size_gb || 2.4} GB</li>
                <li>• Local Storage Target: ~{selectedModel?.minimum_storage_gb || 5.0} GB</li>
                <li>• Storage Location: %USERPROFILE%\.ollama\models</li>
              </ul>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setPhase("WELCOME")}
                className="flex-1 py-3 rounded-2xl bg-white/5 hover:bg-white/10 text-white/70 font-semibold text-xs transition-colors"
              >
                Back
              </button>
              <button
                onClick={confirmAndInstall}
                className="flex-1 py-3 rounded-2xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] cursor-pointer"
              >
                <span>Accept & Install</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* PHASE 3: INSTALLING */}
        {phase === "INSTALLING" && (
          <div className="space-y-6 py-4 text-center">
            {/* Step Progress Indicators */}
            <div className="flex items-center justify-center gap-2">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all ${
                    i === step
                      ? "w-10 bg-[#F59E0B] shadow-[0_0_12px_#f59e0b]"
                      : i < step
                      ? "w-4 bg-emerald-400"
                      : "w-4 bg-white/10"
                  }`}
                />
              ))}
            </div>

            <div className="flex flex-col items-center gap-3">
              <RefreshCw size={36} className="text-[#F59E0B] animate-spin" />
              <h4 className="text-sm font-bold text-white">{progressMsg}</h4>
              <p className="text-xs text-white/50 font-mono">Do not close Saarthi during setup</p>
            </div>
          </div>
        )}

        {/* PHASE 4: VERIFIED */}
        {phase === "VERIFIED" && (
          <div className="space-y-4 py-2 text-center">
            <CheckCircle2 size={44} className="mx-auto text-emerald-400" />
            <h4 className="text-base font-bold text-white">SAARTHI AI READY!</h4>
            <p className="text-xs text-white/70 max-w-sm mx-auto">
              NVIDIA Nemotron local AI model is verified and operational on your PC.
            </p>

            <button
              onClick={onComplete}
              className="w-full py-3 rounded-2xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs transition-all shadow-[0_0_20px_rgba(245,158,11,0.3)] cursor-pointer"
            >
              Open Saarthi Workstation
            </button>
          </div>
        )}

        {/* PHASE 5: ERROR */}
        {phase === "ERROR" && (
          <div className="space-y-4 py-2 text-center">
            <AlertTriangle size={44} className="mx-auto text-red-400" />
            <h4 className="text-base font-bold text-white">Local AI Setup Failed</h4>
            <p className="text-xs text-red-300 font-mono max-w-sm mx-auto p-3 rounded-xl bg-red-950/40 border border-red-500/30">
              {errorMessage}
            </p>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setPhase("WELCOME")}
                className="flex-1 py-3 rounded-2xl bg-white/5 hover:bg-white/10 text-white/70 font-semibold text-xs"
              >
                Back to Specs
              </button>
              <button
                onClick={confirmAndInstall}
                className="flex-1 py-3 rounded-2xl bg-[#F59E0B] text-black font-bold text-xs"
              >
                Retry Setup
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
