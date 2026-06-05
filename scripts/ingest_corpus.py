"""CLI script to parse, chunk, embed, and index the policy corpus."""

import sys
from pathlib import Path

# Allow running as: python scripts/ingest_corpus.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import CHROMA_DIR, CORPUS_DIR
from src.document_loader import load_corpus
from src.ingest import build_vector_store, chunk_documents


def main() -> None:
    print(f"Loading corpus from: {CORPUS_DIR}")
    documents = load_corpus(CORPUS_DIR)
    print(f"  Loaded {len(documents)} document(s):")
    for doc in documents:
        print(f"    - {doc.metadata['source_id']}: {doc.metadata['source_title']}")

    chunks = chunk_documents(documents)
    print(f"\n  Created {len(chunks)} chunks (size={1000}, overlap={200})")

    print(f"\nEmbedding with free local model and storing in: {CHROMA_DIR}")
    vector_store = build_vector_store()
    count = vector_store._collection.count()
    print(f"\nDone. Indexed {count} chunks in ChromaDB.")


if __name__ == "__main__":
    main()
