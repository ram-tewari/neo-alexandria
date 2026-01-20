# Design Document: Phase 17 - Production Hardening

## Overview

Phase 17 transforms Neo Alexandria 2.0 from a development prototype into a production-ready application by implementing critical infrastructure improvements. This phase introduces PostgreSQL database support, API key authentication, real-time task tracking for frontend integration, and optimized Celery worker initialization.

The design maintains strict adherence to the Vertical Slice Architecture with zero circular dependencies, ensuring all new components reside in the shared kernel layer and are accessible to all modules without violating isolation principles.

### Key Design Goals

1. **Production Database Support**: Enable PostgreSQL for scalability while maintaining SQLite compatibility
2. **Security Hardening**: Implement API key authentication for endpoint protection
3. **Frontend Integration**: Provide real-time progress tracking for long-running operations
4. **Performance Optimization**: Pre-load ML models in Celery workers to eliminate cold start delays
5. **Developer Experience**: Containerized backing services for zero-configuration local development
6. **Module Isolation**: Maintain zero circular dependencies across all new components

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                     Neo Alexandria 2.0                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Frontend   │───▶│  API Gateway │───▶│   Modules    │    │
│  │  (React/TS)  │    │  (FastAPI)   │    │ (13 slices)  │    │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘    │
│                             │                     │             │
│                             ▼                     ▼             │
│                      ┌─────────────────────────────────┐       │
│                      │     Shared Kernel              │       │
│                      │  - Auth Service                │       │
│                      │  - Status Tracker              │       │
│                      │  - Database Service            │       │
│                      │  - Cache Service               │       │
│                      │  - Embedding Service           │       │
│                      └─────────┬───────────────────────┘       │
│                                │                                │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              ┌─────▼──────┐          ┌──────▼──────┐
              │ PostgreSQL │          │    Redis    │
              │  Database  │          │    Cache    │
              └────────────┘          └─────────────┘
```

### Component Architecture


#### 1. Docker Infrastructure Layer

**Purpose**: Provide containerized backing services for local development

**Components**:
- PostgreSQL 15 (Alpine) container with persistent volume
- Redis 7 (Alpine) container for cache and message broker
- Docker Compose configuration for orchestration

**Design Decisions**:
- Application runs locally (not containerized) for debugging flexibility
- Named volumes for data persistence across container restarts
- Environment variable configuration for credentials
- Minimal Alpine images for reduced resource footprint

#### 2. Configuration Service (Enhanced)

**Location**: `backend/app/config/settings.py`

**Purpose**: Centralized, type-safe configuration management with PostgreSQL support

**Key Features**:
- Pydantic Settings for validation and type safety
- PostgreSQL connection parameters (server, user, password, database)
- Dynamic database URL construction (SQLite or PostgreSQL)
- API key management with SecretStr
- Test mode flag for authentication bypass

**Design Pattern**: Singleton with LRU cache for performance

#### 3. Authentication Service (JWT + OAuth2)

**Location**: `backend/app/shared/security.py`, `backend/app/shared/oauth2.py`

**Purpose**: JWT token-based authentication with OAuth2 integration for secure, scalable access control

**Key Features**:
- OAuth2 password flow for username/password authentication
- JWT access tokens (30 min expiration) and refresh tokens (7 days)
- Token signature validation using HS256 algorithm
- OAuth2 authorization code flow for third-party providers (Google, GitHub)
- Token revocation list stored in Redis
- FastAPI dependency for Bearer token validation
- Selective endpoint exclusion (/auth/*, /docs, /health)
- Security logging for authentication events
- Test mode bypass for development

**Design Pattern**: OAuth2 with JWT Bearer tokens

#### 4. Rate Limiting Service

**Location**: `backend/app/shared/rate_limiter.py`

**Purpose**: Per-token rate limiting to prevent API abuse and ensure fair resource usage

**Key Features**:
- Sliding window algorithm for accurate rate limiting
- Redis-backed request counting with TTL
- Configurable rate limits per tier (free: 100/min, premium: 1000/min, admin: unlimited)
- Rate limit tier stored in JWT token claims
- HTTP 429 responses with Retry-After header
- Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Graceful degradation when Redis unavailable (fail open)
- Endpoint to check current rate limit status

**Design Pattern**: Middleware with Redis backend

#### 5. Status Tracking Service

**Location**: `backend/app/shared/services/status_tracker.py`
**Schemas**: `backend/app/shared/schemas/status.py`

**Purpose**: Real-time progress tracking for long-running background tasks

**Key Features**:
- Processing stage enumeration (INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING)
- Stage status enumeration (PENDING, PROCESSING, COMPLETED, FAILED)
- Redis-backed storage with TTL
- Overall status calculation from stage statuses
- Graceful degradation when Redis unavailable

**Design Pattern**: Service layer with Redis backend

#### 6. Celery Worker Optimization

**Location**: `backend/app/worker.py` or `backend/app/core/celery_app.py`

**Purpose**: Pre-load ML models at worker startup to eliminate per-task loading overhead

**Key Features**:
- Worker process initialization signal handler
- EmbeddingService pre-loading
- Memory usage logging
- Graceful error handling with retry logic

**Design Pattern**: Signal-based initialization

## Components and Interfaces

### 1. Docker Compose Configuration

**File**: `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: neo-alexandria-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-neo_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-neo_password}
      POSTGRES_DB: ${POSTGRES_DB:-neo_alexandria}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-neo_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: neo-alexandria-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

