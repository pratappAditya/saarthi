"""
Synthetic Anonymized Real-World Career Dataset Generator for Saarthi QA.
Generates 16 distinct candidate profiles and 20 diverse job descriptions.
"""

import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
JDS_DIR = os.path.join(DATA_DIR, "jds")

os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(JDS_DIR, exist_ok=True)

PROFILES = {
    "software_engineer": {
        "title": "Software Engineer (Full Stack)",
        "content": """
Alex Chen
San Francisco, CA | alex.chen@example.com | github.com/alexchen-dev

SUMMARY
Software Engineer with 3+ years of experience building high-throughput web applications, Node.js microservices, and React design systems. Reduced p99 latency by 35% across 2M daily active users.

EXPERIENCE
Software Engineer | Veloce Systems | 2023 - Present
- Spearheaded React 19 SPA migration, improving Core Web Vitals LCP from 3.2s to 1.1s.
- Built GraphQL API gateway handling 45,000 requests per minute with Node.js and Redis.

Junior Developer | Apex Labs | 2021 - 2023
- Implemented automated CI/CD pipeline using GitHub Actions, cutting release cycles from 2 days to 15 minutes.
- Maintained PostgreSQL schema migrations and optimized slow SQL queries.

SKILLS
JavaScript, TypeScript, React, Node.js, Express, PostgreSQL, Redis, Docker, Git, CI/CD
"""
    },
    "senior_backend_engineer": {
        "title": "Senior Backend Engineer",
        "content": """
Marcus Vance
Austin, TX | marcus.vance@example.com | linkedin.com/in/marcus-vance

SUMMARY
Senior Distributed Systems Engineer with 8 years of experience designing fault-tolerant Go microservices, Kafka event streams, and Kubernetes infrastructure. Led 6 engineers across 3 infrastructure squads.

EXPERIENCE
Staff Backend Architect | CloudScale Data | 2022 - Present
- Architected multi-region Kafka streaming cluster handling 1.2M events/sec with 99.999% availability.
- Reduced cloud infrastructure spending by $240,000 annually through Rust WASM sidecar optimizations.

Senior Software Engineer | Datacity Inc | 2018 - 2022
- Designed gRPC microservices in Go for distributed transaction processing.
- Implemented OpenTelemetry tracing across 140 microservices.

SKILLS
Go, Rust, Python, Distributed Systems, Kafka, Kubernetes, gRPC, PostgreSQL, Cassandra, AWS
"""
    },
    "frontend_engineer": {
        "title": "Frontend Architect / Engineer",
        "content": """
Priya Sharma
Seattle, WA | priya.sharma@example.com

SUMMARY
Frontend Engineer with 5 years specializing in web performance, micro-frontends, and accessible design systems.

EXPERIENCE
Lead Frontend Engineer | UI Modern | 2022 - Present
- Built semantic token design system consumed by 18 product teams.
- Optimized Interaction to Next Paint (INP) to sub-50ms on financial dashboards.

SKILLS
TypeScript, React, Next.js, TailwindCSS, WebGL, Vite, Web Vitals, Accessibility (WCAG 2.1)
"""
    },
    "data_analyst": {
        "title": "Data Analyst",
        "content": """
David Miller
Chicago, IL | david.m@example.com

SUMMARY
Data Analyst with 2+ years executing SQL ETL pipelines, Tableau executive dashboards, and A/B testing statistical analyses.

EXPERIENCE
Data Analyst | Commerce Metrics | 2022 - Present
- Created automated Tableau dashboards tracking $12M monthly recurring revenue.
- Ran A/B experiments on checkout funnel, driving 4.2% conversion uplift.

SKILLS
SQL, PostgreSQL, Tableau, Python, Pandas, A/B Testing, Excel, PowerBI
"""
    },
    "data_scientist": {
        "title": "Data Scientist / ML Engineer",
        "content": """
Dr. Elena Rostova
Boston, MA | elena.rostova@example.com

SUMMARY
Data Scientist with Ph.D. in Computational Statistics and 4 years of industry experience deploying PyTorch NLP models and recommendation algorithms.

EXPERIENCE
Senior ML Engineer | Cognitive AI Labs | 2022 - Present
- Fine-tuned 7B parameter Transformer models for semantic retrieval, boosting precision@k by 18%.
- Built real-time feature store using Feast and Redis.

SKILLS
Python, PyTorch, TensorFlow, Scikit-Learn, Transformers, MLOps, MLflow, AWS SageMaker
"""
    },
    "cybersecurity_analyst": {
        "title": "Cybersecurity / Incident Analyst",
        "content": """
Robert Taylor
Washington, DC | r.taylor@example.com

SUMMARY
SOC Analyst with 3 years monitoring SIEM telemetry, threat hunting, and executing incident response playbooks.

EXPERIENCE
Cyber Security Specialist | Defense Guard Tech | 2021 - Present
- Monitored Splunk SIEM alerts across 10,000 corporate endpoints.
- Conducted malware triage and threat intelligence mapping to MITRE ATT&CK.

SKILLS
Splunk, CrowdStrike, Wireshark, Python, Incident Response, ISO 27001, Vulnerability Scanning
"""
    },
    "devops_cloud_engineer": {
        "title": "DevOps / SRE Engineer",
        "content": """
Samantha Brooks
Denver, CO | sam.brooks@example.com

SUMMARY
DevOps Engineer with 6 years configuring AWS multi-region infrastructure, Terraform IAC, and ArgoCD Kubernetes deployments.

EXPERIENCE
Senior DevOps Engineer | CloudOps Global | 2020 - Present
- Managed 12 Kubernetes clusters (EKS) spanning 400+ node instances using ArgoCD and Helm.
- Engineered automated disaster recovery playbook with sub-5-minute RTO.

SKILLS
Kubernetes, Docker, Terraform, AWS, Ansible, Prometheus, Grafana, Python, Bash
"""
    },
    "product_manager": {
        "title": "Product Manager (B2B SaaS)",
        "content": """
Michael Zhang
New York, NY | michael.zhang@example.com

SUMMARY
Product Manager with 5 years launching developer tools and API platforms from 0-to-1.

EXPERIENCE
Senior PM | DevTools SaaS | 2021 - Present
- Owned roadmap for developer API products, growing ARR from $1.5M to $6.8M in 24 months.
- Led cross-functional squad of 12 software engineers and designers.

SKILLS
Product Strategy, User Research, Agile/Scrum, Wireframing, SQL, Mixpanel, Roadmapping
"""
    },
    "mechanical_engineer": {
        "title": "Mechanical Engineer",
        "content": """
James Wilson
Detroit, MI | james.wilson@example.com

SUMMARY
Mechanical Engineer with 4 years designing precision automotive components, SolidWorks 3D models, and GD&T tolerance stacks.

EXPERIENCE
Mechanical Design Engineer | AutoDrive Components | 2022 - Present
- Designed thermal management enclosures using SolidWorks and Ansys FEA.
- Reduced component manufacturing defect rate by 22% through strict GD&T audits.

SKILLS
SolidWorks, AutoCAD, Ansys FEA, GD&T, DFM/DFA, CNC Machining, Thermal Analysis
"""
    },
    "civil_engineer": {
        "title": "Civil Structural Engineer",
        "content": """
Anita Patel
Houston, TX | anita.patel@example.com

SUMMARY
Civil Engineer with 3 years managing commercial structural analysis, AutoCAD blueprints, and site safety compliance.

EXPERIENCE
Structural Engineer | Landmark Infrastructure | 2022 - Present
- Conducted structural load calculations for 14-story commercial building projects.
- Supervised on-site concrete foundation pours and steel frame inspections.

SKILLS
AutoCAD, STAAD.Pro, Revit, Structural Load Analysis, Site Inspection, Building Codes
"""
    },
    "electrical_engineer": {
        "title": "Electrical Engineer",
        "content": """
Karthik Nair
San Jose, CA | karthik.nair@example.com

SUMMARY
Electrical Hardware Engineer with 4 years designing PCB schematics, microcontrollers, and FPGA firmware.

EXPERIENCE
Embedded Systems Engineer | PowerTech Devices | 2021 - Present
- Designed 6-layer high-speed PCB layouts using Altium Designer.
- Developed C/C++ firmware for ARM Cortex-M microcontrollers.

SKILLS
Altium Designer, C/C++, Embedded Systems, FPGA, Oscilloscopes, SPI/I2C/UART
"""
    },
    "fresh_graduate": {
        "title": "Fresh Graduate (Entry Level CS)",
        "content": """
Emily Watson
Boston, MA | emily.watson@example.com

SUMMARY
Recent B.S. Computer Science graduate with strong academic foundation in algorithms, data structures, and Web development.

EDUCATION
B.S. Computer Science | Northeastern University | Graduated May 2026 (GPA: 3.8/4.0)

PROJECTS
Smart Career Dashboard (Capstone)
- Built full-stack React and Python FastAPI app for job tracking.

SKILLS
Python, Java, C++, React, Git, HTML/CSS, Data Structures & Algorithms
"""
    },
    "career_switcher": {
        "title": "Career Switcher (Sales to Data Analyst)",
        "content": """
Jordan Lee
Atlanta, GA | jordan.lee@example.com

SUMMARY
Former Senior Account Manager transitioning into Data Analytics after completing intensive 6-month Data Engineering Bootcamp.

EXPERIENCE
Sales Account Manager | SaaS Tech | 2020 - 2025
- Managed enterprise client portfolio generating $2.4M in annual revenue.

Data Analytics Capstone Project | 2026
- Built SQL revenue forecasting dashboard using Python, Pandas, and PostgreSQL.

SKILLS
SQL, Python, Pandas, Excel, Tableau, Client Communication, Business Intelligence
"""
    },
    "employment_gap": {
        "title": "Senior Engineer (2-Year Sabbatical)",
        "content": """
Rachel Green
Austin, TX | rachel.green@example.com

SUMMARY
Senior Software Engineer with 7 years of software development experience returning to engineering after 2-year family sabbatical.

EXPERIENCE
Senior Software Engineer | Enterprise Cloud Inc | 2017 - 2024
- Built distributed microservices in Java Spring Boot and PostgreSQL.
- Mentored junior engineers and conducted technical interviews.

Sabbatical / Continuous Learning | 2024 - 2026
- Upskilled in Python 3.12, local AI LLM orchestration, and modern React 19 architecture.

SKILLS
Java, Spring Boot, Python, PostgreSQL, REST APIs, Microservices, Git
"""
    },
    "weak_resume": {
        "title": "Candidate with Weak Resume Format",
        "content": """
John Doe
Email: john@test.com | Phone: 555-0199

Job History:
Worked at Company X (2022-2024)
- Was responsible for writing code.
- Fixed bugs in website.
- Helped team members with tasks.

Worked at Company Y (2020-2022)
- Handled daily duties.
- Attended team meetings.

Skills:
Computers, Coding, Python, HTML
"""
    },
    "highly_optimized_resume": {
        "title": "Highly Optimized Staff Engineer Resume",
        "content": """
Pratap Aditya
San Francisco, CA | pratap@example.com | github.com/pratap-dev

SUMMARY
Staff Frontend Architect with 8+ years designing high-throughput developer platforms, local-first client sync engines, and WebGL canvases. Reduced Time-to-Interactive by 42% across 12M monthly active users while saving $180,000 in compute costs.

EXPERIENCE
Staff Frontend Architect | Veloce Cloud Platform | 2022 - Present
- Architected modular edge-rendered micro-frontend platform serving 12M MAU.
- Reduced p99 bundle size by 64% using fine-grained AST tree-shaking and Vite plugins.
- Authored automated accessibility CI test suite enforcing 100% WCAG 2.1 AA compliance.

Senior Systems Engineer | Apex Data Labs | 2018 - 2022
- Engineered high-density WebGL streaming table rendering 500,000 live rows at 60 FPS.
- Rebuilt real-time CRDT sync engine with Web Workers and shared ArrayBuffers.

SKILLS
TypeScript, React 19, WebGL, Rust, WASM, Web Workers, Vite, Core Web Vitals, Local-First AI, Micro-Frontends
"""
    }
}

