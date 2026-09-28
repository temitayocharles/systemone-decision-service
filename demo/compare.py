"""RAG-only versus RAG + System One evidence filtering.

The demo uses the stable v2 Decision Runtime contract.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any, Dict, List

import httpx


RAG_URL = os.getenv("RAG_URL", "http://localhost:8001").rstrip("/")
DECISION_URL = os.getenv("DECISION_URL", "http://localhost:8002").rstrip("/")


def post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    with httpx.Client(timeout=120) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def rag_only(question: str, collection: str, top_k: int) -> Dict[str, Any]:
    started = time.perf_counter()
    result = post_json(
        f"{RAG_URL}/v1/query",
        {
            "collection": collection,
            "question": question,
            "top_k": top_k,
        },
    )
    return {
        "answer": result.get("answer"),
        "sources": result.get("sources", []),
        "tokens": result.get("tokens", 0),
        "latency_ms": int((time.perf_counter() - started) * 1000),
    }


def decision_filtered(
    question: str,
    collection: str,
    top_k: int,
    threshold: float,
    provider: str | None,
) -> Dict[str, Any]:
    started = time.perf_counter()
    retrieved = post_json(
        f"{RAG_URL}/v1/retrieve",
        {
            "collection": collection,
            "question": question,
            "top_k": top_k,
        },
    )
    chunks: List[Dict[str, Any]] = retrieved.get("chunks", [])
    if not chunks:
        return {
            "kept": [],
            "dropped": [],
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "usage": {},
        }

    questions = {
        f"chunk_{idx}": {
            "type": "null",
            "instructions": (
                "Does this evidence chunk materially help answer the user's question?"
            ),
        }
        for idx, _ in enumerate(chunks)
    }
    payload: Dict[str, Any] = {
        "state": {
            "question": question,
            "chunks": {
                f"chunk_{idx}": chunk.get("text", "")
                for idx, chunk in enumerate(chunks)
            },
        },
        "questions": questions,
    }
    if provider:
        payload["provider"] = provider

    decision = post_json(f"{DECISION_URL}/v2/decide", payload)
    answers = decision.get("answers", {})

    kept, dropped = [], []
    for idx, chunk in enumerate(chunks):
        probability = float(
            (answers.get(f"chunk_{idx}") or {}).get("value", 0.0)
        )
        row = {**chunk, "relevance_probability": probability}
        (kept if probability >= threshold else dropped).append(row)

    return {
        "kept": kept,
        "dropped": dropped,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "usage": decision.get("usage", {}),
        "route": decision.get("route", {}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--collection", default="engineering")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--provider")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    output = {
        "rag_only": rag_only(
            args.question,
            args.collection,
            args.top_k,
        ),
        "rag_plus_decision": decision_filtered(
            args.question,
            args.collection,
            args.top_k,
            args.threshold,
            args.provider,
        ),
    }
    print(json.dumps(output, indent=2 if args.verbose else None))


if __name__ == "__main__":
    main()
