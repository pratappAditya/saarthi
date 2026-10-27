"""
Saarthi Watermark Engine
Subtle, professional watermarking for Free-tier generated documents.
"""

from typing import Optional
from app.licensing.models import Entitlements

import hashlib

DEFAULT_WATERMARK_TEXT = "Created with Saarthi • saarthi.ai"

WATERMARK_EXPERIMENTS = {
    "CONTROL": {
        "text": "Created with Saarthi • saarthi.ai",
        "message": "You're using Saarthi Free. Upgrade to remove the Saarthi watermark and unlock unlimited career tools."
    },
    "VARIANT_A": {
        "text": "Created with Saarthi",
        "message": "Remove this watermark with Saarthi Student — ₹149/month."
    },
    "VARIANT_B": {
        "text": "Created with Saarthi",
        "message": "Your resume is ready. Export it without the Saarthi watermark for ₹149/month."
    },
    "VARIANT_C": {
        "text": "Created with Saarthi",
        "message": "Apply professionally with a watermark-free resume. Saarthi Student — ₹149/month."
    }
}

class WatermarkEngine:
    """
    Applies subtle, non-intrusive watermarking to Saarthi-generated career documents
    (tailored resumes, generated cover letters) ONLY for Free-tier users.
    
    Guarantees:
    1. Does NOT obscure contact information, body text, ATS keywords, or headers.
    2. Does NOT modify the user's original uploaded files or source resume facts.
    3. Excludes email drafts, calendar events, application tracker, and chat logs.
    4. Seamlessly strips watermarks for paid users on re-export without AI re-generation.
    """
    
    @staticmethod
    def get_experiment_variant(user_id: str = "default_user") -> str:
        """Deterministically assigns experiment variant based on user identifier hash."""
        h = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
        val = int(h, 16) % 4
        variants = ["CONTROL", "VARIANT_A", "VARIANT_B", "VARIANT_C"]
        return variants[val]

    @staticmethod
    def get_pricing_experiment_variant(user_id: str = "default_user") -> str:
        """Deterministically assigns Student pricing experiment variant (149 Control vs 100 Treatment)."""
        h = hashlib.sha256((user_id + "_pricing").encode("utf-8")).hexdigest()
        val = int(h, 16) % 2
        variants = ["STUDENT_CONTROL_149", "STUDENT_TREATMENT_100"]
        return variants[val]

    @staticmethod
    def get_experiment_data(variant_key: str) -> dict:
        return WATERMARK_EXPERIMENTS.get(variant_key, WATERMARK_EXPERIMENTS["CONTROL"])

    @staticmethod
    def strip_watermark(content: str) -> str:
        """
        Strips any previously injected watermark footers or HTML divs
        from markdown or HTML content for clean paid user re-exports.
        """
        if not content:
            return content

        # Strip Markdown watermark footers
        lines = content.splitlines()
        clean_lines = []
        skip_mode = False
        for line in lines:
            if line.strip() == "---":
                # Check if next line contains watermark text
                skip_mode = True
                continue
            if skip_mode and ("Created with Saarthi" in line or "saarthi.ai" in line or "Saarthi Student" in line):
                continue
            skip_mode = False
            clean_lines.append(line)

        clean_md = "\n".join(clean_lines).rstrip()

        # Strip HTML watermark divs
        if "<div style=\"margin-top: 30px;" in clean_md:
            start_idx = clean_md.find("<div style=\"margin-top: 30px;")
            end_idx = clean_md.find("</div>", start_idx)
            if start_idx != -1 and end_idx != -1:
                clean_md = clean_md[:start_idx] + clean_md[end_idx + 6:]

        return clean_md.rstrip()

    @staticmethod
    def watermark_markdown(
        content: str,
        entitlements: Optional[Entitlements] = None,
        watermark_text: str = DEFAULT_WATERMARK_TEXT
    ) -> str:
        """
        Applies watermark to markdown documents if required by plan entitlement.
        If plan does NOT require watermark, strips any existing watermark footer cleanly.
        """
        if not entitlements or not getattr(entitlements, "requires_watermark", True):
            return WatermarkEngine.strip_watermark(content)
            
        # Avoid duplicate watermark if already present
        if watermark_text in content or "Created with Saarthi" in content:
            return content
            
        watermark_footer = f"\n\n---\n* {watermark_text} *\n"
        return content + watermark_footer

    @staticmethod
    def watermark_html(
        html_content: str,
        entitlements: Optional[Entitlements] = None,
        watermark_text: str = DEFAULT_WATERMARK_TEXT
    ) -> str:
        """
        Applies watermark to HTML document exports.
        If plan does NOT require watermark, strips any existing watermark div cleanly.
        """
        if not entitlements or not getattr(entitlements, "requires_watermark", True):
            return WatermarkEngine.strip_watermark(html_content)
            
        if watermark_text in html_content or "Created with Saarthi" in html_content:
            return html_content
            
        watermark_div = f"""
<div style="margin-top: 30px; padding-top: 10px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 10px; color: #94a3b8; font-family: sans-serif;">
  {watermark_text}
</div>
"""
        if "</body>" in html_content:
            return html_content.replace("</body>", f"{watermark_div}\n</body>")
        return html_content + watermark_div

WatermarkService = WatermarkEngine

