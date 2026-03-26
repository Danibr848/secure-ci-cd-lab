"""API endpoint tests."""

from __future__ import annotations

from app import main


def valid_payload() -> dict:
    return {
        "service_name": "payments-api",
        "internet_exposed": True,
        "handles_pii": True,
        "has_waf": False,
        "authentication": "sso",
        "data_classification": "confidential",
        "business_criticality": "high",
        "open_findings": [
            {"severity": "medium", "count": 2},
            {"severity": "high", "count": 1},
        ],
    }


def test_analyze_endpoint_returns_structured_response(client) -> None:
    response = client.post("/analyze", json=valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["service_name"] == "payments-api"
    assert body["risk_level"] == "critical"
    assert body["decision"] == "block-release"
    assert body["risk_score"] >= 75
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["recommended_actions"]


def test_analyze_endpoint_rejects_invalid_payload(client) -> None:
    payload = valid_payload()
    payload["service_name"] = "!"

    response = client.post("/analyze", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert any("service_name" in item["field"] for item in body["details"])


def test_analyze_endpoint_rejects_duplicate_severity_entries(client) -> None:
    payload = valid_payload()
    payload["open_findings"] = [
        {"severity": "high", "count": 1},
        {"severity": "high", "count": 3},
    ]

    response = client.post("/analyze", json=payload)

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_analyze_endpoint_returns_sanitized_internal_error(client, monkeypatch) -> None:
    def fail(_payload):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(main, "calculate_risk_assessment", fail)

    response = client.post("/analyze", json=valid_payload())

    assert response.status_code == 500
    assert response.json()["error"] == "internal_server_error"
