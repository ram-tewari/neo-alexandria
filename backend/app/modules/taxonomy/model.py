"""
Taxonomy Models

SQLAlchemy models for taxonomy and classification.
Re-exports models from app.database.models to avoid circular imports.
"""

from app.database.models import TaxonomyNode, ResourceTaxonomy

__all__ = ["TaxonomyNode", "ResourceTaxonomy"]
