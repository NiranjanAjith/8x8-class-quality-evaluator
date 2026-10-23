"""
Audio Telemetry & Whisper Transcription Package.
"""
from src.audio.sanitizer import sanitize_transcript_text
from src.audio.vad import compute_vad_timeline, VadResult
from src.audio.transcriber import transcribe_audio_stream, TranscribedSegment
from src.audio.metrics import (
    compute_speech_pacing,
    extract_questions,
    estimate_talk_ratio,
)
from src.audio.pipeline import run_audio_telemetry_pipeline, AudioTelemetryResult

__all__ = [
    "sanitize_transcript_text",
    "compute_vad_timeline",
    "VadResult",
    "transcribe_audio_stream",
    "TranscribedSegment",
    "compute_speech_pacing",
    "extract_questions",
    "estimate_talk_ratio",
    "run_audio_telemetry_pipeline",
    "AudioTelemetryResult",
]
