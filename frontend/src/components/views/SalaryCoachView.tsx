import React, { useState } from 'react';
import { 
  DollarSign, Sparkles, Send, ShieldCheck, Award, TrendingUp, AlertCircle 
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Input, Textarea } from '../common/Input';
import { api } from '../../api';

export const SalaryCoachView: React.FC = () => {
  const { addToast } = useApp();
  const [company, setCompany] = useState('Stripe');
  const [role, setTargetRole] = useState('Lead Security Architect');
  const [baseSalary, setBaseSalary] = useState(140000);
  const [variablePay, setVariablePay] = useState(20000);
  const [bonus, setBonus] = useState(15000);
  const [equity, setEquity] = useState('$50,000 RSUs over 4 years');
  const [targetComp, setTargetComp] = useState(185000);
  const [competingOffer, setCompetingOffer] = useState('Competing offer at CyberDefense ($175k Base)');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await api.analyzeSalaryOffer({
        company,
        role,
        base_salary: Number(baseSalary),
        variable_pay: Number(variablePay),
        bonus: Number(bonus),
        equity,
        target_compensation: Number(targetComp),
        competing_offer: competingOffer
      });
      setResult(res.analysis);
      addToast({
        type: 'success',
        title: 'Salary & Offer Analyzed',
        message: `Calculated total compensation and counter-offer strategy.`
      });
    } catch (err) {
      addToast({ type: 'error', title: 'Analysis Failed', message: 'Could not process offer coaching.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            <span>SALARY & OFFER NEGOTIATION COACH</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Offer Compensation & Strategy Workbench
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Evaluate compensation packages, gap analysis against target goals, and draft counter-offer negotiation letters.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form (5 Cols) */}
        <div className="lg:col-span-5">
          <Card variant="default" padding="md">
            <form onSubmit={handleAnalyze} className="space-y-3 text-xs">
              <h3 className="font-bold text-white font-display-title">Offer Inputs</h3>
              <Input label="Company" value={company} onChange={(e) => setCompany(e.target.value)} required />
              <Input label="Role" value={role} onChange={(e) => setTargetRole(e.target.value)} required />
              <div className="grid grid-cols-2 gap-2">
                <Input label="Base Salary ($)" type="number" value={baseSalary} onChange={(e) => setBaseSalary(Number(e.target.value))} required />
                <Input label="Bonus ($)" type="number" value={bonus} onChange={(e) => setBonus(Number(e.target.value))} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Input label="Variable Pay ($)" type="number" value={variablePay} onChange={(e) => setVariablePay(Number(e.target.value))} />
                <Input label="Target Goal ($)" type="number" value={targetComp} onChange={(e) => setTargetComp(Number(e.target.value))} required />
              </div>
              <Input label="Equity Grant" value={equity} onChange={(e) => setEquity(e.target.value)} />
              <Input label="Competing Offer Context" value={competingOffer} onChange={(e) => setCompetingOffer(e.target.value)} />

              <Button variant="primary" size="md" icon={Sparkles} isLoading={loading} className="w-full mt-2">
                {loading ? 'Analyzing Compensation...' : 'Calculate Strategy & Counter-Offer'}
              </Button>
            </form>
          </Card>
        </div>

        {/* Right Output (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {!result ? (
            <div className="p-12 text-center border border-dashed border-[var(--border-subtle)] rounded-xl space-y-2 text-xs text-gray-400">
              <DollarSign className="w-8 h-8 mx-auto text-emerald-400 opacity-60" />
              <p className="font-bold text-white">No Compensation Analysis Generated Yet</p>
              <p className="max-w-xs mx-auto">Fill in your offer numbers on the left and click "Calculate Strategy" to evaluate compensation and generate a counter-offer letter.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* User Facts vs Analysis Badge */}
              <Card variant="subtle" padding="md" className="space-y-3 text-xs">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Verified User Facts vs Nemotron Analysis</span>
                </h3>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-300">
                  <div className="p-2 rounded bg-white/5 border border-white/10">
                    <p className="text-gray-400">Base Salary:</p>
                    <p className="text-white font-bold">{result.user_facts?.base_salary}</p>
                  </div>
                  <div className="p-2 rounded bg-white/5 border border-white/10">
                    <p className="text-gray-400">Total Target Comp:</p>
                    <p className="text-emerald-400 font-bold">{result.user_facts?.total_target_compensation}</p>
                  </div>
                </div>
              </Card>

              {/* Analysis & Strategy */}
              <Card variant="default" padding="md" className="space-y-3 text-xs">
                <h3 className="font-bold text-white">Negotiation Strategy</h3>
                <div className="space-y-1.5 text-gray-300">
                  <p><strong>Gap to Target Goal:</strong> <span className="text-amber-400 font-mono">{result.analysis?.gap_to_target}</span></p>
                  <p><strong>Recommended Base Counter:</strong> <span className="text-emerald-400 font-mono font-bold">{result.analysis?.recommended_counter_base}</span></p>
                  <p><strong>Leverage Stature:</strong> {result.analysis?.negotiation_stature}</p>
                </div>
                <div className="p-2.5 rounded bg-blue-950/30 border border-blue-500/30 text-blue-200 space-y-1">
                  <strong>Key Discussion Points:</strong>
                  <ul className="list-disc list-inside space-y-0.5 font-mono text-[11px]">
                    {result.analysis?.negotiation_points?.map((pt: string, i: number) => (
                      <li key={i}>{pt}</li>
                    ))}
                  </ul>
                </div>
              </Card>

              {/* Counter-Offer Draft */}
              <Card variant="subtle" padding="md" className="space-y-2 text-xs">
                <h3 className="font-bold text-white font-display-title">Drafted Counter-Offer Letter</h3>
                <div className="p-3 rounded bg-[#101524] border border-[#1c2438] font-mono text-xs text-emerald-200 leading-relaxed max-h-56 overflow-y-auto whitespace-pre-wrap">
                  {result.counter_offer_draft}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
