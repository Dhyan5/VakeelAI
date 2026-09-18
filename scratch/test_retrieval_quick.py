import sys
import io
from pathlib import Path

# Fix Windows console UTF-8 printing
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from backend.retrieval import HybridLegalRetrievalEngine

engine = HybridLegalRetrievalEngine()
print(f"Loaded {len(engine)} chunks into Hybrid Retrieval Engine.\n")

queries = [
    ("English", "Can I get bail if police arrested me for a non-bailable crime?"),
    ("Hindi", "किसी ने मेरे साथ धोखे से पैसे ऐंठ लिए और संपत्ति हड़प ली"),
    ("Kannada", "ಪೊಲೀಸರು ಬಂಧಿಸಿದಾಗ ಜಾಮೀನು ಪಡೆಯಲು ಯಾವ ನಿಯಮಗಳಿವೆ?")
]

for lang, q in queries:
    print(f"==================================================")
    print(f"Language: {lang}")
    print(f"Query:    {q}")
    results = engine.retrieve(q, top_k=2)
    if not results:
        print("  [Result] No relevant law found in the knowledge base for this point.")
    for idx, r in enumerate(results, 1):
        print(f"  Result #{idx}:")
        print(f"    Chunk ID:       {r.get('chunk_id')}")
        print(f"    Act:            {r.get('act_name')}")
        print(f"    Section:        {r.get('section_number')}: {r.get('section_title')}")
        print(f"    Hybrid Score:   {r.get('similarity'):.4f} (Dense: {r.get('dense_score'):.4f}, BM25: {r.get('bm25_score'):.4f})")
    print()
