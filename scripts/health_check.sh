#!/usr/bin/env bash

set -uo pipefail

DISK_LIMIT="${DISK_LIMIT:-90}"
MIN_AVAILABLE_MB="${MIN_AVAILABLE_MB:-512}"
API_URL="${API_URL:-}"

failed=0

echo "=== MiniPay L2 Health Check ==="
date -u '+Timestamp (UTC): %Y-%m-%dT%H:%M:%SZ'

echo
echo "[1] Disk Health"

disk_used=$(df -P / | awk 'NR==2 {gsub("%","",$5);print $5}')

if [[ "$disk_used" =~ ^[0-9]+$ ]] &&
   (( disk_used < DISK_LIMIT )); then
    echo "PASS: Disk usage ${disk_used}%"
else
    echo "FAIL: Disk usage ${disk_used:-unknown}%"
    failed=1
fi

echo
echo "[2] Memory Health"

available_mb=$(awk '/MemAvailable:/ {printf "%.0f", $2/1024}' /proc/meminfo)

if [[ "$available_mb" =~ ^[0-9]+$ ]] &&
   (( available_mb >= MIN_AVAILABLE_MB )); then
    echo "PASS: Available memory ${available_mb} MB"
else
    echo "FAIL: Available memory ${available_mb:-unknown} MB"
    failed=1
fi

echo
echo "[3] MiniPay API Health"

if [[ -z "$API_URL" ]]; then
    echo "SKIP: API_URL not configured"
else
    http_code=$(curl -sS -o /dev/null \
      -w '%{http_code}' \
      --connect-timeout 3 \
      --max-time 10 \
      "$API_URL") || http_code="000"

    if [[ "$http_code" == "200" ]]; then
        echo "PASS: API HTTP 200"
    else
        echo "FAIL: API HTTP $http_code"
        failed=1
    fi
fi

echo
if (( failed == 0 )); then
    echo "RESULT: All executed checks passed"
else
    echo "RESULT: One or more checks failed"
fi

exit "$failed"
