# System One Runbook

System One operates as one decision runtime.

Applications submit state and typed questions. The runtime resolves an eligible configured inference instance, applies the relevant calibration profile, executes the decision, records telemetry, and returns a normalized result.

## High-level stack

System One is one user-facing decision system composed of a small number of cooperating services.

```text
                         Browser / Application
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
           System One UI                 Direct API clients
           demo/ui :8080                       |
                    |                           |
          same-origin proxy                    |
                    |                           |
          +---------+---------+                 |
          |                   |                 |
          v                   v                 |
   RAG service :8001   Decision Runtime :8002 <-+
          |                   |
          |                   +--> provider registry
          |                   +--> capability + health filtering
          |                   +--> calibration profiles
          |                   +--> empirical benchmarks
          |                   +--> telemetry
          |                   |
          |                   +--> local inference (Ollama)
          |                   +--> hosted / cluster inference
          |
          +--> embedding model
          +--> Chroma vector store
          +--> generation model

Knowledge documents
      |
      v
chunk -> embed -> Chroma -> retrieve evidence
                              |
                              v
                    System One decision runtime
                              |
                              v
                 choice / null / score result
```

### What each layer does

**System One UI — `demo/ui`, port `8080`**

The browser-first workspace for non-technical users. It lets users index the built-in knowledge collections, ask questions, inspect retrieved evidence, run typed decisions, batch-triage items, and see service/provider health without writing API commands.

The small `serve_demo.py` process is only a same-origin proxy:
- `/health` and `/v2/*` go to the Decision Runtime on port `8002`
- `/rag/*` goes to the RAG service on port `8001`

**Decision Runtime — `decide/`, port `8002`**

This is the core System One service. It accepts state plus typed questions and returns normalized probabilistic decisions.

It owns:
- provider-instance resolution
- explicit, empirical, and ensemble routing
- capability and health filtering
- calibration-profile loading
- benchmark-aware model selection
- telemetry
- batch execution

Applications depend on this contract rather than on a specific model host.

**RAG service — `rag/`, port `8001`**

An optional evidence source. It ingests the Engineering and Business corpora, creates embeddings, stores them in Chroma, retrieves relevant chunks, and can generate a normal RAG answer.

Retrieved evidence can then be supplied to System One for a typed decision.

**Chroma — port `8000`**

The vector store used by the RAG service. It stores embedded document chunks and returns the nearest evidence for a query.

The Python client and server image are pinned to the same release.

**Ollama — port `11434`**

The bundled local inference host used by the default local stack.

The Compose stack bootstraps:
- `qwen2.5:3b` for generation and local decision inference
- `nomic-embed-text` for embeddings

The runtime is not built around Ollama. Any compatible configured inference endpoint can sit behind System One.

**Provider instances**

A provider instance is a deployment-defined inference target. It can be:
- local
- cluster-internal
- hosted
- any compatible future backend

Each instance supplies configuration such as driver, endpoint, model, credentials, capabilities, and typed attributes.

**Operational data**

System One persists three kinds of runtime evidence:
- calibration profiles
- benchmark records
- telemetry

These support calibrated probabilities, empirical provider/model selection, health-aware routing, and operational inspection.

### Request flow

A typical knowledge-assisted decision follows this path:

```text
1. User asks a question in the UI
2. UI calls the RAG service
3. RAG embeds the question
4. Chroma returns relevant evidence
5. RAG may generate a normal answer
6. UI sends state + evidence to System One
7. Runtime resolves an eligible inference instance
8. Model returns probabilistic typed outputs
9. Calibration is applied where available
10. System One returns a normalized choice / null / score result
11. Telemetry records the execution
```

RAG is optional. Applications can call System One directly whenever they already have the state needed for a decision.

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

For the browser workspace:

```bash
cd demo/ui
python3 serve_demo.py
```

Then open:

```text
http://localhost:8080
```

## Verify

```bash
curl -fsS http://localhost:8002/health
curl -fsS http://localhost:8002/v2/providers
```

Confirm the expected inference instances, models, capabilities, attributes, and authentication state.

The UI also surfaces Decision Runtime and RAG health for normal browser-based use.

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

The browser workspace exposes indexing, retrieval, RAG query, evidence review, and typed decisions without requiring users to work directly with API commands.

## Release certification

A deployment is ready when the configured registry matches the intended inference resources, `/health` succeeds, live certification passes, CI is green, empirical routing has representative benchmark evidence where used, required calibration profiles are fitted, and telemetry is writable.

The operational unit is System One. Models and inference endpoints are interchangeable configured resources behind the runtime.
