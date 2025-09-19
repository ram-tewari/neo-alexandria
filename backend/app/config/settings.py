"""
Neo Alexandria 2.0 - Application Configuration

This module provides centralized configuration management using Pydantic Settings.
It handles environment variables, default values, and configuration validation.

Related files:
- app/database/base.py: Uses DATABASE_URL for database connection
- app/services/quality_service.py: Uses MIN_QUALITY_THRESHOLD for quality scoring
- .env: Environment variables file (optional)
- alembic.ini: Database migration configuration

Configuration includes:
- Database connection settings
- Environment-specific settings (dev/staging/prod)
- Quality control thresholds
- Backup and timezone preferences
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings for configuration management.
    
    Provides type-safe configuration with environment variable support and
    sensible defaults for development and production environments.
    """
    
    DATABASE_URL: str = "sqlite:///./backend.db"
    ENV: Literal["dev", "staging", "prod"] = "dev"
    MIN_QUALITY_THRESHOLD: float = 0.7
    BACKUP_FREQUENCY: Literal["daily", "weekly", "monthly"] = "weekly"
    TIMEZONE: str = "UTC"
    
    # Vector embedding configuration for Phase 4
    EMBEDDING_MODEL_NAME: str = "nomic-ai/nomic-embed-text-v1"
    DEFAULT_HYBRID_SEARCH_WEIGHT: float = 0.5  # 0.0=keyword only, 1.0=semantic only
    EMBEDDING_CACHE_SIZE: int = 1000  # for model caching if needed
    
    # Graph configuration for Phase 5 - Hybrid Knowledge Graph
    DEFAULT_GRAPH_NEIGHBORS: int = 7
    GRAPH_OVERVIEW_MAX_EDGES: int = 50
    GRAPH_WEIGHT_VECTOR: float = 0.6
    GRAPH_WEIGHT_TAGS: float = 0.3
    GRAPH_WEIGHT_CLASSIFICATION: float = 0.1
    GRAPH_VECTOR_MIN_SIM_THRESHOLD: float = 0.85  # for overview candidate pruning

    # Phase 5.5 - Personalized Recommendation Engine
    RECOMMENDATION_PROFILE_SIZE: int = 50
    RECOMMENDATION_KEYWORD_COUNT: int = 5
    RECOMMENDATION_CANDIDATES_PER_KEYWORD: int = 10
    SEARCH_PROVIDER: str = "ddgs"  # currently supports only ddgs
    SEARCH_TIMEOUT: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns a singleton Settings instance that is cached for the lifetime
    of the application. This ensures consistent configuration across all
    modules and avoids repeated environment variable parsing.
    
    Returns:
        Settings: Cached configuration instance
    """
    settings = Settings()
    
    # Validate graph weights sum to 1.0
    total_weight = settings.GRAPH_WEIGHT_VECTOR + settings.GRAPH_WEIGHT_TAGS + settings.GRAPH_WEIGHT_CLASSIFICATION
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(f"Graph weights must sum to 1.0, got {total_weight}")
    
    return settings
