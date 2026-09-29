from __future__ import annotations

import time
from typing import Any, Dict, List

from .chunker import chunk_directory_records
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
        records = chunk_directory_records(directory)
        if not records:
            raise FileNotFoundError(
                f"No markdown files found for collection: {collection_name}"
            )
        texts = [record["text"] for record in records]
        embeddings = [self.embedding_client.embed(text) for text in texts]
        metadatas = [
            {
                "source": record["source"],
                "source_path": record["source_path"],
                "chunk_index": record["chunk_index"],
                "collection": collection_name,
            }
            for record in records
        ]
        self.store.add_documents(
            collection_name,
            texts,
            embeddings,
            metadatas=metadatas,
        )
        return texts

    def retrieve(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(collection_name, q_embedding, top_k)
        return {"chunks": matches}

    def query(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        retrieval_started = time.perf_counter()
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(collection_name, q_embedding, top_k)
        retrieval_latency_ms = int(
            (time.perf_counter() - retrieval_started) * 1000
        )

        context = "\n\n".join(
            match.get("text") or ""
            for match in matches
            if match.get("text")
        )
        prompt = (
            "Use the following evidence to answer the question. "
            "If the content does not answer the question, say so clearly.\n\n"
            f"Evidence:\n{context}\n\n"
            f"Question:\n{question}\n\nAnswer:"
        )

        generation_started = time.perf_counter()
        answer, tokens_in, tokens_out = self.llm.generate(prompt)
        generation_latency_ms = int(
            (time.perf_counter() - generation_started) * 1000
        )

        sources = []
        for rank, match in enumerate(matches, start=1):
            sources.append({
                "rank": rank,
                "text": match.get("text"),
                "source": match.get("source"),
                "source_path": match.get("source_path"),
                "chunk_index": match.get("chunk_index"),
                "collection": match.get("collection") or collection_name,
                "distance": match.get("distance"),
            })

        return {
            "answer": answer,
            "sources": sources,
            "source_count": len(sources),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "retrieval_latency_ms": retrieval_latency_ms,
            "generation_latency_ms": generation_latency_ms,
            "latency_ms": retrieval_latency_ms + generation_latency_ms,
        }
