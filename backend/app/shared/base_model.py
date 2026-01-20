"""
Shared base model and mixins for all domain models.

Provides common SQLAlchemy base class and reusable mixins for timestamps and UUIDs.
"""

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from datetime import datetime, timezone
from uuid import uuid4
import uuid

# Import Base from shared database module
from .database import Base


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(36)
    storing as stringified hex values.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQL_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps.

    Automatically tracks when records are created and updated.
    Uses timezone-aware UTC timestamps.
    """

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    """
    Mixin for UUID primary key.

    Provides a UUID primary key that works across SQLite and PostgreSQL.
    """

    id = Column(GUID(), primary_key=True, default=uuid4)


# Re-export Base for convenience
__all__ = ["Base", "TimestampMixin", "UUIDMixin", "GUID"]
