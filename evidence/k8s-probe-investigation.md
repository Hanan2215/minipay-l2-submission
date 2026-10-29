# Kubernetes Probe and DNS Investigation

Date: 2026-10-29

## Observations

- MiniPay API: 2/2 Ready at last check.
- PostgreSQL: 1/1 Running, PVC Bound.
- CoreDNS: 1/1 Running at last check.
- MiniPay API pods had 5 historical restarts each.
- CoreDNS had 6 historical restarts.
- Kubernetes events confirm liveness-probe failures.
- Readiness and liveness probe timeouts were 1 second.
- Previous API logs showed temporary DNS resolution failures for minipay-db.
- Current DNS resolution succeeded: 10.43.195.254.
- Node Ready, MemoryPressure False, DiskPressure False.
- Observed CPU usage: 30%; memory usage: 59%; disk usage: 56%.
- VM load average: 5.78, 4.33, 5.77.
- Swap: not configured.

## Assessment

Repeated probe failures and temporary DNS resolution failures are
confirmed. Elevated VM load and short probe timeouts may contribute,
but the underlying root cause is not conclusively established.

## Action

No Kubernetes configuration changes, deployments, database writes,
or manual service restarts were performed during this investigation.

## Follow-up

If failures recur, correlate host resource/IO metrics, kubelet
events, CoreDNS logs and API response latency before applying any
probe configuration change.

Any proposed change requires backup, controlled rollout and
post-change verification.
