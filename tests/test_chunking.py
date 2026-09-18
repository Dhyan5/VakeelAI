"""
Tests for legal-aware statutory chunking.
Verifies section boundary identification, chunk ID assignment,
metadata extraction, and handling of Indic section titles.
"""

import pytest
from ingestion.chunker import chunk_legal_statute, LegalChunk
from ingestion.cleaner import clean_legal_text
from ingestion.language_detect import detect_language


def test_section_splitting_and_metadata():
    sample_statute = """
Indian Penal Code (IPC)

Section 302 - Punishment for murder
Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.

Section 378 - Definition of theft
Whoever, with intent to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property, commits theft.
"""
    chunks = chunk_legal_statute(sample_statute, default_act_name="Indian Penal Code (IPC)")
    assert len(chunks) == 2

    # Verify chunk 1
    c1 = chunks[0]
    assert "302" in c1.chunk_id
    assert c1.section_number == "Section 302"
    assert "murder" in c1.section_title.lower()
    assert "Whoever commits murder" in c1.text
    assert c1.language == "en"

    # Verify chunk 2
    c2 = chunks[1]
    assert "378" in c2.chunk_id
    assert c2.section_number == "Section 378"
    assert "theft" in c2.section_title.lower()
    assert "movable property" in c2.text


def test_chunking_indic_statutes():
    hindi_statute = """
भारतीय दंड संहिता

धारा 420 - धोखाधड़ी और संपत्ति की डिलीवरी के लिए बेईमानी से प्रेरित करना
जो कोई भी धोखाधड़ी करता है और जिससे किसी व्यक्ति को कोई संपत्ति देने के लिए प्रेरित किया जाता है, उसे सात साल तक की कैद होगी।
"""
    chunks = chunk_legal_statute(hindi_statute, default_act_name="भारतीय दंड संहिता")
    assert len(chunks) >= 1
    c = chunks[0]
    assert "420" in c.section_number or "420" in c.chunk_id
    assert c.language == "hi"


def test_cleaner_normalizes_artifacts():
    dirty = "Section 302   \r\n\r\n\r\n\r\nWhoever commits   murder.\nPage 1 of 4\n- 1 -"
    cleaned = clean_legal_text(dirty)
    assert "Page 1 of 4" not in cleaned
    assert "- 1 -" not in cleaned
    assert "Section 302" in cleaned
    assert "Whoever commits murder." in cleaned


def test_language_detection_indic():
    kannada_sample = "ಪೊಲೀಸರು ನನ್ನನ್ನು ವಾರಂಟ್ ಇಲ್ಲದೆ ಬಂಧಿಸಿದ್ದಾರೆ ಮತ್ತು ಜಾಮೀನು ನಿರಾಕರಿಸಿದ್ದಾರೆ"
    lang, conf = detect_language(kannada_sample)
    assert lang == "kn"
    assert conf > 0.8

    hindi_sample = "किसी ने मेरे साथ धोखाधड़ी करके पचास लाख रुपये ले लिए"
    lang_hi, conf_hi = detect_language(hindi_sample)
    assert lang_hi == "hi"
    assert conf_hi > 0.8
