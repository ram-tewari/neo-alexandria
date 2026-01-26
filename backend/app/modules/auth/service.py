"""Authentication service layer.

This module provides business logic for user authentication, including
user management, OAuth2 integration, and token generation.
"""

import logging
import secrets
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.security import (
    get_password_hash,
    verify_password,
)
from ...shared.oauth2 import GoogleOAuth2Provider, GitHubOAuth2Provider
from ...config.settings import get_settings
from ...database.models import User
from .model import OAuthAccount

logger = logging.getLogger(__name__)


# ============================================================================
# User Authentication Functions
# ============================================================================


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Authenticate user with username and password.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    try:
        # Find user by username or email
        stmt = select(User).where(
            (User.username == username) | (User.email == username)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {username}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user

    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}")
        return None


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID.

    Args:
        db: Database session
        user_id: User ID (UUID)

    Returns:
        User object if found, None otherwise
    """
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


async def get_or_create_oauth_user(
    db: AsyncSession, provider: str, provider_user_id: str, email: str, username: str
) -> User:
    """Get or create user from OAuth2 provider data.

    Args:
        db: Database session
        provider: OAuth2 provider name (google, github)
        provider_user_id: User ID from provider
        email: User email from provider
        username: Username from provider

    Returns:
        User object (existing or newly created)
    """
    try:
        # Check if OAuth account exists
        stmt = select(OAuthAccount).where(
            (OAuthAccount.provider == provider)
            & (OAuthAccount.provider_user_id == provider_user_id)
        )
        result = await db.execute(stmt)
        oauth_account = result.scalar_one_or_none()

        if oauth_account:
            # Fetch the user separately to avoid lazy loading issues
            logger.info(f"Found existing OAuth user: {provider}:{provider_user_id}")
            user_stmt = select(User).where(User.id == oauth_account.user_id)
            user_result = await db.execute(user_stmt)
            return user_result.scalar_one()

        # Check if user with email exists
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Create new user
            # Generate random password and truncate to 72 bytes (bcrypt limit)
            random_password = secrets.token_urlsafe(32)[:72]
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(random_password),
                tier="free",
                is_active=True,
            )
            db.add(user)
            await db.flush()  # Get user ID
            logger.info(f"Created new user from OAuth: {username}")

        # Link OAuth account to user
        oauth_account = OAuthAccount(
            user_id=user.id, provider=provider, provider_user_id=provider_user_id
        )
        db.add(oauth_account)
        await db.commit()
        await db.refresh(user)

        logger.info(
            f"Linked OAuth account: {provider}:{provider_user_id} to user {user.id}"
        )
        return user

    except Exception as e:
        logger.error(f"Error creating OAuth user: {e}")
        await db.rollback()
        raise


# ============================================================================
# OAuth2 Provider Functions
# ============================================================================


def get_google_provider() -> Optional[GoogleOAuth2Provider]:
    """Get Google OAuth2 provider instance.

    Returns:
        GoogleOAuth2Provider if configured, None otherwise
    """
    settings = get_settings()

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return None

    return GoogleOAuth2Provider(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


def get_github_provider() -> Optional[GitHubOAuth2Provider]:
    """Get GitHub OAuth2 provider instance.

    Returns:
        GitHubOAuth2Provider if configured, None otherwise
    """
    settings = get_settings()

    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        return None

    return GitHubOAuth2Provider(
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET.get_secret_value(),
        redirect_uri=settings.GITHUB_REDIRECT_URI,
    )


def generate_state_token() -> str:
    """Generate random state token for CSRF protection.

    Returns:
        Random URL-safe token
    """
    return secrets.token_urlsafe(32)
