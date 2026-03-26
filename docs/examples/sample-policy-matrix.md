# Sample Policy Matrix

This is a portfolio-friendly snapshot of the policy defined in `docs/security-policy.md`.

## Severity handling

| Severity | Default action | Interview framing |
| --- | --- | --- |
| Low | Warn | Useful for hygiene, not strong enough to block this lab |
| Medium | Warn or review | Worth triage, but not a default release stop here |
| High | Fail | Strong enough to justify a blocked release |
| Critical | Fail | Always blocking |

## Tool-specific gate decisions

| Control | Blocking rule | Tolerated cases |
| --- | --- | --- |
| Ruff | Any lint error | None |
| Pytest | Any test failure | None |
| Coverage | Below 85% | None below threshold |
| Bandit | High severity with medium/high confidence | Medium and low findings are review items |
| Semgrep | Any hit from the curated local rules | Only curated high-signal rules are enabled |
| pip-audit | Any vulnerable package | None |
| Gitleaks | Any committed secret | None |
| Trivy | HIGH or CRITICAL with a fix available | Low/medium findings and unfixed items are tolerated |

## Why this is defendable

- The gates are strict enough to feel real.
- The rules are narrow enough to avoid obvious noise.
- The repo documents both what blocks and what does not block.
