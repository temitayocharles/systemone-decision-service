from __future__ import annotations

import time
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_setting
from .pipeline import RAGPipeline

app = FastAPI(title="System One RAG Example Service")


class QueryRequest(BaseModel):
    collection: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class RetrieveRequest(BaseModel):
    collection: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class IngestRequest(BaseModel):
    collection: str = Field(..., min_length=1)


class ExternalDocument(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExternalIngestRequest(BaseModel):
    collection: str = Field(..., min_length=1)
    documents: List[ExternalDocument] = Field(min_length=1, max_length=500)


pipeline = RAGPipeline()


@app.get("/v1/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "version": "0.3.0"}


@app.get("/v1/provenance/{collection}")
def provenance(collection: str) -> Dict[str, Any]:
    try:
        return pipeline.provenance(collection)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"provenance failed: {exc}") from exc


@app.post("/v1/ingest")
def ingest(payload: IngestRequest) -> Dict[str, Any]:
    try:
        chunks = pipeline.ingest_collection(payload.collection)
        return {"collection": payload.collection, "chunks": len(chunks)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ingest failed: {exc}") from exc


@app.post("/v1/ingest/documents")
def ingest_documents(payload: ExternalIngestRequest) -> Dict[str, Any]:
    try:
        result = pipeline.ingest_documents(
            payload.collection,
            [doc.model_dump() for doc in payload.documents],
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"document ingest failed: {exc}") from exc


@app.post("/v1/retrieve")
def retrieve(payload: RetrieveRequest) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        result = pipeline.retrieve(payload.collection, payload.question, payload.top_k)
        result["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"retrieve failed: {exc}") from exc


@app.post("/v1/query")
def query(payload: QueryRequest) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        result = pipeline.query(payload.collection, payload.question, payload.top_k)
        result["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"query failed: {exc}") from exc


if __name__ == "__main__":
    uvicorn.run(
        "rag.app.main:app",
        host="0.0.0.0",
        port=int(get_setting("RAG_PORT", "8001")),
        reload=False,
    )
