"""
Data models for ingested media sessions.
"""
from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class IngestedMedia:
    source_name: str
    source_type: str  # "file" or "url"
    size_mb: float
    raw_media_bytes: Optional[bytes]  # Ephemeral raw media retained for Epic 3 visual extraction
    wav_bytes: Optional[bytes]        # Normalized 16 kHz Mono audio retained for Epic 4 (Whisper & VAD)
    duration_sec: float
    duration_str: str
    sample_rate: int
    channels: int
    is_audio_evicted: bool = False
    ingested_at: float = 0.0

    def evict_raw_media(self):
        """Purge raw video/container bytes once video frame extraction (Epic 3) is complete."""
        self.raw_media_bytes = None

    def evict_audio(self):
        """Purge normalized WAV bytes once speech transcription and VAD (Epic 4) are complete."""
        self.wav_bytes = None
        self.is_audio_evicted = True
