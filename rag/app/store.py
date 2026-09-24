from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List

import chromadb

from .config import get_setting


class VectorStore:
    def __init__(self):
        host = get_setting("CHROMA_HOST", "localhost")
        port = int(get_setting("CHROMA_PORT", "8000"))
        self._fallback_dir = Path(__file__).resolve().parents[2] / ".chroma"
        self.client = None
        self._using_persistent = False
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.list_collections()
        except Exception:
            self.client = chromadb.PersistentClient(path=str(self._fallback_dir))
            self._using_persistent = True

    def _fallback_to_persistent(self):
        if self._using_persistent:
            return
        self.client = chromadb.PersistentClient(path=str(self._fallback_dir))
        self._using_persistent = True

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def add_documents(self, collection_name: str, texts: List[str], embeddings: List[List[float]]) -> None:
        collection = self.get_or_create_collection(collection_name)
        ids = [str(uuid.uuid4()) for _ in texts]
        collection.add(documents=texts, embeddings=embeddings, ids=ids)

    def query(self, collection_name: str, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(collection_name)
        try:
            results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        except Exception:
            self._fallback_to_persistent()
            collection = self.get_or_create_collection(collection_name)
            results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        output: List[Dict[str, Any]] = []
        for index, doc in enumerate(docs):
            item = {"text": doc}
            if metas and index < len(metas):
                item.update(metas[index] or {})
            output.append(item)
        return output
