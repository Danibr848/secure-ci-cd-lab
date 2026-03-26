# Sample CI Summary

This is a representative example of the Markdown summary produced by the GitHub Actions `summary` job.

```md
## Pipeline controls at a glance

| Control | Result | Blocking policy |
| --- | --- | --- |
| Tests and coverage | success | Test failures, Ruff findings, or coverage below 85% block the run |
| SAST | success | Bandit high-severity findings or curated Semgrep rule hits block the run |
| Dependency scan | success | Known vulnerable packages block the run |
| Secret scan | success | Any detected secret blocks the run |
| Container security | success | Trivy HIGH/CRITICAL findings with fixes available block the run |
```

## Talking point

This summary is useful in GitHub because it turns a multi-job pipeline into a one-screen decision view. A reviewer can understand the release contract without opening each job log.
