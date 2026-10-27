import React from 'react';
import { 
  Sparkles, CheckCircle2, Lock, ShieldCheck, ArrowUpRight, Zap 
} from 'lucide-react';
import { useEntitlements } from '../../context/EntitlementContext';
import { Modal } from './Modal';
import { Button } from './Button';
import { Badge } from './Badge';
import type { PlanId } from '../../types/entitlements';

export const UpgradeModal: React.FC = () => {
  const { 
    isUpgradeModalOpen, 
    closeUpgradeModal, 
    activePlanId, 
    switchPlanDev,
    targetUpgradeCapability,
    catalog 
  } = useEntitlements();

  if (!isUpgradeModalOpen) return null;

  const plans: { id: PlanId; name: string; price: string; period: string; features: string[] }[] = [
    {
      id: 'free',
      name: 'Free',
      price: '₹0',
      period: 'forever',
      features: ['Basic Chat & Memory', 'PDF/DOCX Import & Export', 'Master Resume & ATS', 'Career Applications Tracker']
    },
    {
      id: 'student',
      name: 'Student',
      price: '₹99',
      period: '/month',
      features: ['Everything in Free', 'Education & Study Domain Pack', 'STAR Drills & Salary Coach', 'Guided Workflows & 10GB Vault']
    },
    {
      id: 'personal',
      name: 'Personal',
      price: '₹399',
      period: '/month',
      features: ['Everything in Student', 'Long-term Semantic Memory', 'Saarthi Voice & Real-time Voice', 'Browser & Code Execution Sandbox']
    },
    {
      id: 'power',
      name: 'Power',
      price: '₹799',
      period: '/month',
      features: ['Everything in Personal', 'Terminal & Git / GitHub API', 'Computer Control & Autonomous Agents', 'All 10 Domain Packs & Deep Research']
    },
    {
      id: 'teams',
      name: 'Teams',
      price: '₹699',
      period: '/user/month',
      features: ['Everything in Power', 'Shared Team Workspace & Memory', 'Shared Agent Library', 'RBAC & Audit Logs']
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      features: ['Everything in Teams', 'Dedicated Infrastructure', 'SAML/SSO & SCIM', 'Custom Domain Packs & SLAs']
    }
  ];

  const handleSelectPlan = async (planId: PlanId) => {
    await switchPlanDev(planId);
    closeUpgradeModal();
  };

  return (
    <Modal
      isOpen={isUpgradeModalOpen}
      onClose={closeUpgradeModal}
      title="Unlock Saarthi AI Capabilities"
    >
      <div className="space-y-4 text-xs">
        {targetUpgradeCapability && (
          <div className="p-3 rounded bg-amber-950/30 border border-amber-500/30 text-amber-200 flex items-center justify-between font-mono">
            <span>Capability Required: <strong>{targetUpgradeCapability}</strong></span>
            <Badge variant="warning" size="xs">Locked on {activePlanId.toUpperCase()}</Badge>
          </div>
        )}

        <div className="text-gray-300 space-y-1">
          <p className="text-sm font-bold text-white">Choose your Saarthi Operating Plan</p>
          <p className="text-xs text-gray-400">Select a plan below to test entitlement switching in local development mode.</p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {plans.map((p) => {
            const isCurrent = activePlanId === p.id;
            return (
              <div 
                key={p.id}
                className={`p-4 rounded-xl border transition-all flex flex-col justify-between space-y-3 ${
                  isCurrent 
                    ? 'border-blue-500 bg-blue-950/30 ring-1 ring-blue-500' 
                    : 'border-white/10 bg-white/5 hover:border-white/20'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-white text-sm">{p.name}</h4>
                    {isCurrent && <Badge variant="accent" size="xs">Active Plan</Badge>}
                  </div>
                  <div>
                    <span className="text-xl font-bold text-white">{p.price}</span>
                    <span className="text-[10px] text-gray-400 font-mono">{p.period}</span>
                  </div>

                  <ul className="space-y-1 pt-2 border-t border-white/10 text-[11px] font-mono text-gray-300">
                    {p.features.map((f, fi) => (
                      <li key={fi} className="flex items-center gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <Button
                  variant={isCurrent ? 'outline' : 'primary'}
                  size="sm"
                  className="w-full mt-2"
                  onClick={() => handleSelectPlan(p.id)}
                >
                  {isCurrent ? 'Current Plan' : `Switch to ${p.name} (Dev)`}
                </Button>
              </div>
            );
          })}
        </div>

        <div className="p-3 rounded bg-white/5 border border-white/10 text-[11px] font-mono text-gray-400 text-center">
          Payment processing gateway is not connected in Phase 5A. The plan switcher above updates backend entitlements in local dev mode.
        </div>
      </div>
    </Modal>
  );
};
