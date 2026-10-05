"""
Nyaya – Answer generator: builds the prompt, calls the LLM, streams the response.
"""

import logging
from pathlib import Path
from typing import AsyncIterator, Optional

from app.llm.base import LLMClient, LLMMessage
from app.rag.query_rewrite import map_old_to_new, rewrite_followup, expand_synonyms
from app.rag.retriever import hybrid_search
from app.rag.reranker import rerank
from app.rag.guardrails import (
    classify_query, verify_citations, check_confidence,
    REFUSAL_HARMFUL, REFUSAL_NON_LEGAL, REFUSAL_EMPTY_KB, REFUSAL_LOW_CONFIDENCE,
)
from app.rag.ingest import get_total_chunks

logger = logging.getLogger(__name__)

# Load system prompt
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "system_prompt.txt"
_system_prompt: Optional[str] = None


def get_system_prompt() -> str:
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return "You are Nyaya, an expert AI legal assistant for Indian law."


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    if not chunks:
        return "No relevant documents found in the knowledge base."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        header_parts = []
        if meta.get("act_name"):
            header_parts.append(meta["act_name"])
        if meta.get("section_or_article"):
            header_parts.append(f"Section/Article {meta['section_or_article']}")
        if meta.get("year"):
            header_parts.append(f"({meta['year']})")
        if meta.get("document_type"):
            header_parts.append(f"[{meta['document_type']}]")

        header = " | ".join(header_parts) if header_parts else f"Source {i}"
        chunk_id = chunk.get("chunk_id", f"chunk_{i}")

        parts.append(f"--- SOURCE {i} [chunk_id: {chunk_id}] ---\n{header}\n\n{chunk.get('text', '')}")

    return "\n\n".join(parts)


async def generate_answer(
    query: str,
    llm: LLMClient,
    history: list[dict] = None,
    language: str = "en",
) -> dict:
    """
    Full RAG pipeline: classify → rewrite → retrieve → rerank → generate.
    Returns {answer, citations, mappings, classification, confidence, warnings}.
    """
    history = history or []

    # 1. Pre-classify
    classification = classify_query(query)
    if classification == "HARMFUL":
        return {
            "answer": REFUSAL_HARMFUL,
            "citations": [],
            "mappings": [],
            "classification": classification,
            "confidence": 0,
            "warnings": [],
        }
    if classification == "NON_LEGAL":
        return {
            "answer": REFUSAL_NON_LEGAL,
            "citations": [],
            "mappings": [],
            "classification": classification,
            "confidence": 0,
            "warnings": [],
        }

    # 2. Check if KB is empty
    if get_total_chunks() == 0:
        return {
            "answer": REFUSAL_EMPTY_KB,
            "citations": [],
            "mappings": [],
            "classification": classification,
            "confidence": 0,
            "warnings": [],
        }

    # 3. Rewrite follow-up
    standalone_query = rewrite_followup(query, history)

    # 4. Map old law references
    mapped_query, mappings = map_old_to_new(standalone_query)

    # 5. Retrieve (hybrid)
    results = hybrid_search(mapped_query, top_k=20)

    # 6. Re-rank
    top_results = rerank(query, results, top_k=8)

    # 7. Check confidence
    if not check_confidence(top_results):
        return {
            "answer": REFUSAL_LOW_CONFIDENCE,
            "citations": [],
            "mappings": mappings,
            "classification": classification,
            "confidence": 0,
            "warnings": [],
        }

    # 8. Build prompt
    context = build_context(top_results)
    system = get_system_prompt()

    if language == "hi":
        system += "\n\nIMPORTANT: Respond in Hindi (Devanagari script)."

    # Add mapping info to context
    mapping_note = ""
    if mappings:
        mapping_note = "\n\nNOTE ON LAW MAPPINGS:\n"
        for m in mappings:
            mapping_note += f"- {m['old_law']} Section {m['old_section']} → {m['new_law']} Section {m['new_section']} ({m['title']})\n"
        mapping_note += "Include both old and new references in your answer."

    instructions = (
        "Provide a COMPLETE, DETAILED, AND IN-DEPTH legal analysis for this query. "
        "Thoroughly address each required section: "
        "1. Executive Legal Summary (clear assessment of legal position and rights); "
        "2. Applicable Statutory Provisions & Sections You Can Use (exhaustively enumerate all applicable sections under BNS, BNSS, BSA, CPC, Contract Act, etc., with both new and old codes where applicable, and exact penalties/remedies); "
        "3. Essential Legal Ingredients & Conditions (what must be established to satisfy each section); "
        "4. Step-by-Step Procedure, Forum & Timelines (exact jurisdictional court/tribunal, sequence of actions, notices, and statutory limitation deadlines); "
        "5. Landmark Judicial Precedents & Case Law (relevant Supreme Court or High Court judgments and their ratio); "
        "6. Evidentiary Requirements & Defense Considerations (required documentary/electronic evidence like S.63 BSA certificates and common defenses); "
        "7. Statutory Legal Disclaimer."
    )

    messages = [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user", content=(
            f"RETRIEVED CONTEXT:\n{context}{mapping_note}\n\n"
            f"INSTRUCTION: {instructions}\n\n"
            f"USER QUESTION:\n{query}"
        )),
    ]

    # 9. Generate
    response = await llm.generate(messages)

    # 10. Post-verify citations
    answer, warnings = verify_citations(response.content, top_results)

    # Build citation objects
    citations = []
    for chunk in top_results:
        meta = chunk.get("metadata", {})
        citations.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "act_name": meta.get("act_name", ""),
            "section": meta.get("section_or_article", ""),
            "document_type": meta.get("document_type", ""),
            "year": meta.get("year"),
            "score": chunk.get("rrf_score", chunk.get("score", 0)),
        })

    return {
        "answer": answer,
        "citations": citations,
        "mappings": mappings,
        "classification": classification,
        "confidence": max(r.get("rrf_score", r.get("score", 0)) for r in top_results) if top_results else 0,
        "warnings": warnings,
    }


