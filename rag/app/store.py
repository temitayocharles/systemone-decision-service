from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from .config import get_setting


class VectorStore:
    def __init__(self):
        host = get_setting("CHROMA_HOST", "localhost")
        port = int(get_setting("CHROMA_PORT", "8000"))
        mode = get_setting("CHROMA_MODE", "remote").lower()
        self.host = host
        self.port = port
        self.mode = mode
        self._fallback_dir = (
            Path(__file__).resolve().parents[2] / ".chroma"
        )
        self.client = None
        self._using_persistent = False

        if mode == "local":
            self.client = chromadb.PersistentClient(
                path=str(self._fallback_dir)
            )
            self._using_persistent = True
            return

        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
            )
            self.client.list_collections()
        except Exception:
            if mode != "remote_with_local_fallback":
                raise
            self.client = chromadb.PersistentClient(
                path=str(self._fallback_dir)
            )
            self._using_persistent = True

    def _fallback_to_persistent(self):
        if self._using_persistent:
            return
        if (
            get_setting("CHROMA_MODE", "remote").lower()
            != "remote_with_local_fallback"
        ):
            raise RuntimeError(
                "remote Chroma unavailable and fallback is disabled"
            )
        self.client = chromadb.PersistentClient(
            path=str(self._fallback_dir)
        )
        self._using_persistent = True

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def collection_count(self, name: str) -> int:
        collection = self.get_or_create_collection(name)
        return int(collection.count())

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
        ids = [
            self.document_id(collection_name, text)
            for text in texts
        ]
        kwargs: Dict[str, Any] = {
            "documents": texts,
            "embeddings": embeddings,
            "ids": ids,
        }
        if metadatas is not None:
            kwargs["metadatas"] = metadatas
        collection.upsert(**kwargs)

    def query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(collection_name)
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
        except Exception:
            self._fallback_to_persistent()
            collection = self.get_or_create_collection(
                collection_name
            )
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        output: List[Dict[str, Any]] = []
        for index, doc in enumerate(docs):
            item: Dict[str, Any] = {"text": doc}
            if metas and index < len(metas):
                item.update(metas[index] or {})
            if (
                distances
                and index < len(distances)
                and distances[index] is not None
            ):
                item["distance"] = float(distances[index])
            output.append(item)
        return output
