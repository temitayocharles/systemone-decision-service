# Capability-aware empirical routing

System One routes by **requirements**, not vendor identity.

Each configured provider instance has:

1. a protocol driver,
2. an endpoint/model,
3. a capability set,
4. typed attributes,
5. empirical benchmark records,
6. observed runtime health.

## Capability declarations

Example:

```env
SYSTEMONE_PROVIDER_PRIVATE_CAPABILITIES=private_runtime,multimodal
SYSTEMONE_PROVIDER_PRIVATE_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

Capability names are deliberately open-ended. Adding a future capability does
not require changing the registry schema.

Drivers also add capabilities implied by their protocol. For example,
`openai_compatible` currently contributes:

- `chat_completions`
- `token_logprobs`
- `probabilistic_decisions`

## Routing policy

A caller can ask for requirements rather than a provider:

```json
{
  "policy": {
    "task_type": "incident-triage",
    "required_capabilities": ["token_logprobs", "private_runtime"],
    "forbidden_capabilities": ["external_network"],
    "attribute_equals": {
      "local": true
    },
    "min_attributes": {
      "max_context": 32000
    },
    "max_ece": 0.05,
    "max_p95_latency_ms": 250,
    "min_accuracy": 0.90
  }
}
```

Selection proceeds in this order:

1. task compatibility
2. capability requirements
3. attribute requirements
4. observed health
5. empirical performance constraints
6. empirical scoring among survivors

This means a highly accurate model that lacks a required capability is never
selected simply because its benchmark score is high.

## Health-aware eligibility

The runtime derives current observed health from the latest telemetry event for
each instance.

- latest successful call -> healthy
- latest failed call -> unhealthy
- no observation -> unknown

Unknown is not treated as a failure. A known-unhealthy instance is excluded by
default when empirical routing is used. Set `require_healthy: false` in a
policy when that behavior is not wanted.

## Why capabilities and attributes are separate

Capabilities are boolean properties such as:

- `token_logprobs`
- `multimodal`
- `structured_output`
- `private_runtime`

Attributes carry typed values such as:

- `max_context: 32768`
- `local: true`
- `region: "ca-central"`

The schema remains open-ended so future inference systems can introduce new
properties without changes to application contracts.

## Empirical routing remains authoritative

Capabilities decide **what can satisfy the request**.

Benchmarks decide **which eligible option performs best for the task**.

The combination avoids both vendor hardcoding and capability-blind model
ranking.
