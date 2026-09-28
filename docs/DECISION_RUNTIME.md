# System One Decision Runtime

System One is a provider-independent runtime for typed probabilistic decisions.

## Stable contract

Use `POST /v2/decide` with:

- `state`: application state or evidence
- `questions`: typed `choice`, `score`, or `noul/null` questions
- optional explicit `provider` and `model`
- optional empirical `policy`
- optional `ensemble` provider list

The runtime normalizes provider-specific output into one response contract.

## Provider model

Providers are adapters. Current adapters:

- `openai_compatible`: existing logprob decision engine
- `jev`: Jev System One API

Adding a provider must not require changing application callers.

## Empirical model selection

Benchmark records are persisted by provider, model, and task type. Selection can constrain:

- minimum measured accuracy
- maximum ECE
- maximum p95 latency
- maximum cost per 1,000 decisions
- provider preference

Among eligible models, the runtime scores measured accuracy, calibration, latency, cost, reliability, and sample support. There is no unmeasured synthetic benchmark data.

Use `eval/benchmark_runtime.py` with recorded labeled JSONL data to populate the benchmark store.

## Ensemble mode

Passing `ensemble: ["jev", "openai_compatible"]` calls both providers and combines compatible probability outputs. Failed providers are excluded if at least one provider succeeds.

## Calibration

Versioned calibration profiles live independently from providers. A profile key is:

`provider:model:question_type:version`

The original temperature-calibration machinery remains available for logprob-capable providers. Native provider probabilities can be benchmarked without forced post-hoc scaling.

## Observability

Every provider call records:

- request id
- provider/model
- status
- latency
- actual reported token usage
- question types

`GET /v2/metrics` exposes a compact local summary. The JSONL store can later be exported to Prometheus/OpenTelemetry without changing provider contracts.

## RAG relationship

RAG is an integration/example, not the identity of System One.

- RAG answers: what evidence is available?
- System One decides: what does the evidence imply?
- Applications act on the typed decision.

The runtime can consume evidence from this repository's example RAG service, the separate `rag-system`, Sivanta, or any other caller.
