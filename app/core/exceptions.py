class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, detail: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)

class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found: {resource_id}",
            status_code=404
        )

class ValidationError(AppException):
    def __init__(self, message: str, detail: dict | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            detail=detail
        )

class AuthorizationError(AppException):
    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401
        )

class RateLimitError(AppException):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            code="RATE_LIMITED",
            message=f"Too many requests. Retry after {retry_after}s",
            status_code=429,
            detail={"retry_after": retry_after}
        )
