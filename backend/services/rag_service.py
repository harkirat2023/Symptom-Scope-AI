"""
RAG (Retrieval-Augmented Generation) Service.

Uses LangChain + ChromaDB + Google Generative AI Embeddings
to build a medical knowledge base and retrieve relevant context
for grounded LLM responses.
"""

from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.settings import settings

KNOWLEDGE_DIR = Path(__file__).parent.parent / "ml" / "rag" / "knowledge"


class RAGService:
    """Medical Knowledge Assistant — RAG pipeline."""

    def __init__(self):
        self._embeddings = None
        self._vector_store = None

    @property
    def embeddings(self) -> GoogleGenerativeAIEmbeddings:
        if self._embeddings is None:
            if not settings.gemini_api_key:
                raise RuntimeError("GEMINI_API_KEY is required for RAG embeddings.")
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,
                google_api_key=settings.gemini_api_key,
            )
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
            self.vector_store.add_documents(chunks)

        return len(chunks)

    def retrieve_context(self, query: str, k: int | None = None) -> list[Document]:
        """Retrieve relevant medical context for a query."""
        top_k = k or settings.rag_top_k
        return self.vector_store.similarity_search(query, k=top_k)

    def has_documents(self) -> bool:
        """Check if the knowledge base has any documents."""
        try:
            return self.vector_store._collection.count() > 0
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
