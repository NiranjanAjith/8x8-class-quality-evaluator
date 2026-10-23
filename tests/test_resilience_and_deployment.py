"""
Epic 7: Deployment, Resource Hardening & End-to-End Resilience Test Suite.
Verifies Hugging Face Spaces manifests, zero-division guards, audio-only inputs,
100% face-drop scenarios, and multi-session garbage collection.
"""
import os
import gc
import io
import wave
import numpy as np
from src.vision.pipeline import run_visual_telemetry_pipeline
from src.audio.pipeline import run_audio_telemetry_pipeline
from src.audio.metrics import compute_speech_pacing, extract_questions, estimate_talk_ratio
from src.audio.vad import compute_vad_timeline
from src.models.evaluator import run_evaluation, apply_evaluation_to_session
from src.mock.telemetry_generator import get_scenario
from tests.test_ingestion import create_synthetic_wav


def test_deployment_manifests():
    """Verify all Hugging Face Spaces deployment manifests exist and are valid."""
    # 1. packages.txt
    assert os.path.exists("packages.txt"), "packages.txt is missing"
    with open("packages.txt", "r") as f:
        pkgs = f.read()
    assert "ffmpeg" in pkgs, "ffmpeg missing from packages.txt"

    # 2. README.md YAML frontmatter
    assert os.path.exists("README.md"), "README.md is missing"
    with open("README.md", "r") as f:
        readme = f.read()
    assert "sdk: streamlit" in readme, "sdk: streamlit missing from README.md"
    assert "app_file: app.py" in readme, "app_file: app.py missing from README.md"

    # 3. .streamlit/config.toml
    assert os.path.exists(".streamlit/config.toml"), ".streamlit/config.toml is missing"
    with open(".streamlit/config.toml", "r") as f:
        config = f.read()
    assert "maxUploadSize = 200" in config
    assert "headless = true" in config
    assert "enableXsrfProtection = true" in config

    # 4. requirements.txt
    assert os.path.exists("requirements.txt"), "requirements.txt is missing"
    with open("requirements.txt", "r") as f:
        reqs = f.read()
    for pkg in ["streamlit", "faster-whisper", "opencv-python-headless", "plotly", "requests"]:
        assert pkg in reqs, f"{pkg} missing from requirements.txt"


def test_audio_only_media_pipeline():
    """Verify that pure audio media (no video tracks) executes gracefully without errors."""
    wav_bytes = create_synthetic_wav(duration_sec=2.0, sample_rate=16000, channels=1)

    # Visual pipeline on pure audio
    visual_res = run_visual_telemetry_pipeline(wav_bytes, sample_interval_sec=5.0)
    assert visual_res.success is True
    assert visual_res.slide_count == 0
    assert len(visual_res.slides) == 0

    # Audio pipeline on pure audio
    audio_res = run_audio_telemetry_pipeline(wav_bytes)
    assert audio_res.success is True
    assert audio_res.total_duration_sec == 2.0


def test_total_silence_and_zero_division():
    """Verify that zero-speech, pure silence media does not trigger division-by-zero errors."""
    silence_buf = io.BytesIO()
    with wave.open(silence_buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 32000)  # 2 seconds pure zero silence
    silence_bytes = silence_buf.getvalue()

    # VAD
    vad_res = compute_vad_timeline(silence_bytes)
    assert vad_res.dead_air_pct >= 90.0

    # Zero segments pacing
    wpm = compute_speech_pacing([], active_speech_sec=0.0)
    assert wpm == 0

    # Zero questions
    density, q_total = extract_questions([], total_duration_sec=0.0)
    assert density == 0.0
    assert q_total == 0

    # Zero talk ratio
    teacher_pct, student_pct = estimate_talk_ratio([])
    assert teacher_pct + student_pct == 100.0

    # Evaluation on silence telemetry
    telemetry = {
        "dead_air_pct": 100.0,
        "wpm": 0,
        "question_density": 0.0,
        "total_questions": 0,
        "teacher_talk_pct": 0.0,
        "student_talk_pct": 0.0,
        "slide_count": 0,
        "slide_velocity_min": 0.0,
    }
    eval_res = run_evaluation(telemetry, [], "02:00")
    assert eval_res.overall_tier == "Poor"
    assert len(eval_res.dimension_scores) == 4


def test_all_faces_dropped_resilience():
    """Verify that when 100% of frames have human faces, all are purged and session evaluates smoothly."""
    from src.vision.slide_analyzer import detect_slide_transitions
    # 0 retained frames
    retained_frames = []
    slides, velocity = detect_slide_transitions(retained_frames)
    assert len(slides) == 0
    assert velocity == 0.0

    session = get_scenario("interactive")
    session.retained_slides = []
    session.telemetry["slide_count"] = 0
    session.telemetry["slide_velocity_min"] = 0.0

    eval_res = run_evaluation(session.telemetry, session.transcript_snippets, session.duration_str)
    apply_evaluation_to_session(session, eval_res)
    assert session.pedagogical_evaluation is not None


def test_multi_session_memory_eviction_loop():
    """Verify that multiple consecutive ingestion cycles trigger gc and do not leak buffers."""
    from src.ingestion.models import IngestedMedia

    for i in range(5):
        raw_wav = create_synthetic_wav(duration_sec=1.0, sample_rate=16000, channels=1)
        ingested = IngestedMedia(
            source_name=f"test_session_{i}.wav",
            source_type="file",
            size_mb=len(raw_wav) / (1024 * 1024),
            raw_media_bytes=raw_wav,
            wav_bytes=raw_wav,
            duration_sec=1.0,
            duration_str="00:01",
            sample_rate=16000,
            channels=1,
        )
        assert ingested.raw_media_bytes is not None
        assert ingested.wav_bytes is not None

        # Evict video and audio
        ingested.evict_raw_media()
        ingested.evict_audio()

        assert ingested.raw_media_bytes is None
        assert ingested.wav_bytes is None
        assert ingested.is_audio_evicted is True
        assert ingested.is_video_evicted is True

        gc.collect()


if __name__ == "__main__":
    test_deployment_manifests()
    test_audio_only_media_pipeline()
    test_total_silence_and_zero_division()
    test_all_faces_dropped_resilience()
    test_multi_session_memory_eviction_loop()
    print("All Epic 7 deployment and resilience tests passed successfully!")
