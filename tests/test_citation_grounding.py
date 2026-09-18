"""
Automated Citation Grounding Verification Test Suite (Anti-Hallucination Rule 4).
Flags any statutory or case citation appearing in LLM generation output
that is not present in the retrieved context chunks.
"""

import pytest
from backend.generation import get_generation_service


@pytest.fixture(scope="module")
def gen_service():
    return get_generation_service()


def test_grounded_analysis_passes_verification(gen_service):
    """Grounded output containing only retrieved citations must pass."""
    mock_chunks = [
        {
            "chunk_id": "IPCI-S302-C1",
            "act_name": "Indian Penal Code",
            "section_number": "Section 302",
            "section_title": "Punishment for murder",
            "text": "Whoever commits murder shall be punished with death, or imprisonment for life."
        },
        {
            "chunk_id": "COCP-S154-C1",
            "act_name": "Code of Criminal Procedure",
            "section_number": "Section 154",
            "section_title": "Information in cognizable cases (FIR)",
            "text": "Every information relating to the commission of a cognizable offence shall be reduced to writing."
        }
    ]

    valid_text = (
        "Based on the facts, Section 302 of the Indian Penal Code applies to the homicide. "
        "Furthermore, an FIR must be registered under Section 154 of the Code of Criminal Procedure."
    )

    is_grounded, hallucinations = gen_service.verify_citations_against_context(
        analysis_text=valid_text,
        retrieved_chunks=mock_chunks
    )

    assert is_grounded is True
    assert len(hallucinations) == 0


def test_hallucinated_citation_is_flagged(gen_service):
    """Any citation NOT in retrieved chunks MUST be caught and flagged as hallucination."""
    mock_chunks = [
        {
            "chunk_id": "IPCI-S420-C1",
            "act_name": "Indian Penal Code",
            "section_number": "Section 420",
            "section_title": "Cheating and dishonestly inducing delivery of property",
            "text": "Whoever cheats and thereby dishonestly induces any person to deliver property."
        }
    ]

    # LLM hallucinates Section 467 (Forgery of valuable security) which was never retrieved!
    hallucinated_text = (
        "Under Section 420, the accused is liable for cheating. "
        "Additionally, the accused is liable for forgery under Section 467 and Section 999."
    )

    is_grounded, hallucinations = gen_service.verify_citations_against_context(
        analysis_text=hallucinated_text,
        retrieved_chunks=mock_chunks
    )

    assert is_grounded is False
    # Both 467 and 999 must be caught
    assert any("467" in h for h in hallucinations)
    assert any("999" in h for h in hallucinations)


def test_empty_retrieval_returns_no_law_found(gen_service):
    """When zero chunks retrieved, output must state 'no relevant law found', never invent law."""
    res = gen_service.analyze_legal_question(
        user_query="Can a robot own real estate on Mars under maritime law?",
        retrieved_chunks=[],
        output_language="English"
    )

    assert res["grounded"] is True
    assert "no relevant law found in the knowledge base for this point" in res["analysis"].lower()
