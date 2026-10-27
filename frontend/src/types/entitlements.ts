export type PlanId = 'free' | 'student' | 'personal' | 'power' | 'teams' | 'enterprise';

export type CapabilityId =
  // CORE
  | 'core.chat.basic'
  | 'core.chat.long_context'
  | 'core.chat.multimodal'
  | 'core.chat.advanced_reasoning'
  // MEMORY
  | 'memory.session'
  | 'memory.profile'
  | 'memory.persistent'
  | 'memory.semantic'
  | 'memory.manage'
  | 'memory.export'
  // DOCUMENTS
  | 'documents.import.pdf'
  | 'documents.import.docx'
  | 'documents.import.images'
  | 'documents.import.spreadsheets'
  | 'documents.analysis'
  | 'documents.export.pdf'
  | 'documents.export.docx'
  | 'documents.versioning'
  // CAREER
  | 'career.master_resume'
  | 'career.resume_import'
  | 'career.jd_analysis'
  | 'career.resume_tailoring'
  | 'career.ats'
  | 'career.application_tracker'
  | 'career.interview_prep'
  | 'career.star'
  | 'career.salary_coach'
  | 'career.goals'
  | 'career.trajectory'
  // VOICE
  | 'voice.input'
  | 'voice.output'
  | 'voice.realtime'
  | 'voice.saarthi'
  | 'voice.wake_word'
  | 'voice.proactive'
  // TOOLS
  | 'tools.files'
  | 'tools.search'
  | 'tools.browser'
  | 'tools.data_analysis'
  | 'tools.code_execution'
  | 'tools.terminal'
  | 'tools.git'
  | 'tools.github'
  | 'tools.calendar'
  | 'tools.email'
  | 'tools.computer_control'
  | 'tools.api'
  // AGENTS
  | 'agents.guided'
  | 'agents.custom'
  | 'agents.multistep'
  | 'agents.autonomous'
  | 'agents.background'
  | 'agents.proactive'
  // RESEARCH
  | 'research.basic'
  | 'research.deep'
  | 'research.multi_source'
  | 'research.paper_analysis'
  | 'research.domain_research'
  // DOMAINS
  | 'domain.career'
  | 'domain.education'
  | 'domain.writing'
  | 'domain.general'
  | 'domain.business'
  | 'domain.engineering'
  | 'domain.software'
  | 'domain.cybersecurity'
  | 'domain.science'
  | 'domain.research'
  | 'domain.custom'
  // WORKSPACES
  | 'workspace.projects'
  | 'workspace.knowledge'
  | 'workspace.agents'
  | 'workspace.domains'
  | 'workspace.automation'
  // TEAM
  | 'team.workspace'
  | 'team.shared_memory'
  | 'team.shared_agents'
  | 'team.rbac'
  | 'team.audit'
  | 'team.sso';

export interface PlanCatalogItem {
  id: PlanId;
  name: string;
  price_inr: number;
  billing_period: string;
  description: string;
  badge: string;
}

export type EntitlementsMap = Record<CapabilityId | string, boolean>;

export interface UsageLimitsMap {
  monthly_resume_tailorings: number;
  monthly_agent_tasks: number;
  monthly_deep_research: number;
  custom_agents: number;
  vault_storage_gb: number;
  [key: string]: number;
}

export interface DomainPackConfig {
  id: string;
  name: string;
  category: string;
  description: string;
  minimum_plan: PlanId;
  capabilities: string[];
  tools: string[];
  icon: string;
  is_active: boolean;
  is_installed: boolean;
}
