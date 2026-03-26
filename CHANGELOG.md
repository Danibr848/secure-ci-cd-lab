# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.0] - 2026-03-26

### Added

- FastAPI application with `/health` and `/analyze` endpoints, input validation, structured responses, logging, and controlled error handling.
- Unit and API test suite with coverage enforcement through `pytest` and `pytest-cov`.
- Docker packaging for local execution and container-based security scanning.
- GitHub Actions workflow covering tests, linting, SAST, dependency scanning, secret scanning, container security, and pipeline summary output.
- Dependabot configuration for Python dependencies and GitHub Actions updates.

### Security

- Bandit and Semgrep SAST controls with blocking behavior aligned to a documented policy.
- pip-audit dependency scanning, Gitleaks secret scanning, and Trivy image scanning with explicit fail conditions.
- Security policy documentation that defines severity handling, tolerated findings, and gate rationale.

### Documentation

- Portfolio-oriented README with demo guidance, interview framing, and representative output examples.
- Static example outputs under `docs/examples/` to improve GitHub presentation.
- Portfolio notes for CV, LinkedIn, interview discussion, and GitHub profile usage.
- Local summary and guided demo scripts to improve live walkthrough experience.
