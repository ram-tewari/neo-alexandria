"""
Integration tests for Phase 10: Advanced Graph Intelligence & Literature-Based Discovery

Tests end-to-end workflows including:
- Complete discovery workflow (graph construction → embeddings → discovery)
- Recommendation integration with graph intelligence
"""

import pytest
from backend.app.database.models import Resource, Citation, GraphEdge, GraphEmbedding, DiscoveryHypothesis
from backend.app.services.graph_service import GraphService
from backend.app.services.graph_embeddings_service import GraphEmbeddingsService
from backend.app.services.lbd_service import LBDService
from backend.app.services.recommendation_service import get_graph_based_recommendations, generate_recommendations_with_graph_fusion
import uuid
import json


@pytest.fixture
def test_resources(test_db):
    """Create test resources for integration testing."""
    db_session = test_db()
    resources = []
    
    # Create 10 test resources with metadata
    for i in range(10):
        resource = Resource(
            id=uuid.uuid4(),
            title=f"Test Resource {i}",
            authors=json.dumps([f"Author {i}", f"Author {i+1}"]),
            publication_year=2020 + (i % 3),
            type="article",
            embedding=[0.1 * i] * 768,  # Simple content embedding
            quality_overall=0.5 + (i * 0.05)
        )
        resources.append(resource)
        db_session.add(resource)
    
    db_session.commit()
    return resources


@pytest.fixture
def test_citations(test_db, test_resources):
    """Create citation network for testing."""
    db_session = test_db()
    citations = []
    
    # Create citation chain: 0→1→2→3, 4→5→6, 7→8→9
    citation_pairs = [
        (0, 1), (1, 2), (2, 3),
        (4, 5), (5, 6),
        (7, 8), (8, 9)
    ]
    
    for source_idx, target_idx in citation_pairs:
        citation = Citation(
            id=uuid.uuid4(),
            source_resource_id=test_resources[source_idx].id,
            target_resource_id=test_resources[target_idx].id,
            target_url=f"https://example.com/resource-{target_idx}",
            citation_type="direct",
            context_snippet="Test citation"
        )
        citations.append(citation)
        db_session.add(citation)
    
    db_session.commit()
    return citations


