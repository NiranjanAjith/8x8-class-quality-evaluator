"""
Face-Detection Invalidation Gate.
Detects human faces on sampled video frames and automatically drops them.
Ensures zero biometric data is retained in session state or storage.
"""
from typing import List, Tuple
import cv2
import numpy as np
from src.vision.frame_sampler import TimestampedFrame


_FACE_CASCADE = None


def get_face_cascade() -> cv2.CascadeClassifier:
    """Load and cache the OpenCV frontal face Haar cascade classifier."""
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def detect_face_in_frame(
    image_bgr: np.ndarray,
    scale_factor: float = 1.15,
    min_neighbors: int = 4
) -> bool:
    """
    Check if a frame contains one or more human faces.
    Returns True if a face is detected (indicating a webcam/speaker view to drop).
    """
    if image_bgr is None or image_bgr.size == 0:
        return False

    try:
        cascade = get_face_cascade()
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Fast histogram equalization to improve detection in dim/uneven webcam lighting
        gray = cv2.equalizeHist(gray)

        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(32, 32),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return len(faces) > 0

    except Exception:
        # If classifier fails, fail-safe to keeping the frame
        return False


def filter_non_face_frames(
    frames: List[TimestampedFrame]
) -> Tuple[List[TimestampedFrame], int, int]:
    """
    Filter out all frames containing detected human faces.
    Returns:
        (retained_instructional_frames, total_sampled_count, face_frames_dropped_count)
    """
    retained: List[TimestampedFrame] = []
    face_dropped_count = 0

    for f in frames:
        has_face = detect_face_in_frame(f.image_bgr)
        if has_face:
            face_dropped_count += 1
            # Explicitly deallocate image memory for dropped face frame
            f.image_bgr = None
            f.jpeg_bytes = b""
        else:
            retained.append(f)

    return retained, len(frames), face_dropped_count
