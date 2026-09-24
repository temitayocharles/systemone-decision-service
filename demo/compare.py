"""Honest RAG-only vs RAG-plus-decision comparison.

Path A (RAG-only): ask the RAG service for an answer over the top-k chunks.
Path B (RAG + decision): retrieve the SAME chunks via /v1/retrieve, then ask
the decision service one noul question per chunk, "does this chunk help answer
the user's question?", and keep only chunks at or above the threshold.

Everything reported is measured: latencies are timed here, token counts come
from the services' own responses. Nothing is estimated, reused across paths,
or padded.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict, List

import requests


RAG_URL = "http://localhost:8001"
DECIDE_URL = "http://localhost:8002"


def timed_post(url: str, payload: Dict[str, Any], timeout: int = 180):
    start = time.perf_counter()
    response = requests.post(url, json=payload, timeout=timeout)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return response, latency_ms


def path_a(question: str, collection: str, top_k: int) -> Dict[str, Any]:
    response, latency_ms = timed_post(
        f"{RAG_URL}/v1/query",
        {"collection": collection, "question": question, "top_k": top_k},
    )
    response.raise_for_status()
    body = response.json()
    return {
        "answer": body.get("answer", ""),
        "n_chunks": len(body.get("sources", [])),
        "tokens_in": body.get("tokens_in"),
        "tokens_out": body.get("tokens_out"),
        "latency_ms": latency_ms,
    }


def path_b(
    question: str, collection: str, top_k: int, threshold: float
) -> Dict[str, Any]:
    response, retrieve_ms = timed_post(
        f"{RAG_URL}/v1/retrieve",
        {"collection": collection, "question": question, "top_k": top_k},
    )
    response.raise_for_status()
    chunks = response.json().get("chunks", [])

    kept: List[Dict[str, Any]] = []
    decide_ms = 0
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for chunk in chunks:
        text = chunk.get("text", "")
        if not text.strip():
            continue
        resp, ms = timed_post(
            f"{DECIDE_URL}/v1/decide",
            {
                "state": text,
                "questions": {
                    "actionable": {
                        "type": "noul",
                        "prompt": (
                            "This chunk contains information that helps answer "
                            f"the user's question: {question}"
                        ),
                    }
                },
            },
        )
        decide_ms += ms
        if resp.status_code == 502:
            raise RuntimeError(
                "decision service has no model provider configured "
                f"({resp.json().get('detail')}). Set DECIDE_API_KEY; refusing to fake it."
            )
        resp.raise_for_status()
        body = resp.json()
        p = float(body["results"]["actionable"]["value"])
        for key in usage:
            usage[key] += int((body.get("meta") or {}).get("usage", {}).get(key, 0) or 0)
        if p >= threshold:
            kept.append({"p_actionable": round(p, 3), "text": text})

    return {
        "kept": kept,
        "n_chunks": len(chunks),
        "n_kept": len(kept),
        "usage": usage,
        "latency_ms": retrieve_ms + decide_ms,
        "retrieve_ms": retrieve_ms,
        "decide_ms": decide_ms,
    }


def fmt_tokens(value: Any) -> str:
    return str(value) if isinstance(value, int) else "n/a (not reported)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--collection", default="engineering")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    a = path_a(args.question, args.collection, args.top_k)
    try:
        b = path_b(args.question, args.collection, args.top_k, args.threshold)
    except RuntimeError as exc:
        print(f"path B unavailable: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Question: {args.question}")
    print(f"Collection: {args.collection}, top_k={args.top_k}, noul threshold={args.threshold}")
    print()
    print("| Path | Result | Evidence | Tokens in | Tokens out | Latency (measured) |")
    print("| ---- | ------ | -------- | --------- | ---------- | ------------------ |")
    print(
        f"| RAG-only | answer ({len(a['answer'])} chars) | "
        f"{a['n_chunks']} chunks shown | {fmt_tokens(a['tokens_in'])} | "
        f"{fmt_tokens(a['tokens_out'])} | {a['latency_ms']} ms |"
    )
    print(
        f"| RAG + decision | {b['n_kept']} actionable chunks kept | "
        f"{b['n_kept']}/{b['n_chunks']} chunks (retrieve {b['retrieve_ms']} ms + "
        f"decide {b['decide_ms']} ms) | {b['usage']['prompt_tokens']} | "
        f"{b['usage']['completion_tokens']} | {b['latency_ms']} ms |"
    )
    print()
    print(
        "Token counts are reported by each service for its own calls. "
        "RAG retrieval embeddings are not token-counted by the RAG service, "
        "so they are marked n/a rather than estimated."
    )

    if args.verbose:
        print("\nPath B kept chunks (P(actionable)):")
        for i, chunk in enumerate(b["kept"], start=1):
            print(f"\n{i}. p={chunk['p_actionable']}\n{chunk['text'][:400]}")


if __name__ == "__main__":
    main()
