import React, { createContext, useContext, useState, useEffect } from 'react';
import type { 
  PlanId, CapabilityId, EntitlementsMap, UsageLimitsMap, 
  PlanCatalogItem, DomainPackConfig 
} from '../types/entitlements';
import { API_BASE } from '../api';

const PLAN_HIERARCHY: Record<PlanId, number> = {
  free: 1,
  student: 2,
  personal: 3,
  power: 4,
  teams: 5,
  enterprise: 6
};

interface EntitlementContextType {
  activePlanId: PlanId;
  planName: string;
  capabilities: EntitlementsMap;
  limits: UsageLimitsMap;
  catalog: Record<string, PlanCatalogItem>;
  domainPacks: DomainPackConfig[];
  isLoading: boolean;
  hasCapability: (capabilityId: CapabilityId | string) => boolean;
  hasPlan: (minimumPlanId: PlanId) => boolean;
  switchPlanDev: (planId: PlanId) => Promise<void>;
  refreshEntitlements: () => Promise<void>;
  isUpgradeModalOpen: boolean;
  targetUpgradeCapability: string | null;
  openUpgradeModal: (capabilityId?: string) => void;
  closeUpgradeModal: () => void;
}

const EntitlementContext = createContext<EntitlementContextType | undefined>(undefined);

export const EntitlementProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePlanId, setActivePlanId] = useState<PlanId>('power');
  const [planName, setPlanName] = useState<string>('Saarthi Power');
  const [capabilities, setCapabilities] = useState<EntitlementsMap>({});
  const [limits, setLimits] = useState<UsageLimitsMap>({
    monthly_resume_tailorings: 1000,
    monthly_agent_tasks: 1000,
    monthly_deep_research: 300,
    custom_agents: 50,
    vault_storage_gb: 200
  });
  const [catalog, setCatalog] = useState<Record<string, PlanCatalogItem>>({});
  const [domainPacks, setDomainPacks] = useState<DomainPackConfig[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState<boolean>(false);
  const [targetUpgradeCapability, setTargetUpgradeCapability] = useState<string | null>(null);

  useEffect(() => {
    refreshEntitlements();
  }, []);

  const refreshEntitlements = async () => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE}/account/capabilities`);
      if (res.ok) {
        const data = await res.json();
        setActivePlanId(data.plan_id as PlanId);
        setPlanName(data.plan_name || 'Saarthi Power');
        setCapabilities(data.entitlements || {});
        setLimits(data.limits || {});
        setDomainPacks(data.domain_packs || []);
      }

      const planRes = await fetch(`${API_BASE}/account/plan`);
      if (planRes.ok) {
        const planData = await planRes.json();
        setCatalog(planData.catalog || {});
      }
    } catch (err) {
      console.error("Failed to hydrate entitlements from backend:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const hasCapability = (capabilityId: CapabilityId | string): boolean => {
    return Boolean(capabilities[capabilityId]);
  };

  const hasPlan = (minimumPlanId: PlanId): boolean => {
    const currentRank = PLAN_HIERARCHY[activePlanId] || 1;
    const requiredRank = PLAN_HIERARCHY[minimumPlanId] || 1;
    return currentRank >= requiredRank;
  };

  const switchPlanDev = async (newPlanId: PlanId) => {
    try {
      const res = await fetch(`${API_BASE}/account/dev-switch-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan_id: newPlanId })
      });
      if (res.ok) {
        const data = await res.json();
        setActivePlanId(data.subscription.plan_id as PlanId);
        setPlanName(data.active_plan.name);
        setCapabilities(data.entitlements || {});
        setLimits(data.limits || {});
      }
    } catch (err) {
      console.error("Dev plan switch failed:", err);
    }
  };

  const openUpgradeModal = (capabilityId?: string) => {
    setTargetUpgradeCapability(capabilityId || null);
    setIsUpgradeModalOpen(true);
  };

  const closeUpgradeModal = () => {
    setIsUpgradeModalOpen(false);
    setTargetUpgradeCapability(null);
  };

  return (
    <EntitlementContext.Provider
      value={{
        activePlanId,
        planName,
        capabilities,
        limits,
        catalog,
        domainPacks,
        isLoading,
        hasCapability,
        hasPlan,
        switchPlanDev,
        refreshEntitlements,
        isUpgradeModalOpen,
        targetUpgradeCapability,
        openUpgradeModal,
        closeUpgradeModal
      }}
    >
      {children}
    </EntitlementContext.Provider>
  );
};

export const useEntitlements = () => {
  const ctx = useContext(EntitlementContext);
  if (!ctx) {
    throw new Error("useEntitlements must be used within an EntitlementProvider");
  }
  return ctx;
};
