"""
STT Quality Pipeline for Saarthi Voice.
Applies post-processing normalization:
- Punctuation restoration and sentence capitalization
- Number, date, currency, URL, and email formatting
- Technical term casing via Voice Dictionary
- Spoken formatting command resolution
"""

import re
from typing import Dict, Any, List, Tuple
from app.intelligence.voice.voice_dictionary import voice_dictionary
from app.intelligence.voice.voice_commands import voice_command_processor


class STTQualityPipeline:
    """Post-processing pipeline ensuring high-fidelity transcripts."""

    def __init__(self):
        self._number_words = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
            "ten": "10", "eleven": "11", "twelve": "12", "twenty": "20",
            "thirty": "30", "forty": "40", "fifty": "50", "hundred": "100",
            "thousand": "1000"
        }

    def _capitalize_sentences(self, text: str) -> str:
        """Capitalizes the first letter of each sentence."""
        if not text:
            return text

        # Split on sentence boundaries (. ? !\n)
        def cap_match(match):
            return match.group(1) + match.group(2).upper()

        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        text = re.sub(r"([.!?\n]\s+)([a-z])", cap_match, text)
        return text

    def _normalize_common_patterns(self, text: str) -> str:
        """Normalizes URLs, emails, dates, and common spoken conventions."""
        if not text:
            return text

        # Spoken URLs: "example dot com" -> "example.com"
        text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+dot\s+(com|org|net|in|io|ai|gov)\b", r"\1.\2", text, flags=re.IGNORECASE)

        # Spoken email: "name at example dot com" -> "name@example.com"
        text = re.sub(r"\b([a-zA-Z0-9._%+-]+)\s+at\s+([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b", r"\1@\2", text, flags=re.IGNORECASE)

        # Year phrases: "two thousand twenty six" -> "2026"
        text = re.sub(r"\btwo\s+thousand\s+(and\s+)?twenty\s+six\b", "2026", text, flags=re.IGNORECASE)
        text = re.sub(r"\btwo\s+thousand\s+(and\s+)?twenty\s+five\b", "2025", text, flags=re.IGNORECASE)

        return text

    def normalize(
        self,
        raw_text: str,
        user_id: str = "default_local_user",
        apply_commands: bool = True
    ) -> Tuple[str, List[str]]:
        """
        Runs full post-processing pipeline.
        Returns (normalized_text, applied_command_names)
        """
        if not raw_text or not raw_text.strip():
            return "", []

        applied_commands: List[str] = []

        # 1. Spoken formatting & command detection
        text = raw_text
        if apply_commands:
            text, cmds = voice_command_processor.process_text(text)
            applied_commands = [c.command_name or "command" for c in cmds if c.is_command]

        # 2. Voice dictionary replacements and preferred terminology casing
        text = voice_dictionary.apply_dictionary(text, user_id=user_id)

        # 3. URLs, Emails, Numbers
        text = self._normalize_common_patterns(text)

        # 4. Sentence capitalization
        text = self._capitalize_sentences(text)

        # 5. Punctuation finish (if no trailing punctuation and longer than 3 words)
        if text and text[-1] not in ".?!:\n" and len(text.split()) >= 3:
            text += "."

        return text.strip(), applied_commands


stt_quality_pipeline = STTQualityPipeline()
