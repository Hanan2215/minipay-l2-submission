# Rancher / Kubernetes Operational Evidence

## Verified Local Environment
- Podman available.
- Container image built successfully.
- Container API and UI returned HTTP 200.
- Kubernetes YAML static validation passed.
- kubectl, kind and minikube were not installed during inspection.

## Rancher Status
A live Rancher deployment and cluster workload inspection
have not been performed or verified.

No Rancher screenshots or live pod statuses are claimed.

## Intended Rancher Verification Procedure
1. Connect/import the Kubernetes cluster into Rancher.
2. Open the minipay namespace and inspect workloads.
3. Verify API Deployment replicas and database StatefulSet.
4. Inspect pod readiness, events and container logs.
5. Inspect ConfigMaps and environment-variable references
   without exposing Secret values.
6. Check CPU/memory usage and health indicators.
7. Perform a controlled rollout/restart and observe readiness.
8. Test API and UI access after rollout.

## Equivalent Kubernetes Commands
kubectl get pods,deploy,sts,svc -n minipay
kubectl describe deployment minipay-api -n minipay
kubectl logs deployment/minipay-api -n minipay
kubectl rollout status deployment/minipay-api -n minipay
kubectl top pods -n minipay

These are documented procedures, not verified execution
records.

## Limitation
Static manifest validation and Podman smoke testing do not
establish successful live Kubernetes deployment.
