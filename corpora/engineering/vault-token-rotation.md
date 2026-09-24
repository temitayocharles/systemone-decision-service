# Vault token rotation guide

## Purpose

This runbook explains how to rotate Vault tokens without breaking service access patterns. The safest approach is to rotate the token in a controlled sequence and verify all dependent services before retiring the old credential.

## Procedure

1. Confirm the token has an appropriate TTL and is not shared across unrelated workloads.
2. Create a new token with the same policy set and scoped access.
3. Update the consumer configuration for each service in a safe staging order.
4. Verify service health and token usage after the rollout.
5. Revoke the old token only after validation passes.

## Operator checks

- Check the Vault audit logs for a spike in authentication failures.
- Confirm that the token policy still allows the required secrets paths.
- Validate that the new token is not expired or revoked.
- Use a small test automation path before rotating production credentials.

## Common issues

A common failure mode is an expired token in a background job. Another is a stale secret in a deployment manifest. If service access breaks after rotation, look in the deployment config and the secret injection path before assuming Vault itself is unhealthy.

## Decision guidance

If a service suddenly loses access after a token change, check the token policy, secret injection, and the audit log first. The issue is usually configuration drift, not Vault availability.
