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

from sqlalchemy import String, Text, DateTime, Float, func, JSON, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, CHAR

from ..shared.base_model import Base, GUID


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
    
    # Phase 13: PostgreSQL full-text search vector (PostgreSQL only)
    # This column is added by migration for PostgreSQL databases
    # SQLite continues to use FTS5 virtual tables
    # Note: This is defined as optional since it only exists in PostgreSQL
    search_vector: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # TSVector type in PostgreSQL, NULL in SQLite
    
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
    
    # Phase 9: Enhanced Quality Control Fields
    quality_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_completeness: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_consistency: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_timeliness: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_overall: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_weights: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    quality_last_computed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quality_computation_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Quality outlier detection
    is_quality_outlier: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    outlier_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    outlier_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    needs_quality_review: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    
    # Summary quality fields
    summary_coherence: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary_consistency: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary_fluency: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    
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


class TaxonomyNode(Base):
    """
    Hierarchical taxonomy tree node for ML-based classification.
    
    Implements materialized path pattern for efficient hierarchical queries.
    Supports multi-level taxonomy with parent-child relationships.
    """
    
    __tablename__ = "taxonomy_nodes"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Core metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Hierarchical structure
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    path: Mapped[str] = mapped_column(String(1000), nullable=False)  # Materialized path: "/parent/child"
    
    # Additional metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    
    # Cached resource counts
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    descendant_resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    
    # Metadata flags
    is_leaf: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')  # SQLite uses 0/1 for bool
    allow_resources: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    
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
    # Self-referential: parent node
    parent: Mapped["TaxonomyNode"] = relationship(
        "TaxonomyNode",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    
    # Self-referential: child nodes
    children: Mapped[List["TaxonomyNode"]] = relationship(
        "TaxonomyNode",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_taxonomy_parent_id', 'parent_id'),
        Index('idx_taxonomy_path', 'path'),
        Index('idx_taxonomy_slug', 'slug', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<TaxonomyNode(id={self.id!r}, name={self.name!r}, path={self.path!r})>"


class ResourceTaxonomy(Base):
    """
    Association table for many-to-many Resource-Taxonomy relationship.
    
    Stores ML classification results with confidence scores and metadata.
    Supports both predicted (ML) and manual classifications.
    """
    
    __tablename__ = "resource_taxonomy"
    
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
    taxonomy_node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Classification metadata
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default='0.0')
    is_predicted: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')  # SQLite uses 0/1 for bool
    predicted_by: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Model version or "manual"
    
    # Active learning metadata
    needs_review: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    review_priority: Mapped[float | None] = mapped_column(Float, nullable=True)
    
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
    resource: Mapped["Resource"] = relationship("Resource")
    taxonomy_node: Mapped["TaxonomyNode"] = relationship("TaxonomyNode")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_resource_taxonomy_resource', 'resource_id'),
        Index('idx_resource_taxonomy_taxonomy', 'taxonomy_node_id'),
        Index('idx_resource_taxonomy_needs_review', 'needs_review'),
    )
    
    def __repr__(self) -> str:
        return f"<ResourceTaxonomy(id={self.id!r}, resource_id={self.resource_id!r}, taxonomy_node_id={self.taxonomy_node_id!r}, confidence={self.confidence})>"


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



class GraphEdge(Base):
    """
    Multi-layer graph edge for Phase 10 knowledge graph.
    
    Supports multiple edge types: citation, coauthorship, subject similarity, temporal.
    """
    
    __tablename__ = "graph_edges"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Edge endpoints
    source_resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Edge metadata
    edge_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # 'citation', 'coauthorship', 'subject', 'temporal'
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    edge_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    # Aliases for backward compatibility
    @property
    def source_id(self):
        """Alias for source_resource_id."""
        return self.source_resource_id
    
    @source_id.setter
    def source_id(self, value):
        self.source_resource_id = value
    
    @property
    def target_id(self):
        """Alias for target_resource_id."""
        return self.target_resource_id
    
    @target_id.setter
    def target_id(self, value):
        self.target_resource_id = value
    
    # Indexes
    __table_args__ = (
        Index('idx_graph_edges_source', 'source_resource_id'),
        Index('idx_graph_edges_target', 'target_resource_id'),
        Index('idx_graph_edges_type', 'edge_type'),
    )
    
    def __repr__(self) -> str:
        return f"<GraphEdge(id={self.id!r}, type={self.edge_type!r}, source={self.source_resource_id!r}, target={self.target_resource_id!r})>"


class GraphEmbedding(Base):
    """
    Graph embeddings for Phase 10 structural analysis.
    
    Stores Node2Vec or similar graph embedding representations.
    """
    
    __tablename__ = "graph_embeddings"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Resource reference
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Embedding data
    embedding: Mapped[List[float]] = mapped_column(
        JSON,
        nullable=False
    )
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )  # 'node2vec', 'deepwalk', etc.
    
    # Metadata
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Additional embedding types (aliases for backward compatibility)
    structural_embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True
    )
    fusion_embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True
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
        return f"<GraphEmbedding(id={self.id!r}, resource_id={self.resource_id!r}, model={self.embedding_model!r})>"


