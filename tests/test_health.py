"""Health endpoint tests."""

from __future__ import annotations


def test_health_endpoint_returns_service_status(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.json() == {
        "status": "ok",
        "service": "secure-ci-cd-lab",
        "version": "1.0.0",
        "request_id": response.headers["X-Request-ID"],
    }
