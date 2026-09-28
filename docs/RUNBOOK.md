# System One Runbook

This runbook defines how to operate System One as one decision runtime.

System One exposes a single application-facing decision service. Applications submit state and typed questions. The runtime resolves an eligible configured inference instance, applies the relevant calibration profile, executes the decision, records telemetry, and returns a normalized result.

```text
Applications
    |
    v
System One Decision Runtime
    |
    +-- provider-instance registry
    +-- capability matching
    +-- health eligibility
    +-- empirical selection
    +-- calibration
    +-- telemetry
    |
    v
Compatible inference endpoints
```

## 1. Runtime contract

The operational API is:

- `POST /v2/decide` — execute one decision request
- `POST /v2/batch` — execute multiple isolated decision requests
- `GET /v2/providers` — inspect configured inference instances
- `GET /v2/metrics` — inspect runtime telemetry summary
- `GET /v2/benchmarks` — inspect empirical benchmark records
- `PUT /v2/benchmarks` — persist a benchmark record with provenance
- `POST /v2/calibration/fit` — fit and activate a calibration profile
- `GET /v1/health` — runtime health endpoint

The service listens on port `8002` by default.

## 2. Configure inference instances

System One does not require a fixed provider or model. Inference instances are defined at deployment time.

Example:

```env
SYSTEMONE_PROVIDER_IDS=primary,secondary
SYSTEMONE_DEFAULT_PROVIDER=primary

SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://inference.example/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-a
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=
SYSTEMONE_PROVIDER_PRIMARY_TIMEOUT_S=60
SYSTEMONE_PROVIDER_PRIMARY_MAX_PARALLEL=8

SYSTEMONE_PROVIDER_SECONDARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_SECONDARY_BASE_URL=http://model-server:8000/v1
SYSTEMONE_PROVIDER_SECONDARY_MODEL=model-b
SYSTEMONE_PROVIDER_SECONDARY_API_KEY=
SYSTEMONE_PROVIDER_SECONDARY_TIMEOUT_S=60
SYSTEMONE_PROVIDER_SECONDARY_MAX_PARALLEL=8
```

Instance IDs such as `primary` and `secondary` are deployment labels. The model, endpoint, authentication, and driver behind each label can be changed without changing application code.

For an instance ID such as `local-box`, the corresponding environment prefix is:

```text
SYSTEMONE_PROVIDER_LOCAL_BOX_*
```

## 3. Declare capabilities and attributes

Each inference instance can advertise capabilities and typed attributes.

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

The capability set is open-ended. The runtime also derives protocol capabilities from the configured driver.

For `openai_compatible`, baseline capabilities include:

- `chat_completions`
- `token_logprobs`
- `probabilistic_decisions`

For `systemone_http`, baseline capabilities include:

- `native_systemone`
- `probabilistic_decisions`

## 4. Start System One

For a local Docker deployment:

```bash
cp .env.example .env
docker compose up -d --build
```

For Kubernetes, supply the same `SYSTEMONE_*` configuration through the deployment environment and secret mechanism.

The runtime itself remains the same in either deployment model.

## 5. Verify the running service

Check runtime health:

```bash
curl -fsS http://localhost:8002/v1/health
```

Inspect the resolved inference registry:

```bash
curl -fsS http://localhost:8002/v2/providers
```

Confirm that each expected instance reports:

- instance ID
- driver
- endpoint
- configured model
- authentication state
- concurrency setting
- capabilities
- attributes

## 6. Certify a configured runtime

Use the provider-neutral certification tool:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002
```

To certify a specific instance and model:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002 \
  --provider primary \
  --model model-a
```

Certification verifies the live System One contract against the configured inference endpoint, including typed decision output, probability bounds, route identity, and usage metadata when available.

Keep certification output with the deployment evidence for the corresponding model and serving configuration.

## 7. Execute decisions

A normal request submits state and one or more typed questions:

```json
{
  "state": {
    "service": "payments",
    "status": "degraded"
  },
  "questions": {
    "route": {
      "type": "choice",
      "instructions": "Select the best response path.",
      "criteria": {
        "investigate": "Investigate first",
        "rollback": "Rollback",
        "observe": "Continue observing"
      }
    }
  }
}
```

Submit it to:

```text
POST /v2/decide
```

System One supports three routing modes.

### Default routing

Omit `provider`, `policy`, and `ensemble`. The runtime uses the configured default instance.

### Explicit routing

Specify one configured provider instance:

```json
{
  "provider": "primary"
}
```

A model may also be supplied when the configured driver supports model selection.

### Empirical routing

