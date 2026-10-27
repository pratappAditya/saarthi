import React, { useState, useEffect } from 'react';
import { 
  Mic, MicOff, Volume2, Square, RefreshCw, Radio, Sparkles, Activity,
  Globe, ShieldCheck, Cpu, Zap, AlertTriangle, CheckCircle, Terminal, Play, Pause, Hand
} from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';

export const VoiceWorkspaceView: React.FC = () => {
  const { addToast } = useApp();
  const [session, setSession] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'compact' | 'full' | 'hands_free'>('full');
  const [voiceState, setVoiceState] = useState<string>('IDLE');
  const [transcript, setTranscript] = useState<string>('Ready for voice or hands-free turn...');
  const [assistantSpeech, setAssistantSpeech] = useState<string>('Namaste Pratap, I am Saarthi. Speak naturally in English or Hindi.');
  const [activeDomain, setActiveDomain] = useState<string>('general');
  const [metrics, setMetrics] = useState<any>(null);
  const [isPushToTalkActive, setIsPushToTalkActive] = useState<boolean>(false);
  const [isHandsFreeActive, setIsHandsFreeActive] = useState<boolean>(false);
  const [pendingApproval, setPendingApproval] = useState<any>(null);
  const [inputText, setInputText] = useState<string>('');

  useEffect(() => {
    fetchVoiceProfile();
  }, []);

  const fetchVoiceProfile = async () => {
    try {
      const res = await api.getVoiceProfile();
      if (res && res.profile) {
        // Voice profile initialized
      }
    } catch (e) {
      console.warn("Failed to load voice profile:", e);
    }
  };

  const handleStartSession = async (handsFree = false, pushToTalk = false) => {
    try {
      const res = await api.startVoiceSession(handsFree, pushToTalk);
      if (res && res.session) {
        setSession(res.session);
        setVoiceState(res.session.state || 'LISTENING');
        setIsHandsFreeActive(handsFree);
        setIsPushToTalkActive(pushToTalk);
        addToast({
          type: 'success',
          title: handsFree ? 'Hands-Free Mode Active' : 'Voice Session Active',
          message: 'Saarthi Voice Conversation Engine listening locally.'
        });
      } else {
        addToast({
          type: 'error',
          title: 'Voice Session Entitlement',
          message: 'Interactive voice sessions require PERSONAL, POWER, or TEAMS plan.'
        });
      }
    } catch (err: any) {
      addToast({
        type: 'error',
        title: 'Voice Session Failed',
        message: err.message || 'Could not start voice session.'
      });
    }
  };

  const handleStopSession = async () => {
    if (session?.session_id) {
      try {
        await api.stopVoiceSession(session.session_id);
      } catch (e) {}
    }
    setSession(null);
    setVoiceState('IDLE');
    setIsHandsFreeActive(false);
    setIsPushToTalkActive(false);
    setPendingApproval(null);
    addToast({
      type: 'info',
      title: 'Voice Session Ended',
      message: 'Cleaned up microphone resources.'
    });
  };

  const handleSendTurn = async (overrideText?: string) => {
    const textToSubmit = overrideText || inputText;
    if (!textToSubmit.trim() && !session?.session_id) return;

    if (!session) {
      await handleStartSession();
    }

    const sid = session?.session_id || 'vsession_active';
    setVoiceState('TRANSCRIBING');

    try {
      setVoiceState('THINKING');
      const res = await api.processVoiceTurn(
        sid,
        textToSubmit || "Explain this domain context in bilingual Hindi/English.",
        "en-IN",
        false
      );

      if (res.status === 'pending_approval') {
        setVoiceState('WAITING_FOR_APPROVAL');
        setPendingApproval(res.permission_request);
        setAssistantSpeech(res.assistant_text || "This action requires explicit approval.");
      } else if (res.status === 'success') {
        setVoiceState('SPEAKING');
        setAssistantSpeech(res.assistant_text);
        setActiveDomain(res.domain || 'general');
        setMetrics(res.metrics);
        setPendingApproval(null);
        if (overrideText || inputText) {
          setTranscript(textToSubmit);
          setInputText('');
        }
      }
    } catch (err: any) {
      setVoiceState('ERROR');
      addToast({
        type: 'error',
        title: 'Turn Error',
        message: err.message || 'Voice turn execution failed.'
      });
    }
  };

  const handleInterrupt = async () => {
    if (session?.session_id) {
      try {
        const res = await api.interruptVoiceSession(session.session_id, false);
        setVoiceState('INTERRUPTED');
        setTimeout(() => setVoiceState('LISTENING'), 600);
        addToast({
          type: 'info',
          title: 'Speech Interrupted (Barge-in)',
          message: 'Halted TTS speech output. Microphone restored to LISTENING.'
        });
      } catch (e) {}
    }
  };

  const handleApproveAction = async () => {
    if (!session?.session_id || !pendingApproval) return;
    try {
      await api.approvePermission(pendingApproval.request_id);
      setPendingApproval(null);
      addToast({
        type: 'success',
        title: 'Action Approved',
        message: 'Resuming high-risk voice action execution...'
      });
      handleSendTurn("Proceed with approved action.");
    } catch (err: any) {
      addToast({
        type: 'error',
        title: 'Approval Failed',
        message: err.message
      });
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#070a12] text-white p-6 space-y-6 overflow-y-auto font-sans">
      {/* Top Banner & Hands-Free Mode Indicator */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-purple-600/30 to-blue-600/30 border border-purple-500/40">
            <Radio className="w-6 h-6 text-purple-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">SAARTHI ADVANCED VOICE ENGINE</h1>
              <Badge variant="accent" size="sm">Phase 5H</Badge>
              {isHandsFreeActive && <Badge variant="success" size="sm">HANDS-FREE ACTIVE</Badge>}
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Native Indian English & Hindi voice intelligence, true barge-in, push-to-talk, and domain context.
            </p>
          </div>
        </div>

        {/* View Mode Selectors & Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('compact')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all cursor-pointer ${
              viewMode === 'compact' ? 'bg-purple-600 text-white font-bold' : 'bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            Compact
          </button>
          <button
            onClick={() => setViewMode('full')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all cursor-pointer ${
              viewMode === 'full' ? 'bg-purple-600 text-white font-bold' : 'bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            Full Workspace
          </button>
          <button
            onClick={() => setViewMode('hands_free')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all cursor-pointer ${
              viewMode === 'hands_free' ? 'bg-emerald-600 text-white font-bold' : 'bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            Hands-Free
          </button>
        </div>
      </div>

      {/* Persistent Hands-Free Bar when Hands-Free is active */}
      {isHandsFreeActive && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-blue-950/40 to-purple-950/40 border border-emerald-500/40 flex items-center justify-between shadow-lg animate-in fade-in">
          <div className="flex items-center gap-3">
            <Hand className="w-5 h-5 text-emerald-400 animate-bounce" />
            <div>
              <span className="text-xs font-bold text-emerald-300">Continuous Conversational Hands-Free Mode</span>
              <p className="text-[11px] text-gray-300">Speak naturally. Saarthi detects turns automatically with barge-in support.</p>
            </div>
          </div>
          <Button variant="outline" size="sm" icon={Square} onClick={() => handleStartSession(false, false)}>
            Stop Hands-Free
          </Button>
        </div>
      )}

      {/* Main Container View */}
      {viewMode === 'compact' ? (
        /* COMPACT VOICE WIDGET */
        <div className="max-w-md mx-auto w-full p-6 rounded-3xl bg-[#0d1222] border border-purple-500/30 space-y-4 shadow-2xl">
          <div className="flex items-center justify-between">
            <Badge variant={voiceState === 'SPEAKING' ? 'accent' : voiceState === 'LISTENING' ? 'success' : 'warning'}>
              {voiceState} MODE
            </Badge>
            <span className="text-[10px] text-gray-400 font-mono">saarthi_voice_hi_en</span>
          </div>

          <div className="flex items-center justify-center gap-1.5 h-12 py-2">
            {[30, 60, 90, 45, 75, 20, 80, 50, 95, 40].map((h, i) => (
              <div
                key={i}
                className="w-1.5 bg-gradient-to-t from-purple-500 to-blue-400 rounded-full animate-pulse"
                style={{ height: `${voiceState === 'LISTENING' ? h * 0.5 : voiceState === 'SPEAKING' ? h : 15}%` }}
              />
            ))}
          </div>

          <p className="text-xs text-gray-300 italic text-center font-mono">{transcript}</p>

          <div className="flex gap-2">
            <Button variant="primary" size="sm" icon={Mic} className="flex-1" onClick={() => handleStartSession(false, false)}>
              {session ? 'Active' : 'Start Mic'}
            </Button>
            <Button variant="outline" size="sm" icon={Square} onClick={handleInterrupt}>
              Barge-in
            </Button>
          </div>
        </div>
      ) : (
        /* FULL & HANDS-FREE WORKSPACE VIEW */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Visualizer & Session State */}
          <div className="lg:col-span-2 space-y-6">
            {/* Visualizer Card */}
            <div className="p-8 rounded-3xl bg-gradient-to-b from-[#0e1426] to-[#0a0e1a] border border-white/10 shadow-2xl relative overflow-hidden flex flex-col items-center justify-center space-y-6 min-h-[320px]">
              <div className="absolute top-4 left-4 flex items-center gap-2">
                <Badge variant={voiceState === 'LISTENING' ? 'success' : voiceState === 'SPEAKING' ? 'accent' : 'warning'}>
                  {voiceState}
                </Badge>
                <Badge variant="outline" size="sm">{activeDomain.toUpperCase()} DOMAIN</Badge>
              </div>

              <div className="absolute top-4 right-4 flex items-center gap-2 text-xs text-gray-400 font-mono">
                <Globe className="w-3.5 h-3.5 text-blue-400" />
                <span>en-IN / hi-IN</span>
              </div>

              {/* Large Animated Waveform Orb */}
              <div className="relative flex items-center justify-center py-6">
                <div className={`w-32 h-32 rounded-full bg-gradient-to-tr from-purple-600/40 via-blue-600/40 to-emerald-500/40 flex items-center justify-center transition-all duration-300 ${
                  voiceState === 'SPEAKING' ? 'scale-110 shadow-[0_0_50px_rgba(168,85,247,0.4)]' : voiceState === 'LISTENING' ? 'animate-pulse' : ''
                }`}>
                  <Activity className="w-12 h-12 text-purple-300 animate-pulse" />
                </div>
              </div>

              {/* Speech Output Box */}
              <div className="w-full p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                <div className="flex items-center justify-between text-[11px] text-gray-400 font-mono">
                  <span>SAARTHI VOICE SYNTHESIS (Indian Pronunciation)</span>
                  <Volume2 className="w-4 h-4 text-blue-400" />
                </div>
                <p className="text-sm font-medium text-white leading-relaxed">{assistantSpeech}</p>
              </div>

              {/* Consequential Action Approval Card */}
              {pendingApproval && (
                <div className="w-full p-4 rounded-2xl bg-amber-950/40 border border-amber-500/50 space-y-3 animate-in fade-in">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4" />
                    <span>EXPLICIT AUTHORIZATION REQUIRED (Risk Level: {pendingApproval.risk_level})</span>
                  </div>
                  <p className="text-xs text-gray-200">{pendingApproval.action_description}</p>
                  <div className="flex gap-2">
                    <Button variant="primary" size="sm" icon={CheckCircle} onClick={handleApproveAction}>
                      Approve & Execute
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setPendingApproval(null)}>
                      Reject
                    </Button>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                {!session ? (
                  <Button variant="primary" size="md" icon={Mic} onClick={() => handleStartSession(false, false)}>
                    Start Voice Session
                  </Button>
                ) : (
                  <Button variant="outline" size="md" icon={Square} onClick={handleStopSession}>
                    Stop Session
                  </Button>
                )}

                <Button variant="outline" size="md" icon={Square} onClick={handleInterrupt}>
                  Barge-in Interrupt
                </Button>

                <Button
                  variant={isHandsFreeActive ? "primary" : "outline"}
                  size="md"
                  icon={Hand}
                  onClick={() => handleStartSession(!isHandsFreeActive, false)}
                >
                  {isHandsFreeActive ? 'Disable Hands-Free' : 'Enable Hands-Free'}
                </Button>
              </div>
            </div>

            {/* Manual Turn Input fallback */}
            <div className="p-4 rounded-2xl bg-[#0e1426] border border-white/10 flex gap-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendTurn()}
                placeholder="Type or speak turn in English/Hindi ('Isme kya important hai?')..."
                className="flex-1 bg-transparent text-xs text-white focus:outline-none placeholder-gray-500 font-mono"
              />
              <Button variant="primary" size="sm" icon={Play} onClick={() => handleSendTurn()}>
                Send Turn
              </Button>
            </div>
          </div>

          {/* Right Column: Latency Telemetry & History */}
          <div className="space-y-6">
            {/* Latency & Telemetry Panel */}
            <div className="p-5 rounded-2xl bg-[#0e1426] border border-white/10 space-y-4 font-mono">
              <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                <Cpu className="w-4 h-4 text-purple-400" />
                <span className="font-bold text-xs text-white">LATENCY TELEMETRY</span>
              </div>

              {metrics ? (
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-gray-400">
                    <span>STT Latency:</span>
                    <span className="text-emerald-400">{metrics.stt_latency_ms} ms</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>Reasoning / Thinking:</span>
                    <span className="text-blue-400">{metrics.thinking_latency_ms} ms</span>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>TTS Synthesis:</span>
                    <span className="text-purple-400">{metrics.tts_latency_ms} ms</span>
                  </div>
                  <div className="border-t border-white/10 pt-2 flex justify-between font-bold text-white">
                    <span>Total Turn Latency:</span>
                    <span className="text-emerald-300">{metrics.total_turn_latency_ms} ms</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-gray-500 italic">No telemetry recorded yet. Start a turn.</p>
              )}
            </div>

            {/* Voice Privacy Summary */}
            <div className="p-5 rounded-2xl bg-[#0e1426] border border-white/10 space-y-3 font-mono">
              <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="font-bold text-xs text-white">VOICE PRIVACY GUARANTEE</span>
              </div>
              <ul className="text-[11px] text-gray-300 space-y-1.5">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span>No background microphone recording</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Local STT/TTS engine (Zero cloud telemetry)</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Consequential actions require explicit authorization</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
