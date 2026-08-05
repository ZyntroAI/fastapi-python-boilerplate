from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# --- Optimized for ORM-to-Schema Conversion ---
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Fast ORM mapping
