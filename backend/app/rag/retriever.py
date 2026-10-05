"""
Nyaya – Hybrid retriever: vector similarity + BM25, merged with
Reciprocal Rank Fusion. Supports exact metadata lookups for named provisions.
"""

import logging
from typing import Optional
from app.rag.ingest import get_collection, get_embedding_fn, bm25_search
from app.rag.query_rewrite import extract_provision_reference, expand_synonyms

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 60) -> list[dict]:
    """
    Merge multiple ranked result lists using RRF.
    Each result should have 'chunk_id' and 'text'.
    Returns merged list sorted by RRF score.
    """
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}

    for results in result_lists:
        for rank, result in enumerate(results):
            cid = result["chunk_id"]
            scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
            if cid not in docs:
                docs[cid] = result

    # Sort by RRF score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    merged = []
    for cid in sorted_ids:
        doc = docs[cid].copy()
        doc["rrf_score"] = scores[cid]
        merged.append(doc)

    return merged


def vector_search(query: str, top_k: int = 20, where: Optional[dict] = None) -> list[dict]:
    """Search ChromaDB with embedding similarity."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    embed_fn = get_embedding_fn()
    query_embedding = embed_fn([query])[0]

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, collection.count()),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    try:
        results = collection.query(**kwargs)
    except Exception as e:
        logger.error(f"ChromaDB query error: {e}")
        return []

    hits = []
    if results and results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            hits.append({
                "chunk_id": chunk_id,
                "text": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 1.0,
                "score": 1.0 - (results["distances"][0][i] if results["distances"] else 1.0),
            })

    return hits


def exact_provision_lookup(query: str) -> list[dict]:
    """
    If the query names a specific provision, fetch it via metadata filter.
    """
    refs = extract_provision_reference(query)
    if not refs:
        return []

    results = []
    collection = get_collection()
    if collection.count() == 0:
        return []

    for ref in refs:
        try:
            # Try metadata filter on section_or_article
            where_filter = {"section_or_article": ref["section"]}
            hits = collection.get(
                where=where_filter,
                include=["documents", "metadatas"],
            )
            if hits and hits["ids"]:
                for i, cid in enumerate(hits["ids"]):
                    results.append({
                        "chunk_id": cid,
                        "text": hits["documents"][i] if hits["documents"] else "",
                        "metadata": hits["metadatas"][i] if hits["metadatas"] else {},
                        "score": 1.0,  # Exact match gets max score
                        "exact_match": True,
                    })
        except Exception as e:
            logger.debug(f"Exact lookup failed for {ref}: {e}")

    return results


def hybrid_search(query: str, top_k: int = 20) -> list[dict]:
    """
    Hybrid search: exact lookup + vector + BM25, merged with RRF.
    """
    # 1. Exact provision lookup (highest priority)
    exact_results = exact_provision_lookup(query)

    # 2. Expand query with synonyms for broader recall
    expanded_query = expand_synonyms(query)

    # 3. Vector search
    vector_results = vector_search(expanded_query, top_k=top_k)

    # 4. BM25 keyword search
    bm25_results = bm25_search(expanded_query, top_k=top_k)

    # 5. Merge with RRF
    all_lists = []
    if exact_results:
        all_lists.append(exact_results)
    if vector_results:
        all_lists.append(vector_results)
    if bm25_results:
        all_lists.append(bm25_results)

    if not all_lists:
        return []

    merged = reciprocal_rank_fusion(all_lists)

    # Exact matches always go first
    exact_ids = {r["chunk_id"] for r in exact_results}
    exact_first = [r for r in merged if r["chunk_id"] in exact_ids]
    rest = [r for r in merged if r["chunk_id"] not in exact_ids]

    return exact_first + rest


def get_chunk_by_id(chunk_id: str) -> Optional[dict]:
    """Fetch a single chunk by ID for the citation drawer."""
    collection = get_collection()
    try:
        results = collection.get(
            ids=[chunk_id],
            include=["documents", "metadatas"],
        )
        if results and results["ids"]:
            return {
                "chunk_id": chunk_id,
                "text": results["documents"][0] if results["documents"] else "",
                "metadata": results["metadatas"][0] if results["metadatas"] else {},
            }
    except Exception:
        pass
    return None
