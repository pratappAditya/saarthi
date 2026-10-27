"""
Real Audio Capture Provider for Saarthi.
Uses sounddevice (PortAudio) for real microphone input capture,
audio device enumeration, buffer streaming, and device failure handling.
"""

from __future__ import annotations

import io
import wave
import time
import threading
import logging
from typing import Optional, List, Dict, Any, Tuple
try:
    import sounddevice as sd
except ImportError:
    sd = None

logger = logging.getLogger("app.intelligence.voice.audio_capture")


class SoundDeviceAudioCapture:
    """
    Real microphone audio capture engine using sounddevice.
    Buffers incoming PCM audio at 16kHz Mono 16-bit.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.channels = 1
        self._is_recording = False
        self._audio_buffer = bytearray()
        self._stream: Optional[sd.RawInputStream] = None
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None
        self._device_index: Optional[int] = None

    def list_input_devices(self) -> List[Dict[str, Any]]:
        """Returns list of available microphone input devices on the system."""
        if sd is None:
            return []
        try:
            devices = sd.query_devices()
            default_device = sd.default.device[0]
            input_devices = []
            for i, d in enumerate(devices):
                if d.get("max_input_channels", 0) > 0:
                    input_devices.append({
                        "device_id": i,
                        "name": d.get("name", "Unknown Device"),
                        "max_channels": d.get("max_input_channels"),
                        "default_samplerate": d.get("default_samplerate"),
                        "is_default": (i == default_device)
                    })
            return input_devices
        except Exception as e:
            logger.error(f"Error querying audio devices: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Returns microphone capture engine status."""
        if sd is None:
            return {
                "is_recording": False,
                "has_input_device": False,
                "default_device_name": "None",
                "sample_rate": self.sample_rate,
                "buffered_bytes": len(self._audio_buffer),
                "recording_duration_s": 0.0
            }
        try:
            default_in = sd.default.device[0]
            device_info = sd.query_devices(default_in) if default_in is not None else {}
            has_input = default_in is not None
        except Exception:
            device_info = {}
            has_input = False

        return {
            "is_recording": self._is_recording,
            "has_input_device": has_input,
            "default_device_name": device_info.get("name", "None"),
            "sample_rate": self.sample_rate,
            "buffered_bytes": len(self._audio_buffer),
            "recording_duration_s": round(time.time() - self._start_time, 2) if self._start_time else 0.0
        }

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback collecting raw 16-bit PCM chunks."""
        if status:
            logger.debug(f"Audio stream status: {status}")
        with self._lock:
            if self._is_recording:
                self._audio_buffer.extend(indata)

    def start_recording(self, device_id: Optional[int] = None) -> bool:
        """Starts real microphone recording."""
        with self._lock:
            if self._is_recording:
                return True

            self._audio_buffer.clear()
            self._device_index = device_id
            self._start_time = time.time()

            try:
                self._stream = sd.RawInputStream(
                    samplerate=self.sample_rate,
                    blocksize=1024,
                    device=self._device_index,
                    channels=self.channels,
                    dtype="int16",
                    callback=self._audio_callback
                )
                self._stream.start()
                self._is_recording = True
                logger.info(f"Microphone recording started on device index {device_id or 'default'}")
                return True
            except Exception as e:
                logger.error(f"Failed to start audio recording stream: {e}")
                self._is_recording = False
                self._stream = None
                raise RuntimeError(f"Microphone stream failure: {e}")

    def stop_recording(self) -> bytes:
        """
        Stops recording and returns standard 16kHz 16-bit PCM WAV bytes.
        """
        with self._lock:
            if not self._is_recording:
                return b""

            self._is_recording = False
            if self._stream:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception as e:
                    logger.warning(f"Error stopping audio stream: {e}")
                self._stream = None

            raw_pcm = bytes(self._audio_buffer)
            self._audio_buffer.clear()
            self._start_time = None

        if not raw_pcm:
            return b""

        # Package raw PCM frames into valid WAV container
        bio = io.BytesIO()
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(raw_pcm)

        return bio.getvalue()

    def cancel_recording(self) -> None:
        """Cancels recording and discards buffered audio without saving."""
        with self._lock:
            self._is_recording = False
            if self._stream:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            self._audio_buffer.clear()
            self._start_time = None
            logger.info("Microphone recording cancelled and buffer cleared.")


audio_capture = SoundDeviceAudioCapture()
