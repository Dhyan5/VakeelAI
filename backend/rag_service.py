"""
Orchestration service for VakeelAI Legal RAG.
Coordinates:
1. Document ingestion and text extraction (PDF, DOCX, TXT, OCR)
2. Language detection and translation layer
3. Hybrid dense + BM25 cross-lingual retrieval with anti-hallucination threshold
4. Generation service with Groq API and citation verification
"""

import os
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path
import dotenv

dotenv.load_dotenv()

from .retrieval import get_retrieval_engine, HybridLegalRetrievalEngine
from .generation import get_generation_service, LegalGenerationService
from .translation import translate_query_to_english
from ingestion.language_detect import detect_language, get_language_display_name
from ingestion.parser import extract_text_from_file


class LegalRAGService:
    """
    Main RAG pipeline coordinating retrieval and generation.
    """

    def __init__(
        self,
        retrieval_engine: Optional[HybridLegalRetrievalEngine] = None,
        generation_service: Optional[LegalGenerationService] = None
    ):
        self.retrieval_engine = retrieval_engine or get_retrieval_engine()
        self.generation_service = generation_service or get_generation_service()

    def analyze_case(
        self,
        user_query: str,
        output_language: Optional[str] = None,
        top_k: int = 5,
        min_similarity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute full RAG workflow for a text query.
        """
        if not user_query or not user_query.strip():
            return {
                "analysis": "Please provide a valid case description or legal question.",
                "citations": [],
                "confidence": "EMPTY",
                "grounded": True,
                "hallucinations": [],
                "warnings": ["Empty input query"]
            }

        # Step 1: Detect input language
        detected_lang, confidence = detect_language(user_query)
        target_lang = output_language if output_language and output_language.lower() != "auto" else get_language_display_name(detected_lang)

        # Step 2: Translation layer for retrieval (retrieve in English against English corpus)
        english_query = translate_query_to_english(user_query, detected_lang)

        # Step 3: Hybrid dense + BM25 retrieval
        retrieved_chunks = self.retrieval_engine.retrieve(
            query=english_query,
            top_k=top_k,
            min_similarity=min_similarity
        )

        # Step 4: Generation with citation grounding and safety guardrails
        analysis_result = self.generation_service.analyze_legal_question(
            user_query=user_query,
            retrieved_chunks=retrieved_chunks,
            output_language=target_lang
        )

        # Attach retrieval metadata
        analysis_result["detected_language"] = detected_lang
        analysis_result["detected_language_name"] = get_language_display_name(detected_lang)
        analysis_result["output_language"] = target_lang
        analysis_result["retrieved_chunks_count"] = len(retrieved_chunks)
        analysis_result["source_chunks"] = [
            {
                "chunk_id": c.get("chunk_id"),
                "act_name": c.get("act_name"),
                "section_number": c.get("section_number"),
                "section_title": c.get("section_title"),
                "text": c.get("text"),
                "similarity": c.get("similarity")
            }
            for c in retrieved_chunks
        ]

        return analysis_result

    def analyze_document(
        self,
        file_bytes: bytes,
        filename: str,
        output_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse uploaded document (.pdf, .docx, image, .txt) and analyze extracted text.
        """
        extracted_text = extract_text_from_file(file_bytes, filename=filename)
        if not extracted_text or not extracted_text.strip():
            return {
                "analysis": "We couldn't read this file clearly — please try a clearer document or paste the text directly.",
                "citations": [],
                "confidence": "UNREADABLE",
                "grounded": True,
                "hallucinations": [],
                "warnings": ["No text extracted from document"]
            }

        result = self.analyze_case(extracted_text, output_language=output_language)
        result["source_filename"] = filename
        result["extracted_text_preview"] = extracted_text[:300] + ("..." if len(extracted_text) > 300 else "")
        return result

    def stream_analysis(
        self,
        user_query: str,
        output_language: Optional[str] = None,
        top_k: int = 5
    ) -> Generator[str, None, None]:
        """
        Stream analysis tokens for real-time frontend display.
        """
        detected_lang, _ = detect_language(user_query)
        target_lang = output_language if output_language and output_language.lower() != "auto" else get_language_display_name(detected_lang)
        english_query = translate_query_to_english(user_query, detected_lang)

        retrieved_chunks = self.retrieval_engine.retrieve(query=english_query, top_k=top_k)

        yield from self.generation_service.stream_analysis(
            user_query=user_query,
            retrieved_chunks=retrieved_chunks,
            output_language=target_lang
        )


_rag_service_instance: Optional[LegalRAGService] = None


def get_rag_service() -> LegalRAGService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = LegalRAGService()
    return _rag_service_instance
