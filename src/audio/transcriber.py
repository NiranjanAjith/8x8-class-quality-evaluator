"""
Local Quantized Whisper Speech-to-Text Transcriber.
Runs INT8 Whisper-tiny on CPU in-memory with automatic text PII redaction.
Zero audio or transcripts are transmitted to external cloud APIs.
"""
import io
from dataclasses import dataclass
from typing import List, Optional
from src.audio.sanitizer import sanitize_transcript_text


@dataclass
class TranscribedSegment:
    segment_id: int
    start_sec: float
    end_sec: float
    timestamp_str: str
    speaker: str
    text: str
    words_count: int
    pedagogical_tag: str
    explanation: str


_WHISPER_MODEL = None


def get_whisper_model(model_size: str = "tiny"):
    """Load and cache the INT8 quantized Whisper model for CPU execution."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
            # Load quantized tiny model on CPU for minimal RAM usage (<200MB)
            _WHISPER_MODEL = WhisperModel(model_size, device="cpu", compute_type="int8")
        except Exception:
            _WHISPER_MODEL = None
    return _WHISPER_MODEL


def transcribe_audio_stream(
    wav_bytes: bytes,
    model_size: str = "tiny"
) -> List[TranscribedSegment]:
    """
    Transcribe 16 kHz mono WAV audio in-memory and apply Option A text PII redaction.
    Returns timestamped, sanitized pedagogical dialogue segments.
    """
    if not wav_bytes:
        return []

    model = get_whisper_model(model_size=model_size)
    if model is None:
        # Fallback if model cannot be loaded (e.g. offline sandbox without initial weight cache)
        return []

    try:
        audio_stream = io.BytesIO(wav_bytes)
        segments_gen, info = model.transcribe(
            audio_stream,
            beam_size=1,
            language="en",
            vad_filter=False,  # Dedicated VAD handled in vad.py
            word_timestamps=False,
        )

        transcribed_segments: List[TranscribedSegment] = []
        seg_idx = 1
        prev_was_question = False
        prev_end_sec = 0.0

        for seg in segments_gen:
            clean_text = sanitize_transcript_text(seg.text.strip())
            if not clean_text:
                continue

            mins = int(seg.start // 60)
            secs = int(seg.start % 60)
            t_str = f"{mins:02d}:{secs:02d}"

            words = clean_text.split()
            w_count = len(words)

            # Heuristic speaker assignment and pedagogical tagging
            is_question = clean_text.endswith("?") or any(
                clean_text.lower().startswith(w) for w in ["who", "what", "where", "when", "why", "how", "can you", "could"]
            )

            silence_pause = seg.start - prev_end_sec if prev_end_sec > 0.0 else 0.0

            # Only assign student turn if a prior question was followed by a conversational wait pause (>= 1.5s)
            if prev_was_question and silence_pause >= 1.5:
                speaker = "[Student]"
                pedagogical_tag = "Active Participation"
                explanation = "Student response volunteered following an instructional check-for-understanding."
                prev_was_question = False
            elif is_question:
                speaker = "[Teacher]"
                pedagogical_tag = "Interrogative Prompt"
                explanation = "Check-for-understanding prompt designed to stimulate cohort participation and concept recall."
                prev_was_question = True
            elif w_count > 30:
                speaker = "[Teacher]"
                pedagogical_tag = "Extended Monologue"
                explanation = "Direct conceptual instruction segment delivered continuously without interruption."
                prev_was_question = False
            else:
                speaker = "[Teacher]"
                pedagogical_tag = "Instructional Pacing"
                explanation = "Classroom guidance and conceptual continuity statement."
                prev_was_question = False

            prev_end_sec = seg.end

            transcribed_segments.append(
                TranscribedSegment(
                    segment_id=seg_idx,
                    start_sec=round(seg.start, 2),
                    end_sec=round(seg.end, 2),
                    timestamp_str=t_str,
                    speaker=speaker,
                    text=clean_text,
                    words_count=w_count,
                    pedagogical_tag=pedagogical_tag,
                    explanation=explanation,
                )
            )
            seg_idx += 1

        return transcribed_segments

    except Exception:
        return []
