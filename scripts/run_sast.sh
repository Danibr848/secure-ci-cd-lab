#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[sast] Running Bandit against application code"
bandit -r app -lll -ii -f json -o reports/bandit.json

echo "[sast] Running Semgrep with curated blocking rules"
semgrep scan --config .semgrep.yml --error --json --output reports/semgrep.json app tests

echo "[sast] Reports written to reports/"