### 2. Enhanced Configuration Service

**Interface**:

```python
from pydantic import SecretStr

class Settings(BaseSettings):
    # Existing fields...
    DATABASE_URL: str
    ENV: Literal["dev", "staging", "prod"]
    
    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "neo_user"
    POSTGRES_PASSWORD: str = "neo_password"
    POSTGRES_DB: str = "neo_alexandria"
    POSTGRES_PORT: int = 5432
    
    # JWT Authentication
    JWT_SECRET_KEY: SecretStr = SecretStr("change-this-secret-key-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth2 Providers
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: SecretStr | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: SecretStr | None = None
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/github/callback"
    
    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int = 100  # requests per minute
    RATE_LIMIT_PREMIUM_TIER: int = 1000  # requests per minute
    RATE_LIMIT_ADMIN_TIER: int = 0  # 0 = unlimited
    
    # Testing
    TEST_MODE: bool = False
    
    def get_database_url(self) -> str:
        """Construct database URL based on configuration.
        
        Returns SQLite URL if DATABASE_URL is set to SQLite,
        otherwise constructs PostgreSQL async URL.
        """
        if "sqlite" in self.DATABASE_URL.lower():
            return self.DATABASE_URL
        
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
```
        otherwise constructs PostgreSQL async URL.
        """
        if "sqlite" in self.DATABASE_URL.lower():
            return self.DATABASE_URL
        
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
```

### 3. JWT Authentication Service

**Interface** (`backend/app/shared/security.py`):

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: int
    username: str
    scopes: list[str] = []
    tier: str = "free"  # free, premium, admin

class User(BaseModel):
    """User model for authentication."""
    id: int
    username: str
    email: str
    hashed_password: str
    tier: str = "free"
    is_active: bool = True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.
    
    Args:
        data: Token payload (user_id, username, scopes, tier)
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token.
    
    Args:
        data: Token payload (user_id, username)
        
    Returns:
        Encoded JWT refresh token
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT token and extract user data.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    settings = get_settings()
    
    # Bypass in test mode
    if settings.TEST_MODE:
        return TokenData(user_id=1, username="test_user", tier="admin")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is revoked
        if await is_token_revoked(token):
            logger.warning(f"Revoked token used: {token[:20]}...")
            raise credentials_exception
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        token_type: str = payload.get("type")
        
        if user_id is None or username is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id,
            username=username,
            scopes=payload.get("scopes", []),
            tier=payload.get("tier", "free")
        )
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise credentials_exception
    
    return token_data

async def is_token_revoked(token: str) -> bool:
    """Check if token is in revocation list.
    
    Args:
        token: JWT token to check
        
    Returns:
        True if token is revoked, False otherwise
    """
    try:
        from .cache import cache
        revoked = cache.get(f"revoked_token:{token}")
        return revoked is not None
    except Exception as e:
        logger.error(f"Error checking token revocation: {e}")
        return False

async def revoke_token(token: str, ttl: int = 86400) -> None:
    """Add token to revocation list.
    
    Args:
        token: JWT token to revoke
        ttl: Time-to-live for revocation entry (default: 24 hours)
    """
    try:
        from .cache import cache
        cache.set(f"revoked_token:{token}", True, ttl=ttl)
        logger.info(f"Token revoked: {token[:20]}...")
    except Exception as e:
        logger.error(f"Error revoking token: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)
```

### 4. Rate Limiting Service

**Interface** (`backend/app/shared/rate_limiter.py`):

```python
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

class RateLimiter:
    """Rate limiting service using Redis sliding window."""
    
    def __init__(self, cache_service):
        self.cache = cache_service
    
    async def check_rate_limit(
        self,
        user_id: int,
        tier: str,
        endpoint: str
    ) -> tuple[bool, dict]:
        """Check if request is within rate limits.
        
        Args:
            user_id: User identifier
            tier: User tier (free, premium, admin)
            endpoint: API endpoint being accessed
            
        Returns:
            Tuple of (allowed: bool, headers: dict)
        """
        settings = get_settings()
        
        # Get rate limit for tier
        if tier == "admin":
            return True, self._get_rate_limit_headers(0, 0, 0)
        
        limit = (
            settings.RATE_LIMIT_PREMIUM_TIER if tier == "premium"
            else settings.RATE_LIMIT_FREE_TIER
        )
        
        # Redis key for sliding window
        window_key = f"rate_limit:{user_id}:{int(time.time() // 60)}"
        
        try:
            # Get current count
            current = self.cache.get(window_key) or 0
            
            if current >= limit:
                # Rate limit exceeded
                reset_time = int(time.time() // 60 + 1) * 60
                headers = self._get_rate_limit_headers(limit, 0, reset_time)
                return False, headers
            
            # Increment counter
            self.cache.set(window_key, current + 1, ttl=60)
            
            # Calculate remaining
            remaining = limit - current - 1
            reset_time = int(time.time() // 60 + 1) * 60
            headers = self._get_rate_limit_headers(limit, remaining, reset_time)
            
            return True, headers
            
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e} - allowing request")
            # Fail open if Redis is unavailable
            return True, {}
    
    def _get_rate_limit_headers(
        self,
        limit: int,
        remaining: int,
        reset: int
    ) -> dict:
        """Generate rate limit headers.
        
        Args:
            limit: Total requests allowed
            remaining: Requests remaining in window
            reset: Unix timestamp when limit resets
            
        Returns:
            Dictionary of rate limit headers
        """
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset)
        }

async def rate_limit_dependency(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
) -> None:
    """FastAPI dependency for rate limiting.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    from .cache import cache
    rate_limiter = RateLimiter(cache)
    
    allowed, headers = await rate_limiter.check_rate_limit(
        user_id=current_user.user_id,
        tier=current_user.tier,
        endpoint=request.url.path
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                **headers,
                "Retry-After": headers.get("X-RateLimit-Reset", "60")
            }
        )
    
    # Add rate limit headers to response
    request.state.rate_limit_headers = headers
