"""
RAG (Retrieval-Augmented Generation) Service.

Uses LangChain + ChromaDB + Google Generative AI Embeddings
to build a medical knowledge base and retrieve relevant context
for grounded LLM responses.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Use a lightweight TF-IDF based adapter backed by scikit-learn for embeddings.
# This keeps the RAG pipeline free and avoids heavyweight dependencies like
# PyTorch/transformers while remaining compatible with Chroma's embedding API.
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.settings import settings


class TFIDFEmbeddingAdapter:
    """Simple TF-IDF embedding adapter.

    Notes:
    - This is not a semantic embedding like sentence-transformers but provides a
      deterministic, local vector representation suitable for small RAG setups
      and CI/runtime environments where GPU/torch are unavailable.
    - The adapter fits the vectorizer on the first batch of documents passed to
      embed_documents(). If you prefer to control vocabulary, pass a pre-fit
      vectorizer or call fit on a corpus first.
    """

    def __init__(self):
        self._vectorizer = TfidfVectorizer()
        self._fitted = False

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if not self._fitted:
            mat = self._vectorizer.fit_transform(texts)
            self._fitted = True
        else:
            mat = self._vectorizer.transform(texts)
        return mat.toarray().tolist()

    def embed_query(self, text: str) -> list[float]:
        if not self._fitted:
            # If not yet fitted, fit with the single query to avoid crash; results
            # will be sparse until full corpus is added.
            self._vectorizer.fit([text])
            self._fitted = True
            mat = self._vectorizer.transform([text])
            return mat.toarray()[0].tolist()
        mat = self._vectorizer.transform([text])
        return mat.toarray()[0].tolist()

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return self.embed_documents(texts)

KNOWLEDGE_DIR = Path(__file__).parent.parent / "ml" / "rag" / "knowledge"


class RAGService:
    """Medical Knowledge Assistant — RAG pipeline."""

    def __init__(self):
        self._embeddings = None
        self._vector_store = None

    @property
    def embeddings(self):
        """Return an embeddings adapter instance.

        Uses a lightweight TF-IDF adapter by default (scikit-learn), which is
        deterministic and avoids heavyweight dependencies. This keeps the RAG
        pipeline runnable in constrained environments and on Render without
        GPU/torch installs. If you prefer semantic embeddings, swap this adapter
        for a sentence-transformers-backed implementation and update
        requirements accordingly.
        """
        if self._embeddings is None:
            self._embeddings = TFIDFEmbeddingAdapter()
        return self._embeddings

    @property
    def vector_store(self) -> Chroma:
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name="medical_knowledge",
                embedding_function=self.embeddings,
                persist_directory=settings.chromadb_path,
            )
        return self._vector_store

    def _load_documents(self) -> list[Document]:
        """Load medical knowledge documents from the knowledge directory."""
        docs: list[Document] = []
        if not KNOWLEDGE_DIR.exists():
            return docs

        for file_path in KNOWLEDGE_DIR.glob("*.txt"):
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                source = file_path.stem.replace("_", " ").title()
                docs.append(Document(
                    page_content=content,
                    metadata={"source": source, "file": file_path.name},
                ))

        for file_path in KNOWLEDGE_DIR.glob("*.md"):
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                source = file_path.stem.replace("_", " ").title()
                docs.append(Document(
                    page_content=content,
                    metadata={"source": source, "file": file_path.name},
                ))

        return docs

    def _rebuild_vector_store(self):
        """Drop and recreate the Chroma collection.

        Used when the persistent collection was created by a different embedding
        adapter (e.g. the old Google Generative AI embeddings) and its vector
        dimension no longer matches the current adapter.
        """
        store = self.vector_store
        try:
            store.reset_collection()
        except Exception:
            try:
                store.delete_collection()
            except Exception:
                pass
        self._vector_store = None

    def initialize_knowledge_base(self) -> int:
        """Load, chunk, embed, and store all medical documents."""
        documents = self._load_documents()
        if not documents:
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(documents)

        if chunks:
            try:
                self.vector_store.add_documents(chunks)
            except Exception:
                self._rebuild_vector_store()
                self.vector_store.add_documents(chunks)

        return len(chunks)

    def retrieve_context(self, query: str, k: int | None = None) -> list[Document]:
        """Retrieve relevant medical context for a query."""
        top_k = k or settings.rag_top_k
        return self.vector_store.similarity_search(query, k=top_k)

    def has_documents(self) -> bool:
        """Check if the knowledge base has any documents."""
        try:
            if self.vector_store._collection.count() <= 0:
                return False
            self.vector_store.similarity_search("test", k=1)
            return True
        except Exception:
            return False

    async def answer_with_rag(
        self,
        question: str,
        llm_service,
    ) -> str:
        """Answer a medical question using RAG context."""
        if not self.has_documents():
            return await llm_service.answer_medical_question(question)

        docs = self.retrieve_context(question)
        if not docs:
            return await llm_service.answer_medical_question(question)

        context_parts = []
        for doc in docs:
            context_parts.append(f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}")
        context = "\n\n".join(context_parts)

        return await llm_service.answer_medical_question(
            question=question,
            context=context,
        )

    def get_knowledge_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        try:
            count = self.vector_store._collection.count()
            return {"total_chunks": count, "initialized": count > 0}
        except Exception:
            return {"total_chunks": 0, "initialized": False}
