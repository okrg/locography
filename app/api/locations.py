"""API endpoints for location management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new storage location."""
    db_location = Location(**location.model_dump())
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location


@router.get("/", response_model=List[LocationResponse])
async def list_locations(
    skip: int = 0,
    limit: int = 100,
    location_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all storage locations."""
    stmt = select(Location)

    if location_type:
        stmt = stmt.where(Location.location_type == location_type)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific location by ID."""
    stmt = select(Location).where(Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    return location


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int, location_update: LocationUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing location."""
    stmt = select(Location).where(Location.id == location_id)
    result = await db.execute(stmt)
    db_location = result.scalar_one_or_none()

    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Update fields
    update_data = location_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)

    await db.commit()
    await db.refresh(db_location)
    return db_location


@router.delete("/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a location."""
    stmt = select(Location).where(Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    await db.delete(location)
    await db.commit()
    return {"message": "Location deleted successfully"}
