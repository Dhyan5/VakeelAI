"""
NumPy-based retrieval engine - no FAISS, no Chroma, no external vector DB.

This module provides:
1. Loading and saving of the indexed knowledge base (.npy embeddings + .json metadata)
2. Top-K cosine similarity search using pure NumPy
3. Minimum similarity threshold enforcement (anti-hallucination guardrail)
"""

import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from embedding import get_embedding_service, MultilingualEmbeddingService


class LegalRetrievalEngine:
    """
    Simple retrieval engine using NumPy arrays for embeddings and metadata JSON.

    Index format (on disk):
    - embeddings.npy: 2D float32 array of shape (n_chunks, embedding_dim)
    - metadata.json: List of dicts with keys: text, source, section, language

    This is the entire "database" - simple, fast, and <1GB for a large KB.
    """

    def __init__(self, index_dir: str = "knowledge_base_index"):
        """
        Initialize the retrieval engine.

        Args:
            index_dir: Directory containing embeddings.npy and metadata.json
        """
        self.index_dir = Path(index_dir)
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: List[Dict[str, Any]] = []
        self.embedding_dim = 384  # From MiniLM model
        self.embedding_service = get_embedding_service()
        self._load_index()

    def _load_index(self):
        """Load or initialize the index."""
        embeddings_path = self.index_dir / "embeddings.npy"
        metadata_path = self.index_dir / "metadata.json"

        if embeddings_path.exists() and metadata_path.exists():
            self.embeddings = np.load(str(embeddings_path))
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"Loaded index: {len(self.metadata)} chunks")
        else:
            # Initialize empty index
            self.embeddings = np.zeros((0, self.embedding_dim), dtype=np.float32)
            self.metadata = []
            print("Created new empty index")

    def _save_index(self):
        """Save the current index to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        np.save(str(self.index_dir / "embeddings.npy"), self.embeddings)
        with open(self.index_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add new chunks to the index.

        Args:
            chunks: List of dicts with 'text' and metadata fields

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        texts = [c['text'] for c in chunks]
        new_embeddings = self.embedding_service.embed_texts(texts)

        # Append to existing arrays
        if self.embeddings.shape[0] == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.metadata.extend(chunks)
        self._save_index()

        return len(chunks)

    def clear_index(self):
        """Clear all chunks from the index."""
        self.embeddings = np.zeros((0, self.embedding_dim), dtype=np.float32)
        self.metadata = []
        self._save_index()
        print("Index cleared")

    def retrieve(self, query: str, top_k: int = 5,
                min_similarity: float = 0.4) -> List[Dict[str, Any]]:
        """
        Retrieve top-K chunks most similar to the query.

        Args:
            query: User query text (any language)
            top_k: Maximum number of results to return
            min_similarity: Minimum cosine similarity threshold (anti-hallucination)

        Returns:
            List of matching chunks with similarity scores, sorted by score desc
        """
        if self.embeddings.shape[0] == 0:
            return []

        # Embed query
        query_embedding = self.embedding_service.embed_text(query)

        # Compute cosine similarities
        similarities = self.embedding_service.cosine_similarity(
            query_embedding, self.embeddings
        )

        # Get top-K indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by minimum similarity and build results
        results = []
        for idx in top_indices:
            sim = float(similarities[idx])
            if sim >= min_similarity:
                result = {
                    **self.metadata[idx],
                    'similarity': sim
                }
                results.append(result)

        return results

    def get_chunk_by_id(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by its index."""
        if 0 <= idx < len(self.metadata):
            return {**self.metadata[idx], 'id': idx}
        return None

    def __len__(self) -> int:
        """Return the number of chunks in the index."""
        return len(self.metadata)


