from __future__ import annotations

from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import HTTPException
from pydantic import BaseModel, Field

from .app import app
from .runtime import DecisionRuntime
from .selection import ModelStats, SelectionPolicy
from .telemetry import summarize


runtime = DecisionRuntime()


class RuntimeRequest(BaseModel):
    state: Any
    questions: Dict[str, Dict[str, Any]] = Field(min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    policy: Optional[Dict[str, Any]] = None
    ensemble: Optional[List[str]] = None
    request_id: Optional[str] = None


class BatchRequest(BaseModel):
    requests: List[RuntimeRequest] = Field(min_length=1, max_length=100)


class BenchmarkRecord(BaseModel):
    provider: str
    model: str
    task_type: str
    samples: int = 0
    accuracy: Optional[float] = None
    ece: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    cost_per_1000: Optional[float] = None
    failure_rate: float = 0.0


@app.post("/v2/decide")
async def runtime_decide(payload: RuntimeRequest):
    try:
        policy = SelectionPolicy(**payload.policy) if payload.policy else None
        return await runtime.decide(
            state=payload.state,
            questions=payload.questions,
            provider=payload.provider,
            model=payload.model,
            policy=policy,
            ensemble=payload.ensemble,
            request_id=payload.request_id,
        )
    except (KeyError, LookupError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/v2/batch")
async def runtime_batch(payload: BatchRequest):
    try:
        return {
            "results": await runtime.batch(
                [request.model_dump() for request in payload.requests]
            )
        }
    except (KeyError, LookupError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/v2/providers")
async def providers():
    return {
        "providers": list(runtime.providers.names()),
        "default": runtime.default_provider,
    }


@app.get("/v2/metrics")
async def metrics(limit: int = 1000):
    return summarize(runtime.telemetry.read(limit=max(1, min(limit, 10000))))


@app.get("/v2/benchmarks")
async def benchmarks():
    return {"benchmarks": [s.__dict__ for s in runtime.benchmarks.load()]}


@app.put("/v2/benchmarks")
async def put_benchmark(payload: BenchmarkRecord):
    runtime.benchmarks.upsert(ModelStats(**payload.model_dump()))
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("decide.runtime_api:app", host="0.0.0.0", port=8002, reload=False)
