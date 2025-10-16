"""LLM service for AI-powered cataloging."""

import httpx
from typing import Optional, Dict, Any
from pathlib import Path

from app.core.config import settings


class LLMService:
    """Service for interacting with local LLM with vision capabilities."""

    def __init__(self):
        self.api_url = settings.llm_api_url
        self.model = settings.llm_model
        self.enabled = settings.enable_llm

    async def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using vision model.

        Args:
            image_path: Path to the image file
            prompt: Optional prompt for the analysis

        Returns:
            Dict with analysis results including description and tags
        """
        if not self.enabled:
            return {
                "description": "LLM service is disabled",
                "tags": [],
                "confidence": 0.0,
            }

        try:
            # Default prompt for inventory cataloging
            if prompt is None:
                prompt = (
                    "Analyze this image and provide: "
                    "1) A detailed description of the item shown "
                    "2) Suggested category and tags for inventory management "
                    "3) Notable features or condition"
                )

            # Read image file
            image_data = Path(image_path).read_bytes()

            # Call local LLM API (Ollama format)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "images": [image_data.hex()],
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    description = result.get("response", "")

                    # Extract tags from description (simple keyword extraction)
                    tags = self._extract_tags(description)

                    return {
                        "description": description,
                        "tags": tags,
                        "confidence": 0.8,
                    }
                else:
                    return {
                        "description": "Failed to analyze image",
                        "tags": [],
                        "confidence": 0.0,
                    }

        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {
                "description": f"Error: {str(e)}",
                "tags": [],
                "confidence": 0.0,
            }

    def _extract_tags(self, text: str) -> list:
        """Extract relevant tags from text."""
        # Simple keyword extraction - can be enhanced with NLP
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }

        words = text.lower().split()
        tags = [w.strip(".,!?:;") for w in words if w not in common_words and len(w) > 3]

        # Return unique tags, limited to first 10
        return list(dict.fromkeys(tags))[:10]

    async def generate_description(
        self, name: str, existing_description: Optional[str] = None
    ) -> str:
        """
        Generate enhanced description for an item.

        Args:
            name: Item name
            existing_description: Optional existing description

        Returns:
            Enhanced description
        """
        if not self.enabled:
            return existing_description or name

        try:
            prompt = f"Provide a brief, informative description for an inventory item named '{name}'"
            if existing_description:
                prompt += f" with this user description: {existing_description}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", existing_description or name)

        except Exception as e:
            print(f"Error generating description: {e}")

        return existing_description or name


# Singleton instance
llm_service = LLMService()
