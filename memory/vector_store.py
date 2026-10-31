"""
PROJECT NEXUS — Vector Memory Store
ChromaDB Long-Term Memory for Contextual Recall Across Sessions
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, List, Optional

from config import CHROMA_PERSIST_DIR

logger = logging.getLogger("nexus.memory")


class ResearchMemory:
    """Persistent ChromaDB-backed memory storage for Project Nexus."""
    COLLECTION_NAME = "nexus_research_memory"

    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
            
            # Simple offline embedding function to avoid network calls
            class OfflineHashEmbedding(EmbeddingFunction):
                def __call__(self, input: Documents) -> Embeddings:
                    embeddings = []
                    for doc in input:
                        # 64-dim normalized hash vector
                        h = hashlib.sha256(doc.encode("utf-8")).digest()
                        vec = [((b / 255.0) * 2.0 - 1.0) for b in h * 2][:64]
                        norm = sum(x**2 for x in vec) ** 0.5 or 1.0
                        embeddings.append([x / norm for x in vec])
                    return embeddings

            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=OfflineHashEmbedding(),
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.warning(f"ChromaDB persistent client initialization fallback: {e}")

    def _make_id(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]

    def store_research(
        self,
        query: str,
        findings: list[dict],
        report_markdown: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Stores research results in ChromaDB."""
        doc_id = self._make_id(query + datetime.now().isoformat())
        summary_text = f"Query: {query}\n\nReport:\n{report_markdown[:2500]}"
        meta = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "num_findings": str(len(findings)),
            "attribution": "Developed by Pranav, AI & DE Branch",
        }
        if metadata:
            meta.update({k: str(v) for k, v in metadata.items()})

        if self.collection:
            try:
                self.collection.add(
                    documents=[summary_text],
                    ids=[doc_id],
                    metadatas=[meta],
                )
            except Exception as e:
                logger.warning(f"Could not write to ChromaDB collection: {e}")
        return doc_id

    def recall_similar_research(self, query: str, n_results: int = 3) -> list[dict]:
        """Queries past research sessions with semantic similarity."""
        if not self.collection:
            return []
        try:
            count = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
            )
            recalled = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                for d, m in zip(docs, metas):
                    recalled.append({"content": d, "metadata": m})
            return recalled
        except Exception as e:
            logger.warning(f"ChromaDB search query failed: {e}")
            return []
