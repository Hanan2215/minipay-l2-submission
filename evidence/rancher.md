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
