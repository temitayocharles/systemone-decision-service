# Evaluation Harness

The evaluation tooling measures decision quality and calibration from labelled workloads.

## Benchmark runtime

`eval/benchmark_runtime.py` executes a labelled dataset against a configured provider instance and records:

- sample count
- exact-label accuracy
- expected calibration error
- p95 latency
- failure rate
- optional known cost per 1,000 decisions

Example:

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

The resulting benchmark record is persisted in the runtime benchmark store.

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

## Labelled decision datasets

Runtime benchmark rows contain:

```json
{
  "state": "input state",
  "question": {
    "type": "choice",
    "instructions": "Select the correct option.",
    "criteria": {
      "a": "Option A",
      "b": "Option B"
    }
  },
  "label": "a"
}
```

The label format follows the question type:

- choice: option key
- score: numeric score
- null/noul: expected proposition outcome

Datasets should represent the workload and task distribution used in production.

## Calibration workflow

Calibration is fitted from labelled examples and persisted by provider instance, model, question type, and profile version.

Evaluation should compare calibration before and after fitting and retain:

- ECE
- accuracy
- sample count
- reliability diagram data

## Measurement principles

Performance numbers are recorded only from executed workloads.

For meaningful comparisons:

- use the same labelled dataset across competing provider/model combinations
- use comparable runtime conditions
- report the benchmark sample count
- keep task types separate where their distributions differ
- record cost only when the source value is known
- rerun benchmarks when the model, serving configuration, or calibration profile changes
