"""
Unit tests for Phase 10 2-hop neighbor discovery.

Tests:
- 1-hop retrieval
- 2-hop retrieval with path tracking
- Edge type filtering
- Min_weight filtering
- Ranking algorithm
- Limit enforcement
"""


from backend.app.services.graph_service import GraphService
from backend.app.database.models import Resource, Citation


class TestNeighborDiscovery:
    """Test 2-hop neighbor discovery functionality."""
    
    def test_1hop_retrieval(self, test_db):
        """Test that 1-hop neighbors are retrieved correctly."""
        db = test_db()
        
        # Create resources: A -> B, A -> C
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.8
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.7
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.9
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="https://example.com/paper-b",
            citation_type="direct"
        )
        citation_ac = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_c.id,
            target_url="https://example.com/paper-c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_ac])
        db.commit()
        
        # Get 1-hop neighbors
        graph_service = GraphService(db)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            limit=10
        )
        
        # Verify results
        assert len(neighbors) == 2
        neighbor_ids = {n["resource_id"] for n in neighbors}
        assert str(resource_b.id) in neighbor_ids
        assert str(resource_c.id) in neighbor_ids
        
        # Verify path structure
        for neighbor in neighbors:
            assert neighbor["distance"] == 1
            assert len(neighbor["path"]) == 2
            assert neighbor["path"][0] == str(resource_a.id)
            assert neighbor["intermediate"] is None
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_ac)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_2hop_retrieval_with_path_tracking(self, test_db):
        """Test that 2-hop neighbors are retrieved with correct path information."""
        db = test_db()
        
        # Create resources: A -> B -> C
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.8
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.7
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.9
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations: A -> B -> C
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="https://example.com/paper-b",
            citation_type="direct"
        )
        citation_bc = Citation(
            source_resource_id=resource_b.id,
            target_resource_id=resource_c.id,
            target_url="https://example.com/paper-c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_bc])
        db.commit()
        
        # Get 2-hop neighbors
        graph_service = GraphService(db)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=2,
            limit=10
        )
        
        # Verify C is found as 2-hop neighbor
        neighbor_ids = {n["resource_id"] for n in neighbors}
        assert str(resource_c.id) in neighbor_ids
        
        # Find C in results
        neighbor_c = next(n for n in neighbors if n["resource_id"] == str(resource_c.id))
        
        # Verify path structure
        assert neighbor_c["distance"] == 2
        assert len(neighbor_c["path"]) == 3
        assert neighbor_c["path"][0] == str(resource_a.id)
        assert neighbor_c["path"][1] == str(resource_b.id)
        assert neighbor_c["path"][2] == str(resource_c.id)
        assert neighbor_c["intermediate"] == str(resource_b.id)
        
        # Verify path strength (product of edge weights)
        # Citation edges have weight 1.0, so path_strength should be 1.0 * 1.0 = 1.0
        assert neighbor_c["path_strength"] == 1.0
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_bc)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_edge_type_filtering(self, test_db):
        """Test that edge type filtering works correctly."""
        db = test_db()
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            quality_overall=0.8
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            quality_overall=0.7
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,  # Same year as A for temporal edge
            quality_overall=0.9
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citation: A -> C (not B, so we can test filtering)
        citation_ac = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_c.id,
            target_url="https://example.com/paper-c",
            citation_type="direct"
        )
        db.add(citation_ac)
        db.commit()
        
        # Build graph (will create temporal edges A <-> B and A <-> C due to same year)
        graph_service = GraphService(db)
        graph_service.build_multilayer_graph()
        
        # Get neighbors with citation filter only
        neighbors_citation = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            edge_types=["citation"],
            limit=10
        )
        
        # Should only find C (citation edge)
        neighbor_ids = {n["resource_id"] for n in neighbors_citation}
        assert str(resource_c.id) in neighbor_ids
        assert str(resource_b.id) not in neighbor_ids
        
        # Get neighbors with temporal filter only
        neighbors_temporal = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            edge_types=["temporal"],
            limit=10
        )
        
        # Should find both B and C (temporal edges, same year 2023)
        neighbor_ids_temporal = {n["resource_id"] for n in neighbors_temporal}
        assert str(resource_b.id) in neighbor_ids_temporal
        assert str(resource_c.id) in neighbor_ids_temporal
        
        # Cleanup
        db.delete(citation_ac)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_min_weight_filtering(self, test_db):
        """Test that min_weight threshold filtering works correctly."""
        db = test_db()
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            quality_overall=0.8
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.7
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004",
            publication_year=2023,
            quality_overall=0.9
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citation: A -> B (weight 1.0)
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="https://example.com/paper-b",
            citation_type="direct"
        )
        db.add(citation_ab)
        db.commit()
        
        # Build graph (will create temporal edge A -> C with weight 0.3)
        graph_service = GraphService(db)
        graph_service.build_multilayer_graph()
        
        # Get neighbors with min_weight=0.5 (should exclude temporal edge)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            min_weight=0.5,
            limit=10
        )
        
        # Should only find B (citation weight 1.0 >= 0.5)
        # Should not find C (temporal weight 0.3 < 0.5)
        neighbor_ids = {n["resource_id"] for n in neighbors}
        assert str(resource_b.id) in neighbor_ids
        assert str(resource_c.id) not in neighbor_ids
        
        # Get neighbors with min_weight=0.2 (should include both)
        neighbors_low_threshold = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            min_weight=0.2,
            limit=10
        )
        
        neighbor_ids_low = {n["resource_id"] for n in neighbors_low_threshold}
        assert str(resource_b.id) in neighbor_ids_low
        assert str(resource_c.id) in neighbor_ids_low
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_ranking_algorithm(self, test_db):
        """Test that neighbors are ranked by combined score (path_strength + quality + novelty)."""
        db = test_db()
        
        # Create resources with different quality scores
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.5
        )
        resource_b = Resource(
            title="Paper B (High Quality)",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.9  # High quality
        )
        resource_c = Resource(
            title="Paper C (Low Quality)",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.3  # Low quality
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations with same weight
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="https://example.com/paper-b",
            citation_type="direct"
        )
        citation_ac = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_c.id,
            target_url="https://example.com/paper-c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_ac])
        db.commit()
        
        # Get neighbors
        graph_service = GraphService(db)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            limit=10
        )
        
        # Verify B is ranked higher than C due to quality
        assert len(neighbors) >= 2
        
        # Find B and C in results
        neighbor_b = next((n for n in neighbors if n["resource_id"] == str(resource_b.id)), None)
        neighbor_c = next((n for n in neighbors if n["resource_id"] == str(resource_c.id)), None)
        
        assert neighbor_b is not None
        assert neighbor_c is not None
        
        # B should have higher score than C
        assert neighbor_b["score"] > neighbor_c["score"]
        
        # Verify score components exist
        assert "quality" in neighbor_b
        assert "novelty" in neighbor_b
        assert "path_strength" in neighbor_b
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_ac)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_limit_enforcement(self, test_db):
        """Test that limit parameter is enforced correctly."""
        db = test_db()
        
        # Create source resource
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            quality_overall=0.8
        )
        db.add(resource_a)
        db.commit()
        db.refresh(resource_a)
        
        # Create 10 target resources
        target_resources = []
        for i in range(10):
            resource = Resource(
                title=f"Paper {i}",
                type="article",
                language="en",
                classification_code="004",
                quality_overall=0.5 + i * 0.05
            )
            db.add(resource)
            target_resources.append(resource)
        
        db.commit()
        for r in target_resources:
            db.refresh(r)
        
        # Create citations from A to all targets
        for i, target in enumerate(target_resources):
            citation = Citation(
                source_resource_id=resource_a.id,
                target_resource_id=target.id,
                target_url=f"https://example.com/paper-{i}",
                citation_type="direct"
            )
            db.add(citation)
        
        db.commit()
        
        # Get neighbors with limit=5
        graph_service = GraphService(db)
        neighbors = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            limit=5
        )
        
        # Should return exactly 5 neighbors
        assert len(neighbors) == 5
        
        # Get neighbors with limit=3
        neighbors_limited = graph_service.get_neighbors_multihop(
            resource_id=str(resource_a.id),
            hops=1,
            limit=3
        )
        
        # Should return exactly 3 neighbors
        assert len(neighbors_limited) == 3
        
        # Cleanup
        for target in target_resources:
            db.delete(target)
        db.delete(resource_a)
        db.commit()
        db.close()
