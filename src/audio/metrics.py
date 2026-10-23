"""
Pedagogical Audio Metrics & Conversational Dynamics Extractor.
Derives speech pacing (WPM), question density, and teacher vs. student talk ratios.
"""
from typing import List, Tuple
from src.audio.transcriber import TranscribedSegment


def compute_speech_pacing(
    segments: List[TranscribedSegment],
    active_speech_sec: float
) -> int:
    """
    Calculate Words Per Minute (WPM) across active verbal speech duration.
    Optimal pedagogical range: 125 - 160 WPM.
    """
    if not segments or active_speech_sec <= 0.0:
        return 0

    total_words = sum(s.words_count for s in segments)
    active_minutes = active_speech_sec / 60.0
    wpm = int(round(total_words / active_minutes))
    return max(0, wpm)


def extract_questions(
    segments: List[TranscribedSegment],
    total_duration_sec: float
) -> Tuple[float, int]:
    """
    Quantify question frequency and calculate question density (questions per hour).
    Returns (questions_per_hour, total_question_count).
    """
    if not segments or total_duration_sec <= 0.0:
        return 0.0, 0

    question_count = sum(
        1 for s in segments
        if s.pedagogical_tag == "Interrogative Prompt"
        or s.text.endswith("?")
        or any(s.text.lower().startswith(q) for q in ["who", "what", "where", "when", "why", "how", "can", "could", "would"])
    )

    hours = total_duration_sec / 3600.0
    density = round(question_count / max(0.01, hours), 1)
    return density, question_count


def estimate_talk_ratio(
    segments: List[TranscribedSegment]
) -> Tuple[float, float]:
    """
    Estimate Teacher vs. Student verbal distribution share (percentage points).
    Returns (teacher_talk_pct, student_talk_pct).
    """
    if not segments:
        return 75.0, 25.0

    teacher_words = sum(s.words_count for s in segments if "[Teacher]" in s.speaker)
    student_words = sum(s.words_count for s in segments if "[Student]" in s.speaker)
    total_words = teacher_words + student_words

    if total_words == 0:
        return 75.0, 25.0

    teacher_pct = round((teacher_words / float(total_words)) * 100.0, 1)
    student_pct = round(100.0 - teacher_pct, 1)

    return teacher_pct, student_pct
