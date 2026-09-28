# System One Decision Runtime

System One is a provider-independent runtime for typed probabilistic decisions.

## Stable application contract

Applications call `POST /v2/decide` with:

- `state`
- typed questions
- optionally a provider **instance ID**
- optionally a model override
- optionally an empirical routing policy
- optionally an ensemble of provider instance IDs

Application code does not need to know which vendor, local server, or model sits behind an instance.

## Provider instances

Provider instances are created from deployment configuration.

```env
SYSTEMONE_PROVIDER_IDS=primary,secondary
SYSTEMONE_DEFAULT_PROVIDER=primary

SYSTEMONE_PROVIDER_PRIMARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_PRIMARY_BASE_URL=https://example.invalid/v1
SYSTEMONE_PROVIDER_PRIMARY_MODEL=model-from-this-deployment
SYSTEMONE_PROVIDER_PRIMARY_API_KEY=secret-if-required

SYSTEMONE_PROVIDER_SECONDARY_DRIVER=openai_compatible
SYSTEMONE_PROVIDER_SECONDARY_BASE_URL=http://host.docker.internal:11434/v1
SYSTEMONE_PROVIDER_SECONDARY_MODEL=another-model
SYSTEMONE_PROVIDER_SECONDARY_API_KEY=
```

The labels `primary` and `secondary` are examples only. They have no built-in meaning.

For an instance ID `foo-bar`, configuration uses the normalized prefix
`SYSTEMONE_PROVIDER_FOO_BAR_*`.

## Built-in protocol drivers

### `openai_compatible`

For any endpoint exposing compatible `/chat/completions` token logprobs.

Configuration:

- `BASE_URL`
- `MODEL`
- optional `API_KEY`
- optional `TIMEOUT_S`
- optional `MAX_PARALLEL`

An API key is not required by the runtime because local endpoints may not use authentication.

### `systemone_http`

For any service exposing a compatible `/v1/systemone` contract.

It is a protocol driver, not a vendor identity.

### Custom Python drivers

A deployment may load a custom provider class:

```env
SYSTEMONE_PROVIDER_CUSTOM_DRIVER=python:package.module:ProviderClass
```

This keeps new provider integrations out of application code.

## Default selection

There is no hardcoded default provider or model.

- If `SYSTEMONE_DEFAULT_PROVIDER` is set, it is used.
- Otherwise the first configured instance in `SYSTEMONE_PROVIDER_IDS` is used.
- If no instance is configured and no application-registered provider exists, the runtime refuses the request with a configuration error.

## Empirical selection

Benchmark records are persisted by:

```text
provider-instance-id + model + task-type
```

Selection can constrain:

- minimum measured accuracy
- maximum ECE
- maximum p95 latency
- maximum cost per 1,000 decisions
- provider-instance preference

The router therefore selects from what is actually configured and measured in that environment. It does not contain a vendor preference.

## Calibration

Calibration profiles are versioned by:

```text
provider-instance-id:model:question-type:version
```

This allows the same model served from two different environments to be measured and calibrated independently.

## Observability

Every provider call records:

- request ID
- provider instance ID
- actual model
- status
- latency
- reported token usage
- question types

## RAG relationship

RAG is an integration/example, not the identity of System One.

- RAG retrieves evidence.
- System One produces typed probabilistic decisions.
- Applications consume the stable runtime contract.
