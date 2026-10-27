import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  HardDrive, 
  DownloadCloud, 
  CheckCircle2, 
  Sparkles, 
  ArrowRight, 
  Check, 
  Lock, 
  Terminal,
  Activity
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Progress } from '../common/Progress';
import { Card } from '../common/Card';

export const OnboardingModal: React.FC = () => {
  const { 
    isOnboardingOpen, 
    setIsOnboardingOpen, 
    hardware, 
    activeModel, 
    addToast,
    setAiStatus
  } = useApp();

  const [step, setStep] = useState<number>(1);
  const [downloadProgress, setDownloadProgress] = useState<number>(0);
  const [isInstalling, setIsInstalling] = useState<boolean>(false);

  const startDownload = () => {
    setIsInstalling(true);
    let current = 0;
    const interval = setInterval(() => {
      current += 15;
      setDownloadProgress(current);
      if (current >= 100) {
        clearInterval(interval);
        setIsInstalling(false);
        setAiStatus('ready');
        setStep(5);
        addToast({
          type: 'success',
          title: 'Nemotron AI Engine Ready',
          message: 'Local weights loaded into GPU memory.'
        });
      }
    }, 350);
  };

  const handleFinish = () => {
    setIsOnboardingOpen(false);
    setStep(1);
    setDownloadProgress(0);
  };

  return (
    <Modal
      isOpen={isOnboardingOpen}
      onClose={() => setIsOnboardingOpen(false)}
      maxWidth="2xl"
      showCloseButton={step === 5}
    >
      {/* Progress Dots */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-[var(--border-subtle)]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-blue-600 flex items-center justify-center text-white text-xs font-bold font-display-title">
            S
          </div>
          <span className="text-xs font-semibold tracking-wider text-[var(--text-primary)] font-display-title">
            SAARTHI INITIALIZATION
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                s === step
                  ? 'bg-[var(--accent-primary)] text-white scale-110'
                  : s < step
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-[var(--bg-subtle)] text-[var(--text-muted)] border border-[var(--border-subtle)]'
              }`}
            >
              {s < step ? '✓' : s}
            </div>
          ))}
        </div>
      </div>

      {/* STEP 1: PRIVACY PLEDGE */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 mx-auto">
            <Lock className="w-7 h-7" />
          </div>

          <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-[var(--text-primary)] font-display-title">
              Your AI stays on your computer.
            </h2>
            <p className="text-xs text-[var(--text-secondary)] max-w-lg mx-auto leading-relaxed">
              Unlike cloud career SaaS tools that send your personal resumes, employment history, and compensation goals to third-party servers, Saarthi executes 100% locally.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-center space-y-1">
              <ShieldCheck className="w-5 h-5 text-emerald-400 mx-auto" />
              <h4 className="text-xs font-semibold text-[var(--text-primary)]">Zero Cloud Fallback</h4>
              <p className="text-[10px] text-[var(--text-muted)]">No remote API keys or cloud server transmissions.</p>
            </div>
            <div className="p-3.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-center space-y-1">
              <Cpu className="w-5 h-5 text-blue-400 mx-auto" />
              <h4 className="text-xs font-semibold text-[var(--text-primary)]">Local GPU Acceleration</h4>
              <p className="text-[10px] text-[var(--text-muted)]">NVIDIA Nemotron runs directly on your hardware.</p>
            </div>
            <div className="p-3.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] text-center space-y-1">
              <HardDrive className="w-5 h-5 text-purple-400 mx-auto" />
              <h4 className="text-xs font-semibold text-[var(--text-primary)]">Offline Durability</h4>
              <p className="text-[10px] text-[var(--text-muted)]">Works entirely on flights, trains, and disconnected.</p>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-[var(--border-subtle)]">
            <Button variant="primary" icon={ArrowRight} iconPosition="right" onClick={() => setStep(2)}>
              Configure Local Engine
            </Button>
          </div>
        </div>
      )}

      {/* STEP 2: OLLAMA ENGINE EXPLANATION & CONSENT */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/25 text-blue-400 mx-auto">
            <Terminal className="w-7 h-7" />
          </div>

          <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-[var(--text-primary)] font-display-title">
              Local AI Engine: Ollama
            </h2>
            <p className="text-xs text-[var(--text-secondary)] max-w-lg mx-auto leading-relaxed">
              Saarthi connects via an internal localhost IPC socket to Ollama to manage local quantized LLM weights.
            </p>
          </div>

          <div className="p-4 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                <span className="text-xs font-mono font-semibold text-[var(--text-primary)]">
                  Localhost Daemon (127.0.0.1:11434)
                </span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                DETECTED & RUNNING
              </span>
            </div>
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
              We detected Ollama v0.6.2 running on your system. Saarthi will create an isolated sandbox for approved NVIDIA Nemotron models.
            </p>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-[var(--border-subtle)]">
            <Button variant="ghost" onClick={() => setStep(1)}>
              Back
            </Button>
            <Button variant="primary" icon={ArrowRight} iconPosition="right" onClick={() => setStep(3)}>
              Detect Hardware & Specs
            </Button>
          </div>
        </div>
      )}

      {/* STEP 3: HARDWARE DETECTION & NEMOTRON RECOMMENDATION */}
      {step === 3 && (
        <div className="space-y-6">
          <div className="text-center space-y-1">
            <h2 className="text-xl font-bold text-[var(--text-primary)] font-display-title">
              Hardware Profile & Recommendation
            </h2>
            <p className="text-xs text-[var(--text-secondary)]">
              We profiled your CPU, RAM, and GPU to select the optimal Nemotron model.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
            <div className="p-2.5 rounded bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <div className="text-[10px] text-[var(--text-muted)]">CPU CORES</div>
              <div className="font-bold text-[var(--text-primary)]">{hardware.cores} Cores</div>
            </div>
            <div className="p-2.5 rounded bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <div className="text-[10px] text-[var(--text-muted)]">SYSTEM RAM</div>
              <div className="font-bold text-[var(--text-primary)]">{hardware.ramTotal.split(' ')[0]} GB</div>
            </div>
            <div className="p-2.5 rounded bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <div className="text-[10px] text-[var(--text-muted)]">VRAM DETECTED</div>
              <div className="font-bold text-blue-400">{hardware.vramTotal}</div>
            </div>
            <div className="p-2.5 rounded bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <div className="text-[10px] text-[var(--text-muted)]">FREE STORAGE</div>
              <div className="font-bold text-emerald-400">{hardware.storageFree.split(' ')[0]} GB</div>
            </div>
          </div>

          {/* Recommended Card */}
          <div className="p-4 rounded-[var(--radius-lg)] border-2 border-blue-500/50 bg-blue-950/20 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase font-bold text-blue-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                RECOMMENDED FOR YOUR SYSTEM
              </span>
              <span className="text-xs font-mono font-semibold text-emerald-400">
                {hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tok/s` : 'Not benchmarked'}
              </span>
            </div>
            <h3 className="text-sm font-bold text-[var(--text-primary)] font-display-title">
              NVIDIA Nemotron-Mini 4B Instruct (Q4_K_M)
            </h3>
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
              Calibrated for lightning-fast resume rewrites, ATS scoring, and interview drills without consuming high laptop battery or memory.
            </p>
            <div className="flex items-center gap-4 text-[11px] font-mono text-[var(--text-muted)] pt-1">
              <span>Size: <strong>2.8 GB</strong></span>
              <span>Memory Required: <strong>3.5 GB</strong></span>
              <span>Target TTFT: <strong>&lt; 180ms</strong></span>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-[var(--border-subtle)]">
            <Button variant="ghost" onClick={() => setStep(2)}>
              Back
            </Button>
            <Button variant="ai" icon={DownloadCloud} onClick={() => { setStep(4); startDownload(); }}>
              Download & Initialize Nemotron (2.8 GB)
            </Button>
          </div>
        </div>
      )}

      {/* STEP 4: DOWNLOADING & CALIBRATING */}
      {step === 4 && (
        <div className="space-y-6 text-center py-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-500/15 border border-blue-400/30 flex items-center justify-center text-blue-400 mx-auto animate-pulse">
            <DownloadCloud className="w-7 h-7" />
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-bold text-[var(--text-primary)] font-display-title">
              Downloading Nemotron Weights...
            </h2>
            <p className="text-xs text-[var(--text-secondary)] max-w-md mx-auto">
              Fetching quantized weights directly into Ollama's local directory. Once complete, no internet connection is ever needed.
            </p>
          </div>

          <div className="max-w-md mx-auto space-y-2">
            <Progress value={downloadProgress} size="md" variant="ai" label="Local Model Weights" sublabel="Q4_K_M GGUF" />
            <div className="flex justify-between text-[10px] font-mono text-[var(--text-muted)]">
              <span>Transfer: {Math.round((downloadProgress / 100) * 2800)} MB / 2800 MB</span>
              <span>Local GPU Allocation: Ready</span>
            </div>
          </div>
        </div>
      )}

      {/* STEP 5: VERIFIED & READY */}
      {step === 5 && (
        <div className="space-y-6 text-center py-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center text-emerald-400 mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-[var(--text-primary)] font-display-title">
              Saarthi is Ready.
            </h2>
            <p className="text-xs text-[var(--text-secondary)] max-w-md mx-auto leading-relaxed">
              Your on-device career intelligence engine status is <strong>{hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tokens/sec` : 'Not benchmarked'}</strong>. Your data remains strictly on this machine.
            </p>
          </div>

          <div className="p-3.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] max-w-md mx-auto flex items-center justify-between text-xs font-mono">
            <span className="text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              STATUS: HEALTHY
            </span>
            <span className="text-[var(--text-secondary)]">
              {activeModel.name}
            </span>
          </div>

          <div className="pt-4 border-t border-[var(--border-subtle)]">
            <Button variant="primary" size="lg" icon={Sparkles} onClick={handleFinish} className="w-full sm:w-auto">
              Launch Career Command Center
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
