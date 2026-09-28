# Empirical Selection

System One selects among eligible provider/model combinations using measured benchmark evidence.

## Benchmark identity

Each record is keyed by:

```text
provider-instance + model + task-type
```

A benchmark record contains:

- sample count
- accuracy
- expected calibration error
- p95 latency
- failure rate
- optional known cost per 1,000 decisions

## Dataset format

Benchmark workloads use JSONL.

Example:

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

Use labelled workloads representative of the target task.

## Running a benchmark

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

Repeat for each configured provider/model combination intended to compete for that task.

If reliable pricing is known, pass `--cost-per-1000`. Otherwise leave cost unset.

## Selection policy

```json
{
  "policy": {
    "task_type": "routing",
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "max_cost_per_1000": 1.0,
    "min_accuracy": 0.90,
    "required_capabilities": ["token_logprobs"]
  }
}
```

Candidates must satisfy all configured constraints before scoring.

## Scoring

Eligible candidates are compared using:

- accuracy
- calibration quality
- latency
- cost
- reliability
- benchmark sample support

The selector therefore separates two questions:

1. **Can this provider/model satisfy the request?**
2. **Among eligible candidates, which has the strongest measured performance for the task?**

## Benchmark storage

The benchmark store is configured with:

```env
SYSTEMONE_BENCHMARK_FILE=/path/to/benchmarks.json
```

If unset, the runtime uses its default data path.

## Runtime use

Applications may route explicitly or omit the provider and pass a selection policy. The runtime then resolves the best eligible benchmarked candidate and invokes the corresponding configured provider instance.
