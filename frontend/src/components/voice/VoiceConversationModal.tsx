import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2, Square, RefreshCw, X, Radio, Sparkles, Activity, Hand, Play } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { useApp } from '../../context/AppContext';
import { api } from '../../api';

interface VoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const VoiceConversationModal: React.FC<VoiceModalProps> = ({ isOpen, onClose }) => {
  const { addToast } = useApp();
  const [session, setSession] = useState<any>(null);
  const [state, setState] = useState<string>('LISTENING');
  const [transcript, setTranscript] = useState('Listening for user spoken input (en-IN + hi-IN)...');
  const [lastResponse, setLastResponse] = useState('Namaste Pratap, I am Saarthi. Speak naturally in English or Hindi.');
  const [isHandsFree, setIsHandsFree] = useState<boolean>(false);
  const [inputText, setInputText] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      startVoiceSession();
    } else {
      stopVoiceSession();
    }
  }, [isOpen]);

  const startVoiceSession = async (handsFree = false) => {
    try {
      const data = await api.startVoiceSession(handsFree, false);
      if (data && data.session) {
        setSession(data.session);
        setState(data.session.state || 'LISTENING');
        setIsHandsFree(handsFree);
      } else {
        addToast({
          type: 'error',
          title: 'Voice Session Entitlement',
          message: 'Voice Interaction requires PERSONAL or POWER plan.'
        });
      }
    } catch (err) {
      console.error("Voice session error", err);
    }
  };

  const stopVoiceSession = async () => {
    if (session?.session_id) {
      try {
        await api.stopVoiceSession(session.session_id);
      } catch (e) {}
    }
    setSession(null);
    setState('IDLE');
  };

  const handleInterrupt = async () => {
    if (session?.session_id) {
      try {
        await api.interruptVoiceSession(session.session_id, false);
        setState('LISTENING');
        addToast({
          type: 'info',
          title: 'Speech Interrupted (Barge-in)',
          message: 'Halted TTS speech playback.'
        });
      } catch (e) {}
    }
  };

  const handleSendTurn = async () => {
    if (!inputText.trim()) return;
    const sid = session?.session_id || 'vsession_active';
    setState('THINKING');
    try {
      const res = await api.processVoiceTurn(sid, inputText, "en-IN", false);
      if (res.status === 'success') {
        setState('SPEAKING');
        setLastResponse(res.assistant_text);
        setTranscript(inputText);
        setInputText('');
      } else if (res.status === 'pending_approval') {
        setState('WAITING_FOR_APPROVAL');
        setLastResponse(res.assistant_text);
      }
    } catch (err: any) {
      setState('ERROR');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4 font-mono text-xs animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-[#0b0f19] border border-purple-500/40 rounded-3xl p-6 space-y-6 shadow-2xl relative overflow-hidden">
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-purple-400 animate-pulse" />
            <span className="font-bold text-white text-sm">SAARTHI VOICE IDENTITY SESSION</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-all cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Visualizer & State Badge */}
        <div className="text-center space-y-4 py-4">
          <div className="flex justify-center gap-2">
            <Badge variant={state === 'LISTENING' ? 'success' : state === 'SPEAKING' ? 'accent' : 'warning'} size="md">
              {state} MODE
            </Badge>
            {isHandsFree && <Badge variant="success" size="md">HANDS-FREE</Badge>}
          </div>

          {/* Animated Waveform Visualizer */}
          <div className="flex items-center justify-center gap-1.5 h-16">
            {[40, 70, 30, 90, 50, 80, 20, 60, 100, 45, 75, 35].map((height, i) => (
              <div
                key={i}
                className="w-1.5 bg-gradient-to-t from-purple-500 to-blue-400 rounded-full animate-pulse"
                style={{ height: `${state === 'LISTENING' ? height * 0.6 : state === 'SPEAKING' ? height : 10}%`, animationDelay: `${i * 80}ms` }}
              />
            ))}
          </div>

          <p className="text-gray-300 text-xs italic">{transcript}</p>
        </div>

        {/* Saarthi Response Display */}
        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-[10px] text-gray-400">
            <span>SAARTHI SPEECH SYNTHESIS (hi-IN + en-IN)</span>
            <Volume2 className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <p className="text-white text-xs leading-relaxed">{lastResponse}</p>
        </div>

        {/* Quick Input Bar */}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendTurn()}
            placeholder="Type or speak turn in Hindi/English..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-white text-xs focus:outline-none placeholder-gray-500"
          />
          <Button variant="primary" size="sm" icon={Play} onClick={handleSendTurn}>
            Turn
          </Button>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-center gap-3 pt-2">
          <Button variant="outline" size="sm" icon={Square} onClick={handleInterrupt}>
            Barge-in Interrupt
          </Button>
          <Button variant="outline" size="sm" icon={Hand} onClick={() => startVoiceSession(!isHandsFree)}>
            {isHandsFree ? 'Exit Hands-Free' : 'Hands-Free'}
          </Button>
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={() => addToast({ type: 'info', title: 'Replaying', message: 'Replaying speech response.' })}>
            Replay
          </Button>
        </div>
      </div>
    </div>
  );
};
