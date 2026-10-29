# Rancher / Kubernetes Operational Evidence

## Environment

- Verification date: 29 October 2026
- Rancher version: v2.15.2
- Kubernetes: K3s v1.36.5+k3s1
- Cluster: local, single-node VirtualBox
- Rancher namespace: cattle-system
- MiniPay namespace: minipay
- TLS: locally generated private CA and custom Kubernetes TLS secret

## Verified Results

- Rancher Helm release: deployed, revision 2.
- Rancher Deployment: 1/1 Ready.
- Rancher HTTPS: HTTP 200, verified using the local CA.
- Rancher dashboard login and local cluster access: successful.
- MiniPay API Deployment visible in Rancher: 2/2 Ready.
- PostgreSQL StatefulSet visible in Rancher: 1/1 Ready.
- PostgreSQL PVC: Bound, capacity 2 GiB.
- MiniPay API /health: HTTP 200, database connected.
- In-cluster functional tests: 8/8 PASS.

## Evidence

- rancher-live-verification.txt — final live checks
- rancher-dashboard.png — Rancher local cluster
- rancher-deployments.png — MiniPay API in Rancher
- rancher-statefulsets.png — PostgreSQL in Rancher
- kubernetes-service-tests.txt — functional test results
- kubernetes-live-status.txt — cluster and workload status

## Scope and Limitations

Rancher was deployed using a custom TLS certificate without
cert-manager. An earlier cert-manager image-pull attempt
encountered Quay CDN timeouts, but this did not prevent the
final Rancher deployment.

The setup is local, single-node and not publicly hosted.
External MiniPay port-forward access was not independently
accepted; in-cluster functional testing passed.

No database reset or MiniPay application restart was required
to complete Rancher verification.


## Kubernetes Operations Evidence and Boundaries

The following **previously captured** evidence documents Kubernetes
operations, not a claim that each action was clicked in Rancher:

- API application log inspection and pod CPU/memory readings:
  `evidence/operations-and-rancher-check.txt`.
- Deployment rollout status (success):
  `evidence/kubernetes-live-status.txt`.
- Deployment, StatefulSet and cluster visibility in Rancher screenshots:
  `evidence/rancher-dashboard.png`, `evidence/rancher-deployments.png`,
  `evidence/rancher-statefulsets.png`.
- Configuration (without confidential Secret values) is inspectable in
  `kubernetes/01-settings.yaml`, `kubernetes/03-database.yaml`, and
  `kubernetes/04-api.yaml`.

The submitted screenshots do **not** independently prove Rancher UI
log-viewing, configuration inspection, or an interactive scaling action.
Those are not claimed complete in this document. The original assignment
requests scaling **or rollout/restart** evidence; the captured Kubernetes
rollout-status result addresses the rollout-status portion, but does not
prove a user-triggered rollout/restart.

### Safe read-only commands on the existing K3s VM

```bash
sudo k3s kubectl -n minipay get deployment minipay-api
sudo k3s kubectl -n minipay rollout status deployment/minipay-api --timeout=20s
sudo k3s kubectl -n minipay get pods -o wide
sudo k3s kubectl -n minipay top pods
sudo k3s kubectl -n minipay logs deployment/minipay-api --tail=20
sudo k3s kubectl -n minipay get configmap minipay-settings -o name
```

Review log output for sensitive data before saving or publishing it.
Never run `kubectl get secret -o yaml` for public evidence. Avoid
scaling, restarts, apply/delete commands or DB reset on the working
cluster merely to create screenshots.
