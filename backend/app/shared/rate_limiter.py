"""
Neo Alexandria 2.0 - Rate Limiting Service

This module provides per-token rate limiting using Redis sliding window algorithm
to prevent API abuse and ensure fair resource usage.

Features:
- Sliding window algorithm for accurate rate limiting
- Configurable rate limits per tier (free, premium, admin)
- HTTP 429 responses with Retry-After header
- Rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Graceful degradation when Redis unavailable (fail open)

Related files:
- app/shared/security.py: JWT authentication and token validation
- app/config/settings.py: Rate limit configuration
- app/cache/redis_cache.py: Redis cache service
"""

import logging
import time
from typing import Optional, Tuple

from fastapi import Request, HTTPException, status, Depends

from ..cache.redis_cache import RedisCache
from ..config.settings import get_settings
from .security import TokenData, get_current_user

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting service using Redis sliding window algorithm.

    This class implements per-token rate limiting with configurable tiers
    and graceful degradation when Redis is unavailable.

    Attributes:
        cache: RedisCache instance for request counting
        settings: Application settings with rate limit configuration
    """

    def __init__(self, cache: Optional[RedisCache] = None):
        """Initialize rate limiter.

        Args:
            cache: Optional RedisCache instance. If not provided,
                  creates a new instance.
        """
        self.cache = cache if cache else RedisCache()
        self.settings = get_settings()

    async def check_rate_limit(
        self, user_id: int, tier: str, endpoint: str
    ) -> Tuple[bool, dict]:
        """Check if request is within rate limits.

        Uses sliding window algorithm with per-minute granularity.
        Tracks requests in Redis with automatic TTL expiration.

        Args:
            user_id: User identifier from JWT token
            tier: User tier (free, premium, admin)
            endpoint: API endpoint being accessed

        Returns:
            Tuple of (allowed: bool, headers: dict)
            - allowed: True if request is within limits, False otherwise
            - headers: Rate limit headers to include in response
        """
        # Admin tier has unlimited access
        if tier == "admin":
            return True, self._get_rate_limit_headers(0, 0, 0)

        # Get rate limit for tier
        limit = self._get_tier_limit(tier)

        # Calculate current minute window
        current_minute = int(time.time() // 60)
        window_key = f"rate_limit:{user_id}:{current_minute}"

        try:
            # Get current count for this window
            current_count_str = self.cache.redis.get(window_key)
            current_count = int(current_count_str) if current_count_str else 0

            # Check if limit exceeded
            if current_count >= limit:
                # Rate limit exceeded
                reset_time = (current_minute + 1) * 60
                headers = self._get_rate_limit_headers(limit, 0, reset_time)
                logger.warning(
                    f"Rate limit exceeded for user {user_id} (tier: {tier}): "
                    f"{current_count}/{limit} requests"
                )
                return False, headers

            # Increment counter with TTL
            # Use pipeline for atomic increment + expire
            pipe = self.cache.redis.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, 60)  # TTL of 60 seconds
            pipe.execute()

            # Calculate remaining requests
            remaining = limit - current_count - 1
            reset_time = (current_minute + 1) * 60
            headers = self._get_rate_limit_headers(limit, remaining, reset_time)

            return True, headers

        except Exception as e:
            # Fail open if Redis is unavailable
            logger.warning(
                f"Rate limit check failed for user {user_id}: {e} - allowing request"
            )
            return True, {}

    def _get_tier_limit(self, tier: str) -> int:
        """Get rate limit for user tier.

        Args:
            tier: User tier (free, premium, admin)

        Returns:
            Requests per minute limit
        """
        if tier == "premium":
            return self.settings.RATE_LIMIT_PREMIUM_TIER
        else:
            # Default to free tier for unknown tiers
            return self.settings.RATE_LIMIT_FREE_TIER

    def _get_rate_limit_headers(self, limit: int, remaining: int, reset: int) -> dict:
        """Generate rate limit headers.

        Args:
            limit: Total requests allowed per window
            remaining: Requests remaining in current window
            reset: Unix timestamp when limit resets

        Returns:
            Dictionary of rate limit headers
        """
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


# ============================================================================
# FastAPI Rate Limiting Dependency
# ============================================================================


async def rate_limit_dependency(
    request: Request, current_user: TokenData = Depends(get_current_user)
) -> None:
    """FastAPI dependency for rate limiting.

    This dependency checks rate limits after authentication and before
    endpoint execution. It raises HTTP 429 when limits are exceeded
    and adds rate limit headers to the response.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user from JWT token

    Raises:
        HTTPException: 429 if rate limit exceeded

    Example:
        >>> from fastapi import FastAPI, Depends
        >>> app = FastAPI()
        >>> @app.get("/api/resources", dependencies=[Depends(rate_limit_dependency)])
        >>> async def get_resources():
        ...     return {"resources": []}
    """
    # Check rate limit
    allowed, headers = await rate_limiter.check_rate_limit(
        user_id=current_user.user_id, tier=current_user.tier, endpoint=request.url.path
    )

    if not allowed:
        # Rate limit exceeded - raise 429 with headers
        reset_time = headers.get("X-RateLimit-Reset", "60")

        # Log rate limit violation for monitoring
        logger.warning(
            f"Rate limit violation: user_id={current_user.user_id}, "
            f"tier={current_user.tier}, endpoint={request.url.path}, "
            f"limit={headers.get('X-RateLimit-Limit')}"
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={**headers, "Retry-After": reset_time},
        )

    # Store headers in request state for response middleware
    request.state.rate_limit_headers = headers
