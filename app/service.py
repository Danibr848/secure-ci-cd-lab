"""Business logic for the risk assessment API."""

from __future__ import annotations

from app.schemas import (
    AuthenticationMethod,
    BusinessCriticality,
    DataClassification,
    FindingCount,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    Severity,
)


BASE_SCORE = 10
FINDING_WEIGHTS = {
    Severity.LOW: 1,
    Severity.MEDIUM: 4,
    Severity.HIGH: 8,
    Severity.CRITICAL: 15,
}
AUTH_WEIGHTS = {
    AuthenticationMethod.NONE: 20,
    AuthenticationMethod.PASSWORD: 10,
    AuthenticationMethod.SSO: 4,
    AuthenticationMethod.MFA: 0,
}
DATA_CLASSIFICATION_WEIGHTS = {
    DataClassification.PUBLIC: 0,
    DataClassification.INTERNAL: 5,
    DataClassification.CONFIDENTIAL: 15,
    DataClassification.RESTRICTED: 25,
}
BUSINESS_CRITICALITY_WEIGHTS = {
    BusinessCriticality.LOW: 0,
    BusinessCriticality.MEDIUM: 5,
    BusinessCriticality.HIGH: 10,
}
SEVERITY_ORDER = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]


def calculate_risk_assessment(
    payload: RiskAssessmentRequest,
) -> RiskAssessmentResponse:
    """Calculate a bounded risk score and decision for a service."""
    score = BASE_SCORE
    risk_drivers: list[str] = []
    actions: list[str] = []

    if payload.internet_exposed:
        score += 20
        risk_drivers.append("Service is internet exposed")
    if payload.handles_pii:
        score += 15
        risk_drivers.append("Service processes personal or sensitive data")
        actions.append("Verify encryption, retention, and access logging for PII workflows.")

    score += AUTH_WEIGHTS[payload.authentication]
    if payload.authentication in {AuthenticationMethod.NONE, AuthenticationMethod.PASSWORD}:
        risk_drivers.append("Authentication strength is below a strong federated baseline")
        actions.append("Require stronger authentication such as SSO with MFA for privileged access.")

    score += DATA_CLASSIFICATION_WEIGHTS[payload.data_classification]
    if payload.data_classification in {
        DataClassification.CONFIDENTIAL,
        DataClassification.RESTRICTED,
    }:
        risk_drivers.append("Data classification increases breach impact")

    score += BUSINESS_CRITICALITY_WEIGHTS[payload.business_criticality]
    if payload.business_criticality is BusinessCriticality.HIGH:
        risk_drivers.append("Service has high business criticality")

    if payload.internet_exposed and not payload.has_waf:
        score += 10
        risk_drivers.append("Internet-facing service is not behind a WAF or API gateway")
        actions.append("Place the service behind a WAF or hardened API gateway before release.")

    finding_score, max_open_severity = _score_findings(payload.open_findings)
    score += finding_score

    if max_open_severity in {Severity.HIGH, Severity.CRITICAL}:
        risk_drivers.append("High or critical findings remain open")
        actions.append("Remediate or formally accept high-severity findings before release.")

    if payload.internet_exposed and max_open_severity in {Severity.HIGH, Severity.CRITICAL}:
        score += 5
        risk_drivers.append("Open severe findings are amplified by internet exposure")

    score = min(score, 100)
    risk_level = _classify_risk(score)
    decision = _decision_for_level(risk_level)

    if decision == "block-release":
        actions.append("Block release until mitigations are implemented and the pipeline is green.")
    elif decision == "review-required":
        actions.append("Route the change through a product security or release readiness review.")
    else:
        actions.append("Continue with standard monitoring and keep dependency hygiene current.")

    return RiskAssessmentResponse(
        service_name=payload.service_name,
        risk_score=score,
        risk_level=risk_level,
        decision=decision,
        top_risk_drivers=_top_entries(risk_drivers),
        recommended_actions=_top_entries(actions, limit=4),
        max_open_severity=max_open_severity,
    )


def _score_findings(open_findings: list[FindingCount]) -> tuple[int, Severity | None]:
    """Convert open vulnerability counts into a bounded score."""
    if not open_findings:
        return 0, None

    total_score = 0
    highest_severity: Severity | None = None

    for severity in SEVERITY_ORDER:
        matching = next((item for item in open_findings if item.severity is severity), None)
        if not matching:
            continue
        if highest_severity is None:
            highest_severity = matching.severity
        total_score += FINDING_WEIGHTS[matching.severity] * matching.count

    return min(total_score, 35), highest_severity


def _classify_risk(score: int) -> str:
    """Map a numeric score to a discrete level."""
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def _decision_for_level(risk_level: str) -> str:
    """Convert a risk level into a release decision."""
    decisions = {
        "low": "accept",
        "medium": "accept-with-monitoring",
        "high": "review-required",
        "critical": "block-release",
    }
    return decisions[risk_level]


def _top_entries(items: list[str], limit: int = 3) -> list[str]:
    """Return the first unique entries up to the configured limit."""
    ordered_unique: list[str] = []
    for item in items:
        if item not in ordered_unique:
            ordered_unique.append(item)
    return ordered_unique[:limit]
