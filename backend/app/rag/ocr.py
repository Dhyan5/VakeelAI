"""
Nyaya – OCR and text extraction from various document formats.
Handles PDF (text and scanned), DOCX, TXT, HTML.
"""

import io
import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text(file_path: str, file_bytes: Optional[bytes] = None) -> str:
    """Extract text from a file, auto-detecting format."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if file_bytes is None:
        file_bytes = path.read_bytes()

    if suffix == ".txt":
        return file_bytes.decode("utf-8", errors="replace")
    elif suffix == ".html" or suffix == ".htm":
        return _extract_html(file_bytes)
    elif suffix == ".docx":
        return _extract_docx(file_bytes)
    elif suffix == ".pdf":
        return _extract_pdf(file_path, file_bytes)
    else:
        # Try as plain text
        return file_bytes.decode("utf-8", errors="replace")


def _extract_html(data: bytes) -> str:
    """Extract text from HTML."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(data, "html.parser")
        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except ImportError:
        # Fallback: strip tags with regex
        text = data.decode("utf-8", errors="replace")
        return re.sub(r"<[^>]+>", " ", text)


def _extract_docx(data: bytes) -> str:
    """Extract text from DOCX."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        logger.warning("python-docx not installed. Cannot extract DOCX.")
        return ""


def _extract_pdf(file_path: str, data: bytes) -> str:
    """Extract text from PDF, with OCR fallback for scanned docs."""
    text = ""

    # Try PyMuPDF first (fast, accurate)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=data, filetype="pdf")
        pages_text = []
        for page in doc:
            page_text = page.get_text()
            pages_text.append(page_text)
        text = "\n\n".join(pages_text)
        doc.close()
    except ImportError:
        # Fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)
                text = "\n\n".join(pages_text)
        except ImportError:
            logger.warning("No PDF library available (pymupdf or pdfplumber).")
            return ""

    # Check if text yield is too low (likely scanned) → try OCR
    if _is_scanned(text, data):
        logger.info(f"Low text yield in {file_path}, attempting OCR...")
        ocr_text = _run_ocr(data)
        if ocr_text and len(ocr_text) > len(text):
            text = ocr_text

    return text


def _is_scanned(text: str, pdf_bytes: bytes) -> bool:
    """Heuristic: if text is very short relative to file size, likely scanned."""
    if not text.strip():
        return True
    # If less than 100 chars per 100KB of PDF, probably scanned
    ratio = len(text) / (len(pdf_bytes) / 1024)
    return ratio < 10


def _run_ocr(pdf_bytes: bytes) -> str:
    """Run OCR on a scanned PDF using pytesseract."""
    try:
        import fitz
        from PIL import Image
        import pytesseract

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        ocr_pages = []

        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # OCR with Hindi + English
            page_text = pytesseract.image_to_string(img, lang="hin+eng")
            ocr_pages.append(page_text)

        doc.close()
        return "\n\n".join(ocr_pages)
    except ImportError as e:
        logger.warning(f"OCR dependencies missing: {e}")
        return ""
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


def detect_act_name(filename: str, text: str) -> tuple[Optional[str], Optional[int]]:
    """Try to auto-detect the act name and year from filename or first page."""
    name = None
    year = None

    # Try filename first
    clean = Path(filename).stem.replace("_", " ").replace("-", " ")
    # Look for year pattern
    year_match = re.search(r"(1[89]\d{2}|20[0-2]\d)", clean)
    if year_match:
        year = int(year_match.group(1))
        clean = clean[:year_match.start()].strip().rstrip(",").strip()

    if len(clean) > 5:
        name = clean.title()

    # If not found in filename, try first 500 chars of text
    if not name and text:
        first_page = text[:500]
        # Common pattern: "THE INDIAN CONTRACT ACT, 1872"
        act_match = re.search(
            r"(?:THE\s+)?(.+?(?:ACT|SANHITA|ADHINIYAM|CODE|BILL))\s*[,.]?\s*(1[89]\d{2}|20[0-2]\d)?",
            first_page,
            re.IGNORECASE,
        )
        if act_match:
            name = act_match.group(1).strip().title()
            if act_match.group(2):
                year = int(act_match.group(2))

    return name, year
