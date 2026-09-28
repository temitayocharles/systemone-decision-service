from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import statistics
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from decide.runtime import DecisionRuntime
from decide.selection import ModelStats
from decide.statistics import percentile_nearest_rank


def ece(confidences: List[float], correct: List[int], bins: int = 10) -> float:
    if not confidences:
        return 0.0
    total = len(confidences)
    value = 0.0
    for idx in range(bins):
        lo, hi = idx / bins, (idx + 1) / bins
        members = [
            i for i, p in enumerate(confidences)
            if p >= lo and (p < hi or idx == bins - 1)
        ]
        if not members:
            continue
        avg_conf = statistics.mean(confidences[i] for i in members)
        avg_acc = statistics.mean(correct[i] for i in members)
        value += len(members) / total * abs(avg_conf - avg_acc)
    return value


async def run(args: argparse.Namespace) -> None:
    runtime = DecisionRuntime()
    dataset_path = Path(args.dataset)
    raw_bytes = dataset_path.read_bytes()
    rows = [
        json.loads(line)
        for line in raw_bytes.decode("utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise SystemExit("benchmark dataset is empty")

    confidences: List[float] = []
    correct: List[int] = []
    latencies: List[int] = []
    failures = 0

    for row in rows:
        try:
            result = await runtime.decide(
                state=row["state"],
                questions={"target": row["question"]},
                provider=args.provider,
                model=args.model,
            )
            answer = result["answers"]["target"]
            prediction = answer.get("value")
            confidence = float(answer.get("confidence", 0.0))
            expected = row["label"]
            correct.append(int(str(prediction) == str(expected)))
            confidences.append(confidence)
            latencies.append(int(result.get("latency_ms", 0)))
        except Exception:
            failures += 1

    if not latencies:
        raise SystemExit("no successful benchmark samples")

    stat = ModelStats(
        provider=args.provider,
        model=args.model,
        task_type=args.task_type,
        samples=len(rows),
        accuracy=sum(correct) / len(correct) if correct else 0.0,
        ece=ece(confidences, correct),
        p95_latency_ms=percentile_nearest_rank(latencies, 0.95),
        cost_per_1000=args.cost_per_1000,
        failure_rate=failures / len(rows),
        run_id=str(uuid.uuid4()),
        dataset_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        dataset_path=str(dataset_path),
    )
    runtime.benchmarks.upsert(stat)
    print(json.dumps(stat.__dict__, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--task-type", default="generic")
    parser.add_argument("--cost-per-1000", type=float)
    asyncio.run(run(parser.parse_args()))
