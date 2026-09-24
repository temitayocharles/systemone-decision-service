# Evaluation harness

## Scope

This project measures the choice, score, and noul decision paths against point-in-time evidence. The decision service is evaluated as a calibrated probability model. The RAG service is evaluated as a retrieval and generation path.

## Current implementation

The executable harness in `eval/evaluate.py` builds a deterministic labeled example set and computes a before/after ECE summary plus a reliability-diagram payload. The live API exposes the same calibration shape at `/v1/calibrate` and requires at least 50 examples per request.

The repository does not currently implement the LLM-as-judge or raw-logprob baselines, p95 benchmark collection, or file export for PNG/SVG reliability diagrams. Those are acceptance targets for a fuller evaluation pass, not claims about the current script.

## Example data

The current harness uses four incident-style choice cases repeated to produce 240 examples. It is a smoke/evaluation fixture, not the four-domain benchmark described in the original build packet.

## JSONL contract

Each line is a single JSON object.

```json
{"state": "...", "question": {"type": "choice", "prompt": "...", "options": {"a": "...", "b": "..."}}, "label": "a"}
```

The numbered label values use the option key or score value, as relevant to that question type.

## Target acceptance bars

- ECE after calibration under 0.05 on the validation split, per question type
- p95 latency under 500 ms for a single decision-service question
- Cost per 1,000 decisions under $1 on the chosen provider
- A/B/C baseline table published in the README or in the results output
- Temperature scaling must reduce ECE in the calibration run or the calibration step is declared failed

## Calibration proof currently available

The current proof is the before and after ECE values plus the reliability-diagram JSON payload returned by the harness or `/v1/calibrate`. PNG/SVG export is not implemented.

## Definitions

- ECE: expected calibration error
- p95 latency: 95th percentile latency for one request
- LLM-as-judge baseline: same task judged by a model with the same evidence set
- Raw logprobs baseline: unscaled log-probabilities from the decision engine
