from __future__ import annotations

import time
from typing import Any, Dict, List

from .chunker import chunk_directory
from .config import get_collection_dir
from .embeddings import EmbeddingClient
from .llm import LLMClient
from .store import VectorStore


class RAGPipeline:
    def __init__(self) -> None:
        self.embedding_client = EmbeddingClient()
        self.store = VectorStore()
        self.llm = LLMClient()

    def ingest_collection(self, collection_name: str) -> List[str]:
        directory = get_collection_dir(collection_name)
        chunks = chunk_directory(directory)
        if not chunks:
            raise FileNotFoundError(f"No markdown files found for collection: {collection_name}")
        embeddings = [self.embedding_client.embed(chunk) for chunk in chunks]
        self.store.add_documents(collection_name, chunks, embeddings)
        return chunks

    def retrieve(
        self, collection_name: str, question: str, top_k: int = 5
    ) -> Dict[str, Any]:
        """Raw retrieval: the same chunks /v1/query would use, without generation.

        Exists so downstream consumers (like the decision layer) can work from
        the retrieved evidence directly instead of reusing generated answers.
        """
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(collection_name, q_embedding, top_k)
        return {"chunks": matches}

    def query(self, collection_name: str, question: str, top_k: int = 5) -> Dict[str, Any]:
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(collection_name, q_embedding, top_k)
        context = "\n\n".join(match.get("text") or "" for match in matches if match.get("text"))
        prompt = (
            "Use the following evidence to answer the question. "
            "If the content does not answer the question, say so clearly.\n\n"
            f"Evidence:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        )
        start = time.perf_counter()
        answer, tokens_in, tokens_out = self.llm.generate(prompt)
        latency_ms = int((time.perf_counter() - start) * 1000)
        source_payload = []
        for match in matches:
            text = match.get("text") or match.get("content") or match.get("chunk")
            source_payload.append({"text": text})
        return {
            "answer": answer,
            "sources": source_payload,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": latency_ms,
        }
