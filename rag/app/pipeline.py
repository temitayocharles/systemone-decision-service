from __future__ import annotations

import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from .chunker import chunk_directory_records
from .config import get_collection_dir
from .embeddings import EmbeddingClient
from .llm import LLMClient
from .store import VectorStore


def _simple_chunks(text: str, target_words: int = 650, overlap_words: int = 100) -> List[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, target_words - overlap_words)
    chunks = []
    for start in range(0, len(words), step):
        part = words[start:start + target_words]
        if not part:
            break
        chunks.append(" ".join(part))
        if len(part) < target_words:
            break
    return chunks


class RAGPipeline:
    def __init__(self) -> None:
        self.embedding_client = EmbeddingClient()
        self.store = VectorStore()
        self.llm = LLMClient()

    def _records(self, collection_name: str) -> List[Dict[str, Any]]:
        directory = get_collection_dir(collection_name)
        if not directory.exists():
            raise FileNotFoundError(f"Collection not found: {collection_name}")
        records = chunk_directory_records(directory)
        if not records:
            raise FileNotFoundError(f"No markdown files found for collection: {collection_name}")
        return records

    def provenance(self, collection_name: str) -> Dict[str, Any]:
        directory = get_collection_dir(collection_name)
        if directory.exists():
            records = self._records(collection_name)
            counts = Counter(record["source"] for record in records)
            source_paths = {record["source"]: record["source_path"] for record in records}
            documents = [
                {"source": source, "source_path": source_paths[source], "chunks": counts[source]}
                for source in sorted(counts)
            ]
            expected_chunks = len(records)
        else:
            documents = self.store.collection_documents(collection_name)
            expected_chunks = sum(int(doc.get("chunks", 0)) for doc in documents)

        indexed_records = self.store.collection_count(collection_name)
        return {
            "collection": collection_name,
            "documents": documents,
            "document_count": len(documents),
            "expected_chunks": expected_chunks,
            "indexed_records": indexed_records,
            "indexed": indexed_records > 0 and indexed_records >= expected_chunks,
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
        }

    def ingest_collection(self, collection_name: str) -> List[str]:
        records = self._records(collection_name)
        texts = [record["text"] for record in records]
        embeddings = [self.embedding_client.embed(text) for text in texts]
        metadatas = [
            {
                "source": record["source"],
                "source_path": record["source_path"],
                "chunk_index": record["chunk_index"],
                "collection": collection_name,
                "source_type": "repository",
            }
            for record in records
        ]
        self.store.add_documents(collection_name, texts, embeddings, metadatas=metadatas)
        return texts

    def ingest_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        source_counts: Counter = Counter()

        for document in documents:
            title = str(document["title"])
            content = str(document["content"])
            metadata = dict(document.get("metadata") or {})
            chunks = _simple_chunks(content) or [content]
            for chunk_index, chunk in enumerate(chunks):
                texts.append(chunk)
                item = {
                    "source": metadata.get("source") or title,
                    "source_path": metadata.get("source_path") or title,
                    "source_type": metadata.get("source_type") or "external",
                    "collection": collection_name,
                    "chunk_index": chunk_index,
                }
                for key in ("extension", "mimetype", "size_bytes", "modified_at", "content_mode"):
                    if metadata.get(key) is not None:
                        item[key] = metadata[key]
                metadatas.append(item)
                source_counts[item["source"]] += 1

        embeddings = [self.embedding_client.embed(text) for text in texts]
        self.store.add_documents(collection_name, texts, embeddings, metadatas=metadatas)
        return {
            "collection": collection_name,
            "documents": len(documents),
            "chunks": len(texts),
            "sources": [
                {"source": source, "chunks": count}
                for source, count in sorted(source_counts.items())
            ],
        }

    def retrieve(self, collection_name: str, question: str, top_k: int = 5) -> Dict[str, Any]:
        q_embedding = self.embedding_client.embed(question)
        return {"chunks": self.store.query(collection_name, q_embedding, top_k)}

    def query(self, collection_name: str, question: str, top_k: int = 5) -> Dict[str, Any]:
        retrieval_started = time.perf_counter()
        q_embedding = self.embedding_client.embed(question)
        matches = self.store.query(collection_name, q_embedding, top_k)
        retrieval_latency_ms = int((time.perf_counter() - retrieval_started) * 1000)

        context = "\n\n".join(match.get("text") or "" for match in matches if match.get("text"))
        prompt = (
            "Use the following evidence to answer the question. "
            "If the content does not answer the question, say so clearly.\n\n"
            f"Evidence:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
        )

        generation_started = time.perf_counter()
        answer, tokens_in, tokens_out = self.llm.generate(prompt)
        generation_latency_ms = int((time.perf_counter() - generation_started) * 1000)

        sources = []
        for rank, match in enumerate(matches, start=1):
            source = dict(match)
            source["rank"] = rank
            sources.append(source)

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
