from pydantic import BaseModel, Field

class InstanceRequest(BaseModel):
instance_id: str = Field(min_length=1)

class InstanceResponse(BaseModel):
instance_id: str
status: str
