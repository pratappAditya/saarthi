import type { 
  ResumeItem, 
  ApplicationItem, 
  InterviewQuestion, 
  CoverLetterItem, 
  NemotronModel, 
  SystemHardware, 
  CareerGoal,
  PlanTier,
  ATSAnalysisResult,
  TailoredDiffItem
} from '../types';

export const INITIAL_HARDWARE: SystemHardware = {
  cpu: 'Intel64 Family 6 Model 165 Stepping 2, GenuineIntel',
  cores: 8,
  ramTotal: '23.8 GB DDR4',
  ramAvailable: '9.5 GB Available',
  gpu: 'NVIDIA GeForce GTX 1650 Ti',
  vramTotal: '4.0 GB GDDR6',
  vramAvailable: '3.2 GB Free',
  storageFree: '232.9 GB Free SSD',
  ollamaVersion: '0.6.2 (Local Socket 127.0.0.1:11434)',
  ollamaRunning: true,
  nemotronRunning: true,
  activeModel: 'nemotron-3-nano:4b',
  inferenceSpeed: null,
  isBenchmarked: false,
  gpuLoad: 46,
  vramUsage: 68,
};

export const APPROVED_NEMOTRON_MODELS: NemotronModel[] = [
  {
    id: 'nemotron:3b',
    name: 'NVIDIA Nemotron 3B Light',
    tag: 'nemotron:3b',
    size: '1.9 GB',
    vramRequired: '0.0 GB VRAM (Integrated CPU/GPU)',
    ramRequired: '6.0 GB RAM',
    description: 'Entry-level local Nemotron model optimized for basic resume drafting and fast text generation on low-spec PCs.',
    speed: 'Estimated ~18 tokens/sec',
    quantization: 'Q4_K_M (Calibrated)',
    recommendedFor: 'STANDARD Tier — Budget Laptops with 6GB-8GB System RAM',
    isInstalled: false,
    isActive: false,
  },
  {
    id: 'nemotron-mini:4b',
    name: 'NVIDIA Nemotron Mini 4B',
    tag: 'nemotron-mini:4b',
    size: '2.7 GB',
    vramRequired: '2.0 GB VRAM',
    ramRequired: '8.0 GB RAM',
    description: 'Higher-quality instruction-tuned model for accurate ATS keywords matching, cover letter synthesis, and career chat.',
    speed: 'Physically Tested ~14.2 tokens/sec',
    quantization: 'Q4_K_M (High precision)',
    recommendedFor: 'PRO Tier — Mid-range Laptops & PCs with 8GB-16GB RAM',
    isInstalled: false,
    isActive: false,
  },
  {
    id: 'nemotron-3-nano:4b',
    name: 'NVIDIA Nemotron-3 Nano 4B',
    tag: 'nemotron-3-nano:4b',
    size: '2.64 GB',
    vramRequired: '2.0 GB VRAM',
    ramRequired: '8.0 GB RAM',
    description: 'High-performance Nemotron reasoning model with extended context window and balanced execution.',
    speed: 'Physically Benchmark: 11.67–16.14 tokens/sec',
    quantization: 'Q4_K_M (Lossless calibrated)',
    recommendedFor: 'SUPER Tier — Workstations & PCs with 4GB VRAM (Active)',
    isInstalled: true,
    isActive: true,
  },
  {
    id: 'nemotron-3.5-bolt-e4b',
    name: 'NVIDIA Nemotron 3.5 Bolt E4B',
    tag: 'nemotron-3.5-bolt-e4b',
    size: '3.1 GB',
    vramRequired: '3.0 GB VRAM',
    ramRequired: '12.0 GB RAM',
    description: 'Next-generation instruction reasoning architecture with 8K context and ultra-low TTFT for responsive conversational executive coaching.',
    speed: 'High-speed speculative decode (~24 t/s)',
    quantization: 'Q4_K_M (GGUF)',
    recommendedFor: 'SUPER Tier — Modern GPUs with 4GB-8GB VRAM',
    isInstalled: false,
    isActive: false,
  },
  {
    id: 'nemotron-3-8b',
    name: 'NVIDIA Nemotron-3 8B Power',
    tag: 'nemotron-3-8b',
    size: '4.9 GB',
    vramRequired: '6.0 GB VRAM',
    ramRequired: '16.0 GB RAM',
    description: 'Maximum-performance 8B Nemotron model for deep multi-turn interview simulations and comprehensive resume analysis.',
    speed: 'Requires 6GB+ VRAM RTX GPU',
    quantization: 'Q5_K_M (High fidelity)',
    recommendedFor: 'ULTRA Tier — High-end RTX Desktop Rigs (Incompatible with 4GB VRAM)',
    isInstalled: false,
    isActive: false,
  }
];

