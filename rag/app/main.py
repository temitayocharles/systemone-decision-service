from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_setting
from .pipeline import RAGPipeline

app = FastAPI(title="System One RAG Service")


class QueryRequest(BaseModel):
    collection: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class IngestRequest(BaseModel):
    collection: str = Field(..., min_length=1)


class HealthResponse(BaseModel):
    status: str
    version: str


pipeline = RAGPipeline()


@app.on_event("startup")
def startup() -> None:
    for collection_name in ["engineering", "business"]:
        try:
            pipeline.ingest_collection(collection_name)
        except Exception:
            pass


@app.get("/v1/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/v1/ingest")
def ingest(payload: IngestRequest) -> Dict[str, Any]:
    try:
        chunks = pipeline.ingest_collection(payload.collection)
        return {"collection": payload.collection, "chunks": len(chunks)}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"ingest failed: {exc}") from exc


@app.post("/v1/query")
def query(payload: QueryRequest) -> Dict[str, Any]:
    start = time.perf_counter()
    try:
        result = pipeline.query(payload.collection, payload.question, payload.top_k)
        result["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"query failed: {exc}") from exc


if __name__ == "__main__":
    port = int(get_setting("RAG_PORT", "8001"))
    uvicorn.run("rag.app.main:app", host="0.0.0.0", port=port, reload=False)
