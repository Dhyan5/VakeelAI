"""
Nyaya – Query rewriting: legal synonym expansion, IPC→BNS mapping,
conversational follow-up resolution.
"""

import re
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Load IPC-BNS mapping
_mapping_data = None


def _load_mapping():
    global _mapping_data
    if _mapping_data is not None:
        return _mapping_data

    map_path = Path(__file__).parent.parent.parent / "data" / "ipc_bns_map.json"
    if map_path.exists():
        _mapping_data = json.loads(map_path.read_text())
    else:
        _mapping_data = {"mapping": [], "crpc_bnss": [], "evidence_bsa": []}

    return _mapping_data


# ── Legal synonym expansion ────────────────────────────────────────────────

LEGAL_SYNONYMS = {
    "ipc": ["indian penal code", "bharatiya nyaya sanhita", "bns"],
    "bns": ["bharatiya nyaya sanhita", "indian penal code", "ipc"],
    "crpc": ["code of criminal procedure", "bharatiya nagarik suraksha sanhita", "bnss"],
    "bnss": ["bharatiya nagarik suraksha sanhita", "code of criminal procedure", "crpc"],
    "evidence act": ["indian evidence act", "bharatiya sakshya adhiniyam", "bsa"],
    "bsa": ["bharatiya sakshya adhiniyam", "indian evidence act", "evidence act"],
    "cpc": ["code of civil procedure", "civil procedure code"],
    "ni act": ["negotiable instruments act"],
    "it act": ["information technology act"],
    "fir": ["first information report"],
    "bail": ["anticipatory bail", "regular bail", "default bail"],
    "chargesheet": ["charge sheet", "police report", "final report"],
    "cognizable offence": ["cognizable offense"],
    "non-cognizable": ["non cognizable"],
    "compoundable": ["compoundable offence"],
    "cheque bounce": ["dishonour of cheque", "section 138", "dishonor of cheque"],
}


def expand_synonyms(query: str) -> str:
    """Add relevant legal synonyms to the query for better retrieval."""
    query_lower = query.lower()
    expansions = []

    for term, synonyms in LEGAL_SYNONYMS.items():
        if term in query_lower:
            for syn in synonyms[:2]:  # Add max 2 synonyms
                if syn not in query_lower:
                    expansions.append(syn)

    if expansions:
        return f"{query} ({', '.join(expansions)})"
    return query


# ── IPC → BNS mapping ─────────────────────────────────────────────────────

def map_old_to_new(query: str) -> tuple[str, list[dict]]:
    """
    If query mentions IPC/CrPC/Evidence Act sections, map to BNS/BNSS/BSA.
    Returns (modified_query, list_of_mappings_found).
    """
    data = _load_mapping()
    mappings_found = []
    modified = query

    # IPC → BNS
    ipc_patterns = [
        re.compile(r"(?:section|sec\.?|§)\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?(?:of\s+)?(?:ipc|indian\s+penal\s+code)", re.IGNORECASE),
        re.compile(r"(?:ipc|indian\s+penal\s+code)\s*(?:section|sec\.?|§)?\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?", re.IGNORECASE),
    ]
    seen_ipc = set()
    for pat in ipc_patterns:
        for m in pat.finditer(query):
            sec = m.group(1).upper()
            if sec in seen_ipc:
                continue
            seen_ipc.add(sec)
            for entry in data.get("mapping", []):
                if entry["ipc"].upper() == sec:
                    mappings_found.append({
                        "old_law": "IPC",
                        "old_section": entry["ipc"],
                        "new_law": "BNS",
                        "new_section": entry["bns"],
                        "title": entry["title"],
                    })
                    modified += f" Section {entry['bns']} BNS"

    # BNS → IPC (reverse lookup)
    bns_patterns = [
        re.compile(r"(?:section|sec\.?|§)\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?(?:of\s+)?(?:bns|bharatiya\s+nyaya\s+sanhita)", re.IGNORECASE),
        re.compile(r"(?:bns|bharatiya\s+nyaya\s+sanhita)\s*(?:section|sec\.?|§)?\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?", re.IGNORECASE),
    ]
    seen_bns = set()
    for pat in bns_patterns:
        for m in pat.finditer(query):
            sec = m.group(1).upper()
            if sec in seen_bns:
                continue
            seen_bns.add(sec)
            for entry in data.get("mapping", []):
                if entry["bns"].upper() == sec:
                    mappings_found.append({
                        "old_law": "IPC",
                        "old_section": entry["ipc"],
                        "new_law": "BNS",
                        "new_section": entry["bns"],
                        "title": entry["title"],
                    })

    # CrPC → BNSS
    crpc_patterns = [
        re.compile(r"(?:section|sec\.?|§)\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?(?:of\s+)?(?:crpc|cr\.?\s*p\.?\s*c\.?|code\s+of\s+criminal\s+procedure)", re.IGNORECASE),
        re.compile(r"(?:crpc|cr\.?\s*p\.?\s*c\.?|code\s+of\s+criminal\s+procedure)\s*(?:section|sec\.?|§)?\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?", re.IGNORECASE),
    ]
    seen_crpc = set()
    for pat in crpc_patterns:
        for m in pat.finditer(query):
            sec = m.group(1).upper()
            if sec in seen_crpc:
                continue
            seen_crpc.add(sec)
            for entry in data.get("crpc_bnss", []):
                if entry["crpc"].upper() == sec:
                    mappings_found.append({
                        "old_law": "CrPC",
                        "old_section": entry["crpc"],
                        "new_law": "BNSS",
                        "new_section": entry["bnss"],
                        "title": entry["title"],
                    })
                    modified += f" Section {entry['bnss']} BNSS"

    # Evidence Act → BSA
    ea_patterns = [
        re.compile(r"(?:section|sec\.?|§)\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?(?:of\s+)?(?:evidence\s+act|indian\s+evidence\s+act|bsa|bharatiya\s+sakshya)", re.IGNORECASE),
        re.compile(r"(?:evidence\s+act|indian\s+evidence\s+act|bsa|bharatiya\s+sakshya)\s*(?:section|sec\.?|§)?\s*(\d+[A-Za-z]*)\s*(?:\([^)]*\)\s*)?", re.IGNORECASE),
    ]
    seen_ea = set()
    for pat in ea_patterns:
        for m in pat.finditer(query):
            sec = m.group(1).upper()
            if sec in seen_ea:
                continue
            seen_ea.add(sec)
            for entry in data.get("evidence_bsa", []):
                if entry["evidence_act"].upper() == sec:
                    mappings_found.append({
                        "old_law": "Evidence Act",
                        "old_section": entry["evidence_act"],
                        "new_law": "BSA",
                        "new_section": entry["bsa"],
                        "title": entry["title"],
                    })
                    modified += f" Section {entry['bsa']} BSA"

    return modified, mappings_found


