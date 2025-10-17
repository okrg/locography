"""API endpoints for search functionality."""

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.item import ItemResponse
from app.services.search_service import search_service
from app.services.image_service import image_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/items", response_model=List[ItemResponse])
async def search_items(
    q: Optional[str] = Query(None, description="Text search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    location_id: Optional[int] = Query(None, description="Filter by location"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """Search items by text and filters."""
    items = await search_service.search_items(
        db=db, query=q, category_id=category_id, location_id=location_id, tags=tags, limit=limit
    )
    return items


@router.post("/by-image")
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = Query(10, le=50, description="Maximum results"),
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="Similarity threshold"),
    db: AsyncSession = Depends(get_db),
):
    """Search items by visual similarity using an uploaded image."""
    # Save temporary image
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
        file_data = await file.read()
        tmp_file.write(file_data)
        tmp_path = tmp_file.name

    try:
        # Perform visual search
        results = await search_service.search_by_image(
            db=db, image_path=tmp_path, limit=limit, threshold=threshold
        )

        # Format response
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "item": ItemResponse.model_validate(result["item"]),
                    "similarity": result["similarity"],
                    "matched_image_id": result["matched_image"].id,
                }
            )

        return {
            "results": formatted_results,
            "count": len(formatted_results),
        }

    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)
