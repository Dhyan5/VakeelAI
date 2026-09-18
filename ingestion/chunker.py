"""
Legal-aware text chunker preserving statutory boundaries, section numbers,
clause identifiers, and act titles as structured metadata.
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from .cleaner import clean_legal_text
from .language_detect import detect_language


@dataclass
class LegalChunk:
    chunk_id: str
    act_name: str
    section_number: str
    section_title: str
    text: str
    language: str
    chunk_index: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Section boundary regex patterns
# Matches "Section 302 - Punishment...", "Article 21 - Protection...", "धारा 302", "ವಿಧಿ 21"
SECTION_SPLIT_PATTERN = re.compile(
    r'(?m)^(?:(?:\*{1,2}|#{1,4}\s*)?(?:Section|Sec\.|S\.|Article|Art\.|धारा|अनुच्छेद|ವಿಧಿ|ಪ್ರಕರಣ)\s+([0-9]+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*)[ \t]*[-:–—.]?[ \t]*(.*?))(?=\n|$)',
    re.IGNORECASE
)


def _sanitize_id(text: str) -> str:
    """Generate safe identifier substring."""
    return re.sub(r'[^A-Za-z0-9_-]', '', text.replace(" ", "_"))


def chunk_legal_statute(
    text: str,
    default_act_name: str = "Indian Statute",
    max_chunk_chars: int = 1200,
    overlap_chars: int = 150
) -> List[LegalChunk]:
    """
    Split legal statute text by sections, extracting act name, section numbers,
    titles, and structured metadata. If a section exceeds max_chunk_chars,
    sub-splits with contextual prefix.
    """
    cleaned = clean_legal_text(text)
    if not cleaned:
        return []

    # Detect act name from first lines if present
    act_name = default_act_name
    lines = cleaned.split("\n", 5)
    first_non_empty = [l.strip("#* \t") for l in lines if l.strip()]
    if first_non_empty:
        candidate = first_non_empty[0]
        if any(keyword in candidate.lower() for keyword in ["code", "act", "constitution", "rules", "संहिता", "अधिनियम", "ಸಂಹಿತೆ"]):
            act_name = candidate

    # Find all section header matches
    matches = list(SECTION_SPLIT_PATTERN.finditer(cleaned))
    chunks: List[LegalChunk] = []

    act_prefix = "".join([w[0].upper() for w in re.findall(r'[A-Za-z0-9]+', act_name)[:4]]) or "ACT"

    if not matches:
        # Fallback: size-based chunking with legal sentence boundaries
        words = cleaned.split()
        curr_words: List[str] = []
        curr_len = 0
        chunk_idx = 1

        for word in words:
            curr_words.append(word)
            curr_len += len(word) + 1
            if curr_len >= max_chunk_chars:
                chunk_text = " ".join(curr_words)
                lang, _ = detect_language(chunk_text)
                chunks.append(LegalChunk(
                    chunk_id=f"{act_prefix}-GEN-{chunk_idx}",
                    act_name=act_name,
                    section_number="General",
                    section_title="General Provisions",
                    text=chunk_text,
                    language=lang,
                    chunk_index=chunk_idx
                ))
                chunk_idx += 1
                curr_words = curr_words[-20:]
                curr_len = sum(len(w) + 1 for w in curr_words)

        if curr_words:
            chunk_text = " ".join(curr_words)
            lang, _ = detect_language(chunk_text)
            chunks.append(LegalChunk(
                chunk_id=f"{act_prefix}-GEN-{chunk_idx}",
                act_name=act_name,
                section_number="General",
                section_title="General Provisions",
                text=chunk_text,
                language=lang,
                chunk_index=chunk_idx
            ))
        return chunks

    # Process each section
    for i, match in enumerate(matches):
        sec_num_raw = match.group(1).strip()
        sec_title = (match.group(2) or "").strip().strip("-:–—.")
        start_pos = match.start()
        end_pos = matches[i + 1].start() if (i + 1) < len(matches) else len(cleaned)

        section_body = cleaned[start_pos:end_pos].strip()
        sec_num = f"Section {sec_num_raw}" if "section" not in sec_num_raw.lower() and "article" not in match.group(0).lower() else match.group(0).split("-")[0].split(":")[0].strip("#* \t")

        sec_id_tag = _sanitize_id(sec_num_raw)
        lang, _ = detect_language(section_body)

        if len(section_body) <= max_chunk_chars:
            chunks.append(LegalChunk(
                chunk_id=f"{act_prefix}-S{sec_id_tag}-C1",
                act_name=act_name,
                section_number=sec_num,
                section_title=sec_title,
                text=section_body,
                language=lang,
                chunk_index=len(chunks) + 1
            ))
        else:
            # Long section: break into sub-chunks while maintaining section header prefix
            header_prefix = f"[{act_name} | {sec_num}: {sec_title}]\n"
            paragraphs = section_body.split("\n\n")
            sub_chunk_idx = 1
            current_buffer = header_prefix

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if len(current_buffer) + len(para) + 2 > max_chunk_chars and len(current_buffer) > len(header_prefix):
                    chunks.append(LegalChunk(
                        chunk_id=f"{act_prefix}-S{sec_id_tag}-C{sub_chunk_idx}",
                        act_name=act_name,
                        section_number=sec_num,
                        section_title=sec_title,
                        text=current_buffer.strip(),
                        language=lang,
                        chunk_index=len(chunks) + 1
                    ))
                    sub_chunk_idx += 1
                    current_buffer = header_prefix + para + "\n\n"
                else:
                    current_buffer += para + "\n\n"

            if current_buffer.strip() and current_buffer.strip() != header_prefix.strip():
                chunks.append(LegalChunk(
                    chunk_id=f"{act_prefix}-S{sec_id_tag}-C{sub_chunk_idx}",
                    act_name=act_name,
                    section_number=sec_num,
                    section_title=sec_title,
                    text=current_buffer.strip(),
                    language=lang,
                    chunk_index=len(chunks) + 1
                ))

    return chunks
