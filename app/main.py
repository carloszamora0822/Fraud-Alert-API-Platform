from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.error_handlers import (
    catch_all_handler,
    problem_detail_handler,
    validation_error_handler,
)
from app.core.exceptions import ProblemDetailError
from app.core.rate_limit import limiter
from app.routers import accounts, alerts, auth

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Ingest and query fraud alerts",
    debug=settings.DEBUG,
)

# ── Error Handling (RFC 7807) ────────────────────────────────────
# Order matters: more specific handlers first.
# Our custom exceptions → Problem Details JSON
app.add_exception_handler(ProblemDetailError, problem_detail_handler)
# Pydantic validation errors (bad request bodies) → Problem Details JSON
app.add_exception_handler(RequestValidationError, validation_error_handler)
# Catch-all for unhandled exceptions → generic 500 Problem Details
app.add_exception_handler(Exception, catch_all_handler)

# ── Rate Limiting ────────────────────────────────────────────────
# Attach the limiter to app.state so slowapi can access it from
# inside request handlers (it looks for request.app.state.limiter).
app.state.limiter = limiter

# When a user exceeds their rate limit, slowapi raises RateLimitExceeded.
# This handler converts that into a proper 429 HTTP response.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Simple health check — returns OK if the server is running."""
    return {"status": "healthy"}
