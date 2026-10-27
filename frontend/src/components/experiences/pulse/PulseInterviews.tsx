import React, { useState } from 'react';
import { 
  Swords, 
  Flame, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  Trophy, 
  RotateCcw, 
  Award,
  Zap
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { InterviewQuestion } from '../../../types';

export const PulseInterviews: React.FC = () => {
  const { interviewQuestions, addToast } = useApp();
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [isGrading, setIsGrading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const currentQ = interviewQuestions[currentIdx] || interviewQuestions[0] || null;

  if (!currentQ || interviewQuestions.length === 0) {
    return (
      <div className="space-y-6 animate-in fade-in duration-200">
        <div className="p-8 text-center border-2 border-dashed border-indigo-500/30 rounded-2xl bg-indigo-950/20 space-y-3">
          <Swords className="w-10 h-10 text-indigo-400 mx-auto" />
          <h3 className="text-xl font-extrabold text-white">Training Arena Queue Empty</h3>
          <p className="text-xs text-slate-300 max-w-md mx-auto">
            0 interview drills in queue. Enable Demo Mode or create an application to unlock XP drills.
          </p>
        </div>
      </div>
    );
  }

  const handleGrade = () => {
    setIsGrading(true);
    setTimeout(() => {
      setIsGrading(false);
      setResult({
        score: 93,
        streakBonus: '+50 XP',
        feedback: 'Outstanding STAR velocity! Specific metrics around throughput scaling directly address the interviewer rubric.',
        powerBullet: 'Engineered sub-50ms reactive state engine for 1.2M concurrent client sessions.'
      });
      addToast({ type: 'success', title: 'Arena Drill Cleared!', message: 'Earned +50 XP streak multiplier.' });
    }, 1000);
  };

  const nextDrill = () => {
    setCurrentIdx((prev) => (prev + 1) % interviewQuestions.length);
    setUserAnswer('');
    setResult(null);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-[#101524] border border-[#1c2438] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase">
            <Swords className="w-4 h-4" />
            <span>Interview Training Arena &bull; Speed Drills</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Drill Round {currentIdx + 1} of {interviewQuestions.length}
          </h1>
          <p className="text-xs text-[#94a3b8] mt-0.5">
            Rapid-fire STAR scenario simulator powered by local NVIDIA Nemotron.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-extrabold">
          <Flame className="w-4 h-4 fill-amber-400" />
          <span>STREAK: 4 DRILLS CLEARED</span>
        </div>
      </div>

      {/* Main Arena Box */}
      <div className="bg-[#101524] border border-[#1c2438] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl max-w-4xl mx-auto">
        {/* Question Card */}
        <div className="p-5 rounded-xl bg-[#151c30] border border-[#242e47] space-y-2">
          <div className="flex items-center justify-between text-xs font-bold text-indigo-400 uppercase">
            <span>{currentQ.category} &bull; {currentQ.difficulty}</span>
            <span>Target: {currentQ.companyTarget || 'Tier 1 Tech'}</span>
          </div>
          <h2 className="text-lg sm:text-xl font-bold text-white leading-relaxed">
            "{currentQ.question}"
          </h2>
        </div>

        {/* Input response */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-[#94a3b8] uppercase">Your STAR Formulation</label>
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Type or dictate your structured response (Situation, Task, Action, Result)..."
            rows={5}
            className="w-full p-4 rounded-xl bg-[#0d101a] border border-[#242e47] text-xs text-white placeholder-[#64748b] focus:outline-none focus:border-indigo-500 resize-none font-sans leading-relaxed"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2">
          <Button variant="ghost" size="sm" onClick={nextDrill}>
            Skip / Next Question
          </Button>

          <Button
            variant="ai"
            size="md"
            icon={Zap}
            isLoading={isGrading}
            onClick={handleGrade}
          >
            Submit for AI Grading
          </Button>
        </div>

        {/* Result Card */}
        {result && (
          <div className="p-5 rounded-xl bg-gradient-to-r from-emerald-950/40 to-indigo-950/40 border border-emerald-500/40 space-y-3 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                <span className="font-extrabold text-white text-sm">Arena Score: {result.score}/100</span>
              </div>
              <span className="text-xs font-bold font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/30">
                {result.streakBonus}
              </span>
            </div>

            <p className="text-xs text-[#cbd5e1] leading-relaxed">
              {result.feedback}
            </p>

            <div className="p-3 rounded-lg bg-[#0d101a] border border-[#242e47] text-xs space-y-1">
              <span className="text-[10px] font-bold text-indigo-400 uppercase">Power Bullet Formulation:</span>
              <p className="text-emerald-300 font-semibold italic">"{result.powerBullet}"</p>
            </div>

            <div className="pt-2 flex justify-end">
              <Button variant="primary" size="sm" icon={ArrowRight} onClick={nextDrill}>
                Next Drill Round
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
