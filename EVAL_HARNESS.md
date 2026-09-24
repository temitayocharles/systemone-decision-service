# Evaluation harness

## Scope

This project measures the choice, score, and noul decision paths against point-in-time evidence. The decision service is evaluated as a calibrated probability model. The RAG service is evaluated as a retrieval and generation path.

## Current implementation

`eval/evaluate.py` is an offline scorer: it reads a JSONL file of real
recorded predictions (`{"p": <predicted probability>, "correct": 0|1}`) and
reports accuracy, Brier score, ECE, and a reliability diagram. It invents
nothing; with no input file it reports nothing. Record the predictions during
real runs (for example, while calling /v1/calibrate against labeled data),
then score them here.

The repository does not currently implement the LLM-as-judge or raw-logprob baselines, p95 benchmark collection, or file export for PNG/SVG reliability diagrams. Those are acceptance targets for a fuller evaluation pass, not claims about the current script.

## Example data

There is no bundled labeled example set. The old fixture (four incident-style
choice cases with hardcoded probabilities) was removed because it measured
nothing real. Bring at least 50 fresh labeled examples per question type when
you run /v1/calibrate; the fitted temperature is only as honest as its data.

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

No measured calibration proof exists yet. The machinery is in place and
unit-tested: /v1/calibrate fits a temperature by minimizing NLL on labeled
examples, persists it, and reports ECE before/after with a reliability
diagram. Run it against a live provider on fresh labeled data, score the
recorded predictions with eval/evaluate.py, and only then claim numbers.
PNG/SVG export is not implemented.

## Definitions

- ECE: expected calibration error
- p95 latency: 95th percentile latency for one request
- LLM-as-judge baseline: same task judged by a model with the same evidence set
- Raw logprobs baseline: unscaled log-probabilities from the decision engine
