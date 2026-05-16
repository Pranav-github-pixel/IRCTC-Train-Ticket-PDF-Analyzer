"""General-purpose helper functions used across the application."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from utils.constants import DATE_ONLY_FORMATS, DATETIME_FORMATS


def safe_parse_datetime(text: Optional[str]) -> Optional[datetime]:
    """Attempt to parse *text* into a datetime using known IRCTC formats.

    Tries full datetime formats first, then date-only formats (midnight).

    Args:
        text: Raw date/time string from the PDF.

    Returns:
        Parsed datetime or None if all formats fail.
    """
    if not text:
        return None

    cleaned = clean_text(text)

    # Try full datetime formats
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    # Fallback: date-only formats (assume 00:00)
    for fmt in DATE_ONLY_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    return None


def safe_parse_float(text: Optional[str]) -> Optional[float]:
    """Parse a currency/numeric string into a float.

    Handles rupee symbols (₹, Rs., Rs, INR), commas, and whitespace.

    Args:
        text: Raw currency string from the PDF.

    Returns:
        Parsed float or None.
    """
    if not text:
        return None

    # Strip currency prefixes and whitespace
    cleaned = re.sub(r"[₹]|Rs\.?|INR", "", text, flags=re.IGNORECASE).strip()
    # Remove commas used as thousands separators
    cleaned = cleaned.replace(",", "")
    # Remove any remaining non-numeric chars except dot and minus
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)

    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters.

    Args:
        text: Raw text from PDF extraction.

    Returns:
        Cleaned, single-spaced text.
    """
    # Replace common PDF artifacts
    text = text.replace("\xa0", " ")  # Non-breaking space
    text = text.replace("\t", " ")
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def ensure_dir(path: Path) -> None:
    """Create *path* and all parents if they don't exist.

    Args:
        path: Directory path to ensure.
    """
    path.mkdir(parents=True, exist_ok=True)


def truncate(text: Optional[str], max_length: int = 50) -> str:
    """Truncate *text* for display purposes.

    Args:
        text: Input string.
        max_length: Maximum characters before truncation.

    Returns:
        Truncated string with ellipsis, or empty string if input is None.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
