"""API endpoints for item management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.item import Item
from app.models.image import ItemImage
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.services.llm_service import llm_service
from app.services.image_service import image_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new inventory item."""
    db_item = Item(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all inventory items with optional filters."""
    stmt = select(Item)

    if category_id:
        stmt = stmt.where(Item.category_id == category_id)
    if location_id:
        stmt = stmt.where(Item.location_id == location_id)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific item by ID."""
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing item."""
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item."""
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/images")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image for an item with AI analysis."""
    # Check if item exists
    stmt = select(Item).where(Item.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Save image
    file_data = await file.read()
    file_info = await image_service.save_image(file_data, file.filename)

    # Compute embedding
    embedding = image_service.compute_image_embedding(file_info["file_path"])

    # Analyze with LLM
    ai_analysis = await llm_service.analyze_image(file_info["file_path"])

    # Create image record
    db_image = ItemImage(
        item_id=item_id,
        filename=file_info["filename"],
        file_path=file_info["file_path"],
        file_size=file_info.get("file_size"),
        width=file_info.get("width"),
        height=file_info.get("height"),
        format=file_info.get("format"),
        ai_description=ai_analysis.get("description"),
        embedding=embedding,
        is_primary=is_primary,
    )

    db.add(db_image)

    # Update item AI metadata if this is the first/primary image
    if is_primary or not item.ai_description:
        item.ai_description = ai_analysis.get("description")
        item.ai_tags = ai_analysis.get("tags", [])

    await db.commit()
    await db.refresh(db_image)

    return {
        "message": "Image uploaded successfully",
        "image_id": db_image.id,
        "ai_analysis": ai_analysis,
    }