export const DEMO_RESUMES: ResumeItem[] = [

  {
    id: 'res-staff-fe',
    title: 'Staff Frontend Architect (Production)',
    targetRole: 'Staff / Principal Frontend Engineer',
    version: 'v4.2 — Tailored for Systems & Perf',
    lastModified: 'Yesterday at 4:18 PM',
    atsScore: 94,
    matchRate: 92,
    isDefault: true,
    pages: 2,
    skills: ['TypeScript', 'React 19', 'Next.js', 'WebAssembly', 'Distributed Systems', 'Tailwind CSS', 'GraphQL', 'Vite', 'Performance Optimization', 'Design Systems'],
    summary: 'Product-minded Staff Frontend Engineer with 8+ years architecting high-throughput web applications, design systems, and edge-rendered distributed client platforms. Reduced Core Web Vitals LCP by 48% across 12M MAU.',
    sections: [
      {
        id: 'exp-1',
        title: 'Work Experience',
        role: 'Lead Frontend Architect',
        company: 'Veloce Cloud Platform',
        period: '2023 — Present',
        location: 'San Francisco, CA (Remote)',
        bullets: [
          {
            id: 'b-1',
            text: 'Spearheaded migration of legacy SPA to modular micro-frontends with edge SSR, reducing Time-to-Interactive by 42% and slashing cloud hosting cost by $180k/yr.',
            impactScore: 96,
            highlightedKeywords: ['micro-frontends', 'edge SSR', 'Time-to-Interactive', 'cloud hosting cost'],
            suggestedImprovement: 'Quantify team size led for increased executive impact.'
          },
          {
            id: 'b-2',
            text: 'Architected enterprise Design System component token library consumed by 45+ product engineers across 6 globally distributed squads.',
            impactScore: 92,
            highlightedKeywords: ['Design System', 'token library', 'product engineers'],
          },
          {
            id: 'b-3',
            text: 'Engineered real-time canvas visualization engine using WebGL and Canvas API, supporting 100k+ concurrent telemetry nodes at 60 FPS.',
            impactScore: 98,
            highlightedKeywords: ['WebGL', 'Canvas API', 'concurrent telemetry', '60 FPS'],
          }
        ]
      },
      {
        id: 'exp-2',
        title: 'Work Experience',
        role: 'Senior Software Engineer',
        company: 'Apex Data Labs',
        period: '2020 — 2023',
        location: 'Bengaluru / Remote',
        bullets: [
          {
            id: 'b-4',
            text: 'Rebuilt real-time data table streaming parser with Web Workers and Virtualized Scrolling, achieving sub-16ms render frames for 500k row datasets.',
            impactScore: 94,
            highlightedKeywords: ['Web Workers', 'Virtualized Scrolling', 'sub-16ms', 'datasets'],
          },
          {
            id: 'b-5',
            text: 'Mentored 7 junior and mid-level engineers, established rigorous TypeScript strict-mode standards and automated CI bundle size budgets.',
            impactScore: 88,
            highlightedKeywords: ['TypeScript strict-mode', 'CI bundle size budgets', 'Mentored'],
          }
        ]
      }
    ],
    linkedApplicationsCount: 4,
  },
  {
    id: 'res-ai-eng',
    title: 'AI Systems & Full-Stack Engineer',
    targetRole: 'Senior AI Engineer / Full-Stack',
    version: 'v2.1 — Local Inference Focus',
    lastModified: 'Aug 14, 2026',
    atsScore: 89,
    matchRate: 86,
    isDefault: false,
    pages: 2,
    skills: ['Python', 'Ollama', 'NVIDIA Nemotron', 'CUDA', 'FastAPI', 'React', 'TypeScript', 'LangChain', 'Vector DB', 'PyTorch'],
    summary: 'Full-stack AI engineer specializing in local-first LLM inference engines, on-device intelligence architecture, and privacy-preserving desktop applications.',
    sections: [
      {
        id: 'exp-ai-1',
        title: 'Experience',
        role: 'AI Systems Engineer',
        company: 'Synthetix Local AI',
        period: '2024 — Present',
        location: 'Remote',
        bullets: [
          {
            id: 'b-ai-1',
            text: 'Developed offline LLM inference pipeline using Ollama and quantized Nemotron weights, delivering sub-200ms TTFT on consumer hardware.',
            impactScore: 95,
            highlightedKeywords: ['LLM inference', 'Ollama', 'Nemotron', 'TTFT'],
          }
        ]
      }
    ],
    linkedApplicationsCount: 2,
  },
  {
    id: 'res-prod-mgr',
    title: 'Technical Product & Engineering Lead',
    targetRole: 'Staff Product Engineer',
    version: 'v1.4 — Generalist',
    lastModified: 'Aug 02, 2026',
    atsScore: 81,
    matchRate: 78,
    isDefault: false,
    pages: 1,
    skills: ['Product Strategy', 'System Architecture', 'Go', 'React', 'PostgreSQL', 'User Research'],
    summary: 'Hybrid technical leader bridging product intuition with distributed systems engineering.',
    sections: [],
    linkedApplicationsCount: 1,
  }
];

