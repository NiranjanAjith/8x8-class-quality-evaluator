"""
Unit & Integration Tests for Epic 4: Audio Telemetry, VAD, and Option A PII Sanitizer.
"""
from src.audio.sanitizer import sanitize_transcript_text
from src.audio.vad import compute_vad_timeline
from src.audio.transcriber import TranscribedSegment
from src.audio.metrics import compute_speech_pacing, extract_questions, estimate_talk_ratio
from src.audio.pipeline import run_audio_telemetry_pipeline
from tests.test_ingestion import create_synthetic_wav


def test_transcript_pii_sanitization():
    """Verify Option A text PII sanitizer redacts all structured identifiers."""
    raw_text = (
        "Good morning cohort, I am Prof. Alan Turing. "
        "Please submit your assignment to turing.alan@university.edu or call 555-234-5678. "
        "Make sure to reference your Student ID: STU-89241 and check https://course.canvas.com for slides. "
        "Thanks John for volunteering."
    )
    sanitized = sanitize_transcript_text(raw_text)

    assert "turing.alan@university.edu" not in sanitized
    assert "[EMAIL]" in sanitized

    assert "555-234-5678" not in sanitized
    assert "[PHONE]" in sanitized

    assert "https://course.canvas.com" not in sanitized
    assert "[URL]" in sanitized

    assert "STU-89241" not in sanitized
    assert "[STUDENT_ID]" in sanitized

    assert "Prof. Alan Turing" not in sanitized
    assert "[Teacher]" in sanitized

    assert "John" not in sanitized
    assert "[Student]" in sanitized


def test_in_memory_vad_dead_air_detection():
    """Verify VAD correctly distinguishes speech tone from silence."""
    # 2 seconds of 440Hz tone
    tone_wav = create_synthetic_wav(duration_sec=2.0, sample_rate=16000, channels=1)
    res_tone = compute_vad_timeline(tone_wav)
    assert res_tone.total_duration_sec == 2.0
    assert res_tone.dead_air_pct < 15.0, f"Expected low dead air on active tone, got {res_tone.dead_air_pct}%"

    # Synthetic silence (zero-amplitude samples)
    import io, wave
    silence_buf = io.BytesIO()
    with wave.open(silence_buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 32000)  # 2 seconds of silence
    res_silence = compute_vad_timeline(silence_buf.getvalue())
    assert res_silence.dead_air_pct > 80.0, f"Expected high dead air on silence, got {res_silence.dead_air_pct}%"


def test_speech_pacing_and_question_metrics():
    """Verify calculation of WPM, question density, and talk ratios."""
    segments = [
        TranscribedSegment(1, 0.0, 5.0, "00:00", "[Teacher]", "Can anyone explain the main principle of linear span?", 8, "Interrogative Prompt", ""),
        TranscribedSegment(2, 6.0, 10.0, "00:06", "[Student]", "It is the set of all linear combinations of those vectors.", 10, "Active Participation", ""),
        TranscribedSegment(3, 11.0, 30.0, "00:11", "[Teacher]", "Exactly right, so any vector in that subspace can be reached.", 11, "Instructional Pacing", ""),
    ]

    # Total words = 29. If active speech = 29 sec -> 60 WPM
    wpm = compute_speech_pacing(segments, active_speech_sec=29.0)
    assert wpm == 60

    # Total duration = 60 sec (0.0167 hours). 1 question -> ~60/hr
    density, q_total = extract_questions(segments, total_duration_sec=60.0)
    assert q_total == 1
    assert density == 60.0

    # Talk ratio
    teacher_pct, student_pct = estimate_talk_ratio(segments)
    assert teacher_pct > student_pct
    assert abs(teacher_pct + student_pct - 100.0) < 0.2


def test_audio_pipeline_execution():
    """Verify pipeline runs end-to-end on synthetic audio."""
    tone_wav = create_synthetic_wav(duration_sec=1.5, sample_rate=16000, channels=1)
    res = run_audio_telemetry_pipeline(tone_wav)
    assert res.success is True
    assert res.total_duration_sec == 1.5


def test_ui_audio_pipeline_integration():
    """Verify that transcript_viewer's pipeline runner processes media and sets session state."""
    import streamlit as st
    from src.ui.components.transcript_viewer import _process_and_store_ingested_media
    from src.ingestion.models import IngestedMedia

    # Initialize empty session state
    st.session_state.session_data = None
    tone_wav = create_synthetic_wav(duration_sec=2.0, sample_rate=16000, channels=1)

    success = _process_and_store_ingested_media(tone_wav, "lecture_sample.wav", "file", 0.06)
    assert success is True
    assert "ingested_media" in st.session_state
    ingested: IngestedMedia = st.session_state.ingested_media
    assert ingested.is_audio_evicted is True
    assert ingested.is_video_evicted is True
    assert ingested.wav_bytes is None  # Audio buffer purged
    assert st.session_state.session_data is not None
    assert st.session_state.session_data.telemetry["wpm"] >= 0


if __name__ == "__main__":
    test_transcript_pii_sanitization()
    test_in_memory_vad_dead_air_detection()
    test_speech_pacing_and_question_metrics()
    test_audio_pipeline_execution()
    test_ui_audio_pipeline_integration()
    print("All Epic 4 audio telemetry and PII tests passed successfully!")
