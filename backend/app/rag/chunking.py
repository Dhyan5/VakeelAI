"""
Nyaya – Document chunking: structural splitting for legal documents.
Splits by Article / Section / Order-Rule / Paragraph, keeping provisos,
explanations, and illustrations with their parent section.
"""

import re
import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chunk:
    """A single chunk with metadata."""
    text: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""

    def __post_init__(self):
        if not self.chunk_id:
            self.chunk_id = hashlib.md5(self.text[:200].encode()).hexdigest()[:12]


# ── Patterns for structural splitting ──────────────────────────────────────

SECTION_PATTERNS = [
    # "Section 123." or "Section 123 –" or "§ 123."
    re.compile(r"(?:^|\n)\s*(?:Section|§|Sec\.?)\s+(\d+[A-Za-z]*)\b[.\s–—-]", re.IGNORECASE),
    # "Article 21." / "Art. 21"
    re.compile(r"(?:^|\n)\s*(?:Article|Art\.?)\s+(\d+[A-Za-z]*)\b[.\s–—-]", re.IGNORECASE),
    # "Order IV Rule 1"
    re.compile(r"(?:^|\n)\s*Order\s+([IVXLCDM]+)\s+Rule\s+(\d+)", re.IGNORECASE),
    # "Rule 1."
    re.compile(r"(?:^|\n)\s*Rule\s+(\d+[A-Za-z]*)\b[.\s–—-]", re.IGNORECASE),
    # "Chapter III" (used as fallback section boundary)
    re.compile(r"(?:^|\n)\s*Chapter\s+([IVXLCDM]+|\d+)", re.IGNORECASE),
]

PROVISO_PATTERNS = [
    re.compile(r"^\s*Provided\s+that", re.IGNORECASE),
    re.compile(r"^\s*Explanation", re.IGNORECASE),
    re.compile(r"^\s*Illustration", re.IGNORECASE),
    re.compile(r"^\s*Exception", re.IGNORECASE),
    re.compile(r"^\s*Note:", re.IGNORECASE),
]

JUDGMENT_PARA_PATTERN = re.compile(r"(?:^|\n)\s*(\d+)\.\s+")

# Approximate token count (rough: 1 token ≈ 4 chars for English)
def _approx_tokens(text: str) -> int:
    return len(text) // 4


def chunk_statute(text: str, doc_meta: dict, min_tokens: int = 200, max_tokens: int = 800) -> list[Chunk]:
    """Chunk a statute by sections/articles, keeping provisos attached."""
    chunks = []
    # Find all section boundaries
    boundaries = []
    for pat in SECTION_PATTERNS:
        for m in pat.finditer(text):
            boundaries.append((m.start(), m.group(0).strip()))

    if not boundaries:
        # No structure detected → fall back to paragraph chunking
        return chunk_by_paragraphs(text, doc_meta, min_tokens, max_tokens)

    boundaries.sort(key=lambda x: x[0])

    for i, (start, label) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        section_text = text[start:end].strip()

        if _approx_tokens(section_text) <= max_tokens:
            meta = {**doc_meta}
            # Try to extract section number
            sec_match = re.search(r"(\d+[A-Za-z]*)", label)
            if sec_match:
                meta["section_or_article"] = sec_match.group(1)
            chunks.append(Chunk(text=section_text, metadata=meta))
        else:
            # Section too large → split by sub-sections but keep provisos
            sub_chunks = _split_large_section(section_text, doc_meta, min_tokens, max_tokens)
            chunks.extend(sub_chunks)

    return chunks


def _split_large_section(text: str, doc_meta: dict, min_tokens: int, max_tokens: int) -> list[Chunk]:
    """Split a large section into smaller chunks at paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = ""

    for para in paragraphs:
        # Check if this para is a proviso/explanation → keep with current
        is_proviso = any(p.match(para.strip()) for p in PROVISO_PATTERNS)

        if is_proviso or _approx_tokens(current + "\n\n" + para) <= max_tokens:
            current = (current + "\n\n" + para).strip()
        else:
            if current and _approx_tokens(current) >= min_tokens:
                chunks.append(Chunk(text=current, metadata={**doc_meta}))
            elif current:
                # Too small → merge with next
                current = (current + "\n\n" + para).strip()
                continue
            current = para.strip()

    if current and _approx_tokens(current) >= min_tokens // 2:
        chunks.append(Chunk(text=current, metadata={**doc_meta}))
    elif current and chunks:
        # Merge tail with last chunk
        chunks[-1].text += "\n\n" + current

    return chunks


def chunk_judgment(text: str, doc_meta: dict, min_tokens: int = 200, max_tokens: int = 800) -> list[Chunk]:
    """Chunk a judgment by numbered paragraphs, keeping headnote/ratio separate."""
    chunks = []

    # Try to extract headnote (typically before first numbered paragraph)
    first_para = JUDGMENT_PARA_PATTERN.search(text)
    if first_para and first_para.start() > 200:
        headnote = text[:first_para.start()].strip()
        if headnote:
            meta = {**doc_meta, "section_or_article": "Headnote"}
            chunks.append(Chunk(text=headnote, metadata=meta))
        text = text[first_para.start():]

    return chunks + chunk_by_paragraphs(text, doc_meta, min_tokens, max_tokens)


def chunk_by_paragraphs(text: str, doc_meta: dict, min_tokens: int = 200, max_tokens: int = 800) -> list[Chunk]:
    """Fallback: chunk by double-newline paragraphs with size constraints."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        candidate = (current + "\n\n" + para).strip() if current else para

        if _approx_tokens(candidate) <= max_tokens:
            current = candidate
        else:
            if current and _approx_tokens(current) >= min_tokens // 2:
                chunks.append(Chunk(text=current, metadata={**doc_meta}))
            current = para

    if current and _approx_tokens(current) >= min_tokens // 4:
        chunks.append(Chunk(text=current, metadata={**doc_meta}))
    elif current and chunks:
        chunks[-1].text += "\n\n" + current

    return chunks


def chunk_document(text: str, doc_meta: dict, min_tokens: int = 200, max_tokens: int = 800) -> list[Chunk]:
    """Route to the right chunking strategy based on document type."""
    doc_type = doc_meta.get("document_type", "other")

    if doc_type in ("statute", "rule", "notification"):
        chunks = chunk_statute(text, doc_meta, min_tokens, max_tokens)
    elif doc_type in ("judgment", "supreme_court", "high_court"):
        chunks = chunk_judgment(text, doc_meta, min_tokens, max_tokens)
    else:
        chunks = chunk_by_paragraphs(text, doc_meta, min_tokens, max_tokens)

    # Assign sequential chunk IDs with doc_id prefix
    doc_id = doc_meta.get("doc_id", "doc")
    for i, c in enumerate(chunks):
        c.chunk_id = f"{doc_id}_chunk_{i:04d}"
        c.metadata["chunk_id"] = c.chunk_id
        c.metadata["doc_id"] = doc_id

    return chunks
