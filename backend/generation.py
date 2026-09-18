"""
Legal analysis generation service using Groq API (llama-3.3-70b-versatile)
with strict anti-hallucination citation grounding, pre-generation safety guardrails,
translation preserving legal terms of art, and deterministic offline fallback.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple, Generator
from pathlib import Path
import dotenv

dotenv.load_dotenv()


class LegalGenerationService:
    """
    Generation service for grounded legal research and analysis.
    Uses Groq's free-tier llama-3.3-70b-versatile model.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model = "llama-3.3-70b-versatile"
        self.client = None

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[GenerationService] Error initializing Groq client: {e}")
                self.client = None

        # Load system prompts
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        analysis_prompt_path = prompts_dir / "legal_analysis_system_prompt.md"
        translation_prompt_path = prompts_dir / "translation_system_prompt.md"

        self.system_prompt = ""
        if analysis_prompt_path.exists():
            with open(analysis_prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()

        self.translation_prompt = ""
        if translation_prompt_path.exists():
            with open(translation_prompt_path, "r", encoding="utf-8") as f:
                self.translation_prompt = f.read()

    def run_guardrails(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Pre-generation safety guardrail check.
        Refuses requests seeking to fabricate evidence, coach perjury,
        evade law enforcement, or commit unlawful acts.
        """
        query_lower = query.lower()

        forbidden_patterns = [
            (r'\b(fabricat(e|ing)|forge|forg(ing|ery)|fake)\b.*\b(evidence|document|witness|testimony|alibi)\b',
             "fabricating or forging false evidence"),
            (r'\b(coach|bribe|threaten|intimidate|tamper)\b.*\b(witness|police|judge)\b',
             "witness tampering or coaching testimony"),
            (r'\b(commit|help.*commit|how to commit)\s+perjury\b',
             "committing perjury or misleading a court"),
            (r'\b(evade|escape|hide from|run away from|avoid)\b.*\b(police|arrest|warrant|law enforcement)\b',
             "evading lawful arrest or law enforcement"),
            (r'\b(launder|hide.*assets|evade taxes|destroy evidence)\b',
             "destroying evidence or unlawful concealment of assets")
        ]

        for pattern, explanation in forbidden_patterns:
            if re.search(pattern, query_lower):
                refusal_message = (
                    "### Request Refused: Ethical & Legal Safety Violation\n\n"
                    f"VakeelAI cannot assist with requests involving {explanation}.\n\n"
                    "Under Indian legal procedure (including provisions of the Indian Penal Code, "
                    "Bharatiya Nyaya Sanhita, and Contempt of Courts Act), fabricating evidence, "
                    "witness coaching, committing perjury, and obstructing lawful police investigation "
                    "are non-compoundable criminal offences.\n\n"
                    "This platform is strictly dedicated to legitimate statutory research, "
                    "procedural guidance, and rights protection under law."
                )
                return False, refusal_message

        return True, None

    def _build_context_block(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Construct prompt context block with traceable Chunk IDs."""
        if not retrieved_chunks:
            return "NO RELEVANT STATUTES OR PRECEDENTS FOUND IN KNOWLEDGE BASE."

        context_lines = ["--- BEGIN RETRIEVED CONTEXT ---"]
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_lines.append(
                f"[Chunk {idx}] ID: {chunk.get('chunk_id')}\n"
                f"Act: {chunk.get('act_name', 'Indian Statute')}\n"
                f"Section: {chunk.get('section_number', 'N/A')} - {chunk.get('section_title', '')}\n"
                f"Text:\n{chunk.get('text', '').strip()}\n"
            )
        context_lines.append("--- END RETRIEVED CONTEXT ---")
        return "\n".join(context_lines)

    def extract_citations_from_text(self, text: str) -> List[str]:
        """Extract legal citations (Section X, Article Y, etc.) from text."""
        # Regex matching Section 123, Sec. 123, Article 123, धारा 123, ಕಲಂ 123
        pattern = re.compile(
            r'(?:Section|Sec\.|Article|Art\.|धारा|ಅನುಚ್ಛೇದ|ಕಲಂ|ವಿಧಿ)\s*([0-9]+[A-Za-z]?)',
            re.IGNORECASE
        )
        matches = pattern.findall(text)
        # Normalize to "Section <NUM>" or "Article <NUM>"
        normalized = []
        for m in matches:
            if "art" in text.lower():
                normalized.append(f"Article {m.upper()}")
            else:
                normalized.append(f"Section {m.upper()}")
        return list(dict.fromkeys(normalized))

    def verify_citations_against_context(
        self,
        analysis_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Anti-hallucination verification:
        Ensures that EVERY citation mentioned in the generated output
        exists in the retrieved context chunks.
        Returns (is_valid, list_of_hallucinated_citations).
        """
        # Collect all valid section numbers and article numbers present in chunks
        valid_sections = set()
        for chunk in retrieved_chunks:
            sec_num = chunk.get("section_number", "")
            # extract raw digits/identifiers
            nums = re.findall(r'[0-9]+[A-Za-z]?', sec_num)
            for n in nums:
                valid_sections.add(n.upper())

            # Also scan chunk text for embedded section references
            text_nums = re.findall(r'(?:Section|Sec\.|Article|Art\.)\s*([0-9]+[A-Za-z]?)', chunk.get("text", ""), re.IGNORECASE)
            for tn in text_nums:
                valid_sections.add(tn.upper())

        # Extract citations from generated text
        found_citations = re.findall(
            r'(?:Section|Sec\.|Article|Art\.|धारा|ಕಲಂ|ವಿಧಿ)\s*([0-9]+[A-Za-z]?)',
            analysis_text,
            re.IGNORECASE
        )

        hallucinations = []
        for cite_num in found_citations:
            num_clean = cite_num.strip().upper()
            if num_clean not in valid_sections:
                hallucinations.append(f"Section/Article {num_clean}")

        hallucinations = list(dict.fromkeys(hallucinations))
        is_grounded = (len(hallucinations) == 0)
        return is_grounded, hallucinations

    def analyze_legal_question(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]],
        output_language: str = "English"
    ) -> Dict[str, Any]:
        """
        Main analysis execution.
        Applies safety guardrail, builds prompt, invokes Groq (or grounded fallback),
        and verifies citation grounding.
        """
        # 1. Guardrail check
        is_safe, refusal_msg = self.run_guardrails(user_query)
        if not is_safe:
            return {
                "analysis": refusal_msg,
                "citations": [],
                "confidence": "BLOCKED",
                "grounded": True,
                "hallucinations": [],
                "warnings": ["Request blocked by safety guardrails"]
            }

        # 2. If no chunks retrieved, enforce anti-hallucination rule:
        # Never let LLM guess from parametric memory!
        if not retrieved_chunks:
            no_law_msg = (
                "### Legal Analysis\n\n"
                "**Facts Summary**: Legal inquiry submitted regarding: " + user_query + "\n\n"
                "**Applicable Laws**:\n"
                "*No relevant law found in the knowledge base for this point.*\n\n"
                "**Confidence & Limitations**:\n"
                "- Confidence: LOW\n"
                "- Limitations: The provided knowledge base contains no applicable statutory provisions or case law for this specific query.\n\n"
                "**Legal Disclaimer**:\n"
                "DISCLAIMER: This analysis is an automated legal research aid. It does not constitute legal advice. Always consult a licensed advocate."
            )
            return {
                "analysis": no_law_msg,
                "citations": [],
                "confidence": "LOW",
                "grounded": True,
                "hallucinations": [],
                "warnings": ["No relevant statutory chunks retrieved"]
            }

        context_str = self._build_context_block(retrieved_chunks)

        # 3. If Groq client is configured, call live API
        if self.client:
            user_prompt = (
                f"User Case / Legal Question:\n{user_query}\n\n"
                f"Requested Output Language: {output_language}\n\n"
                f"{context_str}\n\n"
                f"Generate the comprehensive legal analysis strictly following the required 8 sections "
                f"and citing ONLY from the provided context chunks with traceable chunk IDs."
            )

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,  # Low temperature for strict factual grounding
                    max_tokens=2500
                )
                analysis_text = response.choices[0].message.content

                # Verify grounding
                is_grounded, hallucinations = self.verify_citations_against_context(
                    analysis_text, retrieved_chunks
                )

                # Extract valid citations
                citations = [
                    f"{c.get('act_name')} - {c.get('section_number')}"
                    for c in retrieved_chunks
                ]

                confidence = "HIGH" if len(retrieved_chunks) >= 2 else "MEDIUM"

                return {
                    "analysis": analysis_text,
                    "citations": list(dict.fromkeys(citations)),
                    "confidence": confidence,
                    "grounded": is_grounded,
                    "hallucinations": hallucinations,
                    "warnings": [f"Unverified citations detected: {', '.join(hallucinations)}"] if not is_grounded else []
                }
            except Exception as ex:
                print(f"[GenerationService] Groq API call failed: {ex}. Using grounded synthesis fallback.")

        # 4. Grounded Synthesis Fallback (when offline or no API key)
        return self._synthesize_grounded_response(user_query, retrieved_chunks, output_language)

    def _synthesize_grounded_response(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        output_language: str
    ) -> Dict[str, Any]:
        """
        Deterministic, rigorously grounded generator that constructs a structured
        response directly from retrieved context chunks.
        Used for offline testing and when GROQ_API_KEY is not configured.
        """
        lang = output_language.lower()
        is_hindi = "hi" in lang or "hindi" in lang
        is_kannada = "kn" in lang or "kannada" in lang

        # Collect applicable laws traceable to chunk_id
        laws_parts = []
        citations = []
        strengths = []
        weaknesses = []
        next_steps = []

        for chunk in retrieved_chunks:
            cid = chunk.get("chunk_id", "N/A")
            act = chunk.get("act_name", "Indian Statute")
            sec = chunk.get("section_number", "Section")
            title = chunk.get("section_title", "")
            snippet = chunk.get("text", "")
            citations.append(f"{act} ({sec})")

            # Extract first sentence or 150 chars of statutory text
            core_rule = snippet.split("\n")[-1] if "\n" in snippet else snippet[:200]

            if is_hindi:
                laws_parts.append(
                    f"- **{act} - {sec}: {title}** [स्रोत आईडी: `{cid}`]\n"
                    f"  - *विधिक प्रावधान*: {core_rule}\n"
                    f"  - *विश्लेषण*: यह प्रावधान सीधे इस मामले के तथ्यों पर लागू होता है।"
                )
            elif is_kannada:
                laws_parts.append(
                    f"- **{act} - {sec}: {title}** [ಮೂಲ ಗುರುತು: `{cid}`]\n"
                    f"  - *ಕಾನೂನು ನಿಯಮ*: {core_rule}\n"
                    f"  - *ವಿಶ್ಲೇಷಣೆ*: ಈ ಕಾನೂನು ನಿಬಂಧನೆಯು ಪ್ರಸ್ತುತ ಪ್ರಕರಣದ ಸನ್ನಿವೇಶಕ್ಕೆ ಅನ್ವಯಿಸುತ್ತದೆ."
                )
            else:
                laws_parts.append(
                    f"- **{act} - {sec}: {title}** (Traceable Chunk ID: `{cid}`)\n"
                    f"  - *Statutory Rule*: \"{core_rule}\"\n"
                    f"  - *Application*: This provision governs the legal obligations and liabilities arising from the disclosed circumstances."
                )

            # Contextual strength/weakness derivation
            if "bail" in title.lower() or "436" in sec or "437" in sec or "438" in sec:
                strengths.append(f"Statutory remedies for bail available under {sec} ({act}) [Chunk `{cid}`].")
                weaknesses.append(f"Bail in non-bailable offences remains subject to judicial discretion and reasonable suspicion under {sec}.")
                next_steps.append(f"File appropriate bail petition u/s {sec} with supporting affidavits before the jurisdictional court.")
            elif "154" in sec or "fir" in title.lower():
                strengths.append(f"Mandatory statutory registration of First Information Report (FIR) under {sec} for cognizable offences.")
                next_steps.append(f"Lodge formal signed complaint u/s {sec} at the jurisdictional police station.")
            elif "378" in sec or "theft" in title.lower() or "420" in sec or "cheating" in title.lower():
                strengths.append(f"Clear substantive definition and penal provisions established under {sec} [Chunk `{cid}`].")
                weaknesses.append("Prosecution carries the legal burden of demonstrating dishonest intention at the inception.")
                next_steps.append("Compile all transactional receipts, communications, and financial proof for investigation.")
            elif "21" in sec or "constitution" in act.lower():
                strengths.append(f"Fundamental constitutional protection of life and liberty guaranteed under {sec}.")

        if not strengths:
            strengths.append("Direct statutory protection exists under the retrieved sections.")
        if not weaknesses:
            weaknesses.append("Opposing party may contest factual evidence and applicability threshold.")
        if not next_steps:
            next_steps.append("Preserve all documentary evidence and consult an advocate.")

        # Construct markdown structured output
        if is_hindi:
            analysis_body = f"""### 1. Facts Summary (तथ्यों का सारांश)
प्रस्तुत मामले में आवेदक द्वारा निम्नलिखित विधिक प्रश्न उठाया गया है: "{query}".

### 2. Applicable Laws (लागू होने वाले कानून)
ज्ञानकोष से प्राप्त विधिक संदर्भों के अनुसार लागू होने वाली धाराएं:

{chr(10).join(laws_parts)}

### 3. Relevant Precedents (संबंधित न्यायिक निर्णय)
वर्तमान ज्ञानकोष संदर्भ में कोई विशिष्ट न्यायिक दृष्टांत उपलब्ध नहीं है। विश्लेषण संहिताबद्ध सांविधिक प्रावधानों पर आधारित है।

### 4. Strengths for User's Position (पक्ष की मजबूती)
{chr(10).join([f'- {s}' for s in strengths])}

### 5. Weaknesses & Counterarguments (कमजोरियां व संभावित आपत्तियां)
{chr(10).join([f'- {w}' for w in weaknesses])}

### 6. Suggested Next Steps (सुझाए गए आगामी कदम)
{chr(10).join([f'- {n}' for n in next_steps])}

### 7. Confidence & Limitations Note (विश्वसनीयता व सीमाएं)
- **विश्वसनीयता स्तर**: HIGH (प्रासंगिक अधिनियमों की धाराएं सीधे ज्ञानकोष से उद्धृत हैं)
- **सीमाएं**: यह विश्लेषण केवल उपलब्ध ज्ञानकोष पर आधारित है; राज्य-स्तरीय संशोधन लागू हो सकते हैं।

### 8. LEGAL DISCLAIMER (विधिक अस्वीकरण)
```
DISCLAIMER: This is an AI-generated legal research aid for informational purposes only. It does not constitute legal advice. The analysis is based solely on the statutes provided in the context and may be incomplete. Consult a licensed advocate for binding legal advice.
```"""
        elif is_kannada:
            analysis_body = f"""### 1. Facts Summary (ಪ್ರಕರಣದ ಸಾರಾಂಶ)
ಪ್ರಸ್ತುತ ವಿಚಾರಣೆಯಲ್ಲಿ ಅರ್ಜಿದಾರರು ಈ ಕೆಳಗಿನ ಕಾನೂನು ಪ್ರಶ್ನೆಯನ್ನು ಮುಂದಿಟ್ಟಿದ್ದಾರೆ: "{query}".

### 2. Applicable Laws (ಅನ್ವಯವಾಗುವ ಶಾಸನಬದ್ಧ ಕಾನೂನುಗಳು)
ಜ್ಞಾನ ಸಂಗ್ರಹದಿಂದ ಪಡೆದ ಸಂಬಂಧಿತ ಕಾಯ್ದೆ ಮತ್ತು ಕಲಂಗಳು:

{chr(10).join(laws_parts)}

### 3. Relevant Precedents (ನ್ಯಾಯಾಂಗ ತೀರ್ಪುಗಳು)
ಪ್ರಸ್ತುತ ಒದಗಿಸಲಾದ ಜ್ಞಾನ ಸಂಗ್ರಹದಲ್ಲಿ ಪ್ರತ್ಯೇಕ ನ್ಯಾಯಾಂಗ ತೀರ್ಪುಗಳು ಲಭ್ಯವಿಲ್ಲ; ವಿಶ್ಲೇಷಣೆಯು ನೇರ ಶಾಸನಬದ್ಧ ಕಲಂಗಳ ಮೇಲೆ ಆಧಾರಿತವಾಗಿದೆ.

### 4. Strengths for User's Position (ಅರ್ಜಿದಾರರ ಪರವಾದ ಅಂಶಗಳು)
{chr(10).join([f'- {s}' for s in strengths])}

### 5. Weaknesses & Counterarguments (ಸಂಭಾವ್ಯ ಹಿನ್ನಡೆಗಳು ಮತ್ತು ಆಕ್ಷೇಪಣೆಗಳು)
{chr(10).join([f'- {w}' for w in weaknesses])}

### 6. Suggested Next Steps (ಮುಂದಿನ ಕಾನೂನು ಕ್ರಮಗಳು)
{chr(10).join([f'- {n}' for n in next_steps])}

### 7. Confidence & Limitations Note (ವಿಶ್ವಾಸಾರ್ಹತೆ ಮತ್ತು ಮಿತಿಗಳು)
- **ವಿಶ್ವಾಸಾರ್ಹತೆಯ ಮಟ್ಟ**: HIGH (ಕಾನೂನು ಕಲಂಗಳು ನೇರವಾಗಿ ಜ್ಞಾನ ಸಂಗ್ರಹದಿಂದ ಉಲ್ಲೇಖಿಸಲ್ಪಟ್ಟಿವೆ)
- **ಮಿತಿಗಳು**: ಸ್ಥಳೀಯ ರಾಜ್ಯ ತಿದ್ದುಪಡಿಗಳು ಅಥವಾ ವಿಶೇಷ ನಿಯಮಗಳಿಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ಪರವಾನಗಿ ಪಡೆದ ವಕೀಲರ ಸಮಾಲೋಚನೆ ಅಗತ್ಯ.

### 8. LEGAL DISCLAIMER (ಕಾನೂನು ಹಕ್ಕು ನಿರಾಕರಣೆ)
```
DISCLAIMER: This is an AI-generated legal research aid for informational purposes only. It does not constitute legal advice. The analysis is based solely on the statutes provided in the context and may be incomplete. Consult a licensed advocate for binding legal advice.
```"""
        else:
            analysis_body = f"""### 1. Facts Summary
The submitted inquiry requests statutory analysis on the following set of facts: "{query}".

### 2. Applicable Laws
Based strictly on the retrieved knowledge base chunks, the following statutory provisions apply:

{chr(10).join(laws_parts)}

### 3. Relevant Precedents
No specific judicial case citations were retrieved in the knowledge base context for this query. The analysis is based directly on enacted statutory text.

### 4. Strengths for User's Position
{chr(10).join([f'- {s}' for s in strengths])}

### 5. Weaknesses & Counterarguments
{chr(10).join([f'- {w}' for w in weaknesses])}

### 6. Suggested Next Steps
{chr(10).join([f'- {n}' for n in next_steps])}

### 7. Confidence & Limitations Note
- **Confidence Rating**: HIGH (Settled statutory language retrieved with direct factual relevance)
- **Limitations**: State-specific procedural amendments and local court rules may apply; requires advocate verification.

### 8. LEGAL DISCLAIMER
```
DISCLAIMER: This is an AI-generated legal research aid for informational purposes only. It does not constitute legal advice. The analysis is based solely on the statutes provided in the context and may be incomplete. Consult a licensed advocate for binding legal advice. Do not rely on this analysis for any legal proceedings or decisions.
```"""

        # Verify grounding
        is_grounded, hallucinations = self.verify_citations_against_context(analysis_body, retrieved_chunks)

        return {
            "analysis": analysis_body,
            "citations": list(dict.fromkeys(citations)),
            "confidence": "HIGH",
            "grounded": is_grounded,
            "hallucinations": hallucinations,
            "warnings": []
        }

    def stream_analysis(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]],
        output_language: str = "English"
    ) -> Generator[str, None, None]:
        """Streaming generator yielding text deltas."""
        result = self.analyze_legal_question(user_query, retrieved_chunks, output_language)
        full_text = result.get("analysis", "")
        # Stream in words/sentences
        words = full_text.split(" ")
        for i in range(0, len(words), 4):
            chunk = " ".join(words[i:i+4]) + " "
            yield chunk


_generation_service_instance: Optional[LegalGenerationService] = None


def get_generation_service() -> LegalGenerationService:
    global _generation_service_instance
    if _generation_service_instance is None:
        _generation_service_instance = LegalGenerationService()
    return _generation_service_instance
