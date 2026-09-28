# Empirical model selection

The runtime does not assume Jev, an OpenAI-compatible model, or any future provider is best.

Selection is based on recorded benchmark evidence for a task type.

## Dataset

Use JSONL. Every row contains:

```json
{
  "state": "input state",
  "question": {
    "type": "choice",
    "instructions": "Which route?",
    "criteria": {
      "a": "route A",
      "b": "route B"
    }
  },
  "label": "a"
}
```

Use real recorded and labelled examples. Do not manufacture benchmark numbers.

## Run

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider jev \
  --model jev-latest \
  --task-type routing
```

Repeat for every provider/model that should compete for the task.

If actual provider pricing is known for the benchmark period, pass `--cost-per-1000`. If it is unknown, omit it rather than estimating it.

## Select

Applications can omit `provider` and pass a policy:

```json
{
  "state": "...",
  "questions": {"route": {"type": "choice", "instructions": "...", "criteria": {"a": "...", "b": "..."}}},
  "policy": {
    "task_type": "routing",
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "min_accuracy": 0.90
  }
}
```

Only models with measured records satisfying all constraints are eligible.

## What is measured

The benchmark harness records:

- sample count
- exact-label accuracy
- expected calibration error
- p95 latency
- failure rate
- optional known cost per 1,000 decisions

The selection score then balances accuracy, calibration, latency, cost, reliability, and sample support.

## Provider replacement

Applications call System One, not Jev or a specific general model. Re-benchmarking can therefore change the selected provider without changing application contracts.

## Ensemble

For workloads where provider diversity is useful, callers may explicitly request:

```json
"ensemble": ["jev", "openai_compatible"]
```

The runtime calls both and combines compatible probability outputs. This is opt-in because it increases latency and provider cost.
