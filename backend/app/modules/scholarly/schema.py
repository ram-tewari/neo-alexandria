"""
Neo Alexandria 2.0 - Scholarly Metadata Schemas

Pydantic schemas for Phase 6.5 scholarly metadata API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Author(BaseModel):
    """Author information with affiliation and ORCID."""
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class Equation(BaseModel):
    """Mathematical equation with LaTeX representation."""
    position: int
    latex: str
    context: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class TableData(BaseModel):
    """Structured table data."""
    position: int
    caption: Optional[str] = None
    headers: List[str] = []
    rows: List[List[str]] = []
    format: str = "text"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class Figure(BaseModel):
    """Figure/image metadata."""
    position: int
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    url: str
    format: str
    confidence: float = Field(ge=0.0, le=1.0)


class ScholarlyMetadataResponse(BaseModel):
    """Complete scholarly metadata for a resource."""
    resource_id: str
    
    # Authors and attribution
    authors: Optional[List[Author]] = None
    affiliations: Optional[List[str]] = None
    
    # Academic identifiers
    doi: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    isbn: Optional[str] = None
    
    # Publication details
    journal: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publication_year: Optional[int] = None
    
    # Funding
    funding_sources: Optional[List[str]] = None
    acknowledgments: Optional[str] = None
    
    # Content structure counts
    equation_count: int = 0
    table_count: int = 0
    figure_count: int = 0
    reference_count: Optional[int] = None
    
    # Quality metrics
    metadata_completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    extraction_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    requires_manual_review: bool = False
    
    # OCR metadata
    is_ocr_processed: bool = False
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    ocr_corrections_applied: Optional[int] = None

    class Config:
        from_attributes = True


class MetadataExtractionRequest(BaseModel):
    """Request to trigger metadata extraction."""
    force: bool = Field(False, description="Re-extract even if already processed")


class MetadataExtractionResponse(BaseModel):
    """Response from metadata extraction trigger."""
    status: str
    resource_id: str
    message: Optional[str] = None


class MetadataCompletenessStats(BaseModel):
    """Aggregate statistics on metadata completeness."""
    total_resources: int
    with_doi: int
    with_authors: int
    with_publication_year: int
    avg_completeness_score: float
    requires_review_count: int
    by_content_type: dict = {}

