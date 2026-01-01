"""
Neo Alexandria 2.0 - Phase 6.5: Advanced Metadata Extraction

This module implements comprehensive scholarly metadata extraction for academic papers,
including authors, DOIs, equations, tables, figures, and OCR processing.

Related files:
- app/database/models.py: Resource model with scholarly fields
- app/utils/equation_parser.py: LaTeX equation extraction
- app/utils/table_extractor.py: Table structure extraction
- app/modules/resources/service.py: Integration with ingestion pipeline
"""

import json
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ...database import models as db_models
from ...shared.event_bus import event_bus, EventPriority
from ...events.event_types import SystemEvent

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
            
            # Extract structured content (equations, tables, figures)
            equations = self._extract_equations_simple(content)
            tables = self._extract_tables_simple(content)
            figures = self._extract_figures(content)
            
            # Extract additional metadata
            affiliations = self._extract_affiliations(content)
            funding = self._extract_funding(content)
            keywords = self._extract_keywords(content)
            
            # Store counts
            metadata['equation_count'] = len(equations)
            metadata['table_count'] = len(tables)
            metadata['figure_count'] = len(figures)
            
            # Store structured data as JSON
            if equations:
                metadata['equations'] = json.dumps(equations)
            if tables:
                metadata['tables'] = json.dumps(tables)
            if affiliations:
                metadata['affiliations'] = json.dumps(affiliations)
            if funding:
                metadata['funding_sources'] = json.dumps(funding)
            if keywords:
                # Store keywords in a structured format
                metadata['keywords'] = json.dumps(keywords)
            
            # Store complete scholarly metadata in JSON field
            scholarly_metadata = {
                'equations': equations,
                'tables': tables,
                'figures': figures,
                'affiliations': affiliations,
                'funding': funding,
                'keywords': keywords,
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
            metadata['scholarly_metadata'] = json.dumps(scholarly_metadata)
            
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
            
            # Emit metadata.extracted event
            event_bus.emit(
                'metadata.extracted',
                {
                    'resource_id': resource_id,
                    'metadata': scholarly_metadata,
                    'equation_count': len(equations),
                    'table_count': len(tables),
                    'figure_count': len(figures)
                },
                priority=EventPriority.LOW
            )
            
            # Emit equations.parsed event if equations were found
            if equations:
                from .handlers import emit_equations_parsed
                emit_equations_parsed(
                    resource_id=resource_id,
                    equations=equations,
                    equation_count=len(equations)
                )
            
            # Emit tables.extracted event if tables were found
            if tables:
                from .handlers import emit_tables_extracted
                emit_tables_extracted(
                    resource_id=resource_id,
                    tables=tables,
                    table_count=len(tables)
                )
            
            # Emit authors.extracted event if authors were found
            if 'authors' in metadata:
                try:
                    authors_list = json.loads(metadata['authors']) if isinstance(metadata['authors'], str) else metadata['authors']
                    self.emit_authors_extracted_event(resource_id, authors_list)
                except Exception as e:
                    logger.warning(f"Failed to emit authors.extracted event: {e}")
            
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
    
    def emit_authors_extracted_event(self, resource_id: str, authors: List[Dict]) -> None:
        """
        Emit authors.extracted event after author extraction.
        
        Args:
            resource_id: Resource ID
            authors: List of extracted author dictionaries
        """
        if authors:
            event_bus.emit(
                SystemEvent.AUTHORS_EXTRACTED.value,
                {
                    "resource_id": resource_id,
                    "authors": authors,
                    "author_count": len(authors)
                },
                priority=EventPriority.LOW
            )

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
        """
        Extract LaTeX equations from content.
        Supports both inline ($...$) and display ($$...$$) equations.
        """
        equations = []
        
        # First extract display equations ($$...$$) to avoid conflicts with inline
        display_pattern = r'\$\$(.+?)\$\$'
        for match in re.finditer(display_pattern, content, re.DOTALL):
            equations.append({
                'type': 'display',
                'position': match.start(),
                'latex': match.group(1).strip(),
                'mathml': self._latex_to_mathml(match.group(1).strip()),
                'context': content[max(0, match.start()-50):match.end()+50],
                'confidence': 0.9
            })
        
        # Then extract inline equations ($...$)
        # Use negative lookbehind/lookahead to avoid matching $$
        inline_pattern = r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)'
        for match in re.finditer(inline_pattern, content):
            # Skip if this position is already covered by a display equation
            if not any(eq['position'] <= match.start() < eq['position'] + len(match.group(0)) 
                      for eq in equations if eq['type'] == 'display'):
                equations.append({
                    'type': 'inline',
                    'position': match.start(),
                    'latex': match.group(1).strip(),
                    'mathml': self._latex_to_mathml(match.group(1).strip()),
                    'context': content[max(0, match.start()-50):match.end()+50],
                    'confidence': 0.8
                })
        
        # Sort by position
        equations.sort(key=lambda x: x['position'])
        
        # Renumber positions sequentially
        for i, eq in enumerate(equations):
            eq['position'] = i
        
        return equations[:50]  # Limit to 50 equations
    
    def _latex_to_mathml(self, latex: str) -> Optional[str]:
        """
        Convert LaTeX to MathML.
        Returns None if conversion fails.
        """
        try:
            from latex2mathml.converter import convert
            return convert(latex)
        except Exception as e:
            logger.debug(f"LaTeX to MathML conversion failed: {e}")
            return None

    def _extract_tables_simple(self, content: str) -> List[Dict]:
        """
        Extract tables from HTML and Markdown content.
        Supports both HTML <table> tags and Markdown table syntax.
        """
        tables = []
        
        # Try HTML table extraction first
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            for table_elem in soup.find_all('table'):
                table_data = {
                    'position': len(tables),
                    'caption': None,
                    'headers': [],
                    'rows': [],
                    'format': 'html',
                    'confidence': 0.9
                }
                
                # Extract caption
                caption = table_elem.find('caption')
                if caption:
                    table_data['caption'] = caption.get_text(strip=True)
                
                # Extract headers
                thead = table_elem.find('thead')
                if thead:
                    for th in thead.find_all('th'):
                        table_data['headers'].append(th.get_text(strip=True))
                
                # Extract rows
                tbody = table_elem.find('tbody') or table_elem
                for tr in tbody.find_all('tr'):
                    row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if row and not (thead and tr.parent == thead):  # Skip header rows
                        table_data['rows'].append(row)
                
                if table_data['rows']:  # Only add if we found data
                    tables.append(table_data)
        except Exception as e:
            logger.debug(f"HTML table extraction failed: {e}")
        
        # Try Markdown table extraction
        markdown_tables = self._extract_markdown_tables(content)
        tables.extend(markdown_tables)
        
        # Renumber positions
        for i, table in enumerate(tables):
            table['position'] = i
        
        return tables[:20]  # Limit to 20 tables
    
    def _extract_markdown_tables(self, content: str) -> List[Dict]:
        """Extract tables from Markdown syntax."""
        tables = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line looks like a table row (contains |)
            if '|' in line and line.count('|') >= 2:
                # Check if next line is a separator (contains dashes)
                if i + 1 < len(lines) and re.match(r'^\s*\|?[\s\-:|]+\|[\s\-:|]+', lines[i + 1]):
                    # This is a markdown table
                    table_data = {
                        'position': len(tables),
                        'caption': None,
                        'headers': [],
                        'rows': [],
                        'format': 'markdown',
                        'confidence': 0.85
                    }
                    
                    # Parse header row
                    header_cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    table_data['headers'] = header_cells
                    
                    # Skip separator line
                    i += 2
                    
                    # Parse data rows
                    while i < len(lines):
                        row_line = lines[i].strip()
                        if '|' not in row_line or row_line.count('|') < 2:
                            break
                        
                        row_cells = [cell.strip() for cell in row_line.split('|') if cell.strip()]
                        if row_cells:
                            table_data['rows'].append(row_cells)
                        i += 1
                    
                    # Look for caption in previous line (e.g., "Table 1: Caption")
                    if table_data['position'] > 0 and i > 2:
                        prev_line = lines[i - len(table_data['rows']) - 3].strip()
                        caption_match = re.match(r'Table\s+\d+[:\.]?\s*(.+)', prev_line, re.IGNORECASE)
                        if caption_match:
                            table_data['caption'] = caption_match.group(1).strip()
                    
                    if table_data['rows']:  # Only add if we found data
                        tables.append(table_data)
                    
                    continue
            
            i += 1
        
        return tables

    def _compute_completeness(self, metadata: Dict) -> float:
        """Compute metadata completeness score."""
        required_fields = ['doi', 'authors', 'publication_year']
        optional_fields = ['journal', 'arxiv_id', 'equations', 'tables']
        
        required_score = sum(1 for f in required_fields if metadata.get(f)) / len(required_fields)
        optional_score = sum(1 for f in optional_fields if metadata.get(f)) / len(optional_fields)
        
        # Weighted: 70% required, 30% optional
        return required_score * 0.7 + optional_score * 0.3
    
    def _extract_figures(self, content: str) -> List[Dict]:
        """
        Extract figure captions, alt text, and image sources.
        Supports both HTML <figure> tags and Markdown image syntax.
        """
        figures = []
        
        # Try HTML figure extraction
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            for figure_elem in soup.find_all('figure'):
                fig_data = {
                    'position': len(figures),
                    'caption': None,
                    'alt_text': None,
                    'src': None,
                    'format': 'html',
                    'confidence': 0.9
                }
                
                # Extract caption
                figcaption = figure_elem.find('figcaption')
                if figcaption:
                    fig_data['caption'] = figcaption.get_text(strip=True)
                
                # Extract image
                img = figure_elem.find('img')
                if img:
                    fig_data['alt_text'] = img.get('alt', '')
                    fig_data['src'] = img.get('src', '')
                
                if fig_data['src']:  # Only add if we found an image
                    figures.append(fig_data)
        except Exception as e:
            logger.debug(f"HTML figure extraction failed: {e}")
        
        # Try Markdown image extraction
        # Pattern: ![alt text](image_url "optional title")
        markdown_pattern = r'!\[([^\]]*)\]\(([^\)]+?)(?:\s+"([^"]+)")?\)'
        for match in re.finditer(markdown_pattern, content):
            fig_data = {
                'position': len(figures),
                'caption': match.group(3) if match.group(3) else None,  # Optional title
                'alt_text': match.group(1),  # Alt text
                'src': match.group(2).strip(),  # Image URL
                'format': 'markdown',
                'confidence': 0.85
            }
            figures.append(fig_data)
        
        # Renumber positions
        for i, fig in enumerate(figures):
            fig['position'] = i
        
        return figures
    
    def _extract_affiliations(self, content: str) -> List[str]:
        """
        Extract author affiliations using pattern matching.
        Looks for common affiliation formats.
        """
        affiliations = []
        
        # Common affiliation patterns
        patterns = [
            r'Department of ([^,\n]+),\s*([^,\n]+)',  # Department of X, University Y
            r'([^,\n]+)\s+Laboratory,\s*([^,\n]+)',   # X Laboratory, Y Institute
            r'([^,\n]+)\s+Institute(?:\s+of\s+([^,\n]+))?',  # X Institute [of Y]
            r'School of ([^,\n]+),\s*([^,\n]+)',      # School of X, University Y
            r'([^,\n]+)\s+University',                 # X University
            r'([^,\n]+)\s+College',                    # X College
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Combine tuple elements into full affiliation
                    affiliation = ', '.join(filter(None, match))
                else:
                    affiliation = match
                
                # Clean up and add if not too long (avoid false positives)
                affiliation = affiliation.strip()
                if 5 < len(affiliation) < 200 and affiliation not in affiliations:
                    affiliations.append(affiliation)
        
        return affiliations[:20]  # Limit to 20 affiliations
    
    def _extract_funding(self, content: str) -> List[str]:
        """
        Extract funding information using pattern matching.
        Looks for funding statements and grant numbers.
        """
        funding = []
        
        # Look for funding/acknowledgment sections
        patterns = [
            r'(?:funded by|supported by|funding from)\s+([^.;\n]+)',
            r'(?:grant|grants?)\s+(?:number|no\.?|#)?\s*([A-Z0-9\-]+)',
            r'(?:NSF|NIH|DOE|DARPA|NASA)\s+(?:grant|award)?\s*([A-Z0-9\-]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                funding_info = match.strip() if isinstance(match, str) else ' '.join(match).strip()
                if funding_info and len(funding_info) > 3 and funding_info not in funding:
                    funding.append(funding_info)
        
        return funding[:10]  # Limit to 10 funding sources
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        Extract keywords and subject classifications.
        Looks for explicit keyword sections and metadata.
        """
        keywords = []
        
        # Look for explicit keyword sections
        keyword_pattern = r'(?:keywords?|subjects?|topics?|index terms?):?\s*([^.\n]+)'
        matches = re.findall(keyword_pattern, content, re.IGNORECASE)
        
        for match in matches:
            # Split on common delimiters
            terms = re.split(r'[,;·•]', match)
            for term in terms:
                term = term.strip()
                # Filter out very short or very long terms
                if 2 < len(term) < 50 and term.lower() not in keywords:
                    keywords.append(term)
        
        return keywords[:30]  # Limit to 30 keywords

    def _compute_confidence(self, metadata: Dict) -> float:
        """Compute extraction confidence score."""
        # Simple heuristic: more fields = higher confidence
        field_count = len([v for v in metadata.values() if v])
        max_fields = 10
        return min(field_count / max_fields, 1.0)

