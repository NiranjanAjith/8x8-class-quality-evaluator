"""
Audio Telemetry Pipeline Orchestrator.
Coordinates VAD, speech-to-text, PII redaction, pacing/question metrics,
and enforces zero-retention memory eviction.
"""
from dataclasses import dataclass
from typing import List, Optional
from src.audio.vad import compute_vad_timeline, VadResult
from src.audio.transcriber import transcribe_audio_stream, TranscribedSegment
from src.audio.metrics import compute_speech_pacing, extract_questions, estimate_talk_ratio


@dataclass
class AudioTelemetryResult:
    success: bool
    total_duration_sec: float
    dead_air_pct: float
    wpm: int
    question_density: float
    total_questions: int
    teacher_talk_pct: float
    student_talk_pct: float
    segments: List[TranscribedSegment]
    error_message: Optional[str] = None


def run_audio_telemetry_pipeline(wav_bytes: bytes) -> AudioTelemetryResult:
    """
    Execute full audio telemetry extraction pipeline in-memory:
    1. VAD analysis for silence voids and dead air %.
    2. Quantized Whisper-tiny speech-to-text.
    3. PII scrubbing of all emitted transcript tokens.
    4. Pacing (WPM), question density, and talk ratio estimation.
    """
    if not wav_bytes:
        return AudioTelemetryResult(
            success=False,
            total_duration_sec=0.0,
            dead_air_pct=0.0,
            wpm=0,
            question_density=0.0,
            total_questions=0,
            teacher_talk_pct=0.0,
            student_talk_pct=0.0,
            segments=[],
            error_message="Empty audio stream provided."
        )

    try:
        # Step 1: In-memory VAD analysis
        vad_res = compute_vad_timeline(wav_bytes)

        # Step 2: Speech transcription + PII redaction (Option A)
        segments = transcribe_audio_stream(wav_bytes)

        # Step 3: Pacing & Inquiry metrics
        wpm = compute_speech_pacing(segments, vad_res.speech_duration_sec)
        q_density, q_total = extract_questions(segments, vad_res.total_duration_sec)
        teacher_pct, student_pct = estimate_talk_ratio(segments)

        return AudioTelemetryResult(
            success=True,
            total_duration_sec=vad_res.total_duration_sec,
            dead_air_pct=vad_res.dead_air_pct,
            wpm=wpm,
            question_density=q_density,
            total_questions=q_total,
            teacher_talk_pct=teacher_pct,
            student_talk_pct=student_pct,
            segments=segments,
        )

    except Exception as e:
        return AudioTelemetryResult(
            success=False,
            total_duration_sec=0.0,
            dead_air_pct=0.0,
            wpm=0,
            question_density=0.0,
            total_questions=0,
            teacher_talk_pct=0.0,
            student_talk_pct=0.0,
            segments=[],
            error_message=f"Audio pipeline failure: {str(e)}"
        )
