import React, { useState, useEffect } from "react";
import {
  Settings,
  Check,
  Cpu,
  Zap,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
  Layers,
  ArrowRight
} from "lucide-react";
import { api } from "../../api";

interface SettingsScreenProps {
  onClearHistory?: () => void;
  onOpenPricing?: () => void;
  onOpenVendorAdmin?: () => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({
  onClearHistory,
  onOpenPricing,
  onOpenVendorAdmin,
}) => {
  const [activeTab, setActiveTab] = useState("model");
  const [allowInternet, setAllowInternet] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Nemotron Lifecycle & Hardware State
  const [recommendation, setRecommendation] = useState<any>(null);
  const [hardware, setHardware] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [selectedSpec, setSelectedSpec] = useState<any>(null);
  const [switching, setSwitching] = useState(false);
  const [switchMessage, setSwitchMessage] = useState("");
  const [showSwitchModal, setShowSwitchModal] = useState(false);

  const tabs = [
    { id: "general", label: "General" },
    { id: "licensing", label: "Commercial Licensing" },
    { id: "model", label: "AI & Nemotron Models" },
    { id: "memory", label: "Memory" },
    { id: "tools", label: "Tools" },
    { id: "permissions", label: "Permissions" },
    { id: "security", label: "Security & Privacy" },
    { id: "appearance", label: "Appearance" },
    { id: "storage", label: "Storage" },
  ];

  useEffect(() => {
    loadAiSettings();
  }, []);

  const loadAiSettings = async () => {
    try {
      const rec = await api.getNemotronRecommendation();
      setRecommendation(rec);
      setHardware(rec.hardware_summary);

      const st = await api.getAiLifecycleStatus();
      setStatus(st);

      const cat = await api.getNemotronCatalog();
      setModels(cat.models || []);
    } catch (e) {
      console.error("Error loading AI settings:", e);
    }
  };

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  const openSwitchModal = (spec: any) => {
    setSelectedSpec(spec);
    setShowSwitchModal(true);
  };

  const confirmModelSwitch = async () => {
    if (!selectedSpec) return;
    setSwitching(true);
    setSwitchMessage(`Downloading & verifying ${selectedSpec.display_name}...`);

    try {
      const res = await api.switchNemotronModel(selectedSpec.model_id);
      if (res.success) {
        setSwitchMessage(`Successfully switched to ${selectedSpec.display_name}`);
        await loadAiSettings();
        setTimeout(() => {
          setSwitching(false);
          setShowSwitchModal(false);
        }, 1200);
      } else {
        setSwitchMessage(`Switch failed: ${res.message}. Rolled back automatically.`);
        setSwitching(false);
      }
    } catch (e: any) {
      setSwitchMessage(`Error: ${e.message || "Switch failed"}. Rolled back automatically.`);
      setSwitching(false);
    }
  };

  const currentModelId = status?.current_model || "nemotron-3-nano:4b";

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] p-6 overflow-y-auto select-none space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0D0D0D] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Settings size={22} className="text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              SAARTHI SYSTEM CONFIGURATION
            </h2>
          </div>
          <p className="text-xs text-white/50">
            NVIDIA Nemotron local AI binding, hardware specs, and system preferences.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="px-4 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
        >
          {savedSuccess ? <Check size={16} /> : null}
          <span>{savedSuccess ? "Saved Settings" : "Save Changes"}</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-white/5 pb-2 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-3.5 py-2 rounded-xl text-xs font-mono font-semibold transition-all whitespace-nowrap cursor-pointer ${
              activeTab === t.id
                ? "bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40"
                : "bg-[#141414] text-white/40 border border-white/5 hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div className="p-6 rounded-2xl bg-[#141414] border border-white/5 space-y-6 max-w-4xl">
        
        {/* AI & MODEL TAB */}
        {activeTab === "model" && (
          <div className="space-y-6 text-xs font-sans">
            
            {/* Status & Current Model Banner */}
            <div className="p-5 rounded-2xl bg-[#0D0D0D] border border-[#F59E0B]/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-[#F59E0B] font-bold">
                  <Zap size={18} />
                  <span>ACTIVE LOCAL NEMOTRON MODEL</span>
                </div>
                <div className="text-sm font-bold text-white font-mono">
                  {status?.current_model || "nemotron-3-nano:4b"}
                </div>
                <div className="text-white/50 text-[11px]">
                  Provider: Ollama Engine (127.0.0.1:11434) | Status: <span className="text-emerald-400 font-bold">● Ready</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[10px] font-bold">
                  100% PRIVATE & LOCAL
                </span>
              </div>
            </div>

            {/* Hardware Profile Summary */}
            <div className="p-4 rounded-xl bg-[#0D0D0D] border border-white/10 space-y-2 font-mono">
              <div className="flex items-center gap-2 text-white/90 font-bold mb-1">
                <Cpu size={15} className="text-[#F59E0B]" />
                <span>DETECTED SYSTEM SPECIFICATIONS</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-white/70 text-[11px]">
                <div>RAM: <span className="text-white font-bold">{hardware?.total_ram_gb || 16} GB</span></div>
                <div>VRAM: <span className="text-white font-bold">{hardware?.vram_gb || 0} GB</span></div>
                <div>GPU: <span className="text-white font-bold">{hardware?.gpu_vendor || "Integrated"}</span></div>
                <div>Free Disk: <span className="text-white font-bold">{hardware?.free_storage_gb || 100} GB</span></div>
              </div>
            </div>

            {/* Available Nemotron Models across 4 Tiers */}
            <div className="space-y-3">
              <h4 className="font-bold text-white text-sm tracking-tight">AVAILABLE SAARTHI NEMOTRON TIERS</h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {models.map((spec) => {
                  const isCurrent = spec.model_id.toLowerCase() === currentModelId.toLowerCase();
                  const comp = recommendation?.compatibility?.[spec.tier];
                  const isRecommended = recommendation?.recommended_tier === spec.tier;
                  const isCompatible = comp?.compatible ?? true;

                  return (
                    <div
                      key={spec.tier}
                      className={`p-4 rounded-2xl border transition-all flex flex-col justify-between space-y-3 ${
                        isCurrent
                          ? "bg-[#17140D] border-[#F59E0B]/50 shadow-[0_0_20px_rgba(245,158,11,0.15)]"
                          : isCompatible
                          ? "bg-[#0D0D0D] border-white/10 hover:border-white/20"
                          : "bg-[#0D0D0D]/50 border-white/5 opacity-60"
                      }`}
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="px-2.5 py-0.5 rounded-full bg-white/10 font-mono font-bold text-[10px] text-white">
                            {spec.tier} TIER
                          </span>
                          {isCurrent ? (
                            <span className="text-emerald-400 font-mono text-[10px] font-bold">CURRENT ACTIVE</span>
                          ) : isRecommended ? (
                            <span className="text-[#F59E0B] font-mono text-[10px] font-bold">RECOMMENDED ✓</span>
                          ) : isCompatible ? (
                            <span className="text-emerald-400 font-mono text-[10px]">COMPATIBLE ✓</span>
                          ) : (
                            <span className="text-red-400 font-mono text-[10px]">INCOMPATIBLE</span>
                          )}
                        </div>

                        <h5 className="font-bold text-white text-xs">{spec.display_name}</h5>
                        <p className="text-[11px] text-white/60 leading-relaxed">{spec.capability_description}</p>
                      </div>

                      <div className="space-y-2 pt-2 border-t border-white/5 font-mono text-[10px] text-white/50">
                        <div className="flex justify-between">
                          <span>Download Size: ~{spec.estimated_download_size_gb} GB</span>
                          <span>Min RAM: {spec.minimum_ram_gb} GB</span>
                        </div>

                        {!isCurrent && (
                          <button
                            disabled={!isCompatible}
                            onClick={() => openSwitchModal(spec)}
                            className={`w-full py-2 rounded-xl text-xs font-bold font-sans transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                              isCompatible
                                ? "bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black shadow-[0_0_12px_rgba(245,158,11,0.25)]"
                                : "bg-white/5 text-white/30 cursor-not-allowed"
                            }`}
                          >
                            <span>{spec.tier === "ULTRA" || spec.tier === "SUPER" ? "Upgrade Model" : "Use This Model"}</span>
                            <ArrowRight size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        )}

        {/* SECURITY & PRIVACY TAB */}
        {activeTab === "security" && (
          <div className="space-y-4 text-xs font-sans">
            <div className="p-4 rounded-xl bg-[#F59E0B]/10 border border-[#F59E0B]/30 flex items-start justify-between gap-4">
              <div className="space-y-1">
                <h4 className="font-semibold text-[#F59E0B] text-sm">
                  Allow Internet Outbound Traffic
                </h4>
                <p className="text-white/60">
                  When toggled OFF, Saarthi operates in strict air-gapped local execution mode.
                </p>
              </div>

              <button
                onClick={() => setAllowInternet(!allowInternet)}
                className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${
                  allowInternet ? "bg-[#F59E0B]" : "bg-white/10 border border-white/20"
                }`}
              >
                <span
                  className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                    allowInternet ? "left-7" : "left-1"
                  }`}
                />
              </button>
            </div>
          </div>
        )}

        {/* LICENSING TAB */}
        {activeTab === "licensing" && (
          <div className="space-y-4 text-xs font-sans">
            <h4 className="font-semibold text-white text-sm">Commercial License & Plan Entitlements</h4>
            <p className="text-white/60">Ed25519 vendor-signed offline activation tokens with device binding.</p>
            {onOpenPricing && (
              <button
                onClick={onOpenPricing}
                className="px-4 py-2 rounded-xl bg-[#F59E0B] text-black font-bold text-xs hover:bg-[#F59E0B]/90 transition-all"
              >
                Manage Plan
              </button>
            )}
          </div>
        )}

        {/* MEMORY TAB */}
        {activeTab === "memory" && (
          <div className="space-y-4 text-xs font-sans">
            <h4 className="font-semibold text-white text-sm font-sans">Memory & Chat Operations</h4>
            <button
              type="button"
              onClick={onClearHistory}
              className="px-4 py-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-mono font-semibold transition-colors cursor-pointer"
            >
              Clear Chat History
            </button>
          </div>
        )}

        {(activeTab !== "model" && activeTab !== "licensing" && activeTab !== "security" && activeTab !== "memory") && (
          <div className="text-white/50 text-xs py-4 space-y-2">
            <p>Configured according to your local Saarthi preferences.</p>
            <div className="p-3 rounded-xl bg-[#0D0D0D] border border-white/10 font-mono text-white/70">
              Storage Root: E:\Saarthi
            </div>
          </div>
        )}
      </div>

      {/* CONFIRMATION SWITCH MODAL */}
      {showSwitchModal && selectedSpec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl animate-fade-in">
          <div className="w-full max-w-md p-6 rounded-3xl bg-[#0D0D0D] border border-[#F59E0B]/40 space-y-4 text-white">
            <div className="flex items-center gap-2 text-[#F59E0B] font-bold text-sm">
              <Zap size={18} />
              <span>CONFIRM NEMOTRON MODEL UPGRADE</span>
            </div>

            <p className="text-xs text-white/70 leading-relaxed">
              You are switching active AI model to <strong className="text-white">{selectedSpec.display_name}</strong> ({selectedSpec.tier} Tier).
            </p>

            <ul className="text-xs text-white/60 font-mono space-y-1 p-3 rounded-xl bg-[#141414] border border-white/10">
              <li>• Required Storage: ~{selectedSpec.minimum_storage_gb} GB</li>
              <li>• Download Size: ~{selectedSpec.estimated_download_size_gb} GB</li>
              <li>• Automatic Rollback: Enabled if health test fails</li>
            </ul>

            {switching ? (
              <div className="py-3 flex flex-col items-center gap-2 text-center text-xs">
                <RefreshCw size={24} className="text-[#F59E0B] animate-spin" />
                <span className="font-mono text-white/80">{switchMessage}</span>
              </div>
            ) : (
              <div className="flex items-center gap-3 pt-2">
                <button
                  onClick={() => setShowSwitchModal(false)}
                  className="flex-1 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmModelSwitch}
                  className="flex-1 py-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black font-bold text-xs transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)]"
                >
                  Download & Switch
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
