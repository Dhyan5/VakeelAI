"""
Nyaya – Document ingestion pipeline.
Upload → extract → chunk → embed → index in ChromaDB + BM25.
"""

import hashlib
import uuid
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.rag.chunking import chunk_document, Chunk
from app.rag.ocr import extract_text, detect_act_name
from app.db.models import Document
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ── Globals (initialized lazily) ───────────────────────────────────────────
_chroma_client: Optional[chromadb.PersistentClient] = None
_embedding_fn = None
_bm25_index: Optional[dict] = None
_bm25_corpus: list[dict] = []  # [{chunk_id, tokens}]

COLLECTION_NAME = "nyaya_legal"
BM25_INDEX_PATH = Path(settings.data_dir) / "bm25_index.json"

# ── Progress tracking ──────────────────────────────────────────────────────
_ingest_progress: dict[str, dict] = {}  # job_id -> {status, progress, message, ...}


def get_progress(job_id: str) -> dict:
    return _ingest_progress.get(job_id, {"status": "unknown", "progress": 0})


def _set_progress(job_id: str, status: str, progress: float, message: str = ""):
    _ingest_progress[job_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "updated_at": datetime.utcnow().isoformat(),
    }


# ── ChromaDB ───────────────────────────────────────────────────────────────

def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# ── Embedding ──────────────────────────────────────────────────────────────

def get_embedding_fn():
    """Return local embedding function (fastembed or sentence-transformers)."""
    global _embedding_fn
    if _embedding_fn is not None:
        return _embedding_fn

    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name=settings.embedding_model)

        def embed(texts: list[str]) -> list[list[float]]:
            return [e.tolist() for e in model.embed(texts)]

        _embedding_fn = embed
        logger.info(f"Using fastembed with {settings.embedding_model}")
    except ImportError:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(settings.embedding_model)

            def embed(texts: list[str]) -> list[list[float]]:
                return model.encode(texts, normalize_embeddings=True).tolist()

            _embedding_fn = embed
            logger.info(f"Using sentence-transformers with {settings.embedding_model}")
        except ImportError:
            logger.error("No embedding library found. Install fastembed or sentence-transformers.")
            raise RuntimeError("Install fastembed: pip install fastembed")

    return _embedding_fn


# ── BM25 Index ─────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer for BM25."""
    import re
    return re.findall(r'\w+', text.lower())


def load_bm25_corpus():
    """Load saved BM25 corpus from disk."""
    global _bm25_corpus
    if BM25_INDEX_PATH.exists():
        _bm25_corpus = json.loads(BM25_INDEX_PATH.read_text())


def save_bm25_corpus():
    """Save BM25 corpus to disk."""
    BM25_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    BM25_INDEX_PATH.write_text(json.dumps(_bm25_corpus))


def add_to_bm25(chunks: list[Chunk]):
    """Add chunks to the BM25 corpus."""
    global _bm25_corpus
    for c in chunks:
        _bm25_corpus.append({
            "chunk_id": c.chunk_id,
            "tokens": _tokenize(c.text),
            "text": c.text[:500],  # Keep truncated text for display
            "metadata": c.metadata,
        })
    save_bm25_corpus()


def bm25_search(query: str, top_k: int = 20) -> list[dict]:
    """Search BM25 index and return top-k results with scores."""
    if not _bm25_corpus:
        return []

    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        logger.warning("rank_bm25 not installed, skipping BM25 search")
        return []

    corpus_tokens = [doc["tokens"] for doc in _bm25_corpus]
    bm25 = BM25Okapi(corpus_tokens)
    query_tokens = _tokenize(query)
    scores = bm25.get_scores(query_tokens)

    # Get top-k indices
    import numpy as np
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "chunk_id": _bm25_corpus[idx]["chunk_id"],
                "score": float(scores[idx]),
                "text": _bm25_corpus[idx]["text"],
                "metadata": _bm25_corpus[idx]["metadata"],
            })

    return results


# ── Ingestion ──────────────────────────────────────────────────────────────

