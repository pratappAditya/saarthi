import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Sliders, ShieldCheck, CheckCircle2, XCircle, Trash2, HelpCircle, RefreshCw, Eye, Brain, Zap, Layers, Globe, Radio, AlertCircle
} from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';
import { WhatSaarthiKnowsModal } from './WhatSaarthiKnowsModal';

export const PersonalizationView: React.FC = () => {
  const { addToast } = useApp();
  const [profile, setProfile] = useState<any>(null);
  const [learnedPrefs, setLearnedPrefs] = useState<any[]>([]);
  const [expertise, setExpertise] = useState<Record<string, any>>({});
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'explicit' | 'inferred' | 'expertise' | 'settings'>('inferred');
  const [inspectItem, setInspectItem] = useState<any | null>(null);

  useEffect(() => {
    loadPersonalizationData();
  }, []);

  const loadPersonalizationData = async () => {
    try {
      setLoading(true);
      const [profRes, learnedRes, expRes, setRes] = await Promise.all([
        api.getPersonalizationProfile(),
        api.getLearnedPreferences(),
        api.getDomainExpertise(),
        api.getVoicePrivacy() // or settings
      ]);

      if (profRes && profRes.profile) {
        setProfile(profRes.profile);
      }
      if (learnedRes && Array.isArray(learnedRes.learned_preferences)) {
        setLearnedPrefs(learnedRes.learned_preferences);
      }
      if (expRes && expRes.expertise) {
        setExpertise(expRes.expertise);
      }
      setSettings(profRes.profile || {});
    } catch (err: any) {
      console.error("Failed to load personalization data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStyle = async (field: string, val: any) => {
    try {
      const res = await api.updatePersonalizationProfile({ [field]: val });
      if (res && res.profile) {
        setProfile(res.profile);
        addToast({
          type: 'success',
          title: 'Preference Updated',
          message: `Set ${field.replace('_', ' ')} to '${val}'.`
        });
      }
    } catch (e: any) {
      addToast({ type: 'error', title: 'Update Failed', message: e.message });
    }
  };

  const handleConfirmPreference = async (key: string) => {
    try {
      await api.confirmPreference(key);
      addToast({
        type: 'success',
        title: 'Preference Confirmed',
        message: `Inferred item '${key}' promoted to confirmed user fact.`
      });
      loadPersonalizationData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Confirmation Failed', message: e.message });
    }
  };

  const handleRejectPreference = async (key: string) => {
    try {
      await api.rejectPreference(key);
      addToast({
        type: 'info',
        title: 'Preference Rejected',
        message: `Inferred item '${key}' rejected and will not influence Saarthi.`
      });
      loadPersonalizationData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Rejection Failed', message: e.message });
    }
  };

  const handleForgetPreference = async (key: string) => {
    try {
      await api.forgetPreference(key);
      addToast({
        type: 'info',
        title: 'Preference Forgotten',
        message: `Removed '${key}' from memory & personalization engine.`
      });
      loadPersonalizationData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Forget Failed', message: e.message });
    }
  };

  const handleUpdateExpertise = async (domain: string, level: string) => {
    try {
      await api.setDomainExpertise(domain, level);
      addToast({
        type: 'success',
        title: 'Domain Expertise Updated',
        message: `Set ${domain.toUpperCase()} domain depth to ${level.toUpperCase()}.`
      });
      loadPersonalizationData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Expertise Update Failed', message: e.message });
    }
  };

  const handleToggleSetting = async (key: string, val: boolean) => {
    try {
      const res = await api.updatePersonalizationSettings({ [key]: val });
      if (res && res.settings) {
        setProfile((prev: any) => ({ ...prev, [key]: val }));
        addToast({
          type: 'info',
          title: 'Setting Updated',
          message: `${key.replace('_', ' ')} set to ${val ? 'ON' : 'OFF'}.`
        });
      }
    } catch (e: any) {
      addToast({ type: 'error', title: 'Setting Failed', message: e.message });
    }
  };

  const handleResetAll = async () => {
    if (!window.confirm("Are you sure you want to reset all personalization profile & learned data?")) return;
    try {
      await api.resetPersonalization();
      addToast({
        type: 'info',
        title: 'Personalization Reset',
        message: 'Cleared all explicit, inferred, and expertise overrides.'
      });
      loadPersonalizationData();
    } catch (e: any) {
      addToast({ type: 'error', title: 'Reset Failed', message: e.message });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-xs font-mono text-gray-400">
        Loading Saarthi Personalization Engine...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 font-sans text-white p-2 animate-in fade-in duration-200">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-purple-600/30 to-blue-600/30 border border-purple-500/40">
            <Sparkles className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">DEEP PERSONALIZATION DASHBOARD</h1>
              <Badge variant="accent" size="sm">Phase 5I</Badge>
            </div>
            <p className="text-xs text-gray-400 mt-0.5 font-mono">
              Transparent user preferences, domain expertise estimation, explicit vs inferred preference lifecycle, and privacy controls.
            </p>
          </div>
        </div>

        <Button variant="outline" size="sm" icon={RefreshCw} onClick={loadPersonalizationData}>
          Refresh
        </Button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">COMMUNICATION STYLE</span>
          <p className="text-white text-sm font-bold capitalize">{profile?.communication_style || 'Direct'}</p>
          <span className="text-gray-500 text-[10px]">Length: {profile?.preferred_response_length}</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">TECHNICAL DEPTH</span>
          <p className="text-purple-400 text-sm font-bold capitalize">{profile?.technical_depth || 'Adaptive'}</p>
          <span className="text-gray-500 text-[10px]">Formatting: {profile?.preferred_formatting}</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">PROACTIVITY LEVEL</span>
          <p className="text-emerald-400 text-sm font-bold capitalize">{profile?.proactivity_preference || 'Moderate'}</p>
          <span className="text-gray-500 text-[10px]">Confirmation: {profile?.confirmation_preference}</span>
        </Card>

        <Card variant="default" padding="md" className="space-y-2">
          <span className="text-gray-400 text-[10px]">LEARNED INFERENCES</span>
          <p className="text-blue-400 text-sm font-bold">{learnedPrefs.length} Active Items</p>
          <span className="text-gray-500 text-[10px]">Explicit + Confirmed Facts</span>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10 gap-4 font-mono text-xs">
        <button
          onClick={() => setActiveTab('inferred')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'inferred' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Learned Preferences ({learnedPrefs.length})
        </button>
        <button
          onClick={() => setActiveTab('explicit')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'explicit' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Communication & Work Controls
        </button>
        <button
          onClick={() => setActiveTab('expertise')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'expertise' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Domain Expertise Model
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`pb-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'settings' ? 'border-purple-500 text-white font-bold' : 'border-transparent text-gray-400 hover:text-white'
          }`}
        >
          Privacy & Learning Toggles
        </button>
      </div>

      {/* TAB CONTENT 1: LEARNED INFERRED PREFERENCES */}
      {activeTab === 'inferred' && (
        <div className="space-y-4 font-mono">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-300">INFERRED BEHAVIORAL PATTERNS (AI Derived)</span>
            <span className="text-[10px] text-gray-500">Every inference shows confidence & evidence provenance</span>
          </div>

          {learnedPrefs.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-white/10 rounded-2xl text-xs text-gray-400">
              No inferred preferences recorded yet. Continue interacting with Saarthi to build personalized behavioral context.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {learnedPrefs.map((item) => (
                <div key={item.key} className="p-4 rounded-2xl bg-[#0e1426] border border-white/10 space-y-3 relative group">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={item.source === 'USER_CONFIRMED' ? 'success' : 'accent'} size="xs">
                        {item.source}
                      </Badge>
                      <span className="font-bold text-white uppercase">{item.key}</span>
                    </div>
                    <span className="text-purple-300 text-[10px] font-bold">
                      {Math.round((item.confidence || 0.75) * 100)}% Conf
                    </span>
                  </div>

                  <p className="text-emerald-300 font-mono text-xs bg-black/40 p-2 rounded-xl border border-white/5">
                    Value: {typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value)}
                  </p>

                  <p className="text-gray-400 text-[11px] italic leading-tight">
                    Source: {item.evidence}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-white/10">
                    <button
                      onClick={() => setInspectItem(item)}
                      className="text-blue-400 hover:underline text-[10px] flex items-center gap-1 cursor-pointer"
                    >
                      <Eye className="w-3 h-3" /> Inspect Provenance
                    </button>

                    <div className="flex items-center gap-1">
                      {item.source !== 'USER_CONFIRMED' && (
                        <button
                          onClick={() => handleConfirmPreference(item.key)}
                          className="p-1 rounded bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-800/60 cursor-pointer"
                          title="Confirm fact"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => handleRejectPreference(item.key)}
                        className="p-1 rounded bg-rose-950/60 border border-rose-500/40 text-rose-300 hover:bg-rose-800/60 cursor-pointer"
                        title="Reject fact"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleForgetPreference(item.key)}
                        className="p-1 rounded bg-white/5 border border-white/10 text-gray-400 hover:text-white cursor-pointer"
                        title="Forget preference"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT 2: EXPLICIT COMMUNICATION & WORK CONTROLS */}
      {activeTab === 'explicit' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-mono text-xs">
          <Card variant="default" padding="lg" className="space-y-4">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              <span>Communication Preferences</span>
            </h3>

            <div className="space-y-3">
              <div>
                <label className="text-gray-400 block mb-1">Communication Style</label>
                <select
                  value={profile?.communication_style || 'direct'}
                  onChange={(e) => handleUpdateStyle('communication_style', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="direct">Direct & Action-Oriented</option>
                  <option value="explanatory">Explanatory & Educational</option>
                  <option value="conversational">Conversational & Friendly</option>
                  <option value="executive">Executive Briefing</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Preferred Response Length</label>
                <select
                  value={profile?.preferred_response_length || 'concise'}
                  onChange={(e) => handleUpdateStyle('preferred_response_length', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="concise">Concise & Brief</option>
                  <option value="balanced">Balanced</option>
                  <option value="detailed">Detailed & Comprehensive</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Preferred Response Formatting</label>
                <select
                  value={profile?.preferred_formatting || 'bullet_points'}
                  onChange={(e) => handleUpdateStyle('preferred_formatting', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="bullet_points">Bullet Points & Highlights</option>
                  <option value="prose">Structured Prose Paragraphs</option>
                  <option value="code_heavy">Code Heavy & Functional Examples</option>
                </select>
              </div>
            </div>
          </Card>

          <Card variant="default" padding="lg" className="space-y-4">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" />
              <span>Work & Agent Preferences</span>
            </h3>

            <div className="space-y-3">
              <div>
                <label className="text-gray-400 block mb-1">Proactivity Preference</label>
                <select
                  value={profile?.proactivity_preference || 'moderate'}
                  onChange={(e) => handleUpdateStyle('proactivity_preference', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="high">High Proactivity (Frequent suggestions)</option>
                  <option value="moderate">Moderate Proactivity (Balanced alerts)</option>
                  <option value="low">Low Proactivity (Only urgent items)</option>
                  <option value="quiet">Quiet Mode (No proactive prompts)</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Agent Autonomy Preference</label>
                <select
                  value={profile?.autonomy_preference || 'semi_autonomous'}
                  onChange={(e) => handleUpdateStyle('autonomy_preference', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="guided">Guided Step-by-Step</option>
                  <option value="semi_autonomous">Semi-Autonomous (Confirm high-risk)</option>
                  <option value="autonomous">Autonomous Execution</option>
                </select>
              </div>

              <div>
                <label className="text-gray-400 block mb-1">Confirmation Policy</label>
                <select
                  value={profile?.confirmation_preference || 'risk_based'}
                  onChange={(e) => handleUpdateStyle('confirmation_preference', e.target.value)}
                  className="w-full bg-[#070a12] border border-white/10 rounded-xl p-2 text-white text-xs focus:outline-none"
                >
                  <option value="strict">Strict Confirmation (Every tool action)</option>
                  <option value="risk_based">Risk-Based (High-risk actions only)</option>
                  <option value="minimal">Minimal Confirmation</option>
                </select>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT 3: DOMAIN EXPERTISE MODEL */}
      {activeTab === 'expertise' && (
        <div className="space-y-4 font-mono text-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-300">DOMAIN EXPERTISE MATRIX</span>
            <span className="text-[10px] text-gray-500">Saarthi avoids explaining basic concepts for domains rated Advanced or Expert</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {['software', 'cybersecurity', 'career', 'research', 'biology', 'archaeology', 'business', 'education', 'general'].map((dom) => {
              const expItem = expertise[dom];
              const level = expItem ? expItem.level : 'intermediate';

              return (
                <div key={dom} className="p-4 rounded-2xl bg-[#0e1426] border border-white/10 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white uppercase text-sm">{dom}</span>
                    <Badge variant={level === 'expert' ? 'accent' : level === 'advanced' ? 'success' : 'outline'} size="sm">
                      {level.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="flex gap-2">
                    {['novice', 'intermediate', 'advanced', 'expert'].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => handleUpdateExpertise(dom, lvl)}
                        className={`flex-1 py-1.5 rounded-lg text-[10px] capitalize transition-all cursor-pointer ${
                          level === lvl ? 'bg-purple-600 font-bold text-white' : 'bg-white/5 text-gray-400 hover:text-white'
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>

                  <p className="text-[10px] text-gray-400 italic">
                    {expItem?.evidence || 'Default domain baseline.'}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB CONTENT 4: PRIVACY & LEARNING TOGGLES */}
      {activeTab === 'settings' && (
        <div className="max-w-2xl mx-auto space-y-4 font-mono text-xs">
          <Card variant="default" padding="lg" className="space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <span className="font-bold text-white text-sm flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Personalization Privacy & Learning Controls</span>
              </span>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-white">Enable Deep Personalization</span>
                  <p className="text-gray-400 text-[11px]">Allows Saarthi to adapt responses using your profile.</p>
                </div>
                <input
                  type="checkbox"
                  checked={profile?.personalization_enabled ?? true}
                  onChange={(e) => handleToggleSetting('personalization_enabled', e.target.checked)}
                  className="w-4 h-4 accent-purple-600 cursor-pointer"
                />
              </div>

              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <div>
                  <span className="font-bold text-white">Enable Behavioral Learning</span>
                  <p className="text-gray-400 text-[11px]">Allows Saarthi to learn from interactions. (No sensitive profiling)</p>
                </div>
                <input
                  type="checkbox"
                  checked={profile?.learning_enabled ?? true}
                  onChange={(e) => handleToggleSetting('learning_enabled', e.target.checked)}
                  className="w-4 h-4 accent-purple-600 cursor-pointer"
                />
              </div>

              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <div>
                  <span className="font-bold text-white">Enable Pattern Inference</span>
                  <p className="text-gray-400 text-[11px]">Infers preference candidates with explicit evidence provenance.</p>
                </div>
                <input
                  type="checkbox"
                  checked={profile?.inference_enabled ?? true}
                  onChange={(e) => handleToggleSetting('inference_enabled', e.target.checked)}
                  className="w-4 h-4 accent-purple-600 cursor-pointer"
                />
              </div>

              <div className="flex items-center justify-between border-t border-white/10 pt-3">
                <div>
                  <span className="font-bold text-white">Enable Voice Personalization</span>
                  <p className="text-gray-400 text-[11px]">Adapts speaking style & confirmation based on voice interaction.</p>
                </div>
                <input
                  type="checkbox"
                  checked={profile?.voice_personalization_enabled ?? true}
                  onChange={(e) => handleToggleSetting('voice_personalization_enabled', e.target.checked)}
                  className="w-4 h-4 accent-purple-600 cursor-pointer"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-white/10 flex justify-end">
              <Button variant="danger" size="sm" icon={Trash2} onClick={handleResetAll}>
                Reset All Personalization Data
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Inspection Modal */}
      <WhatSaarthiKnowsModal
        item={inspectItem}
        isOpen={!!inspectItem}
        onClose={() => setInspectItem(null)}
        onConfirm={handleConfirmPreference}
        onReject={handleRejectPreference}
        onForget={handleForgetPreference}
      />
    </div>
  );
};
