# app/core/exceptions.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status


@dataclass(frozen=True)
class ErrorInfo:
    code: str
    message: str
    detail: Optional[Any] = None


class AppError(Exception):
    """
    Base application error that carries an HTTP status and a stable error code.
    """
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        detail: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error = ErrorInfo(code=code, message=message, detail=detail)


class BadRequest(AppError):
    def __init__(self, message: str = "Bad request", *, code: str = "bad_request", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, code=code, message=message, detail=detail)


class Unauthorized(AppError):
    def __init__(self, message: str = "Unauthorized", *, code: str = "unauthorized", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code=code, message=message, detail=detail)


class Forbidden(AppError):
    def __init__(self, message: str = "Forbidden", *, code: str = "forbidden", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code=code, message=message, detail=detail)


class NotFound(AppError):
    def __init__(self, message: str = "Not found", *, code: str = "not_found", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message, detail=detail)


class Conflict(AppError):
    def __init__(self, message: str = "Conflict", *, code: str = "conflict", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, code=code, message=message, detail=detail)


class UnprocessableEntity(AppError):
    def __init__(
        self,
        message: str = "Unprocessable entity",
        *,
        code: str = "unprocessable_entity",
        detail: Optional[Any] = None,
    ):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code=code, message=message, detail=detail)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error", *, code: str = "internal_error", detail: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, code=code, message=message, detail=detail)


def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Central handler for AppError.
    """
    err = exc.error
    payload: dict[str, Any] = {
        "error": {
            "code": err.code,
            "message": err.message,
        }
    }
    if err.detail is not None:
        payload["error"]["detail"] = err.detail

    # Optional: include a request id header if you set one elsewhere
    request_id = request.headers.get("x-request-id")
    if request_id:
        payload["request_id"] = request_id

    return JSONResponse(status_code=exc.status_code, content=payload)
