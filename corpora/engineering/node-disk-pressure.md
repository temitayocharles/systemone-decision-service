# Node disk pressure guide

## Overview

Disk pressure on a worker node affects the kubelet, container runtime, and all workloads scheduled to that node. It usually shows up first as evictions, container restarts, and increasing `No space left on device` events.

## First checks

- Review node conditions and the kubelet logs.
- Inspect disk usage on the filesystem hosting `/var/lib/docker`, `/var/lib/containers`, or the Kubernetes data path.
- Check for runaway logs or large temporary files.
- Confirm whether a workload is writing too much data or creating left-over temp files.

## Common causes

- Log volume consuming the filesystem.
- A stuck or runaway job writing to disk.
- A cache or temporary directory expanding unexpectedly.
- A storage volume for a pod is near capacity.

## Response steps

1. Identify the largest consumers on the node.
2. Clean up or rotate logs if they are unexpectedly large.
3. Reduce disk usage in the problematic workload or increase the backing volume.
4. Rebalance workloads if one node is overloaded.

## Decision guidance

If a pod is failing because of disk pressure, treat the node as the first suspect. Quick evidence comes from node conditions, fs usage, and the recent pod eviction events.
