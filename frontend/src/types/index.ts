export type ExperienceMode = 'signature' | 'forge' | 'pulse' | 'aurora';
export type ThemeMode = 'dark' | 'light' | 'system';
export type AccentColor = 'sapphire' | 'emerald' | 'amber' | 'amethyst' | 'rose' | 'cyan';
export type DensityMode = 'comfortable' | 'compact' | 'dense';
export type MotionIntensity = 'subtle' | 'expressive' | 'reduced';
export type SidebarMode = 'expanded' | 'collapsed' | 'compact';

export type AIStatusType = 
  | 'ready'
  | 'setting_up'
  | 'downloading'
  | 'offline'
  | 'model_update_available'
  | 'insufficient_resources'
  | 'error';

export type NavSection =
  | 'home'
  | 'career'
  | 'resumes'
  | 'tailor'
  | 'cover-letters'
  | 'applications'
  | 'interviews'
  | 'memory'
  | 'projects'
  | 'trust'
  | 'profile'
  | 'agents'
  | 'dashboard'
  | 'salary'
  | 'goals'
  | 'trajectory'
  | 'assistant'
  | 'documents'
  | 'insights'
  | 'ai-models'
  | 'settings'
  | 'billing'
  | 'privacy'
  | 'voice'
  | 'personalization'
  | 'routines'
  | 'cross-domain'
  | 'workflow'
  | 'admin'
  | 'legal'
  | 'design-system';

export interface NemotronModel {
  id: string;
  name: string;
  tag: string;
  size: string;
  vramRequired: string;
  ramRequired: string;
  description: string;
  speed: string;
  quantization: string;
  recommendedFor: string;
  isInstalled: boolean;
  isActive: boolean;
  downloadProgress?: number;
}

export interface SystemHardware {
  cpu: string;
  cores: number;
  ramTotal: string;
  ramAvailable: string;
  gpu: string;
  vramTotal: string;
  vramAvailable: string;
  storageFree: string;
  ollamaVersion: string;
  ollamaRunning: boolean;
  nemotronRunning: boolean;
  activeModel: string;
  inferenceSpeed: number | null;
  isBenchmarked: boolean;
  gpuLoad: number;
  vramUsage: number;
}

export interface ResumeBullet {
  id: string;
  text: string;
  impactScore: number;
  highlightedKeywords: string[];
  suggestedImprovement?: string;
}

export interface ResumeSection {
  id: string;
  title: string;
  bullets?: ResumeBullet[];
  content?: string;
  company?: string;
  role?: string;
  period?: string;
  location?: string;
}

export interface ResumeItem {
  id: string;
  title: string;
  targetRole: string;
  version: string;
  lastModified: string;
  atsScore: number;
  matchRate: number;
  isDefault: boolean;
  pages: number;
  skills: string[];
  summary: string;
  sections: ResumeSection[];
  linkedApplicationsCount: number;
  versions?: Array<{
    id: string;
    tag: string;
    createdAt: string;
    sections: any[];
  }>;
  activeVersionId?: string;
  filename?: string;
  fileType?: string;
  fileRef?: string;
}

export interface ATSAnalysisResult {
  overallScore: number;
  parseRate: number;
  keywordMatchRate: number;
  formatCompatibility: number;
  matchedKeywords: string[];
  missingKeywords: string[];
  crucialSkillsMissing: string[];
  actionableInsights: {
    category: 'critical' | 'improvement' | 'strength';
    title: string;
    description: string;
  }[];
}

export interface TailoredDiffItem {
  id: string;
  section: string;
  originalText: string;
  tailoredText: string;
  reason: string;
  accepted: boolean;
}

export interface ApplicationItem {
  id: string;
  company: string;
  companyLogoText: string;
  role: string;
  location: string;
  type: 'Full-time' | 'Remote' | 'Hybrid' | 'Contract';
  salaryRange: string;
  dateApplied: string;
  stage: 'saved' | 'applied' | 'screening' | 'interview' | 'offer' | 'rejected' | 'withdrawn';
  matchScore: number;
  resumeUsedId: string;
  resumeUsedTitle: string;
  nextFollowUpDate: string;
  notes: string;
  contacts: { name: string; title: string; email: string }[];
  interviewDate?: string;
  jobDescription: string;
  tags: string[];
  timeline: {
    date: string;
    event: string;
    details?: string;
  }[];
}

