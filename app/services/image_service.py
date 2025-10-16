"""Image processing and embedding service."""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional, List
import json

from app.core.config import settings


class ImageService:
    """Service for image processing and feature extraction."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file_data: bytes, filename: str) -> dict:
        """
        Save uploaded image and extract metadata.

        Args:
            file_data: Image file bytes
            filename: Original filename

        Returns:
            Dict with file info and metadata
        """
        # Generate unique filename
        from datetime import datetime
        import uuid

        ext = Path(filename).suffix
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = self.upload_dir / unique_name

        # Save file
        file_path.write_bytes(file_data)

        # Extract metadata
        try:
            with Image.open(file_path) as img:
                metadata = {
                    "filename": unique_name,
                    "file_path": str(file_path),
                    "file_size": len(file_data),
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                }
        except Exception as e:
            print(f"Error extracting image metadata: {e}")
            metadata = {
                "filename": unique_name,
                "file_path": str(file_path),
                "file_size": len(file_data),
            }

        return metadata

    def compute_image_embedding(self, image_path: str) -> Optional[List[float]]:
        """
        Compute embedding vector for image-based search.

        Args:
            image_path: Path to image file

        Returns:
            Embedding vector as list of floats
        """
        try:
            # Simple feature extraction using image statistics
            # In production, use a proper vision model
            with Image.open(image_path) as img:
                # Convert to RGB and resize
                img = img.convert("RGB")
                img = img.resize((224, 224))

                # Convert to numpy array
                img_array = np.array(img)

                # Compute basic features (color histograms)
                r_hist = np.histogram(img_array[:, :, 0], bins=32, range=(0, 256))[0]
                g_hist = np.histogram(img_array[:, :, 1], bins=32, range=(0, 256))[0]
                b_hist = np.histogram(img_array[:, :, 2], bins=32, range=(0, 256))[0]

                # Normalize and concatenate
                features = np.concatenate([r_hist, g_hist, b_hist])
                features = features / features.sum()

                return features.tolist()

        except Exception as e:
            print(f"Error computing image embedding: {e}")
            return None

    def compare_images(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute similarity between two image embeddings.

        Args:
            embedding1: First image embedding
            embedding2: Second image embedding

        Returns:
            Similarity score (0-1)
        """
        if not embedding1 or not embedding2:
            return 0.0

        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            print(f"Error comparing images: {e}")
            return 0.0


# Singleton instance
image_service = ImageService()
