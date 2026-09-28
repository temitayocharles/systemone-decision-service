from __future__ import annotations

import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class ModelStats:
    provider: str
    model: str
    task_type: str
    samples: int = 0
    accuracy: Optional[float] = None
    ece: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    cost_per_1000: Optional[float] = None
    failure_rate: float = 0.0


@dataclass
class SelectionPolicy:
    task_type: str = "generic"
    max_ece: Optional[float] = None
    max_p95_latency_ms: Optional[float] = None
    max_cost_per_1000: Optional[float] = None
    min_accuracy: Optional[float] = None
    preferred_provider: Optional[str] = None


class BenchmarkStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = Path(
            path
            or os.getenv(
                "SYSTEMONE_BENCHMARK_FILE",
                str(Path(__file__).resolve().parent / "data" / "benchmarks.json"),
            )
        )

    def load(self) -> List[ModelStats]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError):
            return []
        return [ModelStats(**item) for item in raw if isinstance(item, dict)]

    def save(self, stats: Iterable[ModelStats]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(s) for s in stats], indent=2, sort_keys=True))
        tmp.replace(self.path)

    def upsert(self, stat: ModelStats) -> None:
        rows = self.load()
        keyed: Dict[Tuple[str, str, str], ModelStats] = {
            (s.provider, s.model, s.task_type): s for s in rows
        }
        keyed[(stat.provider, stat.model, stat.task_type)] = stat
        self.save(keyed.values())


def choose_model(
    candidates: Iterable[ModelStats],
    policy: SelectionPolicy,
) -> ModelStats:
    eligible = []
    for stat in candidates:
        if stat.task_type not in {policy.task_type, "generic"}:
            continue
        if policy.preferred_provider and stat.provider != policy.preferred_provider:
            continue
        if policy.max_ece is not None and (
            stat.ece is None or stat.ece > policy.max_ece
        ):
            continue
        if policy.max_p95_latency_ms is not None and (
            stat.p95_latency_ms is None
            or stat.p95_latency_ms > policy.max_p95_latency_ms
        ):
            continue
        if policy.max_cost_per_1000 is not None and (
            stat.cost_per_1000 is None
            or stat.cost_per_1000 > policy.max_cost_per_1000
        ):
            continue
        if policy.min_accuracy is not None and (
            stat.accuracy is None or stat.accuracy < policy.min_accuracy
        ):
            continue
        eligible.append(stat)

    if not eligible:
        raise LookupError("no empirically qualified model satisfies the selection policy")

    def score(s: ModelStats) -> float:
        accuracy = s.accuracy if s.accuracy is not None else 0.5
        calibration = 1.0 - min(max(s.ece or 0.25, 0.0), 1.0)
        latency = 1.0 / (1.0 + (s.p95_latency_ms or 1000.0) / 1000.0)
        cost = 1.0 / (1.0 + (s.cost_per_1000 or 1.0))
        reliability = 1.0 - min(max(s.failure_rate, 0.0), 1.0)
        sample_weight = min(1.0, math.log10(max(s.samples, 1) + 1) / 2.0)
        return sample_weight * (
            0.35 * accuracy
            + 0.25 * calibration
            + 0.15 * latency
            + 0.10 * cost
            + 0.15 * reliability
        )

    return max(eligible, key=score)
