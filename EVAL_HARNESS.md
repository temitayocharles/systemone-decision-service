# Evaluation Harness

The evaluation tooling measures decision quality, calibration, reliability, and runtime performance from labelled workloads.

## Live benchmark runner

`eval/benchmark_runtime.py` executes a labelled JSONL dataset against a configured provider instance.

It records:

- sample count
- exact-label accuracy
- expected calibration error
- p95 latency
- failure rate
- optional known cost per 1,000 decisions
- run ID
- dataset SHA-256
- UTC creation timestamp
- dataset path

Example:

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

The fixture under `eval/data/` verifies the pipeline shape. Replace or supplement it with representative labelled workloads for real comparisons.

## Offline evaluator

`eval/evaluate.py` scores recorded binary prediction rows.

Input JSONL:

```json
{"p": 0.82, "correct": 1}
```

The evaluator reports:

- accuracy
- Brier score
- expected calibration error
- reliability diagram data

## Calibration fitting

The canonical runtime endpoint is:

```text
POST /v2/calibration/fit
```

Binary/null observations:

```json
{
  "probability": 0.82,
  "label": 1
}
```

Choice/score observations:

```json
{
  "probabilities": [0.2, 0.7, 0.1],
  "label_index": 1
}
```

Raw logits can be supplied instead of probabilities.

Calibration profiles are persisted by provider instance, model, question type, and version. Compatible running provider engines reload the new profile after fitting.

## Measurement principles

For meaningful comparisons:

- use the same labelled dataset across competing provider/model combinations
- use comparable runtime conditions
- report sample count and dataset hash
- keep materially different task distributions separate
- record cost only when known
- rerun after model, serving configuration, or calibration changes
- distinguish fixture validation from production evidence
