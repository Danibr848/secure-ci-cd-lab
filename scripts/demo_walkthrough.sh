#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
============================================================
secure-ci-cd-lab :: guided demo walkthrough
============================================================
This walkthrough is designed for a 2-3 minute portfolio demo.

It runs the fastest high-signal local checks:
- Ruff lint to show quality as a gate
- Pytest with the coverage threshold enabled
- Markdown summary generation for easy sharing

It does not run the heavier scans by default.
Use `make ci-local` for the full local pipeline.
EOF

if bash scripts/run_local_checks.sh --quick; then
  RESULT=0
else
  RESULT=$?
fi

if [[ -f artifacts/local-controls-summary.md ]]; then
  echo
  echo "Summary excerpt:"
  head -n 18 artifacts/local-controls-summary.md
fi

cat <<'EOF'

Open these files next during the demo:
- README.md
- .github/workflows/ci.yml
- docs/security-policy.md
- artifacts/local-controls-summary.md
- docs/examples/sample-ci-summary.md
- docs/portfolio-notes.md
EOF

exit "${RESULT}"
