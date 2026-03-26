"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """Return a test client for API tests."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