```

### 5. OAuth2 Provider Integration

**Interface** (`backend/app/shared/oauth2.py`):

```python
from typing import Optional
import httpx
from fastapi import HTTPException, status

class OAuth2Provider:
    """Base class for OAuth2 provider integration."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    async def get_authorization_url(self, state: str) -> str:
        """Get OAuth2 authorization URL."""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from provider."""
        raise NotImplementedError

class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 provider."""
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    async def get_authorization_url(self, state: str) -> str:
        """Get Google OAuth2 authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for Google access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from Google."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            return response.json()

class GitHubOAuth2Provider(OAuth2Provider):
    """GitHub OAuth2 provider."""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    
    async def get_authorization_url(self, state: str) -> str:
        """Get GitHub OAuth2 authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
            "state": state
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for GitHub access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            return response.json()
```

### 6. Status Tracking Service

**Schemas** (`backend/app/shared/schemas/status.py`):

```python
from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field

class ProcessingStage(str, Enum):
    """Processing stages for resource ingestion pipeline."""
    INGESTION = "ingestion"
    QUALITY = "quality"
    TAXONOMY = "taxonomy"
    GRAPH = "graph"
    EMBEDDING = "embedding"

class StageStatus(str, Enum):
    """Status of a processing stage."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceProgress(BaseModel):
    """Progress tracking for a resource through processing stages."""
    resource_id: int
    overall_status: StageStatus
    stages: Dict[ProcessingStage, StageStatus] = Field(default_factory=dict)
    error_message: str | None = None
    updated_at: str  # ISO 8601 timestamp
```

**Service** (`backend/app/shared/services/status_tracker.py`):

```python
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from ..schemas.status import ProcessingStage, StageStatus, ResourceProgress
from ..cache import CacheService

logger = logging.getLogger(__name__)

class StatusTracker:
    """Track resource processing progress in Redis."""
    
    def __init__(self, cache: CacheService):
        self.cache = cache
        self.ttl = 86400  # 24 hours
    
    async def set_progress(
        self,
        resource_id: int,
        stage: ProcessingStage,
        status: StageStatus,
        error_message: Optional[str] = None
    ) -> None:
        """Update progress for a specific stage.
        
        Args:
            resource_id: Resource identifier
            stage: Processing stage being updated
            status: New status for the stage
            error_message: Optional error message if status is FAILED
        """
        try:
            # Get current progress or create new
            progress = await self.get_progress(resource_id)
            if not progress:
                progress = ResourceProgress(
                    resource_id=resource_id,
                    overall_status=StageStatus.PENDING,
                    stages={},
                    updated_at=datetime.now(timezone.utc).isoformat()
                )
            
            # Update stage status
            progress.stages[stage] = status
            if error_message:
                progress.error_message = error_message
            
            # Calculate overall status
            progress.overall_status = self._calculate_overall_status(progress.stages)
            progress.updated_at = datetime.now(timezone.utc).isoformat()
            
            # Store in Redis
            key = f"progress:resource:{resource_id}"
            self.cache.set(key, progress.model_dump(), ttl=self.ttl)
            
        except Exception as e:
            logger.error(f"Failed to set progress for resource {resource_id}: {e}")
    
    async def get_progress(self, resource_id: int) -> Optional[ResourceProgress]:
        """Get current progress for a resource.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            ResourceProgress if found, None otherwise
        """
        try:
            key = f"progress:resource:{resource_id}"
            data = self.cache.get(key)
            if data:
                return ResourceProgress(**data)
            return None
        except Exception as e:
            logger.warning(f"Failed to get progress for resource {resource_id}: {e}")
            return None
    
    def _calculate_overall_status(self, stages: Dict[ProcessingStage, StageStatus]) -> StageStatus:
        """Calculate overall status from stage statuses.
        
        Logic:
        - If any stage is FAILED, overall is FAILED
        - If any stage is PROCESSING, overall is PROCESSING
        - If all stages are COMPLETED, overall is COMPLETED
        - Otherwise, overall is PENDING
        """
        if not stages:
            return StageStatus.PENDING
        
        statuses = set(stages.values())
        
        if StageStatus.FAILED in statuses:
            return StageStatus.FAILED
        if StageStatus.PROCESSING in statuses:
            return StageStatus.PROCESSING
        if all(s == StageStatus.COMPLETED for s in statuses):
            return StageStatus.COMPLETED
        
        return StageStatus.PENDING