JDS = {
    "jd_01_software_engineer": "We are seeking a Software Engineer proficient in JavaScript, TypeScript, React, and Node.js to build scalable web platforms.",
    "jd_02_backend_engineer": "Senior Backend Engineer needed to architect distributed Go/Python microservices, Kafka event streams, and gRPC endpoints under high concurrency.",
    "jd_03_frontend_engineer": "Frontend Engineer required to optimize Core Web Vitals, implement React component libraries, and drive Web accessibility standards.",
    "jd_04_fullstack_engineer": "Full Stack Engineer wanted to build Python FastAPI backends and React TypeScript frontends with PostgreSQL data persistence.",
    "jd_05_data_analyst": "Seeking Data Analyst skilled in SQL, PostgreSQL, Tableau, Python Pandas, and executive BI reporting.",
    "jd_06_data_scientist": "Data Scientist position requiring PyTorch, NLP transformer models, feature engineering, and statistical MLOps pipelines.",
    "jd_07_devops_engineer": "DevOps Engineer required to manage AWS Kubernetes EKS clusters, Terraform infrastructure-as-code, and ArgoCD CI/CD pipelines.",
    "jd_08_security_engineer": "Cybersecurity Analyst needed to manage Splunk SIEM alerts, incident response playbooks, and vulnerability assessments.",
    "jd_09_product_manager": "Product Manager wanted to lead B2B SaaS developer tools, execute product roadmaps, and define key telemetry metrics.",
    "jd_10_mechanical_engineer": "Mechanical Engineer required for SolidWorks 3D modeling, GD&T tolerance stacks, and Ansys FEA thermal analysis.",
    "jd_11_graduate_trainee": "Graduate Engineer Trainee program looking for fresh CS graduates with strong Data Structures, Python/Java fundamentals, and eagerness to learn.",
    "jd_12_engineering_manager": "Engineering Manager needed to lead 12+ software engineers, manage agile delivery, and drive architectural standards.",
    "jd_13_cloud_architect": "Cloud Architect required to design multi-region AWS infrastructure, zero-trust security topologies, and cost-optimization strategies.",
    "jd_14_site_reliability_engineer": "SRE Engineer wanted to manage 99.999% uptime SLAs, Prometheus/Grafana monitoring, and incident post-mortems.",
    "jd_15_embedded_systems_engineer": "Embedded Engineer required for C/C++ firmware, ARM Cortex microcontrollers, Altium PCB schematics, and hardware debugging.",
    "jd_16_civil_structural_engineer": "Civil Engineer needed for AutoCAD structural blueprints, STAAD load calculations, and site safety compliance.",
    "jd_17_qa_automation_engineer": "QA Automation Engineer skilled in Playwright, Cypress, Python pytest, and CI/CD test orchestration.",
    "jd_18_ml_ops_engineer": "MLOps Engineer required to deploy PyTorch models on Kubernetes GPUs with Triton Inference Server and MLflow tracking.",
    "jd_19_technical_writer": "Technical Writer needed to author API developer documentation, OpenAPI specs, and developer onboarding guides.",
    "jd_20_solutions_architect": "Solutions Architect required to design enterprise SaaS integration architectures, security controls, and technical proposals."
}

def generate():
    for name, data in PROFILES.items():
        p_dir = os.path.join(PROFILES_DIR, name)
        os.makedirs(p_dir, exist_ok=True)
        
        # Write raw_resume.txt
        txt_path = os.path.join(p_dir, "raw_resume.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(data["content"].strip())
            
        # Write job_description.txt matching closest
        jd_match = JDS.get(f"jd_{name}", JDS["jd_01_software_engineer"])
        with open(os.path.join(p_dir, "job_description.txt"), "w", encoding="utf-8") as f:
            f.write(jd_match.strip())

    for jd_name, jd_content in JDS.items():
        with open(os.path.join(JDS_DIR, f"{jd_name}.txt"), "w", encoding="utf-8") as f:
            f.write(jd_content.strip())

    print(f"Dataset generated: {len(PROFILES)} candidate profiles, {len(JDS)} job descriptions.")

if __name__ == "__main__":
    generate()
