export const getApiBase = (): string => {
  const envBase = (import.meta as any).env?.VITE_API_BASE_URL;
  if (envBase && typeof envBase === 'string' && envBase.trim() !== '') {
    return `${envBase.replace(/\/+$/, '')}/api`;
  }
  if (typeof window !== 'undefined' && window.location?.origin && !window.location.origin.startsWith('file:')) {
    return `${window.location.origin}/api`;
  }
  return 'http://127.0.0.1:8000/api';
};

export const API_BASE = getApiBase();

export interface StatusResponse {
  backend: string;
  backend_status: string;
  model_provider: string;
  model_name: string;
  model: string;
  ollama_connected: boolean | "not_applicable";
  Ollama: string;
  model_available: boolean;
  configured?: boolean;
  reachable?: boolean;
  is_live?: boolean;
  execution_mode?: string;
  last_error_category?: string | null;
  error_message: string | null;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  status: string;
  permission_request?: any;
  memory_request?: any;
}

export const api = {
  async getStatus(): Promise<StatusResponse> {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },

  async getOllamaDiagnostics(): Promise<any> {
    const res = await fetch(`${API_BASE}/ollama/diagnostics`);
    return res.json();
  },

  async listTools(): Promise<any> {
    const res = await fetch(`${API_BASE}/tools`);
    return res.json();
  },

  async getHistory(sessionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/history/${sessionId}`);
    return res.json();
  },

  async clearHistory(sessionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/history/${sessionId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await res.json();
    if (data && typeof data.response === "string" && data.response.trim().startsWith("{")) {
      try {
        const parsed = JSON.parse(data.response.trim());
        if (parsed && parsed.type === "text" && typeof parsed.content === "string") {
          data.response = parsed.content;
        } else if (parsed && typeof parsed.content === "string") {
          data.response = parsed.content;
        }
      } catch {}
    }
    return data;
  },

  async getPendingPermissions(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/permissions/pending`);
    return res.json();
  },

  async approvePermission(requestId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/permissions/${requestId}/approve`, {
      method: "POST",
    });
    return res.json();
  },

  async denyPermission(requestId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/permissions/${requestId}/deny`, {
      method: "POST",
    });
    return res.json();
  },

  async listMemories(category?: string, projectId?: string): Promise<any> {
    let url = `${API_BASE}/memory`;
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (projectId) params.append("project_id", projectId);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url);
    return res.json();
  },

  async deleteMemory(memoryId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/memory/${memoryId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async approveMemory(requestId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/memory/approve/${requestId}`, {
      method: "POST",
    });
    return res.json();
  },

  async denyMemory(requestId: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/memory/deny/${requestId}`, {
      method: "POST",
    });
    return res.json();
  },

  async getSessions(): Promise<any> {
    const res = await fetch(`${API_BASE}/sessions`);
    return res.json();
  },

  async listFiles(path?: string, recursive?: boolean): Promise<any> {
    let url = `${API_BASE}/files`;
    const params = new URLSearchParams();
    if (path) params.append("path", path);
    if (recursive) params.append("recursive", "true");
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url);
    return res.json();
  },

  async getBenchmark(): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/nemotron/benchmark`);
      return await res.json();
    } catch {
      return { is_benchmarked: false, measured_tps: null, label: "Not benchmarked" };
    }
  },

  async runBenchmark(): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/benchmark`, { method: "POST" });
    return await res.json();
  },

  // Profile & Authentication
  async getProfile(): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/profile`);
      return await res.json();
    } catch {
      return { full_name: '', authenticated: false };
    }
  },

  async updateProfile(profileData: any): Promise<any> {
    const res = await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profileData),
    });
    return res.json();
  },

  async clearProfile(): Promise<any> {
    const res = await fetch(`${API_BASE}/profile`, {
      method: "DELETE",
    });
    return res.json();
  },

  async getAuthSession(): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/auth/session`);
      return await res.json();
    } catch {
      return { authenticated: false, user: null };
    }
  },

  // Licensing

  async getLicenseStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/license/status`);
    return res.json();
  },

  async activateLicense(licenseKey: string): Promise<any> {
    const res = await fetch(`${API_BASE}/license/activate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ license_key: licenseKey }),
    });
    return res.json();
  },

  // Career Workspace
  async listJobApplications(status?: string): Promise<any> {
    let url = `${API_BASE}/career/applications`;
    if (status) url += `?status=${encodeURIComponent(status)}`;
    const res = await fetch(url);
    return res.json();
  },

  async getJobApplicationStats(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/stats`);
    return res.json();
  },

  async createJobApplication(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async updateJobApplication(appId: number, updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async deleteJobApplication(appId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async uploadResumeFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/career/resume/upload`, {
      method: "POST",
      body: formData,
    });
    return res.json();
  },

  async importResume(title: string, rawContent: string, sections?: any[]): Promise<any> {
    const res = await fetch(`${API_BASE}/career/resume/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, raw_content: rawContent, sections }),
    });
    return res.json();
  },

  async listResumes(): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/career/resumes`);
      return await res.json();
    } catch {
      return { resumes: [] };
    }
  },

  async getResume(resumeId: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/resumes/${resumeId}`);
    return res.json();
  },

  async updateResume(resumeId: string | number, updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/resumes/${resumeId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async deleteResume(resumeId: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/resumes/${resumeId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async createResumeVersion(resumeId: string | number, versionTag: string, sections: any[]): Promise<any> {
    const res = await fetch(`${API_BASE}/career/resumes/${resumeId}/versions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version_tag: versionTag, sections }),
    });
    return res.json();
  },

  // Phase 3 JD Tailoring & Requirement Analysis
  async analyzeJD(jdText: string, company: string = "Target Company", role: string = "Target Role", resumeId?: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/jd/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: jdText, company, role, resume_id: resumeId }),
    });
    return res.json();
  },

  async generateJDTailorDiffs(jdText: string, company: string, role: string, resumeId?: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/jd/tailor-diffs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: jdText, company, role, resume_id: resumeId }),
    });
    return res.json();
  },

  async applyTailoredVersion(resumeId: string | number, versionTag: string, company: string, role: string, acceptedDiffs: any[]): Promise<any> {
    const res = await fetch(`${API_BASE}/career/jd/apply-tailored-version`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_id: Number(resumeId), version_tag: versionTag, company, role, accepted_diffs: acceptedDiffs }),
    });
    return res.json();
  },

  // Phase 4 Complete Career Workspace
  async listApplications(status?: string): Promise<any> {
    try {
      const url = status ? `${API_BASE}/career/applications?status=${encodeURIComponent(status)}` : `${API_BASE}/career/applications`;
      const res = await fetch(url);
      return await res.json();
    } catch {
      return { applications: [] };
    }
  },

  async getApplication(appId: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}`);
    return res.json();
  },

  async createApplication(appData: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(appData),
    });
    return res.json();
  },

  async updateApplication(appId: string | number, updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async deleteApplication(appId: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async moveApplicationStage(appId: string | number, stage: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}/move`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stage }),
    });
    return res.json();
  },

  async getApplicationDossier(appId: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/applications/${appId}/dossier`);
    return res.json();
  },

  async generateInterviewPrep(jdText: string, company?: string, role?: string, resumeId?: string | number, appId?: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/interview/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: jdText, company, role, resume_id: resumeId, application_id: appId }),
    });
    return res.json();
  },

  async listInterviewQuestions(appId?: string | number): Promise<any> {
    const url = appId ? `${API_BASE}/career/interview/questions?application_id=${appId}` : `${API_BASE}/career/interview/questions`;
    const res = await fetch(url);
    return res.json();
  },

  async saveStarAnswer(qId: number, situation: string, task: string, action: string, result: string, score: number = 80): Promise<any> {
    const res = await fetch(`${API_BASE}/career/interview/questions/${qId}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: qId, situation, task, action, result, score }),
    });
    return res.json();
  },

  async scoreStarAnswer(qId: number, question: string, situation: string, task: string, action: string, result: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/interview/answers/${qId}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: qId, question, situation, task, action, result }),
    });
    return res.json();
  },

  async analyzeSalaryOffer(offerData: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/salary/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(offerData),
    });
    return res.json();
  },

  async listSalaryOffers(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/salary/offers`);
    return res.json();
  },

  async listCareerGoals(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/goals`);
    return res.json();
  },

  async createCareerGoal(goalData: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/goals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(goalData),
    });
    return res.json();
  },

  async updateCareerGoal(goalId: number, updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/career/goals/${goalId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async deleteCareerGoal(goalId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/career/goals/${goalId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async getCareerTrajectory(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/trajectory`);
    return res.json();
  },

  async getCareerDashboard(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/dashboard`);
    return res.json();
  },

  async analyzeMatch(resumeText: string, jobDescription: string, company?: string, role?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/analyze-match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription, company, role }),
    });
    return res.json();
  },

  async tailorResume(resumeText: string, jobDescription: string, targetRole: string, company: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/tailor-resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription, target_role: targetRole, company }),
    });
    return res.json();
  },

  async generateCoverLetter(resumeText: string, jobDescription: string, company: string, role: string, hiringManager?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/cover-letter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription, company, role, hiring_manager: hiringManager }),
    });
    return res.json();
  },

  async draftEmail(emailType: string, recipientName: string, company: string, role: string, contextNotes?: string, confirmed: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/career/email/draft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_type: emailType, recipient_name: recipientName, company, role, context_notes: contextNotes, confirmed_by_user: confirmed }),
    });
    return res.json();
  },

  async createCalendarEvent(eventType: string, company: string, role: string, eventTime: string, notes?: string, confirmed: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/career/calendar/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: eventType, company, role, event_time: eventTime, notes, confirmed_by_user: confirmed }),
    });
    return res.json();
  },

  async getInterviewPrep(resumeText: string, jobDescription: string, company: string, role: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/interview-prep`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription, company, role }),
    });
    return res.json();
  },

  async verifyStudent(email: string, institution?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/career/verify-student`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, institution }),
    });
    return res.json();
  },

  // Vendor Admin
  async listVendorCustomers(): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/customers`, {
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  async createVendorCustomer(name: string, email: string): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/customers`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ name, email }),
    });
    return res.json();
  },

  async createVendorLicense(customerId: string, plan: string, durationDays: number = 30, maxDevices: number = 2): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ customer_id: customerId, plan, duration_days: durationDays, max_devices: maxDevices }),
    });
    return res.json();
  },

  async suspendVendorLicense(licenseId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses/${licenseId}/suspend`, {
      method: "POST",
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  async restoreVendorLicense(licenseId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses/${licenseId}/restore`, {
      method: "POST",
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  async revokeVendorLicense(licenseId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses/${licenseId}/revoke`, {
      method: "POST",
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  async renewVendorLicense(licenseId: string, extensionDays: number = 30): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses/${licenseId}/renew`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ extension_days: extensionDays }),
    });
    return res.json();
  },

  async changeVendorEntitlement(licenseId: string, newPlan: string): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/licenses/${licenseId}/entitlement`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ new_plan: newPlan }),
    });
    return res.json();
  },

  async getVendorAuditLogs(): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/audit-logs`, {
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  async getVendorAnalytics(): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/analytics`, {
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  // Document Export & Watermarking
  async exportDocument(documentType: string, content: string, format: string = "markdown"): Promise<any> {
    const res = await fetch(`${API_BASE}/career/export-document`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_type: documentType, content, format }),
    });
    return res.json();
  },

  // Referrals
  async getReferrals(userId: string = "default_user"): Promise<any> {
    const res = await fetch(`${API_BASE}/referrals?user_id=${encodeURIComponent(userId)}`);
    return res.json();
  },

  async redeemReferral(code: string, userId: string = "default_user"): Promise<any> {
    const res = await fetch(`${API_BASE}/referrals/redeem`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, user_id: userId }),
    });
    return res.json();
  },

  // Operational Telemetry
  async logTelemetryEvent(eventType: string, details?: any): Promise<any> {
    const res = await fetch(`${API_BASE}/telemetry/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: eventType, details }),
    });
    return res.json();
  },

  async getMonetizationMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/vendor/monetization-metrics`, {
      headers: this.getAdminHeaders()
    });
    return res.json();
  },

  // Saarthi Nemotron Hardware & Model Lifecycle
  async getNemotronHardware(): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/nemotron/hardware`);
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  },

  async getHardware(): Promise<any> {
    return this.getNemotronHardware();
  },

  async getNemotronCatalog(): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/models`);
    return res.json();
  },

  async getNemotronRecommendation(): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/recommendation`);
    return res.json();
  },

  async getAiLifecycleStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/status`);
    return res.json();
  },

  async triggerOllamaInstall(): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/ollama/install`, { method: "POST" });
    return res.json();
  },

  async installNemotronModel(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/install-model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    return res.json();
  },

  async switchNemotronModel(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/switch-model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    return res.json();
  },

  async removeNemotronModel(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/model/remove`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    return res.json();
  },

  async runNemotronHealthCheck(modelId?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/verify-model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    return res.json();
  },

  async getNemotronDownloadStatus(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/download-status/${encodeURIComponent(modelId)}`);
    return res.json();
  },

  async cancelNemotronDownload(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/cancel-download/${encodeURIComponent(modelId)}`, {
      method: "POST",
    });
    return res.json();
  },

  async deleteNemotronModel(modelId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/models/${encodeURIComponent(modelId)}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async runNemotronSmokeTest(modelId?: string, prompt?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/nemotron/smoke-test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, prompt: prompt }),
    });
    return res.json();
  },

  // Auth & Account API
  async register(email: string, password: string, fullName: string = ""): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    return res.json();
  },

  async login(email: string, password: string): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    return res.json();
  },

  async getMe(token: string): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.json();
  },

  // Payments API
  async getPaymentPlans(): Promise<any> {
    const res = await fetch(`${API_BASE}/payment/plans`);
    return res.json();
  },

  async createCheckoutSession(planName: string, provider: string, token: string): Promise<any> {
    const res = await fetch(`${API_BASE}/payment/checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ plan_name: planName, provider }),
    });
    return res.json();
  },

  async verifyPayment(orderId: string, paymentId: string, signature: string, provider: string, token: string): Promise<any> {
    const res = await fetch(`${API_BASE}/payment/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ order_id: orderId, payment_id: paymentId, signature, provider }),
    });
    return res.json();
  },

  // Voice APIs (Phase 5H)
  async getVoiceProfile(): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/profile`);
    return res.json();
  },

  async startVoiceSession(handsFree: boolean = false, pushToTalk: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/session/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hands_free: handsFree, push_to_talk: pushToTalk }),
    });
    return res.json();
  },

  async stopVoiceSession(sessionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/session/stop?session_id=${sessionId}`, {
      method: "POST",
    });
    return res.json();
  },

  async processVoiceTurn(sessionId: string, textOverride?: string, languageHint: string = "en-IN", permissionGranted: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/session/turn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        text_override: textOverride,
        language_hint: languageHint,
        permission_granted: permissionGranted
      }),
    });
    return res.json();
  },

  async interruptVoiceSession(sessionId: string, cancelAgentTask: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/session/interrupt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, cancel_agent_task: cancelAgentTask }),
    });
    return res.json();
  },

  async toggleHandsFree(sessionId: string, enable: boolean): Promise<any> {
    const endpoint = enable ? `${API_BASE}/voice/session/hands-free/start?session_id=${sessionId}` : `${API_BASE}/voice/session/hands-free/stop?session_id=${sessionId}`;
    const res = await fetch(endpoint, { method: "POST" });
    return res.json();
  },

  async getVoiceHistory(sessionId?: string): Promise<any> {
    const url = sessionId ? `${API_BASE}/voice/history?session_id=${sessionId}` : `${API_BASE}/voice/history`;
    const res = await fetch(url);
    return res.json();
  },

  async getVoicePrivacy(): Promise<any> {
    const res = await fetch(`${API_BASE}/voice/privacy`);
    return res.json();
  },

  // Personalization APIs (Phase 5I)
  async getPersonalizationProfile(): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/profile`);
    return res.json();
  },

  async updatePersonalizationProfile(updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/profile`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async setExplicitPreference(key: string, value: any, category: string = "general"): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/preference/explicit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, value, category }),
    });
    return res.json();
  },

  async getLearnedPreferences(): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/learned`);
    return res.json();
  },

  async confirmPreference(key: string): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key }),
    });
    return res.json();
  },

  async rejectPreference(key: string): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key }),
    });
    return res.json();
  },

  async forgetPreference(key: string): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/preference?key=${key}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async resetPersonalization(category?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category }),
    });
    return res.json();
  },

  async explainPersonalization(domain: string = "general", projectId?: string): Promise<any> {
    const url = projectId ? `${API_BASE}/personalization/explain?domain=${domain}&project_id=${projectId}` : `${API_BASE}/personalization/explain?domain=${domain}`;
    const res = await fetch(url);
    return res.json();
  },

  async getDomainExpertise(): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/expertise`);
    return res.json();
  },

  async setDomainExpertise(domain: string, level: string): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/expertise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain, level }),
    });
    return res.json();
  },

  async updatePersonalizationSettings(settings: any): Promise<any> {
    const res = await fetch(`${API_BASE}/personalization/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    return res.json();
  },

  // Routines & Automation APIs (Phase 5J)
  async getRoutines(scope?: string, projectId?: string): Promise<any> {
    let url = `${API_BASE}/routines`;
    const params = [];
    if (scope) params.push(`scope=${scope}`);
    if (projectId) params.push(`project_id=${projectId}`);
    if (params.length > 0) url += `?${params.join("&")}`;
    const res = await fetch(url);
    return res.json();
  },

  async createRoutine(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/routines`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async parseRoutinePrompt(prompt: string, domain?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, domain }),
    });
    return res.json();
  },

  async getRoutineTemplates(): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/templates`);
    return res.json();
  },

  async getUpcomingRoutines(): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/upcoming`);
    return res.json();
  },

  async getRoutineNotifications(): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/notifications`);
    return res.json();
  },

  async getRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}`);
    return res.json();
  },

  async updateRoutine(routineId: string, updates: any): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async deleteRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}`, {
      method: "DELETE",
    });
    return res.json();
  },

  async activateRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}/activate`, {
      method: "POST",
    });
    return res.json();
  },

  async pauseRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}/pause`, {
      method: "POST",
    });
    return res.json();
  },

  async resumeRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}/resume`, {
      method: "POST",
    });
    return res.json();
  },

  async runRoutine(routineId: string, permissionGranted: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permission_granted: permissionGranted }),
    });
    return res.json();
  },

  async getRoutineExecutions(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/routines/${routineId}/executions`);
    return res.json();
  },

  // Cross-Domain Autonomy APIs
  async startCrossDomainWorkflow(objective: string, domain: string = "general"): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objective, domain }),
    });
    return res.json();
  },

  async getCrossDomainWorkflow(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/${taskId}`);
    return res.json();
  },

  async approveWorkflowStep(taskId: string, stepId?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/${taskId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ step_id: stepId }),
    });
    return res.json();
  },

  async cancelWorkflow(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/${taskId}/cancel`, { method: "POST" });
    return res.json();
  },

  async resumeWorkflow(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/${taskId}/resume`, { method: "POST" });
    return res.json();
  },

  async replanWorkflow(taskId: string, failedStepId?: string, errorMsg?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/workflow/${taskId}/replan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ failed_step_id: failedStepId, error_message: errorMsg }),
    });
    return res.json();
  },

  async getDomainTransitions(): Promise<any> {
    const res = await fetch(`${API_BASE}/cross-domain/transitions`);
    return res.json();
  },

  // Unified Saarthi Integration APIs
  async getCommandCenterPayload(): Promise<any> {
    const res = await fetch(`${API_BASE}/unified/command-center`);
    return res.json();
  },

  async sendUnifiedChat(message: string, sessionId: string = "default_session", permissionGranted: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/unified/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId, permission_granted: permissionGranted }),
    });
    return res.json();
  },

  async rememberFact(content: string, domain: string = "general"): Promise<any> {
    const res = await fetch(`${API_BASE}/unified/memory/remember`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, domain }),
    });
    return res.json();
  },

  async forgetFact(query: string): Promise<any> {
    const res = await fetch(`${API_BASE}/unified/memory/forget`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    return res.json();
  },

  // Admin Control Panel APIs
  getAdminHeaders(): Record<string, string> {
    const token = localStorage.getItem("saarthi_admin_token") || "";
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  },

  async adminLogin(loginData: { email?: string; password?: string; admin_key?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginData),
    });
    return res.json();
  },

  async getAdminDashboard(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/dashboard`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminUsers(query?: string, role?: string, plan?: string): Promise<any> {
    let url = `${API_BASE}/admin/users`;
    const params = new URLSearchParams();
    if (query) params.append("query", query);
    if (role) params.append("role", role);
    if (plan) params.append("plan", plan);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminUserDetails(userId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/users/${userId}/details`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async updateAdminUserRole(userId: string, role: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/users/update-role`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ user_id: userId, role }),
    });
    return res.json();
  },

  async updateAdminUserPlan(userId: string, plan: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/update-plan`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ user_id: userId, plan }),
    });
    return res.json();
  },

  async suspendAdminUser(userId: string, reason?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/users/suspend`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ user_id: userId, reason }),
    });
    return res.json();
  },

  async restoreAdminUser(userId: string, reason?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/users/restore`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ user_id: userId, reason }),
    });
    return res.json();
  },

  async deleteAdminUser(userId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/users/${userId}`, {
      method: "DELETE",
      headers: this.getAdminHeaders(),
    });
    return res.json();
  },

  async getAdminEntitlements(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/entitlements`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminQuotas(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/quotas`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async resetAdminQuota(userIdOrDevice: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/quotas/reset`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ user_id_or_device: userIdOrDevice }),
    });
    return res.json();
  },

  async getAdminAIConfig(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/ai/config`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async updateAdminAIConfig(config: any): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/ai/config`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify(config),
    });
    return res.json();
  },

  async getAdminDomains(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/domains`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminTools(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/tools`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async updateAdminToolPolicy(policy: any): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/tools/policy`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify(policy),
    });
    return res.json();
  },

  async getAdminAgentTasks(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/agent/tasks`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async cancelAdminAgentTask(taskId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/agent/tasks/${taskId}/cancel`, {
      method: "POST",
      headers: this.getAdminHeaders(),
    });
    return res.json();
  },

  async getAdminRoutines(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/routines`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async toggleAdminRoutine(routineId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/routines/${routineId}/toggle`, {
      method: "POST",
      headers: this.getAdminHeaders(),
    });
    return res.json();
  },

  async getAdminPendingPermissions(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/permissions/pending`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async actionAdminPermission(reqId: string, action: string = "approve"): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/permissions/${reqId}/action?action=${action}`, {
      method: "POST",
      headers: this.getAdminHeaders(),
    });
    return res.json();
  },

  async getAdminAuditLogs(limit: number = 100): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/audit-logs?limit=${limit}`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminTrustEvents(limit: number = 100): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/trust-events?limit=${limit}`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminDiagnostics(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/diagnostics`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async runAdminDbCheck(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/diagnostics/db-check`, {
      method: "POST",
      headers: this.getAdminHeaders(),
    });
    return res.json();
  },

  async getAdminFeatureFlags(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/feature-flags`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async updateAdminFeatureFlag(key: string, enabled: boolean, rolloutPercentage: number): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/feature-flags/update`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ key, enabled, rollout_percentage: rolloutPercentage }),
    });
    return res.json();
  },

  async getAdminMaintenanceMode(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/maintenance`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async toggleAdminMaintenanceMode(enabled: boolean, message?: string, bypassWhitelist?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/maintenance/toggle`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ enabled, message, bypass_whitelist: bypassWhitelist }),
    });
    return res.json();
  },

  async getAdminFeedback(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/feedback`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getAdminOrganizations(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/organizations`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async createAdminOrganization(name: string, plan: string = "TEAMS", maxSeats: number = 10): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/organizations`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ name, plan, max_seats: maxSeats }),
    });
    return res.json();
  },

  async getAdminIpBans(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/security/bans`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async addAdminIpBan(identifier: string, banType: string = "IP", reason: string = ""): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/security/ban`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ identifier, ban_type: banType, reason }),
    });
    return res.json();
  },

  async removeAdminIpBan(identifier: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/security/unban`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify({ identifier }),
    });
    return res.json();
  },

  async getAdminVersion(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/version`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async globalSearch(q: string): Promise<any> {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`);
    return res.json();
  },

  async generateFlashcards(content: string, count: number = 5, topic?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/study/flashcards/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, count, topic })
    });
    return res.json();
  },

  async createQuiz(content: string, difficulty: string = "medium", numQuestions: number = 5): Promise<any> {
    const res = await fetch(`${API_BASE}/study/quiz/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, difficulty, num_questions: numQuestions })
    });
    return res.json();
  },

  async ingestSyllabus(syllabusText: string, courseName: string, targetExamDate?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/study/syllabus/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ syllabus_text: syllabusText, course_name: courseName, target_exam_date: targetExamDate })
    });
    return res.json();
  },

  // --- SAARTHI OPS READ-ONLY MONITORING & DIAGNOSTICS ---
  async getOpsHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/health`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getOpsMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/metrics`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getOpsServices(): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/services`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getOpsContainers(): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/containers`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getOpsErrors(limit: number = 25): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/errors?limit=${limit}`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async getOpsIncidents(): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/incidents`, { headers: this.getAdminHeaders() });
    return res.json();
  },

  async triggerOpsDiagnosis(data?: any): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/diagnose`, {
      method: "POST",
      headers: this.getAdminHeaders(),
      body: JSON.stringify(data || {})
    });
    return res.json();
  },

  async getOpsAudit(limit: number = 25): Promise<any> {
    const res = await fetch(`${API_BASE}/ops/audit?limit=${limit}`, { headers: this.getAdminHeaders() });
    return res.json();
  }
};



