"""Offline evaluation of recorded decision-service predictions.

Reads a JSONL file where each line is a real recorded prediction::

    {"p": 0.83, "correct": 1}

and reports ECE, Brier score, accuracy, and a reliability diagram.

The predictions must come from actual runs of the decision service (for
example, captured while running /v1/calibrate against labeled data). This
script never invents predictions or metrics; with no input file it reports
nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from decide.calibration import expected_calibration_error, reliability_diagram


def load_predictions(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            p = float(row["p"])
            correct = int(row["correct"])
            if not 0.0 <= p <= 1.0 or correct not in (0, 1):
                raise ValueError(f"line {lineno}: p must be in [0,1], correct in {{0,1}}")
            rows.append({"p": p, "correct": correct})
    if not rows:
        raise ValueError("no predictions in file")
    return rows


def evaluate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    probs = [r["p"] for r in rows]
    correct = [r["correct"] for r in rows]
    brier = float(np.mean([(p - c) ** 2 for p, c in zip(probs, correct)]))
    return {
        "n": len(rows),
        "accuracy": float(np.mean(correct)),
        "brier_score": brier,
        "ece": expected_calibration_error(probs, correct),
        "reliability_diagram": reliability_diagram(probs, correct),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predictions",
        required=True,
        help="JSONL of real recorded predictions: {\"p\": float, \"correct\": 0|1}",
    )
    args = parser.parse_args()
    result = evaluate(load_predictions(Path(args.predictions)))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
