import React from 'react';
import { X, ShieldCheck, CheckCircle2, XCircle, Trash2, Edit3, Sparkles, Activity, Clock, Tag } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

interface PreferenceItem {
  key: string;
  category: string;
  value: any;
  source: 'USER_EXPLICIT' | 'USER_CONFIRMED' | 'MODEL_INFERRED' | 'SYSTEM_DERIVED';
  confidence: number;
  evidence: string;
  created_at: number;
  last_observed: number;
  confirmed?: boolean;
  rejected?: boolean;
  affected_behavior?: string;
}

interface ModalProps {
  item: PreferenceItem | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm?: (key: string) => void;
  onReject?: (key: string) => void;
  onForget?: (key: string) => void;
}

export const WhatSaarthiKnowsModal: React.FC<ModalProps> = ({
  item,
  isOpen,
  onClose,
  onConfirm,
  onReject,
  onForget
}) => {
  if (!isOpen || !item) return null;

  const isExplicit = item.source === 'USER_EXPLICIT' || item.source === 'USER_CONFIRMED';
  const confidencePercent = Math.round((item.confidence || 0.75) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4 font-mono text-xs animate-in fade-in duration-150">
      <div className="w-full max-w-lg bg-[#0b0f19] border border-purple-500/40 rounded-3xl p-6 space-y-5 shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="font-bold text-white text-sm">WHAT SAARTHI KNOWS ABOUT ME</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-all cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Preference Value & Source Badge */}
        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Tag className="w-3.5 h-3.5 text-blue-400" />
              <span className="font-bold text-white uppercase text-xs">{item.key}</span>
            </div>
            <Badge variant={isExplicit ? 'success' : 'accent'} size="sm">
              {item.source}
            </Badge>
          </div>

          <div className="p-3 rounded-xl bg-black/40 border border-white/10 font-bold text-emerald-300 text-sm">
            {typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value)}
          </div>
        </div>

        {/* Inspection Breakdown */}
        <div className="space-y-2 text-gray-300 text-xs">
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 border border-white/10">
            <span className="text-gray-400">Confidence Score:</span>
            <span className="font-bold text-purple-300">{confidencePercent}%</span>
          </div>

          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Evidence / Provenance:</span>
            <p className="text-gray-200 leading-relaxed italic">{item.evidence || 'Derived from user interaction patterns.'}</p>
          </div>

          <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
            <span className="text-gray-400">Affected Saarthi Behavior:</span>
            <p className="text-blue-300 font-medium">{item.affected_behavior || 'Adapts response synthesis & tone.'}</p>
          </div>

          <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1">
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              <span>Created: {new Date(item.created_at * 1000).toLocaleDateString()}</span>
            </div>
            <span>Last Observed: {new Date(item.last_observed * 1000).toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/10">
          {!isExplicit && onConfirm && (
            <Button variant="primary" size="sm" icon={CheckCircle2} onClick={() => { onConfirm(item.key); onClose(); }}>
              Confirm Fact
            </Button>
          )}
          {!isExplicit && onReject && (
            <Button variant="outline" size="sm" icon={XCircle} onClick={() => { onReject(item.key); onClose(); }}>
              Reject Fact
            </Button>
          )}
          {onForget && (
            <Button variant="danger" size="sm" icon={Trash2} onClick={() => { onForget(item.key); onClose(); }}>
              Forget Preference
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
