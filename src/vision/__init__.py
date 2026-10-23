"""
Face-Filtered Visual Content Engine Package.
Extracts instructional slide telemetry and discards human face frames.
"""
from src.vision.frame_sampler import sample_sparse_frames, TimestampedFrame
from src.vision.face_filter import detect_face_in_frame, filter_non_face_frames
from src.vision.slide_analyzer import (
    detect_slide_transitions,
    compute_visual_clutter,
    ExtractedSlide,
)
from src.vision.pipeline import (
    run_visual_telemetry_pipeline,
    VisualTelemetryResult,
)

__all__ = [
    "sample_sparse_frames",
    "TimestampedFrame",
    "detect_face_in_frame",
    "filter_non_face_frames",
    "detect_slide_transitions",
    "compute_visual_clutter",
    "ExtractedSlide",
    "run_visual_telemetry_pipeline",
    "VisualTelemetryResult",
]
