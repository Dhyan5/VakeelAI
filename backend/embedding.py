"""
Multilingual embedding service using paraphrase-multilingual-MiniLM-L12-v2

Model: paraphrase-multilingual-MiniLM-L12-v2
- Covers 50+ languages including English, Hindi (Devanagari), Kannada (Kannada script)
- Embedding dimension: 384
- Model size: ~470MB downloaded, ~1GB RAM at runtime for inference
- Uses sentence-transformers library

This single model enables cross-lingual retrieval: embed English statutes and
Kannada/Hindi queries in the same vector space, allowing direct matching without
separate translation infrastructure.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional
import os

class MultilingualEmbeddingService:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the multilingual embedding model.

        Args:
            model_name: The sentence-transformers model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the model with caching."""
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.

        Args:
            text: Input text (can be English, Hindi, or Kannada)

        Returns:
            1D numpy array of shape (384,)
        """
        if not text or not text.strip():
            return np.zeros(384, dtype=np.float32)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple text strings.

        Args:
            texts: List of input texts

        Returns:
            2D numpy array of shape (len(texts), 384)
        """
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings to unit vectors for cosine similarity.

        Args:
            embeddings: 2D array of shape (n, 384)

        Returns:
            Normalized 2D array
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return embeddings / norms

    def cosine_similarity(self, query_embedding: np.ndarray,
                         doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between query and document embeddings.

        Args:
            query_embedding: 1D array of shape (384,)
            doc_embeddings: 2D array of shape (n, 384)

        Returns:
            1D array of similarities of shape (n,)
        """
        query_norm = self.normalize_embeddings(query_embedding.reshape(1, -1))[0]
        docs_norm = self.normalize_embeddings(doc_embeddings)
        return np.dot(docs_norm, query_norm)


# Global instance for reuse
_embedding_service: Optional[MultilingualEmbeddingService] = None


def get_embedding_service() -> MultilingualEmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = MultilingualEmbeddingService()
    return _embedding_service


def clear_embedding_service():
    """Clear the global embedding service (useful for testing)."""
    global _embedding_service
    _embedding_service = None
