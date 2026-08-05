from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": exc.detail, "path": str(request.url)}
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    # exc.errors() is available for Pydantic/validation errors
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "details": exc.errors(), "path": str(request.url)}
    )