async def stream_answer(
    query: str,
    llm: LLMClient,
    history: list[dict] = None,
    language: str = "en",
) -> AsyncIterator[dict]:
    """
    Streaming version: yields SSE events.
    First yields metadata (citations, mappings), then streams tokens.
    """
    import json
    history = history or []

    # Pre-classify
    classification = classify_query(query)
    if classification == "HARMFUL":
        yield {"type": "meta", "data": {"classification": "HARMFUL", "citations": [], "mappings": []}}
        yield {"type": "token", "data": REFUSAL_HARMFUL}
        yield {"type": "done", "data": {}}
        return

    if classification == "NON_LEGAL":
        yield {"type": "meta", "data": {"classification": "NON_LEGAL", "citations": [], "mappings": []}}
        yield {"type": "token", "data": REFUSAL_NON_LEGAL}
        yield {"type": "done", "data": {}}
        return

    if get_total_chunks() == 0:
        yield {"type": "meta", "data": {"classification": "LEGAL", "citations": [], "mappings": []}}
        yield {"type": "token", "data": REFUSAL_EMPTY_KB}
        yield {"type": "done", "data": {}}
        return

    # Rewrite + map + retrieve + rerank
    standalone_query = rewrite_followup(query, history)
    mapped_query, mappings = map_old_to_new(standalone_query)
    results = hybrid_search(mapped_query, top_k=20)
    top_results = rerank(query, results, top_k=8)

    if not check_confidence(top_results):
        yield {"type": "meta", "data": {"classification": "LEGAL", "citations": [], "mappings": mappings}}
        yield {"type": "token", "data": REFUSAL_LOW_CONFIDENCE}
        yield {"type": "done", "data": {}}
        return

    # Build citations
    citations = []
    for chunk in top_results:
        meta = chunk.get("metadata", {})
        citations.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "act_name": meta.get("act_name", ""),
            "section": meta.get("section_or_article", ""),
            "document_type": meta.get("document_type", ""),
            "year": meta.get("year"),
        })

    # Yield metadata first
    yield {
        "type": "meta",
        "data": {
            "classification": classification,
            "citations": citations,
            "mappings": mappings,
        },
    }

    # Build prompt
    context = build_context(top_results)
    system = get_system_prompt()
    if language == "hi":
        system += "\n\nIMPORTANT: Respond in Hindi (Devanagari script)."

    mapping_note = ""
    if mappings:
        mapping_note = "\n\nNOTE ON LAW MAPPINGS:\n"
        for m in mappings:
            mapping_note += f"- {m['old_law']} Section {m['old_section']} → {m['new_law']} Section {m['new_section']} ({m['title']})\n"

    instructions = (
        "Provide a COMPLETE, DETAILED, AND IN-DEPTH legal analysis for this query. "
        "Thoroughly address each required section: "
        "1. Executive Legal Summary (clear assessment of legal position and rights); "
        "2. Applicable Statutory Provisions & Sections You Can Use (exhaustively enumerate all applicable sections under BNS, BNSS, BSA, CPC, Contract Act, etc., with both new and old codes where applicable, and exact penalties/remedies); "
        "3. Essential Legal Ingredients & Conditions (what must be established to satisfy each section); "
        "4. Step-by-Step Procedure, Forum & Timelines (exact jurisdictional court/tribunal, sequence of actions, notices, and statutory limitation deadlines); "
        "5. Landmark Judicial Precedents & Case Law (relevant Supreme Court or High Court judgments and their ratio); "
        "6. Evidentiary Requirements & Defense Considerations (required documentary/electronic evidence like S.63 BSA certificates and common defenses); "
        "7. Statutory Legal Disclaimer."
    )

    messages = [
        LLMMessage(role="system", content=system),
        LLMMessage(role="user", content=(
            f"RETRIEVED CONTEXT:\n{context}{mapping_note}\n\n"
            f"INSTRUCTION: {instructions}\n\n"
            f"USER QUESTION:\n{query}"
        )),
    ]

    # Stream tokens
    full_answer = ""
    async for token in llm.stream(messages):
        full_answer += token
        yield {"type": "token", "data": token}

    yield {"type": "done", "data": {"full_answer": full_answer}}
