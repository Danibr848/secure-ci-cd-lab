"""Pydantic schemas used by the API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Severity(str, Enum):
    """Severity levels used by the risk model."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthenticationMethod(str, Enum):
    """Supported authentication models."""

    NONE = "none"
    PASSWORD = "password"
    SSO = "sso"
    MFA = "mfa"


class DataClassification(str, Enum):
    """Data classification levels used in the assessment."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class BusinessCriticality(str, Enum):
    """Business criticality levels for the assessed service."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingCount(BaseModel):
    """Open vulnerability counts by severity."""

    model_config = ConfigDict(extra="forbid")

    severity: Severity
    count: int = Field(ge=1, le=50)


class RiskAssessmentRequest(BaseModel):
    """Payload accepted by the /analyze endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    service_name: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$",
        description="Human-readable service identifier.",
    )
    internet_exposed: bool
    handles_pii: bool
    has_waf: bool = False
    authentication: AuthenticationMethod
    data_classification: DataClassification
    business_criticality: BusinessCriticality
    open_findings: list[FindingCount] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def validate_unique_severities(self) -> "RiskAssessmentRequest":
        """Keep finding aggregation deterministic."""
        severities = [finding.severity for finding in self.open_findings]
        if len(severities) != len(set(severities)):
            raise ValueError("open_findings cannot contain duplicate severities")
        return self


class RiskAssessmentResponse(BaseModel):
    """Response returned by the risk analysis endpoint."""

    service_name: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    decision: str
    top_risk_drivers: list[str]
    recommended_actions: list[str]
    max_open_severity: Severity | None = None
    request_id: str | None = None


class HealthResponse(BaseModel):
    """Healthcheck response."""

    status: str
    service: str
    version: str
    request_id: str


class ErrorDetail(BaseModel):
    """Single validation or runtime error detail."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Generic JSON error response."""

    error: str
    message: str
    request_id: str
    details: list[ErrorDetail] = Field(default_factory=list)
