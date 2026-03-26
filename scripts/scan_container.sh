#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-secure-ci-cd-lab:local}"

mkdir -p reports

if command -v trivy >/dev/null 2>&1; then
  echo "[container] Generating Trivy JSON report for ${IMAGE_NAME}"
  trivy image --severity HIGH,CRITICAL --ignore-unfixed --format json --output reports/trivy-image.json "${IMAGE_NAME}"

  echo "[container] Enforcing Trivy gate for ${IMAGE_NAME}"
  trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 "${IMAGE_NAME}"
elif command -v docker >/dev/null 2>&1; then
  echo "[container] Running Trivy through Docker for ${IMAGE_NAME}"
  docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD:/workspace" \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --ignore-unfixed --format json \
    --output /workspace/reports/trivy-image.json "${IMAGE_NAME}"

  docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 "${IMAGE_NAME}"
else
  echo "Trivy or Docker is required to run the container scan." >&2
  exit 1
fi

echo "[container] Report written to reports/trivy-image.json"
