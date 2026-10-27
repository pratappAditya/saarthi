import React, { useState, useEffect } from "react";
import {
  Briefcase,
  FileText,
  Search,
  Plus,
  TrendingUp,
  Award,
  Calendar,
  Mail,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  ExternalLink,
  Trash2,
  Edit3,
  BookOpen,
  UserCheck,
  ShieldCheck,
  Building,
  MapPin,
  DollarSign,
  Send,
  Clock
} from "lucide-react";
import { api } from "../../api";
import type { JobApplication, ApplicationStatus } from "../../types";

export function CareerScreen() {
  const [activeTab, setActiveTab] = useState<"tracker" | "ats" | "cover_letter" | "outreach" | "interview" | "verify" | "referral">("tracker");
  
  // Referral State
  const [referralData, setReferralData] = useState<any>(null);
  const [referralInput, setReferralInput] = useState<string>("");
  const [referralRedeemMsg, setReferralRedeemMsg] = useState<string | null>(null);

  const fetchReferrals = async () => {
    try {
      const data = await api.getReferrals();
      setReferralData(data);
    } catch (err) {
      console.error("Failed to load referrals", err);
    }
  };

  useEffect(() => {
    fetchReferrals();
  }, []);

  const handleRedeemReferral = async (e: React.FormEvent) => {
    e.preventDefault();
    setReferralRedeemMsg(null);
    try {
      const res = await api.redeemReferral(referralInput.trim());
      setReferralRedeemMsg(res.message || "Referral redeemed successfully!");
      fetchReferrals();
    } catch (err: any) {
      setReferralRedeemMsg(err.message || "Failed to redeem referral code.");
    }
  };
  
  // Job Applications State
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<any>({ total_applications: 0, interviews: 0, offers: 0, response_rate: "0%", upcoming_followups: 0 });
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // New Application Modal
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [newCompany, setNewCompany] = useState<string>("");
  const [newRole, setNewRole] = useState<string>("");
  const [newJobUrl, setNewJobUrl] = useState<string>("");
  const [newLocation, setNewLocation] = useState<string>("");
  const [newSalary, setNewSalary] = useState<string>("");
  const [newStatus, setNewStatus] = useState<ApplicationStatus>("SAVED");
  const [newNextAction, setNewNextAction] = useState<string>("");
  const [newFollowUpDate, setNewFollowUpDate] = useState<string>("");

  // Resume & ATS State
  const [resumeText, setResumeText] = useState<string>(`JOHN DOE
Email: john.doe@university.ac.in | Phone: +91 98765 43210
Education: B.Tech Computer Science (2023 - 2026), GPA 8.8/10

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, C++, SQL
- Frameworks: React, FastAPI, Node.js, HTML/CSS, Git
- Tools: VS Code, Docker, Linux, SQLite

PROJECTS
1. Saarthi Personal AI Assistant (Python, FastAPI, React)
   - Built a local-first AI workstation application running offline models.
   - Designed SQLite database schema and REST API endpoints for career tracking.

2. Student Career Portal (TypeScript, React, Node)
   - Created a web dashboard for resume parsing and ATS analysis.`);
   
  const [jobDescription, setJobDescription] = useState<string>(`Full Stack Developer Intern / Junior Engineer
Company: TechCorp India
Location: Bengaluru / Remote

Responsibilities:
- Develop modern web user interfaces using React and TypeScript.
- Build robust backend REST APIs using Python and FastAPI or Node.js.
- Work with SQL databases (SQLite, PostgreSQL) and optimize query performance.
- Collaborate with team on Git workflows and unit testing.`);
  
  const [targetCompany, setTargetCompany] = useState<string>("TechCorp India");
  const [targetRole, setTargetRole] = useState<string>("Full Stack Developer");

  const [atsResult, setAtsResult] = useState<any>(null);
  const [tailoredResume, setTailoredResume] = useState<string>("");
  const [coverLetter, setCoverLetter] = useState<string>("");

  // Outreach & Email State
  const [emailType, setEmailType] = useState<string>("recruiter_follow_up");
  const [emailRecipient, setEmailRecipient] = useState<string>("Hiring Manager");
  const [emailDraftResult, setEmailDraftResult] = useState<any>(null);
  const [emailConfirmed, setEmailConfirmed] = useState<boolean>(false);

  // Calendar Event State
  const [eventType, setEventType] = useState<string>("interview");
  const [eventTime, setEventTime] = useState<string>(new Date(Date.now() + 86400000 * 2).toISOString().slice(0, 16));
  const [calendarResult, setCalendarResult] = useState<any>(null);
  const [calendarConfirmed, setCalendarConfirmed] = useState<boolean>(false);

  // Interview Prep State
  const [interviewPrep, setInterviewPrep] = useState<any>(null);

  // Student Verification State
  const [studentEmail, setStudentEmail] = useState<string>("student@university.ac.in");
  const [verificationResult, setVerificationResult] = useState<any>(null);

  // Fetch applications & stats
  const fetchCareerData = async () => {
    setLoading(true);
    try {
      const appsRes = await api.listJobApplications(filterStatus === "ALL" ? undefined : filterStatus);
      if (appsRes.applications) setApplications(appsRes.applications);
      const statsRes = await api.getJobApplicationStats();
      if (statsRes) setStats(statsRes);
    } catch (err: any) {
      console.error("Failed to load career data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCareerData();
  }, [filterStatus]);

  // Handlers
  const handleCreateApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    try {
      const res = await api.createJobApplication({
        company: newCompany,
        role: newRole,
        job_url: newJobUrl,
        location: newLocation,
        salary: newSalary,
        status: newStatus,
        next_action: newNextAction,
        follow_up_date: newFollowUpDate
      });
      if (res.detail) {
        setErrorMessage(res.detail);
      } else {
        setShowAddModal(false);
        setNewCompany("");
        setNewRole("");
        fetchCareerData();
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to create application");
    }
  };

  const handleDeleteApplication = async (id: number) => {
    if (window.confirm("Are you sure you want to delete this job application?")) {
      await api.deleteJobApplication(id);
      fetchCareerData();
    }
  };

  const handleUpdateStatus = async (id: number, status: ApplicationStatus) => {
    await api.updateJobApplication(id, { status });
    fetchCareerData();
  };

  const handleRunAtsAnalysis = async () => {
    setLoading(true);
    try {
      const match = await api.analyzeMatch(resumeText, jobDescription, targetCompany, targetRole);
      setAtsResult(match);
      const tailored = await api.tailorResume(resumeText, jobDescription, targetRole, targetCompany);
      setTailoredResume(tailored.tailored_resume_markdown);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCoverLetter = async () => {
    setLoading(true);
    try {
      const res = await api.generateCoverLetter(resumeText, jobDescription, targetCompany, targetRole);
      setCoverLetter(res.cover_letter);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDraftEmail = async (confirmed: boolean = false) => {
    try {
      const res = await api.draftEmail(emailType, emailRecipient, targetCompany, targetRole, "Interested in learning more about team roadmap.", confirmed);
      setEmailDraftResult(res);
      setEmailConfirmed(confirmed);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateCalendarEvent = async (confirmed: boolean = false) => {
    try {
      const res = await api.createCalendarEvent(eventType, targetCompany, targetRole, eventTime, "Prepared technical interview topics.", confirmed);
      setCalendarResult(res);
      setCalendarConfirmed(confirmed);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFetchInterviewPrep = async () => {
    setLoading(true);
    try {
      const res = await api.getInterviewPrep(resumeText, jobDescription, targetCompany, targetRole);
      setInterviewPrep(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyStudent = async () => {
    try {
      const res = await api.verifyStudent(studentEmail);
      setVerificationResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const statusColors: Record<string, string> = {
    SAVED: "bg-slate-700 text-slate-300 border-slate-600",
    APPLIED: "bg-blue-900/40 text-blue-300 border-blue-700",
    SCREENING: "bg-cyan-900/40 text-cyan-300 border-cyan-700",
    INTERVIEW: "bg-purple-900/40 text-purple-300 border-purple-700",
    OFFER: "bg-emerald-900/40 text-emerald-300 border-emerald-700",
    REJECTED: "bg-rose-900/40 text-rose-300 border-rose-700",
    WITHDRAWN: "bg-zinc-800 text-zinc-400 border-zinc-700"
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 text-slate-100 overflow-y-auto p-6 space-y-6">
      
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400">
              <Briefcase className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-slate-100 via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                Career & Job Search Workspace
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Local-first AI career accelerator for students & job seekers. 100% private.
              </p>
            </div>
          </div>
        </div>

        {/* PRIMARY SUB-TABS */}
        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab("tracker")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "tracker" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Job Tracker</span>
          </button>
          <button
            onClick={() => setActiveTab("ats")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "ats" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Resume & ATS Match</span>
          </button>
          <button
            onClick={() => setActiveTab("cover_letter")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "cover_letter" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cover Letter</span>
          </button>
          <button
            onClick={() => setActiveTab("outreach")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "outreach" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Email & Calendar</span>
          </button>
          <button
            onClick={() => setActiveTab("interview")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "interview" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Interview Prep</span>
          </button>
          <button
            onClick={() => setActiveTab("verify")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "verify" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Student Status</span>
          </button>
          <button
            onClick={() => setActiveTab("referral")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 ${
              activeTab === "referral" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Invite a Friend</span>
          </button>
        </div>
      </div>

      {/* SUB-TAB 1: JOB TRACKER DASHBOARD */}
      {activeTab === "tracker" && (
        <div className="space-y-6">
          {/* STATS METRICS GRID */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Applications</span>
                <Briefcase className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-slate-100">{stats.total_applications || 0}</div>
              <div className="text-[10px] text-slate-500 mt-1">Saved or submitted</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Interviews</span>
                <Calendar className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-purple-300">{stats.interviews || 0}</div>
              <div className="text-[10px] text-slate-500 mt-1">Scheduled / Active</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Offers</span>
                <Award className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-300">{stats.offers || 0}</div>
              <div className="text-[10px] text-slate-500 mt-1">Received</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Response Rate</span>
                <TrendingUp className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-blue-300">{stats.response_rate || "0%"}</div>
              <div className="text-[10px] text-slate-500 mt-1">Interview conversions</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Follow-ups</span>
                <Clock className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-amber-300">{stats.upcoming_followups || 0}</div>
              <div className="text-[10px] text-slate-500 mt-1">Upcoming actions</div>
            </div>
          </div>

          {/* ACTION BAR & SEARCH */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-3 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search by company or role..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Statuses</option>
                <option value="SAVED">Saved</option>
                <option value="APPLIED">Applied</option>
                <option value="SCREENING">Screening</option>
                <option value="INTERVIEW">Interview</option>
                <option value="OFFER">Offer</option>
                <option value="REJECTED">Rejected</option>
                <option value="WITHDRAWN">Withdrawn</option>
              </select>
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium px-4 py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/10"
            >
              <Plus className="w-4 h-4" />
              <span>Track New Application</span>
            </button>
          </div>

          {/* ERROR ALERT */}
          {errorMessage && (
            <div className="bg-rose-950/40 border border-rose-700/60 p-3 rounded-lg text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* APPLICATIONS LIST */}
          <div className="space-y-3">
            {applications.length === 0 ? (
              <div className="text-center py-12 bg-slate-900/30 border border-dashed border-slate-800 rounded-xl">
                <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                <h3 className="text-sm font-semibold text-slate-300">No Job Applications Tracked</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                  Click "Track New Application" to add target roles and manage your job search progress locally.
                </p>
              </div>
            ) : (
              applications
                .filter(app => 
                  app.company.toLowerCase().includes(searchTerm.toLowerCase()) || 
                  app.role.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((app) => (
                  <div
                    key={app.id}
                    className="bg-slate-900/50 border border-slate-800 hover:border-slate-700 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-slate-100 text-sm">{app.role}</span>
                        <span className="text-slate-400 text-xs">at</span>
                        <span className="font-medium text-cyan-400 text-xs flex items-center">
                          <Building className="w-3 h-3 mr-1" />
                          {app.company}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-3 text-[11px] text-slate-400">
                        {app.location && (
                          <span className="flex items-center text-slate-400">
                            <MapPin className="w-3 h-3 mr-1 text-slate-500" />
                            {app.location}
                          </span>
                        )}
                        {app.salary && (
                          <span className="flex items-center text-slate-400">
                            <DollarSign className="w-3 h-3 mr-0.5 text-emerald-500" />
                            {app.salary}
                          </span>
                        )}
                        <span>Applied: {app.date_applied}</span>
                        {app.follow_up_date && (
                          <span className="text-amber-400 font-medium">
                            Follow-up: {app.follow_up_date}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <select
                        value={app.status}
                        onChange={(e) => handleUpdateStatus(app.id, e.target.value as ApplicationStatus)}
                        className={`text-xs px-2.5 py-1 rounded-md border font-medium focus:outline-none ${
                          statusColors[app.status] || "bg-slate-800 text-slate-300 border-slate-700"
                        }`}
                      >
                        <option value="SAVED">SAVED</option>
                        <option value="APPLIED">APPLIED</option>
                        <option value="SCREENING">SCREENING</option>
                        <option value="INTERVIEW">INTERVIEW</option>
                        <option value="OFFER">OFFER</option>
                        <option value="REJECTED">REJECTED</option>
                        <option value="WITHDRAWN">WITHDRAWN</option>
                      </select>

                      <button
                        onClick={() => handleDeleteApplication(app.id)}
                        className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-950/20 transition-all"
                        title="Delete application"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
            )}
          </div>
        </div>
      )}

      {/* SUB-TAB 2: RESUME & ATS MATCH */}
      {activeTab === "ats" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* INPUT SECTION */}
          <div className="space-y-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Resume & Job Description</span>
            </h2>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Company</label>
                <input
                  type="text"
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Target Role</label>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Your Base Resume (USER FACT Baseline)</label>
              <textarea
                rows={6}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">Job Description (Target Role)</label>
              <textarea
                rows={6}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={handleRunAtsAnalysis}
              disabled={loading}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/10"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? "Analyzing ATS Match..." : "Run ATS Match Analysis"}</span>
            </button>
          </div>

          {/* OUTPUT & ATS SCORE SECTION */}
          <div className="space-y-4">
            {atsResult ? (
              <div className="space-y-4">
                <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="text-xs text-slate-400 font-medium">ATS Match Score</div>
                    <div className="text-3xl font-extrabold text-cyan-400">{atsResult.ats_score}%</div>
                    <div className="text-[11px] text-slate-500 mt-0.5">{atsResult.match_summary}</div>
                  </div>
                  <div className="w-16 h-16 rounded-full border-4 border-cyan-500/40 flex items-center justify-center text-cyan-300 font-bold text-lg">
                    {atsResult.ats_score}%
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl space-y-3">
                  <h3 className="text-xs font-bold text-slate-300">Matching Keywords Found</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {atsResult.matching_keywords.map((kw: string, i: number) => (
                      <span key={i} className="bg-emerald-950/60 border border-emerald-700/60 text-emerald-300 text-[11px] px-2 py-0.5 rounded-md">
                        ✓ {kw}
                      </span>
                    ))}
                  </div>

                  <h3 className="text-xs font-bold text-slate-300 pt-2">Missing Recommended Keywords</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {atsResult.missing_keywords.map((kw: string, i: number) => (
                      <span key={i} className="bg-amber-950/60 border border-amber-700/60 text-amber-300 text-[11px] px-2 py-0.5 rounded-md">
                        + {kw}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl space-y-2">
                  <h3 className="text-xs font-bold text-cyan-400 flex items-center">
                    <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                    USER-PROVIDED FACTS vs AI SUGGESTIONS
                  </h3>
                  <div className="text-[11px] text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                    <div className="font-semibold text-emerald-400 mb-1">User Facts Preserved:</div>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                      {atsResult.user_provided_facts.map((fact: string, idx: number) => (
                        <li key={idx}>{fact}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {tailoredResume && (
                  <div className="bg-slate-900/40 border border-slate-800 p-4 rounded-xl space-y-2">
                    <h3 className="text-xs font-bold text-slate-200">Tailored Resume Output</h3>
                    <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-[11px] text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-48">
                      {tailoredResume}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full border border-dashed border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
                <Sparkles className="w-8 h-8 text-slate-600" />
                <div className="text-xs font-medium text-slate-400">ATS Analysis Ready</div>
                <div className="text-[11px]">Fill in your resume and job description, then click "Run ATS Match Analysis" to view scores and missing keywords.</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SUB-TAB 3: COVER LETTER BUILDER */}
      {activeTab === "cover_letter" && (
        <div className="space-y-4 max-w-2xl mx-auto bg-slate-900/40 p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Tailored Cover Letter Generator</span>
          </h2>
          <p className="text-xs text-slate-400">
            Generates a professional, grounded cover letter for {targetCompany} - {targetRole}.
          </p>

          <button
            onClick={handleGenerateCoverLetter}
            disabled={loading}
            className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/10"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? "Generating Cover Letter..." : "Generate Tailored Cover Letter"}</span>
          </button>

          {coverLetter && (
            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Generated Cover Letter:</span>
                <button
                  onClick={() => navigator.clipboard.writeText(coverLetter)}
                  className="text-cyan-400 hover:underline text-[11px]"
                >
                  Copy to Clipboard
                </button>
              </div>
              <textarea
                rows={12}
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 4: EMAIL & CALENDAR HUB (WITH EXPLICIT CONFIRMATION) */}
      {activeTab === "outreach" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* EMAIL DRAFTING */}
          <div className="space-y-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Mail className="w-4 h-4 text-cyan-400" />
              <span>Professional Email Drafter</span>
            </h2>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Email Type</label>
                <select
                  value={emailType}
                  onChange={(e) => setEmailType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="recruiter_follow_up">Recruiter Follow-up</option>
                  <option value="interview_confirmation">Interview Confirmation</option>
                  <option value="thank_you">Post-Interview Thank You</option>
                  <option value="application_follow_up">Application Status Check</option>
                  <option value="rejection_response">Graceful Rejection Response</option>
                  <option value="offer_response">Offer Response / Acceptance</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Recipient Name</label>
                <input
                  type="text"
                  value={emailRecipient}
                  onChange={(e) => setEmailRecipient(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                onClick={() => handleDraftEmail(false)}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all"
              >
                <Mail className="w-4 h-4" />
                <span>Draft Email (Preview)</span>
              </button>

              {emailDraftResult && (
                <div className="space-y-3 bg-slate-950 p-3 rounded-lg border border-slate-800 mt-3">
                  <div className="text-xs font-bold text-slate-200">{emailDraftResult.subject}</div>
                  <pre className="text-[11px] text-slate-300 font-mono whitespace-pre-wrap">{emailDraftResult.body}</pre>
                  
                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                    <div className="text-[10px] text-amber-400 font-medium">
                      ⚠️ Explicit User Confirmation Required to Send
                    </div>
                    <button
                      onClick={() => handleDraftEmail(true)}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs font-medium flex items-center space-x-1"
                    >
                      <Send className="w-3 h-3" />
                      <span>Confirm & Prepare Mailto</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* CALENDAR SCHEDULING */}
          <div className="space-y-4 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-purple-400" />
              <span>Interview Calendar & Reminders</span>
            </h2>

            <div className="space-y-3">
              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Event Type</label>
                <select
                  value={eventType}
                  onChange={(e) => setEventType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="interview">Technical / HR Interview</option>
                  <option value="recruiter_meeting">Recruiter Phone Screen</option>
                  <option value="follow_up_reminder">Follow-up Reminder</option>
                  <option value="application_deadline">Application Deadline</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 block mb-1">Date & Time</label>
                <input
                  type="datetime-local"
                  value={eventTime}
                  onChange={(e) => setEventTime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                onClick={() => handleCreateCalendarEvent(false)}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all"
              >
                <Calendar className="w-4 h-4" />
                <span>Generate Calendar Event (.ICS)</span>
              </button>

              {calendarResult && (
                <div className="space-y-3 bg-slate-950 p-3 rounded-lg border border-slate-800 mt-3">
                  <div className="text-xs font-bold text-slate-200">{calendarResult.summary}</div>
                  <div className="text-[11px] text-slate-400">Scheduled: {calendarResult.event_time}</div>
                  
                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                    <div className="text-[10px] text-purple-400 font-medium">
                      ⚠️ Requires Confirmation
                    </div>
                    <button
                      onClick={() => {
                        const blob = new Blob([calendarResult.ics_content], { type: "text/calendar" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `interview-${targetCompany}.ics`;
                        a.click();
                        handleCreateCalendarEvent(true);
                      }}
                      className="bg-purple-600 hover:bg-purple-500 text-white px-3 py-1 rounded text-xs font-medium flex items-center space-x-1"
                    >
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Download .ICS Event File</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 5: INTERVIEW PREP STUDIO */}
      {activeTab === "interview" && (
        <div className="space-y-4 max-w-3xl mx-auto bg-slate-900/40 p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            <span>Dedicated Interview Prep Studio</span>
          </h2>
          <p className="text-xs text-slate-400">
            Generate role-specific technical and behavioural interview questions grounded in your resume facts.
          </p>

          <button
            onClick={handleFetchInterviewPrep}
            disabled={loading}
            className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/10"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? "Preparing Questions..." : `Prepare Questions for ${targetCompany}`}</span>
          </button>

          {interviewPrep && (
            <div className="space-y-6 mt-6">
              {/* STAR COACHING FRAMEWORK */}
              <div className="bg-slate-950 p-4 rounded-xl border border-cyan-500/30">
                <h3 className="text-xs font-bold text-cyan-300 mb-2">{interviewPrep.star_coaching.framework}</h3>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {interviewPrep.star_coaching.guidance.map((g: string, i: number) => (
                    <li key={i} dangerouslySetInnerHTML={{ __html: g }} />
                  ))}
                </ul>
              </div>

              {/* TECHNICAL QUESTIONS */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-200">Role-Specific Technical Questions</h3>
                <div className="space-y-2">
                  {interviewPrep.technical_questions.map((q: string, i: number) => (
                    <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs text-slate-300">
                      <span className="text-cyan-400 font-bold mr-2">Q{i + 1}:</span> {q}
                    </div>
                  ))}
                </div>
              </div>

              {/* BEHAVIOURAL QUESTIONS */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-200">Behavioural Questions</h3>
                <div className="space-y-2">
                  {interviewPrep.behavioural_questions.map((q: string, i: number) => (
                    <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs text-slate-300">
                      <span className="text-purple-400 font-bold mr-2">Q{i + 1}:</span> {q}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 6: STUDENT ELIGIBILITY VERIFICATION */}
      {activeTab === "verify" && (
        <div className="space-y-4 max-w-md mx-auto bg-slate-900/40 p-6 rounded-xl border border-slate-800 text-center">
          <UserCheck className="w-10 h-10 text-cyan-400 mx-auto" />
          <h2 className="text-sm font-bold text-slate-200">Student Eligibility Verification</h2>
          <p className="text-xs text-slate-400">
            Verify your .ac.in / .edu university email to qualify for the Student Plan entitlement (₹149/month or ₹1,299/year).
          </p>

          <div className="space-y-3 pt-2 text-left">
            <div>
              <label className="text-[11px] font-medium text-slate-400 block mb-1">University Email Address</label>
              <input
                type="email"
                value={studentEmail}
                onChange={(e) => setStudentEmail(e.target.value)}
                placeholder="student@university.ac.in"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={handleVerifyStudent}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium py-2 rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-all shadow-md shadow-cyan-500/10"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Verify Student Status</span>
            </button>
          </div>

          {verificationResult && (
            <div className={`mt-4 p-3 rounded-lg border text-xs text-left ${
              verificationResult.verified ? "bg-emerald-950/40 border-emerald-700 text-emerald-300" : "bg-rose-950/40 border-rose-700 text-rose-300"
            }`}>
              <div className="font-bold mb-1">{verificationResult.verified ? "✓ Verification Successful" : "✗ Verification Failed"}</div>
              <div>{verificationResult.message || verificationResult.reason}</div>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 7: REFERRAL & INVITE A FRIEND */}
      {activeTab === "referral" && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6 max-w-2xl mx-auto text-center">
          <div className="flex flex-col items-center space-y-2">
            <div className="p-3 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-full">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-slate-100">Invite a Friend to Saarthi</h2>
            <p className="text-xs text-slate-400 max-w-md">
              Share your referral code with friends and colleagues. Give them full access to AI job search tools and earn bonus usage.
            </p>
          </div>

          {referralData && (
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
              <div className="text-[11px] text-slate-400 font-medium">Your Personal Referral Code</div>
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xl font-extrabold text-cyan-400 tracking-wider font-mono bg-cyan-950/40 px-4 py-1.5 rounded-lg border border-cyan-800/60">
                  {referralData.referral_code}
                </span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(referralData.referral_code);
                    alert("Referral code copied to clipboard!");
                  }}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-2 rounded-lg transition-all"
                >
                  Copy Code
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800/80 text-left">
                <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">Successful Referrals</div>
                  <div className="text-lg font-bold text-emerald-400">{referralData.successful_referrals}</div>
                </div>
                <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-slate-400">Earned Benefits</div>
                  <div className="text-xs font-semibold text-amber-300 mt-1">{referralData.earned_rewards_description}</div>
                </div>
              </div>
            </div>
          )}

          {/* REDEEM REFERRAL CODE FORM */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-left space-y-3">
            <div className="text-xs font-bold text-slate-200">Have a Referral Code?</div>
            <form onSubmit={handleRedeemReferral} className="flex items-center space-x-2">
              <input
                type="text"
                required
                placeholder="REF-XXXXXX"
                value={referralInput}
                onChange={(e) => setReferralInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 uppercase font-mono focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium px-4 py-1.5 rounded-lg text-xs transition-all shadow-md shadow-cyan-500/10"
              >
                Redeem Code
              </button>
            </form>
            {referralRedeemMsg && (
              <div className="text-xs text-cyan-300 bg-cyan-950/60 p-2 rounded border border-cyan-800">
                {referralRedeemMsg}
              </div>
            )}
          </div>
        </div>
      )}

      {/* NEW APPLICATION MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100">Track New Job Application</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-200 text-xs">✕</button>
            </div>

            <form onSubmit={handleCreateApplication} className="space-y-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Company Name *</label>
                <input
                  type="text"
                  required
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Role Title *</label>
                <input
                  type="text"
                  required
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Location</label>
                  <input
                    type="text"
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Salary Range</label>
                  <input
                    type="text"
                    value={newSalary}
                    onChange={(e) => setNewSalary(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Initial Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as ApplicationStatus)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="SAVED">SAVED</option>
                  <option value="APPLIED">APPLIED</option>
                  <option value="SCREENING">SCREENING</option>
                  <option value="INTERVIEW">INTERVIEW</option>
                  <option value="OFFER">OFFER</option>
                  <option value="REJECTED">REJECTED</option>
                  <option value="WITHDRAWN">WITHDRAWN</option>
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-medium px-4 py-1.5 rounded-lg text-xs shadow-md shadow-cyan-500/10"
                >
                  Save Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
