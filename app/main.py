"""FastAPI entrypoint for the secure CI/CD lab application."""

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import __version__
from app.logging_utils import configure_logging, get_logger
from app.schemas import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
)
from app.service import calculate_risk_assessment


configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Secure CI/CD Lab API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def attach_request_context(request: Request, call_next):
    """Attach a request identifier to responses and logs."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health(request: Request) -> HealthResponse:
    """Basic liveness endpoint used by CI and container checks."""
    return HealthResponse(
        status="ok",
        service="secure-ci-cd-lab",
        version=__version__,
        request_id=request.state.request_id,
    )


@app.post("/analyze", response_model=RiskAssessmentResponse, tags=["analysis"])
async def analyze(
    payload: RiskAssessmentRequest,
    request: Request,
) -> RiskAssessmentResponse:
    """Return a simple, explainable release risk assessment."""
    response = calculate_risk_assessment(payload)
    response.request_id = request.state.request_id

    logger.info(
        "Risk assessment completed for %s with decision=%s score=%s",
        payload.service_name,
        response.decision,
        response.risk_score,
    )
    return response


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return a structured validation response."""
    request_id = getattr(request.state, "request_id", "unknown")
    details = [
        ErrorDetail(
            field=".".join(str(value) for value in error["loc"][1:]),
            message=error["msg"],
        )
        for error in exc.errors()
    ]

    logger.warning(
        "Validation failed for path=%s request_id=%s",
        request.url.path,
        request_id,
    )
    body = ErrorResponse(
        error="validation_error",
        message="Request payload validation failed.",
        request_id=request_id,
        details=details,
    )
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Return a generic error without leaking internals."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        "Unhandled error for path=%s request_id=%s",
        request.url.path,
        request_id,
    )

    body = ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred.",
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump())
