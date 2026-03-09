from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.user import get_user_by_email

# OAuth2PasswordBearer tells FastAPI: "look for a token in the Authorization header."
# tokenUrl is just for Swagger docs — it points to our login endpoint so the
# interactive docs know where to send credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Role hierarchy — higher index = more permissions.
# We use a list so we can compare roles by their position.
ROLE_HIERARCHY = ["analyst", "admin", "superadmin"]


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that runs before any protected route.

    1. Extracts the JWT from the Authorization header (via oauth2_scheme)
    2. Decodes the token and reads the "sub" claim (the user's email)
    3. Looks up the user in the database
    4. Returns the user object — or raises 401 if anything fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT — this also checks if it's expired
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Look up the user — the token is valid, but does this user still exist?
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    # Stash the user on request.state so the rate limiter can read it.
    # This is how our get_role_limit() function knows the user's role
    # without having to decode the JWT a second time.
    request.state.user = user

    return user


def require_role(minimum_role: str) -> Callable:
    """
    Dependency factory — returns a dependency that checks if the user's role
    is at least `minimum_role` in the hierarchy.

    This is a CLOSURE: the inner function "remembers" `minimum_role` from
    when require_role() was called.

    Usage in a route:
        @router.get("/", dependencies=[Depends(require_role("admin"))])

    Or to also get the user object:
        async def my_route(user: User = Depends(require_role("admin"))):
    """

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.index(user.role)
        required_level = ROLE_HIERARCHY.index(minimum_role)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' does not have sufficient permissions. "
                f"Requires '{minimum_role}' or higher.",
            )
        return user

    return role_checker
