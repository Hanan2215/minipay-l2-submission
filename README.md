# MiniPay — Implementation & L2 Support Engineer Assessment

MiniPay is the Paysys Labs technical assessment implementation covering Linux, Git, PostgreSQL, REST APIs, Python support automation, testing, containers, Kubernetes, Rancher and incident investigation.

## Completed Work

- PostgreSQL database and SQL investigation reports.
- FastAPI payment service with API-key authentication and idempotency.
- Python read-only L2 support utility and automated tests.
- Browser UI with Playwright verification.
- Container build and smoke testing.
- Live K3s deployment: MiniPay API 2/2 and PostgreSQL 1/1.
- Kubernetes service functional tests: 8/8 passed.
- Rancher v2.15.2 deployed and verified through its management UI.
- Three incident investigation and root-cause reports.

## Setup and Documentation

- [Setup instructions](SETUP.md)
- [Architecture](ARCHITECTURE.md)
- [AI usage disclosure](AI_USAGE.md)
- [Original assessment instructions](INSTRUCTIONS.md)
- [Assessment requirements](requirements/)
- [Python support utility](python/README.md)
- [UI automation scope and CI plan](tests/ui/NOTES.md)

## Verification Evidence

- [Rancher operational verification](evidence/rancher.md)
- [Rancher live terminal verification](evidence/rancher-live-verification.txt)
- [Rancher dashboard screenshot](evidence/rancher-dashboard.png)
- [MiniPay API in Rancher](evidence/rancher-deployments.png)
- [PostgreSQL in Rancher](evidence/rancher-statefulsets.png)
- [Kubernetes functional tests](evidence/kubernetes-service-tests.txt)
- [Kubernetes status](evidence/kubernetes-live-status.txt)

## Incident Reports

- [Incident 001](investigation/INCIDENT-001-RCA.md)
- [Incident 002](investigation/INCIDENT-002-RCA.md)
- [Incident 003](investigation/INCIDENT-003-RCA.md)

## Environment Notes

The verified deployment runs on a local single-node K3s VirtualBox environment. Rancher uses a local custom TLS certificate and is not a public production deployment. External MiniPay port-forward access was not independently accepted; in-cluster service tests passed.

## Git Workflow

The assessment implementation was developed through incremental commits
on the `main` branch; no feature-branch merge was claimed. The original
`submission-v1.0` tag and later `submission-v1.1` Rancher-evidence tag
are retained as historical snapshots. Subsequent documentation/tests
must be new commits/tags, not a retag of previously submitted versions.
