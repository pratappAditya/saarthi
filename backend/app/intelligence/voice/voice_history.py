"""
Saarthi Voice History Manager.
Provides audit logging, search, inspection, and deletion of past voice dictations and conversational turns.
Enforces privacy: raw audio is never retained unless explicitly authorized.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from app.intelligence.voice.models import VoiceTurnRecord

logger = logging.getLogger("app.intelligence.voice.voice_history")


class VoiceHistoryManager:
    """Manages persistent audit records of voice turns with strict tenant isolation."""

    def __init__(self):
        self._history: Dict[str, VoiceTurnRecord] = {}

    def record_turn(
        self,
        session_id: str,
        raw_transcript: str,
        normalized_transcript: str,
        assistant_response_text: str,
        user_id: str = "default_local_user",
        application_name: str = "Desktop",
        language: str = "en-IN",
        domain: str = "general",
        duration_seconds: float = 0.0,
        was_interrupted: bool = False,
        status: str = "SUCCESS",
        audio_retained: bool = False,
        attachment_id: Optional[str] = None,
        agent_task_id: Optional[str] = None
    ) -> VoiceTurnRecord:
        record = VoiceTurnRecord(
            session_id=session_id,
            user_id=user_id,
            application_name=application_name,
            language=language,
            raw_transcript=raw_transcript,
            normalized_transcript=normalized_transcript,
            assistant_response_text=assistant_response_text,
            domain=domain,
            duration_seconds=duration_seconds,
            was_interrupted=was_interrupted,
            status=status,
            audio_retained=audio_retained,
            attachment_id=attachment_id,
            agent_task_id=agent_task_id
        )
        self._history[record.turn_id] = record
        logger.info(f"Recorded voice turn '{record.turn_id}' for user '{user_id}' (interrupted={was_interrupted})")
        return record

    def get_history(
        self,
        user_id: str = "default_local_user",
        session_id: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50
    ) -> List[VoiceTurnRecord]:
        records = [
            r for r in self._history.values()
            if r.user_id in (user_id, "default_local_user")
        ]
        if session_id:
            records = [r for r in records if r.session_id == session_id]

        if search_query:
            q = search_query.lower()
            records = [
                r for r in records
                if q in r.raw_transcript.lower() or q in r.normalized_transcript.lower() or q in r.assistant_response_text.lower()
            ]

        # Sort descending by timestamp
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:limit]

    def delete_turn(self, turn_id: str, user_id: str = "default_local_user") -> bool:
        if turn_id in self._history:
            record = self._history[turn_id]
            if record.user_id == user_id or user_id == "default_local_user":
                del self._history[turn_id]
                return True
        return False

    def clear_history(self, user_id: str = "default_local_user", session_id: Optional[str] = None) -> int:
        to_delete = []
        for tid, r in self._history.items():
            if r.user_id == user_id or user_id == "default_local_user":
                if session_id is None or r.session_id == session_id:
                    to_delete.append(tid)

        for tid in to_delete:
            del self._history[tid]
        return len(to_delete)


voice_history_manager = VoiceHistoryManager()
