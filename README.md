# System One Decision Runtime

System One is a provider-independent runtime for typed probabilistic decisions.

Applications submit state and typed questions through one stable API. The runtime resolves compatible inference instances from deployment configuration, filters them by capabilities and health, applies empirical performance constraints and calibration, and returns normalized decisions.

## Core API

- `GET /health`
- `POST /v2/decide`
- `POST /v2/batch`
- `GET /v2/providers`
- `GET /v2/metrics`
- `GET /v2/benchmarks`
- `PUT /v2/benchmarks`
- `POST /v2/calibration/fit`

System One exposes one runtime API generation for decisions, routing, benchmarking, and calibration.

## Architecture

```text
Applications
    |
    v
System One Decision Runtime
    |
    +-- capability matching
    +-- health eligibility
    +-- empirical model selection
    +-- calibration
    +-- telemetry
    |
    v
Compatible inference endpoints
```

Inference instances are deployment-defined. Application code does not depend on a provider brand or model name.

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8002/health
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

Instance labels are arbitrary deployment identifiers.

## Decision request

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

Send to `POST /v2/decide`.

A request can use the configured default instance, explicitly name one instance, request an ensemble, or provide an empirical routing policy.

## Capability-aware empirical routing

Instances can declare open-ended capabilities and typed attributes:

```env
SYSTEMONE_PROVIDER_PRIMARY_CAPABILITIES=private_runtime,structured_output
SYSTEMONE_PROVIDER_PRIMARY_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

Benchmark records are keyed by provider instance, model, and task type and include run provenance. Routing policies filter candidates by capabilities, attributes, observed health, accuracy, calibration error, latency, failure rate, and known cost before empirical scoring.

## Calibration

Calibration is fitted through:

```text
POST /v2/calibration/fit
```

Profiles are keyed by provider instance, model, question type, and version. Compatible active engines reload newly fitted profiles without a service restart.

## Evaluation and certification

- `scripts/certify_runtime.py` performs live end-to-end runtime certification
- `eval/benchmark_runtime.py` records live labelled benchmark evidence
- `eval/evaluate.py` performs offline scoring
- `eval/data/` contains pipeline fixtures

Performance claims require executed labelled workloads.

## RAG integration

The included RAG service is optional:

```text
documents -> retrieval -> evidence -> System One -> typed decision
```

## Documentation

- [Operational Runbook](docs/RUNBOOK.md)
- [Decision Runtime](docs/DECISION_RUNTIME.md)
- [Capability Routing](docs/CAPABILITY_ROUTING.md)
- [Empirical Selection](docs/EMPIRICAL_SELECTION.md)
- [Evaluation Harness](EVAL_HARNESS.md)
- [OpenAPI](openapi.yaml)

## License

See [LICENSE](LICENSE).