def compute_file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_document(
    file_path: str,
    file_bytes: bytes,
    original_filename: str,
    category: str,
    act_name: Optional[str],
    year: Optional[int],
    db: Session,
    job_id: Optional[str] = None,
) -> str:
    """
    Full ingestion pipeline for a single document.
    Returns the document ID.
    """
    if not job_id:
        job_id = str(uuid.uuid4())

    _set_progress(job_id, "extracting", 0.1, "Extracting text...")

    # Check for duplicate
    file_hash = compute_file_hash(file_bytes)
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing and existing.status == "ready":
        _set_progress(job_id, "skipped", 1.0, "Document already ingested.")
        return existing.id

    doc_id = str(uuid.uuid4())

    # Save file
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / f"{doc_id}_{original_filename}"
    saved_path.write_bytes(file_bytes)

    # Extract text
    text = extract_text(str(saved_path), file_bytes)
    if not text.strip():
        _set_progress(job_id, "error", 0, "Could not extract text from this file.")
        _save_doc_record(db, doc_id, original_filename, str(saved_path), category,
                         act_name, year, file_hash, len(file_bytes), 0, "error",
                         "No text extracted")
        return doc_id

    _set_progress(job_id, "detecting", 0.2, "Detecting document info...")

    # Auto-detect act name and year if not provided
    if not act_name or not year:
        detected_name, detected_year = detect_act_name(original_filename, text)
        act_name = act_name or detected_name
        year = year or detected_year

    # Map category to document_type
    doc_type_map = {
        "statute": "statute",
        "supreme_court": "judgment",
        "high_court": "judgment",
        "rules": "rule",
        "notification": "notification",
        "law_commission": "report",
        "other": "other",
    }
    document_type = doc_type_map.get(category, "other")

    _set_progress(job_id, "chunking", 0.3, "Chunking document...")

    # Build chunk metadata
    doc_meta = {
        "act_name": act_name or original_filename,
        "year": year,
        "document_type": document_type,
        "category": category,
        "source_file": original_filename,
        "doc_id": doc_id,
    }

    # Chunk
    chunks = chunk_document(
        text, doc_meta,
        min_tokens=settings.chunk_min_tokens,
        max_tokens=settings.chunk_max_tokens,
    )

    if not chunks:
        _set_progress(job_id, "error", 0, "No chunks produced.")
        _save_doc_record(db, doc_id, original_filename, str(saved_path), category,
                         act_name, year, file_hash, len(file_bytes), 0, "error",
                         "No chunks produced")
        return doc_id

    _set_progress(job_id, "embedding", 0.5, f"Embedding {len(chunks)} chunks...")

    # Embed
    embed_fn = get_embedding_fn()
    texts = [c.text for c in chunks]

    # Batch embed (16 at a time to manage memory)
    all_embeddings = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = embed_fn(batch)
        all_embeddings.extend(batch_embeddings)
        progress = 0.5 + 0.3 * (i + len(batch)) / len(texts)
        _set_progress(job_id, "embedding", progress,
                      f"Embedded {min(i + batch_size, len(texts))}/{len(texts)} chunks...")

    _set_progress(job_id, "indexing", 0.85, "Indexing in vector DB...")

    # Index in ChromaDB
    collection = get_collection()
    chunk_ids = [c.chunk_id for c in chunks]
    metadatas = []
    for c in chunks:
        # ChromaDB requires flat string/int/float metadata
        meta = {}
        for k, v in c.metadata.items():
            if v is not None:
                meta[k] = str(v) if not isinstance(v, (int, float)) else v
        metadatas.append(meta)

    collection.add(
        ids=chunk_ids,
        embeddings=all_embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    _set_progress(job_id, "indexing_bm25", 0.9, "Building keyword index...")

    # Add to BM25
    add_to_bm25(chunks)

    _set_progress(job_id, "ready", 1.0, "Done!")

    # Save document record
    _save_doc_record(db, doc_id, original_filename, str(saved_path), category,
                     act_name, year, file_hash, len(file_bytes), len(chunks), "ready", None)

    return doc_id


def _save_doc_record(db, doc_id, original_filename, saved_path, category,
                     act_name, year, file_hash, file_size, chunk_count, status, error):
    doc = Document(
        id=doc_id,
        filename=str(saved_path),
        original_filename=original_filename,
        category=category,
        act_name=act_name,
        year=year,
        file_hash=file_hash,
        file_size=file_size,
        chunk_count=chunk_count,
        status=status,
        error_message=error,
    )
    db.add(doc)
    db.commit()


def delete_document(doc_id: str, db: Session):
    """Remove a document and its chunks from all indexes."""
    # Remove from ChromaDB
    collection = get_collection()
    try:
        # Get all chunk IDs for this doc
        results = collection.get(where={"doc_id": doc_id})
        if results["ids"]:
            collection.delete(ids=results["ids"])
    except Exception as e:
        logger.warning(f"Error removing from ChromaDB: {e}")

    # Remove from BM25
    global _bm25_corpus
    _bm25_corpus = [c for c in _bm25_corpus if c.get("metadata", {}).get("doc_id") != doc_id]
    save_bm25_corpus()

    # Remove from DB
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        # Delete file
        try:
            Path(doc.filename).unlink(missing_ok=True)
        except Exception:
            pass
        db.delete(doc)
        db.commit()


def get_document_count(db: Session) -> int:
    return db.query(Document).filter(Document.status == "ready").count()


def get_total_chunks() -> int:
    try:
        collection = get_collection()
        return collection.count()
    except Exception:
        return 0


def auto_ingest_knowledge_base(db: Session):
    """Automatically ingest documents from knowledge_base_dir on startup."""
    kb_dir = Path(settings.knowledge_base_dir)
    if not kb_dir.exists():
        return
    supported_exts = {".txt", ".pdf", ".docx", ".html", ".htm"}
    for file_path in sorted(kb_dir.glob("*.*")):
        if file_path.suffix.lower() in supported_exts:
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                existing = db.query(Document).filter(Document.file_hash == file_hash).first()
                if not existing or existing.status != "ready":
                    logger.info(f"Auto-ingesting knowledge base document: {file_path.name}")
                    ingest_document(
                        file_path=str(file_path),
                        file_bytes=content,
                        original_filename=file_path.name,
                        category="statute",
                        act_name=None,
                        year=None,
                        db=db,
                        job_id=f"auto_{file_path.stem}",
                    )
            except Exception as e:
                logger.warning(f"Error auto-ingesting {file_path.name}: {e}")

