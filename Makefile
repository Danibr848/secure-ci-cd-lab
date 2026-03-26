SHELL := bash
PYTHON ?= python
IMAGE_NAME ?= secure-ci-cd-lab:local

.PHONY: install run test coverage lint sast secrets depscan docker-build docker-scan ci-local demo summary-local

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

coverage:
	pytest --cov-report=html

lint:
	ruff check app tests

sast:
	bash scripts/run_sast.sh

secrets:
	bash scripts/run_secret_scan.sh

depscan:
	bash scripts/run_dependency_scan.sh

docker-build:
	docker build --tag $(IMAGE_NAME) .

docker-scan:
	bash scripts/scan_container.sh $(IMAGE_NAME)

ci-local:
	bash scripts/run_local_checks.sh --full

demo:
	bash scripts/demo_walkthrough.sh

summary-local:
	bash scripts/generate_local_summary.sh
