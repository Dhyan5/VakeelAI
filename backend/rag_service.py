"""
Main RAG service orchestrating embedding, retrieval, and generation.

This is the core "engine" that ties together:
1. Multilingual embedding service (for cross-lingual retrieval)
2. NumPy-based retrieval engine (for finding relevant statutes)
3. Groq generation service (for legal analysis)
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import dotenv

dotenv.load_dotenv()

from embedding import get_embedding_service
from retrieval import LegalRetrievalEngine, build_index_from_knowledge_base
from generation import LegalGenerationService


class LegalRAGService:
    """
    Complete RAG service for legal analysis.

    Flow:
    1. User submits query (text or file)
    2. Detect input language
    3. Retrieve top-K relevant statute chunks (cross-lingual)
    4. Generate legal analysis with Groq
    5. Optionally translate to user's preferred language
    """

    def __init__(
        self,
        retrieval_engine: Optional[LegalRetrievalEngine] = None,
        generation_service: Optional[LegalGenerationService] = None
    ):
        self.retrieval_engine = retrieval_engine or LegalRetrievalEngine()
        self.generation_service = generation_service or get_generation_service()

    def analyze_case(
        self,
        user_query: str,
        output_language: str = "English",
        top_k: int = 5,
        min_similarity: float = 0.4
    ) -> Dict[str, Any]:
        """
        Analyze a legal case/query.

        Args:
            user_query: The user's legal question or description
            output_language: Desired output language (Kannada/Hindi/English)
            top_k: Number of statute chunks to retrieve
            min_similarity: Minimum similarity threshold (anti-hallucination)

        Returns:
            Analysis result dict with analysis, citations, confidence, warnings
        """
        if not user_query or not user_query.strip():
            return {
                "analysis": "Please provide a legal question or case description.",
                "citations": [],
                "confidence": "N/A",
                "warnings": ["Empty query"],
                "raw_response": ""
            }

        if not self.generation_service:
            return {
                "analysis": "Error: Groq API key not configured. Please set GROQ_API_KEY in .env",
                "citations": [],
                "confidence": "ERROR",
                "warnings": ["Groq API not configured"],
                "raw_response": ""
            }

        # Step 1: Retrieve relevant statutes (cross-lingual)
        retrieved_chunks = self.retrieval_engine.retrieve(
            query=user_query,
            top_k=top_k,
            min_similarity=min_similarity
        )

        # Step 2: Generate legal analysis
        result = self.generation_service.analyze_legal_question(
            user_query=user_query,
            retrieved_chunks=retrieved_chunks,
            output_language=output_language
        )

        return result

    def analyze_case_with_file(
        self,
        file_content: str,
        output_language: str = "English"
    ) -> Dict[str, Any]:
        """
        Analyze a case based on uploaded file content.

        Args:
            file_content: Extracted text from uploaded file
            output_language: Desired output language

        Returns:
            Analysis result
        """
        return self.analyze_case(file_content, output_language)


# Global instance
_rag_service: Optional[LegalRAGService] = None


def get_rag_service() -> Optional[LegalRAGService]:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        try:
            retrieval_engine = LegalRetrievalEngine()
            generation_service = get_generation_service()
            _rag_service = LegalRAGService(retrieval_engine, generation_service)
        except Exception as e:
            print(f"Warning: Could not initialize RAG service: {e}")
            _rag_service = None
    return _rag_service


def clear_rag_service():
    """Clear the global RAG service."""
    global _rag_service
    _rag_service = None
