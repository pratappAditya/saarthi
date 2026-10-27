"""
Saarthi Voice Dictionary Manager.
Allows users to define custom terminology, preferred spellings,
pronunciation hints, and replacement rules applied during STT post-processing.
"""

import re
import json
import os
import logging
from typing import Dict, Any, List, Optional
from app.intelligence.voice.models import VoiceDictionaryEntry

logger = logging.getLogger("app.intelligence.voice.voice_dictionary")


class VoiceDictionaryManager:
    """Manages custom vocabulary, preferred casing, and domain replacements."""

    def __init__(self, storage_path: str = "voice_dictionary.json"):
        self.storage_path = storage_path
        self._entries: Dict[str, VoiceDictionaryEntry] = {}
        self._load_defaults()

    def _load_defaults(self):
        # Default domain vocabulary
        defaults = [
            VoiceDictionaryEntry(word="postgresql", preferred_spelling="PostgreSQL", domain="software"),
            VoiceDictionaryEntry(word="postgres", preferred_spelling="Postgres", domain="software"),
            VoiceDictionaryEntry(word="saarthi", preferred_spelling="Saarthi", domain="general"),
            VoiceDictionaryEntry(word="sarathi", preferred_spelling="Saarthi", replacement="Saarthi", domain="general"),
            VoiceDictionaryEntry(word="sarthi", preferred_spelling="Saarthi", replacement="Saarthi", domain="general"),
            VoiceDictionaryEntry(word="pratap", preferred_spelling="Pratap", domain="general"),
            VoiceDictionaryEntry(word="fastapi", preferred_spelling="FastAPI", domain="software"),
            VoiceDictionaryEntry(word="vscode", preferred_spelling="VS Code", replacement="VS Code", domain="software"),
            VoiceDictionaryEntry(word="github", preferred_spelling="GitHub", domain="software"),
            VoiceDictionaryEntry(word="pydantic", preferred_spelling="Pydantic", domain="software"),
            VoiceDictionaryEntry(word="trovane", preferred_spelling="Trovane", domain="business")
        ]
        for d in defaults:
            self._entries[d.id] = d

    def add_entry(
        self,
        word: str,
        preferred_spelling: str,
        user_id: str = "default_local_user",
        pronunciation_hint: Optional[str] = None,
        replacement: Optional[str] = None,
        domain: Optional[str] = "general"
    ) -> VoiceDictionaryEntry:
        entry = VoiceDictionaryEntry(
            user_id=user_id,
            word=word.strip().lower(),
            preferred_spelling=preferred_spelling.strip(),
            pronunciation_hint=pronunciation_hint,
            replacement=replacement or preferred_spelling.strip(),
            domain=domain or "general"
        )
        self._entries[entry.id] = entry
        logger.info(f"Added voice dictionary entry: '{word}' -> '{preferred_spelling}'")
        return entry

    def list_entries(self, user_id: str = "default_local_user") -> List[VoiceDictionaryEntry]:
        return [e for e in self._entries.values() if e.user_id in (user_id, "default_local_user")]

    def delete_entry(self, entry_id: str, user_id: str = "default_local_user") -> bool:
        if entry_id in self._entries:
            entry = self._entries[entry_id]
            if entry.user_id == user_id or user_id == "default_local_user":
                del self._entries[entry_id]
                return True
        return False

    def apply_dictionary(self, text: str, user_id: str = "default_local_user") -> str:
        """Applies user voice dictionary replacements and casing corrections."""
        if not text:
            return text

        normalized = text
        relevant_entries = [e for e in self._entries.values() if e.user_id in (user_id, "default_local_user")]

        # Sort entries by length descending to replace longer phrases first
        relevant_entries.sort(key=lambda e: len(e.word), reverse=True)

        for entry in relevant_entries:
            target_word = entry.word
            replacement = entry.replacement or entry.preferred_spelling

            # Case-insensitive word boundary replacement
            pattern = re.compile(rf"\b{re.escape(target_word)}\b", re.IGNORECASE)
            normalized = pattern.sub(replacement, normalized)

        return normalized


voice_dictionary = VoiceDictionaryManager()
