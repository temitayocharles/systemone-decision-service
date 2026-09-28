# System One Decision Runtime

System One is a provider-independent runtime for typed probabilistic decisions.

Applications submit state and typed questions through one stable API. The runtime resolves compatible provider instances from deployment configuration, filters them by capabilities and health, applies empirical performance constraints, and returns normalized decisions.

## Core capabilities

- typed `choice`, `score`, and `null/noul` decisions
- configurable provider instances
- OpenAI-compatible logprob inference
- native System One HTTP integration
- custom Python drivers
- capability-aware routing
- empirical model selection
- provider/model calibration profiles
- batch decisions
- provider ensembles
- runtime telemetry and health-aware eligibility
- benchmark and evaluation tooling
- optional RAG integration

## Architecture

```text
Applications
    |
    v
System One Decision Runtime
    |
    +-- capability filtering
    +-- health eligibility
    +-- empirical performance constraints
    +-- calibrated model selection
    |
    v
Provider instances
    |
    +-- OpenAI-compatible endpoints
    +-- native System One endpoints
    +-- custom drivers
```

Applications depend on the System One contract rather than a specific model host or inference vendor.

## Quick start

Copy the environment template:

```bash
cp .env.example .env
```

Configure one or more provider instances in `.env`, then start the stack:

```bash
docker compose up -d --build
```

Runtime health:

```bash
curl http://localhost:8002/v1/health
```

Configured provider instances:

```bash
curl http://localhost:8002/v2/providers
```

## Provider configuration

Provider instances are deployment-defined.

```env
SYSTEMONE_PROVIDER_IDS=primary,secondary
SYSTEMONE_DEFAULT_PROVIDER=primary

SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://inference.example/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-a
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=

SYSTEMONE_PROVIDER_SECONDARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_SECONDARY_BASE_URL=http://model-server:8000/v1
SYSTEMONE_PROVIDER_SECONDARY_MODEL=model-b
SYSTEMONE_PROVIDER_SECONDARY_API_KEY=
```

Instance labels are arbitrary. Provider/model changes are configuration changes rather than application-code changes.

See [Decision Runtime](docs/DECISION_RUNTIME.md) for the full deployment contract.

## Decision API

`POST /v2/decide`

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

A caller may explicitly select a provider instance, request an ensemble, or provide a routing policy and allow the runtime to choose empirically.

## Capability-aware routing

Each provider instance can declare capabilities and typed attributes:

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

Policies can require or forbid capabilities and constrain attributes before empirical model scoring occurs.

See [Capability Routing](docs/CAPABILITY_ROUTING.md).

## Empirical selection

Benchmarks are stored by:

```text
provider-instance + model + task-type
```

The selector can constrain:

- accuracy
- expected calibration error
- p95 latency
- failure rate
- known cost
- required/forbidden capabilities
- typed attributes
- observed health

Only measured candidates satisfying the policy are eligible.

See [Empirical Selection](docs/EMPIRICAL_SELECTION.md).

## Calibration

Calibration profiles are versioned independently for each provider instance, model, and question type:

```text
provider-instance:model:question-type:version
```

This allows the same model served from different environments to be calibrated independently.

## Evaluation

The repository includes:

- `eval/benchmark_runtime.py` for live provider/model benchmarking
- `eval/evaluate.py` for offline scoring
- `EVAL_HARNESS.md` for dataset and measurement contracts

Benchmarks are populated from labelled workloads. The repository does not ship fabricated performance results.

## RAG integration

The included RAG service demonstrates one integration path:

```text
documents -> retrieval -> evidence -> System One -> typed decision
```

RAG is optional. The Decision Runtime can consume state from any application or evidence source.

## Service ports

- Decision Runtime: `:8002`
- RAG example service: `:8001`
- Chroma: `:8000`
- Ollama example service: `:11434`

## Repository structure

```text
decide/     decision runtime, providers, calibration, routing
eval/       benchmark and evaluation tooling
rag/        optional RAG example service
corpora/    example retrieval corpora
demo/       integration examples
docs/       runtime architecture and routing documentation
tests/      unit and contract tests
openapi.yaml
```

## Documentation

- [Decision Runtime](docs/DECISION_RUNTIME.md)
- [Capability Routing](docs/CAPABILITY_ROUTING.md)
- [Empirical Selection](docs/EMPIRICAL_SELECTION.md)
- [Evaluation Harness](EVAL_HARNESS.md)
- [OpenAPI](openapi.yaml)
