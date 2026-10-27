import React, { useState } from 'react';
import { 
  Cpu, 
  HardDrive, 
  Activity, 
  Zap, 
  ShieldCheck, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  DownloadCloud,
  Terminal,
  ExternalLink,
  Power
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';
import { Drawer } from '../common/Drawer';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';

export const AIStatusPanel: React.FC = () => {
  const { 
    isAIStatusDrawerOpen, 
    setIsAIStatusDrawerOpen, 
    hardware, 
    setHardware, 
    nemotronModels, 
    activeModel, 
    setActiveModelById, 
    installModel, 
    addToast,
    aiStatus,
    setAiStatus
  } = useApp();

  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [benchmarkTokens, setBenchmarkTokens] = useState<number | null>(null);

  const runBenchmark = async () => {
    setIsBenchmarking(true);
    try {
      const res = await api.runBenchmark();
      if (res && res.is_benchmarked && typeof res.measured_tps === 'number') {
        setHardware(prev => ({
          ...prev,
          inferenceSpeed: res.measured_tps,
          isBenchmarked: true
        }));
        setBenchmarkTokens(res.measured_tps);
        addToast({
          type: 'success',
          title: 'Benchmark Complete',
          message: `Measured ${res.measured_tps} tokens/sec on active model.`
        });
      } else {
        addToast({
          type: 'error',
          title: 'Benchmark Failed',
          message: res.message || 'Could not reach local Ollama inference engine.'
        });
      }
    } catch {
      addToast({
        type: 'error',
        title: 'Benchmark Failed',
        message: 'Physical hardware benchmark error.'
      });
    } finally {
      setIsBenchmarking(false);
    }
  };

  const toggleEngineOnline = () => {
    if (hardware.ollamaRunning) {
      setHardware(prev => ({ ...prev, ollamaRunning: false, nemotronRunning: false }));
      setAiStatus('offline');
      addToast({
        type: 'warning',
        title: 'Local AI Engine Paused',
        message: 'Ollama local socket disconnected.'
      });
    } else {
      setHardware(prev => ({ ...prev, ollamaRunning: true, nemotronRunning: true }));
      setAiStatus('ready');
      addToast({
        type: 'success',
        title: 'Local AI Engine Connected',
        message: 'Ollama + Nemotron verified locally.'
      });
    }
  };

  return (
    <Drawer
      isOpen={isAIStatusDrawerOpen}
      onClose={() => setIsAIStatusDrawerOpen(false)}
      title={
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-emerald-500/15 text-emerald-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
              Local AI & Hardware Telemetry
            </h3>
            <p className="text-[11px] text-[var(--text-secondary)]">
              Ollama + NVIDIA Nemotron On-Device Architecture
            </p>
          </div>
        </div>
      }
      width="lg"
    >
      {/* Privacy Notice Card */}
      <div className="p-3.5 rounded-[var(--radius-md)] bg-emerald-950/20 border border-emerald-500/25 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs">
          <h4 className="font-semibold text-emerald-300">100% Zero-Cloud Transmission Policy</h4>
          <p className="text-emerald-300/80 text-[11px] mt-0.5 leading-relaxed">
            All resume parsing, ATS scoring, and interview simulations execute entirely within your local memory sandbox. No telemetry or embeddings ever leave this workstation.
          </p>
        </div>
      </div>

      {/* Engine Status & Toggle */}
      <Card variant="subtle" padding="sm" className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${hardware.ollamaRunning ? 'bg-emerald-400 animate-pulse' : 'bg-neutral-500'}`} />
            <div>
              <div className="text-xs font-semibold text-[var(--text-primary)] font-mono">
                OLLAMA SOCKET: {hardware.ollamaRunning ? 'ACTIVE (127.0.0.1:11434)' : 'STOPPED'}
              </div>
              <div className="text-[10px] text-[var(--text-muted)] font-mono">
                Version: {hardware.ollamaVersion}
              </div>
            </div>
          </div>

          <Button 
            variant={hardware.ollamaRunning ? 'outline' : 'primary'} 
            size="xs"
            onClick={toggleEngineOnline}
            icon={Power}
          >
            {hardware.ollamaRunning ? 'Simulate Offline' : 'Restart Engine'}
          </Button>
        </div>

        {/* Live Hardware Gauges */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[var(--border-subtle)]">
          <div className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1.5">
            <div className="flex justify-between text-[11px] text-[var(--text-secondary)]">
              <span className="font-mono">VRAM Usage</span>
              <span className="font-mono text-blue-400 font-semibold">{hardware.vramUsage}%</span>
            </div>
            <Progress value={hardware.vramUsage} size="xs" variant="accent" showPercentage={false} />
            <div className="text-[10px] text-[var(--text-muted)] font-mono">
              {hardware.vramAvailable}
            </div>
          </div>

          <div className="p-2.5 rounded-[var(--radius-sm)] bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1.5">
            <div className="flex justify-between text-[11px] text-[var(--text-secondary)]">
              <span className="font-mono">GPU Load</span>
              <span className="font-mono text-emerald-400 font-semibold">{hardware.gpuLoad}%</span>
            </div>
            <Progress value={hardware.gpuLoad} size="xs" variant="success" showPercentage={false} />
            <div className="text-[10px] text-[var(--text-muted)] font-mono">
              Inference: {hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} t/s` : 'Not benchmarked'}
            </div>
          </div>
        </div>
      </Card>

      {/* System Hardware Breakdown */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider font-mono">
          Host Hardware Detection
        </h4>
        <div className="space-y-1 text-xs font-mono">
          <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
            <span>Processor:</span>
            <span className="text-[var(--text-primary)] font-medium truncate max-w-[240px]">{hardware.cpu}</span>
          </div>
          <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
            <span>System RAM:</span>
            <span className="text-[var(--text-primary)] font-medium">{hardware.ramTotal} ({hardware.ramAvailable})</span>
          </div>
          <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
            <span>Graphics / VRAM:</span>
            <span className="text-[var(--text-primary)] font-medium truncate max-w-[240px]">{hardware.gpu}</span>
          </div>
          <div className="flex justify-between p-2 rounded bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
            <span>Free Storage:</span>
            <span className="text-[var(--text-primary)] font-medium">{hardware.storageFree}</span>
          </div>
        </div>
      </div>

      {/* Installed & Approved Nemotron Models */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider font-mono">
            Approved Nemotron Models
          </h4>
          <span className="text-[10px] text-[var(--text-muted)] font-mono">
            Official NVIDIA Checkpoints Only
          </span>
        </div>

        <div className="space-y-2">
          {nemotronModels.map((model) => {
            const isCurrent = model.isActive;
            return (
              <div
                key={model.id}
                className={`p-3 rounded-[var(--radius-md)] border transition-all ${
                  isCurrent
                    ? 'bg-[var(--accent-subtle)]/40 border-[var(--accent-primary)]/40'
                    : 'bg-[var(--bg-subtle)] border-[var(--border-subtle)]'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[var(--text-primary)] font-display-title">
                        {model.name}
                      </span>
                      {isCurrent && (
                        <Badge variant="accent" size="xs" dot>
                          ACTIVE
                        </Badge>
                      )}
                    </div>
                    <p className="text-[11px] text-[var(--text-secondary)] mt-0.5">
                      {model.description}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 my-2 text-[10px] font-mono text-[var(--text-muted)] bg-black/20 p-2 rounded">
                  <div>Size: <strong className="text-[var(--text-primary)]">{model.size}</strong></div>
                  <div>Req VRAM: <strong className="text-[var(--text-primary)]">{model.vramRequired}</strong></div>
                  <div>Est Speed: <strong className="text-emerald-400">{model.speed}</strong></div>
                </div>

                {model.downloadProgress !== undefined && model.downloadProgress < 100 && (
                  <div className="my-2">
                    <Progress value={model.downloadProgress} size="xs" variant="ai" label="Downloading local weights" />
                  </div>
                )}

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-[var(--text-muted)] font-mono">
                    {model.quantization}
                  </span>

                  {model.isInstalled ? (
                    !isCurrent ? (
                      <Button
                        variant="secondary"
                        size="xs"
                        onClick={() => setActiveModelById(model.id)}
                      >
                        Switch to this Model
                      </Button>
                    ) : (
                      <span className="text-[11px] text-blue-400 font-semibold font-mono flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                        In-Memory
                      </span>
                    )
                  ) : (
                    <Button
                      variant="primary"
                      size="xs"
                      icon={DownloadCloud}
                      onClick={() => installModel(model.id)}
                    >
                      Download ({model.size})
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Benchmark Tool */}
      <div className="pt-2 border-t border-[var(--border-subtle)] flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={runBenchmark}
          isLoading={isBenchmarking}
          icon={Zap}
        >
          {isBenchmarking ? 'Testing GPU...' : 'Run Token Speed Benchmark'}
        </Button>

        {benchmarkTokens && (
          <span className="text-xs font-mono font-bold text-emerald-400">
            ✓ {benchmarkTokens} tokens/sec
          </span>
        )}
      </div>
    </Drawer>
  );
};
