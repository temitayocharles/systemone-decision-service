# Decision Runtime

System One exposes one stable decision contract across configurable inference backends.

## Runtime contract

Primary endpoints:

- `POST /v2/decide`
- `POST /v2/batch`
- `GET /v2/providers`
- `GET /v2/metrics`
- `GET /v2/benchmarks`
- `PUT /v2/benchmarks`

The runtime accepts state plus typed questions and returns normalized answers, routing metadata, token usage, and latency.

## Question types

### Choice

Select one key from a finite option set and return a probability distribution.

### Score

Return a numeric score and confidence.

### Null / noul

Evaluate a proposition as a probability between 0 and 1.

## Provider instances

Provider instances are declared at deployment time.

For instance ID `primary`:

```env
SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://inference.example/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-a
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=
SYSTEMONE_PROVIDER_PRIMARY_TIMEOUT_S=60
SYSTEMONE_PROVIDER_PRIMARY_MAX_PARALLEL=8
```

The list and default are configured independently:

```env
SYSTEMONE_PROVIDER_IDS=primary,secondary
SYSTEMONE_DEFAULT_PROVIDER=primary
```

Instance names are arbitrary deployment identifiers.

For an ID such as `local-box`, the configuration prefix is normalized to:

```text
SYSTEMONE_PROVIDER_LOCAL_BOX_*
```

## Protocol drivers

### openai_compatible

Uses an OpenAI-compatible `/chat/completions` endpoint with token logprobs.

Required deployment values:

- `BASE_URL`
- `MODEL`

Optional values:

- `API_KEY`
- `TIMEOUT_S`
- `MAX_PARALLEL`

Authentication is optional to support local endpoints.

### systemone_http

Uses a compatible `/v1/systemone` endpoint and normalizes responses into the runtime contract.

### Custom driver

A provider implementation can be loaded dynamically:

```env
SYSTEMONE_PROVIDER_CUSTOM_DRIVER=python:package.module:ProviderClass
```

The application contract remains unchanged when a new driver is introduced.

## Routing modes

### Default route

Uses `SYSTEMONE_DEFAULT_PROVIDER`, or the first configured provider instance when no explicit default is set.

### Explicit route

A request may provide `provider` and optionally `model`.

### Empirical route

A request may omit `provider` and supply a routing `policy`. The runtime evaluates capability, health, and benchmark constraints and selects an eligible provider/model record.

### Ensemble route

A request may provide an `ensemble` list. Compatible outputs are combined into one normalized answer set.

## Calibration profiles

Calibration profiles are keyed by:

```text
provider-instance:model:question-type:version
```

This keeps calibration specific to the actual serving context.

## Observability

Each runtime invocation records:

- request ID
- provider instance
- model
- status
- latency
- token usage
- question types

The telemetry stream supports health-aware routing and operational analysis.

## Scaling model

The runtime API is stateless with respect to request execution. Persistent benchmark, telemetry, and calibration paths can be mounted or replaced by shared storage in clustered deployments.

Provider instances can point to:

- externally hosted inference
- local inference servers
- cluster-internal inference services
- native System One services
- custom drivers

Horizontal runtime scaling does not change the caller contract.
