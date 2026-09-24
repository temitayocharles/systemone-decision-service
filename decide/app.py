from __future__ import annotations

import asyncio
import math
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import config
from .calibration import (
    expected_calibration_error,
    fit_temperature_binary,
    fit_temperature_multiclass,
    load_temperatures,
    reliability_diagram,
    save_temperatures,
)
from .engine import DecisionEngine, EngineError
from .schemas import CalibrationRequest, DecisionRequest, ErrorModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = DecisionEngine()
    yield
    await app.state.engine.aclose()


app = FastAPI(title="System One Decision Service", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422, content={"detail": jsonable_encoder(exc.errors())}
    )


def _engine(request: Request) -> DecisionEngine:
    return request.app.state.engine


@app.get("/v1/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "version": config.APP_VERSION,
        "model": config.MODEL,
        "provider_configured": config.provider_configured(),
    }


@app.post("/v1/decide")
async def decide(payload: DecisionRequest, request: Request) -> Dict[str, Any]:
    engine = _engine(request)
    questions = {qid: q.model_dump() for qid, q in payload.questions.items()}
    try:
        start = time.perf_counter()
        results, usage = await engine.decide(payload.state, questions)
        latency_ms = int((time.perf_counter() - start) * 1000)
    except EngineError as exc:
        # The provider failed or is not configured. We refuse to guess:
        # a 502 with a clear reason instead of invented probabilities.
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    temps = engine.temperatures
    return {
        "results": results,
        "meta": {
            "model": config.MODEL,
            "temperatures": {k: float(v) for k, v in temps.items()},
            "calibrated": {k: abs(float(v) - 1.0) > 1e-9 for k, v in temps.items()},
            "latency_ms": latency_ms,
            "usage": {
                "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                "completion_tokens": int(usage.get("completion_tokens", 0)),
                "total_tokens": int(usage.get("total_tokens", 0)),
            },
            "note": (
                "Probabilities are the provider model's own token distribution, "
                "temperature-scaled. Token counts are reported by the provider; "
                "when the provider omits them they read 0, never estimated."
            ),
        },
    }


def _scaled_confidence(probvecs: List[List[float]], temperature: float) -> List[float]:
    out = []
    for pv in probvecs:
        scaled = [math.log(max(p, 1e-12)) / temperature for p in pv]
        m = max(scaled)
        exps = [math.exp(s - m) for s in scaled]
        total = sum(exps)
        out.append(max(e / total for e in exps))
    return out


async def _calibrate_choice(
    raw: DecisionEngine, payload: CalibrationRequest
) -> Dict[str, Any]:
    async def one(example) -> tuple:
        q = example.question.model_dump()
        ans = await raw.evaluate_choice(q["options"], q["prompt"], example.state)
        keys = list(q["options"].keys())
        if example.label not in keys:
            raise HTTPException(
                status_code=400,
                detail=f"label {example.label!r} is not one of the option keys",
            )
        return [float(ans["probabilities"][k]) for k in keys], keys.index(example.label)

    probvecs: List[List[float]] = []
    label_idx: List[int] = []
    for pv, li in await asyncio.gather(*(one(e) for e in payload.examples)):
        probvecs.append(pv)
        label_idx.append(li)

    pred = [max(range(len(pv)), key=lambda i: pv[i]) for pv in probvecs]
    correct = [int(p == li) for p, li in zip(pred, label_idx)]
    conf_before = [max(pv) for pv in probvecs]
    ece_before = expected_calibration_error(conf_before, correct)

    logits = [[math.log(max(p, 1e-12)) for p in pv] for pv in probvecs]
    temperature, _nll, ece_after = fit_temperature_multiclass(label_idx, logits)
    conf_after = _scaled_confidence(probvecs, temperature)

    return {
        "temperature": temperature,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "accuracy": float(np.mean(correct)),
        "reliability_diagram": reliability_diagram(conf_after, correct),
    }


