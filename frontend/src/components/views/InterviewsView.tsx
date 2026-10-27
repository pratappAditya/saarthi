import React, { useState } from 'react';
import { 
  MessagesSquare, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Play, 
  RotateCcw, 
  Award, 
  ShieldCheck,
  Send,
  Zap,
  Target
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Progress } from '../common/Progress';
import { Textarea } from '../common/Input';
import type { InterviewQuestion } from '../../types';

export const InterviewsView: React.FC = () => {
  const { 
    interviews, 
    activeInterview, 
    setActiveInterview, 
    submitInterviewAnswer, 
    isScoringInterview,
    activeModel,
    hardware,
    addToast
  } = useApp();

  const [answerInput, setAnswerInput] = useState(activeInterview?.userAnswer || '');

  const handleSelectQuestion = (q: InterviewQuestion) => {
    setActiveInterview(q);
    setAnswerInput(q.userAnswer || '');
  };

  const handleGrade = () => {
    if (!activeInterview || !answerInput.trim()) return;
    submitInterviewAnswer(activeInterview.id, answerInput);
  };

  if (!interviews || interviews.length === 0) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
              <MessagesSquare className="w-3.5 h-3.5 text-blue-400" />
              <span>INTERVIEW SIMULATION & STAR DRILLS</span>
            </div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
              Interview Preparation Ground
            </h1>
            <p className="text-xs text-[var(--text-secondary)] mt-0.5">
              Practice behavioral and system architecture questions. Local Nemotron evaluates STAR structure and metrics in real-time.
            </p>
          </div>
        </div>

        <Card variant="default" padding="lg" className="text-center space-y-3 py-12">
          <MessagesSquare className="w-12 h-12 text-[var(--text-muted)] mx-auto opacity-50" />
          <h3 className="text-lg font-bold text-[var(--text-primary)] font-display-title">No Interview Questions Loaded</h3>
          <p className="text-xs text-[var(--text-secondary)] max-w-md mx-auto">
            Your question bank is empty. Enable Demo Mode to practice with sample interview questions or import an application to generate custom drills.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <MessagesSquare className="w-3.5 h-3.5 text-blue-400" />
            <span>INTERVIEW SIMULATION & STAR DRILLS</span>
          </div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight font-display-title">
            Interview Preparation Ground
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Practice behavioral and system architecture questions. Local Nemotron evaluates STAR structure and metrics in real-time.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="ai" size="sm" dot>
            Evaluator: {activeModel.name.split(' ')[0]} ({hardware.isBenchmarked && hardware.inferenceSpeed !== null ? `${hardware.inferenceSpeed} t/s` : 'Not benchmarked'})
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (4 Cols): Question Bank */}
        <div className="lg:col-span-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[var(--text-secondary)] uppercase font-mono">
              Curated Question Bank ({interviews.length})
            </span>
          </div>

          <div className="space-y-2">
            {interviews.map((q) => {
              const isSelected = q.id === activeInterview?.id;
              return (
                <div
                  key={q.id}
                  onClick={() => handleSelectQuestion(q)}
                  className={`p-3 rounded-[var(--radius-md)] border transition-all cursor-pointer select-none space-y-1.5 ${
                    isSelected
                      ? 'bg-[var(--accent-subtle)] border-[var(--accent-primary)]/40 shadow-xs'
                      : 'bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] border-[var(--border-subtle)]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant={q.category === 'system_design' ? 'accent' : 'purple'} size="xs">
                      {q.category.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <span className="text-[10px] font-mono text-[var(--text-muted)]">
                      {q.difficulty}
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-[var(--text-primary)] line-clamp-2 leading-relaxed font-display-title">
                    {q.question}
                  </p>

                  <div className="flex items-center justify-between text-[10px] font-mono text-[var(--text-muted)] pt-1">
                    <span>{q.companyTarget?.split(' ')[0]} Target</span>
                    {q.feedback && (
                      <span className="text-emerald-400 font-bold">
                        Score: {q.feedback.score}/100
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column (8 Cols): Practice Stage & Feedback Rubric */}
        {activeInterview && (
          <div className="lg:col-span-8 space-y-4">
            {/* Active Question Card */}
            <Card variant="default" padding="lg" className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="accent" size="xs">
                    {activeInterview.category.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <span className="text-xs font-mono text-[var(--text-muted)]">
                    Target: {activeInterview.companyTarget}
                  </span>
                </div>

                <h2 className="text-base sm:text-lg font-bold text-[var(--text-primary)] leading-snug font-display-title">
                  {activeInterview.question}
                </h2>
              </div>

              {/* STAR Framework Guide Box */}
              <div className="p-3.5 rounded-[var(--radius-md)] bg-[var(--bg-subtle)] border border-[var(--border-subtle)] space-y-2">
                <div className="text-[10px] font-mono uppercase font-bold text-blue-400 flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5" />
                  <span>Recommended STAR Blueprint</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  <div className="p-2 rounded bg-[var(--bg-surface)]">
                    <strong className="text-[var(--text-primary)] block font-mono text-[10px]">SITUATION</strong>
                    <span className="text-[var(--text-secondary)] line-clamp-2">{activeInterview.starStructure.situation}</span>
                  </div>
                  <div className="p-2 rounded bg-[var(--bg-surface)]">
                    <strong className="text-[var(--text-primary)] block font-mono text-[10px]">TASK</strong>
                    <span className="text-[var(--text-secondary)] line-clamp-2">{activeInterview.starStructure.task}</span>
                  </div>
                  <div className="p-2 rounded bg-[var(--bg-surface)]">
                    <strong className="text-[var(--text-primary)] block font-mono text-[10px]">ACTION</strong>
                    <span className="text-[var(--text-secondary)] line-clamp-2">{activeInterview.starStructure.action}</span>
                  </div>
                  <div className="p-2 rounded bg-[var(--bg-surface)]">
                    <strong className="text-emerald-400 block font-mono text-[10px]">RESULT</strong>
                    <span className="text-[var(--text-secondary)] line-clamp-2">{activeInterview.starStructure.result}</span>
                  </div>
                </div>
              </div>

              {/* User Answer Input */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-[var(--text-secondary)]">Your Answer (Type or Practice Speech)</label>
                  <span className="text-[10px] font-mono text-[var(--text-muted)]">
                    {answerInput.length} chars
                  </span>
                </div>

                <Textarea
                  value={answerInput}
                  onChange={(e) => setAnswerInput(e.target.value)}
                  placeholder="Outline your Situation, Task, Action, and quantified Business Result..."
                  rows={6}
                  className="font-sans text-xs leading-relaxed"
                />

                <div className="flex justify-end pt-1">
                  <Button
                    variant="ai"
                    size="sm"
                    icon={Sparkles}
                    isLoading={isScoringInterview}
                    disabled={!answerInput.trim()}
                    onClick={handleGrade}
                  >
                    {isScoringInterview ? 'Evaluating with Nemotron...' : 'Grade Answer with Local Nemotron'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* AI FEEDBACK RUBRIC */}
            {activeInterview.feedback && (
              <Card variant="default" padding="lg" className="space-y-4 border-blue-500/30 bg-blue-950/10">
                <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-emerald-400" />
                    <div>
                      <h3 className="text-sm font-bold text-[var(--text-primary)] font-display-title">
                        Nemotron Rubric Evaluation
                      </h3>
                      <span className="text-[10px] font-mono text-emerald-400">
                        Zero Cloud Transfer • {hardware.inferenceSpeed} tok/s
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-bold text-emerald-400 font-display-title">
                      {activeInterview.feedback.score} / 100
                    </div>
                  </div>
                </div>

                {/* Score Breakdown Gauges */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                    <div className="text-[10px] font-mono text-[var(--text-muted)]">CLARITY</div>
                    <div className="text-sm font-bold text-blue-400">{activeInterview.feedback.clarityScore}%</div>
                    <Progress value={activeInterview.feedback.clarityScore} size="xs" variant="accent" showPercentage={false} />
                  </div>
                  <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                    <div className="text-[10px] font-mono text-[var(--text-muted)]">QUANTIFIED IMPACT</div>
                    <div className="text-sm font-bold text-emerald-400">{activeInterview.feedback.impactScore}%</div>
                    <Progress value={activeInterview.feedback.impactScore} size="xs" variant="success" showPercentage={false} />
                  </div>
                  <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)] space-y-1">
                    <div className="text-[10px] font-mono text-[var(--text-muted)]">TECH ACCURACY</div>
                    <div className="text-sm font-bold text-purple-400">{activeInterview.feedback.technicalAccuracy}%</div>
                    <Progress value={activeInterview.feedback.technicalAccuracy} size="xs" variant="ai" showPercentage={false} />
                  </div>
                </div>

                {/* Strengths & Gaps */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded bg-emerald-950/20 border border-emerald-500/25 space-y-1.5">
                    <div className="font-bold text-emerald-300 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Identified Strengths</span>
                    </div>
                    <ul className="space-y-1 pl-4 list-disc text-[11px] text-emerald-200/90 leading-relaxed">
                      {activeInterview.feedback.strengths.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3 rounded bg-amber-950/20 border border-amber-500/25 space-y-1.5">
                    <div className="font-bold text-amber-300 flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5" />
                      <span>Improvement Gaps</span>
                    </div>
                    <ul className="space-y-1 pl-4 list-disc text-[11px] text-amber-200/90 leading-relaxed">
                      {activeInterview.feedback.gaps.map((g, idx) => (
                        <li key={idx}>{g}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Phrasing Suggestion */}
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-subtle)] text-xs space-y-1">
                  <span className="text-[10px] font-mono uppercase font-bold text-blue-400">
                    💡 Nemotron Improved Result Formulation
                  </span>
                  <p className="text-[11px] text-[var(--text-secondary)] italic leading-relaxed">
                    "{activeInterview.feedback.improvedBulletSuggestion}"
                  </p>
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
