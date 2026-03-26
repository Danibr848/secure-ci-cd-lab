"""Unit tests for the service scoring logic."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import RiskAssessmentRequest
from app.service import calculate_risk_assessment


def build_request(**overrides) -> RiskAssessmentRequest:
    payload = {
        "service_name": "billing-api",
        "internet_exposed": True,
        "handles_pii": True,
        "has_waf": True,
        "authentication": "sso",
        "data_classification": "confidential",
        "business_criticality": "medium",
        "open_findings": [{"severity": "medium", "count": 2}],
    }
    payload.update(overrides)
    return RiskAssessmentRequest.model_validate(payload)


def test_service_blocks_release_for_critical_risk() -> None:
    assessment = calculate_risk_assessment(
        build_request(
            has_waf=False,
            authentication="password",
            data_classification="restricted",
            business_criticality="high",
            open_findings=[
                {"severity": "critical", "count": 1},
                {"severity": "high", "count": 2},
            ],
        )
    )

    assert assessment.risk_level == "critical"
    assert assessment.decision == "block-release"
    assert assessment.risk_score >= 75
    assert "High or critical findings remain open" in assessment.top_risk_drivers


def test_service_accepts_low_risk_payload() -> None:
    assessment = calculate_risk_assessment(
        build_request(
            service_name="internal-tool",
            internet_exposed=False,
            handles_pii=False,
            has_waf=False,
            authentication="mfa",
            data_classification="public",
            business_criticality="low",
            open_findings=[],
        )
    )

    assert assessment.risk_level == "low"
    assert assessment.decision == "accept"
    assert assessment.risk_score < 25
    assert assessment.max_open_severity is None


def test_score_is_capped_at_one_hundred() -> None:
    assessment = calculate_risk_assessment(
        build_request(
            has_waf=False,
            authentication="none",
            data_classification="restricted",
            business_criticality="high",
            open_findings=[
                {"severity": "critical", "count": 50},
                {"severity": "high", "count": 50},
            ],
        )
    )

    assert assessment.risk_score == 100


def test_request_rejects_duplicate_severity_entries() -> None:
    with pytest.raises(ValidationError):
        build_request(
            open_findings=[
                {"severity": "high", "count": 1},
                {"severity": "high", "count": 2},
            ]
        )
