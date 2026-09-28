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
- batch decisions with per-item error isolation
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

```bash
cp .env.example .env
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

Instance labels are arbitrary. Provider/model changes are deployment configuration changes.

See [Decision Runtime](docs/DECISION_RUNTIME.md).

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

A caller can select one provider instance, request an ensemble, or supply a routing policy for empirical selection.

## Capability-aware routing

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

Policies can require or forbid capabilities and constrain typed attributes before empirical scoring.

See [Capability Routing](docs/CAPABILITY_ROUTING.md).

## Empirical selection

Benchmark records are keyed by:

```text
provider-instance + model + task-type
```

Every persisted benchmark includes provenance:

- run ID
- dataset SHA-256
- creation timestamp
- dataset path
- sample count
- accuracy
- ECE
- p95 latency
- failure rate
- known cost when supplied

Use:

```bash
PYTHONPATH=. python eval/benchmark_runtime.py \
  --dataset eval/data/routing.jsonl \
  --provider primary \
  --model model-a \
  --task-type routing
```

The bundled `eval/data/routing.jsonl` is a small pipeline fixture, not a performance claim.

See [Empirical Selection](docs/EMPIRICAL_SELECTION.md).

## Calibration

The canonical fitting endpoint is:

```text
POST /v2/calibration/fit
```

Profiles are keyed by:

```text
provider-instance:model:question-type:version
```

For binary/null calibration, observations contain `probability` and `label`. For choice/score calibration, observations contain `label_index` plus either raw `logits` or a probability vector.

A newly fitted profile is persisted and reloaded into active compatible provider engines without requiring a service restart.

## Evaluation

The repository includes:

- `eval/benchmark_runtime.py` for live provider/model benchmarking
- `eval/evaluate.py` for offline scoring
- `eval/data/` for pipeline fixtures
- `EVAL_HARNESS.md` for measurement contracts

Performance claims require executed labelled workloads.

## RAG integration

```text
documents -> retrieval -> evidence -> System One -> typed decision
```

The included demo uses the v2 Decision Runtime contract.

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

## License

See [LICENSE](LICENSE).
