# Kubernetes CrashLoopBackOff diagnostic guide

## Overview

This runbook covers Kubernetes pods stuck in CrashLoopBackOff. The pod is restarting repeatedly because the container exits soon after startup.

## First checks

Check the pod status and container exit codes. If the container exits with code 137, this usually means the process was terminated by SIGKILL. That often indicates memory pressure, OOM kill, or a forced stop from an orchestration event.

## Investigate the restart reason

Use `kubectl describe pod` and inspect the `State` section. If the `Last State` shows `Terminated` with exit code 137, look at memory limits and the system memory usage of the node. You should also inspect the workload and the resource requests and limits.

## Common root causes

- The app uses more memory than the limit allows.
- The node is under memory pressure and the kernel kills the pod.
- A sidecar or init container exits early due to config or certificate issues.
- The startup command is invalid, causing the app to exit quickly.

## What to check first

Review the pod events and the application logs. In a CrashLoopBackOff loop, start with the last container log lines. If the cause is OOM, you will usually see `Out of memory` or a Java heap error. If the process was killed by the kernel, the node-level memory pressure and cgroup reports are the next most important evidence.

## Response steps

1. Confirm the pod is restarting and capture the latest `kubectl logs` output.
2. Check the node memory pressure and any eviction events.
3. Increase the memory limit only after confirming the app actually needs more headroom.
4. Recheck the liveness and readiness probes. A failing readiness check can cause restart loops if the app is not healthy.
5. Review the startup command and config map values. A small typo can cause immediate exit.

## Decision guidance

If exit code 137 appears, treat it as a likely node memory or kill event until proven otherwise. The fastest path is to inspect the node memory pressure, the pod resource limits, and the recent application logs.
