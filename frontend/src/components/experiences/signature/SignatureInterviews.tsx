import React, { useState } from 'react';
import { 
  Mic2, 
  Sparkles, 
  CheckCircle2, 
  ChevronRight, 
  Award, 
  Play, 
  Volume2, 
  MessageSquare,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import { Button } from '../../common/Button';
import type { InterviewQuestion } from '../../../types';

export const SignatureInterviews: React.FC = () => {
  const { interviewQuestions, addToast, setActiveSection } = useApp();
  const [selectedQuestion, setSelectedQuestion] = useState<InterviewQuestion | null>(null);
  
  const currentQuestion = selectedQuestion || interviewQuestions[0];
  const [userResponse, setUserResponse] = useState(currentQuestion?.userAnswer || '');
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [feedback, setFeedback] = useState(currentQuestion?.feedback);

  if (!currentQuestion || interviewQuestions.length === 0) {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#222630]">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-[#8b949e] uppercase">
              <Mic2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Private Coaching Room &bull; Executive Simulation</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-serif font-medium text-white tracking-tight mt-1">
              Executive Interview Strategy & STAR Drills
            </h1>
            <p className="text-xs text-[#8b949e] mt-0.5">
              Private, on-device AI simulation analyzing executive presence, leadership storytelling, and quantitative impact.
            </p>
          </div>
        </div>

        <div className="p-12 text-center border border-[#222630] rounded-xl bg-[#111318] space-y-4">
          <Mic2 className="w-12 h-12 text-[#8b949e] mx-auto opacity-50" />
          <h3 className="text-lg font-serif font-bold text-white">No Practice Scenarios Loaded</h3>
          <p className="text-xs text-[#8b949e] max-w-md mx-auto">
            Your STAR drill practice queue is empty. Enable Demo Mode or import an application to generate custom interview questions.
          </p>
        </div>
      </div>
    );
  }

  const handleSimulateCoaching = () => {
    setIsSynthesizing(true);
    setTimeout(() => {
      setIsSynthesizing(false);
      setFeedback({
        score: 92,
        impactScore: 95,
        clarityScore: 90,
        technicalAccuracy: 94,
        strengths: [
          'Excellent leadership framing using quantified team velocity metrics',
          'Clear executive de-escalation framework and business outcome clarity'
        ],
        gaps: [
          'Could further highlight long-term architectural risk mitigation'
        ],
        improvedBulletSuggestion: 'Spearheaded zero-downtime ledger migration across 14 services, mitigating $4.2M transactional risk.'
      });
      addToast({ type: 'success', title: 'Executive Coaching Synthesis Completed' });
    }, 1200);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#222630]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#8b949e] uppercase">
            <Mic2 className="w-3.5 h-3.5 text-blue-400" />
            <span>Private Coaching Room &bull; Executive Simulation</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-serif font-medium text-white tracking-tight mt-1">
            Executive Interview Strategy & STAR Drills
          </h1>
          <p className="text-xs text-[#8b949e] mt-0.5">
            Private, on-device AI simulation analyzing executive presence, leadership storytelling, and quantitative impact.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-emerald-400 bg-emerald-950/30 px-3 py-1.5 rounded-lg border border-emerald-800/40">
          <ShieldCheck className="w-4 h-4" />
          <span>Local Nemotron-3 8B Audio/Text Sandbox</span>
        </div>
      </div>

      {/* Main Split: Left Scenario Selector, Right Private Coaching Studio */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left (4 cols): Executive Scenarios */}
        <div className="lg:col-span-4 space-y-3">
          <div className="text-xs font-mono uppercase tracking-wider text-[#8b949e] px-1 pb-1">
            Executive Scenarios ({interviewQuestions.length})
          </div>

          {interviewQuestions.map((q: any) => {
            const isSelected = currentQuestion?.id === q.id;
            return (
              <div
                key={q.id}
                onClick={() => {
                  setSelectedQuestion(q);
                  setUserResponse(q.userAnswer || '');
                  setFeedback(q.feedback);
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                  isSelected
                    ? 'bg-[#161a23] border-blue-500/60 shadow-lg'
                    : 'bg-[#111318] border-[#222630] hover:border-[#30363d]'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono text-[#8b949e]">
                  <span className="uppercase text-blue-400 font-semibold">{q.category}</span>
                  <span>{q.difficulty}</span>
                </div>
                <h4 className="text-xs font-serif font-semibold text-white line-clamp-2">
                  {q.question}
                </h4>
              </div>
            );
          })}
        </div>

        {/* Right (8 cols): Interactive Private Coaching Room */}
        <div className="lg:col-span-8 bg-[#111318] rounded-xl border border-[#222630] p-6 lg:p-8 space-y-6">
          {/* Question Prompt */}
          <div className="border-b border-[#222630] pb-5 space-y-3">
            <div className="flex items-center justify-between text-xs font-mono text-[#8b949e]">
              <span className="text-blue-400 uppercase">Scenario Focus &bull; {currentQuestion.category}</span>
              {currentQuestion.companyTarget && <span>Target: {currentQuestion.companyTarget}</span>}
            </div>
            <h2 className="text-xl font-serif font-medium text-white leading-relaxed">
              "{currentQuestion.question}"
            </h2>
          </div>

          {/* STAR Framework Guide */}
          <div className="p-4 rounded-lg bg-[#161a23] border border-[#222630] space-y-3">
            <div className="text-xs font-mono text-[#8b949e] uppercase tracking-wider">
              Recommended STAR Framework
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 rounded bg-[#111318] space-y-1">
                <span className="font-mono text-[10px] text-blue-400 font-bold">SITUATION</span>
                <p className="text-[#8b949e] text-[11px] leading-tight">{currentQuestion.starStructure.situation}</p>
              </div>
              <div className="p-2.5 rounded bg-[#111318] space-y-1">
                <span className="font-mono text-[10px] text-blue-400 font-bold">TASK</span>
                <p className="text-[#8b949e] text-[11px] leading-tight">{currentQuestion.starStructure.task}</p>
              </div>
              <div className="p-2.5 rounded bg-[#111318] space-y-1">
                <span className="font-mono text-[10px] text-blue-400 font-bold">ACTION</span>
                <p className="text-[#8b949e] text-[11px] leading-tight">{currentQuestion.starStructure.action}</p>
              </div>
              <div className="p-2.5 rounded bg-[#111318] space-y-1">
                <span className="font-mono text-[10px] text-blue-400 font-bold">RESULT</span>
                <p className="text-[#8b949e] text-[11px] leading-tight">{currentQuestion.starStructure.result}</p>
              </div>
            </div>
          </div>

          {/* User Response Area */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-[#8b949e]">
              <span>Your Response Formulation</span>
              <span>Private Local Buffer</span>
            </div>
            <textarea
              value={userResponse}
              onChange={(e) => setUserResponse(e.target.value)}
              placeholder="Outline your executive narrative using the STAR framework..."
              rows={5}
              className="w-full p-4 rounded-lg bg-[#0c0e12] border border-[#222630] text-xs text-white placeholder-[#6e7681] focus:outline-none focus:border-blue-500 font-sans leading-relaxed resize-none"
            />
          </div>

          {/* Action Row */}
          <div className="flex items-center justify-between pt-2">
            <Button
              variant="ghost"
              size="sm"
              icon={RotateCcw}
              onClick={() => setUserResponse('')}
            >
              Reset Draft
            </Button>
            <Button
              variant="ai"
              size="sm"
              icon={Sparkles}
              isLoading={isSynthesizing}
              onClick={handleSimulateCoaching}
            >
              Synthesize Executive Feedback
            </Button>
          </div>

          {/* Coaching Feedback Synthesis */}
          {feedback && (
            <div className="p-5 rounded-lg bg-[#141923] border border-blue-500/30 space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center justify-between border-b border-[#222630] pb-3">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-serif font-bold text-white">Chief-of-Staff Feedback Rubric</span>
                </div>
                <span className="text-xs font-mono text-emerald-400 font-bold">{feedback.score}/100 Overall</span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center text-xs font-mono">
                <div className="p-2 rounded bg-[#111318] text-[#8b949e]">
                  Impact: <strong className="text-white">{feedback.impactScore}%</strong>
                </div>
                <div className="p-2 rounded bg-[#111318] text-[#8b949e]">
                  Clarity: <strong className="text-white">{feedback.clarityScore}%</strong>
                </div>
                <div className="p-2 rounded bg-[#111318] text-[#8b949e]">
                  Accuracy: <strong className="text-white">{feedback.technicalAccuracy}%</strong>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="text-emerald-400 font-medium font-serif">Executive Strengths:</div>
                <ul className="list-disc pl-4 text-[#c9d1d9] space-y-1">
                  {feedback.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>

              {feedback.improvedBulletSuggestion && (
                <div className="p-3 rounded bg-[#111318] border border-[#222630] text-xs space-y-1">
                  <div className="text-blue-400 font-mono font-semibold">Recommended Polish Formulation:</div>
                  <p className="text-white italic">"{feedback.improvedBulletSuggestion}"</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
