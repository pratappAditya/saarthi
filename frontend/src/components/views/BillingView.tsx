import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Check, ShieldCheck, Zap, Lock, CreditCard, Layers, Users, Download, FileText, Sparkles, AlertCircle } from 'lucide-react';
import { useEntitlements } from '../../context/EntitlementContext';
import { useApp } from '../../context/AppContext';
import type { PlanId } from '../../types/entitlements';

export const BillingView: React.FC = () => {
  const { addToast } = useApp();
  const { activePlanId, planName, switchPlanDev, limits, domainPacks } = useEntitlements();
  const [switching, setSwitching] = useState<string | null>(null);
  const [selectedLockedFeature, setSelectedLockedFeature] = useState<{ name: string; requiredPlan: string; reason: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'plans' | 'invoices' | 'teams'>('plans');

  // Simulated User Invoices List
  const invoices = [
    { id: 'INV-2026-001', date: '2026-08-01', amount: '₹799', status: 'PAID', plan: 'POWER' },
    { id: 'INV-2026-002', date: '2026-07-01', amount: '₹399', status: 'PAID', plan: 'PERSONAL' },
  ];

  // Simulated Team Members
  const [teamMembers, setTeamMembers] = useState([
    { id: 'm1', name: 'User Admin (You)', email: 'admin@saarthi.local', role: 'OWNER', status: 'ACTIVE' },
    { id: 'm2', name: 'Priya Sharma', email: 'priya@techco.com', role: 'ADMIN', status: 'ACTIVE' },
    { id: 'm3', name: 'Rohan Gupta', email: 'rohan@techco.com', role: 'MEMBER', status: 'ACTIVE' },
  ]);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const seatLimit = 5;

  const plans: { id: PlanId; name: string; price: string; period: string; badge: string; description: string; features: string[] }[] = [
    {
      id: 'free',
      name: 'Free Baseline',
      badge: '₹0',
      price: '₹0',
      period: 'forever',
      description: 'Essential local career tools and basic chat companion.',
      features: [
        'Local Master Resume parsing & storage',
        'Basic ATS match score extraction',
        'PDF/DOCX document export',
        '100% Offline execution on device'
      ]
    },
    {
      id: 'student',
      name: 'Student',
      badge: '₹99/mo',
      price: '₹99',
      period: 'per month',
      description: 'For students & learners with Education domain pack and study tools.',
      features: [
        'Everything in Free',
        'Education & Study Domain Pack',
        'STAR interview drills & 8-dimension scorer',
        'Salary & Offer negotiation coach',
        '10GB vault storage'
      ]
    },
    {
      id: 'personal',
      name: 'Personal',
      badge: '₹399/mo',
      price: '₹399',
      period: 'per month',
      description: 'Full personal AI companion with long-term semantic memory and voice.',
      features: [
        'Everything in Student',
        'Long-term semantic memory & profile persistence',
        'Saarthi custom voice persona & real-time voice',
        'Automated web browser & code execution sandbox',
        '50GB vault storage'
      ]
    },
    {
      id: 'power',
      name: 'Power',
      badge: '₹799/mo',
      price: '₹799',
      period: 'per month',
      description: 'For developers & researchers with terminal, computer control, and deep research.',
      features: [
        'Everything in Personal',
        'Interactive terminal & Git/GitHub API',
        'Computer control & autonomous agents',
        'All 10 Domain Packs (Engineering, Cyber, Science)',
        '200GB vault storage'
      ]
    },
    {
      id: 'teams',
      name: 'Teams',
      badge: '₹699/user',
      price: '₹699',
      period: 'per user / month',
      description: 'Shared team workspace, team memory, RBAC, and agent workflows.',
      features: [
        'Everything in Power',
        'Shared team workspace & memory',
        'Shared agent library & RBAC controls',
        '1TB team vault storage'
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      badge: 'Custom',
      price: 'Custom',
      period: 'tailored billing',
      description: 'Dedicated infrastructure, SAML/SSO, audit logs, and enterprise SLAs.',
      features: [
        'Everything in Teams',
        'Dedicated local/private deployment',
        'SAML/SSO & SCIM enterprise auth',
        'Custom domain packs & dedicated SLAs'
      ]
    }
  ];

  const handleSwitchPlan = async (planId: PlanId) => {
    try {
      setSwitching(planId);
      await switchPlanDev(planId);
      addToast({
        type: 'success',
        title: 'Plan Updated',
        message: `Subscription successfully updated to '${planId.toUpperCase()}'. Server verified signature.`
      });
    } catch (err) {
      addToast({ type: 'error', title: 'Switch Failed', message: 'Could not switch plan.' });
    } finally {
      setSwitching(null);
    }
  };

  const handleAddTeamMember = () => {
    if (!newMemberEmail || !newMemberEmail.includes('@')) {
      addToast({ type: 'error', title: 'Invalid Email', message: 'Please enter a valid email address.' });
      return;
    }
    if (teamMembers.length >= seatLimit) {
      addToast({ type: 'error', title: 'Seat Limit Reached', message: `Organization seat limit (${seatLimit}) reached. Upgrade seats to invite more members.` });
      return;
    }
    setTeamMembers([
      ...teamMembers,
      { id: `m_${Date.now()}`, name: newMemberEmail.split('@')[0], email: newMemberEmail, role: 'MEMBER', status: 'PENDING' }
    ]);
    setNewMemberEmail('');
    addToast({ type: 'success', title: 'Invitation Sent', message: `Invited ${newMemberEmail} to team organization.` });
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-subtle)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-secondary)] mb-1">
            <CreditCard className="w-3.5 h-3.5 text-blue-400" />
            <span>SAARTHI BILLING & SUBSCRIPTION MANAGEMENT</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Billing, Invoices & Team Seats
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Manage your subscription tier, Razorpay payments, download invoices, and configure team workspace seats.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="accent" size="md">
            Active Plan: {planName} ({activePlanId.toUpperCase()})
          </Badge>
        </div>
      </div>

      {/* Payments Policy Banner */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-4 text-xs font-mono text-amber-200">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <span className="font-bold text-amber-300">Payments coming after funding.</span>
            <p className="text-[11px] text-amber-200/80 mt-0.5">
              Live payment processing is intentionally disabled. Plan catalog & subscriptions are active in preview / test mode.
            </p>
          </div>
        </div>
        <Badge variant="accent" size="sm">TEST MODE ONLY</Badge>
      </div>

      {/* Subscription Status Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/40 border border-blue-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs font-mono">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-bold text-white">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Status: Subscription Active (Preview / Test Mode)</span>
          </div>
          <p className="text-gray-400">Next billing date: <span className="text-white font-bold">2026-09-29</span> via Razorpay Sandbox.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="xs" onClick={() => handleSwitchPlan('free')}>
            Cancel Subscription
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveTab('plans')}
          className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
            activeTab === 'plans' ? 'bg-blue-600 text-white font-bold' : 'text-gray-400 hover:bg-white/5'
          }`}
        >
          Plans & Pricing Catalog
        </button>
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
            activeTab === 'invoices' ? 'bg-blue-600 text-white font-bold' : 'text-gray-400 hover:bg-white/5'
          }`}
        >
          Invoices & Billing Receipts
        </button>
        <button
          onClick={() => setActiveTab('teams')}
          className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
            activeTab === 'teams' ? 'bg-blue-600 text-white font-bold' : 'text-gray-400 hover:bg-white/5'
          }`}
        >
          Team Organization & Seats
        </button>
      </div>

      {/* Tab 1: Plans Catalog Grid */}
      {activeTab === 'plans' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plans.map((p) => {
              const isCurrent = activePlanId === p.id;
              return (
                <Card
                  key={p.id}
                  variant="default"
                  padding="md"
                  className={`space-y-3 text-xs flex flex-col justify-between transition-all ${
                    isCurrent ? 'ring-2 ring-blue-500 border-blue-500 bg-blue-950/20' : ''
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Badge variant={isCurrent ? 'accent' : 'outline'} size="xs">{p.badge}</Badge>
                      {isCurrent && <span className="text-[10px] text-emerald-400 font-mono font-bold">Active Plan</span>}
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base">{p.name}</h3>
                      <p className="text-gray-400 font-mono text-[11px] mt-0.5">{p.description}</p>
                    </div>

                    <div className="pt-1">
                      <span className="text-2xl font-bold text-white tracking-tight">{p.price}</span>
                      <span className="text-[10px] text-gray-400 font-mono ml-1">{p.period}</span>
                    </div>

                    <ul className="space-y-1.5 pt-3 border-t border-white/10 text-[11px] font-mono text-gray-300">
                      {p.features.map((f, fi) => (
                        <li key={fi} className="flex items-center gap-1.5">
                          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Button
                    variant={isCurrent ? 'outline' : 'primary'}
                    size="sm"
                    className="w-full mt-3"
                    isLoading={switching === p.id}
                    onClick={() => handleSwitchPlan(p.id)}
                  >
                    {isCurrent ? 'Active Plan' : `Upgrade to ${p.name}`}
                  </Button>
                </Card>
              );
            })}
          </div>

          {/* Active Limits & Domain Packs Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-2">
            <div className="lg:col-span-6">
              <Card variant="default" padding="md" className="space-y-3 text-xs">
                <h3 className="font-bold text-white font-display-title">Active Usage Limits ({activePlanId.toUpperCase()})</h3>
                <div className="space-y-2 font-mono text-[11px] text-gray-300">
                  <div className="flex justify-between p-2 rounded bg-white/5 border border-white/10">
                    <span>Monthly Resume Tailorings:</span>
                    <span className="text-emerald-400 font-bold">{limits.monthly_resume_tailorings === -1 ? 'Unlimited' : limits.monthly_resume_tailorings}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-white/5 border border-white/10">
                    <span>Monthly Agent Tasks:</span>
                    <span className="text-blue-400 font-bold">{limits.monthly_agent_tasks === -1 ? 'Unlimited' : limits.monthly_agent_tasks}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-white/5 border border-white/10">
                    <span>Monthly Deep Research Runs:</span>
                    <span className="text-amber-400 font-bold">{limits.monthly_deep_research === -1 ? 'Unlimited' : limits.monthly_deep_research}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-white/5 border border-white/10">
                    <span>Vault Storage Allocation:</span>
                    <span className="text-purple-400 font-bold">{limits.vault_storage_gb} GB</span>
                  </div>
                </div>
              </Card>
            </div>

            <div className="lg:col-span-6">
              <Card variant="subtle" padding="md" className="space-y-3 text-xs">
                <h3 className="font-bold text-white flex items-center justify-between">
                  <span>Domain Packs Access Status</span>
                  <span className="text-[10px] text-gray-400 font-mono">{domainPacks.length} Available</span>
                </h3>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  {domainPacks.slice(0, 6).map((dp) => (
                    <div key={dp.id} className="p-2 rounded bg-white/5 border border-white/10 space-y-0.5">
                      <div className="flex justify-between text-gray-200 font-bold">
                        <span>{dp.name.split(' ')[0]}</span>
                        <Badge variant={dp.minimum_plan === activePlanId ? 'accent' : 'outline'} size="xs">{dp.minimum_plan}</Badge>
                      </div>
                      <p className="text-[10px] text-gray-400 truncate">{dp.category}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Invoices List */}
      {activeTab === 'invoices' && (
        <Card variant="default" padding="md" className="space-y-4 text-xs font-mono">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-sm">Billing History & Invoices</h3>
            <Badge variant="outline" size="xs">Provider: Razorpay Sandbox</Badge>
          </div>

          <div className="divide-y divide-white/10">
            {invoices.map((inv) => (
              <div key={inv.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <div>
                    <span className="text-white font-bold block">{inv.id}</span>
                    <span className="text-gray-400 text-[10px]">{inv.date} — Plan: {inv.plan}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-emerald-400 font-bold">{inv.amount}</span>
                  <Badge variant="accent" size="xs">{inv.status}</Badge>
                  <Button variant="ghost" size="xs" onClick={() => addToast({ type: 'info', title: 'Receipt PDF', message: `Downloading invoice receipt ${inv.id}...` })}>
                    <Download className="w-3.5 h-3.5 mr-1" /> PDF
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Tab 3: Team Management & Seats */}
      {activeTab === 'teams' && (
        <div className="space-y-4 text-xs font-mono">
          <Card variant="default" padding="md" className="space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div>
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <Users className="w-4 h-4 text-purple-400" />
                  <span>Saarthi Team Workspace (TechCo Org)</span>
                </h3>
                <p className="text-gray-400 text-[11px] mt-0.5">Seats allocated: {teamMembers.length} of {seatLimit} seats (₹699/user/month).</p>
              </div>
              <Badge variant="accent" size="sm">Seats Used: {teamMembers.length}/{seatLimit}</Badge>
            </div>

            {/* Invite New Member */}
            <div className="flex items-center gap-2">
              <input
                type="email"
                placeholder="Enter colleague email address..."
                value={newMemberEmail}
                onChange={(e) => setNewMemberEmail(e.target.value)}
                className="flex-1 bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
              <Button variant="primary" size="sm" onClick={handleAddTeamMember}>
                Invite Member
              </Button>
            </div>

            {/* Members Directory */}
            <div className="divide-y divide-white/10 pt-2">
              {teamMembers.map((m) => (
                <div key={m.id} className="py-2.5 flex items-center justify-between">
                  <div>
                    <span className="text-white font-bold block">{m.name}</span>
                    <span className="text-gray-400 text-[10px]">{m.email}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant={m.role === 'OWNER' ? 'accent' : 'outline'} size="xs">{m.role}</Badge>
                    <span className="text-emerald-400 text-[10px]">{m.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Feature Locked Explanation Modal */}
      {selectedLockedFeature && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-blue-500/40 rounded-2xl max-w-md w-full p-6 space-y-4 text-xs font-mono text-white shadow-2xl">
            <div className="flex items-center gap-3 text-amber-400">
              <Lock className="w-6 h-6" />
              <h3 className="font-bold text-base text-white">Feature Locked</h3>
            </div>
            <p className="text-gray-300">
              The feature <span className="text-blue-400 font-bold">{selectedLockedFeature.name}</span> requires the <span className="text-emerald-400 font-bold">{selectedLockedFeature.requiredPlan}</span> plan or higher.
            </p>
            <p className="text-gray-400 text-[11px]">
              Reason: {selectedLockedFeature.reason}
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setSelectedLockedFeature(null)}>
                Close
              </Button>
              <Button variant="primary" size="sm" onClick={() => { setSelectedLockedFeature(null); setActiveTab('plans'); }}>
                Upgrade Plan Now
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
