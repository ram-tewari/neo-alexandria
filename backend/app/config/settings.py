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

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings using Pydantic Settings for configuration management.

    Provides type-safe configuration with environment variable support and
    sensible defaults for development and production environments.
    """

    DATABASE_URL: str = "sqlite:///./backend.db"
    TEST_DATABASE_URL: str | None = None  # Optional test database URL
    ENV: Literal["dev", "staging", "prod"] = "dev"
    
    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = "http://localhost:5173"

    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "devpassword"
    POSTGRES_DB: str = "neo_alexandria_dev"
    POSTGRES_PORT: int = 5432

    # JWT Authentication
    JWT_SECRET_KEY: SecretStr = SecretStr("change-this-secret-key-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth2 Providers - Google
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: SecretStr | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # OAuth2 Providers - GitHub
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: SecretStr | None = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/github/callback"

    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int = 100  # requests per minute
    RATE_LIMIT_PREMIUM_TIER: int = 1000  # requests per minute
    RATE_LIMIT_ADMIN_TIER: int = 0  # 0 = unlimited

    # Testing
    TEST_MODE: bool = Field(default=False)

    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode from TESTING env var."""
        import os

        return os.getenv("TESTING", "").lower() in ("true", "1", "yes")

    MIN_QUALITY_THRESHOLD: float = 0.7
    BACKUP_FREQUENCY: Literal["daily", "weekly", "monthly"] = "weekly"
    TIMEZONE: str = "UTC"

    # Redis configuration for Celery and caching
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_CACHE_DB: int = 2
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

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

    # Phase 17.5 - Advanced RAG Architecture
    # Chunking Configuration
    CHUNK_ON_RESOURCE_CREATE: bool = True  # Enable automatic chunking during ingestion
    CHUNKING_STRATEGY: str = "semantic"  # "semantic" or "fixed"
    CHUNK_SIZE: int = 500  # Words for semantic, characters for fixed
    CHUNK_OVERLAP: int = 50  # Words or characters overlap between chunks

    # Graph Extraction Configuration
    GRAPH_EXTRACTION_ENABLED: bool = True  # Enable graph extraction
    GRAPH_EXTRACTION_METHOD: str = "llm"  # "llm", "spacy", or "hybrid"
    GRAPH_EXTRACT_ON_CHUNK: bool = (
        False  # Enable automatic graph extraction after chunking
    )

    # Synthetic Questions Configuration
    SYNTHETIC_QUESTIONS_ENABLED: bool = (
        False  # Enable synthetic question generation (expensive, opt-in)
    )
    QUESTIONS_PER_CHUNK: int = 2  # Number of questions to generate per chunk
    QUESTION_GENERATION_MODEL: str = "gpt-3.5-turbo"  # Model for question generation

    # Retrieval Configuration
    DEFAULT_RETRIEVAL_STRATEGY: str = (
        "parent-child"  # "parent-child", "graphrag", or "hybrid"
    )
    PARENT_CHILD_CONTEXT_WINDOW: int = 2  # Number of surrounding chunks to include
    GRAPHRAG_MAX_HOPS: int = 2  # Maximum graph traversal depth

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env file

    def get_database_url(self) -> str:
        """
        Construct database URL based on configuration.

        Returns SQLite URL if DATABASE_URL is set to SQLite,
        otherwise constructs PostgreSQL async URL using asyncpg driver.

        Returns:
            str: Database connection URL (SQLite or PostgreSQL)

        Examples:
            SQLite: sqlite:///./backend.db
            PostgreSQL: postgresql+asyncpg://user:pass@host:5432/db
        """
        if "sqlite" in self.DATABASE_URL.lower():
            return self.DATABASE_URL

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns a singleton Settings instance that is cached for the lifetime
    of the application. This ensures consistent configuration across all
    modules and avoids repeated environment variable parsing.

    Returns:
        Settings: Cached configuration instance

    Raises:
        ValueError: If configuration validation fails
    """
    settings = Settings()

    # Validate graph weights sum to 1.0
    total_weight = (
        settings.GRAPH_WEIGHT_VECTOR
        + settings.GRAPH_WEIGHT_TAGS
        + settings.GRAPH_WEIGHT_CLASSIFICATION
    )
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(
            f"Configuration validation failed: GRAPH_WEIGHT_VECTOR + GRAPH_WEIGHT_TAGS + "
            f"GRAPH_WEIGHT_CLASSIFICATION must sum to 1.0, got {total_weight}. "
            f"Expected type: float (sum=1.0)"
        )

    # Validate JWT configuration
    if (
        not settings.JWT_SECRET_KEY
        or settings.JWT_SECRET_KEY.get_secret_value()
        == "change-this-secret-key-in-production"
    ):
        if settings.ENV == "prod":
            raise ValueError(
                "Configuration validation failed: JWT_SECRET_KEY must be set to a secure value in production. "
                "Expected type: SecretStr (non-default value)"
            )

    if settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
        raise ValueError(
            f"Configuration validation failed: JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive, "
            f"got {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}. Expected type: int (> 0)"
        )

    if settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS <= 0:
        raise ValueError(
            f"Configuration validation failed: JWT_REFRESH_TOKEN_EXPIRE_DAYS must be positive, "
            f"got {settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS}. Expected type: int (> 0)"
        )

    # Validate rate limiting configuration
    if settings.RATE_LIMIT_FREE_TIER < 0:
        raise ValueError(
            f"Configuration validation failed: RATE_LIMIT_FREE_TIER must be non-negative, "
            f"got {settings.RATE_LIMIT_FREE_TIER}. Expected type: int (>= 0)"
        )

    if settings.RATE_LIMIT_PREMIUM_TIER < 0:
        raise ValueError(
            f"Configuration validation failed: RATE_LIMIT_PREMIUM_TIER must be non-negative, "
            f"got {settings.RATE_LIMIT_PREMIUM_TIER}. Expected type: int (>= 0)"
        )

    if settings.RATE_LIMIT_ADMIN_TIER < 0:
        raise ValueError(
            f"Configuration validation failed: RATE_LIMIT_ADMIN_TIER must be non-negative (0 = unlimited), "
            f"got {settings.RATE_LIMIT_ADMIN_TIER}. Expected type: int (>= 0)"
        )

    # Validate PostgreSQL configuration when using PostgreSQL
    if "postgresql" in settings.DATABASE_URL.lower():
        if not settings.POSTGRES_SERVER:
            raise ValueError(
                "Configuration validation failed: POSTGRES_SERVER must be set when using PostgreSQL. "
                "Expected type: str (non-empty)"
            )
        if not settings.POSTGRES_USER:
            raise ValueError(
                "Configuration validation failed: POSTGRES_USER must be set when using PostgreSQL. "
                "Expected type: str (non-empty)"
            )
        if not settings.POSTGRES_PASSWORD:
            raise ValueError(
                "Configuration validation failed: POSTGRES_PASSWORD must be set when using PostgreSQL. "
                "Expected type: str (non-empty)"
            )
        if not settings.POSTGRES_DB:
            raise ValueError(
                "Configuration validation failed: POSTGRES_DB must be set when using PostgreSQL. "
                "Expected type: str (non-empty)"
            )
        if settings.POSTGRES_PORT <= 0 or settings.POSTGRES_PORT > 65535:
            raise ValueError(
                f"Configuration validation failed: POSTGRES_PORT must be between 1 and 65535, "
                f"got {settings.POSTGRES_PORT}. Expected type: int (1-65535)"
            )

    # Validate Redis configuration
    if settings.REDIS_PORT <= 0 or settings.REDIS_PORT > 65535:
        raise ValueError(
            f"Configuration validation failed: REDIS_PORT must be between 1 and 65535, "
            f"got {settings.REDIS_PORT}. Expected type: int (1-65535)"
        )

    # Validate quality threshold
    if not 0.0 <= settings.MIN_QUALITY_THRESHOLD <= 1.0:
        raise ValueError(
            f"Configuration validation failed: MIN_QUALITY_THRESHOLD must be between 0.0 and 1.0, "
            f"got {settings.MIN_QUALITY_THRESHOLD}. Expected type: float (0.0-1.0)"
        )

    # Validate hybrid search weight
    if not 0.0 <= settings.DEFAULT_HYBRID_SEARCH_WEIGHT <= 1.0:
        raise ValueError(
            f"Configuration validation failed: DEFAULT_HYBRID_SEARCH_WEIGHT must be between 0.0 and 1.0, "
            f"got {settings.DEFAULT_HYBRID_SEARCH_WEIGHT}. Expected type: float (0.0-1.0)"
        )

    # Validate Advanced RAG configuration (Phase 17.5)
    if settings.CHUNKING_STRATEGY not in ("semantic", "fixed"):
        raise ValueError(
            f"Configuration validation failed: CHUNKING_STRATEGY must be 'semantic' or 'fixed', "
            f"got '{settings.CHUNKING_STRATEGY}'. Expected type: str ('semantic' | 'fixed')"
        )

    if settings.CHUNK_SIZE <= 0:
        raise ValueError(
            f"Configuration validation failed: CHUNK_SIZE must be positive, "
            f"got {settings.CHUNK_SIZE}. Expected type: int (> 0)"
        )

    if settings.CHUNK_OVERLAP < 0:
        raise ValueError(
            f"Configuration validation failed: CHUNK_OVERLAP must be non-negative, "
            f"got {settings.CHUNK_OVERLAP}. Expected type: int (>= 0)"
        )

    if settings.CHUNK_OVERLAP >= settings.CHUNK_SIZE:
        raise ValueError(
            f"Configuration validation failed: CHUNK_OVERLAP must be less than CHUNK_SIZE, "
            f"got CHUNK_OVERLAP={settings.CHUNK_OVERLAP}, CHUNK_SIZE={settings.CHUNK_SIZE}. "
            f"Expected: CHUNK_OVERLAP < CHUNK_SIZE"
        )

    if settings.GRAPH_EXTRACTION_METHOD not in ("llm", "spacy", "hybrid"):
        raise ValueError(
            f"Configuration validation failed: GRAPH_EXTRACTION_METHOD must be 'llm', 'spacy', or 'hybrid', "
            f"got '{settings.GRAPH_EXTRACTION_METHOD}'. Expected type: str ('llm' | 'spacy' | 'hybrid')"
        )

    if settings.QUESTIONS_PER_CHUNK <= 0:
        raise ValueError(
            f"Configuration validation failed: QUESTIONS_PER_CHUNK must be positive, "
            f"got {settings.QUESTIONS_PER_CHUNK}. Expected type: int (> 0)"
        )

    if settings.DEFAULT_RETRIEVAL_STRATEGY not in (
        "parent-child",
        "graphrag",
        "hybrid",
    ):
        raise ValueError(
            f"Configuration validation failed: DEFAULT_RETRIEVAL_STRATEGY must be 'parent-child', 'graphrag', or 'hybrid', "
            f"got '{settings.DEFAULT_RETRIEVAL_STRATEGY}'. Expected type: str ('parent-child' | 'graphrag' | 'hybrid')"
        )

    if settings.PARENT_CHILD_CONTEXT_WINDOW < 0:
        raise ValueError(
            f"Configuration validation failed: PARENT_CHILD_CONTEXT_WINDOW must be non-negative, "
            f"got {settings.PARENT_CHILD_CONTEXT_WINDOW}. Expected type: int (>= 0)"
        )

    if settings.GRAPHRAG_MAX_HOPS <= 0:
        raise ValueError(
            f"Configuration validation failed: GRAPHRAG_MAX_HOPS must be positive, "
            f"got {settings.GRAPHRAG_MAX_HOPS}. Expected type: int (> 0)"
        )

    return settings
