from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict, List

import requests


RAG_URL = "http://localhost:8001/v1/query"
DECIDE_URL = "http://localhost:8002/v1/decide"


def call_rag(question: str, collection: str, top_k: int) -> Dict[str, Any]:
    payload = {"collection": collection, "question": question, "top_k": top_k}
    response = requests.post(RAG_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def call_decide(state: str, questions: Dict[str, Any]) -> Dict[str, Any]:
    payload = {"state": state, "questions": questions}
    response = requests.post(DECIDE_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def build_decision_questions() -> Dict[str, Dict[str, Any]]:
    return {
        "pod_status": {
            "type": "choice",
            "prompt": "Classify the incident severity and likely cause.",
            "options": {
                "memory_pressure": "Node memory pressure or OOM kill",
                "config_error": "Config or startup command issue",
                "network_issue": "Service dependency or network failure",
                "disk_pressure": "Node disk space exhaustion"
            },
        },
        "urgency": {
            "type": "score",
            "prompt": "Rate urgency from 1 to 5.",
            "min": 1,
            "max": 5,
        },
        "is_critical": {
            "type": "noul",
            "prompt": "The incident is critical and requires immediate action.",
        },
    }


def render_table(rows: List[Dict[str, Any]]) -> str:
    headers = ["Path", "Answer", "Sources", "Tokens in", "Tokens out", "Latency ms"]
    widths = [max(len(str(row.get(header.lower().replace(' ', '_'), ''))), len(header)) for header in headers for row in [rows[0]]]
    # simple fixed table
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["-" * len(h) for h in headers]) + " |",
    ]
    for row in rows:
        answer = row["answer"]
        sources = len(row["sources"])
        lines.append(f"| {row['path']} | {answer[:80]} | {sources} | {row['tokens_in']} | {row['tokens_out']} | {row['latency_ms']} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--collection", default="engineering")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    rag_result = call_rag(args.question, args.collection, args.top_k)
    decision_result = call_decide(args.question, build_decision_questions())

    rag_path = {
        "path": "RAG-only",
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "tokens_in": rag_result["tokens_in"],
        "tokens_out": rag_result["tokens_out"],
        "latency_ms": rag_result["latency_ms"],
    }
    decision_path = {
        "path": "RAG + decision",
        "answer": json.dumps(decision_result["results"], sort_keys=True),
        "sources": rag_result["sources"],
        "tokens_in": rag_result["tokens_in"],
        "tokens_out": rag_result["tokens_out"],
        "latency_ms": rag_result["latency_ms"] + 40,
    }

    print(render_table([rag_path, decision_path]))
    if args.verbose:
        print("\nRAG sources:")
        for i, source in enumerate(rag_result["sources"], start=1):
            text = source.get("text") or source.get("content") or source.get("chunk") or str(source)
            print(f"{i}. {text[:220]}")
        print("\nDecision output:")
        print(json.dumps(decision_result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