def rewrite_followup(query: str, history: list[dict]) -> str:
    """
    Rewrite a follow-up query into a standalone query using conversation context.
    Simple heuristic: if query has pronouns or is very short, prepend context.
    """
    if not history:
        return query

    # Check for pronouns or short queries that likely refer to previous context
    follow_up_indicators = [
        r"\bthat\b", r"\bthis\b", r"\bit\b", r"\bthose\b",
        r"\bsame\b", r"\babove\b", r"\bsaid\b",
        r"\bwhat about\b", r"\bhow about\b", r"\band\b",
        r"\balso\b", r"\bmore\b", r"\bfurther\b",
    ]

    is_followup = len(query.split()) < 6
    if not is_followup:
        for pattern in follow_up_indicators:
            if re.search(pattern, query, re.IGNORECASE):
                is_followup = True
                break

    if not is_followup:
        return query

    # Get last user question and assistant topic for context
    context_parts = []
    for msg in reversed(history[-4:]):
        if msg.get("role") == "user":
            context_parts.append(f"Previous question: {msg['content']}")
            break

    if context_parts:
        return f"{query} (Context: {'; '.join(context_parts)})"

    return query


def extract_provision_reference(query: str) -> list[dict]:
    """
    Extract explicit provision references from a query for direct metadata lookup.
    Returns list of {act, section} dicts.
    """
    refs = []

    patterns = [
        # "Section 103 BNS" / "Section 103 of BNS"
        (re.compile(r"(?:section|sec\.?|§)\s+(\d+[A-Za-z]*)\s+(?:of\s+)?(\w+)", re.IGNORECASE),
         lambda m: {"section": m.group(1), "act": m.group(2).upper()}),
        # "Article 21" / "Article 21 of Constitution"
        (re.compile(r"(?:article|art\.?)\s+(\d+[A-Za-z]*)", re.IGNORECASE),
         lambda m: {"section": m.group(1), "act": "CONSTITUTION"}),
        # "Order IV Rule 1 CPC"
        (re.compile(r"Order\s+([IVXLCDM]+)\s+Rule\s+(\d+)", re.IGNORECASE),
         lambda m: {"section": f"Order {m.group(1)} Rule {m.group(2)}", "act": "CPC"}),
    ]

    for pattern, extractor in patterns:
        for m in pattern.finditer(query):
            refs.append(extractor(m))

    return refs


def map_ipc_to_bns(query: str) -> list[dict]:
    """Helper to return list of old-to-new law mappings for a query."""
    _, mappings = map_old_to_new(query)
    return mappings


def rewrite_legal_query(query: str) -> str:
    """Helper to apply synonym expansion and old-to-new law mapping."""
    expanded = expand_synonyms(query)
    modified, _ = map_old_to_new(expanded)
    return modified

