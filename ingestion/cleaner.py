"""
Legal document text cleaner and normalizer.
Handles unicode normalization, whitespace cleanup, header/footer artifacts,
and legal citation formatting standardization.
"""

import re
import unicodedata


def clean_legal_text(text: str) -> str:
    """
    Cleans raw document text while preserving section structures,
    legal citations, and Indic characters (Hindi, Kannada).
    """
    if not text:
        return ""

    # Normalize unicode to NFKC (composes accents, normalizes compatibility chars)
    cleaned = unicodedata.normalize("NFKC", text)

    # Standardize line breaks
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters (except tab and newline)
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)

    # Normalize multiple blank lines to at most two
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Normalize excessive spaces and tabs
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)

    # Strip page number headers/footers common in legal court PDFs (e.g. "Page 1 of 12", "- 4 -")
    cleaned = re.sub(r'(?i)\bpage\s+\d+\s+(?:of\s+\d+)?\b', '', cleaned)
    cleaned = re.sub(r'(?m)^\s*[-—–]\s*\d+\s*[-—–]\s*$', '', cleaned)

    # Clean leading and trailing whitespace
    return cleaned.strip()
