# Kubernetes Network and DNS Incident Runbook

Use this runbook when pods cannot resolve service names, connections intermittently time out, service-to-service traffic fails, or a deployment appears healthy while application requests cannot reach dependencies.

## Operating principles

Work from observable evidence, keep changes reversible, and record the state before and after each intervention. Prefer the smallest action that can distinguish between competing causes. Escalate when the blast radius, security impact, financial exposure, or uncertainty exceeds the authority of the operator. All thresholds, owners, and approval limits should be interpreted against the local environment rather than assumed from this runbook.

## Establish the failure boundary

Determine whether the issue is DNS resolution, service discovery, routing, policy, endpoint health, or an upstream dependency.

### 1. reproduce from the affected pod
Treat reproduce from the affected pod as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. compare pod and node DNS configuration
Treat compare pod and node dns configuration as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. inspect CoreDNS health and recent restarts
Treat inspect coredns health and recent restarts as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. check service and endpoint objects
Treat check service and endpoint objects as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. compare same-namespace and cross-namespace resolution
Treat compare same-namespace and cross-namespace resolution as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. test direct pod IP reachability
Treat test direct pod ip reachability as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. inspect NetworkPolicy selectors
Treat inspect networkpolicy selectors as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. review CNI daemon health
Treat review cni daemon health as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## DNS diagnosis

Validate the complete resolution path before changing CoreDNS configuration.

### 1. query the service FQDN
Treat query the service fqdn as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. query an external hostname
Treat query an external hostname as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. inspect resolv.conf inside the pod
Treat inspect resolv.conf inside the pod as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. check ndots and search domains
Treat check ndots and search domains as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. review CoreDNS logs for SERVFAIL or timeout
Treat review coredns logs for servfail or timeout as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. inspect upstream resolver reachability
Treat inspect upstream resolver reachability as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. compare failing and healthy nodes
Treat compare failing and healthy nodes as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. check node-local DNS cache if present
Treat check node-local dns cache if present as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Network path diagnosis

Use independent network signals to isolate routing and policy failures.

### 1. confirm destination endpoints are ready
Treat confirm destination endpoints are ready as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. test service ClusterIP connectivity
Treat test service clusterip connectivity as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. test direct endpoint connectivity
Treat test direct endpoint connectivity as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. review kube-proxy or eBPF dataplane state
Treat review kube-proxy or ebpf dataplane state as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. inspect security groups or firewall rules at cluster boundaries
Treat inspect security groups or firewall rules at cluster boundaries as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. check MTU mismatch symptoms
Treat check mtu mismatch symptoms as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. review conntrack pressure
Treat review conntrack pressure as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. compare traffic from another namespace
Treat compare traffic from another namespace as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Mitigation

Apply the least disruptive mitigation that restores service while preserving evidence.

### 1. restart only a clearly unhealthy DNS component
Treat restart only a clearly unhealthy dns component as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. roll back a recent NetworkPolicy change
Treat roll back a recent networkpolicy change as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. move a workload away from a failing node
Treat move a workload away from a failing node as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. restore a known-good CNI configuration
Treat restore a known-good cni configuration as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. temporarily reduce dependency fan-out
Treat temporarily reduce dependency fan-out as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. use a documented emergency resolver only with approval
Treat use a documented emergency resolver only with approval as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Recovery and closure

A runbook is complete only when the original symptom is no longer present, dependent services are healthy, monitoring is stable for an appropriate observation window, and any temporary bypass has been removed or explicitly tracked. Capture the root cause or best-supported contributing factors, the evidence that ruled out alternatives, the action taken, and the follow-up work that would prevent recurrence. If the incident or process exposed a control gap, create a durable corrective action rather than relying on operator memory.
