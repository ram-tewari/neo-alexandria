"""
Resources Module - Database Models

This module defines the Resource SQLAlchemy model for the Resources module.
The Resource model implements a hybrid Dublin Core + custom metadata schema.

Related files:
- schema.py: Pydantic schemas for validation
- service.py: Business logic for resource operations
- ../../shared/base_model.py: Base model classes
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, Float, func, JSON, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...shared.base_model import Base, GUID


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
    
    # Relationships - using string-based references to avoid circular imports
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
