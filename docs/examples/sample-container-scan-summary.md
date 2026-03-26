# Sample Container Scan Summary

This is a representative Trivy summary for portfolio presentation.

## Gate policy

- Block on `HIGH` and `CRITICAL` vulnerabilities with fixes available
- Ignore unfixed vulnerabilities to reduce base-image noise
- Keep `LOW` and `MEDIUM` findings as backlog hygiene, not release blockers

## Example output

```text
$ trivy image --severity HIGH,CRITICAL --ignore-unfixed secure-ci-cd-lab:local
2026-03-26T09:42:10Z    INFO    Vulnerability scanning is enabled
2026-03-26T09:42:12Z    INFO    Detected OS: debian 12.7 (bookworm)
2026-03-26T09:42:12Z    INFO    Number of language-specific files: 1

secure-ci-cd-lab:local (debian 12.7/bookworm)
==============================================
Total: 0 (HIGH: 0, CRITICAL: 0)
```

## Example interpretation

| Dimension | Result |
| --- | --- |
| Gate result | PASS |
| Reason | No HIGH or CRITICAL vulnerabilities with fixes available were found |
| Tolerated findings | Low/medium issues may still exist and should be reviewed separately |
| Interview angle | The repo scans the built artifact, not only source dependencies |
