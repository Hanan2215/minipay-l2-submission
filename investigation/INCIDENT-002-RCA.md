# Live Kubernetes Verification Update — 29 October 2026

The earlier sections document the investigation at their
original verification stage.

Subsequent K3s deployment and functional testing confirmed:

- Kubernetes node Ready.
- MiniPay API Deployment: 2/2 available replicas.
- PostgreSQL StatefulSet: 1/1 running.
- PostgreSQL PVC: Bound, 2 GiB.
- Live Kubernetes Service functional tests: 8/8 passed.
- Customer creation, payment creation and idempotent retry passed.
- API health, Web UI, authentication, payment lookup and
  customer history passed.

Evidence:
- evidence/kubernetes-service-tests.txt
- evidence/kubernetes-live-status.txt

The in-cluster application is functioning. External
port-forward testing encountered connection problems;
external access has not been independently accepted.

Rancher UI verification remains pending.

---

# INCIDENT-002 — Application Unavailable After Deployment

Priority: P1
Status: Configuration corrected; live rollout unverified.

## Observations and Root Causes
The supplied starter Kubernetes manifest has these defects:

- Line 18: Invalid placeholder image YOUR_IMAGE_HERE.
- Line 27: Readiness probe targets 8081 instead of 8080.
- Line 44: Service selector does not match Deployment pod labels.
- Line 47: Service targetPort 8081 differs from container port 8080.
- Required database configuration and credentials are missing.

Original evidence: starter/kubernetes/broken-api.yaml

## Investigation and Correction
Preserved the original starter manifest unchanged.
Created corrected manifests under kubernetes/ with matching labels,
ports, configuration, probes, resource limits and database PVC.

The initial Podman image also failed with PermissionError
for /opt/minipay/app/main.py. File ownership was corrected
in Dockerfile and the image rebuilt.

## Verification
Container API: HTTP 200
Container Web UI: HTTP 200
Five Kubernetes YAML files: static validation passed.
Selectors, ports, probes and PVC checks: passed.

Evidence:
evidence/container-smoke-fixed.txt
evidence/kubernetes-validation.txt

## Remaining Work
Actual Kubernetes deployment, pod readiness, service access,
database connectivity and Rancher verification are pending.
Live service recovery is not claimed.

## Prevention
Validate manifests in CI, check selectors and ports,
test container permissions, monitor rollout readiness,
secure credentials and maintain rollback procedures.
