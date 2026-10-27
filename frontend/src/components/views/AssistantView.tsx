import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  ShieldCheck, 
  Copy, 
  Check, 
  Cpu, 
  Trash2, 
  ArrowRight,
  Terminal,
  FileText,
  Briefcase
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

export const AssistantView: React.FC = () => {
  const { 
    assistantMessages, 
    sendAssistantMessage, 
    isAssistantThinking, 
    activeModel, 
    hardware, 
    activeResume,
    applications,
    addToast
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
    addToast({ type: 'success', title: 'Response Copied to Clipboard' });
    setTimeout(() => setCopiedId(null), 2000);
  };

  const promptStarters = [
    { title: 'Evaluate Resume Gaps', desc: 'Scan for missing Staff-level keywords in Master v4.2', icon: FileText },
    { title: 'Simulate System Design Panel', desc: 'Ask me 3 architectural scaling questions for Stripe', icon: Cpu },
    { title: 'Salary Negotiation Script', desc: 'Draft a polite counter-offer for Vercel ($275k -> $295k)', icon: Briefcase },
    { title: 'Ollama Hardware Stress Test', desc: 'Run a 500-token inference speed diagnostic', icon: Terminal }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <Bot className="w-3.5 h-3.5 text-blue-400" />
            <span>SAARTHI COPILOT • FULL-SCREEN WORKSPACE</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Local Career Assistant
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Dedicated career strategist powered by {activeModel.name}. All chat history is stored strictly in your local sandbox.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="success" size="sm" dot>
            100% On-Device ({hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} tok/s` : 'Not benchmarked'})
          </Badge>
        </div>
      </div>

      {/* Main Chat Box */}
      <Card variant="default" padding="none" className="h-[620px] flex flex-col overflow-hidden">
        {/* Top Info Banner */}
        <div className="p-3 bg-[var(--bg-surface-elevated)]/40 border-b border-[var(--border-subtle)] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-[var(--text-secondary)] text-[11px]">
              Local Memory Active: <strong className="text-[var(--text-primary)]">{activeResume?.title || 'Untitled Resume'}</strong>, {applications.length} Applications
            </span>
          </div>
          <span className="text-[10px] font-mono text-[var(--text-muted)]">
            Model: {activeModel.name.split(' ')[0]} (Q4_K_M)
          </span>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
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
                  className={`p-4 rounded-[var(--radius-lg)] text-xs leading-relaxed max-w-[85%] whitespace-pre-wrap ${
                    isUser
                      ? 'bg-[var(--accent-primary)] text-white font-medium'
                      : 'bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border-subtle)]'
                  }`}
                >
                  {msg.text}
                </div>

                {!isUser && (
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={() => handleCopy(msg.text, msg.id)}
                      className="flex items-center gap-1 px-2 py-0.5 text-[10px] text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded bg-[var(--bg-subtle)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] cursor-pointer"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Response</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            );
          })}

          {isAssistantThinking && (
            <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)] p-3 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)]">
              <span className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span>Generating response locally on {hardware.gpu}...</span>
            </div>
          )}
        </div>

        {/* Starter Prompts */}
        <div className="p-3 border-t border-[var(--border-subtle)] bg-[var(--bg-subtle)]/50">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
            {promptStarters.map((p, i) => {
              const Icon = p.icon;
              return (
                <button
                  key={i}
                  onClick={() => sendAssistantMessage(p.desc)}
                  className="p-2.5 rounded-[var(--radius-md)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border border-[var(--border-subtle)] hover:border-blue-500/30 text-left transition-all cursor-pointer space-y-0.5"
                >
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--text-primary)]">
                    <Icon className="w-3.5 h-3.5 text-blue-400" />
                    <span className="truncate">{p.title}</span>
                  </div>
                  <p className="text-[10px] text-[var(--text-muted)] truncate">{p.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSend} className="p-3 border-t border-[var(--border-subtle)] bg-[var(--bg-surface)] flex gap-2">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Ask anything about your resume, applications, interview practice, or career strategy..."
            className="flex-1 bg-[var(--bg-subtle)] text-[var(--text-primary)] border border-[var(--border-strong)] focus:border-blue-500 rounded-[var(--radius-md)] px-4 py-2.5 text-xs placeholder:text-[var(--text-muted)] focus:outline-none"
          />
          <Button
            variant="ai"
            type="submit"
            icon={Send}
            disabled={!inputVal.trim() || isAssistantThinking}
          >
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
};
