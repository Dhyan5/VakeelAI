"""
Translation layer for cross-lingual retrieval and generation.
Converts non-English queries to English for optimal retrieval against English statutes,
while preserving original queries for display and faithfully translating output.
"""

import os
import re
from typing import Optional
import dotenv

dotenv.load_dotenv()

# Indic to English Legal Keyword Glossary
# Enables instant, zero-latency, zero-cost keyword expansion for cross-lingual retrieval
INDIC_LEGAL_GLOSSARY = {
    # Kannada
    "ಜಾಮೀನು": "bail",
    "ನಿರೀಕ್ಷಣಾ ಜಾಮೀನು": "anticipatory bail",
    "ಬಂಧನ": "arrest detention",
    "ಪೊಲೀಸ್": "police",
    "ದೂರು": "complaint FIR",
    "ಪ್ರಥಮ ಮಾಹಿತಿ ವರದಿ": "First Information Report FIR",
    "ಕೊಲೆ": "murder homicide Section 302",
    "ಕಳ್ಳತನ": "theft Section 378",
    "ದರೋಡೆ": "dacoity robbery Section 395",
    "ಮೋಸ": "cheating fraud Section 420",
    "ವಂಚನೆ": "fraud cheating dishonestly",
    "ಬೆದರಿಕೆ": "intimidation threat Section 506",
    "ಸಾಕ್ಷ್ಯ": "evidence witness Section 3 Section 65B",
    "ನ್ಯಾಯಾಲಯ": "court magistrate",
    "ಆಸ್ತಿ": "property trespass Section 448",
    "ಅಕ್ರಮ ಪ್ರವೇಶ": "criminal trespass Section 448",
    "ವಿಧಿ": "article constitution",
    "ಸಂವಿಧಾನ": "constitution fundamental rights",
    "ಸಮಾನತೆ": "equality Article 14",
    "ಜೀವಿಸುವ ಹಕ್ಕು": "right to life Article 21",

    # Hindi
    "जमानत": "bail",
    "अग्रिम जमानत": "anticipatory bail Section 438",
    "गिरफ्तारी": "arrest Section 41",
    "पुलिस": "police officer",
    "शिकायत": "complaint FIR Section 154",
    "प्रथम सूचना रिपोर्ट": "First Information Report FIR",
    "एफआईआर": "FIR Section 154",
    "हत्या": "murder Section 302",
    "कत्ल": "murder Section 302",
    "चोरी": "theft Section 378",
    "डकैती": "dacoity Section 395",
    "धोखाधड़ी": "cheating fraud Section 420",
    "धोखा": "cheating fraud",
    "धमकी": "criminal intimidation Section 506",
    "सबूत": "evidence document Section 3",
    "साक्ष्य": "evidence Section 65B",
    "गवाह": "witness statement",
    "अदालत": "court magistrate",
    "न्यायालय": "court judicial magistrate",
    "संपत्ति": "property movable property",
    "कब्जा": "possession trespass Section 448",
    "अनुच्छेद": "article constitution",
    "संविधान": "constitution of india",
    "समानता": "equality Article 14",
    "प्राण और दैಹिक स्वतंत्रता": "protection of life personal liberty Article 21"
}


def translate_query_to_english(query: str, source_lang: str) -> str:
    """
    Translate or expand non-English query to English legal terms for retrieval.
    First checks Groq API if available, else applies legal lexicon expansion.
    """
    if not query or source_lang == "en":
        return query

    # Try Groq translation if API key is present
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            prompt = (
                f"Translate the following {source_lang} legal inquiry into a clear, concise English "
                f"legal search query focusing on relevant Indian statutory terms:\n\n{query}\n\n"
                f"Output ONLY the English translation without comments."
            )
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200
            )
            english_query = resp.choices[0].message.content.strip()
            if english_query:
                return english_query
        except Exception:
            pass

    # High-fidelity Indic glossary expansion fallback
    expanded_terms = []
    for indic_term, english_equiv in INDIC_LEGAL_GLOSSARY.items():
        if indic_term in query:
            expanded_terms.append(english_equiv)

    if expanded_terms:
        # Combine original query with English legal concepts
        return f"{query} {' '.join(expanded_terms)}"

    return query
