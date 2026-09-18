"""
Knowledge Base Seeding Script.
Reads statutes from knowledge_base/, parses and chunks with legal awareness,
and creates the NumPy embeddings + JSON metadata index.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from backend.retrieval import HybridLegalRetrievalEngine


def seed():
    print("=" * 60)
    print("Seeding Knowledge Base for VakeelAI Legal RAG...")
    print("=" * 60)

    kb_dir = PROJECT_ROOT / "knowledge_base"
    index_dir = PROJECT_ROOT / "knowledge_base_index"

    print(f"Source statutes directory: {kb_dir}")
    print(f"Target index directory:   {index_dir}")

    engine = HybridLegalRetrievalEngine(index_dir=str(index_dir))
    engine.rebuild_from_kb(kb_dir=str(kb_dir))

    print(f"\n[OK] Seeding complete! Total chunks indexed: {len(engine)}")
    print("Sample indexed chunks:")
    for chunk in engine.metadata[:5]:
        print(f"  • [{chunk.get('chunk_id')}] {chunk.get('act_name')} - {chunk.get('section_number')}: {chunk.get('section_title')}")

    print("=" * 60)


if __name__ == "__main__":
    seed()
