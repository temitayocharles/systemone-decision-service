# Empirical model selection

The runtime does not assume any provider instance or model is best.

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

The provider argument is the **instance ID configured in the deployment environment**.

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-name-from-that-deployment \
  --task-type routing
```

Repeat for every configured instance/model that should compete for the task.

If actual provider pricing is known for the benchmark period, pass
`--cost-per-1000`. If it is unknown, omit it rather than estimating it.

## Select

Applications can omit `provider` and pass a policy:

```json
{
  "state": "...",
  "questions": {
    "route": {
      "type": "choice",
      "instructions": "...",
      "criteria": {
        "a": "...",
        "b": "..."
      }
    }
  },
  "policy": {
    "task_type": "routing",
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "min_accuracy": 0.90
  }
}
```

Only measured instance/model records satisfying all constraints are eligible.

## What is measured

The benchmark harness records:

- sample count
- exact-label accuracy
- expected calibration error
- p95 latency
- failure rate
- optional known cost per 1,000 decisions

The selection score balances accuracy, calibration, latency, cost, reliability,
and sample support.

## Provider replacement

Applications call System One rather than a provider directly. The deployment
may change an instance's endpoint/model through environment configuration, or
benchmark a different instance, without changing the application contract.

## Ensemble

Callers may explicitly combine configured instances:

```json
{
  "ensemble": ["primary", "secondary"]
}
```

The labels are deployment-defined. The runtime combines compatible probability
outputs and makes no assumption about the vendor or model behind either label.
