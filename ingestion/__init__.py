"""
Ingestion module for multilingual legal documents.
Provides document parsing (PDF, DOCX, images via OCR),
cleaning, language detection, and legal-aware chunking.
"""

from .parser import extract_text_from_file, extract_text_from_image, is_tesseract_available
from .cleaner import clean_legal_text
from .language_detect import detect_language, get_language_display_name
from .chunker import chunk_legal_statute, LegalChunk

__all__ = [
    "extract_text_from_file",
    "extract_text_from_image",
    "is_tesseract_available",
    "clean_legal_text",
    "detect_language",
    "get_language_display_name",
    "chunk_legal_statute",
    "LegalChunk",
]