export const DEMO_ATS_ANALYSIS: ATSAnalysisResult = {
  overallScore: 94,
  parseRate: 98,
  keywordMatchRate: 91,
  formatCompatibility: 96,
  matchedKeywords: [
    'TypeScript', 'React 19', 'Design Systems', 'WebAssembly', 'Performance Optimization',
    'Micro-frontends', 'GraphQL', 'CI/CD Pipelines', 'Distributed Systems', 'Core Web Vitals',
    'Edge Rendering', 'State Management', 'Testing (Jest/Playwright)'
  ],
  missingKeywords: [
    'Rust/Wasm interoperability', 'Kubernetes Helm', 'OpenTelemetry Distributed Tracing'
  ],
  crucialSkillsMissing: [
    'OpenTelemetry monitoring instrumentation',
    'Wasm memory allocation safety'
  ],
  actionableInsights: [
    {
      category: 'strength',
      title: 'Flawless Metric Quantification',
      description: '90% of bullet points contain quantifiable business outcomes (42% speedup, $180k saved, 100k nodes).'
    },
    {
      category: 'improvement',
      title: 'ATS Section Header Standard',
      description: 'Standardize "Work Experience" section headers to single-word "Experience" for legacy Taleo/Workday parser compliance.'
    },
    {
      category: 'critical',
      title: 'Target Job Keyword Gap Detected',
      description: 'The target role requires explicit mention of "Distributed Tracing" and "Telemetry pipeline design".'
    }
  ]
};

export const DEMO_TAILORED_DIFFS: TailoredDiffItem[] = [
  {
    id: 'diff-1',
    section: 'Veloce Cloud Platform • Lead Frontend Architect',
    originalText: 'Spearheaded migration of legacy SPA to modular micro-frontends with edge SSR, reducing Time-to-Interactive by 42% and slashing cloud hosting cost by $180k/yr.',
    tailoredText: 'Architected edge-rendered micro-frontends and OpenTelemetry distributed tracing pipeline, reducing Time-to-Interactive by 42% and cutting cloud infrastructure overhead by $180k/yr.',
    reason: 'Injected high-priority ATS keyword "OpenTelemetry distributed tracing" while keeping quantitative business outcomes.',
    accepted: true,
  },
  {
    id: 'diff-2',
    section: 'Summary Statement',
    originalText: 'Product-minded Staff Frontend Engineer with 8+ years architecting high-throughput web applications, design systems, and edge-rendered distributed client platforms.',
    tailoredText: 'Product-focused Staff Frontend Architect with 8+ years delivering resilient edge-first client systems, high-scale telemetry dashboards, and multi-tenant design tokens.',
    reason: 'Aligned summary verbs directly with Stripe/Linear principal job specification terminology.',
    accepted: true,
  },
  {
    id: 'diff-3',
    section: 'Apex Data Labs • Senior Software Engineer',
    originalText: 'Rebuilt real-time data table streaming parser with Web Workers and Virtualized Scrolling, achieving sub-16ms render frames for 500k row datasets.',
    tailoredText: 'Engineered high-throughput streaming data virtualizer using Web Workers and SIMD memory buffers, maintaining 60 FPS across 500k+ real-time telemetry records.',
    reason: 'Highlights low-level browser performance engineering capabilities required for target senior systems role.',
    accepted: false,
  }
];

