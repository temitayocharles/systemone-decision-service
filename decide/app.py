from __future__ import annotations

import math
import os
import time
from typing import Any, Dict, List

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .calibration import expected_calibration_error, reliability_diagram, softmax
from .config import TEMPERATURE
from .engine import DecisionEngine
from .schemas import CalibrationRequest, DecisionRequest, ErrorModel

app = FastAPI(title="System One Decision Service")
engine = DecisionEngine()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/v1/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "version": os.getenv("APP_VERSION", "0.1.0")}


@app.post("/v1/decide")
def decide(payload: DecisionRequest) -> Dict[str, Any]:
    try:
        start = time.perf_counter()
        result = engine.decide(payload.state, payload.questions)
        result["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/calibrate")
def calibrate(payload: CalibrationRequest) -> Dict[str, Any]:
    if len(payload.examples) < 50:
        raise HTTPException(status_code=400, detail="At least 50 examples required")

    probs: List[float] = []
    labels: List[int] = []
    for example in payload.examples:
        question = example.question
        state = example.state
        if payload.question_type == "choice":
            q = question.model_dump()
            answer = engine.evaluate_choice(q["options"], q["prompt"], state)
            best = answer["value"]
            prob = answer["probabilities"].get(best, 0.0)
            probs.append(float(prob))
            labels.append(1 if best == example.label else 0)
        elif payload.question_type == "score":
            q = question.model_dump()
            answer = engine.evaluate_score(q["prompt"], state, int(q["min"]), int(q["max"]), q.get("labels"))
            value = int(answer["value"])
            prob = answer["probabilities"].get(str(value), 0.0)
            probs.append(float(prob))
            labels.append(1 if value == int(example.label) else 0)
        else:
            q = question.model_dump()
            answer = engine.evaluate_noul(q["prompt"], state)
            value = float(answer["value"])
            probs.append(value)
            labels.append(1 if float(example.label) >= 0.5 else 0)

    before = expected_calibration_error(probs, labels)
    temperature = 1.0
    after = before
    if payload.question_type == "noul":
        adjusted = [float(max(v, 1.0 - v)) for v in probs]
        after = expected_calibration_error(adjusted, labels)
    else:
        for temp in [x / 10 for x in range(2, 81)]:
            logits = np.asarray([math.log(max(1e-6, p)) for p in probs], dtype=float)
            candidate = softmax(logits, temperature=temp)
            ece = expected_calibration_error(candidate, labels)
            if ece < after:
                after = ece
                temperature = temp

    return {
        "question_type": payload.question_type,
        "n_examples": len(payload.examples),
        "temperature": float(temperature),
        "ece_before": float(before),
        "ece_after": float(after),
        "reliability_diagram": reliability_diagram(probs, labels),
    }


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "8002"))
    uvicorn.run("decide.app:app", host="0.0.0.0", port=port, reload=False)
