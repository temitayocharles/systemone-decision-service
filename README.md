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

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8002/health
curl http://localhost:8002/v2/providers
```

The Compose stack bootstraps the bundled Ollama models used by the default local configuration and pins the Chroma client/server to the same release.

Bundled local models:

- `qwen2.5:3b`
- `nomic-embed-text`

Model files persist in the `ollama-data` volume.

## Provider configuration

Inference instances are deployment-defined. See `.env.example` for the full local and secondary configuration.

## RAG integration

The included RAG service is optional:

```text
documents -> retrieval -> evidence -> System One -> typed decision
```

The local stack includes Ollama and Chroma. The Chroma Python client used by the RAG service and the Chroma server image are intentionally pinned to the same version so collection operations use one compatible API generation.

## Evaluation and certification

- `scripts/certify_runtime.py` performs live end-to-end runtime certification
- `eval/benchmark_runtime.py` records live labelled benchmark evidence
- `eval/evaluate.py` performs offline scoring
- `eval/data/` contains pipeline fixtures

Performance claims require executed labelled workloads.

## Documentation

- [Operational Runbook](docs/RUNBOOK.md)
- [Decision Runtime](docs/DECISION_RUNTIME.md)
- [Capability Routing](docs/CAPABILITY_ROUTING.md)
- [Empirical Selection](docs/EMPIRICAL_SELECTION.md)
- [Evaluation Harness](EVAL_HARNESS.md)
- [OpenAPI](openapi.yaml)

## License

See [LICENSE](LICENSE).
