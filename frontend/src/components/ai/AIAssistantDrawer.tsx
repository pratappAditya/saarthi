import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  ShieldCheck, 
  Copy, 
  Check, 
  Terminal, 
  Cpu,
  Layers,
  ArrowRight
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Drawer } from '../common/Drawer';
import { Button } from '../common/Button';

export const AIAssistantDrawer: React.FC = () => {
  const { 
    isAssistantOpen, 
    setIsAssistantOpen, 
    assistantMessages, 
    sendAssistantMessage, 
    isAssistantThinking,
    activeModel,
    hardware,
    activeSection,
    activeResume,
    activeApplication
  } = useApp();

  const [inputVal, setInputVal] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim() || isAssistantThinking) return;
    sendAssistantMessage(inputVal);
    setInputVal('');
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getContextChips = () => {
    switch (activeSection) {
      case 'resumes':
      case 'tailor':
        return [
          'Improve bullet point metrics',
          'Check ATS keyword density',
          'Suggest missing skills for Staff Engineer',
          'Rephrase summary to be more executive'
        ];
      case 'applications':
        return [
          `Draft follow-up for ${activeApplication?.company || 'Stripe'}`,
          'Analyze salary leverage for this role',
          'Prepare likely panel interview questions',
          'Review application timeline status'
        ];
      case 'interviews':
        return [
          'Grade my STAR situation/result',
          'Generate 5 system design scenario questions',
          'Simulate aggressive follow-up interviewer questions',
          'How to answer salary expectations'
        ];
      case 'cover-letters':
        return [
          'Make cover letter sound more technical',
          'Shorten opening paragraph to 3 lines',
          'Align cover letter with Veloce Cloud metrics'
        ];
      default:
        return [
          'What should I prioritize today?',
          'Analyze my current pipeline velocity',
          'Find highest ATS match in my resume library',
          'Run local model diagnostics'
        ];
    }
  };

  return (
    <Drawer
      isOpen={isAssistantOpen}
      onClose={() => setIsAssistantOpen(false)}
      title={
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-blue-500/15 text-blue-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] font-display-title">
              Saarthi Career Copilot
            </h3>
            <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono">
              <ShieldCheck className="w-3 h-3" />
              <span>Local {activeModel.name.split(' ')[0]} • Zero Cloud Transfer</span>
            </div>
          </div>
        </div>
      }
      width="lg"
    >
      {/* Privacy Guarantee Banner */}
      <div className="p-2.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-[11px] text-[var(--text-secondary)]">
            Inference: <strong className="text-[var(--text-primary)]">{hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tok/s` : 'Not benchmarked'}</strong> on local GPU
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          OFFLINE SECURE
        </span>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 space-y-4 pr-1">
        {assistantMessages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1`}
            >
              <div className="flex items-center gap-2 px-1 text-[10px] text-[var(--text-muted)] font-mono">
                <span>{isUser ? 'You' : `Saarthi (${activeModel.name.split(' ')[0]})`}</span>
                <span>•</span>
                <span>{msg.timestamp}</span>
                {msg.tokensPerSec && !isUser && (
                  <span className="text-emerald-400">({msg.tokensPerSec} t/s)</span>
                )}
              </div>

              <div
                className={`p-3.5 rounded-[var(--radius-lg)] text-xs leading-relaxed max-w-[90%] whitespace-pre-wrap ${
                  isUser
                    ? 'bg-[var(--accent-primary)] text-white font-medium'
                    : 'bg-[var(--bg-surface-elevated)] text-[var(--text-primary)] border border-[var(--border-subtle)] shadow-xs'
                }`}
              >
                {msg.text}
              </div>

              {/* Action Chips / Copy Button */}
              {!isUser && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  <button
                    onClick={() => handleCopy(msg.text, msg.id)}
                    className="flex items-center gap-1 px-2 py-0.5 text-[10px] text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded bg-[var(--bg-subtle)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] transition-colors cursor-pointer"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>

                  {msg.chips?.map((chip, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendAssistantMessage(chip)}
                      className="px-2 py-0.5 text-[10px] text-[var(--text-secondary)] hover:text-blue-400 rounded-full bg-[var(--bg-subtle)] hover:bg-blue-500/10 border border-[var(--border-subtle)] hover:border-blue-500/30 transition-colors cursor-pointer"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {isAssistantThinking && (
          <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)] p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
            <span className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span>Nemotron thinking locally ({activeModel.name})...</span>
          </div>
        )}
      </div>

      {/* Contextual Suggestions for Current Screen */}
      <div className="pt-2 border-t border-[var(--border-subtle)]">
        <div className="text-[10px] uppercase font-mono tracking-wider text-[var(--text-muted)] mb-1.5 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-blue-400" />
          Suggested Actions ({activeSection})
        </div>
        <div className="flex flex-wrap gap-1.5">
          {getContextChips().map((chip, idx) => (
            <button
              key={idx}
              onClick={() => sendAssistantMessage(chip)}
              className="text-[11px] px-2.5 py-1 rounded-[var(--radius-sm)] bg-[var(--bg-subtle)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-blue-500/40 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer text-left flex items-center gap-1"
            >
              <span>{chip}</span>
              <ArrowRight className="w-2.5 h-2.5 opacity-50" />
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="relative pt-2">
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder={`Ask anything about your resume, applications, or ${activeModel.name.split(' ')[0]}...`}
          className="w-full bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border-strong)] focus:border-blue-500 rounded-[var(--radius-md)] pl-3.5 pr-12 py-2.5 text-xs placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={!inputVal.trim() || isAssistantThinking}
          className="absolute right-2 top-4 p-1.5 rounded-[var(--radius-sm)] bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white transition-colors cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </Drawer>
  );
};
