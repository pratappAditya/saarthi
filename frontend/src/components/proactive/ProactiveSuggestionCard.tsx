import React from 'react';
import { Lightbulb, CheckCircle, XCircle, ArrowRight, HelpCircle } from 'lucide-react';
import { Badge } from '../common/Badge';

export interface SuggestionData {
  id: string;
  title: string;
  notice_text: string;
  rationale: string;
  action_type: 'SUGGEST' | 'ASK' | 'ACT';
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'accepted' | 'dismissed';
}

interface CardProps {
  suggestion: SuggestionData;
  onAccept: (id: string) => void;
  onDismiss: (id: string) => void;
}

export const ProactiveSuggestionCard: React.FC<CardProps> = ({
  suggestion,
  onAccept,
  onDismiss
}) => {
  if (suggestion.status !== 'pending') return null;

  return (
    <div className="bg-[#0b0f19] border border-amber-500/40 rounded-2xl p-4 space-y-3 font-mono text-xs shadow-xl animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-amber-400 animate-pulse" />
          <span className="font-bold text-white text-sm">{suggestion.title}</span>
        </div>
        <Badge variant={suggestion.priority === 'high' ? 'warning' : 'accent'} size="xs">
          {suggestion.action_type}
        </Badge>
      </div>

      {/* Notice & Rationale */}
      <div className="space-y-1.5">
        <p className="text-amber-200 font-medium">{suggestion.notice_text}</p>
        <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-[11px] leading-relaxed flex items-start gap-2">
          <HelpCircle className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="text-gray-400 font-bold">Why Saarthi suggested this: </span>
            {suggestion.rationale}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-2 pt-1">
        <button
          onClick={() => onDismiss(suggestion.id)}
          className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-400 hover:text-white flex items-center gap-1 transition-all cursor-pointer"
        >
          <XCircle className="w-3.5 h-3.5" />
          <span>Dismiss</span>
        </button>
        <button
          onClick={() => onAccept(suggestion.id)}
          className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-200 font-bold flex items-center gap-1 transition-all cursor-pointer"
        >
          <CheckCircle className="w-3.5 h-3.5 text-amber-400" />
          <span>Accept & Proceed</span>
        </button>
      </div>
    </div>
  );
};
