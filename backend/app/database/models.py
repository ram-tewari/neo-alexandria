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
- Citation: Citation relationships between resources
- Collection: User-curated collections of resources with hierarchical support
- CollectionResource: Many-to-many association between collections and resources
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, Float, Enum, func, JSON, Integer, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    
    # Phase 8: Sparse vector embeddings for three-way hybrid search
    sparse_embedding: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON string: {"token_id": weight, ...}
    
    sparse_embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )  # Model name: "bge-m3" or "splade"
    
    sparse_embedding_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Phase 6.5: Scholarly Metadata Fields
    # Author and Attribution
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: [{"name": "...", "affiliation": "...", "orcid": "..."}]
    affiliations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: ["Institution 1", ...]
    
    # Academic Identifiers
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    pmid: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    arxiv_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # Publication Details
    journal: Mapped[str | None] = mapped_column(String, nullable=True)
    conference: Mapped[str | None] = mapped_column(String, nullable=True)
    volume: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issue: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pages: Mapped[str | None] = mapped_column(String(50), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    
    # Funding and Support
    funding_sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: ["NSF Grant #...", ...]
    acknowledgments: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Content Structure Counts
    equation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    table_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    figure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    reference_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Structured Content Storage
    equations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: [{"position": int, "latex": "...", ...}]
    tables: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: [{"position": int, "caption": "...", ...}]
    figures: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: [{"position": int, "caption": "...", ...}]
    
    # Metadata Quality
    metadata_completeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    requires_manual_review: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')  # SQLite uses 0/1 for bool
    
    # OCR Metadata
    is_ocr_processed: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ocr_corrections_applied: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
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
    
    # Relationships
    # Many-to-many: collections containing this resource
    collections: Mapped[List["Collection"]] = relationship(
        "Collection",
        secondary="collection_resources",
        back_populates="resources"
    )
    
    # One-to-many: annotations on this resource
    annotations: Mapped[List["Annotation"]] = relationship(
        "Annotation",
        back_populates="resource",
        cascade="all, delete-orphan"
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_resources_sparse_updated', 'sparse_embedding_updated_at'),
    )
    
    def __repr__(self) -> str:
        scholarly_info = f", doi={self.doi!r}" if self.doi else ""
        return f"<Resource(id={self.id!r}, title={self.title!r}{scholarly_info})>"


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


class Citation(Base):
    """
    Tracks citation relationships between resources.
    
    Supports both external citations (URLs) and internal citations (resolved resources).
    Used for building citation networks and computing importance scores via PageRank.
    """
    
    __tablename__ = "citations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    source_resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False
    )
    target_resource_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Citation metadata
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    citation_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="reference"
    )
    context_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Computed fields
    importance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
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
        return f"<Citation(id={self.id!r}, source={self.source_resource_id!r}, target_url={self.target_url!r})>"


class CollectionResource(Base):
    """
    Many-to-many association table between collections and resources.
    
    Tracks when resources were added to collections and supports efficient
    membership queries through composite indexing.
    """
    
    __tablename__ = "collection_resources"
    
    # Composite primary key
    collection_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Timestamp for when resource was added to collection
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_collection_resources_collection', 'collection_id'),
        Index('idx_collection_resources_resource', 'resource_id'),
    )
    
    def __repr__(self) -> str:
        return f"<CollectionResource(collection_id={self.collection_id!r}, resource_id={self.resource_id!r})>"


class Collection(Base):
    """
    User-curated collection of resources with hierarchical organization.
    
    Collections support:
    - Hierarchical nesting (parent/subcollections)
    - Visibility controls (private/shared/public)
    - Aggregate embeddings for semantic similarity
    - Many-to-many relationships with resources
    """
    
    __tablename__ = "collections"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Core metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Ownership and access control
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="private",
        server_default="private",
        index=True
    )  # 'private' | 'shared' | 'public'
    
    # Hierarchical structure (self-referential)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Semantic representation (aggregate of member resource embeddings)
    embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
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
    
    # Relationships
    # Self-referential: parent collection
    parent: Mapped["Collection"] = relationship(
        "Collection",
        remote_side=[id],
        back_populates="subcollections",
        foreign_keys=[parent_id]
    )
    
    # Self-referential: child collections
    subcollections: Mapped[List["Collection"]] = relationship(
        "Collection",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    # Many-to-many: resources in this collection
    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        secondary="collection_resources",
        back_populates="collections"
    )
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id!r}, name={self.name!r}, owner_id={self.owner_id!r}, visibility={self.visibility!r})>"


class Annotation(Base):
    """
    User annotations on resource content with text highlighting and notes.
    
    Supports:
    - Precise text selection via character offsets
    - Rich note-taking with semantic embeddings
    - Tag-based organization and color-coding
    - Context preservation for previews
    - Privacy controls (private/shared)
    - Collection associations
    """
    
    __tablename__ = "annotations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    # Text selection (precise positioning via character offsets)
    start_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    end_offset: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    highlighted_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # User content
    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    tags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON array: ["tag1", "tag2", ...]
    
    # Visual styling
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        default="#FFFF00",
        server_default="#FFFF00"
    )
    
    # Semantic search support
    embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )
    
    # Context preservation (50 chars before/after for previews)
    context_before: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    context_after: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Sharing and organization
    is_shared: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )  # SQLite uses 0/1 for bool
    collection_ids: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON array: ["uuid1", "uuid2", ...]
    
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
    
    # Relationships
    resource: Mapped["Resource"] = relationship(
        "Resource",
        back_populates="annotations"
    )
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_annotations_resource', 'resource_id'),
        Index('idx_annotations_user', 'user_id'),
        Index('idx_annotations_user_resource', 'user_id', 'resource_id'),
        Index('idx_annotations_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        note_preview = f", note={self.note[:30]!r}..." if self.note and len(self.note) > 30 else f", note={self.note!r}" if self.note else ""
        return f"<Annotation(id={self.id!r}, resource_id={self.resource_id!r}, user_id={self.user_id!r}{note_preview})>"
