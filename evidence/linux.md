# MiniPay - Linux Operational Evidence

## Environment

- OS: Parrot Security 6.3 (Debian-based)
- Kernel: 6.11+parrot-amd64
- Architecture: x86_64
- Environment: Oracle VirtualBox
- CPU: 4 vCPUs
- RAM: 7.8 GiB
- Filesystem: Btrfs
- Persistent root: /dev/sda1
- Evidence date: 2026-10-27

## 1. OS and Kernel

Commands:

    cat /etc/os-release
    uname -a

Observed:
- Parrot Security 6.3 (lorikeet)
- Linux kernel 6.11+parrot-amd64
- Architecture x86_64

## 2. CPU

Commands:

    nproc
    uptime
    top -b -n 1

Observed:
- 4 vCPUs
- Load average: 0.01, 0.02, 0.00
- CPU idle: 100% at sampled interval
- No CPU saturation observed during this sample

Note: Load average is not the same as CPU utilization.

## 3. Memory

Command:

    free -h

Observed:
- Total: 7.8 GiB
- Available: approximately 6.9 GiB
- Swap: 0 GiB

## 4. Disk

Commands:

    df -h /
    lsblk -f

Observed:
- Root filesystem: /dev/sda1 (Btrfs)
- Capacity: 44 GiB
- Used: 17 GiB
- Available: 27 GiB
- Utilization: 39%

## 5. Listening Ports

Command:

    sudo ss -lntp

Observed:
- TCP port 53 listening on IPv4 and IPv6
- Process: dnsmasq

MiniPay application ports are not yet deployed.

## 6. Highest Memory-Consuming Process

Command:

    ps -eo pid,comm,%mem,rss --sort=-rss | head -11

Observed:
- Process: Xorg
- PID at sample: 1158
- RSS: 142188 KiB
- Percentage of memory: 1.7%

PID values may change after reboot.

## 7. Directory Disk Usage

Command:

    du -h --max-depth=1 "$HOME" 2>/dev/null | sort -h

Observed:
- Home directory: approximately 6.5 MiB
- Cache directory: approximately 5.2 MiB
- Projects directory: approximately 436 KiB

These measurements were taken before MiniPay deployment.

## 8. Network and DNS

Commands:

    getent ahostsv4 github.com
    curl -sS -o /dev/null -w 'HTTP=%{http_code} TIME=%{time_total}s\n' --max-time 15 https://github.com

Observed:
- GitHub DNS resolution succeeded
- HTTPS status: HTTP 200
- Response time: 0.825366 seconds

## 9. Container Runtime

Commands:

    docker --version
    systemctl is-active docker

Observed:
- Docker CLI command invokes Podman emulation
- Podman version: 4.3.1
- docker.service: inactive

Docker Engine was not verified as running.
Container runtime selection remains pending.

## 10. System Logs

Commands:

    sudo journalctl -b -p warning -n 10 --no-pager
    systemctl status systemd-journald --no-pager
    sudo journalctl --disk-usage

Observed:
- Historical systemd-journald watchdog timeout
- Journal files reported corrupt or unclean shutdown
- Journald subsequently active and processing requests
- Journal storage approximately 48 MB

Root cause of the earlier watchdog failure is unconfirmed.
No log deletion or service restart was performed.

## 11. Application and Container Logs

Application deployment is pending.

After deployment, verify using:

    podman logs <container-name>

or, when using Kubernetes:

    kubectl logs -n minipay <pod-name>

Actual application log evidence will be added after deployment.

## 12. Troubleshooting Approach

### High CPU

1. Inspect top and per-process CPU usage.
2. Identify sustained CPU-intensive processes.
3. Review relevant service and application logs.
4. Correlate workload, requests, and recent deployments.
5. Apply targeted remediation after identifying the cause.

### Low Disk Space

1. Check df -h and df -i.
2. Find large directories using du.
3. Inspect logs, container storage and database files.
4. Identify safe retention or cleanup candidates.
5. Avoid deleting live database or application data.

### API Unreachable

1. Confirm application process and service health.
2. Check listening ports with ss -lntp.
3. Test local and remote connectivity with curl.
4. Verify DNS, firewall, service routing and probes.
5. Examine application and container logs.

### Repeated Process Termination

1. Inspect systemctl status and journalctl.
2. Identify exit codes, signals and OOM events.
3. Check memory limits, configuration and dependencies.
4. Compare timestamps with recent deployments.
5. Validate a targeted correction before closure.

## 13. Repeatable Health Check

Script:

    scripts/health_check.sh

The script will be validated separately.
API health checking remains pending until MiniPay is deployed.

## 14. Outstanding Evidence

- MiniPay application/container logs
- API health-check execution after deployment
- Kubernetes workload health and pod logs

## 15. Health-Check Script Validation

Validation date: 2026-10-27

### Test A: Script Syntax

Command:

    bash -n scripts/health_check.sh

Result:
- PASS: No syntax errors reported.

### Test B: Local System Health

Command:

    ./scripts/health_check.sh

Observed output:
- Disk usage: 39% - PASS
- Available memory: 7080 MB - PASS
- API: SKIP (API_URL not configured)
- Result: All executed checks passed

### Test C: Unavailable API Detection

Command:

    API_URL=http://127.0.0.1:8000/health ./scripts/health_check.sh

Observed output:
- Disk usage: 39% - PASS
- Available memory: 7081 MB - PASS
- API: Connection refused, HTTP 000
- Result: One or more checks failed

Interpretation:
MiniPay API was not yet deployed. The health-check
correctly detected that the configured API endpoint
was unreachable.

This was an expected negative test, not evidence
of a deployed application failure.

Final API success validation remains pending
until the MiniPay application is running.
