# Database Latency and Connection Saturation Runbook

Use this runbook when application latency rises with database wait time, connection pools saturate, queries queue, transactions time out, or a database remains reachable but cannot sustain normal workload.

## Operating principles

Work from observable evidence, keep changes reversible, and record the state before and after each intervention. Prefer the smallest action that can distinguish between competing causes. Escalate when the blast radius, security impact, financial exposure, or uncertainty exceeds the authority of the operator. All thresholds, owners, and approval limits should be interpreted against the local environment rather than assumed from this runbook.

## Confirm the symptom

Separate database latency from application, network, and dependency latency.

### 1. compare application and database latency timelines
Treat compare application and database latency timelines as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. measure active versus waiting connections
Treat measure active versus waiting connections as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. review connection pool saturation
Treat review connection pool saturation as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. inspect transaction timeout rates
Treat inspect transaction timeout rates as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. identify the highest-volume query families
Treat identify the highest-volume query families as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. check database CPU memory and I/O pressure
Treat check database cpu memory and i/o pressure as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Query and lock analysis

Find whether slow work, blocked work, or excess concurrency is the primary driver.

### 1. inspect long-running queries
Treat inspect long-running queries as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. identify lock wait chains
Treat identify lock wait chains as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. review transaction age
Treat review transaction age as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. compare execution plans with known-good behavior
Treat compare execution plans with known-good behavior as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. check missing or stale statistics
Treat check missing or stale statistics as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. look for sudden cardinality changes
Treat look for sudden cardinality changes as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. review batch jobs and migrations
Treat review batch jobs and migrations as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Capacity and storage

Validate resource and storage conditions before scaling.

### 1. inspect disk latency and queue depth
Treat inspect disk latency and queue depth as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. check free space and growth rate
Treat check free space and growth rate as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. review cache hit ratios
Treat review cache hit ratios as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. inspect checkpoint or vacuum pressure
Treat inspect checkpoint or vacuum pressure as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. compare replica lag
Treat compare replica lag as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. review network latency between application and database
Treat review network latency between application and database as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. check compute throttling
Treat check compute throttling as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Mitigation and recovery

Choose reversible actions based on evidence and business impact.

### 1. cancel a clearly runaway query
Treat cancel a clearly runaway query as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. pause a noncritical batch workload
Treat pause a noncritical batch workload as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. reduce application concurrency
Treat reduce application concurrency as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. restore a previous query plan or release
Treat restore a previous query plan or release as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. scale capacity when saturation is confirmed
Treat scale capacity when saturation is confirmed as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. fail over only when replication health is understood
Treat fail over only when replication health is understood as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. validate latency after each change
Treat validate latency after each change as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Recovery and closure

A runbook is complete only when the original symptom is no longer present, dependent services are healthy, monitoring is stable for an appropriate observation window, and any temporary bypass has been removed or explicitly tracked. Capture the root cause or best-supported contributing factors, the evidence that ruled out alternatives, the action taken, and the follow-up work that would prevent recurrence. If the incident or process exposed a control gap, create a durable corrective action rather than relying on operator memory.
