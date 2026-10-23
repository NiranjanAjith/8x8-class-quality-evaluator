"""
In-Memory Media Loader for Files and Remote Stream URLs.
Enforces size ceilings, streaming abort guards, and zero disk writes.
"""
import io
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
import requests


MAX_ALLOWED_SIZE_MB = 200
DEFAULT_TIMEOUT_SEC = 30
CHUNK_SIZE_BYTES = 64 * 1024  # 64 KB


@dataclass
class MediaLoadResult:
    success: bool
    source_type: str  # "file" or "url"
    source_name: str
    data: bytes
    size_bytes: int
    size_mb: float
    content_type: str
    error_message: Optional[str] = None


def load_media_from_file(uploaded_file, max_size_mb: int = MAX_ALLOWED_SIZE_MB) -> MediaLoadResult:
    """
    Read an uploaded file (from st.file_uploader) directly into memory.
    Enforces maximum size bounds.
    """
    if uploaded_file is None:
        return MediaLoadResult(
            success=False,
            source_type="file",
            source_name="",
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type="",
            error_message="No file was uploaded."
        )

    file_name = getattr(uploaded_file, "name", "uploaded_media")
    content_type = getattr(uploaded_file, "type", "application/octet-stream")

    try:
        # Check size if available
        file_size = getattr(uploaded_file, "size", None)
        max_bytes = max_size_mb * 1024 * 1024
        if file_size and file_size > max_bytes:
            return MediaLoadResult(
                success=False,
                source_type="file",
                source_name=file_name,
                data=b"",
                size_bytes=file_size,
                size_mb=file_size / (1024 * 1024),
                content_type=content_type,
                error_message=f"File exceeds maximum allowed size of {max_size_mb} MB ({file_size / (1024*1024):.1f} MB detected)."
            )

        # Read into memory
        data = uploaded_file.read()
        actual_size = len(data)
        if actual_size > max_bytes:
            return MediaLoadResult(
                success=False,
                source_type="file",
                source_name=file_name,
                data=b"",
                size_bytes=actual_size,
                size_mb=actual_size / (1024 * 1024),
                content_type=content_type,
                error_message=f"File exceeds maximum allowed size of {max_size_mb} MB."
            )

        return MediaLoadResult(
            success=True,
            source_type="file",
            source_name=file_name,
            data=data,
            size_bytes=actual_size,
            size_mb=actual_size / (1024 * 1024),
            content_type=content_type
        )
    except Exception as e:
        return MediaLoadResult(
            success=False,
            source_type="file",
            source_name=file_name,
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type=content_type,
            error_message=f"Failed to read uploaded file: {str(e)}"
        )


def load_media_from_url(
    url: str,
    max_size_mb: int = MAX_ALLOWED_SIZE_MB,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC
) -> MediaLoadResult:
    """
    Stream a remote media file or 8x8 recording directly into memory.
    Enforces chunked reading with immediate abort if cumulative bytes exceed max_size_mb.
    """
    url = url.strip() if url else ""
    if not url:
        return MediaLoadResult(
            success=False,
            source_type="url",
            source_name="",
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type="",
            error_message="Empty URL provided."
        )

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return MediaLoadResult(
            success=False,
            source_type="url",
            source_name=url,
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type="",
            error_message=f"Invalid URL protocol '{parsed.scheme}://'. Only HTTP/HTTPS URLs are supported."
        )

    # Derive a display name from path
    source_name = parsed.path.split("/")[-1] if parsed.path else "remote_stream"
    if not source_name or source_name == "/":
        source_name = "remote_stream"

    max_bytes = max_size_mb * 1024 * 1024

    try:
        with requests.get(url, stream=True, timeout=timeout_sec, allow_redirects=True) as response:
            if response.status_code != 200:
                return MediaLoadResult(
                    success=False,
                    source_type="url",
                    source_name=source_name,
                    data=b"",
                    size_bytes=0,
                    size_mb=0.0,
                    content_type="",
                    error_message=f"HTTP request failed with status code {response.status_code} ({response.reason})."
                )

            content_type = response.headers.get("Content-Type", "application/octet-stream")
            content_len = response.headers.get("Content-Length")
            if content_len:
                try:
                    total_expected = int(content_len)
                    if total_expected > max_bytes:
                        return MediaLoadResult(
                            success=False,
                            source_type="url",
                            source_name=source_name,
                            data=b"",
                            size_bytes=total_expected,
                            size_mb=total_expected / (1024 * 1024),
                            content_type=content_type,
                            error_message=f"Remote media exceeds maximum allowed size of {max_size_mb} MB ({total_expected / (1024*1024):.1f} MB reported)."
                        )
                except ValueError:
                    pass

            # Chunked in-memory stream accumulation with abort guard
            buffer = io.BytesIO()
            accumulated = 0

            for chunk in response.iter_content(chunk_size=CHUNK_SIZE_BYTES):
                if chunk:
                    accumulated += len(chunk)
                    if accumulated > max_bytes:
                        del buffer
                        return MediaLoadResult(
                            success=False,
                            source_type="url",
                            source_name=source_name,
                            data=b"",
                            size_bytes=accumulated,
                            size_mb=accumulated / (1024 * 1024),
                            content_type=content_type,
                            error_message=f"Stream aborted: payload exceeded the maximum {max_size_mb} MB ceiling."
                        )
                    buffer.write(chunk)

            data = buffer.getvalue()
            del buffer
            actual_size = len(data)

            return MediaLoadResult(
                success=True,
                source_type="url",
                source_name=source_name,
                data=data,
                size_bytes=actual_size,
                size_mb=actual_size / (1024 * 1024),
                content_type=content_type
            )

    except requests.exceptions.Timeout:
        return MediaLoadResult(
            success=False,
            source_type="url",
            source_name=source_name,
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type="",
            error_message=f"Connection timed out after {timeout_sec} seconds while fetching the media stream."
        )
    except requests.exceptions.RequestException as e:
        return MediaLoadResult(
            success=False,
            source_type="url",
            source_name=source_name,
            data=b"",
            size_bytes=0,
            size_mb=0.0,
            content_type="",
            error_message=f"Failed to fetch remote media stream: {str(e)}"
        )