```

### 5. Celery Worker Optimization

**Implementation** (`backend/app/worker.py`):

```python
import logging
from celery import Celery
from celery.signals import worker_process_init

from .config.settings import get_settings
from .shared.embeddings import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()

# Create Celery app
celery_app = Celery(
    "neo_alexandria",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Global embedding service instance (initialized at worker startup)
_embedding_service: Optional[EmbeddingService] = None

@worker_process_init.connect
def init_worker_process(**kwargs):
    """Initialize worker process with pre-loaded ML models.
    
    This signal handler runs once when each worker process starts,
    loading ML models into memory to avoid per-task loading overhead.
    """
    global _embedding_service
    
    logger.info("Initializing Celery worker process...")
    
    try:
        # Pre-load embedding service and models
        logger.info("Loading embedding models...")
        _embedding_service = EmbeddingService()
        
        # Trigger model loading by generating a test embedding
        test_text = "Initialization test"
        _embedding_service.generate_embedding(test_text)
        
        logger.info("✓ Embedding models loaded successfully")
        logger.info("Worker process initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize worker process: {e}", exc_info=True)
        # Don't fail worker startup, but log the error
        _embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get pre-loaded embedding service instance.
    
    Returns:
        Pre-loaded EmbeddingService instance
        
    Raises:
        RuntimeError: If embedding service failed to initialize
    """
    if _embedding_service is None:
        raise RuntimeError("Embedding service not initialized in worker")
    return _embedding_service
```

## Data Models

### Authentication Schema

```python
# Token Models
Token {
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
}

TokenData {
    user_id: int
    username: str
    scopes: list[str]
    tier: str  # free, premium, admin
}

# User Model
User {
    id: int
    username: str
    email: str
    hashed_password: str
    tier: str = "free"
    is_active: bool = True
}

# OAuth2 Models
OAuth2AuthorizationRequest {
    provider: str  # google, github
    redirect_uri: str
    state: str
}

OAuth2CallbackData {
    code: str
    state: str
}
```

### Rate Limiting Schema

```python
RateLimitInfo {
    limit: int
    remaining: int
    reset: int  # Unix timestamp
}

RateLimitTier = Enum("free", "premium", "admin")
```

### Status Tracking Schema

```python
# Enums
ProcessingStage = Enum("INGESTION", "QUALITY", "TAXONOMY", "GRAPH", "EMBEDDING")
StageStatus = Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED")

# Progress Model
ResourceProgress {
    resource_id: int
    overall_status: StageStatus
    stages: Dict[ProcessingStage, StageStatus]
    error_message: Optional[str]
    updated_at: str (ISO 8601)
}
```

### Redis Storage Format

```
# Token Revocation
Key: "revoked_token:{token}"
Value: True
TTL: 86400 seconds (24 hours)

# Rate Limiting
Key: "rate_limit:{user_id}:{minute_timestamp}"
Value: request_count (integer)
TTL: 60 seconds

# Status Tracking
Key: "progress:resource:{resource_id}"
Value: JSON-serialized ResourceProgress
TTL: 86400 seconds (24 hours)
```

### Configuration Schema

```python
Settings {
    # Database
    DATABASE_URL: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    
    # JWT Authentication
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    
    # OAuth2 Providers
    GOOGLE_CLIENT_ID: str | None
    GOOGLE_CLIENT_SECRET: SecretStr | None
    GOOGLE_REDIRECT_URI: str
    GITHUB_CLIENT_ID: str | None
    GITHUB_CLIENT_SECRET: SecretStr | None
    GITHUB_REDIRECT_URI: str
    
    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int
    RATE_LIMIT_PREMIUM_TIER: int
    RATE_LIMIT_ADMIN_TIER: int
    
    # Testing
    TEST_MODE: bool
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_CACHE_DB: int
    
    # Methods
    get_database_url() -> str
}
```

### Authentication Router

**Location**: `backend/app/modules/auth/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 password flow login.
    
    Returns JWT access and refresh tokens.
    """
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "tier": user.tier,
            "scopes": form_data.scopes
        }
    )
    refresh_token = create_refresh_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Create new access token
        access_token = create_access_token(
            data={
                "user_id": payload["user_id"],
                "username": payload["username"],
                "tier": payload.get("tier", "free")
            }
        )
        
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Logout and revoke current token."""
    await revoke_token(token)
    return {"message": "Successfully logged out"}

@router.get("/google")
async def google_login():
    """Initiate Google OAuth2 flow."""
    settings = get_settings()
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth2 not configured")
    
    provider = GoogleOAuth2Provider(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    state = generate_state_token()  # Random state for CSRF protection
    auth_url = await provider.get_authorization_url(state)
    
    return {"authorization_url": auth_url, "state": state}

@router.get("/google/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth2 callback."""
    settings = get_settings()
    provider = GoogleOAuth2Provider(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    # Exchange code for token
    token_data = await provider.exchange_code_for_token(code)
    user_info = await provider.get_user_info(token_data["access_token"])
    
    # Create or get user
    user = await get_or_create_oauth_user(
        provider="google",
        provider_user_id=user_info["id"],
        email=user_info["email"],
        username=user_info.get("name", user_info["email"])
    )
    
    # Create JWT tokens
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "tier": user.tier}
    )
    refresh_token = create_refresh_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/github")
