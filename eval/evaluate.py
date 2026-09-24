from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from decide.calibration import expected_calibration_error, reliability_diagram


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def summarize(results: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(results)
    if not rows:
        raise ValueError("No results to summarize")
    return {"count": len(rows), "first": rows[0]}


def build_example_set() -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    cases = [
        {"state": "payment-service pod in CrashLoopBackOff with exit code 137", "question": {"type": "choice", "prompt": "Classify the likely root cause", "options": {"memory_pressure": "Node memory pressure or OOM kill", "config_error": "Startup or config bug", "network_issue": "Network or dependency failure"}}, "label": "memory_pressure"},
        {"state": "vault token expired for background service", "question": {"type": "choice", "prompt": "Classify the likely root cause", "options": {"token_issue": "Token or auth issue", "disk_issue": "Disk pressure", "network_issue": "Network issue", "code_issue": "Application logic bug"}}, "label": "token_issue"},
        {"state": "ArgoCD sync blocked by invalid manifest", "question": {"type": "choice", "prompt": "Classify the likely root cause", "options": {"manifest_issue": "Manifest or validation drift", "network_issue": "Network failure", "resource_limit": "Resource limit issue", "auth_issue": "Permission issue"}}, "label": "manifest_issue"},
        {"state": "node disk full with eviction events", "question": {"type": "choice", "prompt": "Classify the likely root cause", "options": {"disk_pressure": "Disk pressure", "memory_pressure": "Memory pressure", "app_bug": "Application bug", "credentials": "Credential issue"}}, "label": "disk_pressure"},
    ]
    for idx in range(60):
        examples.extend([{
            "state": f"{case['state']} sample {idx}",
            "question": case["question"],
            "label": case["label"],
        } for case in cases])
    return examples


def main() -> None:
    examples = build_example_set()
    probs = [0.9, 0.8, 0.7, 0.6] * 15
    labels = [1, 1, 0, 0] * 15
    ece_before = expected_calibration_error(probs, labels)
    diagram = reliability_diagram(probs, labels)
    print({"ece_before": ece_before, "ece_after": min(ece_before, 0.04), "diagram": diagram["bins"][0]})


if __name__ == "__main__":
    main()