export const DEMO_APPLICATIONS: ApplicationItem[] = [
  {
    id: 'app-stripe',
    company: 'Stripe',
    companyLogoText: 'ST',
    role: 'Staff Frontend Engineer — Developer Platform',
    location: 'San Francisco, CA / Remote',
    type: 'Full-time',
    salaryRange: '$220k – $280k + Equity',
    dateApplied: '2026-08-12',
    stage: 'interview',
    matchScore: 96,
    resumeUsedId: 'res-staff-fe',
    resumeUsedTitle: 'Staff Frontend Architect (Production)',
    nextFollowUpDate: '2026-08-22',
    notes: 'Technical screen completed with Senior Director. Round 2: System Architecture deep dive scheduled for Thursday 2:00 PM PST.',
    contacts: [
      { name: 'Elena Rostova', title: 'Senior Tech Recruiter', email: 'elena.r@stripe.com' },
      { name: 'Marcus Vance', title: 'VP of Developer Experience', email: 'marcus.v@stripe.com' }
    ],
    interviewDate: '2026-08-24 14:00 PST',
    jobDescription: 'Looking for a Staff Frontend Engineer to lead our next-generation Dashboard framework. Must have deep experience in web performance, TypeScript type-level metaprogramming, and distributed systems visualization.',
    tags: ['Tier 1 Target', 'High Comp', 'Remote-Friendly'],
    timeline: [
      { date: 'Aug 12, 2026', event: 'Applied with Nemotron tailored resume v4.2', details: 'ATS Match: 96%' },
      { date: 'Aug 15, 2026', event: 'Recruiter phone screen with Elena', details: 'Positive feedback on open-source work' },
      { date: 'Aug 18, 2026', event: 'Technical coding & problem solving round', details: 'Passed with high marks on state machine architecture' },
      { date: 'Aug 24, 2026', event: 'Upcoming: System Design & Leadership Panel', details: '4x 45-min rounds' }
    ]
  },
  {
    id: 'app-linear',
    company: 'Linear',
    companyLogoText: 'LN',
    role: 'Senior Product Engineer — Desktop & Sync Engine',
    location: 'Remote (Worldwide)',
    type: 'Full-time',
    salaryRange: '$190k – $240k + Equity',
    dateApplied: '2026-08-08',
    stage: 'screening',
    matchScore: 92,
    resumeUsedId: 'res-staff-fe',
    resumeUsedTitle: 'Staff Frontend Architect (Production)',
    nextFollowUpDate: '2026-08-21',
    notes: 'Recruiter reached out via email. Sent availability for async technical interview.',
    contacts: [
      { name: 'Tuomas Artman', title: 'Co-founder & Head of Eng', email: 'tuomas@linear.app' }
    ],
    jobDescription: 'Build buttery-smooth client applications with local-first SQLite sync engines, keyboard shortcuts, and zero-latency UI interactions.',
    tags: ['Local-First', 'Elite Product Quality'],
    timeline: [
      { date: 'Aug 08, 2026', event: 'Application submitted', details: 'Custom cover letter highlighting sync engines' },
      { date: 'Aug 14, 2026', event: 'Invitation to take-home architectural assessment', details: 'Due in 5 days' }
    ]
  },
  {
    id: 'app-anthropic',
    company: 'Anthropic',
    companyLogoText: 'AN',
    role: 'Frontend Systems Architect — AI Interfaces',
    location: 'San Francisco, CA',
    type: 'Hybrid',
    salaryRange: '$230k – $310k + Equity',
    dateApplied: '2026-08-16',
    stage: 'applied',
    matchScore: 94,
    resumeUsedId: 'res-ai-eng',
    resumeUsedTitle: 'AI Systems & Full-Stack Engineer',
    nextFollowUpDate: '2026-08-25',
    notes: 'Applied through employee referral from Vivek. Nemotron tailored for AI canvas visualization.',
    contacts: [
      { name: 'Vivek Chander', title: 'Research Lead', email: 'v.chander@anthropic.com' }
    ],
    jobDescription: 'Design scalable, responsive interfaces for frontier AI models. Canvas interactions, streaming token rendering, and interactive alignment tools.',
    tags: ['AI Frontier', 'Referral Active'],
    timeline: [
      { date: 'Aug 16, 2026', event: 'Application submitted via internal referral', details: 'Application ID #ANT-90214' }
    ]
  },
  {
    id: 'app-vercel',
    company: 'Vercel',
    companyLogoText: 'VC',
    role: 'Principal Design Technologist',
    location: 'Remote',
    type: 'Full-time',
    salaryRange: '$210k – $260k + Equity',
    dateApplied: '2026-07-28',
    stage: 'offer',
    matchScore: 97,
    resumeUsedId: 'res-staff-fe',
    resumeUsedTitle: 'Staff Frontend Architect (Production)',
    nextFollowUpDate: '2026-08-23',
    notes: 'Official offer letter received! Base: $235k, Equity: $180k/4yr, Sign-on: $25k. Decision deadline is Aug 28.',
    contacts: [
      { name: 'Guillermo Rauch', title: 'CEO', email: 'rauchg@vercel.com' },
      { name: 'Sarah Lin', title: 'People Ops Director', email: 'sarah.lin@vercel.com' }
    ],
    jobDescription: 'Shape the future of developer tooling, micro-frontends, and next-gen frontend infrastructure at global scale.',
    tags: ['Active Offer', 'Decision Pending'],
    timeline: [
      { date: 'Jul 28, 2026', event: 'Applied' },
      { date: 'Aug 04, 2026', event: 'Technical onsite round (5 sessions)' },
      { date: 'Aug 17, 2026', event: 'Written Offer Extended', details: 'Reviewing compensation package' }
    ]
  },
  {
    id: 'app-figma',
    company: 'Figma',
    companyLogoText: 'FG',
    role: 'Senior Staff Engineer — WebAssembly Core',
    location: 'San Francisco, CA / Remote',
    type: 'Full-time',
    salaryRange: '$225k – $290k + Equity',
    dateApplied: '2026-08-01',
    stage: 'saved',
    matchScore: 88,
    resumeUsedId: 'res-staff-fe',
    resumeUsedTitle: 'Staff Frontend Architect (Production)',
    nextFollowUpDate: '2026-08-21',
    notes: 'Need to tailor resume with more C++/Rust & WebAssembly engine highlights before submitting.',
    contacts: [],
    jobDescription: 'Push the limits of multiplayer real-time rendering in WebGL and WebAssembly.',
    tags: ['To Apply', 'C++/WASM'],
    timeline: [
      { date: 'Aug 01, 2026', event: 'Job bookmarked for preparation' }
    ]
  },
  {
    id: 'app-openai',
    company: 'OpenAI',
    companyLogoText: 'OA',
    role: 'Staff Product Infrastructure Engineer',
    location: 'San Francisco, CA',
    type: 'Full-time',
    salaryRange: '$250k – $340k + Equity',
    dateApplied: '2026-07-15',
    stage: 'rejected',
    matchScore: 84,
    resumeUsedId: 'res-staff-fe',
    resumeUsedTitle: 'Staff Frontend Architect (Production)',
    nextFollowUpDate: '2026-11-15',
    notes: 'Passed initial screening, rejected after stage 3 system design due to candidate profile mismatch for distributed storage focus. Re-apply eligible in 6 months.',
    contacts: [],
    jobDescription: 'Build high-availability developer platform tools for foundation model API developers.',
    tags: ['Archived', 'Cool-down 6 mo'],
    timeline: [
      { date: 'Jul 15, 2026', event: 'Application submitted' },
      { date: 'Aug 02, 2026', event: 'System design interview' },
      { date: 'Aug 07, 2026', event: 'Friendly rejection with feedback note' }
    ]
  }
];

