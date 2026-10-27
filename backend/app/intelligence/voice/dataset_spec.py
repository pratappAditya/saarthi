"""
Saarthi 10-Speaker Bilingual Voice Evaluation Dataset Specification.
Defines protocols, consent requirements, sentence design, phonetic distribution,
code-switching coverage, and rigorous evaluation methodology.
CRITICAL: Do NOT start model training automatically. This document serves as the
authoritative evaluation protocol prior to any recording or fine-tuning.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class DatasetSpeakerProfile(BaseModel):
    speaker_id: str
    age_bracket: str
    gender: str
    native_language: str
    primary_accent: str  # e.g., North Indian, South Indian, Urban Bilingual
    proficiency_hindi: str
    proficiency_english: str
    proficiency_hinglish: str


class EvaluationBenchmarkProtocol(BaseModel):
    protocol_name: str
    target_metrics: List[str]  # WER, CER, BLEU, MOS, Latency
    wer_target_english: float = 0.08  # <= 8%
    wer_target_hindi: float = 0.10    # <= 10%
    wer_target_hinglish: float = 0.12 # <= 12%
    mos_target_tts: float = 4.2       # Mean Opinion Score >= 4.2 / 5.0


class VoiceDatasetEvaluationSpec:
    """Formal bilingual evaluation specification for Hindi, English, and Hinglish."""

    @staticmethod
    def get_consent_framework() -> Dict[str, Any]:
        return {
            "consent_required": True,
            "anonymization": "All audio stripped of PII; indexed strictly by UUID speaker token.",
            "revocation": "Participant may request complete deletion of voice samples at any time.",
            "usage_scope": "Evaluation, accent calibration, and phonetic robustness testing only. No public redistribution.",
            "storage_security": "Encrypted at rest (AES-256), isolated from general tenant data."
        }

    @staticmethod
    def get_sentence_design() -> Dict[str, Any]:
        return {
            "total_sentences_per_speaker": 150,
            "hindi_coverage": {
                "count": 50,
                "phonetic_distribution": "All 11 vowels and 33 Devanagari consonants represented.",
                "domain_types": ["General conversation", "Historical/Cultural", "Scientific terminology"]
            },
            "english_coverage": {
                "count": 50,
                "phonetic_distribution": "Standard Indian English phoneme distribution, aspirated stops, rhotic variations.",
                "domain_types": ["Software development", "System commands", "Technical architecture"]
            },
            "hinglish_coverage": {
                "count": 50,
                "code_switch_types": [
                    "Intra-sentential (e.g., 'Kal mujhe Bangalore office ke liye ek report bana dena')",
                    "Technical loanwords (e.g., 'Is database query ko optimize kar do')",
                    "Command directives (e.g., 'Summary ko bullet points mein rewrite karo')"
                ]
            }
        }

    @staticmethod
    def get_environmental_matrices() -> Dict[str, Any]:
        return {
            "speaking_rates": ["Normal (~140 wpm)", "Fast (~180 wpm)", "Slow (~100 wpm)"],
            "noise_conditions": [
                "Clean Studio (SNR > 30 dB)",
                "Office Ambient (keyboard, AC hum, SNR ~ 18 dB)",
                "Mobile / Roadside Ambient (traffic, distant murmur, SNR ~ 10 dB)"
            ],
            "microphones": ["Built-in laptop microphone", "Headset condenser", "Studio dynamic microphone"]
        }

    @staticmethod
    def get_speaker_distribution() -> List[Dict[str, Any]]:
        return [
            {"id": "SPK-01", "gender": "Female", "accent": "Delhi / NCR Urban Bilingual"},
            {"id": "SPK-02", "gender": "Male", "accent": "Western UP Hindi Dominant"},
            {"id": "SPK-03", "gender": "Female", "accent": "Mumbai / Marathi Influenced Hinglish"},
            {"id": "SPK-04", "gender": "Male", "accent": "Bengaluru / South Indian English Bilingual"},
            {"id": "SPK-05", "gender": "Female", "accent": "Kolkata / Bengali Influenced Bilingual"},
            {"id": "SPK-06", "gender": "Male", "accent": "Hyderabad / Dakhni English Blend"},
            {"id": "SPK-07", "gender": "Female", "accent": "Punjab / Northern English Lilt"},
            {"id": "SPK-08", "gender": "Male", "accent": "Chennai / Tamil Influenced English"},
            {"id": "SPK-09", "gender": "Female", "accent": "Bihari / Maithili Background Hindi"},
            {"id": "SPK-10", "gender": "Male", "accent": "Cosmopolitan Indian English"}
        ]

    @staticmethod
    def get_evaluation_methodology() -> Dict[str, Any]:
        return {
            "metrics": {
                "Word Error Rate (WER)": "Computed against human-verified gold ground-truth transcripts.",
                "Character Error Rate (CER)": "Critical for Devanagari matra and compound ligature accuracy.",
                "Code-Switch Boundary Accuracy": "Precision/Recall on language transition points.",
                "Mean Opinion Score (MOS)": "5-point double-blind perceptual listening evaluation for TTS naturalness."
            },
            "automation": "Automated evaluation harness compares STT transcript outputs against phonetic test corpus."
        }


voice_dataset_spec = VoiceDatasetEvaluationSpec()
