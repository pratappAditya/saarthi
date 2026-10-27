import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Paperclip,
  ChevronDown,
  ChevronUp,
  FileText,
  Brain,
  ShieldAlert,
  Copy,
  Terminal,
} from "lucide-react";
import type { Message, SaarthiState } from "../../types";
import { ToolCard } from "../tools/ToolCard";
import { SaarthiOrb } from "../common/SaarthiOrb";

const parseInlineMarkdown = (text: string): React.ReactNode[] => {
  let parts: any[] = [text];

  parts = parts.flatMap((part) => {
    if (typeof part !== "string") return [part];
    const subParts = part.split(/(`[^`]+`)/g);
    return subParts.map((sub) => {
      if (sub.startsWith("`") && sub.endsWith("`")) {
        return (
          <code key={sub} className="px-1.5 py-0.5 rounded bg-black/80 text-[#F59E0B] font-mono text-[10px] border border-white/5 font-semibold">
            {sub.slice(1, -1)}
          </code>
        );
      }
      return sub;
    });
  });

  parts = parts.flatMap((part) => {
    if (typeof part !== "string") return [part];
    const subParts = part.split(/(\*\*[^*]+\*\*)/g);
    return subParts.map((sub) => {
      if (sub.startsWith("**") && sub.endsWith("**")) {
        return (
          <strong key={sub} className="font-bold text-white">
            {sub.slice(2, -2)}
          </strong>
        );
      }
      return sub;
    });
  });

  parts = parts.flatMap((part) => {
    if (typeof part !== "string") return [part];
    const subParts = part.split(/(\[[^\]]+\]\([^)]+\))/g);
    return subParts.map((sub) => {
      const match = sub.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (match) {
        return (
          <a
            key={sub}
            href={match[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#F59E0B] hover:underline inline-flex items-center gap-0.5"
          >
            {match[1]}
          </a>
        );
      }
      return sub;
    });
  });

  return parts;
};

const renderMarkdown = (text: string) => {
  if (!text) return null;

  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts.map((part, idx) => {
    if (part.startsWith("```") && part.endsWith("```")) {
      const match = part.match(/```(\w*)\n([\s\S]*?)```/);
      const language = match ? match[1] : "";
      const code = match ? match[2].trim() : part.slice(3, -3).trim();

      return (
        <div key={idx} className="my-2 rounded-xl border border-white/10 bg-black/60 overflow-hidden font-mono text-[11px]">
          <div className="flex items-center justify-between px-3 py-1.5 bg-[#141414] border-b border-white/5 text-[9px] text-white/40 uppercase font-semibold tracking-wider select-none">
            <span>{language || "code"}</span>
            <button
              onClick={() => navigator.clipboard.writeText(code)}
              className="hover:text-white transition-colors cursor-pointer"
              title="Copy code block"
            >
              Copy
            </button>
          </div>
          <pre className="p-3 overflow-x-auto text-[#F59E0B] leading-normal font-mono select-text">
            <code>{code}</code>
          </pre>
        </div>
      );
    }

    const lines = part.split("\n");
    return (
      <div key={idx} className="space-y-1">
        {lines.map((line, lIdx) => {
          if (line.startsWith("### ")) {
            return <h4 key={lIdx} className="text-xs font-bold text-white tracking-wide mt-2.5 mb-0.5">{line.slice(4)}</h4>;
          }
          if (line.startsWith("## ")) {
            return <h3 key={lIdx} className="text-sm font-bold text-white tracking-wide mt-3 mb-1">{line.slice(3)}</h3>;
          }
          if (line.startsWith("- ") || line.startsWith("* ")) {
            return (
              <li key={lIdx} className="list-disc list-inside ml-1 text-white/80 leading-relaxed text-xs">
                {parseInlineMarkdown(line.slice(2))}
              </li>
            );
          }
          const numMatch = line.match(/^(\d+)\.\s(.*)/);
          if (numMatch) {
            return (
              <li key={lIdx} className="list-decimal list-inside ml-1 text-white/80 leading-relaxed text-xs">
                {parseInlineMarkdown(numMatch[2])}
              </li>
            );
          }
          if (!line.trim()) {
            return <div key={lIdx} className="h-1.5" />;
          }
          return (
            <p key={lIdx} className="leading-relaxed text-xs text-white/85">
              {parseInlineMarkdown(line)}
            </p>
          );
        })}
      </div>
    );
  });
};

interface ChatCanvasProps {
  messages: Message[];
  onSendMessage: (text: string, files?: File[]) => void;
  saarthiState: SaarthiState;
  onApproveTool?: (toolId: string) => void;
  onDenyTool?: (toolId: string) => void;
  onOpenPermissionDemo?: () => void;
  onApproveMemory?: (requestId: string, messageId: string) => void;
  onDenyMemory?: (requestId: string, messageId: string) => void;
}

export const ChatCanvas: React.FC<ChatCanvasProps> = ({
  messages,
  onSendMessage,
  saarthiState,
  onApproveTool,
  onDenyTool,
  onOpenPermissionDemo,
  onApproveMemory,
  onDenyMemory,
}) => {
  const [inputText, setInputText] = useState("");
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [expandedThinking, setExpandedThinking] = useState<Record<string, boolean>>({});
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, saarthiState]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() && attachedFiles.length === 0) return;
    onSendMessage(inputText, attachedFiles);
    setInputText("");
    setAttachedFiles([]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachedFiles(Array.from(e.target.files));
    }
  };

  const toggleThinking = (msgId: string) => {
    setExpandedThinking((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleQuickPrompt = (promptText: string) => {
    onSendMessage(promptText);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0A0A] overflow-hidden select-none">
      {/* Conversational Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {/* Quick Action Suggestion Chips */}
        <div className="max-w-3xl mx-auto flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button
            onClick={() => handleQuickPrompt("Evaluate my resume for high-impact gaps and ATS keyword missing items.")}
            className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-[#F59E0B] shrink-0 font-mono transition-all cursor-pointer"
          >
            ✦ Evaluate Resume Gaps
          </button>
          <button
            onClick={() => handleQuickPrompt("Simulate a System Design panel interview drill for distributed cache architecture.")}
            className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-blue-400 shrink-0 font-mono transition-all cursor-pointer"
          >
            ✦ Simulate System Design Panel
          </button>
          <button
            onClick={() => handleQuickPrompt("Generate an executive salary negotiation script with quantitative equity and base anchors.")}
            className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-emerald-400 shrink-0 font-mono transition-all cursor-pointer"
          >
            ✦ Salary Negotiation Script
          </button>
          <button
            onClick={() => handleQuickPrompt("Run a hardware benchmark on Ollama Nemotron model inference speed.")}
            className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs text-purple-400 shrink-0 font-mono transition-all cursor-pointer"
          >
            ✦ Hardware Benchmark
          </button>
        </div>

        {messages.map((msg) => {
          const isSaarthi = msg.sender === "saarthi";
          const isSystem = msg.sender === "system";

          if (isSystem) {
            return (
              <div
                key={msg.id}
                className="mx-auto max-w-xl p-2.5 rounded-xl bg-[#0D0D0D] border border-white/5 text-center text-xs font-mono text-white/40"
              >
                {msg.text}
              </div>
            );
          }

          return (
            <div
              key={msg.id}
              className={`max-w-3xl mx-auto flex gap-3 ${
                isSaarthi ? "items-start" : "items-start flex-row-reverse"
              }`}
            >
              {/* Avatar Emblem */}
              {isSaarthi ? (
                <div className="w-8 h-8 rounded-lg bg-[#F59E0B] flex items-center justify-center shrink-0 shadow-[0_0_12px_rgba(245,158,11,0.3)]">
                  <div className="w-4 h-4 border-2 border-black rounded-full flex items-center justify-center">
                    <div className="w-1 h-1 bg-black rounded-full" />
                  </div>
                </div>
              ) : (
                <div className="w-8 h-8 rounded-lg bg-[#141414] border border-white/10 flex items-center justify-center shrink-0 text-xs font-bold text-white/80 font-mono">
                  YOU
                </div>
              )}

              {/* Message Content Container */}
              <div
                className={`flex-1 min-w-0 space-y-3 ${
                  isSaarthi ? "text-white/90" : "text-white"
                }`}
              >
                {/* Header Metadata */}
                <div
                  className={`flex items-center gap-2 text-[11px] font-mono text-white/30 w-full ${
                    isSaarthi ? "justify-start" : "justify-end"
                  }`}
                >
                  <span className="font-semibold text-white/60">
                    {isSaarthi ? "SAARTHI" : "YOU"}
                  </span>
                  <span>• {msg.timestamp}</span>
                  {msg.modelUsed && (
                    <span className="text-[#F59E0B] bg-[#141414] px-2 py-0.5 rounded border border-white/5">
                      {msg.modelUsed}
                    </span>
                  )}
                  {msg.executionTimeMs && (
                    <span className="text-white/30">
                      ({msg.executionTimeMs}ms)
                    </span>
                  )}
                  {isSaarthi && (
                    <button
                      onClick={() => navigator.clipboard.writeText(msg.text || '')}
                      className="ml-auto hover:text-[#F59E0B] transition-colors cursor-pointer text-white/30 p-1 rounded flex items-center gap-1 bg-[#141414] border border-white/5 px-2"
                      title="Copy response text"
                    >
                      <Copy size={11} />
                      <span className="text-[9px] font-bold">COPY</span>
                    </button>
                  )}
                </div>

                {/* Agent Reasoning Steps */}
                {isSaarthi && msg.thinkingSteps && msg.thinkingSteps.length > 0 && (
                  <div className="rounded-xl bg-[#0D0D0D] border border-white/5 overflow-hidden text-xs">
                    <button
                      onClick={() => toggleThinking(msg.id)}
                      className="w-full px-3 py-2 flex items-center justify-between text-white/40 hover:text-white font-mono text-[11px] bg-[#141414] cursor-pointer"
                      type="button"
                    >
                      <span className="flex items-center gap-1.5 font-semibold">
                        <Terminal size={12} className="text-[#F59E0B]" />
                        TECHNICAL EXECUTION LOG
                      </span>
                      {expandedThinking[msg.id] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                    {expandedThinking[msg.id] && (
                      <div className="p-3 bg-black/80 font-mono text-[10px] text-white/70 overflow-x-auto leading-relaxed border-t border-white/5 space-y-1 max-h-48 scrollbar-thin">
                        {msg.thinkingSteps.map((step, idx) => (
                          <div key={idx} className="whitespace-pre-wrap">{step}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Tool Executions */}
                {msg.toolExecution && (
                  <div className="space-y-2">
                    <ToolCard
                      tool={msg.toolExecution}
                      onApprove={() => onApproveTool && onApproveTool(msg.toolExecution!.id)}
                      onDeny={() => onDenyTool && onDenyTool(msg.toolExecution!.id)}
                    />
                  </div>
                )}

                {/* Memory Request Box */}
                {msg.memoryRequest && (
                  <div className="p-3.5 rounded-xl bg-[#141414] border border-[#F59E0B]/30 space-y-3">
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#F59E0B] uppercase font-bold">
                      <Brain size={14} /> MEMORY TRANSACTION PENDING
                    </div>
                    <div className="space-y-1">
                      <span className="text-[9px] font-mono text-white/30 uppercase tracking-widest block">
                        What Saarthi wants to remember:
                      </span>
                      <p className="text-white/90 font-medium font-mono text-xs p-2.5 rounded bg-black border border-white/5">
                        "{msg.memoryRequest.content}"
                      </p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-[9px] font-mono text-white/30 uppercase tracking-widest block">
                        Why it may be useful:
                      </span>
                      <p className="text-white/60 text-xs">
                        Keeps context around user preferences, rules, or environment details dynamically synced for future conversations.
                      </p>
                    </div>
                    {msg.memoryRequest.status === "pending" && (
                      <div className="flex items-center gap-2 pt-1.5">
                        <button
                          type="button"
                          onClick={() => onDenyMemory && onDenyMemory(msg.memoryRequest.request_id, msg.id)}
                          className="px-3 py-1 rounded bg-white/5 hover:bg-white/10 text-white/70 text-xs font-mono border border-white/5 cursor-pointer"
                        >
                          Ignore
                        </button>
                        <button
                          type="button"
                          onClick={() => onApproveMemory && onApproveMemory(msg.memoryRequest.request_id, msg.id)}
                          className="px-3 py-1 rounded bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-black text-xs font-mono font-semibold cursor-pointer"
                        >
                          Remember
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Message Body Text */}
                <div
                  className={`p-4 rounded-2xl ${
                    isSaarthi
                      ? "bg-[#0D0D0D] border border-white/5 text-white/90"
                      : "bg-[#F59E0B]/15 border border-[#F59E0B]/30 text-white"
                  } leading-relaxed text-sm font-sans space-y-3 shadow-sm select-text`}
                >
                  {renderMarkdown(msg.text || '')}
                </div>

                {/* Citations / Source Cards */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-1 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/30">
                      LOCAL SOURCES / CITATIONS
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.citations.map((cit) => (
                        <div
                          key={cit.id}
                          className="p-3 rounded-xl bg-[#0D0D0D] border border-white/5 text-xs hover:border-[#F59E0B]/30 transition-all"
                        >
                          <div className="font-medium text-[#F59E0B] truncate">
                            {cit.title}
                          </div>
                          <div className="text-[10px] font-mono text-white/40 truncate mt-0.5">
                            {cit.source}
                          </div>
                          <p className="text-[11px] text-white/50 line-clamp-2 mt-1">
                            "{cit.snippet}"
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Live Thinking State Indicator */}
        {(String(saarthiState) === "thinking" || String(saarthiState) === "tool_executing") && (
          <div className="max-w-3xl mx-auto flex items-center gap-3 p-3 rounded-2xl bg-[#0D0D0D] border border-[#F59E0B]/30 animate-pulse">
            <SaarthiOrb
              state={(() => {
                const latestMessage = messages[messages.length - 1];
                const activeTool = latestMessage && latestMessage.sender === "saarthi" && latestMessage.toolExecution;
                if (String(saarthiState) === "tool_executing" && activeTool) {
                  if (activeTool.name.includes("file")) return "reading_files";
                  if (activeTool.name.includes("memory")) return "reading_memory";
                  return "running_tool";
                }
                return "thinking";
              })()}
              size="sm"
            />
            <div className="font-mono text-xs text-[#F59E0B] flex flex-col">
              <span className="font-semibold">SAARTHI AGENT AT WORK</span>
              <span className="text-white/40 text-[11px]">
                {(() => {
                  const latestMessage = messages[messages.length - 1];
                  const activeTool = latestMessage && latestMessage.sender === "saarthi" && latestMessage.toolExecution;
                  if (String(saarthiState) === "tool_executing" && activeTool) {
                    if (activeTool.name.includes("file")) {
                      return "Reading workspace file context...";
                    } else if (activeTool.name.includes("memory")) {
                      return "Accessing localized memory tables...";
                    } else {
                      return `Executing tool: ${activeTool.name}...`;
                    }
                  } else if (String(saarthiState) === "thinking") {
                    return "Analyzing parameters & planning next action...";
                  }
                  return "Evaluating local memory and files...";
                })()}
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Form Bar */}
      <div className="p-4 bg-[#0A0A0A] border-t border-white/5">
        <form
          onSubmit={handleSubmit}
          className="max-w-3xl mx-auto relative flex flex-col gap-2 rounded-2xl bg-[#141414] border border-white/10 focus-within:border-[#F59E0B]/80 p-3 transition-all shadow-xl"
        >
          {/* File Capsule Attachments Preview */}
          {attachedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 px-2 pt-1 pb-2 border-b border-white/5">
              {attachedFiles.map((f, i) => (
                <div
                  key={i}
                  className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-[#F59E0B] flex items-center gap-2"
                >
                  <FileText size={12} />
                  <span className="truncate max-w-[150px]">{f.name}</span>
                  <span className="text-[10px] text-white/40">
                    ({(f.size / 1024).toFixed(0)} KB)
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2">
            <label className="p-2 rounded-xl text-white/40 hover:text-[#F59E0B] hover:bg-white/5 cursor-pointer transition-colors">
              <Paperclip size={18} />
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>

            <textarea
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask Saarthi, run a command, or analyze local files..."
              className="flex-1 bg-transparent text-white placeholder-white/20 text-sm focus:outline-none resize-none py-1.5 font-sans"
            />

            {/* Permission Simulator Button */}
            <button
              type="button"
              onClick={onOpenPermissionDemo}
              className="px-2.5 py-1.5 rounded-xl bg-[#F59E0B]/10 hover:bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30 text-xs font-mono flex items-center gap-1 transition-all cursor-pointer"
              title="Demo Permission Request Dialog"
            >
              <ShieldAlert size={14} />
              <span className="hidden sm:inline">Demo Permission</span>
            </button>

            <button
              type="submit"
              disabled={!inputText.trim() && attachedFiles.length === 0}
              className="p-2.5 rounded-xl bg-[#F59E0B] hover:bg-[#F59E0B]/90 disabled:opacity-30 text-black font-semibold transition-all cursor-pointer shadow-[0_0_12px_rgba(245,158,11,0.3)]"
            >
              <Send size={16} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

