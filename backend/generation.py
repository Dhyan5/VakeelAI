"""
Groq-based generation service with legal analysis and optional translation.

This module handles:
1. Legal analysis generation via Groq API
2. Optional translation of results to user's preferred language
3. Guardrail checks for illegal requests

Assumptions:
- Groq's free tier currently includes llama-3.3-70b-versatile (as of 2026)
- Uses JSON mode for structured output when needed
- Two calls per analysis: one for legal analysis, one for translation (if needed)
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import dotenv

# Load environment variables
dotenv.load_dotenv()

from groq import Groq


class LegalGenerationService:
    """
    Groq-based legal analysis and translation service.

    Cost: $0 for both free-tier models (llama-3.3-70b-versatile)
    """

    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the Groq client.

        Args:
            groq_api_key: Optional API key override (loads from env by default)
        """
        api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in .env or pass explicitly.\n"
                "Get your key from: https://console.groq.com/keys"
            )

        self.client = Groq(api_key=api_key)

        # Current best free-tier model on Groq (as of 2026)
        # Check: https://console.groq.com/docs/models for updates
        self.analysis_model = "llama-3.3-70b-versatile"
        self.translation_model = "llama-3.3-70b-versatile"

        # Load system prompt
        prompts_dir = Path(__file__).parent.parent / "prompts"
        self.system_prompt_path = prompts_dir / "legal_analysis_system_prompt.md"

        if self.system_prompt_path.exists():
            with open(self.system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        else:
            # Fallback system prompt if file doesn't exist
            self.system_prompt = self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Default system prompt if file is missing."""
        return """You are an Indian legal research assistant. Provide accurate legal analysis
based ONLY on the statutes provided in the context. NEVER fabricate citations."""

    def _build_legal_analysis_prompt(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Build the prompt for legal analysis.

        Args:
            user_query: The user's legal question
            retrieved_chunks: List of retrieved statute chunks

        Returns:
            (system_prompt, user_prompt) tuple
        """
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"### Context {i}:\n"
                f"Source: {chunk.get('source', 'Unknown')}\n"
                f"Section: {chunk.get('section', 'Unknown')}\n"
                f"Text:\n{chunk.get('text', '')}\n"
            )

        context = "\n".join(context_parts) if context_parts else "NO RELEVANT STATUTES FOUND IN KNOWLEDGE BASE."

        user_prompt = f"""User Query: {user_query}

{context}

Please provide your legal analysis following the exact format specified in the system prompt."""

        return self.system_prompt, user_prompt

    def _build_translation_prompt(self, text: str, target_language: str) -> str:
        """Build prompt for translation."""
        return f"""Translate the following legal analysis to {target_language}.
Maintain the structure and all legal terminology in English where standard.
Do not add or remove any information.

{text}"""

    def _run_guardrail(self, user_query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the query seeks help with illegal activities.

        Returns:
            (allowed, rejection_message) tuple
        """
        # Simple keyword-based guardrail
        illegal_keywords = [
            "fabricate", "forge", "falsify", "perjure", "commit perjury",
            "hide evidence", "destroy evidence", "tamper with evidence",
            "bribe", "bribery", "pay off", "influence", "witness intimidation",
            "escape", "evade law enforcement", "avoid prosecution",
            "hide assets", "money laundering", "fraud", "scam",
            "threaten", "harass", "intimidate", "violence", "attack"
        ]

        query_lower = user_query.lower()

        for keyword in illegal_keywords:
            if keyword in query_lower:
                return False, (
                    "I cannot assist with requests involving illegal activities, "
                    "including but not limited to: fabricating evidence, committing "
                    "perjury, hiding assets, evading law enforcement, or other unlawful acts. "
                    "This tool is for legitimate legal research and guidance only."
                )

        return True, None

    def analyze_legal_question(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]],
        output_language: str = "English"
    ) -> Dict[str, Any]:
        """
        Generate legal analysis for a question.

        Args:
            user_query: The legal question
            retrieved_chunks: Retrieved statute chunks from retrieval engine
            output_language: Desired output language

        Returns:
            Analysis result dict with:
                - analysis: Main legal analysis
                - citations: List of cited statutes
                - confidence: HIGH/MEDIUM/LOW
                - warnings: Any generated warnings
                - raw_response: Full LLM response
        """
        # Run guardrail check
        allowed, rejection_msg = self._run_guardrail(user_query)
        if not allowed:
            return {
                "analysis": rejection_msg,
                "citations": [],
                "confidence": "N/A",
                "warnings": ["Guardrail blocked this query"],
                "raw_response": rejection_msg
            }

        # Build prompt
        system_prompt, user_prompt = self._build_legal_analysis_prompt(
            user_query, retrieved_chunks
        )

        try:
            # First call: Legal analysis
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.analysis_model,
                temperature=0.3,  # Lower temperature for accuracy
                max_tokens=4000
            )

            raw_response = chat_completion.choices[0].message.content

            # Second call: Translate if needed (still $0 on free tier)
            final_analysis = raw_response
            if output_language.lower() != "english" and output_language.lower() not in ["en", "eng"]:
                translation_prompt = self._build_translation_prompt(raw_response, output_language)

                translation_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional legal translator. "
                         "Translate legal text accurately while preserving all citations and "
                         "technical terms in English where standard.""},
                        {"role": "user", "content": translation_prompt}
                    ],
                    model=self.translation_model,
                    temperature=0.2,
                    max_tokens=4000
                )

                final_analysis = translation_completion.choices[0].message.content

            # Extract confidence level from response (last line often contains it)
            confidence = self._extract_confidence(raw_response)

            # Extract citations
            citations = self._extract_citations(raw_response, retrieved_chunks)

            return {
                "analysis": final_analysis,
                "citations": citations,
                "confidence": confidence,
                "warnings": [],
                "raw_response": raw_response
            }

        except Exception as e:
            return {
                "analysis": f"Error generating analysis: {str(e)}",
                "citations": [],
                "confidence": "ERROR",
                "warnings": [f"Generation error: {str(e)}"],
                "raw_response": str(e)
            }

    def _extract_confidence(self, text: str) -> str:
        """Extract confidence level from analysis text."""
        confidence_indicators = {
            "HIGH": ["high confidence", "clear precedent", "well-established", "unambiguous"],
            "MEDIUM": ["possible", "arguable", "uncertain", "depends", "mitigating factors"],
            "LOW": ["weak", "unlikely", "speculative", "no clear authority"]
        }

        text_lower = text.lower()

        for level, keywords in confidence_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level

        return "MEDIUM"  # Default

    def _extract_citations(self, text: str, retrieved_chunks: List[Dict]) -> List[str]:
        """Extract cited sections from the response."""
        citations = []

        # Try to extract section references from text
        import re

        # Pattern for Indian legal citations
        patterns = [
            r'Section\s+\d+[\w()]*\s*(?:IPC|CrPC|BNSS|CrPC|Evidence\s+Act)?',
            r'S\.?\s*\d+[\w()]*',
            r'Article\s+\d+',
            r'Section\s+\d+',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)

        # Deduplicate while preserving order
        seen = set()
        unique_citations = []
        for citation in citations:
            key = citation.lower()
            if key not in seen:
                seen.add(key)
                unique_citations.append(citation)

        return unique_citations[:10]  # Limit to top 10

    def streaming_analysis(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]],
        output_language: str = "English"
    ):
        """
        Generator for streaming legal analysis.

        Yields chunks of the analysis as they arrive from Groq.
        """
        system_prompt, user_prompt = self._build_legal_analysis_prompt(
            user_query, retrieved_chunks
        )

        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.analysis_model,
                temperature=0.3,
                max_tokens=4000,
                stream=True
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Return final result for post-processing
            yield {"full_response": full_response}

        except Exception as e:
            yield {"error": str(e)}


# Global instance
_generation_service: Optional[LegalGenerationService] = None


def get_generation_service() -> Optional[LegalGenerationService]:
    """Get or create the global generation service instance."""
    global _generation_service
    if _generation_service is None:
        try:
            _generation_service = LegalGenerationService()
        except ValueError:
            # API key not configured
            _generation_service = None
    return _generation_service


def clear_generation_service():
    """Clear the global generation service."""
    global _generation_service
    _generation_service = None
