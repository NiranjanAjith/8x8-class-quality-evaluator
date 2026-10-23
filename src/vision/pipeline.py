"""
Visual Content Engine Pipeline Orchestrator.
Coordinates sparse frame extraction, biometric invalidation filtering,
slide transition velocity analysis, and ephemeral memory cleanup.
"""
from dataclasses import dataclass
from typing import List, Optional
from src.vision.frame_sampler import sample_sparse_frames
from src.vision.face_filter import filter_non_face_frames
from src.vision.slide_analyzer import detect_slide_transitions, ExtractedSlide


@dataclass
class VisualTelemetryResult:
    success: bool
    total_frames_sampled: int
    face_frames_dropped: int
    instructional_frames_retained: int
    slide_count: int
    slide_velocity_min: float
    slides: List[ExtractedSlide]
    error_message: Optional[str] = None


def run_visual_telemetry_pipeline(
    video_bytes: bytes,
    sample_interval_sec: float = 5.0
) -> VisualTelemetryResult:
    """
    Run complete visual content telemetry pipeline:
    1. Sparse frame extraction via in-memory FFmpeg pipe.
    2. Face detection invalidation: automatically drop all face frames (0 biometric storage).
    3. Structural slide change detection (transition velocity & timestamps).
    4. Visual clutter & layout complexity indexing.
    """
    if not video_bytes:
        return VisualTelemetryResult(
            success=True,
            total_frames_sampled=0,
            face_frames_dropped=0,
            instructional_frames_retained=0,
            slide_count=0,
            slide_velocity_min=0.0,
            slides=[],
            error_message="No video payload provided."
        )

    try:
        # Step 1: Sparse frame sampling
        sampled_frames = sample_sparse_frames(video_bytes, sample_interval_sec=sample_interval_sec)
        total_sampled = len(sampled_frames)

        if total_sampled == 0:
            # Media stream has no video track (e.g. audio-only WAV/MP3)
            return VisualTelemetryResult(
                success=True,
                total_frames_sampled=0,
                face_frames_dropped=0,
                instructional_frames_retained=0,
                slide_count=0,
                slide_velocity_min=0.0,
                slides=[],
            )

        # Step 2: Biometric invalidation gate (drop all face frames)
        retained_frames, total_checked, faces_dropped = filter_non_face_frames(sampled_frames)

        # Step 3: Slide transition detection & clutter extraction
        extracted_slides, slide_velocity = detect_slide_transitions(retained_frames)

        return VisualTelemetryResult(
            success=True,
            total_frames_sampled=total_sampled,
            face_frames_dropped=faces_dropped,
            instructional_frames_retained=len(retained_frames),
            slide_count=len(extracted_slides),
            slide_velocity_min=slide_velocity,
            slides=extracted_slides,
        )

    except Exception as e:
        return VisualTelemetryResult(
            success=False,
            total_frames_sampled=0,
            face_frames_dropped=0,
            instructional_frames_retained=0,
            slide_count=0,
            slide_velocity_min=0.0,
            slides=[],
            error_message=f"Visual pipeline failure: {str(e)}"
        )
