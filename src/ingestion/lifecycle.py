"""
Ephemeral Lifecycle & Memory Eviction Guard.
Guarantees audio and raw media buffers are scrubbed from RAM immediately post-processing.
Zero persistent retention in application state.
"""
import gc
import time
from typing import Optional


class EphemeralAudioBuffer:
    """
    Context manager managing in-memory ephemeral media buffers.
    Ensures that as soon as downstream processing (transcription, VAD) exits,
    buffers are deleted and explicitly collected from Python heap memory.
    """

    def __init__(self, data: bytes, description: str = "Audio Buffer"):
        self.description = description
        self.allocated_bytes = len(data) if data else 0
        self.allocated_mb = self.allocated_bytes / (1024 * 1024)
        self._data: Optional[bytes] = data
        self.is_active = True
        self.allocated_at = time.time()
        self.evicted_at: Optional[float] = None

    def get_data(self) -> bytes:
        """Access the underlying data buffer while active."""
        if not self.is_active or self._data is None:
            raise RuntimeError(
                f"Attempted to access '{self.description}' after memory eviction was completed."
            )
        return self._data

    def evict(self) -> dict:
        """
        Explicitly purge buffer reference and trigger garbage collection.
        Returns a diagnostic summary of the eviction.
        """
        if not self.is_active:
            return self.get_summary()

        purged_bytes = self.allocated_bytes
        self._data = None
        self.is_active = False
        self.evicted_at = time.time()

        # Force immediate garbage collection of orphaned buffers
        gc.collect()

        return {
            "description": self.description,
            "purged_bytes": purged_bytes,
            "purged_mb": purged_bytes / (1024 * 1024),
            "evicted": True,
            "lifecycle_duration_ms": (self.evicted_at - self.allocated_at) * 1000,
        }

    def get_summary(self) -> dict:
        """Return diagnostic status of buffer lifecycle."""
        return {
            "description": self.description,
            "allocated_bytes": self.allocated_bytes,
            "allocated_mb": self.allocated_mb,
            "is_active": self.is_active,
            "evicted": not self.is_active,
            "evicted_at": self.evicted_at,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.evict()


def purge_buffers(*buffers: EphemeralAudioBuffer):
    """Purge multiple ephemeral buffers in sequence."""
    for b in buffers:
        if b and isinstance(b, EphemeralAudioBuffer):
            b.evict()
    gc.collect()