async def github_login():
    """Initiate GitHub OAuth2 flow."""
    settings = get_settings()
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=501, detail="GitHub OAuth2 not configured")
    
    provider = GitHubOAuth2Provider(
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GITHUB_REDIRECT_URI
    )
    
    state = generate_state_token()
    auth_url = await provider.get_authorization_url(state)
    
    return {"authorization_url": auth_url, "state": state}

@router.get("/github/callback")
async def github_callback(code: str, state: str):
    """Handle GitHub OAuth2 callback."""
    settings = get_settings()
    provider = GitHubOAuth2Provider(
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GITHUB_REDIRECT_URI
    )
    
    # Exchange code for token
    token_data = await provider.exchange_code_for_token(code)
    user_info = await provider.get_user_info(token_data["access_token"])
    
    # Create or get user
    user = await get_or_create_oauth_user(
        provider="github",
        provider_user_id=str(user_info["id"]),
        email=user_info["email"],
        username=user_info["login"]
    )
    
    # Create JWT tokens
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "tier": user.tier}
    )
    refresh_token = create_refresh_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information."""
    user = await get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/rate-limit")
async def get_rate_limit_status(current_user: TokenData = Depends(get_current_user)):
    """Get current rate limit status for user."""
    settings = get_settings()
    
    if current_user.tier == "admin":
        limit = 0  # Unlimited
    elif current_user.tier == "premium":
        limit = settings.RATE_LIMIT_PREMIUM_TIER
    else:
        limit = settings.RATE_LIMIT_FREE_TIER
    
    # Get current usage from Redis
    window_key = f"rate_limit:{current_user.user_id}:{int(time.time() // 60)}"
    current = cache.get(window_key) or 0
    remaining = max(0, limit - current)
    reset = int(time.time() // 60 + 1) * 60
    
    return RateLimitInfo(limit=limit, remaining=remaining, reset=reset)
```



## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I identified the following patterns:
- **Round-trip properties**: Data persistence (1.6), status tracking (5.5)
- **Format validation**: URL construction (2.2, 2.3), error responses (8.3)
- **Error handling**: Authentication failures (4.3, 4.6), Redis unavailability (5.9, 8.2)
- **Configuration validation**: Database URLs (2.1), environment variables (3.6)
- **Structural tests**: File locations (7.1-7.7), enum definitions (5.1-5.3)

Many criteria are examples or edge cases rather than universal properties. I've consolidated related properties and marked structural/example tests separately.

### Universal Properties

**Property 1: Database URL Construction Correctness**
*For any* valid PostgreSQL configuration (server, user, password, database, port), the constructed database URL should match the format `postgresql+asyncpg://{user}:{password}@{server}:{port}/{database}` and be parseable by SQLAlchemy.
**Validates: Requirements 2.2, 2.3**

**Property 2: Database URL Backward Compatibility**
*For any* SQLite database URL, the configuration service should accept it unchanged and the system should successfully connect to the database.
**Validates: Requirements 2.1, 2.4**

**Property 3: Configuration Validation**
*For any* invalid configuration (missing required fields, invalid types, malformed values), the Configuration_Service should raise validation errors at initialization time before the application starts.
**Validates: Requirements 2.6, 3.6, 8.4**

**Property 4: Authentication Success**
*For any* HTTP request with X-API-Key header matching the configured MASTER_API_KEY, the authentication service should allow the request to proceed without raising exceptions.
**Validates: Requirements 4.2**

**Property 5: Authentication Failure**
*For any* HTTP request with an invalid or missing X-API-Key header (when TEST_MODE is false), the authentication service should return HTTP 403 with a structured error response containing a detail field.
**Validates: Requirements 4.3, 8.3**

**Property 6: Authentication Logging**
*For any* authentication failure, the authentication service should create a log entry with at least WARNING level containing information about the failed attempt.
**Validates: Requirements 4.6**

**Property 7: Global Authentication Application**
*For any* API endpoint except /docs, /openapi.json, and /monitoring/health, requests without valid authentication should be rejected with HTTP 403.
**Validates: Requirements 4.4**

**Property 8: Status Tracking Round-Trip**
*For any* resource_id, processing stage, and stage status, calling set_progress followed by get_progress should return a ResourceProgress object with the same resource_id and the specified stage status in the stages dictionary.
**Validates: Requirements 5.4, 5.5**

**Property 9: Overall Status Calculation**
*For any* set of stage statuses, the calculated overall_status should follow these rules:
- If any stage is FAILED, overall is FAILED
- Else if any stage is PROCESSING, overall is PROCESSING  
- Else if all stages are COMPLETED, overall is COMPLETED
- Else overall is PENDING
**Validates: Requirements 5.8**

**Property 10: Status Tracking TTL**
*For any* progress record stored in Redis, the key should have a TTL set (not -1) to ensure automatic expiration and prevent memory bloat.
**Validates: Requirements 5.10**

**Property 11: Worker Model Reuse**
*For any* sequence of embedding generation tasks executed by the same worker process, the embedding model should be loaded exactly once (during worker initialization), not once per task.
**Validates: Requirements 6.4**

**Property 12: Data Persistence Across Container Restarts**
*For any* data written to the PostgreSQL database, stopping and restarting the Docker containers should preserve that data (the data should still be retrievable after restart).
**Validates: Requirements 1.6**

### Example Tests

The following criteria are best tested with specific examples rather than universal properties:

**Example 1: Docker Infrastructure Startup**
- Verify `docker-compose -f docker-compose.dev.yml up` starts PostgreSQL and Redis containers
- Verify PostgreSQL exposes port 5432 with named volume
- Verify Redis exposes port 6379
- Verify docker-compose.yml uses environment variables for credentials
- Verify no app service is defined in docker-compose.yml
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

**Example 2: Configuration Fields**
- Verify Settings class has POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB fields
- Verify Settings class has MASTER_API_KEY field of type SecretStr
- Verify Settings class has TEST_MODE field of type bool
- Verify Settings class has get_database_url() method
**Validates: Requirements 3.2, 3.3, 3.4, 3.5**

**Example 3: .env File Loading**
- Create a .env file with test values
- Verify Settings loads values from .env file
**Validates: Requirements 3.7**

**Example 4: Authentication Dependency**
- Verify get_api_key function exists and is a valid FastAPI dependency
- Verify function signature accepts api_key parameter from Security(api_key_header)
**Validates: Requirements 4.1**

**Example 5: Unauthenticated Endpoint Access**
- Verify /docs, /openapi.json, and /monitoring/health are accessible without X-API-Key header
**Validates: Requirements 4.5**

**Example 6: Test Mode Bypass**
- When TEST_MODE=true, verify requests without X-API-Key header are allowed
**Validates: Requirements 4.7**

**Example 7: Status Tracking Schema**
- Verify ProcessingStage enum has values: INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING
- Verify StageStatus enum has values: PENDING, PROCESSING, COMPLETED, FAILED
- Verify ResourceProgress model has fields: resource_id, overall_status, stages, error_message, updated_at
**Validates: Requirements 5.1, 5.2, 5.3**

**Example 8: Module Integration**
- Verify modules call set_progress with COMPLETED status when stages complete
- Verify modules call set_progress with FAILED status and error details when stages fail
**Validates: Requirements 5.6, 5.7**

**Example 9: Redis Unavailability Handling**
- When Redis is unavailable, verify Status_Tracker logs warnings and returns default progress states
**Validates: Requirements 5.9**

**Example 10: Worker Initialization**
- Verify @worker_process_init signal handler is registered
- Verify worker pre-loads ML models at startup
- Verify EmbeddingService is initialized during worker_process_init
- Verify worker logs initialization progress and memory usage
**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

**Example 11: Worker Error Handling**
- When model loading fails, verify worker logs errors and retries with exponential backoff
- Verify worker supports graceful shutdown and releases resources
**Validates: Requirements 6.6, 6.7**

**Example 12: Module Isolation**
- Verify Auth_Service is in app/shared/security.py
- Verify Status_Tracker is in app/shared/services/status_tracker.py
- Verify Configuration_Service is in app/config/settings.py
- Verify modules import from app.shared.security and app.shared.services.status_tracker
- Run module isolation checker and verify zero violations
- Verify shared kernel has no dependencies on domain modules
**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7**

**Example 13: Database Connection Errors**
- When PostgreSQL is unavailable, verify system logs connection errors and fails startup with clear messages
**Validates: Requirements 8.1**

**Example 14: Redis Degradation**
- When Redis is unavailable, verify Status_Tracker logs warnings and continues operation
**Validates: Requirements 8.2**

**Example 15: Health Checks**
- Verify health check endpoint exists and verifies database and cache connectivity
**Validates: Requirements 8.5**

**Example 16: Celery Task Error Handling**
- When a Celery task fails, verify worker logs detailed error information and updates status tracking
- Verify system implements retry logic for transient failures
**Validates: Requirements 8.6, 8.7**



## Error Handling

### Database Connection Errors

**PostgreSQL Connection Failures**:
- Log detailed error messages including host, port, database name (not password)
- Fail application startup with clear error message
- Provide troubleshooting hints (check Docker containers, credentials, network)

**SQLite Connection Failures**:
- Log file path and permissions
- Fail application startup with clear error message
- Suggest checking file permissions and disk space

### Redis Connection Errors

**Cache Service Degradation**:
- Log warning when Redis is unavailable
- Continue operation with degraded functionality
- Return None for cache misses
- Skip cache writes silently
- Log each failed operation at DEBUG level

**Status Tracker Degradation**:
- Log warning when Redis is unavailable
- Return default progress states (all stages PENDING)
- Log each failed set_progress call at WARNING level
- Continue application operation

### Authentication Errors

**Invalid API Key**:
- Return HTTP 403 Forbidden
- Log warning with truncated key (first 8 characters only)
- Include generic error message: "Could not validate credentials"
- Do not reveal whether key exists or is invalid

**Missing API Key**:
- Return HTTP 403 Forbidden
- Log warning about missing key
- Include generic error message: "Could not validate credentials"

**Test Mode**:
- Bypass authentication when TEST_MODE=true
- Log info message about test mode bypass
- Return placeholder key: "test-mode-bypass"

### Configuration Errors

**Invalid Configuration**:
- Raise ValidationError at startup with detailed field errors
- Include field name, expected type, received value
- Fail fast before application starts accepting requests

**Missing Required Fields**:
- Use default values where appropriate
- Raise ValidationError for truly required fields
- Document all defaults in Settings class

### Worker Initialization Errors

**Model Loading Failures**:
- Log error with full traceback
- Retry with exponential backoff (1s, 2s, 4s, 8s, 16s)
- After 5 retries, log critical error and set _embedding_service to None
- Allow worker to start but fail tasks with clear error message

**Memory Errors**:
- Log memory usage before and after model loading
- If OOM occurs, log critical error with memory stats
- Suggest increasing worker memory allocation

## Testing Strategy

### Unit Tests

**Configuration Service**:
- Test get_database_url() with SQLite URLs (unchanged)
- Test get_database_url() with PostgreSQL configuration
- Test validation errors for invalid configurations
- Test default values for optional fields
- Test .env file loading
- Test SecretStr masking for MASTER_API_KEY

**Authentication Service**:
- Test get_api_key() with valid key (success)
- Test get_api_key() with invalid key (403 error)
- Test get_api_key() with missing key (403 error)
- Test get_api_key() in TEST_MODE (bypass)
- Test authentication logging for failures
- Test error response structure

**Status Tracker**:
- Test set_progress() stores data in Redis
- Test get_progress() retrieves data from Redis
- Test round-trip (set then get)
- Test overall_status calculation with various stage combinations
- Test TTL is set on Redis keys
- Test graceful degradation when Redis unavailable
- Test error message storage and retrieval

**Celery Worker**:
- Test worker_process_init signal handler registration
- Test embedding service initialization
- Test model reuse across multiple tasks
- Test error handling for model loading failures
- Test graceful shutdown

### Property-Based Tests

**Property Test 1: Database URL Construction**
- Generate random valid PostgreSQL configurations
- Verify constructed URL matches expected format
- Verify URL is parseable by SQLAlchemy
- Run 100 iterations
**Feature: phase17-production-hardening, Property 1: Database URL Construction Correctness**

**Property Test 2: Authentication Success**
- Generate random valid API keys
- Configure as MASTER_API_KEY
- Verify authentication succeeds
- Run 100 iterations
**Feature: phase17-production-hardening, Property 4: Authentication Success**

**Property Test 3: Authentication Failure**
- Generate random invalid API keys (not matching MASTER_API_KEY)
- Verify authentication fails with 403
- Verify error response structure
- Run 100 iterations
**Feature: phase17-production-hardening, Property 5: Authentication Failure**

**Property Test 4: Status Tracking Round-Trip**
- Generate random resource IDs, stages, and statuses
- Call set_progress then get_progress
- Verify retrieved data matches set data
- Run 100 iterations
**Feature: phase17-production-hardening, Property 8: Status Tracking Round-Trip**

**Property Test 5: Overall Status Calculation**
- Generate random combinations of stage statuses
- Calculate overall status
- Verify calculation follows rules (FAILED > PROCESSING > COMPLETED > PENDING)
- Run 100 iterations
**Feature: phase17-production-hardening, Property 9: Overall Status Calculation**

### Integration Tests

**Docker Infrastructure**:
- Test docker-compose up starts containers
- Test PostgreSQL connectivity on port 5432
- Test Redis connectivity on port 6379
- Test data persistence across container restarts
- Test volume mounting

**End-to-End Authentication**:
- Test protected endpoint with valid key (success)
- Test protected endpoint with invalid key (403)
- Test unprotected endpoints without key (success)
- Test global authentication application

**End-to-End Status Tracking**:
- Create resource
- Update progress through all stages
- Verify frontend can retrieve progress
- Verify TTL expiration

**Database Migration**:
- Test SQLite to PostgreSQL migration
- Verify data integrity after migration
- Test application works with both databases

### Performance Tests

**Authentication Overhead**:
- Measure request latency with authentication
- Target: < 5ms overhead per request
- Test with 1000 concurrent requests

**Status Tracking Latency**:
- Measure set_progress and get_progress latency
- Target: < 10ms per operation
- Test with 1000 concurrent operations

**Worker Initialization Time**:
- Measure time to load embedding models
- Target: < 30 seconds
- Test with cold start

**Database Connection Pool**:
- Test connection pool under load
- Verify no connection exhaustion
- Test with 100 concurrent requests

## Deployment Considerations

### Environment Variables

**Required for Production**:
```bash
# Database
POSTGRES_SERVER=your-postgres-host
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=neo_alexandria
POSTGRES_PORT=5432

# Authentication
MASTER_API_KEY=your-secure-api-key-change-this

# Redis
REDIS_HOST=your-redis-host
REDIS_PORT=6379

# Environment
ENV=prod
TEST_MODE=false
```

**Optional with Defaults**:
```bash
# Redis databases
REDIS_CACHE_DB=2
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Embedding configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
```

### Docker Deployment

**Development**:
```bash
# Start backing services
docker-compose -f docker-compose.dev.yml up -d

# Run application locally
cd backend
uvicorn app.main:app --reload
```

**Production**:
```bash
# Use production docker-compose with app service
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes/cloud platform
```

### Database Migration

**SQLite to PostgreSQL**:
1. Export data from SQLite using Alembic
2. Start PostgreSQL container
3. Update DATABASE_URL to PostgreSQL
4. Run Alembic migrations
5. Import data
6. Verify data integrity
7. Update application configuration

### Security Hardening

**API Key Management**:
- Generate strong random API keys (32+ characters)
- Rotate keys regularly
- Store keys in secure secret management system
- Never commit keys to version control
- Use different keys for dev/staging/prod

**Database Security**:
- Use strong passwords (16+ characters)
- Restrict network access to database
- Enable SSL/TLS for PostgreSQL connections
- Regular security updates for PostgreSQL

**Redis Security**:
- Enable Redis authentication (requirepass)
- Restrict network access
- Use Redis ACLs for fine-grained permissions
- Regular security updates

### Monitoring

**Health Checks**:
- `/monitoring/health` - Overall system health
- Check database connectivity
- Check Redis connectivity
- Check worker status

**Metrics to Track**:
- Authentication success/failure rate
- Database connection pool usage
- Redis cache hit/miss rate
- Status tracking operation latency
- Worker initialization time
- API response times

**Logging**:
- Authentication failures (security monitoring)
- Database connection errors
- Redis connection errors
- Worker initialization progress
- Configuration validation errors

### Backup Strategy

**Database Backups**:
- PostgreSQL: Use pg_dump for regular backups
- Schedule: Daily incremental, weekly full
- Retention: 30 days
- Test restore procedures regularly

**Redis Backups**:
- Enable RDB snapshots
- Schedule: Hourly snapshots
- Retention: 24 hours (status data is ephemeral)

## Migration Path

### Phase 1: Infrastructure Setup
1. Create docker-compose.dev.yml
2. Test PostgreSQL and Redis containers
3. Verify data persistence

### Phase 2: Configuration Enhancement
1. Update Settings class with PostgreSQL fields
2. Implement get_database_url() method
3. Add MASTER_API_KEY and TEST_MODE fields
4. Test configuration validation

### Phase 3: Authentication Implementation
1. Create app/shared/security.py
2. Implement get_api_key() dependency
3. Update app/main.py with global authentication
4. Exclude public endpoints
5. Test authentication flow

### Phase 4: Status Tracking Implementation
1. Create app/shared/schemas/status.py with enums and models
2. Create app/shared/services/status_tracker.py
3. Integrate with existing CacheService
4. Test status tracking operations

### Phase 5: Worker Optimization
1. Update worker.py with worker_process_init signal
2. Implement model pre-loading
3. Test worker initialization
4. Measure performance improvements

### Phase 6: Integration and Testing
1. Run full test suite
2. Test with PostgreSQL
3. Test with SQLite (backward compatibility)
4. Test authentication on all endpoints
5. Test status tracking end-to-end
6. Verify module isolation

### Phase 7: Documentation
1. Update setup guide with Docker instructions
2. Document environment variables
3. Create PostgreSQL migration guide
4. Document API authentication
5. Document status tracking API

## Success Criteria

- ✅ Docker infrastructure starts successfully
- ✅ PostgreSQL connection works
- ✅ SQLite backward compatibility maintained
- ✅ Authentication protects all endpoints except exclusions
- ✅ Status tracking stores and retrieves progress
- ✅ Celery workers pre-load models
- ✅ Zero circular dependency violations
- ✅ All tests passing (unit, property, integration)
- ✅ Performance targets met (< 5ms auth, < 10ms status tracking, < 30s worker init)
- ✅ Documentation complete and accurate

