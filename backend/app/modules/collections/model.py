"""
Neo Alexandria 2.0 - Collection Models

SQLAlchemy models for collections and collection-resource associations.

Models:
- Collection: User-curated collection of resources
- CollectionResource: Many-to-many association between collections and resources
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, ForeignKey, Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.shared.base_model import Base, GUID


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
    # Use string-based reference to avoid circular import
    resources: Mapped[List["Resource"]] = relationship(  # type: ignore
        "Resource",
        secondary="collection_resources",
        back_populates="collections"
    )
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id!r}, name={self.name!r}, owner_id={self.owner_id!r}, visibility={self.visibility!r})>"
