#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

echo "[depscan] Verifying installed package metadata"
python -m pip check

echo "[depscan] Auditing runtime Python dependencies from requirements.txt"
pip-audit --strict --desc --format json -o reports/pip-audit.json -r requirements.txt

echo "[depscan] Report written to reports/pip-audit.json"
