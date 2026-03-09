from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter
from app.routers import accounts, alerts, auth

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Ingest and query fraud alerts",
    debug=settings.DEBUG,
)

# ── Rate Limiting ────────────────────────────────────────────────
# 1. Attach the limiter to app.state so slowapi can access it from
#    inside request handlers (it looks for request.app.state.limiter).
app.state.limiter = limiter

# 2. Register an error handler: when a user exceeds their rate limit,
#    slowapi raises RateLimitExceeded. This handler converts that into
#    a proper 429 HTTP response with a "Retry-After" header.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Simple health check — returns OK if the server is running."""
    return {"status": "healthy"}
