# ArgoCD sync failure guide

## Overview

When ArgoCD reports sync failure, the most important fact is whether the failure is caused by a Git drift, a cluster validation issue, or a resource conflict. The symptoms are often visible in the app diff and the cluster state.

## First checks

1. Inspect the app status and the sync status panel.
2. Compare the desired manifest in Git against the live cluster state.
3. Look for validation errors such as immutable field changes or invalid image references.
4. Check for a missing namespace or a resource that is being re-created in the wrong sequence.

## Typical problems

- Namespace mismatch between the app and the cluster.
- An invalid resource because of schema or custom resource mismatch.
- Incompatible changes to a live object that cannot be updated in place.
- A secret or config value that is missing in the target environment.

## Response steps

- Reconcile the live state with the desired Git state.
- Confirm the cluster has the required CRDs and permissions.
- Review the diff for resource ordering and hooks.
- Fix the broken manifest before reattempting sync.

## Decision guidance

If the sync error is a validation or conflict issue, the most actionable first move is to inspect the exact resource diff and the cluster event logs. Do not retry blindly until the manifest drift is understood.
