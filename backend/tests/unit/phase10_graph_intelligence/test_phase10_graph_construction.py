"""
Unit tests for Phase 10 multi-layer graph construction.

Tests:
- Citation edge creation
- Co-authorship edge creation
- Subject similarity edge creation
- Temporal edge creation
- Graph caching
- Edge weight calculations
"""

import json

from backend.app.services.graph_service import GraphService
from backend.app.database.models import Resource, Citation, ResourceTaxonomy, TaxonomyNode, GraphEdge


class TestMultiLayerGraphConstruction:
    """Test multi-layer graph construction functionality."""
    
    def test_citation_edge_creation(self, test_db):
        """Test that citation edges are created correctly from Citation table."""
        db = test_db()
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            source="https://example.com/paper-a",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_b = Resource(
            title="Paper B",
            source="https://example.com/paper-b",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add(resource_a)
        db.add(resource_b)
        db.commit()
        db.refresh(resource_a)
        db.refresh(resource_b)
        
        # Create citation: A cites B (target_url is required)
        citation = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url=resource_b.source or "https://example.com/paper-b",
            citation_type="direct",
            context_snippet="As shown in [1]..."
        )
        db.add(citation)
        db.commit()
        
        # Build graph
        graph_service = GraphService(db)
        G = graph_service.build_multilayer_graph()
        
        # Verify citation edge exists
        assert G.has_node(str(resource_a.id))
        assert G.has_node(str(resource_b.id))
        assert G.has_edge(str(resource_a.id), str(resource_b.id))
        
        # Verify edge properties
        edge_data = G.get_edge_data(str(resource_a.id), str(resource_b.id))
        assert edge_data is not None
        
        # Find citation edge
        citation_edge = None
        for key, data in edge_data.items():
            if data.get("edge_type") == "citation":
                citation_edge = data
                break
        
        assert citation_edge is not None
        assert citation_edge["weight"] == 1.0
        assert citation_edge["edge_type"] == "citation"
        
        # Verify edge persisted to database
        db_edge = db.query(GraphEdge).filter(
            GraphEdge.source_id == resource_a.id,
            GraphEdge.target_id == resource_b.id,
            GraphEdge.edge_type == "citation"
        ).first()
        
        assert db_edge is not None
        assert db_edge.weight == 1.0
        
        # Cleanup
        db.delete(citation)
        db.delete(resource_a)
        db.delete(resource_b)
        db.commit()
        db.close()
    
    def test_coauthorship_edge_creation(self, test_db):
        """Test that co-authorship edges are created for resources sharing authors."""
        db = test_db()
        
        # Create resources with shared authors
        authors_json = json.dumps([
            {"name": "John Doe"},
            {"name": "Jane Smith"}
        ])
        
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            authors=authors_json
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            authors=json.dumps([
                {"name": "Jane Smith"},
                {"name": "Bob Johnson"}
            ])
        )
        db.add(resource_a)
        db.add(resource_b)
        db.commit()
        db.refresh(resource_a)
        db.refresh(resource_b)
        
        # Build graph
        graph_service = GraphService(db)
        G = graph_service.build_multilayer_graph()
        
        # Verify co-authorship edges exist (bidirectional)
        assert G.has_edge(str(resource_a.id), str(resource_b.id))
        assert G.has_edge(str(resource_b.id), str(resource_a.id))
        
        # Verify edge properties
        edge_data_ab = G.get_edge_data(str(resource_a.id), str(resource_b.id))
        
        # Find co-authorship edge
        coauthor_edge = None
        for key, data in edge_data_ab.items():
            if data.get("edge_type") == "co_authorship":
                coauthor_edge = data
                break
        
        assert coauthor_edge is not None
        # Weight should be 1.0 / num_shared_authors = 1.0 / 1 = 1.0
        assert coauthor_edge["weight"] == 1.0
        assert coauthor_edge["edge_type"] == "co_authorship"
        
        # Cleanup
        db.delete(resource_a)
        db.delete(resource_b)
        db.commit()
        db.close()
    
    def test_subject_similarity_edge_creation(self, test_db):
        """Test that subject similarity edges are created from ResourceTaxonomy."""
        db = test_db()
        
        # Create taxonomy node (use 'name' not 'code', and 'slug' is required)
        taxonomy_node = TaxonomyNode(
            name="Computer Science",
            slug="computer-science",
            path="/computer-science",
            level=1
        )
        db.add(taxonomy_node)
        db.commit()
        db.refresh(taxonomy_node)
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            source="https://example.com/paper-a",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_b = Resource(
            title="Paper B",
            source="https://example.com/paper-b",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add(resource_a)
        db.add(resource_b)
        db.commit()
        db.refresh(resource_a)
        db.refresh(resource_b)
        
        # Create taxonomy associations
        rt_a = ResourceTaxonomy(
            resource_id=resource_a.id,
            taxonomy_node_id=taxonomy_node.id,
            confidence=0.9,
            is_predicted=False,
            predicted_by="manual"
        )
        rt_b = ResourceTaxonomy(
            resource_id=resource_b.id,
            taxonomy_node_id=taxonomy_node.id,
            confidence=0.85,
            is_predicted=False,
            predicted_by="manual"
        )
        db.add(rt_a)
        db.add(rt_b)
        db.commit()
        
        # Build graph
        graph_service = GraphService(db)
        G = graph_service.build_multilayer_graph()
        
        # Verify subject similarity edges exist (bidirectional)
        assert G.has_edge(str(resource_a.id), str(resource_b.id))
        assert G.has_edge(str(resource_b.id), str(resource_a.id))
        
        # Verify edge properties
        edge_data_ab = G.get_edge_data(str(resource_a.id), str(resource_b.id))
        
        # Find subject similarity edge
        subject_edge = None
        for key, data in edge_data_ab.items():
            if data.get("edge_type") == "subject_similarity":
                subject_edge = data
                break
        
        assert subject_edge is not None
        assert subject_edge["weight"] == 0.5
        assert subject_edge["edge_type"] == "subject_similarity"
        
        # Cleanup
        db.delete(rt_a)
        db.delete(rt_b)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(taxonomy_node)
        db.commit()
        db.close()
    
    def test_temporal_edge_creation(self, test_db):
        """Test that temporal edges are created for resources from same year."""
        db = test_db()
        
        # Create resources with same publication year
        resource_a = Resource(
            title="Paper A",
            source="https://example.com/paper-a",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023
        )
        resource_b = Resource(
            title="Paper B",
            source="https://example.com/paper-b",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023
        )
        db.add(resource_a)
        db.add(resource_b)
        db.commit()
        db.refresh(resource_a)
        db.refresh(resource_b)
        
        # Build graph
        graph_service = GraphService(db)
        G = graph_service.build_multilayer_graph()
        
        # Verify temporal edges exist (bidirectional)
        assert G.has_edge(str(resource_a.id), str(resource_b.id))
        assert G.has_edge(str(resource_b.id), str(resource_a.id))
        
        # Verify edge properties
        edge_data_ab = G.get_edge_data(str(resource_a.id), str(resource_b.id))
        
        # Find temporal edge
        temporal_edge = None
        for key, data in edge_data_ab.items():
            if data.get("edge_type") == "temporal":
                temporal_edge = data
                break
        
        assert temporal_edge is not None
        assert temporal_edge["weight"] == 0.3
        assert temporal_edge["edge_type"] == "temporal"
        assert temporal_edge["metadata"]["year"] == 2023
        
        # Cleanup
        db.delete(resource_a)
        db.delete(resource_b)
        db.commit()
        db.close()
    
    def test_graph_caching(self, test_db):
        """Test that graph is cached and reused."""
        db = test_db()
        
        # Create a resource
        resource = Resource(
            title="Test Paper",
            source="https://example.com/test-paper",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add(resource)
        db.commit()
        
        # Build graph first time
        graph_service = GraphService(db)
        G1 = graph_service.build_multilayer_graph()
        
        # Verify cache is set
        assert graph_service._graph_cache is not None
        assert graph_service._cache_timestamp is not None
        
        # Build graph second time (should use cache)
        G2 = graph_service.build_multilayer_graph()
        
        # Should return same graph object
        assert G1 is G2
        
        # Force refresh
        G3 = graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Should return different graph object
        assert G1 is not G3
        
        # Cleanup
        db.delete(resource)
        db.commit()
        db.close()
    
    def test_edge_weight_calculations(self, test_db):
        """Test that edge weights are calculated correctly for each type."""
        db = test_db()
        
        # Create resources with multiple edge types
        authors_json = json.dumps([
            {"name": "John Doe"},
            {"name": "Jane Smith"},
            {"name": "Bob Johnson"}
        ])
        
        resource_a = Resource(
            title="Paper A",
            source="https://example.com/paper-a",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            authors=authors_json
        )
        resource_b = Resource(
            title="Paper B",
            source="https://example.com/paper-b",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            authors=json.dumps([
                {"name": "Jane Smith"},
                {"name": "Bob Johnson"}
            ])
        )
        db.add(resource_a)
        db.add(resource_b)
        db.commit()
        db.refresh(resource_a)
        db.refresh(resource_b)
        
        # Create citation (target_url is required)
        citation = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url=resource_b.source or "https://example.com/paper-b",
            citation_type="direct"
        )
        db.add(citation)
        db.commit()
        
        # Build graph
        graph_service = GraphService(db)
        G = graph_service.build_multilayer_graph()
        
        # Get all edges between A and B
        edge_data = G.get_edge_data(str(resource_a.id), str(resource_b.id))
        
        # Collect edge types and weights
        edges_by_type = {}
        for key, data in edge_data.items():
            edge_type = data.get("edge_type")
            weight = data.get("weight")
            edges_by_type[edge_type] = weight
        
        # Verify citation edge weight
        assert "citation" in edges_by_type
        assert edges_by_type["citation"] == 1.0
        
        # Verify co-authorship edge weight (2 shared authors)
        assert "co_authorship" in edges_by_type
        assert edges_by_type["co_authorship"] == 0.5  # 1.0 / 2 shared authors
        
        # Verify temporal edge weight
        assert "temporal" in edges_by_type
        assert edges_by_type["temporal"] == 0.3
        
        # Cleanup
        db.delete(citation)
        db.delete(resource_a)
        db.delete(resource_b)
        db.commit()
        db.close()
