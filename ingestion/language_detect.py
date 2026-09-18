"""
Language detection utility for English, Hindi, and Kannada.
Combines unicode character script heuristics (highly reliable for Indic scripts)
with statistical fallback (langdetect) for edge cases.
"""

import re
from typing import Tuple

# Unicode script ranges
# Devanagari: U+0900 - U+097F
DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')
# Kannada: U+0C80 - U+0CFF
KANNADA_REGEX = re.compile(r'[\u0C80-\u0CFF]')

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the primary language of the input text.
    Returns a tuple of (lang_code, confidence) where lang_code is 'en', 'hi', or 'kn'.
    """
    if not text or not text.strip():
        return "en", 1.0

    sample = text.strip()
    total_chars = len(sample)

    # Count script characters
    devanagari_count = len(DEVANAGARI_REGEX.findall(sample))
    kannada_count = len(KANNADA_REGEX.findall(sample))

    # If significant Kannada characters exist (indicative of Kannada or code-mix)
    if kannada_count > 0 and (kannada_count / max(total_chars, 1) > 0.05 or kannada_count >= 5):
        confidence = min(0.99, max(0.60, kannada_count / total_chars * 2))
        return "kn", float(confidence)

    # If significant Devanagari characters exist (indicative of Hindi or code-mix)
    if devanagari_count > 0 and (devanagari_count / max(total_chars, 1) > 0.05 or devanagari_count >= 5):
        confidence = min(0.99, max(0.60, devanagari_count / total_chars * 2))
        return "hi", float(confidence)

    # Fallback to langdetect if available
    try:
        from langdetect import detect_langs
        predictions = detect_langs(sample)
        if predictions:
            top = predictions[0]
            if top.lang in ["hi", "kn", "en"]:
                return top.lang, float(top.prob)
    except Exception:
        pass

    # Default to English
    return "en", 0.95


def get_language_display_name(lang_code: str) -> str:
    """Return friendly display name for language code."""
    return LANGUAGE_NAMES.get(lang_code.lower(), "English")
