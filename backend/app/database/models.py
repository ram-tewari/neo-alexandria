"""
Neo Alexandria 2.0 - Database Models

This module defines all SQLAlchemy database models for Neo Alexandria 2.0.
It implements a hybrid Dublin Core + custom metadata schema with authority control
and classification systems.

Related files:
- app/database/base.py: Base class and database configuration
- app/services/: Business logic that uses these models
- app/schemas/: Pydantic schemas for API validation
- alembic/versions/: Database migration scripts

Models include:
- Resource: Main entity with Dublin Core metadata and custom fields
- ClassificationCode: UDC-inspired classification system
- AuthoritySubject/Creator/Publisher: Authority control tables for normalization
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, Float, Enum, func, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, CHAR

from .base import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36) to store string representation of UUID.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
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
            return value


class Resource(Base):
    """Resource model implementing hybrid Dublin Core + custom metadata schema."""
    
    __tablename__ = "resources"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Dublin Core required fields
    title: Mapped[str] = mapped_column(String, nullable=False)
    
    # Dublin Core optional fields
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator: Mapped[str | None] = mapped_column(String, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String, nullable=True)
    contributor: Mapped[str | None] = mapped_column(String, nullable=True)
    date_created: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_modified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    type: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str | None] = mapped_column(String, nullable=True)
    identifier: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    coverage: Mapped[str | None] = mapped_column(String, nullable=True)
    rights: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # JSON arrays for multi-valued fields
    subject: Mapped[List[str]] = mapped_column(
        JSON, 
        nullable=False, 
        default=list,
        server_default='[]'
    )
    relation: Mapped[List[str]] = mapped_column(
        JSON, 
        nullable=False, 
        default=list,
        server_default='[]'
    )
    
    # Custom fields
    classification_code: Mapped[str | None] = mapped_column(String, nullable=True)
    read_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="unread"
    )
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Ingestion workflow fields
    ingestion_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending"
    )
    ingestion_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ingestion_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Vector embedding for Phase 4 hybrid search
    embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        server_default='[]'
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    def __repr__(self) -> str:
        return f"<Resource(id={self.id!r}, title={self.title!r})>"


class ClassificationCode(Base):
    """Lookup table for personal/UDC-inspired classification codes."""

    __tablename__ = "classification_codes"

    # Three-digit code as primary key, e.g., "000", "100", ... "999"
    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_code: Mapped[str | None] = mapped_column(String(3), ForeignKey("classification_codes.code"), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default='[]',
    )

    def __repr__(self) -> str:
        return f"<ClassificationCode(code={self.code!r}, title={self.title!r})>"


class AuthoritySubject(Base):
    """Authority table for subjects with canonical form, variants, and usage counts."""

    __tablename__ = "authority_subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_form: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    variants: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default='[]',
    )
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AuthoritySubject(id={self.id!r}, canonical_form={self.canonical_form!r})>"


class AuthorityCreator(Base):
    """Authority table for creators/authors with canonical form, variants, and usage counts."""

    __tablename__ = "authority_creators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_form: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    variants: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default='[]',
    )
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AuthorityCreator(id={self.id!r}, canonical_form={self.canonical_form!r})>"


class AuthorityPublisher(Base):
    """Authority table for publishers with canonical form, variants, and usage counts."""

    __tablename__ = "authority_publishers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_form: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    variants: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default='[]',
    )
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<AuthorityPublisher(id={self.id!r}, canonical_form={self.canonical_form!r})>"
