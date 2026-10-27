# Saarthi Real-World Manual QA Test Matrix

| QA Phase | Subsystem / Control | Verification Method | Result | Severity if Failed |
| :--- | :--- | :--- | :---: | :---: |
| **Phase 1** | Application Startup & Server Handshake | Browser UI & `/api/health` | **PASS** | P0 |
| **Phase 2** | UI Button & Navigation Matrix (248 Controls) | Click audit across views | **PASS** | P1 |
| **Phase 3** | Experience Shell Parity (Signature, Forge, Pulse, Aurora) | Cross-shell state check | **PASS** | P1 |
| **Phase 4** | Command Center & Proactive Home | Component render & DB sync | **PASS** | P2 |
| **Phase 5** | Universal Chat & Conversation History | E2E chat & SQLite history | **PASS** | P1 |
| **Phase 6** | Memory Inspection, Provenance & Deletion | `user_memories` DB CRUD | **PASS** | P1 |
| **Phase 7** | Projects & Isolation | Project creation & file scope | **PASS** | P1 |
| **Phase 8** | Multimodal OCR, PDF, DOCX & Vision | Document ingestion engine | **PASS** | P1 |
| **Phase 9** | Academic Research & Citation Provenance | Literature search engine | **PASS** | P1 |
| **Phase 10** | 17 Universal Domain Packs | `DomainRegistry` inspection | **PASS** | P1 |
| **Phase 11** | Agentic TaskGraph & Risk Permissions | `permission_engine.py` | **PASS** | P0 |
| **Phase 12** | Proactive JARVIS Suggestions | `proactive_engine.py` | **PASS** | P2 |
| **Phase 13** | Goal & Milestone Tracking | Career & project goals | **PASS** | P2 |
| **Phase 14** | Routines & Visual Builder | `routine_engine.py` | **PASS** | P2 |
| **Phase 15** | Cross-Domain Autonomy & Handoffs | `domain_handoff.py` | **PASS** | P2 |
| **Phase 16** | Career Workspace (ATS, STAR, Salary) | `career_engine.py` | **PASS** | P1 |
| **Phase 17** | Education & Study Workspace | `study_api.py` endpoints | **PASS** | P1 |
| **Phase 18** | Software & SWE Workbench | Code execution & terminal | **PASS** | P1 |
| **Phase 19** | Business Workspace | Strategy & competitive analysis | **PASS** | P2 |
| **Phase 20** | Writing & Copyediting Workbench | Document transformation | **PASS** | P2 |
| **Phase 21** | Cybersecurity & OWASP Audits | Log review & threat modeling | **PASS** | P2 |
| **Phase 22** | Unified Global Search (`/api/search`) | `search_api.py` query engine | **PASS** | P1 |
| **Phase 23** | Notification Center & Quiet Hours | Toast stack & digest mode | **PASS** | P2 |
| **Phase 24** | Export System & Watermark Enforcement | Document export engine | **PASS** | P2 |
| **Phase 25** | Plan Matrix & Server Entitlement Gating | `require_capability` check | **PASS** | P0 |
| **Phase 26** | Admin Control Plane (21 Subsystems) | `verify_admin_access` 403 gate | **PASS** | P0 |
| **Phase 27** | Billing-Ready Architecture & Frozen Tiers | `teams`/`enterprise` frozen | **PASS** | P1 |
| **Phase 28** | Onboarding Tour & First-Run Setup | `BetaOnboardingModal.tsx` | **PASS** | P2 |
| **Phase 29** | Trust Center, Audit & Privacy Controls | `intelligence_audit.py` | **PASS** | P0 |
| **Phase 30** | Generic Local Voice Engine (STT/TTS) | `VoiceConversationModal.tsx` | **PASS** | P1 |
| **Phase 31** | Responsive UI & Design System | Cross-resolution UI checks | **PASS** | P2 |
| **Phase 32** | Application Restart & Database Persistence | Database reload verification | **PASS** | P0 |
| **Phase 33** | Edge Case Failure & Error Recovery | Exception shield & retries | **PASS** | P1 |
| **Phase 34** | Code Hygiene & Type Checking | `tsc -b` compilation | **PASS** | P1 |
| **Phase 35** | Real Error Monitoring | Zero console & backend tracebacks | **PASS** | P1 |
