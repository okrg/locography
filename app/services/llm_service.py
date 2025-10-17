"""LLM service for AI-powered cataloging using OpenAI-compatible API."""

import httpx
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path

from app.core.config import settings


class LLMService:
    """Service for interacting with local LLM via LM Studio's OpenAI-compatible API."""

    def __init__(self):
        self.api_url = settings.llm_api_url
        self.model = settings.llm_model
        self.api_key = settings.llm_api_key
        self.enabled = settings.enable_llm
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    async def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze an image using vision model via OpenAI-compatible API.

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

            # Read and encode image file as base64
            image_data = Path(image_path).read_bytes()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # Determine image format
            image_format = Path(image_path).suffix.lower().lstrip('.')
            if image_format == 'jpg':
                image_format = 'jpeg'

            # Call LM Studio API using OpenAI format
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/{image_format};base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    description = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    # Extract tags from description (simple keyword extraction)
                    tags = self._extract_tags(description)

                    return {
                        "description": description,
                        "tags": tags,
                        "confidence": 0.8,
                    }
                else:
                    error_detail = response.text
                    print(f"LLM API error: {response.status_code} - {error_detail}")
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
        Generate enhanced description for an item using OpenAI-compatible API.

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
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    description = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return description or existing_description or name

        except Exception as e:
            print(f"Error generating description: {e}")

        return existing_description or name

    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with LLM supporting tool calling.

        Args:
            messages: List of message dictionaries with role and content
            tools: Optional list of tool definitions for function calling

        Returns:
            Dict with response including any tool calls
        """
        if not self.enabled:
            return {
                "content": "LLM service is disabled",
                "tool_calls": None
            }

        try:
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False,
            }
            
            # Add tools if provided
            if tools:
                request_data["tools"] = tools
                request_data["tool_choice"] = "auto"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json=request_data,
                )

                if response.status_code == 200:
                    result = response.json()
                    message = result.get("choices", [{}])[0].get("message", {})
                    
                    return {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls", None)
                    }
                else:
                    error_detail = response.text
                    print(f"LLM API error: {response.status_code} - {error_detail}")
                    return {
                        "content": "Failed to get response",
                        "tool_calls": None
                    }

        except Exception as e:
            print(f"Error in chat_with_tools: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None
            }


# Singleton instance
llm_service = LLMService()
