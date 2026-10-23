"""
In-Memory Voice Activity Detection (VAD) & Dead-Air Quantification.
Analyzes 16 kHz 16-bit mono PCM audio in 30ms frames to quantify active speech and silence voids.
Zero disk I/O; executes entirely in-memory.
"""
import io
import wave
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np


@dataclass
class SilenceGap:
    start_sec: float
    end_sec: float
    duration_sec: float
    timestamp_str: str


@dataclass
class VadResult:
    total_duration_sec: float
    speech_duration_sec: float
    silence_duration_sec: float
    dead_air_pct: float
    speech_ratio_pct: float
    silence_gaps: List[SilenceGap]
    total_silence_gaps: int


def compute_vad_timeline(
    wav_bytes: bytes,
    frame_duration_ms: int = 30,
    min_silence_gap_sec: float = 2.0
) -> VadResult:
    """
    Segment 16 kHz mono PCM into 30ms frames and compute speech vs. dead-air silence.
    - Slices audio into 480-sample frames (at 16 kHz, 30ms = 480 samples).
    - Uses adaptive Root Mean Square (RMS) energy thresholding.
    - Flags silence gaps exceeding min_silence_gap_sec (default 2.0s).
    """
    if not wav_bytes:
        return VadResult(
            total_duration_sec=0.0,
            speech_duration_sec=0.0,
            silence_duration_sec=0.0,
            dead_air_pct=0.0,
            speech_ratio_pct=0.0,
            silence_gaps=[],
            total_silence_gaps=0
        )

    try:
        # Extract raw PCM samples from WAV container
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            framerate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            n_frames = wf.getnframes()
            raw_pcm = wf.readframes(n_frames)

        if channels != 1 or sample_width != 2:
            # Fallback sample reading if not 16-bit mono
            samples = np.frombuffer(raw_pcm, dtype=np.int16)
        else:
            samples = np.frombuffer(raw_pcm, dtype=np.int16)

        total_samples = len(samples)
        if total_samples == 0:
            return VadResult(0.0, 0.0, 0.0, 0.0, 0.0, [], 0)

        total_duration_sec = total_samples / float(framerate)

        # 30ms window at framerate
        frame_samples = int(framerate * (frame_duration_ms / 1000.0))
        num_frames = total_samples // frame_samples

        if num_frames == 0:
            return VadResult(total_duration_sec, 0.0, total_duration_sec, 100.0, 0.0, [], 0)

        # Compute RMS energy per frame
        reshaped = samples[: num_frames * frame_samples].reshape(num_frames, frame_samples)
        rms_energies = np.sqrt(np.mean(reshaped.astype(float) ** 2, axis=1))

        # Ambient noise floor estimation capped to prevent speech suppression
        noise_floor = min(800.0, float(np.percentile(rms_energies, 10)))
        speech_threshold = max(250.0, noise_floor * 1.5)

        is_speech = rms_energies > speech_threshold
        speech_frame_count = int(np.count_nonzero(is_speech))
        speech_duration_sec = speech_frame_count * (frame_duration_ms / 1000.0)
        silence_duration_sec = max(0.0, total_duration_sec - speech_duration_sec)

        dead_air_pct = round((silence_duration_sec / total_duration_sec) * 100.0, 1)
        speech_ratio_pct = round(100.0 - dead_air_pct, 1)

        # Detect consecutive silence runs exceeding min_silence_gap_sec
        silence_gaps: List[SilenceGap] = []
        in_silence = False
        gap_start_idx = 0
        min_gap_frames = int(min_silence_gap_sec / (frame_duration_ms / 1000.0))

        for idx, speech_active in enumerate(is_speech):
            if not speech_active and not in_silence:
                in_silence = True
                gap_start_idx = idx
            elif speech_active and in_silence:
                in_silence = False
                gap_len = idx - gap_start_idx
                if gap_len >= min_gap_frames:
                    t_start = gap_start_idx * (frame_duration_ms / 1000.0)
                    t_end = idx * (frame_duration_ms / 1000.0)
                    mins = int(t_start // 60)
                    secs = int(t_start % 60)
                    silence_gaps.append(
                        SilenceGap(
                            start_sec=round(t_start, 1),
                            end_sec=round(t_end, 1),
                            duration_sec=round(t_end - t_start, 1),
                            timestamp_str=f"{mins:02d}:{secs:02d}",
                        )
                    )

        # Check trailing silence gap
        if in_silence:
            gap_len = len(is_speech) - gap_start_idx
            if gap_len >= min_gap_frames:
                t_start = gap_start_idx * (frame_duration_ms / 1000.0)
                t_end = len(is_speech) * (frame_duration_ms / 1000.0)
                mins = int(t_start // 60)
                secs = int(t_start % 60)
                silence_gaps.append(
                    SilenceGap(
                        start_sec=round(t_start, 1),
                        end_sec=round(t_end, 1),
                        duration_sec=round(t_end - t_start, 1),
                        timestamp_str=f"{mins:02d}:{secs:02d}",
                    )
                )

        return VadResult(
            total_duration_sec=round(total_duration_sec, 1),
            speech_duration_sec=round(speech_duration_sec, 1),
            silence_duration_sec=round(silence_duration_sec, 1),
            dead_air_pct=dead_air_pct,
            speech_ratio_pct=speech_ratio_pct,
            silence_gaps=silence_gaps,
            total_silence_gaps=len(silence_gaps)
        )

    except Exception:
        # Graceful fallback on malformed audio header
        return VadResult(
            total_duration_sec=0.0,
            speech_duration_sec=0.0,
            silence_duration_sec=0.0,
            dead_air_pct=0.0,
            speech_ratio_pct=0.0,
            silence_gaps=[],
            total_silence_gaps=0
        )
