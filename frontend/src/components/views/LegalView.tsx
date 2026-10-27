import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { ShieldCheck, FileText, Lock, Cookie, HelpCircle, AlertTriangle } from 'lucide-react';

export const LegalView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'terms' | 'privacy' | 'cookies' | 'refunds' | 'support'>('terms');

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>SAARTHI LEGAL & COMPLIANCE CENTER</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Terms, Privacy & Legal Policy
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Trovane Technologies official legal placeholders and compliance documentation for Saarthi.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[var(--border-subtle)] gap-2">
        <button
          onClick={() => setActiveTab('terms')}
          className={`px-4 py-2 text-xs font-mono rounded-t-lg flex items-center gap-2 transition-colors ${
            activeTab === 'terms' ? 'bg-blue-900/30 text-blue-400 border-b-2 border-blue-500 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          Terms of Service
        </button>
        <button
          onClick={() => setActiveTab('privacy')}
          className={`px-4 py-2 text-xs font-mono rounded-t-lg flex items-center gap-2 transition-colors ${
            activeTab === 'privacy' ? 'bg-blue-900/30 text-blue-400 border-b-2 border-blue-500 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          Privacy Policy
        </button>
        <button
          onClick={() => setActiveTab('cookies')}
          className={`px-4 py-2 text-xs font-mono rounded-t-lg flex items-center gap-2 transition-colors ${
            activeTab === 'cookies' ? 'bg-blue-900/30 text-blue-400 border-b-2 border-blue-500 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          <Cookie className="w-3.5 h-3.5" />
          Cookie & Consent
        </button>
        <button
          onClick={() => setActiveTab('refunds')}
          className={`px-4 py-2 text-xs font-mono rounded-t-lg flex items-center gap-2 transition-colors ${
            activeTab === 'refunds' ? 'bg-blue-900/30 text-blue-400 border-b-2 border-blue-500 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          Refund Policy
        </button>
        <button
          onClick={() => setActiveTab('support')}
          className={`px-4 py-2 text-xs font-mono rounded-t-lg flex items-center gap-2 transition-colors ${
            activeTab === 'support' ? 'bg-blue-900/30 text-blue-400 border-b-2 border-blue-500 font-bold' : 'text-gray-400 hover:text-white'
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          Contact & Support
        </button>
      </div>

      {/* Tab Content */}
      <Card className="p-6 space-y-4">
        {activeTab === 'terms' && (
          <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
            <h2 className="text-base font-bold text-white">Terms of Service — Saarthi (Trovane Technologies)</h2>
            <p className="text-amber-300/80 font-mono bg-amber-950/20 p-2 rounded border border-amber-800/40">
              [INTERNAL REVIEW PLACEHOLDER] — Formal legal documentation pending final counsel review prior to public commercial deployment.
            </p>
            <p>
              By accessing or using Saarthi (saarthi.trovanetech.com), you agree to be bound by these Terms of Service. Saarthi is owned and operated by Trovane Technologies.
            </p>
            <h3 className="text-sm font-semibold text-white">1. Use of AI Services</h3>
            <p>
              Saarthi provides universal AI operating companion services including chat, voice, document processing, research, and agent execution. You agree not to misuse the platform or bypass authorization boundaries.
            </p>
            <h3 className="text-sm font-semibold text-white">2. User Data & Ownership</h3>
            <p>
              Your local files, resumes, and personal memory remain your sole property. Saarthi stores sensitive memory locally on your device or in encrypted vault isolation.
            </p>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
            <h2 className="text-base font-bold text-white">Privacy Policy</h2>
            <p>
              Trovane Technologies respects user privacy. Saarthi implements zero-knowledge privacy boundaries where administrative roles cannot casually inspect user private prompts, files, or messages.
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Local execution and local LLM runtime priority.</li>
              <li>Encrypted auth token exchange.</li>
              <li>Strict server-side capability and entitlement authorization.</li>
            </ul>
          </div>
        )}

        {activeTab === 'cookies' && (
          <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
            <h2 className="text-base font-bold text-white">Cookie & Local Storage Policy</h2>
            <p>
              Saarthi utilizes essential HTTP-only cookies and local session storage strictly for maintaining user authentication state and active session parameters.
            </p>
          </div>
        )}

        {activeTab === 'refunds' && (
          <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
            <h2 className="text-base font-bold text-white">Refund Policy Placeholder</h2>
            <div className="p-4 rounded-lg bg-blue-950/30 border border-blue-500/30 text-blue-200 font-mono">
              <strong>Notice:</strong> Live payment collection is currently disabled. Payments coming after funding.
            </div>
            <p>
              Upon activation of commercial billing, refund terms will allow a 14-day refund period for all paid subscription tiers (`STUDENT`, `PERSONAL`, `POWER`, `TEAMS`).
            </p>
          </div>
        )}

        {activeTab === 'support' && (
          <div className="space-y-4 text-xs text-gray-300 leading-relaxed">
            <h2 className="text-base font-bold text-white">Contact & Support</h2>
            <p>
              For enterprise inquiries, technical support, or billing questions, contact Trovane Technologies support:
            </p>
            <div className="font-mono bg-slate-900 p-4 rounded border border-gray-800 space-y-1">
              <div>Email: <a href="mailto:support@trovanetech.com" className="text-blue-400">support@trovanetech.com</a></div>
              <div>Admin Console: <span className="text-purple-400">admin.saarthi.trovanetech.com</span></div>
              <div>Product Domain: <span className="text-emerald-400">saarthi.trovanetech.com</span></div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
