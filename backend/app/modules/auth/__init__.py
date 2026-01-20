"""Authentication module for Neo Alexandria 2.0.

This module provides JWT-based authentication with OAuth2 support,
including login, token refresh, logout, and third-party OAuth2 flows
for Google and GitHub.
"""

from .router import router

__all__ = ["router"]
