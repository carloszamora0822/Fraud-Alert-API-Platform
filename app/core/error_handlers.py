"""
Global exception handlers that convert exceptions into RFC 7807
Problem Details JSON responses.

Registered on the FastAPI app in main.py. When any of our custom
exceptions (or an unhandled error) occurs, these handlers intercept
it and return a consistent JSON body with Content-Type
'application/problem+json'.
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import ProblemDetailError


def _problem_response(
    status: int,
    type_uri: str,
    title: str,
    detail: str,
    instance: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Build a RFC 7807 JSONResponse with the right content type."""
    return JSONResponse(
        status_code=status,
        content={
            "type": type_uri,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
        },
        headers=headers,
        media_type="application/problem+json",
    )


async def problem_detail_handler(
    request: Request, exc: ProblemDetailError
) -> JSONResponse:
    """Catch any of our custom ProblemDetailError subclasses."""
    headers = getattr(exc, "headers", None)
    return _problem_response(
        status=exc.status,
        type_uri=exc.type_uri,
        title=exc.title,
        detail=exc.detail,
        instance=request.url.path,
        headers=headers,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Catch Pydantic validation errors (bad request body, wrong types, etc.)
    and format them as RFC 7807.

    FastAPI normally returns 422 with its own format. We override that
    to keep all errors consistent.
    """
    return _problem_response(
        status=422,
        type_uri="/errors/validation",
        title="Validation Error",
        detail=str(exc.errors()),
        instance=request.url.path,
    )


async def catch_all_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Safety net — any unhandled exception becomes a 500 with no
    internal details leaked. In production you'd log exc here.
    """
    return _problem_response(
        status=500,
        type_uri="/errors/internal",
        title="Internal Server Error",
        detail="An unexpected error occurred",
        instance=request.url.path,
    )
