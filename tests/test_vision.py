"""
Unit Tests for Epic 3: Face-Filtered Visual Content Engine.
"""
import numpy as np
import cv2
from src.vision.slide_analyzer import compute_visual_clutter, detect_slide_transitions
from src.vision.face_filter import detect_face_in_frame, filter_non_face_frames
from src.vision.frame_sampler import TimestampedFrame
from src.vision.pipeline import run_visual_telemetry_pipeline


def test_visual_clutter_computation():
    """Verify clean slides yield low clutter, and complex text yields higher clutter."""
    # 1. Clean white canvas (minimal edges)
    clean_slide = np.full((360, 640, 3), 255, dtype=np.uint8)
    cv2.putText(clean_slide, "Title", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    clutter_clean = compute_visual_clutter(clean_slide)
    assert clutter_clean < 0.25, f"Expected clean slide clutter < 0.25, got {clutter_clean}"

    # 2. Cluttered canvas with dense lines/text
    cluttered_slide = np.full((360, 640, 3), 240, dtype=np.uint8)
    for y in range(30, 350, 20):
        cv2.line(cluttered_slide, (20, y), (620, y), (0, 0, 0), 1)
        cv2.putText(cluttered_slide, f"Dense code line trace pointer {y}", (30, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 20, 20), 1)
    clutter_dense = compute_visual_clutter(cluttered_slide)
    assert clutter_dense > clutter_clean, "Expected dense slide to have higher clutter than clean slide."


def test_face_detection_on_uniform_image():
    """Verify uniform slides do not falsely trigger face detection."""
    slide = np.full((360, 640, 3), 250, dtype=np.uint8)
    cv2.putText(slide, "Mathematics Lecture: Vector Spaces", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    has_face = detect_face_in_frame(slide)
    assert has_face is False


def test_slide_transitions_detection():
    """Verify static video frames do not trigger multiple slide transitions."""
    # 3 identical frames
    img1 = np.full((180, 320, 3), 255, dtype=np.uint8)
    cv2.putText(img1, "Slide A", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    _, jpeg1 = cv2.imencode(".jpg", img1)

    frames = [
        TimestampedFrame(0, 0.0, "00:00", img1.copy(), jpeg1.tobytes()),
        TimestampedFrame(1, 5.0, "00:05", img1.copy(), jpeg1.tobytes()),
        TimestampedFrame(2, 10.0, "00:10", img1.copy(), jpeg1.tobytes()),
    ]

    slides, velocity = detect_slide_transitions(frames, delta_threshold=0.20)
    assert len(slides) == 1, f"Expected 1 slide for static content, got {len(slides)}"

    # Add a transition to Slide B (completely inverted black background)
    img2 = np.full((180, 320, 3), 30, dtype=np.uint8)
    cv2.putText(img2, "Slide B: New Topic", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    _, jpeg2 = cv2.imencode(".jpg", img2)
    frames.append(TimestampedFrame(3, 15.0, "00:15", img2, jpeg2.tobytes()))

    slides_after, velocity_after = detect_slide_transitions(frames, delta_threshold=0.20)
    assert len(slides_after) == 2, f"Expected 2 slides after transition, got {len(slides_after)}"


def test_pipeline_on_empty_payload():
    """Verify graceful handling when no video stream is present."""
    res = run_visual_telemetry_pipeline(b"")
    assert res.success is True
    assert res.slide_count == 0
    assert len(res.slides) == 0


if __name__ == "__main__":
    test_visual_clutter_computation()
    test_face_detection_on_uniform_image()
    test_slide_transitions_detection()
    test_pipeline_on_empty_payload()
    print("All Epic 3 vision tests passed successfully!")
