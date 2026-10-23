"""
Lightweight Regex Transcript Text PII Sanitizer (Option A).
Redacts structured identifiers (emails, phone numbers, URLs, student IDs)
and standardizes instructor and participant references before UI or model ingestion.
Zero external API overhead; executes in milliseconds.
"""
import re
from typing import Dict, Tuple


# Pre-compiled high-performance regex patterns
_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    re.IGNORECASE
)

_PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

_URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)[^\s/$.?#].[^\s]*\b",
    re.IGNORECASE
)

_STUDENT_ID_PATTERN = re.compile(
    r"\b(?:ID|Student\s*ID|Roll\s*(?:No|Number|Num)?|Badge|SSN)[\s:#-]*[A-Za-z0-9-]{4,12}\b",
    re.IGNORECASE
)

_TEACHER_TITLE_PATTERN = re.compile(
    r"\b(?:Prof\.|Professor|Dr\.|Doctor|Mr\.|Ms\.|Mrs\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b"
)

_GREETING_VOCATIVE_PATTERN = re.compile(
    r"\b(Hey|Hi|Hello|Thanks|Thank you|Good job|Well done|Great work|Yes|No)\s+([A-Z][a-z]+)\b"
)


def sanitize_transcript_text(text: str) -> str:
    """
    Scrub structured PII from transcript text using deterministic regex rules:
    - Emails -> [EMAIL]
    - Phone Numbers -> [PHONE]
    - URLs -> [URL]
    - Student IDs -> [STUDENT_ID]
    - Teacher/Instructor titles -> [Teacher]
    - Spoken student names -> [Student]
    """
    if not text:
        return ""

    sanitized = text

    # 1. Scrub Emails
    sanitized = _EMAIL_PATTERN.sub("[EMAIL]", sanitized)

    # 2. Scrub Phone Numbers
    sanitized = _PHONE_PATTERN.sub("[PHONE]", sanitized)

    # 3. Scrub URLs
    sanitized = _URL_PATTERN.sub("[URL]", sanitized)

    # 4. Scrub Student IDs
    sanitized = _STUDENT_ID_PATTERN.sub("[STUDENT_ID]", sanitized)

    # 5. Standardize Instructor References
    sanitized = _TEACHER_TITLE_PATTERN.sub("[Teacher]", sanitized)

    # 6. Standardize Greeting Student Vocatives (e.g. "Thanks John" -> "Thanks [Student]")
    sanitized = _GREETING_VOCATIVE_PATTERN.sub(r"\1 [Student]", sanitized)

    return sanitized


def sanitize_segments_batch(segments: list) -> list:
    """
    Sanitize text across a list of segment dictionaries or TranscribedSegment objects.
    """
    for s in segments:
        if hasattr(s, "text"):
            s.text = sanitize_transcript_text(s.text)
        elif isinstance(s, dict) and "text" in s:
            s["text"] = sanitize_transcript_text(s["text"])
    return segments
