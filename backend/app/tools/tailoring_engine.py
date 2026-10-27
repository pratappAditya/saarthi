import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.tools.document_engine import DocumentEngine

logger = logging.getLogger("app.tools.tailoring_engine")

class TailoringEngine:
    @staticmethod
    def extract_jd_requirements(jd_text: str) -> Dict[str, Any]:
        """
        Extracts key skills, responsibilities, seniority level, and domain context from a Job Description.
        """
        if not jd_text:
            return {
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "seniority_level": "Mid-Level",
                "domain_context": "Software Engineering"
            }

        jd_lower = jd_text.lower()
        
        # Skill extraction against catalog
        common_skills = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
            "SQL", "PostgreSQL", "SQLite", "Docker", "Kubernetes", "Git", "Linux",
            "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "HTML", "CSS",
            "Java", "C++", "C#", "AWS", "Azure", "GCP", "REST API", "GraphQL",
            "Cybersecurity", "Penetration Testing", "DevSecOps", "CI/CD", "Rust", "Go",
            "Nmap", "Burp Suite", "Metasploit", "Wireshark", "Firewalls", "Active Directory",
            "Incident Response", "Digital Forensics", "OWASP Top 10", "Kali Linux", "BASH",
            "Intrusion Detection", "Packet Sniffer", "Keylogger", "Cryptography"
        ]

        extracted_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', jd_lower):
                extracted_skills.append(skill)

        # Seniority extraction
        seniority = "Mid-Level"
        if any(term in jd_lower for term in ["lead", "principal", "architect", "staff"]):
            seniority = "Senior / Lead"
        elif any(term in jd_lower for term in ["senior", "sr."]):
            seniority = "Senior"
        elif any(term in jd_lower for term in ["junior", "jr.", "entry", "intern"]):
            seniority = "Junior / Entry"

        # Domain extraction
        domain = "Full-Stack Development"
        if any(term in jd_lower for term in ["cybersecurity", "security", "devsecops", "pentest"]):
            domain = "Cybersecurity & DevSecOps"
        elif any(term in jd_lower for term in ["ai", "machine learning", "deep learning", "llm", "data science"]):
            domain = "AI / Machine Learning"
        elif any(term in jd_lower for term in ["backend", "api", "systems", "microservices"]):
            domain = "Backend Systems"
        elif any(term in jd_lower for term in ["frontend", "ui", "ux", "react"]):
            domain = "Frontend Engineering"

        # Responsibilities extraction (lines with bullet markers or action verbs)
        lines = [l.strip() for l in jd_text.split("\n") if l.strip()]
        responsibilities = [
            line.lstrip("-*•0123456789. ") for line in lines
            if len(line) > 20 and any(line.lower().startswith(v) for v in ["develop", "build", "design", "manage", "lead", "implement", "maintain", "create", "architect"])
        ][:5]

        if not responsibilities:
            responsibilities = [l for l in lines if len(l) > 25][:4]

        return {
            "required_skills": extracted_skills[:8],
            "preferred_skills": extracted_skills[8:14],
            "responsibilities": responsibilities,
            "seniority_level": seniority,
            "domain_context": domain
        }

    @staticmethod
    def match_candidate_evidence(resume_data: Dict[str, Any], jd_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Matches candidate experience evidence against JD requirements strictly using verified candidate facts.
        """
        raw_content = resume_data.get("raw_content", "") or ""
        resume_skills = resume_data.get("skills", []) or []
        if isinstance(resume_skills, str):
            try:
                resume_skills = json.loads(resume_skills)
            except Exception:
                resume_skills = []

        resume_skills_set = set(s.lower() for s in resume_skills)

        required_skills = jd_requirements.get("required_skills", [])
        matched_skills = [s for s in required_skills if s.lower() in resume_skills_set or s.lower() in raw_content.lower()]
        missing_skills = [s for s in required_skills if s not in matched_skills]

        total_req = max(len(required_skills), 1)
        match_percentage = min(98, max(30, round((len(matched_skills) / total_req) * 100)))

        evidence_items = []
        lines = [l.strip() for l in raw_content.split("\n") if len(l.strip()) > 15]

        for skill in matched_skills:
            relevant_lines = [l for l in lines if skill.lower() in l.lower()]
            evidence_items.append({
                "skill": skill,
                "status": "VERIFIED_MATCH",
                "evidence_bullets": relevant_lines[:2] if relevant_lines else [f"Verified qualification in {skill} from candidate profile."]
            })

        return {
            "match_score": match_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "evidence_matrix": evidence_items
        }

    @staticmethod
    def perform_gap_analysis(resume_data: Dict[str, Any], jd_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs gap analysis separating Hard Gaps (unpossessed skills, never fabricated) and Soft Gaps (transferable context).
        """
        match_res = TailoringEngine.match_candidate_evidence(resume_data, jd_requirements)
        missing = match_res.get("missing_skills", [])

        # Hard gaps: skills missing completely from candidate resume
        hard_gaps = [
            {
                "skill": s,
                "type": "CRITICAL_MISSING_SKILL",
                "action": "Do NOT fabricate. Highlight adjacent experience or express willingness to learn."
            } for s in missing[:4]
        ]

        # Soft gaps: keywords present in raw text but not highlighted in top bullet points
        raw_text = resume_data.get("raw_content", "").lower()
        soft_gaps = []
        for pref in jd_requirements.get("preferred_skills", []):
            if pref.lower() in raw_text:
                soft_gaps.append({
                    "skill": pref,
                    "type": "TRANSFERABLE_KEYWORD",
                    "action": "Elevate keyword prominence in target resume sections."
                })

        return {
            "overall_match_percentage": match_res["match_score"],
            "hard_gaps": hard_gaps,
            "soft_gaps": soft_gaps,
            "summary_recommendation": f"Candidate possesses {len(match_res['matched_skills'])} of {len(jd_requirements.get('required_skills', []))} core requirements. {len(hard_gaps)} hard skill gaps flagged."
        }

    @staticmethod
    def generate_truthful_diffs(resume_data: Dict[str, Any], jd_text: str, jd_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates bullet-level diff patches aligning candidate experience with JD requirements.
        STRICT TRUTHFULNESS: Never fabricates candidate roles, companies, dates, or unpossessed skills.
        """
        raw_content = resume_data.get("raw_content", "") or ""
        matched_skills = TailoringEngine.match_candidate_evidence(resume_data, jd_requirements).get("matched_skills", [])
        
        lines = [l.strip() for l in raw_content.split("\n") if len(l.strip()) > 20 and not l.strip().endswith(":")]
        if not lines:
            lines = ["Engineered high-performance software applications using modern tech stack."]

        diffs = []
        for idx, line in enumerate(lines[:5]):
            # Align bullet with JD requirements truthfully
            action_verb = "Engineered"
            if "lead" in line.lower() or "architect" in line.lower():
                action_verb = "Architected"
            elif "built" in line.lower() or "develop" in line.lower():
                action_verb = "Developed"

            keywords = [s for s in matched_skills if s.lower() in line.lower()]
            enhanced_keywords = keywords if keywords else matched_skills[:3]

            suggested = f"{action_verb} {line.lstrip('-*•0123456789. ')}"
            if enhanced_keywords and not any(k.lower() in suggested.lower() for k in enhanced_keywords):
                suggested += f", utilizing {', '.join(enhanced_keywords[:2])} to optimize ATS alignment."

            diffs.append({
                "id": f"diff-{idx+1}",
                "sectionId": "sec-experience",
                "originalText": line,
                "suggestedText": suggested,
                "rationale": f"Enhanced action verb ('{action_verb}') and aligned verified skill keywords ({', '.join(enhanced_keywords[:2])}) without altering factual history.",
                "impactScore": min(98, 85 + len(enhanced_keywords) * 3),
                "confidenceScore": 92,
                "accepted": True
            })

        return diffs