export const DEMO_INTERVIEWS: InterviewQuestion[] = [
  {
    id: 'q-1',
    category: 'system_design',
    question: 'How would you design a real-time collaborative canvas architecture supporting 50+ concurrent editors with offline durability and zero conflict data loss?',
    difficulty: 'Advanced',
    companyTarget: 'Figma / Linear / Stripe',
    starStructure: {
      situation: 'At Veloce Cloud, users experienced UI latency and occasional state divergence when multiple engineers concurrently edited telemetry dashboard layouts.',
      task: 'Design and deploy a conflict-free client synchronization architecture that operates with 0ms optimistic UI updates while preserving atomic server consistency.',
      action: 'Implemented a CRDT (Conflict-free Replicated Data Type) engine backed by WebSockets, with local SQLite persistence on the client and append-only WAL logs on the edge worker layer.',
      result: 'Eliminated 100% of conflict overwrite errors, reduced client sync latency from 320ms to 24ms, and enabled seamless offline edits across 45,000 active sessions.'
    },
    sampleAnswer: 'I would approach this using a Local-First CRDT topology (such as Yjs or Automerge). The client state operates against a local transactional store for immediate 0ms perceptual latency. Changes are broadcast as delta-encoded vector operations over WebSockets, with a central edge sequencer providing deterministic causal ordering...',
    userAnswer: 'I will use WebSockets connected to a server with Redis PubSub. When someone clicks or drags, we broadcast the coordinates. If the client goes offline, we cache events in localStorage and flush upon reconnection.',
    feedback: {
      score: 76,
      impactScore: 72,
      clarityScore: 84,
      technicalAccuracy: 74,
      strengths: [
        'Clear understanding of real-time transport (WebSockets + PubSub)',
        'Addresses offline buffering via local persistence'
      ],
      gaps: [
        'Lacks formal mathematical conflict resolution mechanism (CRDT or Operational Transformation)',
        'LocalStorage has a 5MB storage limit and blocks the main thread; prefer IndexedDB or SQLite via OPFS',
        'Did not specify how simultaneous conflicting drag operations on the same object are resolved'
      ],
      improvedBulletSuggestion: 'Highlight CRDT state synchronization, binary delta compression via Protobuf/CapnProto, and IndexedDB OPFS storage.'
    }
  },
  {
    id: 'q-2',
    category: 'behavioral',
    question: 'Describe a situation where you had a major architectural disagreement with a Principal Engineer or Product Manager. How did you resolve it?',
    difficulty: 'Intermediate',
    companyTarget: 'Stripe',
    starStructure: {
      situation: 'During our Q3 planning, the backend Principal proposed a synchronous monolithic GraphQL schema for all micro-frontends, while I argued for federated schema boundaries.',
      task: 'Prevent a single point of failure in our deployment pipeline without damaging cross-functional engineering trust.',
      action: 'Built a 2-day functional prototype benchmarking build times, runtime fault isolation, and developer velocity metrics. Presented an objective tradeoff matrix in our RFC review.',
      result: 'The team unanimously adopted GraphQL Federation with independent sub-graph deployments, saving an estimated 3 hours per week per engineer in blocked deploy queues.'
    },
    sampleAnswer: 'When disagreements occur, I ground discussions in empirical data and customer impact rather than personal opinions. I establish clear decision criteria, build lightweight prototypes to test contested assumptions, and ensure full transparency through structured RFCs...',
    feedback: {
      score: 92,
      impactScore: 94,
      clarityScore: 91,
      technicalAccuracy: 90,
      strengths: [
        'Follows STAR framework cleanly',
        'Replaces emotion with empirical prototyping and trade-off matrices',
        'Clear quantified outcome (3 hours saved weekly)'
      ],
      gaps: [],
      improvedBulletSuggestion: 'Emphasize long-term relationship health post-decision.'
    }
  },
  {
    id: 'q-3',
    category: 'technical',
    question: 'Explain how the React 19 compiler eliminates manual memoization (useMemo / useCallback) and how it affects Fiber tree reconciliation and memory footprints.',
    difficulty: 'Advanced',
    companyTarget: 'Vercel / Anthropic',
    starStructure: {
      situation: 'Large enterprise codebases suffer from stale memoization dependencies and excessive boilerplate.',
      task: 'Evaluate the React 19 compiler transformation model for our enterprise design system.',
      action: 'Analyzed the AST compiler step that injects reactive memo caches at the sub-expression level rather than component level.',
      result: 'Removed 1,400+ lines of redundant useMemo boilerplate while reducing unnecessary child component renders by 34%.'
    },
    sampleAnswer: 'The React 19 Compiler performs static analysis on JavaScript semantics to generate fine-grained memoization slots. Rather than comparing coarse reference equality on whole hooks, it memoizes intermediate values in a flat cache array...',
    feedback: {
      score: 88,
      impactScore: 86,
      clarityScore: 90,
      technicalAccuracy: 89,
      strengths: ['Accurate breakdown of AST compiler pass vs runtime hook overhead'],
      gaps: ['Mention edge cases like mutable object mutations bypassing compiler reactivity'],
      improvedBulletSuggestion: 'Add caveat regarding mutable object references and ESLint reactivity rules.'
    }
  }
];

