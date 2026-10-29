#!/usr/bin/env bash
# Read-only MiniPay operational verification: no scale/restart/apply/DB writes.
set -euo pipefail

echo '=== CAPTURE DATE (LOCAL) ==='
date -Is
echo '=== CLUSTER ==='
sudo k3s kubectl get nodes
echo '=== MINIPAY WORKLOADS ==='
sudo k3s kubectl -n minipay get deployments,statefulsets,pods,pvc
echo '=== API ROLLOUT STATUS ==='
sudo k3s kubectl -n minipay rollout status deployment/minipay-api --timeout=20s
echo '=== API LOGS: FILTERED HEALTH REQUESTS ONLY ==='
sudo k3s kubectl -n minipay logs deployment/minipay-api --tail=80 | grep -E 'GET /(health|openapi.json) ' | tail -n 12 || true
echo '=== RESOURCE METRICS (may be unavailable) ==='
sudo k3s kubectl -n minipay top pods || true
echo '=== NONSECRET CONFIGURATION ==='
sudo k3s kubectl -n minipay get deployment minipay-api \
  -o jsonpath='replicas={.spec.replicas}{"\n"}{range .spec.template.spec.containers[*]}container={.name} image={.image}{"\n"}{end}'
echo
echo '=== RANCHER DEPLOYMENT ==='
sudo k3s kubectl -n cattle-system get deployment rancher
