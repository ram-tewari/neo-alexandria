"""
Neo Alexandria 2.0 - Phase 6 Citation Tests

This module tests the citation extraction, resolution, and graph functionality.
"""

import pytest
import uuid
from datetime import datetime, timezone

from backend.app.database.models import Resource, Citation
from backend.app.services.citation_service import CitationService


@pytest.fixture
def db_session(test_db):
    """Create a database session for tests."""
    db = test_db()
    try:
        yield db
    finally:
        db.close()


class TestCitationModel:
    """Test Citation model creation and relationships."""
    
    def test_create_citation(self, db_session):
        """Test creating a citation record."""
        # Create two resources
        resource1 = Resource(
            title="Source Resource",
            source="https://example.com/source",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Target Resource",
            source="https://example.com/target",
            read_status="unread",
            quality_score=0.9
        )
        db_session.add(resource1)
        db_session.add(resource2)
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        
        # Create citation
        citation = Citation(
            source_resource_id=resource1.id,
            target_resource_id=resource2.id,
            target_url="https://example.com/target",
            citation_type="reference",
            context_snippet="This is a reference to the target",
            position=1
        )
        db_session.add(citation)
        db_session.commit()
        db_session.refresh(citation)
        
        assert citation.id is not None
        assert citation.source_resource_id == resource1.id
        assert citation.target_resource_id == resource2.id
        assert citation.citation_type == "reference"


class TestCitationService:
    """Test CitationService methods."""
    
    def test_service_initialization(self, db_session):
        """Test CitationService initialization."""
        service = CitationService(db_session)
        assert service.db == db_session
    
    def test_normalize_url(self, db_session):
        """Test URL normalization."""
        service = CitationService(db_session)
        
        # Test fragment removal
        assert service._normalize_url("https://example.com/page#section") == "https://example.com/page"
        
        # Test trailing slash removal
        assert service._normalize_url("https://example.com/page/") == "https://example.com/page"
        
        # Test case normalization
        assert service._normalize_url("HTTPS://EXAMPLE.COM/Page") == "https://example.com/Page"
    
    def test_classify_citation_type(self, db_session):
        """Test citation type classification."""
        service = CitationService(db_session)
        
        # Test dataset classification
        assert service._classify_citation_type("https://example.com/data.csv") == "dataset"
        assert service._classify_citation_type("https://example.com/data.json") == "dataset"
        
        # Test code classification
        assert service._classify_citation_type("https://github.com/user/repo") == "code"
        assert service._classify_citation_type("https://gitlab.com/user/repo") == "code"
        
        # Test reference classification
        assert service._classify_citation_type("https://doi.org/10.1234/example") == "reference"
        assert service._classify_citation_type("https://arxiv.org/abs/1234.5678") == "reference"
        
        # Test general classification
        assert service._classify_citation_type("https://example.com/page") == "general"
    
    def test_create_citation(self, db_session):
        """Test creating a citation via service."""
        # Create resources
        resource1 = Resource(
            title="Source",
            source="https://example.com/source",
            read_status="unread",
            quality_score=0.8
        )
        db_session.add(resource1)
        db_session.commit()
        db_session.refresh(resource1)
        
        service = CitationService(db_session)
        
        citation_data = {
            "source_resource_id": str(resource1.id),
            "target_url": "https://example.com/target",
            "citation_type": "reference",
            "context_snippet": "Test context"
        }
        
        citation = service.create_citation(citation_data)
        
        assert citation.id is not None
        assert citation.source_resource_id == resource1.id
        assert citation.target_url == "https://example.com/target"
    
    def test_get_citations_for_resource(self, db_session):
        """Test retrieving citations for a resource."""
        # Create resources
        resource1 = Resource(
            title="Source",
            source="https://example.com/source",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Target",
            source="https://example.com/target",
            read_status="unread",
            quality_score=0.9
        )
        db_session.add_all([resource1, resource2])
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        
        # Create outbound citation
        citation1 = Citation(
            source_resource_id=resource1.id,
            target_resource_id=resource2.id,
            target_url="https://example.com/target",
            citation_type="reference"
        )
        
        # Create inbound citation
        citation2 = Citation(
            source_resource_id=resource2.id,
            target_resource_id=resource1.id,
            target_url="https://example.com/source",
            citation_type="reference"
        )
        
        db_session.add_all([citation1, citation2])
        db_session.commit()
        
        service = CitationService(db_session)
        
        # Test outbound only
        outbound = service.get_citations_for_resource(str(resource1.id), direction="outbound")
        assert len(outbound) == 1
        assert outbound[0].target_resource_id == resource2.id
        
        # Test inbound only
        inbound = service.get_citations_for_resource(str(resource1.id), direction="inbound")
        assert len(inbound) == 1
        assert inbound[0].source_resource_id == resource2.id
        
        # Test both
        both = service.get_citations_for_resource(str(resource1.id), direction="both")
        assert len(both) == 2
    
    def test_resolve_internal_citations(self, db_session):
        """Test resolving citations to internal resources."""
        # Create resources
        resource1 = Resource(
            title="Source",
            source="https://example.com/source",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Target",
            source="https://example.com/target",
            read_status="unread",
            quality_score=0.9
        )
        db_session.add_all([resource1, resource2])
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        
        # Create unresolved citation
        citation = Citation(
            source_resource_id=resource1.id,
            target_url="https://example.com/target",
            citation_type="reference"
        )
        db_session.add(citation)
        db_session.commit()
        db_session.refresh(citation)
        
        assert citation.target_resource_id is None
        
        service = CitationService(db_session)
        resolved_count = service.resolve_internal_citations()
        
        assert resolved_count == 1
        
        # Refresh citation
        db_session.refresh(citation)
        assert citation.target_resource_id == resource2.id