def build_index_from_knowledge_base(
    kb_dir: str = "knowledge_base",
    output_dir: str = "knowledge_base_index",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> LegalRetrievalEngine:
    """
    Build the index from knowledge base files.

    Legal text requires careful chunking by section/clause boundaries,
    not naive sentence splitting (which breaks on "u/s", "S. 302", etc.)

    Args:
        kb_dir: Directory containing .txt/.pdf knowledge base files
        output_dir: Where to save embeddings.npy and metadata.json
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        Initialized LegalRetrievalEngine with the built index
    """
    import re

    def chunk_text_by_sections(text: str, source: str, language: str = "en") -> List[Dict[str, Any]]:
        """
        Chunk legal text by section markers.

        Legal Indian texts have patterns like:
        - "Section 302." or "S. 302."
        - "Section 302(1)" with sub-clauses
        - Indian Constitution: "Article 14", "Article 21"

        We split on section markers when possible, then fallback to size-based chunking.
        """
        # Detect language from script
        has_devanagari = bool(re.search(r'[ऀ-ॿ]', text))
        has_kannada = bool(re.search(r'[ಀ-೿]', text))

        if has_devanagari:
            # Hindi patterns
            section_pattern = r'(धारा\s*\d+[\w(]*\.?)'
        elif has_kannada:
            # Kannada patterns
            section_pattern = r'(ವಿಧಿ\s*\d+[\w(]*\.?)'
        else:
            # English patterns
            section_pattern = r'(Section\s*\d+[\w(]*\.?)'

        # Try to split by sections first
        chunks = []

        # Pattern to find section boundaries
        pattern = r'((?:Section|S\.|धारा|ವಿಧಿ)\s*\d+(?:\([\w\d]+\))?(?:\s*\n)?\.?)'

        # Split text at section markers
        parts = re.split(pattern, text)

        if len(parts) > 1:
            # Reconstruct with section headers
            current_section = ""
            for i, part in enumerate(parts):
                if part.strip() and re.match(r'^(Section|S\.|धारा|ವಿಧಿ)\s*\d', part.strip()):
                    # This is a section header
                    if current_section:
                        chunks.append(current_section.strip())
                    current_section = part
                else:
                    # This is content
                    current_section += part

            if current_section:
                chunks.append(current_section.strip())
        else:
            # Fallback: simple size-based chunking
            words = text.split()
            current_chunk = []
            current_length = 0

            for word in words:
                word_length = len(word) + 1  # +1 for space
                if current_length + word_length > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = current_chunk[-chunk_overlap:]  # Keep overlap
                    current_length = sum(len(w) + 1 for w in current_chunk)
                current_chunk.append(word)
                current_length += word_length

            if current_chunk:
                chunks.append(' '.join(current_chunk))

        # Build chunk metadata
        result = []
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text) < 20:  # Skip very short chunks
                continue

            # Try to extract section number
            section_match = re.search(r'(Section|S\.|धारा|ವಿಧಿ)\s*(\d+(?:\([\w\d]+\))?\.?)', chunk_text)
            section = section_match.group(0) if section_match else f"Chunk-{i}"

            result.append({
                'text': chunk_text.strip(),
                'source': source,
                'section': section,
                'language': language,
                'chunk_index': i
            })

        return result

    def read_file_content(filepath: Path) -> Tuple[str, str]:
        """Read text content from a file, detecting language."""
        try:
            # Try UTF-8 first
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1
            with open(filepath, 'r', encoding='latin-1') as f:
                text = f.read()

        # Detect language
        has_devanagari = bool(re.search(r'[ऀ-ॿ]', text))
        has_kannada = bool(re.search(r'[ಀ-೿]', text))

        if has_devanagari:
            language = "hi"
        elif has_kannada:
            language = "kn"
        else:
            language = "en"

        return text, language

    # Initialize engine
    engine = LegalRetrievalEngine(output_dir)
    engine.clear_index()

    # Process all files in knowledge base directory
    kb_path = Path(kb_dir)
    files_processed = 0
    total_chunks = 0

    for filepath in kb_path.glob("*.txt"):
        try:
            text, language = read_file_content(filepath)
            chunks = chunk_text_by_sections(text, filepath.name, language)

            if chunks:
                count = engine.add_chunks(chunks)
                total_chunks += count
                files_processed += 1
                print(f"  {filepath.name}: {len(chunks)} chunks")
        except Exception as e:
            print(f"  Error processing {filepath}: {e}")

    print(f"\nIndex built: {files_processed} files, {total_chunks} total chunks")
    return engine


# Global instance
_retrieval_engine: Optional[LegalRetrievalEngine] = None


def get_retrieval_engine() -> LegalRetrievalEngine:
    """Get or create the global retrieval engine instance."""
    global _retrieval_engine
    if _retrieval_engine is None:
        _retrieval_engine = LegalRetrievalEngine()
    return _retrieval_engine


def clear_retrieval_engine():
    """Clear the global retrieval engine."""
    global _retrieval_engine
    _retrieval_engine = None
