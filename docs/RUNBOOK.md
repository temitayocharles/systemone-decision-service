# System One Operational Runbook

This runbook covers deployment, provider configuration, live certification, calibration, benchmarking, routing validation, and troubleshooting for the System One Decision Runtime.

## 1. Configure provider instances

Provider instances are deployment-defined.

Example:

```env
SYSTEMONE_PROVIDER_IDS=primary
SYSTEMONE_DEFAULT_PROVIDER=primary

SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://inference.example/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-a
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=
SYSTEMONE_PROVIDER_PRIMARY_TIMEOUT_S=60
SYSTEMONE_PROVIDER_PRIMARY_MAX_PARALLEL=8
```

For a local endpoint, use the local service URL and leave `API_KEY` empty when authentication is not required.

Capabilities and attributes can be supplied independently:

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768}
```

## 2. Start the runtime

Docker Compose:

```bash
cp .env.example .env
docker compose up -d --build
```

Kubernetes deployments should provide the same `SYSTEMONE_PROVIDER_*` settings through the deployment environment and secrets mechanism.

## 3. Verify service health

```bash
curl -fsS http://localhost:8002/v1/health
curl -fsS http://localhost:8002/v2/providers
```

Confirm that:

- the runtime health endpoint returns successfully
- the expected provider instance appears
- the configured model is correct
- the capability set matches the deployment
- authentication metadata reflects whether a key is configured

## 4. Run live provider certification

Use the bundled certification script:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002
```

To target a specific instance/model:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002 \
  --provider primary \
  --model model-a
```

A passing certification verifies that the live runtime:

- reaches the configured inference endpoint
- receives typed answers
- returns a two-way choice distribution summing to 1
- returns bounded confidence values
- returns a bounded binary/null probability
- identifies the actual route and model
- returns non-negative usage when usage is reported

Retain the JSON output with the deployment evidence when certifying a model endpoint.

## 5. Run the test suite

```bash
python -m pytest -q
```

The live-provider smoke test may be skipped when no live provider credentials are configured. Unit and contract tests do not substitute for live model certification.

## 6. Benchmark a provider/model

The repository includes a small routing fixture for pipeline validation:

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

For performance evidence, replace or supplement the fixture with representative labelled workload data.

Each persisted benchmark includes:

- run ID
- dataset SHA-256
- UTC creation timestamp
- dataset path
- sample count
- accuracy
- ECE
- p95 latency
- failure rate
- known cost when supplied

Inspect records:

```bash
curl -fsS http://localhost:8002/v2/benchmarks
```

## 7. Fit calibration

### Null/binary observations

```json
{
  "provider": "primary",
  "model": "model-a",
  "question_type": "null",
  "examples": [
    {"probability": 0.82, "label": 1}
  ]
}
```

At least 20 labelled examples are required.

### Choice/score observations

Use `label_index` plus either `logits` or `probabilities`:

```json
{
  "provider": "primary",
  "model": "model-a",
  "question_type": "choice",
  "examples": [
    {
      "probabilities": [0.1, 0.8, 0.1],
      "label_index": 1
    }
  ]
}
```

Submit to:

```text
POST /v2/calibration/fit
```

The profile is persisted and active compatible provider engines reload it without a runtime restart.

## 8. Validate empirical routing

After benchmark records exist for competing provider/model combinations, submit a policy without an explicit provider:

```json
{
  "state": "task state",
  "questions": {
    "route": {
      "type": "choice",
      "instructions": "Choose the route.",
      "criteria": {
        "a": "Route A",
        "b": "Route B"
      }
    }
  },
  "policy": {
    "task_type": "routing",
    "required_capabilities": ["token_logprobs"],
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "min_accuracy": 0.90
  }
}
```

Verify the returned `route.provider` and `route.model` correspond to an eligible benchmark record.

## 9. Batch validation

`POST /v2/batch` returns one result per input item.

Each item contains:

- `ok: true` plus `result`, or
- `ok: false` plus a typed error

A failing item does not invalidate successful siblings.

## 10. Runtime telemetry

```bash
curl -fsS "http://localhost:8002/v2/metrics?limit=1000"
```

Telemetry includes request status, latency, token usage, provider instance, model, and question types.

The latest telemetry event per provider instance also contributes to health-aware empirical routing.

## 11. RAG integration demo

With the RAG and Decision Runtime services running:

```bash
PYTHONPATH=. python demo/compare.py \
  --question "My service is unhealthy; what evidence is relevant?" \
  --collection engineering \
  --top-k 8 \
  --verbose
```

The demo retrieves evidence and uses the v2 Decision Runtime to score evidence relevance.

## 12. Troubleshooting

### 502 from `/v2/decide`

Check:

1. provider instance exists in `/v2/providers`
2. base URL is reachable from the runtime container/pod
3. configured model exists at the endpoint
4. authentication is valid when required
5. the endpoint returns token logprobs for `openai_compatible`
6. routing policy has at least one eligible benchmark record

### No empirically qualified model

Confirm:

- benchmark records exist for the requested `task_type`
- capability requirements match configured instances
- the latest observed provider health is not failed
- ECE, latency, accuracy, and cost thresholds are achievable by at least one record

### Calibration appears unchanged

Confirm:

- provider instance ID and model exactly match the runtime route
- question type matches the fitted profile
- the calibration fit endpoint returned the expected profile
- the next request is using the same provider/model identity

### Local model endpoint cannot be reached

Check container/cluster DNS and network routing. A loopback address inside the runtime container points to the runtime container itself; use the model service hostname or an appropriate host gateway address.

## 13. Release checklist

Before treating a provider/model deployment as certified:

- CI test suite is green
- live certification script passes
- provider/model identity is recorded
- labelled benchmark dataset is identified by hash
- benchmark results are persisted
- calibration profile is fitted when required
- empirical routing constraints are tested
- telemetry is writable
- no temporary Git branches remain
