# Backup Restore and Data Recovery Verification Runbook

Use this runbook to validate that backups are restorable, to prepare for a production recovery, or to recover data after corruption, accidental deletion, storage failure, or an unsuccessful deployment.

## Operating principles

Work from observable evidence, keep changes reversible, and record the state before and after each intervention. Prefer the smallest action that can distinguish between competing causes. Escalate when the blast radius, security impact, financial exposure, or uncertainty exceeds the authority of the operator. All thresholds, owners, and approval limits should be interpreted against the local environment rather than assumed from this runbook.

## Define the recovery objective

State exactly what must be recovered and what loss window is acceptable before touching backup media.

### 1. identify affected datasets
Treat identify affected datasets as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. record the incident time window
Treat record the incident time window as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. determine required recovery point
Treat determine required recovery point as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. determine required recovery time
Treat determine required recovery time as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. identify dependent systems
Treat identify dependent systems as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. classify whether recovery is full partial or point-in-time
Treat classify whether recovery is full partial or point-in-time as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. confirm encryption key availability
Treat confirm encryption key availability as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. identify legal or retention constraints
Treat identify legal or retention constraints as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Validate backup artifacts

Do not assume a backup is usable because a job reported success.

### 1. verify artifact existence and size
Treat verify artifact existence and size as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. verify checksums where available
Treat verify checksums where available as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. verify backup catalog metadata
Treat verify backup catalog metadata as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. confirm encryption and key references
Treat confirm encryption and key references as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. check retention tier and immutability state
Treat check retention tier and immutability state as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. review the most recent successful restore test
Treat review the most recent successful restore test as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. validate incremental chain completeness
Treat validate incremental chain completeness as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. confirm database log or WAL continuity
Treat confirm database log or wal continuity as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 9. check object-store version availability
Treat check object-store version availability as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Prepare an isolated restore

Restore into an isolated target first whenever the incident allows it.

### 1. provision isolated storage
Treat provision isolated storage as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. prevent accidental production writes
Treat prevent accidental production writes as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. restore base snapshot
Treat restore base snapshot as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. apply incremental backups
Treat apply incremental backups as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. apply transaction logs to target point
Treat apply transaction logs to target point as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. capture restore warnings
Treat capture restore warnings as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. validate schema and object counts
Treat validate schema and object counts as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. compare critical table row counts
Treat compare critical table row counts as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 9. validate application-readable samples
Treat validate application-readable samples as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 10. measure restore duration
Treat measure restore duration as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Data integrity verification

Use application-level checks in addition to storage-level success.

### 1. run referential-integrity checks
Treat run referential-integrity checks as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. validate checksums or hashes for critical objects
Treat validate checksums or hashes for critical objects as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. compare aggregate balances or counts
Treat compare aggregate balances or counts as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. verify recent business transactions
Treat verify recent business transactions as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. check sequence and identity values
Treat check sequence and identity values as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. validate permissions and ownership
Treat validate permissions and ownership as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. confirm timezone and collation settings
Treat confirm timezone and collation settings as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. check replication configuration
Treat check replication configuration as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 9. verify search or cache rebuild requirements
Treat verify search or cache rebuild requirements as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Production recovery execution

Use an explicit change boundary and rollback point.

### 1. announce write freeze if required
Treat announce write freeze if required as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. capture final pre-recovery state
Treat capture final pre-recovery state as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. stop conflicting writers
Treat stop conflicting writers as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. restore or promote the validated target
Treat restore or promote the validated target as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. update connection endpoints
Treat update connection endpoints as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. rotate credentials only if required
Treat rotate credentials only if required as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. run smoke tests before broad traffic
Treat run smoke tests before broad traffic as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. restore traffic gradually
Treat restore traffic gradually as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 9. monitor error and latency rates
Treat monitor error and latency rates as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 10. retain the pre-recovery state until validation completes
Treat retain the pre-recovery state until validation completes as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Post-recovery monitoring

A successful restore is not the end of recovery.

### 1. monitor replication and backup jobs
Treat monitor replication and backup jobs as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 2. confirm new recovery points are being created
Treat confirm new recovery points are being created as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 3. verify scheduled jobs resumed
Treat verify scheduled jobs resumed as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 4. check downstream exports and integrations
Treat check downstream exports and integrations as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 5. review delayed messages and queues
Treat review delayed messages and queues as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 6. validate user-facing data consistency
Treat validate user-facing data consistency as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 7. schedule a follow-up restore test
Treat schedule a follow-up restore test as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

### 8. record actual RPO and RTO achieved
Treat record actual rpo and rto achieved as an evidence-gathering step rather than an assumption. Record the observation, timestamp, affected scope, and any change that immediately preceded it. Compare the result with the known-good baseline for the service or process, and separate correlation from causation. If the evidence is ambiguous, preserve the current state and gather the next independent signal before making a destructive change.

## Recovery and closure

A runbook is complete only when the original symptom is no longer present, dependent services are healthy, monitoring is stable for an appropriate observation window, and any temporary bypass has been removed or explicitly tracked. Capture the root cause or best-supported contributing factors, the evidence that ruled out alternatives, the action taken, and the follow-up work that would prevent recurrence. If the incident or process exposed a control gap, create a durable corrective action rather than relying on operator memory.
