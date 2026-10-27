"""
Saarthi Spoken Voice Commands Processor.
Parses conversational interaction primitives, formatting commands,
editing directives, and speech-driven system actions.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class ParsedVoiceCommand(BaseModel):
    is_command: bool = False
    command_type: Optional[str] = None  # formatting, editing, transform, action
    command_name: Optional[str] = None
    remaining_text: str = ""
    applied_formatting: Optional[str] = None
    requires_approval: bool = False


class VoiceCommandProcessor:
    """Interprets and processes spoken command primitives."""

    # Formatting substitutions
    FORMATTING_RULES = [
        (re.compile(r"\bnew\s+paragraph\b", re.IGNORECASE), "\n\n"),
        (re.compile(r"\bnew\s+line\b", re.IGNORECASE), "\n"),
        (re.compile(r"\bbullet\s+point\b|\bbullet\b", re.IGNORECASE), "\n• "),
        (re.compile(r"\bnumbered\s+list\b", re.IGNORECASE), "\n1. ")
    ]

    # Action command patterns
    ACTION_PATTERNS = {
        "undo": re.compile(r"^\s*(undo|undo that)\s*$", re.IGNORECASE),
        "redo": re.compile(r"^\s*(redo|redo that)\s*$", re.IGNORECASE),
        "delete_that": re.compile(r"^\s*(delete that|clear that|scratch that)\s*$", re.IGNORECASE),
        "rewrite_that": re.compile(r"^\s*(rewrite that|rewrite this)\s*$", re.IGNORECASE),
        "make_formal": re.compile(r"^\s*(make it formal|make this formal|rewrite formal)\s*$", re.IGNORECASE),
        "make_shorter": re.compile(r"^\s*(make it shorter|shorten this|summarize this)\s*$", re.IGNORECASE),
        "translate_hindi": re.compile(r"^\s*(translate to hindi|hindi mein bolo|explain in hindi)\s*$", re.IGNORECASE),
        "translate_english": re.compile(r"^\s*(translate to english|english mein bolo|explain in english)\s*$", re.IGNORECASE),
        "send": re.compile(r"^\s*(send it|send message|submit)\s*$", re.IGNORECASE),
        "stop": re.compile(r"^\s*(stop|pause|halt)\s*$", re.IGNORECASE),
        "cancel": re.compile(r"^\s*(cancel|cancel that|abort)\s*$", re.IGNORECASE)
    }

    def process_text(self, text: str) -> Tuple[str, List[ParsedVoiceCommand]]:
        """
        Parses text for embedded formatting primitives and dedicated action commands.
        Returns: (transformed_text, list_of_commands)
        """
        if not text:
            return "", []

        commands: List[ParsedVoiceCommand] = []

        # Check pure action commands first
        clean_stripped = text.strip()
        for cmd_name, pattern in self.ACTION_PATTERNS.items():
            if pattern.match(clean_stripped):
                req_app = cmd_name in ("send", "delete_that")
                cmd = ParsedVoiceCommand(
                    is_command=True,
                    command_type="action",
                    command_name=cmd_name,
                    remaining_text="",
                    requires_approval=req_app
                )
                commands.append(cmd)
                return "", commands

        # Apply inline formatting replacements
        modified_text = text
        for pattern, replacement in self.FORMATTING_RULES:
            if pattern.search(modified_text):
                modified_text = pattern.sub(replacement, modified_text)
                commands.append(ParsedVoiceCommand(
                    is_command=True,
                    command_type="formatting",
                    command_name=replacement.strip() or "newline",
                    remaining_text=modified_text,
                    applied_formatting=replacement
                ))

        return modified_text.strip(), commands


voice_command_processor = VoiceCommandProcessor()
