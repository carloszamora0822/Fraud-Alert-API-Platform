"""
Custom exception classes that carry RFC 7807 Problem Details fields.

Instead of raising bare HTTPException(status_code=404, detail="..."),
we raise specific exceptions like NotFoundError("Alert", alert_id).
Each one knows its own status code, type URI, and title — so the
error handler can format them all identically.
"""


class ProblemDetailError(Exception):
    """
    Base class for all API errors.

    Every subclass sets its own status, type, and title.
    The 'detail' field is instance-specific (passed at raise time).
    """

    status: int = 500
    type_uri: str = "/errors/internal"
    title: str = "Internal Server Error"

    def __init__(self, detail: str = "An unexpected error occurred") -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(ProblemDetailError):
    status = 404
    type_uri = "/errors/not-found"
    title = "Not Found"

    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(f"{resource} with id '{resource_id}' not found")


class ConflictError(ProblemDetailError):
    status = 409
    type_uri = "/errors/conflict"
    title = "Conflict"

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail)


class AuthenticationError(ProblemDetailError):
    status = 401
    type_uri = "/errors/unauthorized"
    title = "Unauthorized"

    def __init__(self, detail: str = "Invalid or expired credentials") -> None:
        self.headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(detail)


class ForbiddenError(ProblemDetailError):
    status = 403
    type_uri = "/errors/forbidden"
    title = "Forbidden"

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail)
