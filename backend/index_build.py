"""
Build the knowledge base index for Legal RAG.

Usage:
    python index_build.py

This script:
1. Reads all .txt files from knowledge_base/
2. Chunks them by section boundaries (legal text aware)
3. Embeds all chunks with multilingual model
4. Saves to knowledge_base_index/embeddings.npy and metadata.json
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from retrieval import build_index_from_knowledge_base


def main():
    """Build the knowledge base index."""
    print("=" * 60)
    print("Legal RAG - Building Knowledge Base Index")
    print("=" * 60)
    print()

    # Build the index
    engine = build_index_from_knowledge_base(
        kb_dir="knowledge_base",
        output_dir="knowledge_base_index",
        chunk_size=500,
        chunk_overlap=50
    )

    print()
    print("=" * 60)
    print(f"Index built successfully!")
    print(f"  - {len(engine)} total chunks")
    print(f"  - Saved to: knowledge_base_index/")
    print("=" * 60)


if __name__ == "__main__":
    main()
