"""Database models for authentication module.

This module defines SQLAlchemy models for OAuth accounts.
The User model is imported from the main database models.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ...shared.database import Base
from ...shared.base_model import GUID


class OAuthAccount(Base):
    """OAuth account linking model.

    Links users to their OAuth2 provider accounts (Google, GitHub, etc.).

    Attributes:
        id: Primary key
        user_id: Foreign key to users table (UUID)
        provider: OAuth2 provider name (google, github)
        provider_user_id: User ID from OAuth2 provider
        user: Related user object
    """

    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # google, github
    provider_user_id = Column(String, nullable=False)

    # Relationships
    user = relationship("User", backref="oauth_accounts")

    def __repr__(self) -> str:
        return f"<OAuthAccount(id={self.id}, provider='{self.provider}', user_id={self.user_id})>"
