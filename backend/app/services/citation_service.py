"""
Neo Alexandria 2.0 - Citation Service (Phase 6)

This module handles citation extraction, resolution, and graph operations for Neo Alexandria 2.0.
It extracts citations from resource content, resolves internal citations, and computes importance scores.

Related files:
- app/database/models.py: Citation and Resource models
- app/routers/citations.py: Citation API endpoints
- app/services/resource_service.py: Resource ingestion integration
- app/schemas/citation.py: Pydantic schemas for API validation

Features:
- Citation extraction from HTML, PDF, and Markdown content
- Internal citation resolution (matching URLs to existing resources)
- PageRank-style importance scoring
- Citation graph construction for visualization
- Integration with knowledge graph service
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.app.database.models import Citation, Resource
from backend.app.database.base import Base


class CitationService:
    """
    Handles citation extraction, resolution, and graph operations.
    
    This service provides methods for extracting citations from various content types,
    resolving external URLs to internal resources, computing importance scores via
    PageRank, and building citation graphs for visualization.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the citation service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self._parser = None  # Lazy load parser if needed
        
        # Ensure tables exist
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass
    
    def extract_citations(self, resource_id: str) -> List[Dict[str, Any]]:
        """
        Extract citations from resource content.
        
        Algorithm:
        1. Retrieve resource from database
        2. Determine content type (HTML, PDF, Markdown)
        3. Parse content based on type:
           - HTML: Extract <a href="..."> links, <cite> tags
           - PDF: Use pdfplumber to extract hyperlinks and reference sections
           - Markdown: Parse [text](url) syntax
        4. For each extracted citation:
           - Extract URL
           - Determine citation type (heuristic: .csv/.json → dataset, github → code, else reference)
           - Extract context snippet (50 chars before/after)
           - Record position in document
        5. Return list of citation dicts
        
        Args:
            resource_id: UUID of the resource to extract citations from
            
        Returns:
            List of citation dictionaries with keys: target_url, citation_type, context_snippet, position
            
        Raises:
            ValueError: If resource not found
        """
        # Convert string resource_id to UUID
        try:
            resource_uuid = uuid.UUID(resource_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid resource ID: {resource_id}")
        
        # Retrieve resource
        result = self.db.execute(
            select(Resource).filter(Resource.id == resource_uuid)
        )
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise ValueError(f"Resource not found: {resource_id}")
        
        # Check if resource has content
        if not resource.identifier:
            return []
        
        # Determine content type and extract citations
        content_type = resource.format or ""
        citations = []
        
        try:
            if "html" in content_type.lower():
                citations = self._extract_from_html(resource)
            elif "pdf" in content_type.lower():
                citations = self._extract_from_pdf(resource)
            elif "markdown" in content_type.lower() or "md" in content_type.lower():
                citations = self._extract_from_markdown(resource)
            else:
                # Try HTML as fallback
                citations = self._extract_from_html(resource)
        except Exception as e:
            # Log warning but return partial results
            print(f"Warning: Citation extraction failed for {resource_id}: {e}")
            return citations
        
        # Store citations in database
        for i, citation_data in enumerate(citations):
            citation = Citation(
                source_resource_id=resource_uuid,
                target_url=citation_data["target_url"],
                citation_type=citation_data.get("citation_type", "reference"),
                context_snippet=citation_data.get("context_snippet"),
                position=citation_data.get("position", i)
            )
            self.db.add(citation)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Warning: Failed to save citations for {resource_id}: {e}")
        
        return citations
    
    def _extract_from_html(self, resource: Resource) -> List[Dict[str, Any]]:
        """Extract citations from HTML content."""
        citations = []
        
        # Read HTML content from archived file
        if not resource.identifier:
            return citations
        
        try:
            archive_path = Path(resource.identifier)
            if not archive_path.exists():
                return citations
            
            # Read HTML file
            html_file = archive_path / "content.html"
            if not html_file.exists():
                return citations
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML and extract links
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all <a> tags with href
            for i, link in enumerate(soup.find_all('a', href=True)):
                url = link['href']
                
                # Skip internal anchors and javascript
                if url.startswith('#') or url.startswith('javascript:'):
                    continue
                
                # Determine citation type
                citation_type = self._classify_citation_type(url)
                
                # Extract context (text around the link)
                context = self._extract_context(link, html_content)
                
                citations.append({
                    "target_url": url,
                    "citation_type": citation_type,
                    "context_snippet": context,
                    "position": i
                })
        
        except Exception as e:
            print(f"Warning: HTML citation extraction failed: {e}")
        
        return citations[:50]  # Limit to first 50 citations
    
    def _extract_from_pdf(self, resource: Resource) -> List[Dict[str, Any]]:
        """Extract citations from PDF content."""
        citations = []
        
        # PDF extraction requires pdfplumber
        try:
            import pdfplumber
        except ImportError:
            print("Warning: pdfplumber not installed, skipping PDF citation extraction")
            return citations
        
        if not resource.identifier:
            return citations
        
        try:
            archive_path = Path(resource.identifier)
            if not archive_path.exists():
                return citations
            
            # Look for PDF file
            pdf_file = archive_path / "content.pdf"
            if not pdf_file.exists():
                return citations
            
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract hyperlinks if available
                    if hasattr(page, 'hyperlinks'):
                        for i, link in enumerate(page.hyperlinks):
                            url = link.get('uri', '')
                            if url:
                                citation_type = self._classify_citation_type(url)
                                citations.append({
                                    "target_url": url,
                                    "citation_type": citation_type,
                                    "context_snippet": None,
                                    "position": page_num * 100 + i
                                })
                    
                    # Extract URLs from text using regex
                    text = page.extract_text() or ""
                    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
                    for i, url in enumerate(urls):
                        citation_type = self._classify_citation_type(url)
                        citations.append({
                            "target_url": url,
                            "citation_type": citation_type,
                            "context_snippet": None,
                            "position": page_num * 100 + len(citations) + i
                        })
        
        except Exception as e:
            print(f"Warning: PDF citation extraction failed: {e}")
        
        return citations[:50]  # Limit to first 50 citations
    
    def _extract_from_markdown(self, resource: Resource) -> List[Dict[str, Any]]:
        """Extract citations from Markdown content."""
        citations = []
        
        if not resource.identifier:
            return citations
        
        try:
            archive_path = Path(resource.identifier)
            if not archive_path.exists():
                return citations
            
            # Read markdown file
            md_file = archive_path / "content.md"
            if not md_file.exists():
                # Try text file
                md_file = archive_path / "content.txt"
                if not md_file.exists():
                    return citations
            
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Extract markdown links [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            matches = re.finditer(link_pattern, md_content)
            
            for i, match in enumerate(matches):
                url = match.group(2)
                
                # Skip internal anchors
                if url.startswith('#'):
                    continue
                
                citation_type = self._classify_citation_type(url)
                
                # Extract context around the link
                start = max(0, match.start() - 50)
                end = min(len(md_content), match.end() + 50)
                context = md_content[start:end]
                
                citations.append({
                    "target_url": url,
                    "citation_type": citation_type,
                    "context_snippet": context,
                    "position": i
                })
        
        except Exception as e:
            print(f"Warning: Markdown citation extraction failed: {e}")
        
        return citations[:50]  # Limit to first 50 citations
    
    def _classify_citation_type(self, url: str) -> str:
        """
        Classify citation type based on URL heuristics.
        
        Args:
            url: The URL to classify
            
        Returns:
            Citation type: "dataset", "code", "reference", or "general"
        """
        url_lower = url.lower()
        
        # Dataset indicators
        if any(ext in url_lower for ext in ['.csv', '.json', '.xml', '.xlsx', '.tsv']):
            return "dataset"
        
        # Code repository indicators
        if any(domain in url_lower for domain in ['github.com', 'gitlab.com', 'bitbucket.org']):
            return "code"
        
        # Academic/reference indicators
        if any(domain in url_lower for domain in ['doi.org', 'arxiv.org', 'scholar.google', 'pubmed']):
            return "reference"
        
        return "general"
    
    def _extract_context(self, element, full_text: str, window: int = 50) -> str:
        """
        Extract context around an element in text.
        
        Args:
            element: BeautifulSoup element
            full_text: Full text content
            window: Number of characters before/after
            
        Returns:
            Context snippet
        """
        try:
            # Get text content of the element
            element_text = element.get_text()
            
            # Find position in full text
            pos = full_text.find(element_text)
            if pos == -1:
                return element_text[:100]
            
            # Extract window around position
            start = max(0, pos - window)
            end = min(len(full_text), pos + len(element_text) + window)
            
            return full_text[start:end]
        except Exception:
            return ""

    
    def resolve_internal_citations(self, citation_ids: Optional[List[str]] = None) -> int:
        """
        Match citation target URLs to existing resources.
        
        Algorithm:
        1. Query citations where target_resource_id IS NULL
        2. For each citation:
           - Normalize target_url (strip fragments, trailing slashes)
           - Query Resource table: WHERE url = normalized_target_url OR alternate_url = normalized_target_url
           - If match found → update citation.target_resource_id
        3. Return count of resolved citations
        
        Args:
            citation_ids: Optional list of specific citation IDs to resolve. If None, resolves all unresolved.
            
        Returns:
            Count of resolved citations
        """
        # Query unresolved citations
        query = select(Citation).filter(Citation.target_resource_id.is_(None))
        
        if citation_ids:
            # Convert string IDs to UUIDs
            uuid_ids = []
            for cid in citation_ids:
                try:
                    uuid_ids.append(uuid.UUID(cid))
                except (ValueError, TypeError):
                    continue
            
            if uuid_ids:
                query = query.filter(Citation.id.in_(uuid_ids))
        
        result = self.db.execute(query)
        unresolved_citations = result.scalars().all()
        
        resolved_count = 0
        
        # Process in batches of 100
        batch_size = 100
        for i in range(0, len(unresolved_citations), batch_size):
            batch = unresolved_citations[i:i + batch_size]
            
            for citation in batch:
                # Normalize URL
                normalized_url = self._normalize_url(citation.target_url)
                
                # Try to find matching resource
                resource_result = self.db.execute(
                    select(Resource).filter(
                        func.lower(Resource.source) == normalized_url.lower()
                    )
                )
                matching_resource = resource_result.scalar_one_or_none()
                
                if matching_resource:
                    citation.target_resource_id = matching_resource.id
                    self.db.add(citation)
                    resolved_count += 1
            
            # Commit batch
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                print(f"Warning: Failed to commit citation resolution batch: {e}")
        
        return resolved_count
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.
        
        Removes fragments, trailing slashes, and normalizes scheme.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            # Remove fragment and normalize
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip('/'),
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))
            return normalized
        except Exception:
            return url.lower().rstrip('/')
    
    def get_citation_graph(self, resource_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        Build citation graph for visualization.
        
        Returns:
        {
            "nodes": [{"id": resource_id, "title": str, "type": "source"|"cited"|"citing"}],
            "edges": [{"source": resource_id, "target": resource_id, "type": citation_type}]
        }
        
        Algorithm:
        1. Start with focal resource (depth 0)
        2. Get outbound citations (resources this one cites)
        3. Get inbound citations (resources that cite this one)
        4. If depth > 1, recursively expand neighbors
        5. Build nodes list (deduplicated resources)
        6. Build edges list (citation relationships)
        
        Args:
            resource_id: UUID of the focal resource
            depth: Graph depth (max 2)
            
        Returns:
            Dictionary with nodes and edges lists
        """
        # Limit depth to prevent exponential explosion
        depth = min(depth, 2)
        
        # Convert string resource_id to UUID
        try:
            resource_uuid = uuid.UUID(resource_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid resource ID: {resource_id}")
        
        # Check if resource exists
        result = self.db.execute(
            select(Resource).filter(Resource.id == resource_uuid)
        )
        focal_resource = result.scalar_one_or_none()
        
        if not focal_resource:
            raise ValueError(f"Resource not found: {resource_id}")
        
        # Track visited nodes and edges
        nodes_dict = {}
        edges_list = []
        visited = set()
        
        # Add focal resource
        nodes_dict[str(resource_uuid)] = {
            "id": str(resource_uuid),
            "title": focal_resource.title,
            "type": "source"
        }
        
        # BFS traversal
        queue = [(resource_uuid, 0)]
        
        while queue and len(nodes_dict) < 100:  # Limit to 100 nodes
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_depth >= depth:
                continue
            
            # Get outbound citations
            outbound_result = self.db.execute(
                select(Citation).filter(
                    Citation.source_resource_id == current_id,
                    Citation.target_resource_id.isnot(None)
                )
            )
            outbound_citations = outbound_result.scalars().all()
            
            for citation in outbound_citations:
                target_id = citation.target_resource_id
                
                # Add edge
                edges_list.append({
                    "source": str(current_id),
                    "target": str(target_id),
                    "type": citation.citation_type
                })
                
                # Add target node if not already present
                if str(target_id) not in nodes_dict:
                    target_result = self.db.execute(
                        select(Resource).filter(Resource.id == target_id)
                    )
                    target_resource = target_result.scalar_one_or_none()
                    
                    if target_resource:
                        nodes_dict[str(target_id)] = {
                            "id": str(target_id),
                            "title": target_resource.title,
                            "type": "cited"
                        }
                        
                        # Add to queue for next depth
                        if current_depth + 1 < depth:
                            queue.append((target_id, current_depth + 1))
            
            # Get inbound citations
            inbound_result = self.db.execute(
                select(Citation).filter(
                    Citation.target_resource_id == current_id
                )
            )
            inbound_citations = inbound_result.scalars().all()
            
            for citation in inbound_citations:
                source_id = citation.source_resource_id
                
                # Add edge
                edges_list.append({
                    "source": str(source_id),
                    "target": str(current_id),
                    "type": citation.citation_type
                })
                
                # Add source node if not already present
                if str(source_id) not in nodes_dict:
                    source_result = self.db.execute(
                        select(Resource).filter(Resource.id == source_id)
                    )
                    source_resource = source_result.scalar_one_or_none()
                    
                    if source_resource:
                        nodes_dict[str(source_id)] = {
                            "id": str(source_id),
                            "title": source_resource.title,
                            "type": "citing"
                        }
                        
                        # Add to queue for next depth
                        if current_depth + 1 < depth:
                            queue.append((source_id, current_depth + 1))
        
        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges_list
        }
    
    def compute_citation_importance(self, resource_ids: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Calculate PageRank-style importance scores.
        
        Algorithm:
        1. Build citation adjacency matrix (sparse)
        2. Run PageRank algorithm:
           - Damping factor: 0.85
           - Max iterations: 100
           - Convergence threshold: 1e-6
        3. Normalize scores to [0, 1]
        4. Update Citation.importance_score for all citations
        5. Return dict mapping resource_id → importance_score
        
        Args:
            resource_ids: Optional list of resource IDs to compute scores for. If None, computes for all.
            
        Returns:
            Dictionary mapping resource_id to importance score
        """
        try:
            import networkx as nx
        except ImportError:
            print("Warning: networkx not installed, skipping PageRank computation")
            return {}
        
        # Build citation graph
        G = nx.DiGraph()
        
        # Query all citations with resolved targets
        query = select(Citation).filter(Citation.target_resource_id.isnot(None))
        
        if resource_ids:
            # Convert string IDs to UUIDs
            uuid_ids = []
            for rid in resource_ids:
                try:
                    uuid_ids.append(uuid.UUID(rid))
                except (ValueError, TypeError):
                    continue
            
            if uuid_ids:
                query = query.filter(
                    (Citation.source_resource_id.in_(uuid_ids)) |
                    (Citation.target_resource_id.in_(uuid_ids))
                )
        
        result = self.db.execute(query)
        citations = result.scalars().all()
        
        # Add edges to graph
        for citation in citations:
            G.add_edge(
                str(citation.source_resource_id),
                str(citation.target_resource_id)
            )
        
        if len(G.nodes()) == 0:
            return {}
        
        # Compute PageRank
        try:
            pagerank_scores = nx.pagerank(
                G,
                alpha=0.85,
                max_iter=100,
                tol=1e-6
            )
        except Exception as e:
            print(f"Warning: PageRank computation failed: {e}")
            return {}
        
        # Normalize scores to [0, 1]
        if pagerank_scores:
            max_score = max(pagerank_scores.values())
            min_score = min(pagerank_scores.values())
            score_range = max_score - min_score
            
            if score_range > 0:
                normalized_scores = {
                    k: (v - min_score) / score_range
                    for k, v in pagerank_scores.items()
                }
            else:
                normalized_scores = {k: 0.5 for k in pagerank_scores.keys()}
        else:
            normalized_scores = {}
        
        # Update citation importance scores
        for citation in citations:
            target_id = str(citation.target_resource_id)
            
            # Use target's PageRank as citation importance
            if target_id in normalized_scores:
                citation.importance_score = normalized_scores[target_id]
                self.db.add(citation)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Warning: Failed to update citation importance scores: {e}")
        
        return normalized_scores
    
    def create_citation(self, citation_data: Dict[str, Any]) -> Citation:
        """
        Create a new citation record.
        
        Args:
            citation_data: Dictionary with citation fields
            
        Returns:
            Created Citation object
        """
        # Convert string IDs to UUIDs
        source_id = citation_data.get("source_resource_id")
        target_id = citation_data.get("target_resource_id")
        
        try:
            source_uuid = uuid.UUID(source_id) if source_id else None
            target_uuid = uuid.UUID(target_id) if target_id else None
        except (ValueError, TypeError):
            raise ValueError("Invalid resource ID format")
        
        if not source_uuid:
            raise ValueError("source_resource_id is required")
        
        citation = Citation(
            source_resource_id=source_uuid,
            target_resource_id=target_uuid,
            target_url=citation_data.get("target_url", ""),
            citation_type=citation_data.get("citation_type", "reference"),
            context_snippet=citation_data.get("context_snippet"),
            position=citation_data.get("position")
        )
        
        self.db.add(citation)
        self.db.commit()
        self.db.refresh(citation)
        
        return citation
    
    def get_citations_for_resource(
        self,
        resource_id: str,
        direction: str = "both"
    ) -> List[Citation]:
        """
        Get citations for a resource.
        
        Args:
            resource_id: UUID of the resource
            direction: "outbound" (this resource cites), "inbound" (cites this resource), "both"
            
        Returns:
            List of Citation objects
        """
        # Convert string resource_id to UUID
        try:
            resource_uuid = uuid.UUID(resource_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid resource ID: {resource_id}")
        
        citations = []
        
        if direction in ["outbound", "both"]:
            # Get outbound citations
            outbound_result = self.db.execute(
                select(Citation).filter(Citation.source_resource_id == resource_uuid)
            )
            citations.extend(outbound_result.scalars().all())
        
        if direction in ["inbound", "both"]:
            # Get inbound citations
            inbound_result = self.db.execute(
                select(Citation).filter(Citation.target_resource_id == resource_uuid)
            )
            citations.extend(inbound_result.scalars().all())
        
        return citations
