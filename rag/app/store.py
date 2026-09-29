from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from .config import get_setting


class VectorStore:
    def __init__(self):
        self.host = get_setting("CHROMA_HOST", "localhost")
        self.port = int(get_setting("CHROMA_PORT", "8000"))
        self.mode = get_setting("CHROMA_MODE", "remote").lower()
        self._fallback_dir = Path(__file__).resolve().parents[2] / ".chroma"
        self._using_persistent = False

        if self.mode == "local":
            self.client = chromadb.PersistentClient(path=str(self._fallback_dir))
            self._using_persistent = True
        else:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            self.client.list_collections()

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def collection_count(self, name: str) -> int:
        return int(self.get_or_create_collection(name).count())

    def collection_documents(self, name: str) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(name)
        result = collection.get(include=["metadatas"])
        counts: Counter = Counter()
        paths: Dict[str, str] = {}
        source_types: Dict[str, str] = {}
        for meta in result.get("metadatas") or []:
            meta = meta or {}
            source = meta.get("source") or "unknown"
            counts[source] += 1
            paths[source] = meta.get("source_path") or source
            source_types[source] = meta.get("source_type") or "external"
        return [
            {
                "source": source,
                "source_path": paths[source],
                "source_type": source_types[source],
                "chunks": counts[source],
            }
            for source in sorted(counts)
        ]

    @staticmethod
    def document_id(collection_name: str, text: str) -> str:
        body = f"{collection_name}\0{text}".encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        collection = self.get_or_create_collection(collection_name)
        ids = [self.document_id(collection_name, text) for text in texts]
        kwargs: Dict[str, Any] = {"documents": texts, "embeddings": embeddings, "ids": ids}
        if metadatas is not None:
            kwargs["metadatas"] = metadatas
        collection.upsert(**kwargs)

    def query(self, collection_name: str, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        output = []
        for index, doc in enumerate(docs):
            item: Dict[str, Any] = {"text": doc}
            if metas and index < len(metas):
                item.update(metas[index] or {})
            if distances and index < len(distances) and distances[index] is not None:
                item["distance"] = float(distances[index])
            output.append(item)
        return output
