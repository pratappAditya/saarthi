import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Send,
  Check,
  AlertCircle,
  X,
  Command,
  FileText,
  CornerDownLeft,
  ArrowRight,
  Shield,
  Settings,
  Mic,
  MicOff,
  Copy,
  CheckCircle2,
  ExternalLink,
  Layers,
  ChevronDown,
  Info,
  Square,
  Volume2,
  VolumeX,
  Globe
} from 'lucide-react';

export type DesktopState =
  | 'IDLE'
  | 'READY'
  | 'LISTENING'
  | 'PROCESSING'
  | 'THINKING'
  | 'SPEAKING'
  | 'COMPLETED'
  | 'ERROR';

export interface ActiveAppInfo {
  app_name: string;
  bundle_id?: string;
  window_title?: string;
  is_accessible: boolean;
  focused_field_available?: boolean;
}

export interface FloatingSaarthiUIProps {
  initialState?: DesktopState;
  onClose?: () => void;
  standalone?: boolean;
}

export const FloatingSaarthiUI: React.FC<FloatingSaarthiUIProps> = ({
  initialState = 'READY',
  onClose,
  standalone = false
}) => {
  const [currentState, setCurrentState] = useState<DesktopState>(initialState);
  const [prompt, setPrompt] = useState('');
  const [activeApp, setActiveApp] = useState<ActiveAppInfo>({
    app_name: 'Visual Studio Code',
    bundle_id: 'com.microsoft.VSCode',
    window_title: 'SaarthiDesktop.py — Saarthi',
    is_accessible: true,
    focused_field_available: true
  });
  const [selectedText, setSelectedText] = useState<string>(
    'def execute_command(self, prompt: str):\n    return self.pipeline.execute_request(prompt)'
  );
  const [response, setResponse] = useState<string | null>(null);
  const [insertionStatus, setInsertionStatus] = useState<
    'NONE' | 'SUPPORTED' | 'UNSUPPORTED' | 'PERMISSION_REQUIRED' | 'FAILED' | 'INSERTED'
  >('NONE');
  const [autoInsert, setAutoInsert] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Saarthi Desktop Ready');
  const [showSettings, setShowSettings] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shortcutKey, setShortcutKey] = useState('Fn');
  const [shortcutMode, setShortcutMode] = useState<'TOGGLE_TO_ACTIVATE' | 'HOLD_TO_ACTIVATE'>(
    'TOGGLE_TO_ACTIVATE'
  );
  const [voiceSessionId, setVoiceSessionId] = useState<string | null>(null);
  const [voiceLanguage, setVoiceLanguage] = useState<'en-IN' | 'hi-IN' | 'hi-en'>('en-IN');
  const [isBargeInActive, setIsBargeInActive] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (currentState === 'READY' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [currentState]);

  const handleActionClick = (actionName: string) => {
    let actionPrompt = '';
    if (actionName === 'rewrite') {
      actionPrompt = 'Rewrite this code with clear docstrings and error handling.';
    } else if (actionName === 'explain') {
      actionPrompt = 'Explain what this code block is doing step by step.';
    } else if (actionName === 'summarize') {
      actionPrompt = 'Summarize this concisely.';
    } else if (actionName === 'translate') {
      actionPrompt = 'Translate / explain this in conversational Hinglish.';
    }
    setPrompt(actionPrompt);
    submitCommand(actionPrompt, actionName);
  };

  const handleVoiceToggle = async () => {
    if (currentState === 'LISTENING') {
      // User finished speaking, send turn
      if (!prompt.trim()) {
        setCurrentState('READY');
        setStatusMessage('Listening stopped');
        return;
      }
      submitCommand(prompt, 'voice');
    } else if (currentState === 'SPEAKING') {
      // Barge-in: interrupt speaking
      handleBargeIn();
    } else {
      // Start listening
      try {
        setCurrentState('LISTENING');
        setStatusMessage(`Listening (${voiceLanguage})... Speak now`);
        const res = await fetch('/api/voice/session/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'default_local_user', push_to_talk: true })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.session?.session_id) {
            setVoiceSessionId(data.session.session_id);
          }
        }
      } catch {
        setCurrentState('LISTENING');
        setStatusMessage(`Listening (${voiceLanguage})... Speak now`);
      }
    }
  };

  const handleBargeIn = async () => {
    setIsBargeInActive(true);
    setStatusMessage('Interrupted Saarthi speech (Barge-in). Listening...');
    setCurrentState('LISTENING');
    if (voiceSessionId) {
      try {
        await fetch('/api/voice/session/interrupt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: voiceSessionId, cancel_agent_task: false })
        });
      } catch {
        // Safe ignore
      }
    }
    setTimeout(() => setIsBargeInActive(false), 1500);
  };

  const submitCommand = async (userPrompt?: string, actionType: string = 'chat') => {
    const textToSend = userPrompt || prompt;
    if (!textToSend.trim()) return;

    setCurrentState('PROCESSING');
    setStatusMessage('Analyzing application context...');
    setResponse(null);
    setInsertionStatus('NONE');

    setTimeout(() => {
      setCurrentState('THINKING');
      setStatusMessage('Saarthi Intelligence generating solution...');
    }, 400);

    try {
      const res = await fetch('/api/desktop/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: textToSend,
          action: actionType,
          active_application: activeApp,
          selected_text: selectedText || null,
          auto_insert_requested: autoInsert
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP error ${res.status}`);
      }

      const data = await res.json();
      const outputText = data.response || data.message || 'Operation processed successfully.';
      setResponse(outputText);
      
      // If voice turn, transition through SPEAKING then COMPLETED
      if (actionType === 'voice') {
        setCurrentState('SPEAKING');
        setStatusMessage('Saarthi speaking response... (Click mic to interrupt)');
        setTimeout(() => {
          setCurrentState('COMPLETED');
          setStatusMessage('Task completed successfully');
        }, 3000);
      } else {
        setCurrentState('COMPLETED');
        setStatusMessage('Task completed successfully');
      }

      if (autoInsert) {
        setInsertionStatus('INSERTED');
      } else {
        setInsertionStatus('SUPPORTED');
      }
    } catch (err: any) {
      setCurrentState('ERROR');
      setStatusMessage('Failed to execute command: ' + (err.message || 'Connection error'));
    }
  };

  const handleDirectInsert = async () => {
    if (!response) return;
    try {
      const res = await fetch('/api/desktop/insert-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: response,
          target_app: activeApp.app_name,
          target_bundle_id: activeApp.bundle_id
        })
      });
      if (res.ok) {
        setInsertionStatus('INSERTED');
      } else {
        setInsertionStatus('FAILED');
      }
    } catch {
      setInsertionStatus('FAILED');
    }
  };

  const copyToClipboard = () => {
    if (response) {
      navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getStateColor = () => {
    switch (currentState) {
      case 'IDLE':
        return 'border-slate-700/50 bg-slate-900/80 shadow-slate-950/50';
      case 'READY':
        return 'border-cyan-500/40 bg-slate-950/95 shadow-cyan-950/40 ring-1 ring-cyan-500/20';
      case 'LISTENING':
        return 'border-amber-500/60 bg-slate-950/95 shadow-amber-950/50 ring-2 ring-amber-500/40';
      case 'PROCESSING':
        return 'border-indigo-500/50 bg-slate-950/95 shadow-indigo-950/40 ring-1 ring-indigo-500/20';
      case 'THINKING':
        return 'border-purple-500/50 bg-slate-950/95 shadow-purple-950/40 ring-1 ring-purple-500/30';
      case 'SPEAKING':
        return 'border-teal-500/60 bg-slate-950/95 shadow-teal-950/50 ring-2 ring-teal-500/40 animate-pulse';
      case 'COMPLETED':
        return 'border-emerald-500/50 bg-slate-950/95 shadow-emerald-950/40 ring-1 ring-emerald-500/20';
      case 'ERROR':
        return 'border-rose-500/50 bg-slate-950/95 shadow-rose-950/40 ring-1 ring-rose-500/20';
    }
  };

  return (
    <div
      className={`w-full max-w-xl mx-auto rounded-2xl border backdrop-blur-2xl transition-all duration-300 overflow-hidden text-slate-100 shadow-2xl ${getStateColor()} ${
        standalone ? 'p-0' : 'm-4'
      }`}
    >
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/80 bg-slate-900/60">
        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 shadow-md shadow-cyan-900/30">
            <Sparkles className="w-4 h-4 text-white" />
            {(currentState === 'THINKING' || currentState === 'SPEAKING') && (
              <span className="absolute -inset-1 rounded-lg bg-cyan-400/30 animate-ping" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold tracking-wider uppercase bg-gradient-to-r from-cyan-300 via-indigo-300 to-purple-300 bg-clip-text text-transparent">
                Saarthi Companion
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800/60 font-mono text-cyan-300 font-semibold">
                Voice 2.0
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Language Selector Capsule */}
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-800/90 border border-slate-700 text-[11px] text-slate-300">
            <Globe className="w-3 h-3 text-cyan-400" />
            <select
              value={voiceLanguage}
              onChange={(e) => setVoiceLanguage(e.target.value as any)}
              className="bg-transparent text-slate-300 border-none outline-none text-[11px] cursor-pointer"
            >
              <option value="en-IN" className="bg-slate-900 text-slate-200">English (India)</option>
              <option value="hi-IN" className="bg-slate-900 text-slate-200">Hindi (हिंदी)</option>
              <option value="hi-en" className="bg-slate-900 text-slate-200">Hinglish</option>
            </select>
          </div>

          {/* Active App Badge */}
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-[11px] text-slate-300 max-w-[160px] truncate"
            title={`Active Window: ${activeApp.window_title || activeApp.app_name}`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
            <span className="font-medium truncate">{activeApp.app_name}</span>
          </div>

          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            title="Desktop Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
              title="Hide Companion"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="p-4 space-y-3.5">
        {/* State Banner / Notice */}
        {currentState === 'LISTENING' && (
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-amber-950/40 border border-amber-600/40 text-amber-200 text-xs animate-pulse">
            <div className="flex items-center gap-2">
              <Mic className="w-4 h-4 text-amber-400 shrink-0 animate-bounce" />
              <span>
                <strong>Microphone Active:</strong> Capturing {voiceLanguage === 'hi-IN' ? 'Hindi' : voiceLanguage === 'hi-en' ? 'Hinglish' : 'Indian English'} speech...
              </span>
            </div>
            <button
              onClick={handleVoiceToggle}
              className="px-2 py-0.5 rounded bg-amber-800/60 border border-amber-600/60 hover:bg-amber-700/60 text-amber-100 font-medium text-[11px] transition"
            >
              Stop &amp; Process
            </button>
          </div>
        )}

        {currentState === 'SPEAKING' && (
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-teal-950/40 border border-teal-600/50 text-teal-200 text-xs">
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-teal-400 shrink-0 animate-pulse" />
              <span>
                <strong>Saarthi Speaking:</strong> Neural voice active.
              </span>
            </div>
            <button
              onClick={handleBargeIn}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-rose-900/80 border border-rose-600 hover:bg-rose-800 text-rose-100 font-semibold text-[11px] transition shadow-md shadow-rose-950/50"
              title="Barge-in / Interrupt Speech"
            >
              <Square className="w-3 h-3 fill-current" />
              Interrupt (Barge-in)
            </button>
          </div>
        )}

        {/* Selected Text Pill (Context) */}
        {selectedText && (
          <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5 font-medium text-cyan-400">
                <FileText className="w-3.5 h-3.5" />
                Selected Context ({selectedText.length} chars)
              </span>
              <button
                onClick={() => setSelectedText('')}
                className="text-slate-500 hover:text-slate-300 text-[10px]"
              >
                Clear Context
              </button>
            </div>
            <p className="font-mono text-[11px] text-slate-300 line-clamp-2 bg-slate-950/60 p-2 rounded border border-slate-800/80">
              {selectedText}
            </p>

            {/* Quick Context Action Chips */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              <button
                onClick={() => handleActionClick('rewrite')}
                className="px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-700/50 hover:bg-cyan-900/60 text-cyan-200 text-[11px] transition font-medium"
              >
                ✨ Rewrite
              </button>
              <button
                onClick={() => handleActionClick('explain')}
                className="px-2.5 py-1 rounded-lg bg-indigo-950/60 border border-indigo-700/50 hover:bg-indigo-900/60 text-indigo-200 text-[11px] transition font-medium"
              >
                💡 Explain
              </button>
              <button
                onClick={() => handleActionClick('summarize')}
                className="px-2.5 py-1 rounded-lg bg-purple-950/60 border border-purple-700/50 hover:bg-purple-900/60 text-purple-200 text-[11px] transition font-medium"
              >
                📑 Summarize
              </button>
              <button
                onClick={() => handleActionClick('translate')}
                className="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-700/50 hover:bg-emerald-900/60 text-emerald-200 text-[11px] transition font-medium"
              >
                🇮🇳 Hindi / Hinglish
              </button>
            </div>
          </div>
        )}

        {/* Prompt Input Box & Microphone Button */}
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                submitCommand();
              }
            }}
            placeholder={
              currentState === 'LISTENING'
                ? `Transcribing live voice (${voiceLanguage})...`
                : selectedText
                ? `Ask Saarthi about selected text or speak...`
                : `What would you like Saarthi to do in ${activeApp.app_name}?`
            }
            className={`w-full px-4 py-3 pr-28 rounded-xl bg-slate-900/90 border transition text-sm placeholder:text-slate-500 shadow-inner ${
              currentState === 'LISTENING'
                ? 'border-amber-500/80 focus:ring-amber-500'
                : 'border-slate-700/70 focus:border-cyan-500 focus:ring-cyan-500'
            }`}
          />

          <div className="absolute right-2 top-2 flex items-center gap-1.5">
            {/* Live Microphone Button */}
            <button
              onClick={handleVoiceToggle}
              className={`p-1.5 rounded-lg transition shadow-md ${
                currentState === 'LISTENING'
                  ? 'bg-amber-600 hover:bg-amber-500 text-white animate-pulse shadow-amber-950/50'
                  : currentState === 'SPEAKING'
                  ? 'bg-teal-600 hover:bg-teal-500 text-white'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
              title={
                currentState === 'LISTENING'
                  ? 'Stop Recording'
                  : currentState === 'SPEAKING'
                  ? 'Interrupt Speaking'
                  : 'Hold or Click to Speak'
              }
            >
              {currentState === 'LISTENING' ? (
                <Mic className="w-4 h-4 text-white" />
              ) : (
                <Mic className="w-4 h-4 text-slate-300" />
              )}
            </button>

            <button
              onClick={() => submitCommand()}
              disabled={!prompt.trim() || currentState === 'THINKING'}
              className="p-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition shadow-md shadow-cyan-900/30"
              title="Execute Command (Enter)"
            >
              <CornerDownLeft className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Auto-Insert Toggle & Status Bar */}
        <div className="flex items-center justify-between text-xs px-1 text-slate-400">
          <label className="flex items-center gap-2 cursor-pointer hover:text-slate-300">
            <input
              type="checkbox"
              checked={autoInsert}
              onChange={(e) => setAutoInsert(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-cyan-600 focus:ring-0 focus:ring-offset-0"
            />
            <span>Auto-insert generated text into {activeApp.app_name}</span>
          </label>

          <span className="text-[11px] font-mono text-slate-500 flex items-center gap-1">
            <Command className="w-3 h-3" /> {shortcutKey}
          </span>
        </div>

        {/* Output Result Card */}
        {response && (
          <div className="p-3.5 rounded-xl bg-slate-900/95 border border-slate-800 text-sm space-y-3 animate-in fade-in duration-200">
            <div className="flex items-center justify-between text-xs border-b border-slate-800/80 pb-2">
              <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Saarthi Output
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] transition"
                  title="Copy text"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-300" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>

                <button
                  onClick={handleDirectInsert}
                  className="flex items-center gap-1 px-2.5 py-0.5 rounded bg-cyan-700 hover:bg-cyan-600 text-white text-[11px] font-medium transition"
                  title="Direct Text Insertion"
                >
                  <ArrowRight className="w-3 h-3" />
                  <span>Insert into {activeApp.app_name}</span>
                </button>
              </div>
            </div>

            <div className="text-slate-200 text-xs leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap font-sans">
              {response}
            </div>

            {/* Insertion Status Notification */}
            {insertionStatus !== 'NONE' && (
              <div className="flex items-center gap-2 pt-1 text-[11px]">
                {insertionStatus === 'INSERTED' && (
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Successfully inserted into {activeApp.app_name}
                  </span>
                )}
                {insertionStatus === 'SUPPORTED' && (
                  <span className="text-slate-400">
                    Text ready. Click &quot;Insert into {activeApp.app_name}&quot; to inject at cursor.
                  </span>
                )}
                {insertionStatus === 'FAILED' && (
                  <span className="flex items-center gap-1 text-rose-400">
                    <AlertCircle className="w-3.5 h-3.5" /> Direct insertion failed. Please paste manually.
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Settings Drawer */}
        {showSettings && (
          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                <Settings className="w-3.5 h-3.5" /> Desktop Companion Settings
              </span>
              <button
                onClick={() => setShowSettings(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Global Shortcut</label>
                <select
                  value={shortcutKey}
                  onChange={(e) => setShortcutKey(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="Fn">Fn (Globe / Function)</option>
                  <option value="Control+Space">Control + Space</option>
                  <option value="Command+Shift+S">Command + Shift + S</option>
                  <option value="Alt+Space">Alt + Space</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Activation Mode</label>
                <select
                  value={shortcutMode}
                  onChange={(e) => setShortcutMode(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value="TOGGLE_TO_ACTIVATE">Toggle (Press to show/hide)</option>
                  <option value="HOLD_TO_ACTIVATE">Hold (Release to finish)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center gap-1 text-emerald-400">
                <Shield className="w-3.5 h-3.5" /> Voice Privacy: No Background Listening
              </span>
              <span>Saarthi v2.0-voice</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Status Line */}
      <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 font-mono">
        <span>STATUS: {statusMessage}</span>
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          VOICE OPERATING LAYER 2.0
        </span>
      </div>
    </div>
  );
};