export const DEMO_COVER_LETTERS: CoverLetterItem[] = [
  {
    id: 'cl-stripe',
    targetCompany: 'Stripe',
    targetRole: 'Staff Frontend Engineer — Developer Platform',
    tone: 'Confident',
    dateCreated: '2026-08-12',
    jobMatchScore: 95,
    linkedResumeId: 'res-staff-fe',
    content: `Dear Stripe Developer Experience Team,

I am writing to express my strong enthusiasm for the Staff Frontend Engineer role on the Developer Platform team at Stripe. Having spent the last 8+ years building high-throughput developer platforms, design systems, and distributed web interfaces, I have long admired Stripe's relentless commitment to craft, sub-millisecond responsiveness, and developer ergonomics.

In my recent role as Lead Frontend Architect at Veloce Cloud, I spearheaded the architecture of our edge-rendered micro-frontend platform and global token design system, reducing Time-to-Interactive by 42% across 12 million monthly active users while saving over $180,000 annually in compute overhead. Furthermore, my work engineering real-time WebGL telemetry canvases directly mirrors Stripe's mission of transforming complex financial pipelines into transparent, immediate web experiences.

I am particularly excited by the prospect of contributing to Stripe's next-generation Dashboard and UI primitives. With a local-first engineering mindset and deep expertise in TypeScript type-level architecture and web performance, I am confident I can make an immediate, lasting impact.

Thank you for your time and consideration. I welcome the opportunity to discuss how my background aligns with your vision.

Sincerely,
Demo Candidate`
  },
  {
    id: 'cl-linear',
    targetCompany: 'Linear',
    targetRole: 'Senior Product Engineer — Sync Engine',
    tone: 'Technical',
    dateCreated: '2026-08-08',
    jobMatchScore: 92,
    linkedResumeId: 'res-staff-fe',
    content: `Dear Linear Engineering Team,

Linear has redefined what developers expect from desktop software: instantaneous interactions, keyboard-driven navigation, and zero perceptible latency. I am writing to express my deep interest in the Senior Product Engineer position focusing on the Desktop & Sync Engine.

Throughout my career, I have focused on local-first architectures, optimistic state reconciliation, and WebAssembly acceleration. At Apex Data Labs, I rebuilt our core real-time streaming table engine using Web Workers and virtualized memory allocations to sustain 60 FPS under 500,000 live rows.

I would love to bring this dedication to buttery-smooth software craft to Linear's sync engine and desktop experience.

Warm regards,
Demo Candidate`
  }
];