class DiscoveryHypothesis(Base):
    """
    Literature-based discovery hypothesis for Phase 10.
    
    Stores potential connections discovered through graph analysis.
    """
    
    __tablename__ = "discovery_hypotheses"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Hypothesis components
    concept_a: Mapped[str] = mapped_column(String, nullable=False)
    concept_b: Mapped[str] = mapped_column(String, nullable=False)
    linking_concept: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Resource references (for ABC discovery pattern)
    resource_a_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=True
    )
    resource_b_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=True
    )
    resource_c_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=True
    )
    
    # Supporting evidence
    supporting_resources: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of resource IDs
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Aliases for backward compatibility
    @property
    def a_resource_id(self):
        """Alias for resource_a_id."""
        return self.resource_a_id
    
    @a_resource_id.setter
    def a_resource_id(self, value):
        self.resource_a_id = value
    
    @property
    def b_resource_id(self):
        """Alias for resource_b_id."""
        return self.resource_b_id
    
    @b_resource_id.setter
    def b_resource_id(self, value):
        self.resource_b_id = value
    
    # Hypothesis metadata
    hypothesis_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'abc', 'direct', 'temporal', etc.
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )  # 'pending', 'validated', 'rejected'
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    def __repr__(self) -> str:
        return f"<DiscoveryHypothesis(id={self.id!r}, {self.concept_a!r} -> {self.concept_b!r}, confidence={self.confidence_score})>"