class TestCitationGraph:
    """Test citation graph construction."""
    
    def test_get_citation_graph_simple(self, db_session):
        """Test building a simple citation graph."""
        # Create resources
        resource1 = Resource(
            title="Resource 1",
            source="https://example.com/1",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Resource 2",
            source="https://example.com/2",
            read_status="unread",
            quality_score=0.9
        )
        resource3 = Resource(
            title="Resource 3",
            source="https://example.com/3",
            read_status="unread",
            quality_score=0.7
        )
        db_session.add_all([resource1, resource2, resource3])
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        db_session.refresh(resource3)
        
        # Create citations: 1 -> 2, 2 -> 3
        citation1 = Citation(
            source_resource_id=resource1.id,
            target_resource_id=resource2.id,
            target_url="https://example.com/2",
            citation_type="reference"
        )
        citation2 = Citation(
            source_resource_id=resource2.id,
            target_resource_id=resource3.id,
            target_url="https://example.com/3",
            citation_type="reference"
        )
        db_session.add_all([citation1, citation2])
        db_session.commit()
        
        service = CitationService(db_session)
        graph = service.get_citation_graph(str(resource1.id), depth=1)
        
        assert len(graph["nodes"]) >= 2  # At least resource1 and resource2
        assert len(graph["edges"]) >= 1  # At least one edge
        
        # Check that resource1 is the source
        node_ids = [node["id"] for node in graph["nodes"]]
        assert str(resource1.id) in node_ids


class TestCitationEndpoints:
    """Test citation API endpoints."""
    
    def test_get_resource_citations_endpoint(self, client, db_session):
        """Test GET /citations/resources/{id}/citations endpoint."""
        # Create resources
        resource1 = Resource(
            title="Source",
            source="https://example.com/source",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Target",
            source="https://example.com/target",
            read_status="unread",
            quality_score=0.9
        )
        db_session.add_all([resource1, resource2])
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        
        # Create citation
        citation = Citation(
            source_resource_id=resource1.id,
            target_resource_id=resource2.id,
            target_url="https://example.com/target",
            citation_type="reference"
        )
        db_session.add(citation)
        db_session.commit()
        
        # Test endpoint
        response = client.get(f"/citations/resources/{resource1.id}/citations")
        assert response.status_code == 200
        
        data = response.json()
        assert "outbound" in data
        assert "inbound" in data
        assert "counts" in data
        assert data["counts"]["outbound"] == 1
    
    def test_citation_graph_endpoint(self, client, db_session):
        """Test GET /citations/graph/citations endpoint."""
        # Create resources
        resource1 = Resource(
            title="Resource 1",
            source="https://example.com/1",
            read_status="unread",
            quality_score=0.8
        )
        resource2 = Resource(
            title="Resource 2",
            source="https://example.com/2",
            read_status="unread",
            quality_score=0.9
        )
        db_session.add_all([resource1, resource2])
        db_session.commit()
        db_session.refresh(resource1)
        db_session.refresh(resource2)
        
        # Create citation
        citation = Citation(
            source_resource_id=resource1.id,
            target_resource_id=resource2.id,
            target_url="https://example.com/2",
            citation_type="reference"
        )
        db_session.add(citation)
        db_session.commit()
        
        # Test endpoint
        response = client.get("/citations/graph/citations")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
