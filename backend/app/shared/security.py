"""JWT authentication and security utilities.

This module provides JWT token-based authentication with OAuth2 support,
password hashing, and token management for the Neo Alexandria 2.0 API.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================================================
# Data Models
# ============================================================================


class Token(BaseModel):
    """OAuth2 token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    user_id: str  # Changed from int to str to support UUID
    username: str
    scopes: list[str] = []
    tier: str = "free"  # free, premium, admin


# ============================================================================
# Password Hashing Functions
# ============================================================================


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = get_password_hash("my_secure_password")
        >>> len(hashed) > 0
        True
    """
    # Bcrypt has a 72-byte limit - truncate password if needed
    # Convert to bytes, truncate, then back to string to avoid cutting mid-character
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = get_password_hash("test123")
        >>> verify_password("test123", hashed)
        True
        >>> verify_password("wrong", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT Token Functions
# ============================================================================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Token payload (user_id, username, scopes, tier)
        expires_delta: Token expiration time (optional)

    Returns:
        Encoded JWT token

    Example:
        >>> token = create_access_token({"user_id": 1, "username": "test"})
        >>> len(token) > 0
        True
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token.

    Args:
        data: Token payload (user_id, username)

    Returns:
        Encoded JWT refresh token

    Example:
        >>> token = create_refresh_token({"user_id": 1, "username": "test"})
        >>> len(token) > 0
        True
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired

    Example:
        >>> token = create_access_token({"user_id": 1, "username": "test"})
        >>> payload = decode_token(token)
        >>> payload["user_id"]
        1
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise


def validate_token_type(payload: dict, expected_type: str) -> bool:
    """Validate token type (access vs refresh).

    Args:
        payload: Decoded token payload
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        True if token type matches, False otherwise

    Example:
        >>> token = create_access_token({"user_id": 1, "username": "test"})
        >>> payload = decode_token(token)
        >>> validate_token_type(payload, "access")
        True
        >>> validate_token_type(payload, "refresh")
        False
    """
    token_type = payload.get("type")
    return token_type == expected_type


# ============================================================================
# Token Revocation Functions
# ============================================================================


async def is_token_revoked(token: str) -> bool:
    """Check if token is in revocation list.

    Args:
        token: JWT token to check

    Returns:
        True if token is revoked, False otherwise

    Example:
        >>> # Token not revoked initially
        >>> import asyncio
        >>> token = create_access_token({"user_id": 1, "username": "test"})
        >>> asyncio.run(is_token_revoked(token))
        False
    """
    try:
        from .cache import cache

        revoked = cache.get(f"revoked_token:{token}")
        return revoked is not None
    except Exception as e:
        logger.error(f"Error checking token revocation: {e}")
        # Fail open - if we can't check revocation, allow the token
        return False


async def revoke_token(token: str, ttl: int = 86400) -> None:
    """Add token to revocation list.

    Args:
        token: JWT token to revoke
        ttl: Time-to-live for revocation entry in seconds (default: 24 hours)

    Example:
        >>> import asyncio
        >>> token = create_access_token({"user_id": 1, "username": "test"})
        >>> asyncio.run(revoke_token(token))
        >>> asyncio.run(is_token_revoked(token))
        True
    """
    try:
        from .cache import cache

        cache.set(f"revoked_token:{token}", "revoked", ttl=ttl)
        logger.info(f"Token revoked: {token[:20]}...")
    except Exception as e:
        logger.error(f"Error revoking token: {e}")
        # Log error but don't raise - revocation is best-effort


# ============================================================================
# FastAPI Authentication Dependency
# ============================================================================


def check_user_permissions(user: TokenData, required_scopes: list[str]) -> None:
    """Check if user has required permissions.

    Args:
        user: TokenData with user information
        required_scopes: List of required scopes

    Raises:
        HTTPException: 403 if user lacks required permissions

    Example:
        >>> user = TokenData(user_id=1, username="test", scopes=["read"])
        >>> check_user_permissions(user, ["read"])  # OK
        >>> check_user_permissions(user, ["write"])  # Raises 403
    """
    if not required_scopes:
        # No specific permissions required
        return

    # Check if user has all required scopes
    user_scopes = set(user.scopes)
    required_scopes_set = set(required_scopes)

    if not required_scopes_set.issubset(user_scopes):
        missing_scopes = required_scopes_set - user_scopes
        logger.warning(
            f"Permission denied for user {user.user_id}: "
            f"missing scopes {missing_scopes}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}",
        )


# Token cache to avoid repeated validation (in-memory cache with 60s TTL)
_token_cache: dict[str, tuple[TokenData, float]] = {}
_TOKEN_CACHE_TTL = 60  # seconds


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT token and extract user data.

    This is a FastAPI dependency that validates the Bearer token from the
    Authorization header and returns the user data from the token.
    
    Performance: Tokens are cached for 60 seconds to avoid repeated validation.

    Args:
        token: JWT token from Authorization header

    Returns:
        TokenData with user information

    Raises:
        HTTPException: 401 if token is invalid, expired, or revoked

    Example:
        >>> from fastapi import FastAPI, Depends
        >>> app = FastAPI()
        >>> @app.get("/protected")
        >>> async def protected_route(user: TokenData = Depends(get_current_user)):
        ...     return {"user_id": user.user_id}
    """
    import time
    
    # Check cache first (significant performance improvement)
    current_time = time.time()
    if token in _token_cache:
        cached_data, cache_time = _token_cache[token]
        if current_time - cache_time < _TOKEN_CACHE_TTL:
            # Cache hit - return cached user data
            return cached_data
        else:
            # Cache expired - remove from cache
            del _token_cache[token]
    
    settings = get_settings()

    # Bypass authentication in test mode
    if settings.is_test_mode or settings.TEST_MODE:
        logger.info("TEST_MODE enabled - bypassing authentication")
        # In test mode, still decode the token to get actual user data
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            username = payload.get("username")
            tier = payload.get("tier", "free")  # Get tier from token
            return TokenData(user_id=user_id, username=username, scopes=[], tier=tier)
        except Exception:
            # Fallback for invalid tokens in test mode
            return TokenData(user_id=1, username="test_user", scopes=[], tier="free")

    # Structured error response for invalid/expired tokens (HTTP 401)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Check if token is revoked (only if not in cache)
        if await is_token_revoked(token):
            logger.warning(
                f"Authentication failure: Revoked token used - {token[:20]}..."
            )
            raise credentials_exception

        # Decode and validate token
        payload = decode_token(token)

        # Extract user data
        user_id: Optional[str] = payload.get("user_id")  # Changed from int to str
        username: Optional[str] = payload.get("username")
        token_type: Optional[str] = payload.get("type")

        # Validate required fields
        if user_id is None or username is None:
            logger.warning(
                "Authentication failure: Token missing required fields (user_id or username)"
            )
            raise credentials_exception

        # Validate token type
        if token_type != "access":
            logger.warning(
                f"Authentication failure: Invalid token type '{token_type}' (expected: access)"
            )
            raise credentials_exception

        # Create TokenData
        token_data = TokenData(
            user_id=user_id,
            username=username,
            scopes=payload.get("scopes", []),
            tier=payload.get("tier", "free"),
        )
        
        # Cache the validated token data
        _token_cache[token] = (token_data, current_time)
        
        # Clean up old cache entries (simple cleanup every 100 validations)
        if len(_token_cache) > 1000:
            # Remove expired entries
            expired_tokens = [
                t for t, (_, cache_time) in _token_cache.items()
                if current_time - cache_time >= _TOKEN_CACHE_TTL
            ]
            for t in expired_tokens:
                del _token_cache[t]

        return token_data

    except JWTError as e:
        logger.warning(f"Authentication failure: JWT validation error - {e}")
        raise credentials_exception
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication failure: Unexpected error - {e}")
        raise credentials_exception
