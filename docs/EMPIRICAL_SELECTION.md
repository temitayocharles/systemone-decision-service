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
- run ID
- dataset SHA-256
- creation timestamp
- dataset path

The provenance fields are mandatory when a benchmark is persisted.

## Dataset format

Benchmark workloads use JSONL.

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

The repository includes `eval/data/routing.jsonl` as a small pipeline fixture. Use representative labelled workloads for model comparisons and performance claims.

## Running a benchmark

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

The harness computes the dataset SHA-256 and run metadata automatically.

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

The selector separates eligibility from empirical ranking.

## Benchmark storage

```env
SYSTEMONE_BENCHMARK_FILE=/path/to/benchmarks.json
```

If unset, the runtime uses its default data path.

## Runtime use

Applications may route explicitly or omit the provider and pass a selection policy. The runtime resolves the best eligible benchmarked candidate and invokes the corresponding configured provider instance.
