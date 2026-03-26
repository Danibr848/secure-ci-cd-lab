#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

if command -v gitleaks >/dev/null 2>&1; then
  echo "[secrets] Running local gitleaks binary"
  gitleaks git --source . --redact --report-format sarif --report-path reports/gitleaks.sarif --exit-code 1
elif command -v docker >/dev/null 2>&1; then
  echo "[secrets] Running gitleaks through Docker"
  docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:latest git \
    --source /repo \
    --redact \
    --report-format sarif \
    --report-path /repo/reports/gitleaks.sarif \
    --exit-code 1
else
  echo "gitleaks or Docker is required to run the secret scan." >&2
  exit 1
fi

echo "[secrets] Report written to reports/gitleaks.sarif"
