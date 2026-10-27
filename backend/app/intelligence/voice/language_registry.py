"""
Language Registry for Saarthi Voice.
Provides extensible catalog of supported languages, code-switching profiles,
default neural voice mappings, and STT language targets.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.intelligence.voice.models import VoiceLanguageCode


class LanguageProfile(BaseModel):
    code: str
    name: str
    script: str
    locale: str
    edge_tts_male_voice: str
    edge_tts_female_voice: str
    stt_target_locale: str
    is_active: bool = True
    supports_code_switching: bool = False


class LanguageRegistry:
    """Central registry of voice-supported languages in Saarthi."""

    def __init__(self):
        self._profiles: Dict[str, LanguageProfile] = {
            VoiceLanguageCode.ENGLISH_IN.value: LanguageProfile(
                code=VoiceLanguageCode.ENGLISH_IN.value,
                name="Indian English",
                script="Latin",
                locale="en-IN",
                edge_tts_male_voice="en-IN-PrabhatNeural",
                edge_tts_female_voice="en-IN-NeerjaNeural",
                stt_target_locale="en-IN",
                is_active=True,
                supports_code_switching=True
            ),
            VoiceLanguageCode.HINDI_IN.value: LanguageProfile(
                code=VoiceLanguageCode.HINDI_IN.value,
                name="Hindi",
                script="Devanagari",
                locale="hi-IN",
                edge_tts_male_voice="hi-IN-MadhurNeural",
                edge_tts_female_voice="hi-IN-SwaraNeural",
                stt_target_locale="hi-IN",
                is_active=True,
                supports_code_switching=True
            ),
            VoiceLanguageCode.HINGLISH.value: LanguageProfile(
                code=VoiceLanguageCode.HINGLISH.value,
                name="Hinglish (Hindi + English)",
                script="Devanagari/Latin",
                locale="hi-en",
                edge_tts_male_voice="hi-IN-MadhurNeural",
                edge_tts_female_voice="hi-IN-SwaraNeural",
                stt_target_locale="hi-IN",  # Google Speech Recognizer handles code-switched Hindi-English via hi-IN locale
                is_active=True,
                supports_code_switching=True
            ),
            VoiceLanguageCode.BENGALI_IN.value: LanguageProfile(
                code=VoiceLanguageCode.BENGALI_IN.value,
                name="Bengali",
                script="Bengali",
                locale="bn-IN",
                edge_tts_male_voice="bn-IN-BashkarNeural",
                edge_tts_female_voice="bn-IN-TanishaaNeural",
                stt_target_locale="bn-IN",
                is_active=False
            ),
            VoiceLanguageCode.TAMIL_IN.value: LanguageProfile(
                code=VoiceLanguageCode.TAMIL_IN.value,
                name="Tamil",
                script="Tamil",
                locale="ta-IN",
                edge_tts_male_voice="ta-IN-ValluvarNeural",
                edge_tts_female_voice="ta-IN-PallaviNeural",
                stt_target_locale="ta-IN",
                is_active=False
            ),
            VoiceLanguageCode.TELUGU_IN.value: LanguageProfile(
                code=VoiceLanguageCode.TELUGU_IN.value,
                name="Telugu",
                script="Telugu",
                locale="te-IN",
                edge_tts_male_voice="te-IN-MohanNeural",
                edge_tts_female_voice="te-IN-ShrutiNeural",
                stt_target_locale="te-IN",
                is_active=False
            ),
            VoiceLanguageCode.MARATHI_IN.value: LanguageProfile(
                code=VoiceLanguageCode.MARATHI_IN.value,
                name="Marathi",
                script="Devanagari",
                locale="mr-IN",
                edge_tts_male_voice="mr-IN-ManoharNeural",
                edge_tts_female_voice="mr-IN-AarohiNeural",
                stt_target_locale="mr-IN",
                is_active=False
            ),
            VoiceLanguageCode.GUJARATI_IN.value: LanguageProfile(
                code=VoiceLanguageCode.GUJARATI_IN.value,
                name="Gujarati",
                script="Gujarati",
                locale="gu-IN",
                edge_tts_male_voice="gu-IN-NiranjanNeural",
                edge_tts_female_voice="gu-IN-DhwaniNeural",
                stt_target_locale="gu-IN",
                is_active=False
            )
        }

    def get_profile(self, code: str) -> Optional[LanguageProfile]:
        # Normalize code
        if code in self._profiles:
            return self._profiles[code]
        if code.lower().startswith("hi"):
            return self._profiles[VoiceLanguageCode.HINDI_IN.value]
        if code.lower().startswith("en"):
            return self._profiles[VoiceLanguageCode.ENGLISH_IN.value]
        return None

    def list_active_languages(self) -> List[LanguageProfile]:
        return [p for p in self._profiles.values() if p.is_active]

    def register_language(self, profile: LanguageProfile) -> None:
        self._profiles[profile.code] = profile

    def detect_code_switching(self, text: str) -> Dict[str, Any]:
        """
        Analyzes a transcription to detect code-switching between Hindi and English.
        Detects both Devanagari script presence and Romanized Hinglish phonetic markers.
        """
        if not text:
            return {"primary_language": "en-IN", "is_code_switched": False, "languages": ["en-IN"]}

        has_devanagari = any("\u0900" <= char <= "\u097f" for char in text)
        has_latin = any("a" <= char.lower() <= "z" for char in text)

        # Common Hinglish conversational marker tokens
        hinglish_markers = {
            "kya", "hai", "hain", "mujhe", "mera", "meri", "hum", "aap", "tum",
            "bana", "dena", "karo", "kardo", "karna", "chahiye", "accha", "theek",
            "batao", "samjhao", "dijiye", "shukriya", "dhanyawad", "namaste", "kal",
            "aaj", "kitna", "kaise", "kab", "kahan", "kyun", "wala", "wali", "wale"
        }
        words = [w.strip(".,?!\"'").lower() for w in text.split()]
        hinglish_matches = [w for w in words if w in hinglish_markers]

        if has_devanagari and has_latin:
            return {
                "primary_language": "hi-en",
                "is_code_switched": True,
                "languages": ["hi-IN", "en-IN"],
                "reason": "mixed_devanagari_and_latin_script"
            }
        elif len(hinglish_matches) >= 1 and has_latin:
            return {
                "primary_language": "hi-en",
                "is_code_switched": True,
                "languages": ["hi-IN", "en-IN"],
                "matched_markers": hinglish_matches,
                "reason": "latin_script_with_hindi_markers"
            }
        elif has_devanagari:
            return {
                "primary_language": "hi-IN",
                "is_code_switched": False,
                "languages": ["hi-IN"]
            }
        else:
            return {
                "primary_language": "en-IN",
                "is_code_switched": False,
                "languages": ["en-IN"]
            }


language_registry = LanguageRegistry()
