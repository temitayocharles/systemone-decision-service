# System One Runbook

System One operates as one decision runtime.

Applications submit state and typed questions. The runtime resolves an eligible configured inference instance, applies the relevant calibration profile, executes the decision, records telemetry, and returns a normalized result.

## API

- `GET /health`
- `POST /v2/decide`
- `POST /v2/batch`
- `GET /v2/providers`
- `GET /v2/metrics`
- `GET /v2/benchmarks`
- `PUT /v2/benchmarks`
- `POST /v2/calibration/fit`

The service listens on port `8002` by default.

## Configure inference instances

```env
SYSTEMONE_PROVIDER_IDS=primary,secondary
SYSTEMONE_DEFAULT_PROVIDER=primary

SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://inference.example/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-a
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=
SYSTEMONE_PROVIDER_PRIMARY_TIMEOUT_S=60
SYSTEMONE_PROVIDER_PRIMARY_MAX_PARALLEL=8
```

Instance IDs are deployment labels. Endpoints, models, credentials, capabilities, and attributes can change without changing application code.

Capabilities and attributes:

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

## Start

Local Docker deployment:

```bash
cp .env.example .env
docker compose up -d --build
```

Kubernetes supplies the same `SYSTEMONE_*` configuration through the deployment environment and secret mechanism.

## Verify

```bash
curl -fsS http://localhost:8002/health
curl -fsS http://localhost:8002/v2/providers
```

Confirm the expected inference instances, models, capabilities, attributes, and authentication state.

## Certify

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002
```

To target a specific configured instance/model:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002 \
  --provider primary \
  --model model-a
```

Certification verifies the live health, provider registry, decision route, typed answers, probability bounds, and usage metadata.

## Decide

Send state and typed questions to `POST /v2/decide`.

Routing modes are mutually exclusive:

- default routing uses the configured default instance
- explicit routing names one provider instance
- empirical routing supplies a policy
- ensemble routing supplies a list of configured instances

Empirical policies can constrain task type, capabilities, typed attributes, observed health, ECE, p95 latency, accuracy, failure rate, and known cost.

## Batch

`POST /v2/batch` accepts up to 100 requests. Each item returns independently with its input index and either a result or typed error.

## Benchmark

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

Use representative labelled workloads for real performance evidence.

Persisted benchmarks include provider instance, model, task type, sample count, accuracy, ECE, p95 latency, failure rate, optional known cost, run ID, dataset SHA-256, creation timestamp, and dataset path.

## Calibrate

Fit labelled observations through `POST /v2/calibration/fit`.

Profiles are stored by:

```text
provider-instance:model:question-type:version
```

At least 20 labelled observations are required. Compatible active engines reload the fitted profile without a restart.

## Observe

```bash
curl -fsS "http://localhost:8002/v2/metrics?limit=1000"
```

Telemetry records request ID, provider instance, model, status, latency, token usage, and question types. Latest observed provider status contributes to health-aware empirical routing.

## Scale

The request execution layer is stateless and can be horizontally replicated behind one service endpoint. Use durable or shared storage for benchmark records, calibration profiles, and telemetry when multiple replicas operate together.

Inference endpoints may be external, local, or cluster-internal.

## RAG

RAG is an optional evidence source:

```text
documents -> retrieval -> evidence -> System One -> typed decision
```

The included demo sends retrieved evidence through the same `/v2/decide` contract.

## Release certification

A deployment is ready when the configured registry matches the intended inference resources, `/health` succeeds, live certification passes, CI is green, empirical routing has representative benchmark evidence where used, required calibration profiles are fitted, and telemetry is writable.

The operational unit is System One. Models and inference endpoints are interchangeable configured resources behind the runtime.
