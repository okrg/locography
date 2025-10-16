"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./locography.db"

    # API
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"

    # LLM Integration
    llm_api_url: Optional[str] = "http://localhost:11434"
    llm_model: str = "llava"
    enable_llm: bool = True

    # Upload settings
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"

    # Location tracking
    enable_location_tracking: bool = False

    # Search settings
    enable_vector_search: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
