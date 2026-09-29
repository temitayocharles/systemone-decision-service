# TLS Certificate Expiry and Trust Failure Runbook

Use this runbook for certificate-expiry alerts, hostname mismatch, trust-chain failures, mutual-TLS authentication errors, or services that become unreachable after certificate rotation.

## Operating principles

Work from observable evidence, keep changes reversible, and record the state before and after each intervention. Prefer the smallest action that can distinguish between competing causes. Escalate when the blast radius, security impact, financial exposure, or uncertainty exceeds the authority of the operator. All thresholds, owners, and approval limits should be interpreted against the local environment rather than assumed from this runbook.

## Identify the certificate in use

Confirm which listener, ingress, proxy, or application process is presenting the certificate.

### 1. capture the served certificate chain
Treat capture the served certificate chain as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. check subject alternative names
Treat check subject alternative names as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. record not-before and not-after timestamps
Treat record not-before and not-after timestamps as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. identify issuing authority
Treat identify issuing authority as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. compare secret or keystore versions
Treat compare secret or keystore versions as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. check SNI behavior
Treat check sni behavior as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Trace distribution and rotation

Determine whether the new certificate reached every component that should consume it.

### 1. inspect secret synchronization status
Treat inspect secret synchronization status as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. check deployment reload behavior
Treat check deployment reload behavior as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. compare replicas for certificate serial number
Treat compare replicas for certificate serial number as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. review ingress controller reload logs
Treat review ingress controller reload logs as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. inspect sidecar or service-mesh certificates
Treat inspect sidecar or service-mesh certificates as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. confirm trust store updates
Treat confirm trust store updates as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Restore trust safely

Use the narrowest recovery path and preserve rollback options.

### 1. restore a known-good certificate secret
Treat restore a known-good certificate secret as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. trigger documented certificate reload
Treat trigger documented certificate reload as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. restart only stale consumers
Treat restart only stale consumers as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. verify intermediate certificates
Treat verify intermediate certificates as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. validate mTLS peer trust
Treat validate mtls peer trust as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. test from internal and external clients
Treat test from internal and external clients as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Recovery and closure

A runbook is complete only when the original symptom is no longer present, dependent services are healthy, monitoring is stable for an appropriate observation window, and any temporary bypass has been removed or explicitly tracked. Capture the root cause or best-supported contributing factors, the evidence that ruled out alternatives, the action taken, and the follow-up work that would prevent recurrence. If the incident or process exposed a control gap, create a durable corrective action rather than relying on operator memory.
