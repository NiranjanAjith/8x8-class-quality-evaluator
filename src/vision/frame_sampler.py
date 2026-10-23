"""
In-Memory Sparse Video Frame Sampler.
Extracts periodic video frames directly from memory buffers using FFmpeg pipes.
Zero video files are written to disk.
"""
import io
import subprocess
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from src.ingestion.audio_extractor import get_ffmpeg_binary


@dataclass
class TimestampedFrame:
    frame_index: int
    timestamp_sec: float
    timestamp_str: str
    image_bgr: np.ndarray
    jpeg_bytes: bytes


def sample_sparse_frames(
    video_bytes: bytes,
    sample_interval_sec: float = 5.0
) -> List[TimestampedFrame]:
    """
    Extract video frames at sparse intervals (default: 1 frame every 5s) directly in-memory.
    Scales frames down to 640px width to minimize memory footprint while preserving slide text.
    Returns empty list if media contains no video stream (e.g., audio-only files).
    """
    if not video_bytes:
        return []

    try:
        ffmpeg_bin = get_ffmpeg_binary()
    except Exception:
        return []

    # In-memory streaming pipe: extracts 1 frame every N seconds as MJPEG stream to stdout
    fps_filter = f"fps=1/{sample_interval_sec},scale=640:-1"
    cmd = [
        ffmpeg_bin,
        "-v", "error",
        "-y",
        "-i", "pipe:0",
        "-vf", fps_filter,
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-q:v", "4",
        "pipe:1"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_data, stderr_data = process.communicate(input=video_bytes)

        if process.returncode != 0 or not stdout_data:
            # Media may be audio-only or invalid video container
            return []

        # Parse individual JPEG frames from the MJPEG byte stream
        # JPEG SOI: 0xFF 0xD8, EOI: 0xFF 0xD9
        raw_stream = stdout_data
        frames: List[TimestampedFrame] = []
        offset = 0
        frame_idx = 0

        # Lazy import of cv2
        import cv2

        while offset < len(raw_stream):
            start = raw_stream.find(b"\xff\xd8", offset)
            if start == -1:
                break
            end = raw_stream.find(b"\xff\xd9", start + 2)
            if end == -1:
                break

            jpeg_data = raw_stream[start : end + 2]
            offset = end + 2

            # Decode JPEG in-memory into OpenCV BGR image array
            np_arr = np.frombuffer(jpeg_data, dtype=np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is not None:
                t_sec = frame_idx * sample_interval_sec
                mins = int(t_sec // 60)
                secs = int(t_sec % 60)
                t_str = f"{mins:02d}:{secs:02d}"

                frames.append(
                    TimestampedFrame(
                        frame_index=frame_idx,
                        timestamp_sec=t_sec,
                        timestamp_str=t_str,
                        image_bgr=img,
                        jpeg_bytes=jpeg_data,
                    )
                )
                frame_idx += 1

        return frames

    except Exception:
        return []
