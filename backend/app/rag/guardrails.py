"""
Nyaya – Guardrails: pre-classification, post-generation verification,
confidence thresholds, and prompt-injection defense.
"""

import re
import logging

logger = logging.getLogger(__name__)


# ── Pre-classification (rule-based, no LLM call needed) ───────────────────

HARMFUL_PATTERNS = [
    r"how\s+(?:to|can\s+i)\s+(?:forge|fake|fabricate)",
    r"how\s+(?:to|can\s+i)\s+(?:destroy|tamper|hide)\s+evidence",
    r"how\s+(?:to|can\s+i)\s+(?:evade|escape|avoid)\s+(?:police|arrest|law)",
    r"how\s+(?:to|can\s+i)\s+(?:commit|plan|execute)\s+(?:murder|robbery|fraud|kidnap)",
    r"how\s+(?:to|can\s+i)\s+(?:bribe|blackmail|extort)",
    r"how\s+(?:to|can\s+i)\s+(?:hack|steal\s+data|phish)",
    r"reveal\s+(?:your|the)\s+(?:system\s+prompt|api\s+key|instructions)",
    r"ignore\s+(?:your|all|previous)\s+(?:instructions|rules|guidelines)",
]

NON_LEGAL_PATTERNS = [
    r"(?:write|create|code|build|make|implement)\s+.*(?:python|java|javascript|code|program|script|app|website|function|algorithm|binary\s+search)",
    r"\b(?:python|java|javascript|typescript|c\+\+|golang|binary\s+search|sorting\s+algorithm|bug\s+fix)\b",
    r"(?:who\s+will\s+win|score|match|cricket|football|ipl|world\s+cup)",
    r"\b(?:cricket|football|world\s+cup|ipl|fifa|olympics)\b",
    r"(?:recipe|cook|bake|ingredients|make)\s+.*(?:curry|chicken|cake|dish|food|bread|biryani)",
    r"\b(?:recipe|cooking|curry|butter\s+chicken|biryani|ingredients)\b",
    r"\b(?:bitcoin|ethereum|crypto|cryptocurrency|invest\s+in\s+crypto|trading\s+strategy)\b",
    r"(?:tell\s+me\s+a\s+joke|funny|humor)",
    r"(?:weather|temperature|forecast)\s+(?:in|at|for)",
    r"\b(?:weather\s+forecast|forecast\s+for|rain\s+tomorrow)\b",
    r"(?:write\s+(?:a|an)\s+(?:poem|essay|story|song|email))",
    r"(?:who\s+is\s+the\s+(?:president|pm|ceo)\s+of)",
    r"(?:what\s+is\s+the\s+(?:capital|population)\s+of)",
    r"(?:translate|convert)\s+.+\s+(?:to|into)\s+(?:hindi|english|french|spanish)",
    r"(?:math|calculate|solve)\s+\d+",
]

LEGAL_KEYWORDS = [
    "law", "legal", "act", "section", "article", "court", "judge", "advocate",
    "lawyer", "case", "bail", "fir", "arrest", "complaint", "petition",
    "suit", "appeal", "tribunal", "arbitration", "contract", "property",
    "divorce", "custody", "maintenance", "inheritance", "will", "succession",
    "company", "director", "shareholder", "consumer", "defamation", "cheque",
    "murder", "theft", "robbery", "fraud", "forgery", "assault", "rape",
    "dowry", "harassment", "domestic violence", "cyber", "it act",
    "constitution", "fundamental rights", "directive principles",
    "ipc", "bns", "crpc", "bnss", "cpc", "evidence", "bsa",
    "limitation", "specific relief", "transfer of property",
    "negotiable instruments", "arbitration", "pmla", "pocso",
    "motor vehicles", "labour", "employment", "wages", "gratuity",
    "pf", "esi", "gst", "income tax", "rera", "copyright", "patent",
    "trademark", "rights", "offence", "punishment", "penalty",
    "cognizable", "non-cognizable", "bailable", "non-bailable",
    "summons", "warrant", "chargesheet", "judgment", "decree", "order",
    "writ", "habeas corpus", "mandamus", "certiorari", "prohibition",
    "quo warranto", "pil", "public interest litigation",
    "sanhita", "adhiniyam", "vidhi", "kanoon", "nyaya", "adalat",
    "notice", "eviction", "tenancy", "rent", "agreement", "deed",
    "stamp duty", "registration",
]


