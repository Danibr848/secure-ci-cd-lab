# Sample Local Run Output

This is a representative example for GitHub presentation. Exact wording and timing may vary by platform and tool version.

## `make demo`

```text
$ make demo
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
[ci-local] Running Ruff quality gate
All checks passed!
[ci-local] Running pytest suite with coverage gate
.........                                                           [100%]
---------- coverage: platform linux, python 3.11.x ----------
Name                    Stmts   Miss  Cover
-------------------------------------------
app/main.py                46      4    91%
app/schemas.py             43      0   100%
app/service.py             56      3    95%
-------------------------------------------
TOTAL                     145      7    95%
9 passed in 0.91s
[ci-local] Summary written to artifacts/local-controls-summary.md
```

## Generated summary excerpt

```md
| Control | Status | Evidence | Gate behavior |
| --- | --- | --- | --- |
| Ruff quality gate | PASS | `reports/lint.txt` | Blocks on any lint finding |
| Pytest suite | PASS | `reports/pytest.txt`, `reports/junit.xml` | Blocks on any failing unit or API test |
| Coverage gate | PASS | `coverage.xml` | Blocks below 85% |
| Coverage result | 95.0% | `coverage.xml` | Informational representation of the last run |
| SAST controls | NOT RUN | `reports/bandit.json`, `reports/semgrep.json` | Full pipeline blocks on Bandit high findings or curated Semgrep hits |
```

## Why this example exists

The quick demo is intentionally lighter than the full pipeline. It proves that the repository has real executable checks while keeping the live walkthrough fast enough for a recruiter or manager conversation.
