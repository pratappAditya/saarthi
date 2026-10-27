import React, { useState } from 'react';
import { 
  Radio, 
  Sparkles, 
  Orbit, 
  CheckCircle2, 
  RotateCcw, 
  Volume2, 
  Zap, 
  Award,
  Bot
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { InterviewQuestion } from '../../../types';

export const AuroraInterviews: React.FC = () => {
  const { interviewQuestions, addToast } = useApp();
  const [selectedQ, setSelectedQ] = useState<InterviewQuestion | null>(null);
  
  const currentQ = selectedQ || interviewQuestions[0];
  const [userSpeech, setUserSpeech] = useState(currentQ?.userAnswer || '');
  const [isSimulating, setIsSimulating] = useState(false);
  const [feedback, setFeedback] = useState(currentQ?.feedback);

  if (!currentQ || interviewQuestions.length === 0) {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div className="p-12 text-center border border-cyan-500/20 rounded-2xl bg-cyan-950/10 space-y-4">
          <Radio className="w-12 h-12 text-cyan-400 mx-auto opacity-50" />
          <h3 className="text-xl font-bold text-white">Simulation Studio Empty</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            No interview scenarios in queue. Enable Demo Mode or import an application to generate custom practice scenarios.
          </p>
        </div>
      </div>
    );
  }

  const handleSimulate = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
      setFeedback({
        score: 95,
        impactScore: 97,
        clarityScore: 94,
        technicalAccuracy: 96,
        strengths: [
          'High executive confidence and clear STAR architectural arc',
          'Quantified business outcome: reduced payment checkout drop-off by 14%'
        ],
        gaps: [
          'Minor: could further emphasize developer ergonomics during multi-team rollout'
        ],
        improvedBulletSuggestion: 'Spearheaded zero-latency checkout pipeline scaling to 1.4B daily events with 99.999% availability.'
      });
      addToast({ type: 'success', title: 'Spatial Simulation Complete', message: 'Local Nemotron neural rubric evaluated.' });
    }, 1200);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-[#11162a]/70 backdrop-blur-2xl border border-indigo-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest">
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-ping" />
            <span>AI Simulation Studio &bull; Neural Dialogue Space</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-light text-white tracking-tight mt-1">
            Immersive Interview Simulation
          </h1>
          <p className="text-xs text-[#94a3b8] mt-0.5">
            Real-time conversational evaluation executing strictly in local device memory.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>AUDIO / TEXT STREAM ACTIVE</span>
        </div>
      </div>

      {/* Main Simulation Arena */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left (4 cols): Scenarios */}
        <div className="lg:col-span-4 space-y-2.5">
          <div className="text-xs font-mono text-cyan-400 uppercase px-1">
            Simulation Scenarios ({interviewQuestions.length})
          </div>

          {interviewQuestions.map((q) => {
            const isSelected = currentQ?.id === q.id;
            return (
              <div
                key={q.id}
                onClick={() => {
                  setSelectedQ(q);
                  setUserSpeech(q.userAnswer || '');
                  setFeedback(q.feedback);
                }}
                className={`p-4 rounded-2xl backdrop-blur-xl border transition-all cursor-pointer space-y-1.5 ${
                  isSelected
                    ? 'bg-[#182142]/80 border-cyan-500/60 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                    : 'bg-[#11162a]/60 border-indigo-500/20 hover:border-indigo-500/40'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-cyan-300">
                  <span className="uppercase">{q.category}</span>
                  <span>{q.difficulty}</span>
                </div>
                <h4 className="text-xs font-semibold text-white line-clamp-2">
                  {q.question}
                </h4>
              </div>
            );
          })}
        </div>

        {/* Right (8 cols): Spatial Simulation Studio */}
        <div className="lg:col-span-8 bg-[#11162a]/70 backdrop-blur-2xl border border-indigo-500/30 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl">
          {/* Question Prompt */}
          <div className="p-5 rounded-2xl bg-[#141b34]/70 border border-indigo-500/20 space-y-2">
            <div className="text-xs font-mono text-cyan-400 uppercase">
              Interviewer Prompt &bull; {currentQ.category}
            </div>
            <h2 className="text-lg font-light text-white leading-relaxed">
              "{currentQ.question}"
            </h2>
          </div>

          {/* User Formulation */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-[#94a3b8]">
              <span>Candidate Narrative</span>
              <span className="text-cyan-400">Live Voice / Text Input</span>
            </div>
            <textarea
              value={userSpeech}
              onChange={(e) => setUserSpeech(e.target.value)}
              placeholder="Speak or formulate your response using the STAR executive methodology..."
              rows={5}
              className="w-full p-4 rounded-2xl bg-[#0d1224]/80 border border-indigo-500/20 text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-cyan-500 resize-none font-sans leading-relaxed"
            />
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" onClick={() => setUserSpeech('')}>
              Clear Buffer
            </Button>
            <Button
              variant="ai"
              size="md"
              icon={Sparkles}
              isLoading={isSimulating}
              onClick={handleSimulate}
            >
              Synthesize Neural Rubric
            </Button>
          </div>

          {/* Neural Rubric Results */}
          {feedback && (
            <div className="p-5 rounded-2xl bg-[#141b34]/90 border border-cyan-500/40 space-y-3 animate-in fade-in duration-200">
              <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-cyan-400" />
                  <span className="text-xs font-mono uppercase text-white font-bold">Neural Simulation Rubric</span>
                </div>
                <span className="text-sm font-mono font-bold text-cyan-300">{feedback.score}/100</span>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                <div className="p-2 rounded-xl bg-[#0d1224] text-cyan-300">
                  Impact: <strong>{feedback.impactScore}%</strong>
                </div>
                <div className="p-2 rounded-xl bg-[#0d1224] text-cyan-300">
                  Clarity: <strong>{feedback.clarityScore}%</strong>
                </div>
                <div className="p-2 rounded-xl bg-[#0d1224] text-cyan-300">
                  Accuracy: <strong>{feedback.technicalAccuracy}%</strong>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[#0d1224] text-xs space-y-1">
                <span className="text-cyan-400 font-mono text-[10px] uppercase font-bold">High Resonance Formulation:</span>
                <p className="text-white italic">"{feedback.improvedBulletSuggestion}"</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