class User(Base):
    """
    User model for authentication and profile management.
    
    Basic user entity with email and username for Phase 11 recommendation system.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Core fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    interactions: Mapped[List["UserInteraction"]] = relationship(
        "UserInteraction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    recommendation_feedback: Mapped[List["RecommendationFeedback"]] = relationship(
        "RecommendationFeedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, email={self.email!r}, username={self.username!r})>"


class UserProfile(Base):
    """
    User profile for personalized recommendations in Phase 11.
    
    Stores user preferences, learned patterns, and recommendation settings.
    Supports diversity, novelty, and recency preferences for hybrid recommendations.
    """
    
    __tablename__ = "user_profiles"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign key (one-to-one with User)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Research context (JSON arrays stored as Text)
    research_domains: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON: ["AI", "ML", "NLP"]
    active_domain: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Learned preferences (JSON arrays stored as Text)
    preferred_taxonomy_ids: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON: ["uuid1", "uuid2", ...]
    preferred_authors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON: ["Author 1", "Author 2", ...]
    preferred_sources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON: ["source1.com", "source2.com", ...]
    excluded_sources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )  # JSON: ["excluded1.com", "excluded2.com", ...]
    
    # Preference settings (0.0-1.0 range)
    diversity_preference: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        server_default='0.5'
    )
    novelty_preference: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.3,
        server_default='0.3'
    )
    recency_bias: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        server_default='0.5'
    )
    
    # Interaction metrics
    total_interactions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )
    avg_session_duration: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_user_profiles_user', 'user_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id!r}, user_id={self.user_id!r}, total_interactions={self.total_interactions})>"


class UserInteraction(Base):
    """
    User-resource interaction tracking for Phase 11 recommendation engine.
    
    Tracks all user interactions with resources using implicit feedback signals.
    Supports multiple interaction types with computed interaction strength.
    """
    
    __tablename__ = "user_interactions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Interaction metadata
    interaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'view', 'annotation', 'collection_add', 'export', 'rating'
    interaction_strength: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default='0.0'
    )  # 0.0-1.0 computed score
    
    # Implicit feedback signals
    dwell_time: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )  # seconds
    scroll_depth: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )  # 0.0-1.0
    annotation_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )
    return_visits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )
    
    # Explicit feedback
    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )  # 1-5 stars
    
    # Context
    session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    interaction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        index=True
    )
    
    # Derived fields
    is_positive: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )  # SQLite uses 0/1 for bool (strength > 0.4)
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default='0.0'
    )  # 0.0-1.0
    
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="interactions"
    )
    resource: Mapped["Resource"] = relationship("Resource")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_interactions_user_resource', 'user_id', 'resource_id'),
        Index('idx_user_interactions_timestamp', 'interaction_timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<UserInteraction(id={self.id!r}, user_id={self.user_id!r}, resource_id={self.resource_id!r}, type={self.interaction_type!r}, strength={self.interaction_strength})>"


class RecommendationFeedback(Base):
    """
    Recommendation feedback tracking for Phase 11 continuous improvement.
    
    Tracks recommendation performance to compute CTR and strategy effectiveness.
    Supports explicit user feedback for recommendation quality assessment.
    """
    
    __tablename__ = "recommendation_feedback"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Recommendation context
    recommendation_strategy: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'collaborative', 'content', 'graph', 'hybrid'
    recommendation_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    rank_position: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Feedback signals
    was_clicked: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0'
    )  # SQLite uses 0/1 for bool
    was_useful: Mapped[bool | None] = mapped_column(
        Integer,
        nullable=True
    )  # SQLite uses 0/1 for bool (explicit feedback)
    feedback_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Timestamps
    recommended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    feedback_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="recommendation_feedback"
    )
    resource: Mapped["Resource"] = relationship("Resource")
    
    # Indexes
    __table_args__ = (
        Index('idx_recommendation_feedback_user', 'user_id'),
        Index('idx_recommendation_feedback_resource', 'resource_id'),
        Index('idx_recommendation_feedback_strategy', 'recommendation_strategy'),
    )
    
    def __repr__(self) -> str:
        return f"<RecommendationFeedback(id={self.id!r}, user_id={self.user_id!r}, resource_id={self.resource_id!r}, strategy={self.recommendation_strategy!r}, clicked={self.was_clicked})>"


class ModelVersion(Base):
    """
    Model version tracking for ML models with metadata and metrics.
    
    Tracks trained model versions with semantic versioning, metadata about
    training configuration, and performance metrics for comparison.
    """
    
    __tablename__ = "model_versions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Version information
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )  # Semantic version: v1.0.0
    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'classification', 'ncf', 'embedding'
    model_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # 'training', 'testing', 'production', 'archived'
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    promoted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Metadata and metrics (JSON)
    model_metadata: Mapped[dict | None] = mapped_column(
        'metadata',
        JSON,
        nullable=True
    )  # Training config, dataset info, hyperparameters
    model_metrics: Mapped[dict | None] = mapped_column(
        'metrics',
        JSON,
        nullable=True
    )  # Accuracy, F1, latency, model size
    
    # Relationships
    control_experiments: Mapped[List["ABTestExperiment"]] = relationship(
        "ABTestExperiment",
        foreign_keys="ABTestExperiment.control_version_id",
        back_populates="control_version"
    )
    treatment_experiments: Mapped[List["ABTestExperiment"]] = relationship(
        "ABTestExperiment",
        foreign_keys="ABTestExperiment.treatment_version_id",
        back_populates="treatment_version"
    )
    prediction_logs: Mapped[List["PredictionLog"]] = relationship(
        "PredictionLog",
        back_populates="model_version"
    )
    retraining_runs: Mapped[List["RetrainingRun"]] = relationship(
        "RetrainingRun",
        back_populates="model_version"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_model_versions_version', 'version'),
        Index('idx_model_versions_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<ModelVersion(id={self.id!r}, version={self.version!r}, type={self.model_type!r}, status={self.status!r})>"


class ABTestExperiment(Base):
    """
    A/B test experiment configuration for comparing model versions.
    
    Tracks experiments comparing control (current) and treatment (new) model
    versions with traffic splitting and results analysis.
    """
    
    __tablename__ = "ab_test_experiments"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Experiment configuration
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Foreign keys to model versions
    control_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False
    )
    treatment_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Traffic configuration
    traffic_split: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )  # 0.0-1.0, percentage of traffic to treatment
    
    # Experiment timeline
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Status and results
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # 'running', 'completed', 'cancelled'
    results: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )  # Analysis results with metrics and statistical tests
    
    # Relationships
    control_version: Mapped["ModelVersion"] = relationship(
        "ModelVersion",
        foreign_keys=[control_version_id],
        back_populates="control_experiments"
    )
    treatment_version: Mapped["ModelVersion"] = relationship(
        "ModelVersion",
        foreign_keys=[treatment_version_id],
        back_populates="treatment_experiments"
    )
    prediction_logs: Mapped[List["PredictionLog"]] = relationship(
        "PredictionLog",
        back_populates="experiment"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_ab_test_experiments_status', 'status'),
        Index('idx_ab_test_experiments_dates', 'start_date', 'end_date'),
    )
    
    def __repr__(self) -> str:
        return f"<ABTestExperiment(id={self.id!r}, name={self.name!r}, status={self.status!r}, split={self.traffic_split})>"


class PredictionLog(Base):
    """
    Prediction logging for A/B test analysis.
    
    Logs predictions from both control and treatment models during A/B tests
    for performance comparison and statistical analysis.
    """
    
    __tablename__ = "prediction_logs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("ab_test_experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("model_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Prediction data
    input_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    predictions: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )  # Model predictions with scores
    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    # Relationships
    experiment: Mapped["ABTestExperiment"] = relationship(
        "ABTestExperiment",
        back_populates="prediction_logs"
    )
    model_version: Mapped["ModelVersion"] = relationship(
        "ModelVersion",
        back_populates="prediction_logs"
    )
    user: Mapped["User | None"] = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_prediction_logs_experiment_id', 'experiment_id'),
        Index('idx_prediction_logs_model_version_id', 'model_version_id'),
        Index('idx_prediction_logs_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<PredictionLog(id={self.id!r}, experiment_id={self.experiment_id!r}, version_id={self.model_version_id!r}, latency={self.latency_ms}ms)>"


class RetrainingRun(Base):
    """
    Retraining run tracking for automated model retraining pipeline.
    
    Tracks each retraining run with trigger type, dataset information,
    resulting model version, and performance metrics.
    """
    
    __tablename__ = "retraining_runs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Trigger information
    trigger_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # "scheduled", "manual", "data_growth", "performance_degradation"
    
    # Dataset information
    dataset_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    new_data_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Foreign key to resulting model version
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # "running", "completed", "failed"
    
    # Timing information
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    training_time_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Results and metrics
    metrics: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )  # Training metrics, evaluation results, comparison with production
    
    # Error information
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    model_version: Mapped["ModelVersion | None"] = relationship(
        "ModelVersion",
        back_populates="retraining_runs"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_retraining_runs_status', 'status'),
        Index('idx_retraining_runs_started_at', 'started_at'),
    )
    
    def __repr__(self) -> str:
        return f"<RetrainingRun(id={self.id!r}, trigger={self.trigger_type!r}, status={self.status!r}, dataset_size={self.dataset_size})>"
