"""Shared application exceptions mapped to HTTP responses.

Registered in the FastAPI app so domain errors (not found, conflict, forbidden)
return consistent JSON instead of a bare 500.
"""
from __future__ import annotations


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str, *, detail: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail or {}

    def to_response(self) -> dict:
        return {"code": self.code, "message": self.message, **self.detail}


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
