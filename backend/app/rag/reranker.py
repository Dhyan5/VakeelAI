"""
Nyaya – Re-ranker: uses a cross-encoder to re-rank retrieved chunks.
Falls back to score-based sorting if the model is not available.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_reranker = None


def get_reranker():
    """Load cross-encoder reranker model (lazy, cached)."""
    global _reranker
    if _reranker is not None:
        return _reranker

    try:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        logger.info("Loaded cross-encoder reranker")
        return _reranker
    except ImportError:
        logger.warning("sentence-transformers not installed, using score-based ranking")
        return None
    except Exception as e:
        logger.warning(f"Could not load reranker: {e}")
        return None


def rerank(query: str, results: list[dict], top_k: int = 8) -> list[dict]:
    """
    Re-rank results using a cross-encoder. Falls back to RRF/distance scores.
    """
    if not results:
        return []

    reranker = get_reranker()

    if reranker is not None:
        # Prepare pairs for cross-encoder
        pairs = [(query, r.get("text", "")) for r in results[:30]]  # Re-rank top 30
        try:
            scores = reranker.predict(pairs)
            for i, score in enumerate(scores):
                results[i]["rerank_score"] = float(score)
            results[:30] = sorted(results[:30], key=lambda x: x.get("rerank_score", 0), reverse=True)
        except Exception as e:
            logger.warning(f"Re-ranking failed: {e}")

    return results[:top_k]
