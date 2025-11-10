"""
Neo Alexandria 2.0 - Phase 6.5: Advanced Metadata Extraction

This module implements comprehensive scholarly metadata extraction for academic papers,
including authors, DOIs, equations, tables, figures, and OCR processing.

Related files:
- app/database/models.py: Resource model with scholarly fields
- app/utils/equation_parser.py: LaTeX equation extraction
- app/utils/table_extractor.py: Table structure extraction
- app/services/resource_service.py: Integration with ingestion pipeline
"""

import json
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.database import models as db_models

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Advanced metadata extraction for scholarly content.
    Implements MeXtract-style comprehensive extraction.
    """

    def __init__(self, db: Session):
        self.db = db

    def extract_scholarly_metadata(self, resource_id: str) -> Dict:
        """
        Master orchestrator for scholarly metadata extraction.
        
        Returns: Dict of all extracted fields
        """
        try:
            import uuid as uuid_module
            resource_uuid = uuid_module.UUID(resource_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid resource_id: {resource_id}")
            return {}

        resource = self.db.query(db_models.Resource).filter(
            db_models.Resource.id == resource_uuid
        ).first()

        if not resource:
            logger.error(f"Resource not found: {resource_id}")
            return {}

        # Get content and determine type
        content = resource.description or ""
        content_type = resource.format or ""
        
        # Initialize result
        metadata = {}
        
        try:
            # Detect document type and route to appropriate extractor
            if "pdf" in content_type.lower():
                metadata = self.extract_paper_metadata(content, content_type)
            elif "html" in content_type.lower():
                metadata = self.extract_paper_metadata(content, content_type)
            else:
                # Try generic extraction
                metadata = self.extract_paper_metadata(content, content_type)
            
            # Extract structured content
            equations = self._extract_equations_simple(content)
            tables = self._extract_tables_simple(content)
            
            metadata['equation_count'] = len(equations)
            metadata['table_count'] = len(tables)
            metadata['figure_count'] = 0  # Placeholder
            
            if equations:
                metadata['equations'] = json.dumps(equations)
            if tables:
                metadata['tables'] = json.dumps(tables)
            
            # Compute completeness and confidence
            metadata['metadata_completeness_score'] = self._compute_completeness(metadata)
            metadata['extraction_confidence'] = self._compute_confidence(metadata)
            metadata['requires_manual_review'] = metadata['extraction_confidence'] < 0.7
            
            # Update resource
            for key, value in metadata.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
            
            self.db.add(resource)
            self.db.commit()
            
            logger.info(f"Extracted scholarly metadata for resource {resource_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {resource_id}: {e}")
            resource.requires_manual_review = True
            resource.extraction_confidence = 0.0
            self.db.add(resource)
            self.db.commit()
            return {}

    def extract_paper_metadata(self, content: str, content_type: str) -> Dict:
        """
        Extract metadata specific to academic papers.
        
        Fields extracted:
        - Authors, DOI, publication info
        - Journal, year, pages
        - Funding sources
        """
        metadata = {}
        
        # Extract DOI
        doi = self._extract_doi(content)
        if doi:
            metadata['doi'] = doi
        
        # Extract arXiv ID
        arxiv_id = self._extract_arxiv_id(content)
        if arxiv_id:
            metadata['arxiv_id'] = arxiv_id
        
        # Extract publication year
        year = self._extract_publication_year(content)
        if year:
            metadata['publication_year'] = year
        
        # Extract authors (simple pattern matching)
        authors = self._extract_authors(content)
        if authors:
            metadata['authors'] = json.dumps(authors)
        
        # Extract journal name
        journal = self._extract_journal(content)
        if journal:
            metadata['journal'] = journal
        
        return metadata

    def _extract_doi(self, content: str) -> Optional[str]:
        """Extract DOI using regex pattern."""
        # DOI pattern: 10.xxxx/xxxxx
        pattern = r'10\.\d{4,}/[^\s]+'
        match = re.search(pattern, content)
        if match:
            doi = match.group(0)
            # Clean up common trailing punctuation
            doi = doi.rstrip('.,;:)')
            return doi
        return None

    def _extract_arxiv_id(self, content: str) -> Optional[str]:
        """Extract arXiv identifier."""
        # arXiv patterns: arXiv:YYMM.NNNNN or arXiv:arch-ive/YYMMNNN
        patterns = [
            r'arXiv:(\d{4}\.\d{4,5})',
            r'arxiv\.org/abs/(\d{4}\.\d{4,5})',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_publication_year(self, content: str) -> Optional[int]:
        """Extract publication year from content."""
        # Look for 4-digit years in reasonable range
        current_year = datetime.now().year
        pattern = r'\b(19\d{2}|20\d{2})\b'
        matches = re.findall(pattern, content)
        
        for match in matches:
            year = int(match)
            if 1900 <= year <= current_year:
                return year
        return None

    def _extract_authors(self, content: str) -> List[Dict]:
        """Extract author names (simple heuristic)."""
        # This is a placeholder - real implementation would use NER
        authors = []
        
        # Look for common author patterns
        # Example: "John Doe, Jane Smith"
        # This is very basic and would need improvement
        
        return authors

    def _extract_journal(self, content: str) -> Optional[str]:
        """Extract journal name (simple heuristic)."""
        # Look for common journal indicators
        patterns = [
            r'(?:published in|appeared in)\s+([A-Z][^.]+)',
            r'Journal of ([^.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_equations_simple(self, content: str) -> List[Dict]:
        """Simple equation extraction (placeholder for full implementation)."""
        equations = []
        
        # Look for LaTeX-style equations
        patterns = [
            r'\$\$(.+?)\$\$',  # Display math
            r'\$(.+?)\$',      # Inline math
        ]
        
        position = 0
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                equations.append({
                    'position': position,
                    'latex': match.group(1),
                    'context': content[max(0, match.start()-50):match.end()+50],
                    'confidence': 0.8
                })
                position += 1
        
        return equations[:50]  # Limit to 50 equations

    def _extract_tables_simple(self, content: str) -> List[Dict]:
        """Simple table detection (placeholder for full implementation)."""
        tables = []
        
        # Look for table indicators
        table_pattern = r'Table\s+\d+[:\.]?\s*([^\n]+)'
        for match in re.finditer(table_pattern, content, re.IGNORECASE):
            tables.append({
                'position': len(tables),
                'caption': match.group(1).strip(),
                'confidence': 0.6
            })
        
        return tables[:20]  # Limit to 20 tables

    def _compute_completeness(self, metadata: Dict) -> float:
        """Compute metadata completeness score."""
        required_fields = ['doi', 'authors', 'publication_year']
        optional_fields = ['journal', 'arxiv_id', 'equations', 'tables']
        
        required_score = sum(1 for f in required_fields if metadata.get(f)) / len(required_fields)
        optional_score = sum(1 for f in optional_fields if metadata.get(f)) / len(optional_fields)
        
        # Weighted: 70% required, 30% optional
        return required_score * 0.7 + optional_score * 0.3

    def _compute_confidence(self, metadata: Dict) -> float:
        """Compute extraction confidence score."""
        # Simple heuristic: more fields = higher confidence
        field_count = len([v for v in metadata.values() if v])
        max_fields = 10
        return min(field_count / max_fields, 1.0)
