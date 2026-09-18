"""
Tests for hybrid cross-lingual legal retrieval.
Validates cross-lingual accuracy (English, Hindi, Kannada) and
anti-hallucination confidence cutoffs on out-of-domain queries.
"""

import pytest
from backend.retrieval import get_retrieval_engine
from backend.translation import translate_query_to_english


@pytest.fixture(scope="module")
def engine():
    return get_retrieval_engine()


def test_cross_lingual_retrieval_english(engine):
    query = "bail in non-bailable offences"
    results = engine.retrieve(query, top_k=3)
    assert len(results) > 0
    sections = [r.get("section_number") for r in results]
    # Should retrieve Section 436 or Section 437
    assert any("436" in s or "437" in s or "438" in s for s in sections)


def test_cross_lingual_retrieval_hindi(engine):
    query = "धोखाधड़ी और बेईमानी से संपत्ति हड़पना"
    eng_query = translate_query_to_english(query, "hi")
    results = engine.retrieve(eng_query, top_k=3)
    assert len(results) > 0
    sections = [r.get("section_number") for r in results]
    # Should retrieve Section 420 or Section 378
    assert any("420" in s or "378" in s for s in sections)


def test_cross_lingual_retrieval_kannada(engine):
    query = "ಪೊಲೀಸರು ವಾರಂಟ್ ಇಲ್ಲದೆ ಬಂಧಿಸಿದರೆ ಜಾಮೀನು ಪಡೆಯುವುದು ಹೇಗೆ?"
    eng_query = translate_query_to_english(query, "kn")
    results = engine.retrieve(eng_query, top_k=3)
    assert len(results) > 0
    sections = [r.get("section_number") for r in results]
    # Should retrieve Section 41, 436, or 437
    assert any("41" in s or "436" in s or "437" in s or "438" in s for s in sections)


def test_anti_hallucination_cutoff_on_gibberish(engine):
    gibberish = "xyzzy abcqwerty 998877 quantum teleportation recipe for pancakes"
    # Strict cutoff should return zero results
    results = engine.retrieve(gibberish, top_k=3, min_similarity=0.45)
    assert len(results) == 0