async def _calibrate_score(
    raw: DecisionEngine, payload: CalibrationRequest
) -> Dict[str, Any]:
    async def one(example) -> tuple:
        q = example.question.model_dump()
        labels = q.get("labels")
        points = (
            sorted(set(int(v) for v in labels))
            if labels
            else list(range(int(q["min"]), int(q["max"]) + 1))
        )
        ans = await raw.evaluate_score(
            q["prompt"], example.state, int(q["min"]), int(q["max"]), labels
        )
        try:
            li = points.index(int(example.label))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"label {example.label!r} is not a candidate score",
            )
        return [float(ans["probabilities"][str(p)]) for p in points], li

    probvecs: List[List[float]] = []
    label_idx: List[int] = []
    for pv, li in await asyncio.gather(*(one(e) for e in payload.examples)):
        probvecs.append(pv)
        label_idx.append(li)

    pred = [max(range(len(pv)), key=lambda i: pv[i]) for pv in probvecs]
    correct = [int(p == li) for p, li in zip(pred, label_idx)]
    conf_before = [max(pv) for pv in probvecs]
    ece_before = expected_calibration_error(conf_before, correct)

    logits = [[math.log(max(p, 1e-12)) for p in pv] for pv in probvecs]
    temperature, _nll, ece_after = fit_temperature_multiclass(label_idx, logits)
    conf_after = _scaled_confidence(probvecs, temperature)

    return {
        "temperature": temperature,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "accuracy": float(np.mean(correct)),
        "reliability_diagram": reliability_diagram(conf_after, correct),
    }


async def _calibrate_noul(
    raw: DecisionEngine, payload: CalibrationRequest
) -> Dict[str, Any]:
    async def one(example) -> tuple:
        q = example.question.model_dump()
        ans = await raw.evaluate_noul(q["prompt"], example.state)
        return float(ans["value"]), int(float(example.label) >= 0.5)

    probs: List[float] = []
    labels: List[int] = []
    for p, lab in await asyncio.gather(*(one(e) for e in payload.examples)):
        probs.append(p)
        labels.append(lab)

    pred = [int(p >= 0.5) for p in probs]
    correct = [int(p == lab) for p, lab in zip(pred, labels)]
    conf_before = [max(p, 1.0 - p) for p in probs]
    ece_before = expected_calibration_error(conf_before, correct)

    temperature, _nll, ece_after = fit_temperature_binary(labels, probs)

    return {
        "temperature": temperature,
        "ece_before": ece_before,
        "ece_after": ece_after,
        "accuracy": float(np.mean(correct)),
        "reliability_diagram": reliability_diagram(conf_before, correct),
    }


@app.post("/v1/calibrate")
async def calibrate(payload: CalibrationRequest, request: Request) -> Dict[str, Any]:
    # Fit against raw (T=1.0) model probabilities so the fitted temperature
    # reflects the model, not a previous fit.
    raw = DecisionEngine(temperatures={"choice": 1.0, "score": 1.0, "noul": 1.0})
    try:
        try:
            if payload.question_type == "choice":
                stats = await _calibrate_choice(raw, payload)
            elif payload.question_type == "score":
                stats = await _calibrate_score(raw, payload)
            else:
                stats = await _calibrate_noul(raw, payload)
        except EngineError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        await raw.aclose()

    temperatures = load_temperatures()
    temperatures[payload.question_type] = float(stats["temperature"])
    save_temperatures(temperatures)
    _engine(request).reload_temperatures()

    return {
        "question_type": payload.question_type,
        "n_examples": len(payload.examples),
        "temperature": float(stats["temperature"]),
        "ece_before": float(stats["ece_before"]),
        "ece_after": float(stats["ece_after"]),
        "accuracy": float(stats["accuracy"]),
        "reliability_diagram": stats["reliability_diagram"],
        "note": (
            "Temperature fitted by minimizing NLL on this labeled set, then "
            "persisted. Re-run on fresh labeled data before trusting it in "
            "production; ECE on 50 examples is a rough estimate."
        ),
    }


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "8002"))
    uvicorn.run("decide.app:app", host="0.0.0.0", port=port, reload=False)
