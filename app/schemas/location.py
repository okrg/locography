"""Location schemas."""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LocationBase(BaseModel):
    """Base location schema."""

    name: str
    description: Optional[str] = None
    location_type: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    z_coord: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    model_url: Optional[str] = None
    parent_id: Optional[int] = None


class LocationCreate(LocationBase):
    """Schema for creating locations."""

    pass


class LocationUpdate(BaseModel):
    """Schema for updating locations."""

    name: Optional[str] = None
    description: Optional[str] = None
    location_type: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    z_coord: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    model_url: Optional[str] = None
    parent_id: Optional[int] = None


class LocationResponse(LocationBase):
    """Schema for location responses."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
