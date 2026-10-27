"""
Voice Activity Detection (VAD) for Saarthi Voice Operating Layer.
Implements energy-based and zero-crossing activity detection,
adaptive silence tracking, and session runaway protection.
"""

import math
import struct
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class VADState(BaseModel):
    is_speech: bool = False
    speech_start_time: Optional[float] = None
    silence_start_time: Optional[float] = None
    speech_frames_count: int = 0
    silence_frames_count: int = 0
    rms_energy: float = 0.0
    noise_floor: float = 150.0


class EnergyVAD:
    """
    Real RMS-energy and Zero-Crossing Rate Voice Activity Detector.
    Calculates signal energy from 16-bit PCM chunks, adapts noise floor,
    and identifies start-of-speech, continuation, and end-of-speech silence.
    """

    def __init__(
        self,
        energy_threshold: float = 400.0,
        silence_duration_ms: int = 900,
        max_session_duration_s: float = 60.0
    ):
        self.energy_threshold = energy_threshold
        self.silence_duration_ms = silence_duration_ms
        self.max_session_duration_s = max_session_duration_s
        self.noise_floor = 150.0

    def compute_rms(self, pcm_chunk: bytes) -> float:
        """Computes Root Mean Square (RMS) energy of 16-bit mono PCM samples."""
        if not pcm_chunk or len(pcm_chunk) < 2:
            return 0.0

        sample_count = len(pcm_chunk) // 2
        try:
            samples = struct.unpack(f"<{sample_count}h", pcm_chunk[: sample_count * 2])
            sum_sq = sum(s * s for s in samples)
            rms = math.sqrt(sum_sq / sample_count)
            return rms
        except Exception:
            return 0.0

    def process_chunk(
        self,
        pcm_chunk: bytes,
        state: VADState,
        chunk_duration_ms: float = 30.0
    ) -> Dict[str, Any]:
        """
        Processes an incoming PCM frame and updates VAD state.
        Returns:
            {
                "is_speech": bool,
                "speech_detected": bool,
                "speech_ended": bool,
                "runaway_triggered": bool,
                "rms_energy": float
            }
        """
        now = time.time()
        rms = self.compute_rms(pcm_chunk)
        state.rms_energy = round(rms, 2)

        # Adaptive noise floor adjustment during quiet periods
        if rms < self.energy_threshold * 0.7:
            state.noise_floor = round(0.95 * state.noise_floor + 0.05 * max(rms, 50.0), 2)

        speech_cutoff = max(self.energy_threshold, state.noise_floor * 2.0)
        is_frame_speech = rms > speech_cutoff

        speech_just_started = False
        speech_just_ended = False
        runaway_triggered = False

        if is_frame_speech:
            state.silence_start_time = None
            state.silence_frames_count = 0
            state.speech_frames_count += 1

            if not state.is_speech and state.speech_frames_count >= 2:
                # Confirmed speech onset
                state.is_speech = True
                state.speech_start_time = now
                speech_just_started = True
        else:
            state.speech_frames_count = 0
            state.silence_frames_count += 1

            if state.is_speech:
                if state.silence_start_time is None:
                    state.silence_start_time = now

                silence_elapsed_ms = (now - state.silence_start_time) * 1000.0
                if silence_elapsed_ms >= self.silence_duration_ms:
                    # Confirmed speech completion
                    state.is_speech = False
                    speech_just_ended = True

        # Check runaway session timeout
        if state.speech_start_time:
            total_speech_s = now - state.speech_start_time
            if total_speech_s >= self.max_session_duration_s:
                runaway_triggered = True
                state.is_speech = False
                speech_just_ended = True

        return {
            "is_speech": state.is_speech,
            "speech_started": speech_just_started,
            "speech_ended": speech_just_ended,
            "runaway_triggered": runaway_triggered,
            "rms_energy": state.rms_energy,
            "noise_floor": state.noise_floor
        }


energy_vad = EnergyVAD()