def classify_query(query: str) -> str:
    """
    Classify a query as LEGAL, NON_LEGAL, or HARMFUL.
    Uses rule-based patterns (fast, no LLM cost).
    """
    query_lower = query.lower().strip()

    # Check harmful patterns first
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, query_lower):
            return "HARMFUL"

    # Check non-legal patterns
    non_legal_score = 0
    for pattern in NON_LEGAL_PATTERNS:
        if re.search(pattern, query_lower):
            non_legal_score += 1

    # Check legal keywords with word boundary matching
    legal_score = 0
    for keyword in LEGAL_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", query_lower):
            legal_score += 1

    # Decision logic
    if non_legal_score >= 1 and legal_score == 0:
        return "NON_LEGAL"
    if legal_score >= 1:
        return "LEGAL"

    # Ambiguous → treat as LEGAL (be inclusive)
    return "LEGAL"


# ── Refusal messages ──────────────────────────────────────────────────────

REFUSAL_HARMFUL = (
    "I'm sorry, I cannot assist with that request. As a legal research assistant, "
    "I can explain the law and its consequences, but I cannot help plan or facilitate "
    "illegal activities.\n\n"
    "If you have a legal question about rights, procedures, or consequences, "
    "I'd be happy to help with that instead."
)

REFUSAL_NON_LEGAL = (
    "I'm Nyaya, a legal research assistant focused on Indian law. "
    "I can only help with legal questions — such as your rights, court procedures, "
    "applicable laws, or legal remedies.\n\n"
    "Feel free to ask me any question about Indian law!"
)

REFUSAL_EMPTY_KB = (
    "I don't have any legal documents in my knowledge base yet. "
    "Please upload relevant legal documents (statutes, judgments, etc.) in the "
    "Knowledge Base section so I can provide accurate, cited answers.\n\n"
    "Without documents, I cannot provide reliable legal information."
)

REFUSAL_LOW_CONFIDENCE = (
    "I couldn't find sufficient information in my knowledge base to answer "
    "this question accurately. I don't want to risk providing incorrect legal information.\n\n"
    "**Suggestions:**\n"
    "- Upload the relevant Act or judgment to the Knowledge Base\n"
    "- Try rephrasing your question with specific section/article numbers\n"
    "- Consult a qualified advocate for this query"
)


# ── Post-generation verification ──────────────────────────────────────────

def verify_citations(answer: str, retrieved_chunks: list[dict]) -> tuple[str, list[str]]:
    """
    Verify that cited sections/cases in the answer exist in the retrieved context.
    Returns (cleaned_answer, list_of_warnings).
    """
    warnings = []

    # Extract all section references from the answer
    section_refs = re.findall(
        r"Section\s+(\d+[A-Za-z]*)\s+(?:of\s+)?(\w[\w\s]*?)(?:\.|,|\)|\]|\n)",
        answer, re.IGNORECASE
    )

    # Build set of sections present in retrieved chunks
    retrieved_sections = set()
    for chunk in retrieved_chunks:
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})
        # From metadata
        if meta.get("section_or_article"):
            retrieved_sections.add(str(meta["section_or_article"]).lower())
        # From text
        for m in re.finditer(r"(?:section|article|§)\s+(\d+[A-Za-z]*)", text, re.IGNORECASE):
            retrieved_sections.add(m.group(1).lower())

    # Check each citation
    for sec_num, act_name in section_refs:
        if sec_num.lower() not in retrieved_sections:
            warnings.append(
                f"Section {sec_num} of {act_name.strip()} was cited but not found in retrieved context"
            )

    return answer, warnings


def check_confidence(results: list[dict], threshold: float = 0.01) -> bool:
    """
    Check if retrieval results are confident enough to generate an answer.
    Returns True if confidence is sufficient.
    """
    if not results:
        return False

    # Check RRF scores
    top_score = max(r.get("rrf_score", r.get("score", 0)) for r in results[:3])
    return top_score >= threshold
