"""
Initialize the RAG knowledge base.

Loads medical knowledge documents from ml/rag/knowledge/,
chunks them, generates embeddings, and stores them in ChromaDB.

Usage:
    python -m ml.rag.init_knowledge_base
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.rag_service import RAGService


def main():
    print("Initializing RAG knowledge base...")
    rag = RAGService()
    chunk_count = rag.initialize_knowledge_base()

    if chunk_count > 0:
        print(f"Knowledge base initialized with {chunk_count} chunks.")
    else:
        print("No documents found in ml/rag/knowledge/. Add .txt or .md files and rerun.")

    stats = rag.get_knowledge_stats()
    print(f"Vector store stats: {stats}")


if __name__ == "__main__":
    main()
