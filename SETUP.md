# MiniPay Setup Guide

## Environment
- Linux / Parrot OS
- Python 3.11
- PostgreSQL 15
- Podman or Docker
- Git

## Python
Create a virtual environment:

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

Copy .env.example to .env and set a private MINIPAY_API_KEY.

Never commit .env.

## Database
Create a local PostgreSQL database named minipay.
Apply database/schema.sql, then database/api_extension.sql.

The original database/generate_data.py provides the synthetic
dataset generator. Review its usage before seeding; do not
run it twice on the same populated database.

The assessed local dataset initially contained:
- 1,000 customers
- 50,000 transactions
- 56,589 callback attempts

Use local PostgreSQL authentication and the DB connection
specified in MINIPAY_DATABASE_URL.

## Run Application
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

UI: http://127.0.0.1:8000/ui/
API documentation: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health

## Automated Tests
.venv/bin/python -m pytest tests/api/ tests/unit/ tests/ui/ -v

Browser testing requires:
.venv/bin/python -m playwright install chromium

API tests create synthetic demo records.

## Container
podman build -t minipay-api:1.0 .

The verified container smoke tests covered /openapi.json
and /ui/. Container-to-database connectivity was not verified.

## Kubernetes
Manifests: kubernetes/

Live deployment verified on 29 October 2026:
- K3s namespace minipay: API Deployment 2/2 Ready.
- PostgreSQL StatefulSet 1/1 Ready; PVC 2 GiB Bound.
- In-cluster functional tests: 8/8 PASS.
- Rancher v2.15.2: Helm deployed, revision 2.
- Rancher HTTPS: HTTP 200 with the local trusted CA.
- Rancher UI: local cluster, MiniPay API and database verified.

Verification commands (on the configured K3s VM):
  sudo k3s kubectl -n minipay get deployments,statefulsets,pods,pvc
  sudo k3s kubectl -n cattle-system get deployment rancher
  sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm status rancher -n cattle-system

Rancher evidence: evidence/rancher.md
Deployment uses local TLS and local Kubernetes credentials.
External MiniPay port-forward access was not independently verified.
