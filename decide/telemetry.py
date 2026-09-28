from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class TelemetryStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = Path(
            path
            or os.getenv(
                "SYSTEMONE_TELEMETRY_FILE",
                str(Path(__file__).resolve().parent / "data" / "decisions.jsonl"),
            )
        )
        self._lock = threading.Lock()

    def record(self, event: Dict[str, Any]) -> None:
        payload = {"ts": time.time(), **event}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, separators=(",", ":"), default=str) + "\n")

    def read(self, limit: int = 1000) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = self.path.read_text(encoding="utf-8").splitlines()
        out = []
        for line in rows[-limit:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out


def summarize(events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(events)
    if not rows:
        return {"count": 0}
    latencies = sorted(float(r.get("latency_ms", 0)) for r in rows)
    idx = min(len(latencies) - 1, max(0, int(round(0.95 * (len(latencies) - 1)))))
    return {
        "count": len(rows),
        "p95_latency_ms": latencies[idx],
        "failures": sum(1 for r in rows if r.get("status") != "ok"),
        "tokens": sum(int((r.get("usage") or {}).get("total_tokens", 0)) for r in rows),
    }
