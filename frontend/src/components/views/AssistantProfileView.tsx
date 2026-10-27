import React, { useState, useEffect } from 'react';
import { Bot, Sliders, Mic, Shield, Save, CheckCircle2, Sparkles, Volume2 } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Input } from '../common/Input';
import { useApp } from '../../context/AppContext';

export const AssistantProfileView: React.FC = () => {
  const { addToast } = useApp();
  const [name, setName] = useState('Saarthi');
  const [tone, setTone] = useState('intelligent, calm, helpful');
  const [verbosity, setVerbosity] = useState('concise');
  const [formality, setFormality] = useState('adaptive');
  const [proactivity, setProactivity] = useState('risk_aware');
  const [confirmationPolicy, setConfirmationPolicy] = useState('risk_based');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/profile/assistant');
      if (res.ok) {
        const data = await res.json();
        const p = data.profile || {};
        setName(p.name || 'Saarthi');
        setTone(p.tone || 'intelligent, calm, helpful');
        setVerbosity(p.verbosity || 'concise');
        setFormality(p.formality || 'adaptive');
        setProactivity(p.proactivity || 'risk_aware');
        setConfirmationPolicy(p.confirmation_policy || 'risk_based');
      }
    } catch (err) {
      console.error("Failed to load assistant profile", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/profile/assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          tone,
          verbosity,
          formality,
          proactivity,
          confirmation_policy: confirmationPolicy
        })
      });
      if (res.ok) {
        addToast({ type: 'success', title: 'Profile Updated', message: 'Saarthi Assistant settings persisted to SQLite.' });
      }
    } catch (err) {
      addToast({ type: 'error', title: 'Update Failed', message: 'Could not save assistant profile.' });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-200 font-mono text-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Bot className="w-3.5 h-3.5 text-purple-400" />
            <span>SAARTHI ASSISTANT IDENTITY & PERSONALITY</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Assistant Settings & Voice Profile
          </h1>
        </div>
      </div>

      {/* Settings Form */}
      <Card variant="default" padding="md" className="space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Sliders className="w-4 h-4 text-purple-400" />
          <span>Configurable Assistant Profile</span>
        </h3>

        {loading ? (
          <div className="py-8 text-center text-gray-400">Loading Assistant Settings...</div>
        ) : (
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Assistant Identity Name" value={name} onChange={(e) => setName(e.target.value)} required />
              <Input label="Conversational Tone" value={tone} onChange={(e) => setTone(e.target.value)} required />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-mono text-gray-400 mb-1">Verbosity Level</label>
                <select value={verbosity} onChange={(e) => setVerbosity(e.target.value)} className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs">
                  <option value="concise">Concise & Direct (Recommended)</option>
                  <option value="balanced">Balanced</option>
                  <option value="detailed">Detailed & Comprehensive</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-gray-400 mb-1">Formality</label>
                <select value={formality} onChange={(e) => setFormality(e.target.value)} className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs">
                  <option value="adaptive">Adaptive Professional</option>
                  <option value="casual">Casual & Friendly</option>
                  <option value="formal">Strictly Formal</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-mono text-gray-400 mb-1">Proactivity Policy</label>
                <select value={proactivity} onChange={(e) => setProactivity(e.target.value)} className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs">
                  <option value="risk_aware">Risk-Aware Proactive Suggestions</option>
                  <option value="passive">Passive (Respond only when prompted)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-gray-400 mb-1">Confirmation Policy</label>
                <select value={confirmationPolicy} onChange={(e) => setConfirmationPolicy(e.target.value)} className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs">
                  <option value="risk_based">Risk-Based Approval (Ask on Moderate/High Risk)</option>
                  <option value="always_ask">Always Ask Before Tool Execution</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="primary" size="sm" icon={Save} type="submit">
                Save Profile Settings
              </Button>
            </div>
          </form>
        )}
      </Card>

      {/* Voice Status Card */}
      <Card variant="default" padding="md" className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-blue-400" />
            <span className="font-bold text-white text-sm">Saarthi Voice Persona</span>
          </div>
          <Badge variant="outline" size="xs">Coming Soon — Speech Output Ready</Badge>
        </div>
        <p className="text-gray-400 text-xs leading-relaxed">
          Voice Identity Profile: <strong className="text-white">Saarthi (en-IN + hi-IN, Indian English + Hindi accent)</strong>. No background microphone listening is enabled in Phase 5C for strict privacy compliance.
        </p>
      </Card>
    </div>
  );
};
