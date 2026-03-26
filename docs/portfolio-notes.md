# Portfolio Notes

## CV bullets

- Built a portfolio-grade FastAPI service and secure GitHub Actions pipeline that combines testing, coverage enforcement, SAST, dependency auditing, secret scanning, and container image scanning.
- Defined and documented explicit quality and security gates, including coverage thresholds, curated blocking rules, and artifact-based image security policy.
- Created local demo and reporting workflows that make CI/CD security controls easy to explain to recruiters, hiring managers, and technical interviewers.

## Interview angles

### 1. QA Automation plus DevSecOps

This project shows that I do not treat automated testing and security scanning as separate concerns. I designed the repository so both contribute to the same release decision.

### 2. Policy-driven secure delivery

The key value is not the tool list. The key value is the release policy: what blocks, what is tolerated, and why that tradeoff is credible for a small but real delivery pipeline.

### 3. Portfolio design for technical audiences

I optimized the repository so a reviewer can understand it quickly in GitHub, run a short local demo, and still find deeper documentation when they want to assess engineering judgment.

## Short LinkedIn summary

Built `secure-ci-cd-lab`, a compact portfolio project that demonstrates secure CI/CD in practice with FastAPI, pytest, coverage gates, SAST, dependency scanning, secret scanning, container image scanning, and documented release policy gates in GitHub Actions.

## Longer GitHub profile README summary

`secure-ci-cd-lab` is a small but serious secure delivery laboratory built to show how QA automation, product security, and CI/CD engineering fit together. The repository includes a FastAPI service, unit and API tests, coverage enforcement, Bandit and Semgrep SAST checks, pip-audit dependency scanning, Gitleaks secret scanning, Trivy container scanning, Dependabot configuration, and policy documentation that explains exactly when a pipeline should block a release.
