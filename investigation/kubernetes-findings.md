# Incident 2 — Broken Kubernetes Deployment

## Problem
The supplied starter manifest contains configuration defects
that would prevent a reliable MiniPay deployment.

## Root Cause Findings

1. Line 18: YOUR_IMAGE_HERE is not a deployable application image.
2. Line 27: Readiness probe uses port 8081, while the container
   declares port 8080.
3. Line 44: Service selects minipay-backend, but Deployment pods
   are labeled minipay-api.
4. Line 47: Service routes to port 8081 instead of 8080.
5. Required application API key and PostgreSQL connection
   settings are not defined in the starter manifest.
6. Namespace, database workload, persistent storage and
   resource limits are not supplied.

## Remediation
Preserved the original broken manifest unchanged.

Created a separate Kubernetes configuration with:
- Namespace and ConfigMap
- PostgreSQL StatefulSet and persistent volume claim
- Database initialization schema
- API Deployment with two replicas
- Correct labels and service target port
- Readiness and liveness probes
- CPU and memory requests/limits
- External Kubernetes Secret references

## Security
Real API keys and database passwords must be supplied through
a Kubernetes Secret at deployment time. Secrets are not
committed to Git.

## Verification Status
Static root-cause investigation completed.

Actual cluster rollout, pod readiness, database initialization,
service connectivity and Rancher verification remain pending.
No successful cluster deployment is claimed.
