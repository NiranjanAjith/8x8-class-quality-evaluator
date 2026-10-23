"""
Instructional Material Analyzer: Slide Transition Velocity & Visual Clutter.
Analyzes retained non-face frames to detect presentation pacing and visual complexity.
"""
import base64
from dataclasses import dataclass
from typing import List, Tuple
import cv2
import numpy as np
from src.vision.frame_sampler import TimestampedFrame


@dataclass
class ExtractedSlide:
    slide_id: str
    timestamp: str
    timestamp_sec: float
    title: str
    content_type: str  # "Presentation Deck", "Code Editor", "Digital Whiteboard"
    clutter_index: float  # 0.0 (clean) to 1.0 (cluttered)
    base64_jpeg: str  # Data URI for direct HTML/Streamlit image rendering


def compute_visual_clutter(image_bgr: np.ndarray) -> float:
    """
    Compute normalized visual clutter index (0.0 to 1.0) using edge density.
    Clean presentation slides with ample whitespace score <0.3.
    Dense text blocks, complex schematics, or unformatted code score >0.6.
    """
    if image_bgr is None or image_bgr.size == 0:
        return 0.0

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.count_nonzero(edges)) / float(gray.size)

    # Normalize edge density: typical slide edge density is 0.01 - 0.12
    normalized_clutter = min(1.0, max(0.0, edge_density / 0.10))
    return round(normalized_clutter, 2)


def classify_content_type(image_bgr: np.ndarray, clutter_index: float) -> str:
    """Classify instructional material into Deck, Code Editor, or Digital Whiteboard."""
    if image_bgr is None or image_bgr.size == 0:
        return "Presentation Deck"

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))

    # Dark background with moderate/high edge density -> Code Editor (dark theme)
    if mean_val < 90 and clutter_index >= 0.35:
        return "Code Editor"
    # Very bright with low clutter -> Digital Whiteboard or Clean Deck
    elif mean_val > 215:
        return "Digital Whiteboard" if clutter_index > 0.4 else "Presentation Deck"
    else:
        return "Presentation Deck"


def detect_slide_transitions(
    retained_frames: List[TimestampedFrame],
    delta_threshold: float = 0.20
) -> Tuple[List[ExtractedSlide], float]:
    """
    Identify distinct slide transitions across retained instructional frames.
    Compares frame-to-frame pixel dissimilarity.
    Returns:
        (extracted_slides, slide_velocity_minutes_per_slide)
    """
    if not retained_frames:
        return [], 0.0

    extracted_slides: List[ExtractedSlide] = []
    prev_comparison_gray: np.ndarray = None

    slide_counter = 1

    for f in retained_frames:
        # Resize to standardized thumbnail resolution for rapid structural comparison
        small_gray = cv2.cvtColor(
            cv2.resize(f.image_bgr, (160, 90), interpolation=cv2.INTER_AREA),
            cv2.COLOR_BGR2GRAY
        )

        is_new_slide = False
        if prev_comparison_gray is None:
            # First frame is always Slide 1
            is_new_slide = True
        else:
            # Compute normalized mean absolute difference
            diff = np.mean(np.abs(small_gray.astype(float) - prev_comparison_gray.astype(float))) / 255.0
            if diff >= delta_threshold:
                is_new_slide = True

        if is_new_slide:
            prev_comparison_gray = small_gray
            clutter = compute_visual_clutter(f.image_bgr)
            ctype = classify_content_type(f.image_bgr, clutter)
            b64_data = base64.b64encode(f.jpeg_bytes).decode("ascii") if f.jpeg_bytes else ""
            b64_uri = f"data:image/jpeg;base64,{b64_data}" if b64_data else ""

            slide_obj = ExtractedSlide(
                slide_id=f"slide_{slide_counter:02d}",
                timestamp=f.timestamp_str,
                timestamp_sec=f.timestamp_sec,
                title=f"Instructional Slide {slide_counter}",
                content_type=ctype,
                clutter_index=clutter,
                base64_jpeg=b64_uri,
            )
            extracted_slides.append(slide_obj)
            slide_counter += 1

    # Calculate average transition velocity: total minutes / total slides
    total_duration_sec = retained_frames[-1].timestamp_sec if retained_frames else 0.0
    total_minutes = total_duration_sec / 60.0
    slide_velocity_min = total_minutes / max(1, len(extracted_slides)) if extracted_slides else 0.0

    return extracted_slides, round(slide_velocity_min, 1)
