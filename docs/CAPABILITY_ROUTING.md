# Capability Routing

System One selects provider instances by requirements and measured performance.

## Capability profile

Each provider instance has:

- protocol-derived capabilities
- deployment-declared capabilities
- typed attributes
- empirical benchmark records
- observed runtime health

Example:

```env
SYSTEMONE_PROVIDER_PRIVATE_CAPABILITIES=private_runtime,multimodal,structured_output
SYSTEMONE_PROVIDER_PRIVATE_ATTRIBUTES_JSON={"local":true,"max_context":32768,"region":"ca-central"}
```

Capability names are open-ended.

## Protocol-derived capabilities

The built-in drivers contribute baseline capabilities automatically.

### openai_compatible

- `chat_completions`
- `token_logprobs`
- `probabilistic_decisions`

### systemone_http

- `native_systemone`
- `probabilistic_decisions`

Custom drivers may declare additional deployment capabilities.

## Typed attributes

Attributes express non-boolean properties.

Examples:

```json
{
  "local": true,
  "max_context": 32768,
  "region": "ca-central"
}
```

Routing policies can require exact values or numeric minimum/maximum bounds.

## Routing policy

```json
{
  "policy": {
    "task_type": "incident-triage",
    "required_capabilities": [
      "token_logprobs",
      "private_runtime"
    ],
    "forbidden_capabilities": [
      "external_network"
    ],
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

## Selection pipeline

Selection is performed in this order:

1. task-type compatibility
2. required and forbidden capabilities
3. attribute constraints
4. observed health
5. empirical performance thresholds
6. empirical scoring among eligible candidates

Capability eligibility is resolved before benchmark ranking.

## Health state

Current observed health is derived from the latest telemetry event for each provider instance.

- latest successful call: healthy
- latest failed call: unhealthy
- no observation: unknown

A known-unhealthy instance is excluded by default during empirical routing. Set `require_healthy: false` when a policy should ignore observed health.

## Extensibility

Capabilities and attributes intentionally use an open schema. New model-server features can be represented without changing the application API or registry data model.

Examples of deployment-defined capabilities may include:

- `streaming`
- `multimodal`
- `structured_output`
- `private_runtime`
- `tool_calling`
- `long_context`

The runtime remains centered on requirements rather than vendor identity.
