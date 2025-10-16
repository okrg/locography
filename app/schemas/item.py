"""Item schemas."""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ItemBase(BaseModel):
    """Base item schema."""

    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity: int = 1
    unit: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: str = "USD"
    tags: Optional[List[str]] = None


class ItemCreate(ItemBase):
    """Schema for creating items."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating items."""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    tags: Optional[List[str]] = None


class ItemResponse(ItemBase):
    """Schema for item responses."""

    id: int
    ai_description: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    model_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
