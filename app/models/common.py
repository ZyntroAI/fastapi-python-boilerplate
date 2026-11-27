from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime

T = TypeVar("T")

class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation successful"

class DataResponse(BaseResponse, Generic[T]):
    data: Optional[T] = None

class ListResponse(BaseResponse, Generic[T]):
    data: list[T]
    total: int
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    detail: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
