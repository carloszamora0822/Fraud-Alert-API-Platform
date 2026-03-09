"""
Rate limiting configuration using slowapi.

slowapi wraps the `limits` library and integrates it with FastAPI.
It tracks how many requests each client makes, and returns a 429 status
code ("Too Many Requests") when they exceed their allowed rate.

Key concept — **rate limit key function**:
slowapi needs a way to identify *who* is making the request so it can
count requests per user. By default it uses the client's IP address,
but we override this to use the user's email from their JWT token.
This way, rate limits follow the *user*, not the IP.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import settings


def _get_rate_limit_key(request: Request) -> str:
    """
    Extract a unique key to identify the requester.

    - If the user is authenticated (their info is stored in request.state
      by a dependency), we use their email as the key.
    - If not (e.g., unauthenticated endpoints like /health), we fall back
      to the client's IP address.
    """
    # request.state is a bag where FastAPI/Starlette lets you stash data
    # that travels with the request. We'll set "user" on it in our dependency.
    user = getattr(request.state, "user", None)
    if user is not None:
        return user.email
    return get_remote_address(request)


def get_role_limit(request: Request) -> str:
    """
    Dynamic rate limit — returns a different limit string depending on
    the user's role.

    slowapi calls this function for each request to determine which
    limit applies. This is how we give admins 10x the quota of analysts.
    """
    user = getattr(request.state, "user", None)
    if user is not None and user.role in ("admin", "superadmin"):
        return settings.RATE_LIMIT_ADMIN
    return settings.RATE_LIMIT_ANALYST


# Create the global Limiter instance.
# - key_func: how to identify the requester (our custom function)
# - default_limits: applied to routes that DON'T have an explicit @limiter.limit()
# - storage_uri: "memory://" means counts are stored in-process RAM.
#   In production with multiple servers, you'd use Redis instead so all
#   servers share the same counters.
limiter = Limiter(
    key_func=_get_rate_limit_key,
    default_limits=[settings.RATE_LIMIT_ANALYST],
    storage_uri="memory://",
)
