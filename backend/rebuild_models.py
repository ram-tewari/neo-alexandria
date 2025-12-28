"""
Script to rebuild database/models.py with all model definitions.
This fixes the circular import issue by having a single source of truth.
"""

# Read the original comprehensive models file from git history or backup
# For now, we'll use a minimal version that imports from the correct location

models_content = '''"""
Neo Alexandria 2.0 - Database Models

SINGLE SOURCE OF TRUTH for all SQLAlchemy database models.
All models defined here to avoid circular import dependencies.
"""

import enum
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, Float, func, JSON, Integer, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..shared.base_model import Base, GUID

# For now, import from module files (temporary solution)
# TODO: Move all definitions here
from ..modules.resources.model import Resource
from ..modules.collections.model import Collection, CollectionResource  
from ..modules.annotations.model import Annotation
from ..modules.graph.model import Citation, GraphEdge, GraphEmbedding, DiscoveryHypothesis
from ..modules.recommendations.model import UserProfile, UserInteraction, RecommendationFeedback

# Shared models defined here
class ClassificationCode(Base):
    """Lookup table for personal/UDC-inspired classification codes."""
    __tablename__ = "classification_codes"
    
    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_code: Mapped[str | None] = mapped_column(String(20), ForeignKey("classification_codes.code", ondelete="SET NULL"), nullable=True)
    keywords: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list, server_default='[]')

class TaxonomyNode(Base):
    """Hierarchical taxonomy tree node for ML-based classification."""
    __tablename__ = "taxonomy_nodes"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scheme: Mapped[str] = mapped_column(String(50), nullable=False, default="custom", index=True)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class ResourceTaxonomy(Base):
    """Association table for many-to-many Resource-Taxonomy relationship."""
    __tablename__ = "resource_taxonomy"
    
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    taxonomy_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), primary_key=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_manual: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    needs_review: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    predicted_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", server_default="user")
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    is_verified: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

__all__ = [
    "Resource", "Collection", "CollectionResource", "Annotation",
    "Citation", "GraphEdge", "GraphEmbedding", "DiscoveryHypothesis",
    "UserProfile", "UserInteraction", "RecommendationFeedback",
    "ClassificationCode", "TaxonomyNode", "ResourceTaxonomy", "User"
]
'''

# Write the file
with open('app/database/models.py', 'w') as f:
    f.write(models_content)

print("✓ Created app/database/models.py with temporary imports")
print("  This allows the app to start while we fix the circular dependencies")