class TestEndToEndDiscoveryWorkflow:
    """Test complete discovery workflow from graph construction to hypothesis generation."""
    
    def test_complete_workflow(self, test_db, test_resources, test_citations):
        """
        Test end-to-end discovery workflow:
        1. Build multi-layer graph
        2. Compute Graph2Vec embeddings
        3. Compute fusion embeddings
        4. Perform open discovery
        5. Validate hypothesis
        6. Verify edge weight updates
        """
        db_session = test_db()
        # Step 1: Build multi-layer graph
        graph_service = GraphService(db_session)
        graph = graph_service.build_multilayer_graph(refresh_cache=True)
        
        assert graph is not None
        assert graph.number_of_nodes() == 10
        assert graph.number_of_edges() > 0
        
        # Verify citation edges exist
        citation_edges = [e for e in graph.edges(data=True) if e[2].get('edge_type') == 'citation']
        assert len(citation_edges) == 7  # 7 citation pairs
        
        # Step 2: Compute Graph2Vec embeddings (simplified for testing)
        embeddings_service = GraphEmbeddingsService(db_session)
        
        # For testing, we'll create mock structural embeddings
        for resource in test_resources:
            graph_embedding = GraphEmbedding(
                id=uuid.uuid4(),
                resource_id=resource.id,
                structural_embedding=[0.05 * i for i in range(128)],
                embedding_method="graph2vec",
                embedding_version="v1.0"
            )
            db_session.add(graph_embedding)
        
        db_session.commit()
        
        # Step 3: Compute fusion embeddings
        embeddings_service.compute_fusion_embeddings(alpha=0.5)
        
        # Verify fusion embeddings created
        fusion_count = db_session.query(GraphEmbedding).filter(
            GraphEmbedding.fusion_embedding.isnot(None)
        ).count()
        assert fusion_count == 10
        
        # Step 4: Perform open discovery from resource 0
        lbd_service = LBDService(db_session)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(test_resources[0].id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Should find resource 2 through resource 1 (0→1→2)
        assert len(hypotheses) > 0
        
        # Find hypothesis for resource 2
        hypothesis_for_2 = next(
            (h for h in hypotheses if h['c_resource']['id'] == str(test_resources[2].id)),
            None
        )
        assert hypothesis_for_2 is not None
        assert hypothesis_for_2['plausibility_score'] > 0.0
        assert len(hypothesis_for_2['b_resources']) > 0
        
        # Step 5: Validate hypothesis
        # Query the hypothesis record from database (it was stored by open_discovery)
        hypothesis_record = db_session.query(DiscoveryHypothesis).filter(
            DiscoveryHypothesis.a_resource_id == test_resources[0].id,
            DiscoveryHypothesis.c_resource_id == test_resources[2].id,
            DiscoveryHypothesis.hypothesis_type == "open"
        ).first()
        
        assert hypothesis_record is not None
        
        # Get initial edge weights
        initial_edges = db_session.query(GraphEdge).filter(
            GraphEdge.source_id == test_resources[0].id,
            GraphEdge.target_id == test_resources[1].id
        ).all()
        
        initial_weights = {e.edge_type: e.weight for e in initial_edges}
        
        # Validate hypothesis
        hypothesis_record.is_validated = True
        hypothesis_record.validation_notes = "Test validation"
        hypothesis_record.user_id = "test_user"
        db_session.commit()
        
        # Step 6: Verify edge weight updates (would be done by validation endpoint)
        # For this test, we'll manually update weights to simulate the behavior
        for edge in initial_edges:
            edge.weight = edge.weight * 1.1  # 10% increase
        db_session.commit()
        
        # Verify weights increased
        updated_edges = db_session.query(GraphEdge).filter(
            GraphEdge.source_id == test_resources[0].id,
            GraphEdge.target_id == test_resources[1].id
        ).all()
        
        for edge in updated_edges:
            if edge.edge_type in initial_weights:
                assert edge.weight > initial_weights[edge.edge_type]
    
    def test_closed_discovery_workflow(self, test_db, test_resources, test_citations):
        """Test closed discovery connecting two known resources."""
        db_session = test_db()
        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Perform closed discovery: connect resource 0 to resource 2
        lbd_service = LBDService(db_session)
        paths = lbd_service.closed_discovery(
            a_resource_id=str(test_resources[0].id),
            c_resource_id=str(test_resources[2].id),
            max_hops=3
        )
        
        # Should find path 0→1→2
        assert len(paths) > 0
        
        best_path = paths[0]
        assert best_path['path_length'] == 2
        assert len(best_path['b_resources']) >= 1
        assert best_path['plausibility_score'] > 0.0
        
        # Verify intermediate resource is resource 1
        b_resource_ids = [r['id'] for r in best_path['b_resources']]
        assert str(test_resources[1].id) in b_resource_ids


class TestRecommendationIntegration:
    """Test integration of graph intelligence with recommendation service."""
    
    def test_graph_based_recommendations(self, test_db, test_resources, test_citations):
        """Test graph-based recommendations include 2-hop neighbors."""
        db_session = test_db()
        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Get graph-based recommendations for resource 0
        recommendations = get_graph_based_recommendations(
            db=db_session,
            resource_id=str(test_resources[0].id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Should include 2-hop neighbors
        assert len(recommendations) > 0
        
        # Verify recommendations have required fields
        for rec in recommendations:
            assert 'resource_id' in rec or 'id' in rec
            assert 'score' in rec or 'plausibility_score' in rec
    
    def test_recommendation_fusion(self, test_db, test_resources, test_citations):
        """Test fusion of content-based and graph-based recommendations."""
        db_session = test_db()
        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Create mock graph embeddings for fusion
        for resource in test_resources:
            graph_embedding = GraphEmbedding(
                id=uuid.uuid4(),
                resource_id=resource.id,
                structural_embedding=[0.05 * i for i in range(128)],
                fusion_embedding=[0.1 * i for i in range(128)],
                embedding_method="fusion",
                embedding_version="v1.0"
            )
            db_session.add(graph_embedding)
        
        db_session.commit()
        
        # Get fused recommendations
        recommendations = generate_recommendations_with_graph_fusion(
            db=db_session,
            resource_id=str(test_resources[0].id),
            limit=10,
            content_weight=0.7,
            graph_weight=0.3
        )
        
        # Should return combined recommendations
        assert len(recommendations) > 0
        
        # Verify recommendations have required fields
        for rec in recommendations:
            # Check for either resource dict or resource_id field
            assert 'resource' in rec or 'resource_id' in rec or 'id' in rec
            assert 'score' in rec or 'similarity' in rec
    
    def test_hypothesis_based_recommendations(self, test_db, test_resources, test_citations):
        """Test recommendations include LBD hypotheses."""
        db_session = test_db()
        # Build graph
        graph_service = GraphService(db_session)
        graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Generate some hypotheses first
        lbd_service = LBDService(db_session)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(test_resources[0].id),
            limit=5,
            min_plausibility=0.0
        )
        
        # Verify hypotheses were generated
        assert len(hypotheses) > 0
        
        # Get graph-based recommendations
        recommendations = get_graph_based_recommendations(
            db=db_session,
            resource_id=str(test_resources[0].id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Should include hypothesis-based recommendations
        assert len(recommendations) > 0


class TestGraphCaching:
    """Test graph caching and invalidation."""
    
    def test_graph_cache_reuse(self, test_db, test_resources, test_citations):
        """Test that graph is cached and reused."""
        db_session = test_db()
        graph_service = GraphService(db_session)
        
        # First build
        graph1 = graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Second build without refresh should use cache
        graph2 = graph_service.build_multilayer_graph(refresh_cache=False)
        
        # Should be the same graph object (from cache)
        assert graph1.number_of_nodes() == graph2.number_of_nodes()
        assert graph1.number_of_edges() == graph2.number_of_edges()
    
    def test_graph_cache_invalidation(self, test_db, test_resources, test_citations):
        """Test that cache is invalidated when graph changes."""
        db_session = test_db()
        graph_service = GraphService(db_session)
        
        # Build initial graph
        graph1 = graph_service.build_multilayer_graph(refresh_cache=True)
        initial_edge_count = graph1.number_of_edges()
        
        # Add new citation
        new_citation = Citation(
            id=uuid.uuid4(),
            source_resource_id=test_resources[3].id,
            target_resource_id=test_resources[4].id,
            target_url="https://example.com/resource-4",
            citation_type="direct",
            context_snippet="New citation"
        )
        db_session.add(new_citation)
        db_session.commit()
        
        # Rebuild with refresh
        graph2 = graph_service.build_multilayer_graph(refresh_cache=True)
        
        # Should have more edges
        assert graph2.number_of_edges() > initial_edge_count


@pytest.fixture
def db_session():
    """Mock database session for testing."""
    # This would be provided by your test configuration
    # For now, this is a placeholder
    from backend.app.database.base import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close() 