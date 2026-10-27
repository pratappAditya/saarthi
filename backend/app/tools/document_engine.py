import os
import re
import json
from typing import Dict, Any, List, Optional
from app.licensing.watermark import WatermarkService

class DocumentEngine:
    @staticmethod
    def parse_document(file_path: str) -> Dict[str, Any]:
        """
        Parses PDF, DOCX, TXT, MD, or image files to extract text content, skills, and candidate profile details.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        raw_text = ""

        if ext in (".txt", ".md"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                raw_text = "\n".join(pages)
            except Exception as e:
                raw_text = f"[PDF Parsing Warning: Could not extract full text: {e}]"
        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(file_path)
                raw_text = "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                raw_text = f"[DOCX Parsing Warning: Could not extract full text: {e}]"
        elif ext in (".png", ".jpg", ".jpeg"):
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(file_path)
                raw_text = pytesseract.image_to_string(img)
            except Exception:
                raw_text = f"[OCR Notice: pytesseract / Tesseract binary not installed on host machine for {filename}]"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read(5000)

        # Clean raw text from any PDF/binary stream artifacts or control characters
        raw_text = DocumentEngine.clean_extracted_text(raw_text)

        # Structure Extraction
        extracted_skills = DocumentEngine._extract_skills(raw_text)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        phones = re.findall(r'\(?\+\d{1,3}\)?[-.\s]?\d{3,5}[-.\s]?\d{4,6}', raw_text)

        # Extract structured sections
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
        header_name = lines[0] if lines and len(lines[0]) < 40 and not any(k in lines[0].lower() for k in ["resume", "curriculum", "cv"]) else "Candidate Profile"
        summary = " ".join(lines[1:4]) if len(lines) > 1 else "Parsed candidate experience."

        sections = [
          {
            "id": "sec-1",
            "title": "Parsed Experience & Qualifications",
            "company": "Extracted Record",
            "period": "Recent",
            "bullets": [
              {
                "id": "b-1",
                "text": line,
                "originalText": line,
                "impactScore": 85,
                "highlightedKeywords": [s for s in extracted_skills if s.lower() in line.lower()]
              } for line in lines[2:8] if len(line) > 10
            ]
          }
        ]

        return {
            "filename": filename,
            "file_path": file_path,
            "raw_text": raw_text,
            "char_count": len(raw_text),
            "extracted_emails": list(set(emails)),
            "extracted_phones": list(set(phones)),
            "extracted_skills": extracted_skills,
            "extracted_name": header_name,
            "summary": summary,
            "sections": sections
        }

    @staticmethod
    def clean_extracted_text(text: str) -> str:
        if not text:
            return ""
        # Remove null bytes and unprintable control characters
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        # Remove PDF header and object markers (%PDF-1.7, 1 0 obj, << >>, endobj, stream, etc.)
        cleaned = re.sub(r'%PDF-\d\.\d', '', cleaned)
        cleaned = re.sub(r'\d+\s+\d+\s+obj\b', '', cleaned)
        cleaned = re.sub(r'/(Title|Producer|Creator|Author|CreationDate|ModDate|Keywords)\s*\(.*?\)', '', cleaned)
        cleaned = re.sub(r'<<.*?>>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'\b(endobj|obj|stream|endstream|xref|trailer|startxref)\b', '', cleaned)
        # Remove repeated non-ASCII replacement symbols
        cleaned = re.sub(r'[\uFFFD]{2,}', '', cleaned)
        # Collapse multi-spaces and trailing lines
        cleaned = "\n".join([line.strip() for line in cleaned.split("\n") if line.strip()])
        return cleaned.strip()

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        common_skills = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
            "SQL", "PostgreSQL", "SQLite", "Docker", "Kubernetes", "Git", "Linux",
            "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "HTML", "CSS",
            "Java", "C++", "C#", "AWS", "Azure", "GCP", "REST API", "GraphQL"
        ]
        found = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found.append(skill)
        return found

    @staticmethod
    def export_document(content: str, output_path: str, plan: str = "FREE", format_type: str = "txt") -> Dict[str, Any]:
        """
        Exports candidate resume or document cleanly to PDF, DOCX, or TXT formats.
        Applies Saarthi watermark for FREE tier accounts.
        Produces clean unwatermarked exports for paid tier accounts (STUDENT, PERSONAL, POWER).
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        is_paid = plan.upper() in ("STUDENT", "PERSONAL", "POWER")
        ext = format_type.lower()
        if not ext and "." in output_path:
            ext = output_path.rsplit(".", 1)[1].lower()

        clean_text = DocumentEngine.clean_extracted_text(content)

        if ext == "pdf" or output_path.endswith(".pdf"):
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

                doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                styles = getSampleStyleSheet()
                story = []

                if not is_paid:
                    story.append(Paragraph("<i>--- WATERMARKED EXPORT: GENERATED BY SAARTHI FREE TIER ---</i>", styles["Italic"]))
                    story.append(Spacer(1, 12))

                for line in clean_text.split("\n"):
                    line_str = line.strip()
                    if not line_str:
                        story.append(Spacer(1, 6))
                        continue

                    safe_line = line_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    if line_str.startswith("# "):
                        story.append(Paragraph(safe_line[2:], styles["Heading1"]))
                    elif line_str.startswith("## "):
                        story.append(Paragraph(safe_line[3:], styles["Heading2"]))
                    elif line_str.startswith("### "):
                        story.append(Paragraph(safe_line[4:], styles["Heading3"]))
                    elif line_str.startswith("- ") or line_str.startswith("* "):
                        story.append(Paragraph(f"• {safe_line[2:]}", styles["Normal"]))
                    else:
                        story.append(Paragraph(safe_line, styles["Normal"]))

                if not is_paid:
                    story.append(Spacer(1, 12))
                    story.append(Paragraph("<i>--- Upgrade to Student, Personal, or Power for clean unwatermarked exports ---</i>", styles["Italic"]))

                doc.build(story)
            except Exception as e:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)

        elif ext == "docx" or output_path.endswith(".docx"):
            try:
                import docx
                doc = docx.Document()
                if not is_paid:
                    doc.add_paragraph("--- WATERMARKED EXPORT: GENERATED BY SAARTHI FREE TIER ---")

                for line in clean_text.split("\n"):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    if line_str.startswith("# "):
                        doc.add_heading(line_str[2:], level=1)
                    elif line_str.startswith("## "):
                        doc.add_heading(line_str[3:], level=2)
                    elif line_str.startswith("### "):
                        doc.add_heading(line_str[4:], level=3)
                    elif line_str.startswith("- ") or line_str.startswith("* "):
                        doc.add_paragraph(line_str[2:], style="List Bullet")
                    else:
                        doc.add_paragraph(line_str)

                if not is_paid:
                    doc.add_paragraph("--- Upgrade to Student, Personal, or Power for clean unwatermarked exports ---")

                doc.save(output_path)
            except Exception as e:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)
        else:
            final_content = clean_text
            if not is_paid:
                watermark_header = "--- WATERMARKED EXPORT: GENERATED BY SAARTHI FREE TIER ---\n\n"
                watermark_footer = "\n\n--- Upgrade to Student, Personal, or Power for clean unwatermarked exports ---"
                final_content = watermark_header + clean_text + watermark_footer

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)

        return {
            "status": "success",
            "file_path": output_path,
            "plan": plan,
            "is_watermarked": not is_paid,
            "clean_export": is_paid
        }
