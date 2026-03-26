#!/usr/bin/env bash
set -uo pipefail

MODE="${1:---full}"
IMAGE_NAME="${IMAGE_NAME:-secure-ci-cd-lab:local}"
COVERAGE_THRESHOLD=85
OVERALL_FAILED=0

LINT_STATUS="not-run"
TEST_STATUS="not-run"
COVERAGE_STATUS="not-run"
COVERAGE_PERCENT="not-available"
SAST_STATUS="not-run"
DEPENDENCY_STATUS="not-run"
SECRETS_STATUS="not-run"
CONTAINER_BUILD_STATUS="not-run"
CONTAINER_SCAN_STATUS="not-run"
FINAL_GATE_RESULT="not-run"
FINAL_GATE_NOTE="No checks executed."

usage() {
  echo "Usage: bash scripts/run_local_checks.sh [--full|--quick]" >&2
  exit 2
}

run_step() {
  local label="$1"
  local status_var="$2"
  local log_file="$3"
  shift 3

  echo "[ci-local] ${label}"
  if "$@" 2>&1 | tee "${log_file}"; then
    printf -v "${status_var}" "%s" "passed"
  else
    printf -v "${status_var}" "%s" "failed"
    OVERALL_FAILED=1
    echo "[ci-local] ${label} failed. See ${log_file}" >&2
  fi
}

capture_coverage() {
  if [[ ! -f coverage.xml ]]; then
    COVERAGE_STATUS="not-available"
    COVERAGE_PERCENT="not-available"
    return
  fi

  local line_rate
  line_rate="$(grep -o 'line-rate="[^"]*"' coverage.xml | head -n 1 | cut -d '"' -f 2 || true)"

  if [[ -z "${line_rate}" ]]; then
    COVERAGE_STATUS="not-available"
    COVERAGE_PERCENT="not-available"
    return
  fi

  COVERAGE_PERCENT="$(awk "BEGIN { printf \"%.1f\", ${line_rate} * 100 }")"
  if awk "BEGIN { exit !(${COVERAGE_PERCENT} >= ${COVERAGE_THRESHOLD}) }"; then
    COVERAGE_STATUS="passed"
  else
    COVERAGE_STATUS="failed"
    OVERALL_FAILED=1
  fi
}

write_status_file() {
  mkdir -p artifacts
  cat > artifacts/local-status.env <<EOF
PIPELINE_MODE='${PIPELINE_MODE}'
GENERATED_AT='$(date -u +'%Y-%m-%d %H:%M:%SZ')'
LINT_STATUS='${LINT_STATUS}'
TEST_STATUS='${TEST_STATUS}'
COVERAGE_STATUS='${COVERAGE_STATUS}'
COVERAGE_PERCENT='${COVERAGE_PERCENT}'
COVERAGE_THRESHOLD='${COVERAGE_THRESHOLD}'
SAST_STATUS='${SAST_STATUS}'
DEPENDENCY_STATUS='${DEPENDENCY_STATUS}'
SECRETS_STATUS='${SECRETS_STATUS}'
CONTAINER_BUILD_STATUS='${CONTAINER_BUILD_STATUS}'
CONTAINER_SCAN_STATUS='${CONTAINER_SCAN_STATUS}'
FINAL_GATE_RESULT='${FINAL_GATE_RESULT}'
FINAL_GATE_NOTE='${FINAL_GATE_NOTE}'
IMAGE_NAME='${IMAGE_NAME}'
EOF
}

case "${MODE}" in
  --full)
    PIPELINE_MODE="local-full"
    ;;
  --quick)
    PIPELINE_MODE="quick-demo"
    ;;
  *)
    usage
    ;;
esac

mkdir -p reports artifacts

run_step "Running Ruff quality gate" LINT_STATUS "reports/lint.txt" ruff check app tests
run_step "Running pytest suite with coverage gate" TEST_STATUS "reports/pytest.txt" pytest --junitxml=reports/junit.xml
capture_coverage

if [[ "${MODE}" == "--full" ]]; then
  run_step "Running SAST controls" SAST_STATUS "reports/sast.txt" bash scripts/run_sast.sh
  run_step "Running dependency scan" DEPENDENCY_STATUS "reports/depscan.txt" bash scripts/run_dependency_scan.sh
  run_step "Running secret scan" SECRETS_STATUS "reports/secrets.txt" bash scripts/run_secret_scan.sh
  run_step "Building container image" CONTAINER_BUILD_STATUS "reports/docker-build.txt" docker build --tag "${IMAGE_NAME}" .

  if [[ "${CONTAINER_BUILD_STATUS}" == "passed" ]]; then
    run_step "Running container scan" CONTAINER_SCAN_STATUS "reports/container-scan.txt" bash scripts/scan_container.sh "${IMAGE_NAME}"
  else
    CONTAINER_SCAN_STATUS="not-run"
  fi
fi

if [[ ${OVERALL_FAILED} -eq 1 ]]; then
  FINAL_GATE_RESULT="failed"
  if [[ "${MODE}" == "--quick" ]]; then
    FINAL_GATE_NOTE="Quick demo checks failed. Review reports and re-run make demo."
  else
    FINAL_GATE_NOTE="One or more local controls failed. Review reports and re-run make ci-local."
  fi
else
  if [[ "${MODE}" == "--quick" ]]; then
    FINAL_GATE_RESULT="partial"
    FINAL_GATE_NOTE="Quick demo passed for executed checks. Run make ci-local for the full local gate."
  else
    FINAL_GATE_RESULT="passed"
    FINAL_GATE_NOTE="All configured local controls passed."
  fi
fi

write_status_file
bash scripts/generate_local_summary.sh artifacts/local-status.env artifacts/local-controls-summary.md >/dev/null
echo "[ci-local] Summary written to artifacts/local-controls-summary.md"

if [[ ${OVERALL_FAILED} -eq 1 ]]; then
  exit 1
fi
