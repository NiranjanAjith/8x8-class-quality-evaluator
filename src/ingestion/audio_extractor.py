"""
In-Memory Audio Extraction & Normalization using FFmpeg.
Extracts audio from video/audio streams and downsamples to 16 kHz mono 16-bit PCM WAV in memory.
Zero unencrypted media is written to persistent disk.
"""
import io
import os
import shutil
import subprocess
import wave
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioExtractionResult:
    success: bool
    wav_bytes: bytes
    sample_rate: int
    channels: int
    sample_width: int
    duration_sec: float
    duration_str: str
    size_bytes: int
    error_message: Optional[str] = None


def get_ffmpeg_binary() -> str:
    """
    Locate the FFmpeg binary dynamically:
    1. System PATH
    2. Homebrew default path
    3. Bundled imageio-ffmpeg static binary
    """
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg

    homebrew_ffmpeg = "/opt/homebrew/bin/ffmpeg"
    if os.path.exists(homebrew_ffmpeg) and os.access(homebrew_ffmpeg, os.X_OK):
        return homebrew_ffmpeg

    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        raise RuntimeError(
            "FFmpeg executable not found on system PATH, Homebrew, or via imageio-ffmpeg. "
            "Please ensure ffmpeg or imageio-ffmpeg is installed."
        ) from e


def extract_audio_pcm_16k(media_bytes: bytes, target_sr: int = 16000) -> AudioExtractionResult:
    """
    Stream media bytes through an in-memory FFmpeg process to extract and normalize audio:
    - Drops video stream (-vn)
    - Converts codec to 16-bit signed PCM (-acodec pcm_s16le)
    - Downmixes to single mono channel (-ac 1)
    - Resamples to 16,000 Hz (-ar 16000)
    - Emits WAV container directly to stdout pipe
    """
    if not media_bytes:
        return AudioExtractionResult(
            success=False,
            wav_bytes=b"",
            sample_rate=0,
            channels=0,
            sample_width=0,
            duration_sec=0.0,
            duration_str="0m 0s",
            size_bytes=0,
            error_message="Empty media payload provided for audio extraction."
        )

    try:
        ffmpeg_bin = get_ffmpeg_binary()
    except Exception as e:
        return AudioExtractionResult(
            success=False,
            wav_bytes=b"",
            sample_rate=0,
            channels=0,
            sample_width=0,
            duration_sec=0.0,
            duration_str="0m 0s",
            size_bytes=0,
            error_message=str(e)
        )

    # In-memory streaming pipes: stdin -> stdout
    cmd = [
        ffmpeg_bin,
        "-v", "error",
        "-y",
        "-i", "pipe:0",
        "-vn",
        "-acodec", "pcm_s16le",
        "-ac", "1",
        "-ar", str(target_sr),
        "-f", "wav",
        "pipe:1"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_data, stderr_data = process.communicate(input=media_bytes)

        if process.returncode != 0:
            err_msg = stderr_data.decode("utf-8", errors="replace").strip()
            return AudioExtractionResult(
                success=False,
                wav_bytes=b"",
                sample_rate=0,
                channels=0,
                sample_width=0,
                duration_sec=0.0,
                duration_str="0m 0s",
                size_bytes=0,
                error_message=f"FFmpeg extraction failed (code {process.returncode}): {err_msg}"
            )

        wav_bytes = stdout_data
        actual_size = len(wav_bytes)

        # Patch streaming WAV headers (FFmpeg writes 0x7FFFFFFF when piping to stdout)
        # to ensure standard wave parsers and browser players read exact duration and boundaries.
        data_idx = wav_bytes.find(b"data")
        if data_idx != -1 and actual_size > data_idx + 8:
            pcm_bytes_len = actual_size - (data_idx + 8)
            wav_ba = bytearray(wav_bytes)
            import struct
            struct.pack_into("<I", wav_ba, 4, max(0, actual_size - 8))
            struct.pack_into("<I", wav_ba, data_idx + 4, pcm_bytes_len)
            wav_bytes = bytes(wav_ba)

        # Inspect WAV header in-memory using standard library wave
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            duration_sec = n_frames / float(framerate) if framerate > 0 else 0.0

        mins = int(duration_sec // 60)
        secs = int(duration_sec % 60)
        duration_str = f"{mins}m {secs}s"

        return AudioExtractionResult(
            success=True,
            wav_bytes=wav_bytes,
            sample_rate=framerate,
            channels=channels,
            sample_width=sample_width,
            duration_sec=duration_sec,
            duration_str=duration_str,
            size_bytes=actual_size
        )

    except Exception as e:
        return AudioExtractionResult(
            success=False,
            wav_bytes=b"",
            sample_rate=0,
            channels=0,
            sample_width=0,
            duration_sec=0.0,
            duration_str="0m 0s",
            size_bytes=0,
            error_message=f"Unexpected error during audio extraction: {str(e)}"
        )
