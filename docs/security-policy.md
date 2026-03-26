# Security and Quality Policy

## Purpose

This repository is a compact secure CI/CD lab. The policy below defines which checks are informative, which checks are release gates, and why those decisions are credible for a portfolio project.

Use this file together with:

- `README.md` for the high-level project narrative
- `docs/examples/sample-policy-matrix.md` for a GitHub-friendly snapshot
- `.github/workflows/ci.yml` for the executable policy in CI

## Severity matrix

| Severity | Default handling | Explanation |
| --- | --- | --- |
| Low | Warn | Useful for hygiene, not strong enough to block this lab by default |
| Medium | Warn or review | Reviewed in context unless a curated rule is intentionally promoted to blocking |
| High | Fail | Strong enough to justify a release stop in this repository |
| Critical | Fail | Always treated as blocking |

## Pipeline gate matrix

| Control | Tool | Pipeline blocking condition | Tolerated findings or notes |
| --- | --- | --- | --- |
| Code quality | `ruff` | Any lint error blocks | None; the ruleset is intentionally small and high-signal |
| Unit and API testing | `pytest` | Any failing test blocks | None |
| Coverage | `pytest-cov` | Coverage below `85%` blocks | None below threshold |
| SAST | `bandit` | High-severity findings with medium/high confidence block (`-lll -ii`) | Medium/low findings are reviewed but do not block by default |
| SAST | `semgrep` | Any hit from the curated local rules blocks | Only explicitly curated rules are enabled |
| Dependency scan | `pip-audit` | Any known vulnerable runtime package from `requirements.txt` blocks | None; vulnerable runtime dependencies are treated as actionable |
| Secret scan | `gitleaks` | Any detected secret blocks | None; secrets are never tolerated |
| Container scan | `trivy` | `HIGH` or `CRITICAL` vulnerabilities with fixes available block | Low/medium findings are informational; unfixed findings are ignored to reduce noise |

## Tolerance rules

The policy is intentionally simple:

- Low-severity findings are informative unless a tool-specific rule explicitly promotes them.
- Medium findings are reviewed, not ignored, but they do not block this lab by default.
- High and critical findings block when they are produced by a blocking control.
- Hardcoded secrets are never tolerated.
- Container findings without vendor fixes are not used as a blocking criterion because the lab uses `ignore-unfixed: true`.

## Why each control exists

### Ruff

- Keeps obvious correctness issues out of the repo.
- Reinforces that quality gates and security gates belong to the same delivery contract.

### Pytest and coverage

- Covers both the service logic and the HTTP contract.
- The threshold lives in `pytest.ini`, which makes the gate visible and easy to defend in interview discussion.
- Coverage is not presented as proof of quality; it is a minimum confidence signal.

### Bandit

- Focuses on Python-specific insecure coding patterns.
- The repo blocks only on high-severity findings with enough confidence to keep the gate defensible and low-noise.

### Semgrep

- Uses a local `.semgrep.yml` file with a narrow, explainable rule set.
- The rules are intentionally chosen to be easy to discuss:
  - dangerous subprocess usage
  - unsafe YAML loading
  - disabled TLS verification

### pip-audit

- Checks the runtime dependency set declared in `requirements.txt`.
- This keeps the blocking gate focused on shipped application dependencies instead of security tooling dependencies used only in CI.
- The policy is still strict because this repo is meant to show release readiness, not just reporting.

### Gitleaks

- Scans repository history in CI by using `fetch-depth: 0`.
- Runs from the official container image to avoid wrapper-specific licensing friction.
- Detecting one secret is enough to fail the pipeline because secret leakage is an incident, not a soft warning.

### Trivy

- Scans the built image so the gate reflects the shipped artifact, not only the source tree.
- In CI, Trivy runs from the official container image instead of the GitHub Action wrapper to avoid setup fragility and keep behavior close to the local Docker-based workflow.
- Blocks only on `HIGH` and `CRITICAL` vulnerabilities with fixes available.
- Medium and low findings remain useful for backlog hygiene and trend tracking, but they are not release blockers here.

## How to interpret failures

1. Confirm whether the finding is real and reachable.
2. Fix the issue or document a justified risk decision outside the codebase.
3. Re-run the relevant local command.
4. Confirm the result in the generated local summary or in the GitHub Actions summary.

## Limitations

- Static analysis does not prove absence of vulnerabilities.
- Dependency advisories can lag newly disclosed issues.
- Secret scanning does not rotate leaked credentials; it only detects them.
- Container scanning does not replace runtime hardening, signing, or provenance.
- The local scripts assume Bash semantics. On Windows, use Git Bash or WSL for the shell wrappers.

## Educational value

This lab is useful because it lets you explain secure delivery in terms of release criteria instead of listing tools. It is small enough to walk through quickly, but concrete enough to support discussion around QA automation, DevSecOps, product security, and CI/CD policy design.