export interface InterviewQuestion {
  id: string;
  category: 'behavioral' | 'technical' | 'system_design' | 'situational' | 'culture';
  question: string;
  difficulty: 'Foundation' | 'Intermediate' | 'Advanced';
  companyTarget?: string;
  starStructure: {
    situation: string;
    task: string;
    action: string;
    result: string;
  };
  sampleAnswer: string;
  userAnswer?: string;
  feedback?: {
    score: number;
    impactScore: number;
    clarityScore: number;
    technicalAccuracy: number;
    strengths: string[];
    gaps: string[];
    improvedBulletSuggestion: string;
  };
}

export interface CoverLetterItem {
  id: string;
  targetCompany: string;
  targetRole: string;
  tone: 'Confident' | 'Technical' | 'Executive' | 'Conversational';
  dateCreated: string;
  content: string;
  jobMatchScore: number;
  linkedResumeId: string;
}

export interface CareerGoal {
  targetTitle: string;
  targetLevel: string;
  targetCompRange: string;
  targetIndustries: string[];
  coreSkills: { name: string; proficiency: number; demand: 'High' | 'Very High' | 'Medium' }[];
  timelineGoal: string;
  weeklyApplicationTarget: number;
  weeklyApplicationsDone: number;
}

export interface PlanTier {
  id: 'free' | 'student' | 'personal' | 'power';
  name: string;
  badge?: string;
  inrPrice: number;
  usdPrice: number;
  billingPeriod: string;
  tagline: string;
  features: string[];
  isPopular?: boolean;
  ctaText: string;
}

// Legacy Saarthi Types
export type NavTab = string;
export type MemoryCategory = string;
export type JobApplication = any;
export type ApplicationStatus = any;

export interface SaarthiState {
  system_status?: any;
  messages?: any[];
  tasks?: any[];
  memories?: any[];
  activity_logs?: any[];
  active_tab?: string;
  sidebar_open?: boolean;
  selected_file?: string | null;
  working_dir?: string;
  [key: string]: any;
}

export interface FileItem {
  id?: string;
  name: string;
  path: string;
  is_dir: boolean;
  size?: number | string;
  type?: string;
  indexed?: boolean;
  lastModified?: string;
  tags?: string[];
  status?: string;
  contentPreview?: string;
}

export interface MemoryItem {
  id: number | string;
  title?: string;
  category: string;
  key?: string;
  content: string;
  project?: string;
  project_id?: string;
  status?: string;
  created_at?: string;
  createdAt?: string;
  updatedAt?: string;
  pinned?: boolean;
  tags?: string[];
}

export interface TaskItem {
  id: string;
  task_id?: string;
  name?: string;
  title?: string;
  description?: string;
  status: string;
  progress?: number;
  created_at?: string;
  dueDate?: string;
  createdBy?: string;
  relatedFileNames?: string[];
  priority?: 'high' | 'medium' | 'low' | string;
}

export interface ActivityLog {
  id: string;
  title?: string;
  description?: string;
  timestamp: string;
  timeFormatted?: string;
  type?: string;
  message?: string;
  details?: any;
  toolName?: string;
  actionType?: string;
  status?: string;
}

export interface SystemStatusInfo {
  status?: string;
  backend?: string;
  backend_status?: string;
  model?: string;
  model_provider?: string;
  ollama_connected?: boolean | string;
  model_available?: boolean;
  error_message?: string;
  cpuUsage?: number;
  gpuUsage?: number;
  gpuName?: string;
  ramUsageGb?: number;
  ramTotalGb?: number;
  storagePath?: string;
  storageUsageGb?: number;
  storageTotalGb?: number;
  modelName?: string;
  provider?: string;
  ollamaPort?: number;
  connectionMode?: string;
  activeProcesses?: number;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant' | 'saarthi' | string;
  content?: string;
  text?: string;
  timestamp: string;
  toolExecution?: any;
  memoryRequest?: any;
  modelUsed?: string;
  executionTimeMs?: number;
  thinkingSteps?: any[];
  citations?: any[];
}

export interface ToolExecution {
  id: string;
  tool_name?: string;
  name?: string;
  command?: string;
  status: 'queued' | 'running' | 'success' | 'failed' | 'approval_required' | string;
  arguments?: any;
  output?: string;
  timestamp?: string;
  resultSummary?: string;
  techDetails?: any;
}

export interface PermissionRequest {
  id: string;
  tool_name?: string;
  description?: string;
  created_at?: string;
  riskLevel?: 'high' | 'medium' | 'low' | string;
  command?: string;
  purpose?: string;
  affectedResources?: string[];
}
