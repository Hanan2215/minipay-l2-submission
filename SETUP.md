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
For a **fresh isolated Linux machine only** (not on the already-working
assessment VM), install/start PostgreSQL and create the database. The
`api_extension.sql` script needs a `psql` variable named `app_user`:

```bash
sudo -u postgres createdb minipay
sudo -u postgres psql -v ON_ERROR_STOP=1 -d minipay < database/schema.sql
sudo -u postgres psql -v ON_ERROR_STOP=1 -v app_user="$USER" -d minipay < database/api_extension.sql
```

The extension script creates/grants the Linux login's database role for
local **peer authentication**. This assumes the default Debian/Parrot
local PostgreSQL authentication; other OS and authentication setups
need corresponding connection settings/permissions. Do not run these
initialization commands against the existing populated database.

For the original synthetic test dataset on a **newly initialized** DB:

```bash
python3 database/generate_data.py > /tmp/minipay-seed.sql
sudo -u postgres psql -v ON_ERROR_STOP=1 -d minipay < /tmp/minipay-seed.sql
```

In `.env`, set `MINIPAY_DATABASE_URL` for the login/database you just
created (for local peer auth, `dbname=minipay user=<your-linux-login>`),
and set a private `MINIPAY_API_KEY`. Never commit `.env`.

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


## Reproducibility: More Detailed K3s Notes

The submitted Kubernetes manifests represent the **tested target
configuration**. A new evaluator cluster still requires an image
import/push, Kubernetes Secrets and local K3s/container tooling;
these are deliberately not committed. Do not blindly re-apply these
manifests over the already-working assessment cluster.

New isolated-cluster preparation sequence:

1. Install/start K3s and configure `kubectl` access.
2. Build image `minipay-api:1.0` with Podman or Docker.
3. Make that image available to the K3s node's container runtime,
   e.g. export from Podman and import with K3s containerd:

   ```bash
   podman save -o /tmp/minipay-api.tar minipay-api:1.0
   sudo k3s ctr images import /tmp/minipay-api.tar
   ```

4. Apply namespace `kubernetes/00-namespace.yaml`, then create the
   `minipay-credentials` Secret in namespace `minipay`. Required keys:
   `api-key` and `db-password`. Prepare two separate local files holding
   the private values in a **non-repository**, permission-protected
   directory (file mode `0600`, directory mode `0700`). Example using
   files **already created securely** by the evaluator:

   ```bash
   sudo k3s kubectl apply -f kubernetes/00-namespace.yaml
   sudo k3s kubectl -n minipay create secret generic minipay-credentials \
     --from-file=api-key="$HOME/.local/share/minipay-secrets/api-key" \
     --from-file=db-password="$HOME/.local/share/minipay-secrets/db-password"
   ```

   Do not print secret contents, put secret values in shell command
   arguments/history or commit the files. Only on a fresh isolated
   cluster. `Secret` objects do not by themselves constitute encrypted
   at-rest storage; secure the cluster appropriately.
5. Apply the remaining YAML manifests in numerical order, then
   inspect pod readiness and rollout. Database schema ConfigMap is
   mounted as PostgreSQL init scripts on **fresh** database storage.
   Existing PVCs will not be reinitialized by applying a ConfigMap.
6. Verify in-cluster MiniPay API and database connectivity; see
   `scripts/verify_k8s_service.py` and the recorded result
   `evidence/kubernetes-service-tests.txt`.

For the existing VM, use **read-only** status and log inspection only:

```bash
sudo k3s kubectl -n minipay get deployments,statefulsets,pods,pvc
sudo k3s kubectl -n minipay rollout status deployment/minipay-api --timeout=20s
sudo k3s kubectl -n minipay logs deployment/minipay-api --tail=20
```

Rancher was deployed separately using a **locally generated private
CA**, Helm and a private TLS Secret outside the public repository.
This Git repository intentionally does not reproduce the private key
or authentication material. See `evidence/rancher.md` for verification
and operational limitations.

## Kubernetes Restart/Rollout Procedure (not executed here)

For an authorized change in an isolated/test cluster, check current
rollout status, capture current configuration and logs, then perform a
controlled API-only rollout if explicitly permitted. This command is
**NOT read-only** and must NOT be run merely to gather evidence:

```bash
# AUTHORIZED TEST CLUSTER ONLY; impacts API pods
sudo k3s kubectl -n minipay rollout restart deployment/minipay-api
sudo k3s kubectl -n minipay rollout status deployment/minipay-api --timeout=120s
```

Afterwards verify 2/2 readiness and `/health`. Never restart the DB or
clear its persistent volume as part of an API rollout demonstration.

## UI CI and Regression Strategy

See `tests/ui/NOTES.md` for test prerequisites, the existing Playwright
scenario, proposed CI integration and recommended release/regression
coverage. A CI pipeline has not been independently run.
