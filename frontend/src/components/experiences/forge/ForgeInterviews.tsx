import React, { useState } from 'react';
import { 
  Terminal, 
  Play, 
  CheckCircle2, 
  Activity, 
  Code, 
  Sliders, 
  Zap, 
  RotateCcw,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { useApp } from '../../../context/AppContext';
import type { InterviewQuestion } from '../../../types';

export const ForgeInterviews: React.FC = () => {
  const { interviewQuestions, hardware, addToast } = useApp();
  const [selectedQ, setSelectedQ] = useState<InterviewQuestion | null>(null);

  const currentQ = selectedQ || interviewQuestions[0];
  const [userCodeOrAnswer, setUserCodeOrAnswer] = useState(currentQ?.userAnswer || '');
  const [isRunningEval, setIsRunningEval] = useState(false);
  const [evalResult, setEvalResult] = useState(currentQ?.feedback);

  if (!currentQ || interviewQuestions.length === 0) {
    return (
      <div className="space-y-6 font-mono animate-in fade-in duration-200">
        <div className="p-8 text-center border border-[#30363d] rounded bg-[#0d1117] space-y-3">
          <Terminal className="w-10 h-10 text-[#8b949e] mx-auto" />
          <div className="text-sm font-bold text-[#c9d1d9]">~/workspace/interview-lab $ ./eval_runner.py --list</div>
          <div className="text-xs text-[#8b949e]">STATUS 200: 0 test cases loaded in current environment session.</div>
        </div>
      </div>
    );
  }

  const handleRunEvaluation = () => {
    setIsRunningEval(true);
    setTimeout(() => {
      setIsRunningEval(false);
      setEvalResult({
        score: 94,
        impactScore: 96,
        clarityScore: 92,
        technicalAccuracy: 95,
        strengths: [
          'High architectural rigor: correctly identified race conditions in distributed token cache',
          'Quantified latency improvement: reduced p99 from 240ms to 42ms'
        ],
        gaps: [
          'Edge case: consider network partition behavior during failover cluster reelection'
        ],
        improvedBulletSuggestion: 'Architected distributed multi-region token cache with deterministic quorum, reducing p99 latency by 82% under 40k req/s load.'
      });
      addToast({ type: 'success', title: 'Nemotron Evaluator Trace Completed (0 runtime errors)' });
    }, 1000);
  };

  return (
    <div className="space-y-3 font-mono text-xs animate-in fade-in duration-200">
      {/* Top Test Suite Toolbar */}
      <div className="p-2.5 bg-[#0d1117] border border-[#21262d] rounded flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-white">INTERVIEW_LAB: EVAL_RUNNER.PY</span>
          <span className="text-[10px] text-[#8b949e]">[{currentQ.category.toUpperCase()}]</span>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] text-emerald-400">MODEL: {hardware.activeModel.split('/')[1]}</span>
          <button
            onClick={handleRunEvaluation}
            disabled={isRunningEval}
            className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            <Play className="w-3 h-3 fill-current" /> {isRunningEval ? 'RUNNING_EVAL...' : 'RUN_TEST_SUITE'}
          </button>
        </div>
      </div>

      {/* Main Split: Left Scenario AST & STAR spec, Right Trace / Output Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-2 h-[calc(100vh-210px)] min-h-[520px]">
        {/* Left (5 cols): Test Spec & STAR Parameter Injections */}
        <div className="lg:col-span-5 bg-[#0d1117] border border-[#21262d] rounded p-3 flex flex-col justify-between overflow-y-auto space-y-3">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[11px] font-bold text-white border-b border-[#21262d] pb-1">
              <span>TEST_PROMPT_SPEC</span>
              <span className="text-blue-400">{currentQ.difficulty}</span>
            </div>

            <div className="p-2.5 rounded bg-[#090b0e] border border-[#21262d] text-white leading-relaxed">
              {currentQ.question}
            </div>

            <div className="space-y-1 text-[11px]">
              <div className="text-[#8b949e] font-bold">STAR_ASSERTION_CONSTRAINTS:</div>
              <div className="p-2 rounded bg-[#161b22] space-y-1 text-[10px]">
                <div><span className="text-blue-400 font-bold">SITUATION:</span> {currentQ.starStructure.situation}</div>
                <div><span className="text-blue-400 font-bold">TASK:</span> {currentQ.starStructure.task}</div>
                <div><span className="text-blue-400 font-bold">ACTION:</span> {currentQ.starStructure.action}</div>
                <div><span className="text-blue-400 font-bold">RESULT:</span> {currentQ.starStructure.result}</div>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-[#21262d] space-y-1">
            <div className="text-[10px] text-[#8b949e]">SELECT_FIXTURE_SCENARIO:</div>
            <select
              value={currentQ.id}
              onChange={(e) => {
                const q = interviewQuestions.find(x => x.id === e.target.value);
                if (q) {
                  setSelectedQ(q);
                  setUserCodeOrAnswer(q.userAnswer || '');
                  setEvalResult(q.feedback);
                }
              }}
              className="w-full p-1.5 rounded bg-[#161b22] border border-[#30363d] text-[11px] text-white font-mono"
            >
              {interviewQuestions.map((q) => (
                <option key={q.id} value={q.id}>{q.category}: {q.question.slice(0, 45)}...</option>
              ))}
            </select>
          </div>
        </div>

        {/* Right (7 cols): Input Buffer + Telemetry Trace Console */}
        <div className="lg:col-span-7 bg-[#0d1117] border border-[#21262d] rounded p-3 flex flex-col justify-between overflow-hidden">
          <div className="flex-1 flex flex-col space-y-2 overflow-hidden">
            <div className="flex items-center justify-between text-[11px] font-bold text-white border-b border-[#21262d] pb-1">
              <span>CANDIDATE_SOLUTION_BUFFER</span>
              <span className="text-[#8b949e] text-[10px]">INLINE_COMPILER</span>
            </div>

            <textarea
              value={userCodeOrAnswer}
              onChange={(e) => setUserCodeOrAnswer(e.target.value)}
              placeholder="# Write technical explanation, system architecture trace, or STAR bullet..."
              className="flex-1 w-full p-2.5 bg-[#090b0e] border border-[#21262d] text-white font-mono text-[11px] focus:outline-none focus:border-blue-500 resize-none rounded leading-relaxed"
            />
          </div>

          {/* Trace Console Output */}
          {evalResult && (
            <div className="mt-2 p-2.5 rounded bg-[#090b0e] border border-emerald-500/40 space-y-2">
              <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold border-b border-[#21262d] pb-1">
                <span>[NEMOTRON_EVAL_TRACE: OK]</span>
                <span>SCORE: {evalResult.score}/100</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-[10px]">
                <div>IMPACT: <strong className="text-white">{evalResult.impactScore}%</strong></div>
                <div>CLARITY: <strong className="text-white">{evalResult.clarityScore}%</strong></div>
                <div>TECH_ACCURACY: <strong className="text-white">{evalResult.technicalAccuracy}%</strong></div>
              </div>
              <div className="text-[10px] text-[#8b949e]">
                <strong className="text-emerald-400">OPTIMIZED_BULLET: </strong>
                <span className="text-white">"{evalResult.improvedBulletSuggestion}"</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
