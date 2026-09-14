"""Compute request/response models — the API's public contract."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InstanceRequest(BaseModel):
    """Body for actions that operate on one instance."""

    instance_id: str = Field(min_length=1, description="Provider instance identifier")


class InstanceResponse(BaseModel):
    """Normalised result of a compute action.

    Deliberately provider-neutral: every adapter returns this shape, so swapping
    BytePlus for AWS changes nothing downstream.
    """

    instance_id: str
    status: str


class InstanceListResponse(BaseModel):
    instances: list[InstanceResponse]
