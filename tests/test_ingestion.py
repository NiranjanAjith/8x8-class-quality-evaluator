"""
Unit & Integration Tests for Epic 2: Media Ingestion & Ephemeral Lifecycle.
"""
import io
import math
import struct
import wave
from src.ingestion.media_loader import load_media_from_file, load_media_from_url, MediaLoadResult
from src.ingestion.audio_extractor import extract_audio_pcm_16k, get_ffmpeg_binary
from src.ingestion.lifecycle import EphemeralAudioBuffer


def create_synthetic_wav(duration_sec: float = 2.0, sample_rate: int = 44100, channels: int = 2) -> bytes:
    """Generate in-memory synthetic stereo WAV audio (440Hz sine wave)."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        num_frames = int(duration_sec * sample_rate)
        frames = []
        for i in range(num_frames):
            val = int(32767.0 * 0.4 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            # stereo: duplicate sample for both channels
            if channels == 2:
                frames.append(struct.pack("<hh", val, val))
            else:
                frames.append(struct.pack("<h", val))
        wf.writeframes(b"".join(frames))
    return buffer.getvalue()


class MockUploadedFile:
    """Mock Streamlit UploadedFile object."""
    def __init__(self, name: str, data: bytes, content_type: str = "audio/wav"):
        self.name = name
        self._data = data
        self.size = len(data)
        self.type = content_type

    def read(self) -> bytes:
        return self._data


def test_ffmpeg_binary_availability():
    """Verify FFmpeg binary can be located."""
    ffmpeg_path = get_ffmpeg_binary()
    assert ffmpeg_path is not None
    assert len(ffmpeg_path) > 0


def test_load_media_from_file():
    """Verify local file ingestion and size validation."""
    raw_audio = create_synthetic_wav(duration_sec=1.0)
    mock_file = MockUploadedFile("test_audio.wav", raw_audio)

    res = load_media_from_file(mock_file, max_size_mb=10)
    assert res.success is True
    assert res.source_type == "file"
    assert res.source_name == "test_audio.wav"
    assert res.size_bytes == len(raw_audio)
    assert len(res.data) == len(raw_audio)


def test_load_media_from_file_size_limit():
    """Verify file exceeding size ceiling is rejected."""
    raw_audio = create_synthetic_wav(duration_sec=1.0)
    mock_file = MockUploadedFile("huge.wav", raw_audio)

    # Set threshold lower than audio size (e.g. 0.0001 MB)
    res = load_media_from_file(mock_file, max_size_mb=0)
    assert res.success is False
    assert "exceeds maximum allowed size" in res.error_message


def test_load_media_from_invalid_url():
    """Verify invalid URL protocols are rejected."""
    res = load_media_from_url("ftp://example.com/audio.mp3")
    assert res.success is False
    assert "Invalid URL protocol" in res.error_message


def test_audio_extraction_and_normalization():
    """
    Test FFmpeg extraction: converts 44.1kHz stereo audio to 16kHz mono 16-bit PCM WAV.
    """
    stereo_44k = create_synthetic_wav(duration_sec=2.5, sample_rate=44100, channels=2)

    res = extract_audio_pcm_16k(stereo_44k, target_sr=16000)
    assert res.success is True
    assert res.channels == 1, f"Expected 1 channel (mono), got {res.channels}"
    assert res.sample_rate == 16000, f"Expected 16000 Hz, got {res.sample_rate}"
    assert res.sample_width == 2, f"Expected 2 bytes (16-bit), got {res.sample_width}"
    assert abs(res.duration_sec - 2.5) < 0.1, f"Expected ~2.5s duration, got {res.duration_sec}"
    assert len(res.wav_bytes) > 0


def test_ephemeral_lifecycle_guard():
    """Verify buffer is explicitly purged on context exit and cannot be accessed."""
    raw_data = b"ephemeral_sample_audio_buffer_data"
    
    with EphemeralAudioBuffer(raw_data, description="Test Buffer") as buf:
        assert buf.is_active is True
        assert buf.get_data() == raw_data
        assert buf.allocated_bytes == len(raw_data)

    # After context exit
    assert buf.is_active is False
    assert buf.evicted_at is not None
    raised = False
    try:
        buf.get_data()
    except RuntimeError:
        raised = True
    assert raised is True, "Expected RuntimeError when accessing evicted buffer."


if __name__ == "__main__":
    test_ffmpeg_binary_availability()
    test_load_media_from_file()
    test_load_media_from_file_size_limit()
    test_load_media_from_invalid_url()
    test_audio_extraction_and_normalization()
    test_ephemeral_lifecycle_guard()
    print("All Epic 2 ingestion and lifecycle tests passed successfully!")