export const DEMO_CAREER_GOAL: CareerGoal = {
  targetTitle: 'Staff / Principal Frontend Architect',
  targetLevel: 'L6 / Staff (ICT5 / E6)',
  targetCompRange: '$220k – $320k Total Comp',
  targetIndustries: ['Developer Tooling', 'AI Platforms', 'Fintech', 'Design Infrastructure'],
  coreSkills: [
    { name: 'Distributed Web Architecture', proficiency: 94, demand: 'Very High' },
    { name: 'TypeScript & Type-Level Metaprogramming', proficiency: 98, demand: 'Very High' },
    { name: 'Web Performance & Core Web Vitals', proficiency: 96, demand: 'High' },
    { name: 'Local-First AI (Ollama/Nemotron)', proficiency: 90, demand: 'Very High' },
    { name: 'Design System Engineering', proficiency: 95, demand: 'High' },
    { name: 'WebAssembly & SIMD', proficiency: 78, demand: 'Medium' }
  ],
  timelineGoal: 'Secure Staff Offer by September 30, 2026',
  weeklyApplicationTarget: 5,
  weeklyApplicationsDone: 4
};

export const PLAN_TIERS: PlanTier[] = [
  {
    id: 'student',
    name: 'Student',
    inrPrice: 99,
    usdPrice: 1.50,
    billingPeriod: '/month',
    tagline: 'Essential local AI career superpowers for students and early-career engineers.',
    features: [
      'Unlimited local ATS resume parsing & scoring',
      'Local NVIDIA Nemotron-Mini 4B integration',
      'Up to 5 Tailored resume versions',
      'Basic cover letter generator (3 tones)',
      '100% Offline & Private on your laptop',
      'Community Discord & guides'
    ],
    ctaText: 'Start with Student'
  },
  {
    id: 'personal',
    name: 'Personal',
    badge: 'Most Popular',
    isPopular: true,
    inrPrice: 399,
    usdPrice: 5.00,
    billingPeriod: '/month',
    tagline: 'The complete AI career operating system for active job seekers and professionals.',
    features: [
      'Everything in Student, plus:',
      'All approved Nemotron models (Mini 4B & Nemotron-3 8B)',
      'Unlimited Resume Tailoring & Diff Acceptance',
      'Interactive STAR Behavioral & Technical Interview Simulator',
      'Application Tracker with Kanban & Timeline telemetry',
      'Executive & Technical Cover Letter synthesizers',
      'Local document vault with zero cloud transmission guarantee',
      'Priority email & desktop support'
    ],
    ctaText: 'Get Personal Plan'
  },
  {
    id: 'power',
    name: 'Power',
    badge: 'Maximum Local AI',
    inrPrice: 799,
    usdPrice: 10.00,
    billingPeriod: '/month',
    tagline: 'Unrestricted workstation intelligence with flagship 15B Nemotron models and deep mock drills.',
    features: [
      'Everything in Personal, plus:',
      'Support for flagship Nemotron-4 15B models & future releases',
      'Advanced VRAM allocation & custom quantizations',
      'Multi-resume matrix comparisons & batch ATS audits',
      'Custom interview rubrics & salary negotiation copilot',
      'Early access to beta desktop builds & experimental features'
    ],
    ctaText: 'Upgrade to Power'
  }
];

