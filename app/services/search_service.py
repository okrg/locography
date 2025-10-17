"""Search service for text and image-based search."""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.models.image import ItemImage
from app.services.image_service import image_service


class SearchService:
    """Service for searching inventory items."""

    async def search_items(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        location_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Item]:
        """
        Search items by text query and filters.

        Args:
            db: Database session
            query: Text search query
            category_id: Filter by category
            location_id: Filter by location
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of matching items
        """
        stmt = select(Item)

        # Text search in name and description
        if query:
            search_term = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Item.name.ilike(search_term),
                    Item.description.ilike(search_term),
                    Item.ai_description.ilike(search_term),
                )
            )

        # Category filter
        if category_id:
            stmt = stmt.where(Item.category_id == category_id)

        # Location filter
        if location_id:
            stmt = stmt.where(Item.location_id == location_id)

        # Tags filter (if provided)
        # Note: JSON operations vary by database, this is a simple approach
        if tags:
            for tag in tags:
                stmt = stmt.where(func.json_contains(Item.tags, f'"{tag}"'))

        stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def search_by_image(
        self, db: AsyncSession, image_path: str, limit: int = 10, threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search items by visual similarity.

        Args:
            db: Database session
            image_path: Path to query image
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of items with similarity scores
        """
        # Compute embedding for query image
        query_embedding = image_service.compute_image_embedding(image_path)

        if not query_embedding:
            return []

        # Get all items with images
        stmt = select(Item).join(ItemImage).where(ItemImage.embedding.isnot(None))
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        # Compute similarities
        results = []
        for item in items:
            for image in item.images:
                if image.embedding:
                    similarity = image_service.compare_images(query_embedding, image.embedding)

                    if similarity >= threshold:
                        results.append(
                            {
                                "item": item,
                                "similarity": similarity,
                                "matched_image": image,
                            }
                        )

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:limit]


# Singleton instance
search_service = SearchService()
