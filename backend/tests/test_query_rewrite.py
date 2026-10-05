import pytest
from app.rag.query_rewrite import map_ipc_to_bns, rewrite_legal_query

def test_map_ipc_to_bns():
    mappings = map_ipc_to_bns("What is the punishment under Section 302 IPC?")
    assert len(mappings) >= 1
    assert any(m.get("new_section") == "103" for m in mappings)

    mappings_420 = map_ipc_to_bns("He was booked under Section 420 IPC for cheating.")
    assert len(mappings_420) >= 1
    assert any(m.get("new_section") == "318" for m in mappings_420)

def test_rewrite_legal_query():
    rewritten = rewrite_legal_query("What is the penalty for cheque bounce?")
    assert "cheque" in rewritten.lower() or "negotiable" in rewritten.lower()

    rewritten_ipc = rewrite_legal_query("Punishment under Section 302 IPC")
    assert "103" in rewritten_ipc or "BNS" in rewritten_ipc