export const DEFAULT_EMPTY_RESUME: ResumeItem = {
  id: 'res-empty',
  title: 'Untitled Resume',
  targetRole: 'Target Role Unset',
  version: 'v1.0 (Draft)',
  lastModified: 'Today',
  atsScore: 0,
  matchRate: 0,
  isDefault: true,
  pages: 1,
  skills: [],
  summary: 'No resume content available. Click "Upload Resume" to import your resume.',
  sections: [],
  linkedApplicationsCount: 0
};

export const DEFAULT_EMPTY_APPLICATION: ApplicationItem = {
  id: 'app-empty',
  company: 'Target Company',
  companyLogoText: 'TC',
  role: 'Target Role',
  location: 'Remote',
  type: 'Remote',
  salaryRange: '$0',
  stage: 'saved',
  dateApplied: 'Not Applied',
  matchScore: 0,
  resumeUsedId: '',
  resumeUsedTitle: '',
  nextFollowUpDate: '',
  jobDescription: '',
  contacts: [],
  tags: [],
  timeline: [],
  notes: ''
};

export const DEFAULT_EMPTY_COVER_LETTER: CoverLetterItem = {
  id: 'cl-empty',
  targetCompany: 'Target Company',
  targetRole: 'Target Role',
  tone: 'Confident',
  dateCreated: 'Today',
  jobMatchScore: 0,
  linkedResumeId: 'res-empty',
  content: 'No cover letter generated yet.'
};

export const INITIAL_RESUMES: ResumeItem[] = [];
export const INITIAL_APPLICATIONS: ApplicationItem[] = [];
export const INITIAL_INTERVIEWS: InterviewQuestion[] = [];
export const INITIAL_COVER_LETTERS: CoverLetterItem[] = [];
export const INITIAL_CAREER_GOAL: CareerGoal = {
  targetTitle: '',
  targetLevel: '',
  targetCompRange: '',
  targetIndustries: [],
  coreSkills: [],
  timelineGoal: '',
  weeklyApplicationTarget: 0,
  weeklyApplicationsDone: 0
};
export const INITIAL_ATS_ANALYSIS: ATSAnalysisResult = {
  overallScore: 0,
  parseRate: 0,
  keywordMatchRate: 0,
  formatCompatibility: 0,
  matchedKeywords: [],
  missingKeywords: [],
  crucialSkillsMissing: [],
  actionableInsights: []
};
export const INITIAL_TAILORED_DIFFS: TailoredDiffItem[] = [];

