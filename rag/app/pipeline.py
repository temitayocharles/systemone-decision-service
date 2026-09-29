from __future__ import annotations

import time
from collections import Counter
from typing import Any, Dict, List

from .chunker import chunk_directory_records
from .config import get_collection_dir, get_setting
from .embeddings import EmbeddingClient
from .llm import LLMClient
from .store import VectorStore


class RAGPipeline:
    def __init__(self) -> None:
        self.embedding_client = EmbeddingClient()
        self.store = VectorStore()
        self.llm = LLMClient()

    def _records(self, collection_name: str) -> List[Dict[str, Any]]:
        directory = get_collection_dir(collection_name)
        if not directory.exists():
            raise FileNotFoundError(
                f"Collection not found: {collection_name}"
            )
        records = chunk_directory_records(directory)
        if not records:
            raise FileNotFoundError(
                f"No markdown files found for collection: {collection_name}"
            )
        return records

    def provenance(self, collection_name: str) -> Dict[str, Any]:
        records = self._records(collection_name)
        counts = Counter(record["source"] for record in records)
        source_paths = {
            record["source"]: record["source_path"]
            for record in records
        }
        documents = [
            {
                "source": source,
                "source_path": source_paths[source],
                "chunks": counts[source],
            }
            for source in sorted(counts)
        ]
        indexed_records = self.store.collection_count(
            collection_name
        )
        expected_chunks = len(records)
        return {
            "collection": collection_name,
            "documents": documents,
            "document_count": len(documents),
            "expected_chunks": expected_chunks,
            "indexed_records": indexed_records,
            "indexed": indexed_records >= expected_chunks,
            "embedding": {
                "provider": self.embedding_client.provider,
                "model": self.embedding_client.model,
            },
            "vector_store": {
                "type": "chroma",
                "mode": self.store.mode,
                "host": self.store.host,
                "port": self.store.port,
            },
            "stages": [
                {
                    "id": "documents",
                    "label": "Source documents",
                    "count": len(documents),
                },
                {
                    "id": "chunk",
                    "label": "Chunk",
                    "count": expected_chunks,
                },
                {
                    "id": "embed",
                    "label": "Embed",
                    "provider": self.embedding_client.provider,
                    "model": self.embedding_client.model,
                },
                {
                    "id": "store",
                    "label": "Store",
                    "records": indexed_records,
                    "backend": "Chroma",
                },
            ],
        }

    def ingest_collection(self, collection_name: str) -> List[str]:
        records = self._records(collection_name)
        texts = [record["text"] for record in records]
        embeddings = [
            self.embedding_client.embed(text)
            for text in texts
        ]
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
        matches = self.store.query(
            collection_name,
            q_embedding,
            top_k,
        )
        return {"chunks": matches}

    def query(
        self,
        collection_name: str,
        question: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        retrieval_started = time.perf_counter()
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(
            collection_name,
            q_embedding,
            top_k,
        )
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
            sources.append(
                {
                    "rank": rank,
                    "text": match.get("text"),
                    "source": match.get("source"),
                    "source_path": match.get("source_path"),
                    "chunk_index": match.get("chunk_index"),
                    "collection": (
                        match.get("collection")
                        or collection_name
                    ),
                    "distance": match.get("distance"),
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "source_count": len(sources),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "retrieval_latency_ms": retrieval_latency_ms,
            "generation_latency_ms": generation_latency_ms,
            "latency_ms": (
                retrieval_latency_ms + generation_latency_ms
            ),
        }
