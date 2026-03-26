#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[depscan] Verifying installed package metadata"
python -m pip check

echo "[depscan] Auditing Python dependencies"
pip-audit --strict --desc --format json --output reports/pip-audit.json

echo "[depscan] Report written to reports/pip-audit.json"
