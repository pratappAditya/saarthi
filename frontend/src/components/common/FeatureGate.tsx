import React from 'react';
import { Lock, Sparkles, ShieldAlert, ArrowUpRight } from 'lucide-react';
import { useEntitlements } from '../../context/EntitlementContext';
import type { CapabilityId, PlanId } from '../../types/entitlements';
import { Card } from './Card';
import { Button } from './Button';
import { Badge } from './Badge';

interface FeatureGateProps {
  capability: CapabilityId | string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
}

export const FeatureGate: React.FC<FeatureGateProps> = ({
  capability,
  children,
  fallback,
  showUpgradePrompt = true
}) => {
  const { hasCapability, openUpgradeModal } = useEntitlements();

  if (hasCapability(capability)) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (showUpgradePrompt) {
    return <UpgradePrompt capability={capability} />;
  }

  return null;
};

interface PlanGateProps {
  minimumPlan: PlanId;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PlanGate: React.FC<PlanGateProps> = ({
  minimumPlan,
  children,
  fallback
}) => {
  const { hasPlan, openUpgradeModal } = useEntitlements();

  if (hasPlan(minimumPlan)) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  return (
    <Card variant="subtle" padding="md" className="space-y-3 text-xs text-center border-amber-500/30 bg-amber-950/20">
      <Lock className="w-6 h-6 mx-auto text-amber-400" />
      <div>
        <h4 className="font-bold text-white uppercase text-[11px] font-mono">Plan Required: {minimumPlan.toUpperCase()}</h4>
        <p className="text-gray-400 mt-1">This feature requires a minimum of the {minimumPlan.toUpperCase()} plan.</p>
      </div>
      <Button variant="primary" size="sm" icon={ArrowUpRight} onClick={() => openUpgradeModal()}>
        Upgrade to {minimumPlan.toUpperCase()}
      </Button>
    </Card>
  );
};

interface UpgradePromptProps {
  capability: string;
  title?: string;
  description?: string;
}

export const UpgradePrompt: React.FC<UpgradePromptProps> = ({
  capability,
  title,
  description
}) => {
  const { openUpgradeModal } = useEntitlements();

  const formattedCapName = capability
    .split('.')
    .pop()
    ?.replace(/_/g, ' ')
    .toUpperCase() || 'CAPABILITY';

  return (
    <Card variant="subtle" padding="md" className="space-y-3 text-xs border border-amber-500/30 bg-[#121624]">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-amber-400 font-mono font-bold text-[10px]">
          <Lock className="w-3.5 h-3.5" />
          <span>LOCKED CAPABILITY — {formattedCapName}</span>
        </div>
        <Badge variant="warning" size="xs">Power / Pro</Badge>
      </div>

      <div>
        <h4 className="font-bold text-white text-sm">{title || `${formattedCapName} Upgrade`}</h4>
        <p className="text-gray-400 font-mono text-[11px] mt-1 leading-relaxed">
          {description || `Unlock ${formattedCapName} for advanced automated workflows, terminal execution, and proactive AI.`}
        </p>
      </div>

      <div className="flex items-center gap-2 pt-1">
        <Button variant="primary" size="sm" icon={Sparkles} onClick={() => openUpgradeModal(capability)}>
          Upgrade Plan
        </Button>
        <span className="text-[10px] text-gray-500 font-mono">From ₹399/mo</span>
      </div>
    </Card>
  );
};

interface UsageLimitProps {
  capability: string;
  currentCount?: number;
  maxLimit?: number;
}

export const UsageLimit: React.FC<UsageLimitProps> = ({
  capability,
  currentCount = 0,
  maxLimit = 100
}) => {
  const isUnlimited = maxLimit === -1;
  const pct = isUnlimited ? 0 : Math.min(100, Math.round((currentCount / maxLimit) * 100));

  return (
    <div className="p-2.5 rounded bg-white/5 border border-white/10 space-y-1.5 text-xs font-mono">
      <div className="flex justify-between text-[10px] text-gray-300">
        <span>{capability} Usage</span>
        <span>{isUnlimited ? 'Unlimited' : `${currentCount} / ${maxLimit}`}</span>
      </div>
      {!isUnlimited && (
        <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-300 ${pct > 85 ? 'bg-rose-500' : pct > 60 ? 'bg-amber-400' : 'bg-emerald-400'}`} 
            style={{ width: `${pct}%` }} 
          />
        </div>
      )}
    </div>
  );
};

interface EntitledFeatureProps {
  capability: string;
  label?: string;
}

export const EntitledFeature: React.FC<EntitledFeatureProps> = ({ capability, label }) => {
  const { hasCapability } = useEntitlements();
  const entitled = hasCapability(capability);

  return (
    <div className={`flex items-center gap-1.5 text-xs font-mono ${entitled ? 'text-emerald-400' : 'text-gray-500'}`}>
      <span>{entitled ? '✓' : '✗'}</span>
      <span>{label || capability}</span>
    </div>
  );
};
