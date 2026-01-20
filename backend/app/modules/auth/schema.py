"""Pydantic schemas for authentication module.

This module defines request and response schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """OAuth2 password flow login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
    scopes: list[str] = Field(
        default_factory=list, description="Optional OAuth2 scopes"
    )


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class OAuth2AuthorizationResponse(BaseModel):
    """OAuth2 authorization URL response."""

    authorization_url: str = Field(
        ..., description="URL to redirect user to for authorization"
    )
    state: str = Field(..., description="CSRF protection state token")


class UserInfoResponse(BaseModel):
    """Current user information response."""

    id: str = Field(..., description="User ID (UUID)")  # Changed from int to str
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    tier: str = Field(..., description="User tier (free, premium, admin)")
    is_active: bool = Field(..., description="Whether user account is active")


class RateLimitInfo(BaseModel):
    """Rate limit status information."""

    limit: int = Field(..., description="Total requests allowed per window")
    remaining: int = Field(..., description="Requests remaining in current window")
    reset: int = Field(..., description="Unix timestamp when limit resets")
    tier: str = Field(..., description="User tier (free, premium, admin)")