Supply a routing policy instead of a provider:

```json
{
  "policy": {
    "task_type": "routing",
    "required_capabilities": ["token_logprobs"],
    "attribute_equals": {
      "local": true
    },
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "min_accuracy": 0.90
  }
}
```

The runtime filters candidates by task, capabilities, attributes, observed health, and empirical thresholds before selecting among the eligible benchmarked models.

### Ensemble routing

Specify the configured instances to combine:

```json
{
  "ensemble": ["primary", "secondary"]
}
```

Compatible outputs are normalized into one decision result.

The routing modes are mutually exclusive.

## 8. Run batch decisions

Submit up to 100 requests through:

```text
POST /v2/batch
```

Each result is isolated and returned with its input index.

Successful item:

```json
{
  "index": 0,
  "ok": true,
  "result": {}
}
```

Unsuccessful item:

```json
{
  "index": 1,
  "ok": false,
  "error": {
    "type": "RuntimeError",
    "detail": "..."
  }
}
```

One item does not invalidate the successful results of other batch items.

## 9. Benchmark an inference instance

Use a labelled workload representative of the task.

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

For production evidence, use a task-specific labelled dataset rather than the bundled pipeline fixture.

Each persisted benchmark contains:

- provider instance
- model
- task type
- sample count
- accuracy
- expected calibration error
- p95 latency
- failure rate
- known cost when supplied
- run ID
- dataset SHA-256
- creation timestamp
- dataset path

Inspect benchmark records:

```bash
curl -fsS http://localhost:8002/v2/benchmarks
```

Benchmark identity is:

```text
provider-instance + model + task-type
```

## 10. Fit calibration

Calibration is fitted against labelled observations for the exact provider instance, model, and question type being served.

### Null / binary calibration

```json
{
  "provider": "primary",
  "model": "model-a",
  "question_type": "null",
  "examples": [
    {
      "probability": 0.82,
      "label": 1
    }
  ]
}
```

### Choice / score calibration

```json
{
  "provider": "primary",
  "model": "model-a",
  "question_type": "choice",
  "examples": [
    {
      "probabilities": [0.10, 0.80, 0.10],
      "label_index": 1
    }
  ]
}
```

Raw logits may be supplied instead of probability vectors.

At least 20 labelled observations are required.

Submit calibration data to:

```text
POST /v2/calibration/fit
```

Profiles are persisted by:

```text
provider-instance:model:question-type:version
```

Compatible active engines reload the fitted profile without requiring a runtime restart.

## 11. Validate empirical routing

Once benchmark records exist for candidate instances, send a decision request with a policy and no explicit provider.

Example:

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

Verify that the returned `route.provider` and `route.model` correspond to an eligible persisted benchmark record.

## 12. Observe the runtime

Inspect telemetry:

```bash
curl -fsS "http://localhost:8002/v2/metrics?limit=1000"
```

Runtime telemetry records:

- request ID
- provider instance
- model
- status
- latency
- token usage
- question types

The latest observed result for each configured instance contributes to health-aware empirical routing.

## 13. Scale System One

The request execution layer is stateless. Multiple runtime replicas can sit behind one service endpoint.

```text
                    Application
                         |
                         v
                   Runtime Service
                         |
              +----------+----------+
              |          |          |
              v          v          v
          Runtime 1  Runtime 2  Runtime 3
              |          |          |
              +----------+----------+
                         |
                         v
                 Inference endpoints
```

For clustered deployments, use shared or durable storage for:

- benchmark records
- calibration profiles
- telemetry

Provider endpoints may be external, local, or cluster-internal.

## 14. RAG integration

RAG is an optional evidence source, not a separate decision architecture.

```text
documents
   |
   v
retrieval
   |
   v
evidence
   |
   v
System One
   |
   v
typed decision
```

With the included RAG service running:

```bash
PYTHONPATH=. python demo/compare.py \
  --question "My service is unhealthy; what evidence is relevant?" \
  --collection engineering \
  --top-k 8 \
  --verbose
```

The demo sends retrieved evidence through the same System One v2 decision contract used by other applications.

## 15. Release certification

A System One deployment is ready for use when:

- the configured provider registry matches the deployment
- runtime health succeeds
- live certification succeeds for each intended inference instance
- the test suite is green
- representative labelled workloads have been benchmarked where empirical routing is used
- benchmark provenance is recorded
- calibration profiles are fitted where required
- empirical routing policies resolve an eligible model
- runtime telemetry is writable and observable

The operational unit is always **System One**. Models and inference endpoints are interchangeable configured resources behind that runtime.
