"""
Unit tests for Phase 10 Literature-Based Discovery (LBD).

Tests:
- Open discovery: A→B→C path discovery, direct connection exclusion, plausibility scoring
- Closed discovery: 2-hop and 3-hop path finding, path strength calculation, common neighbors
"""

import pytest

try:
    import numpy as np
except ImportError:
    np = None

from backend.app.services.lbd_service import LBDService
from backend.app.database.models import Resource, Citation


class TestLBDOpenDiscovery:
    """Test LBD open discovery functionality."""
    
    def test_abc_path_discovery(self, test_db):
        """Test that A→B→C paths are discovered correctly."""
        db = test_db()
        
        # Create resources: A -> B -> C (no direct A -> C)
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations: A -> B -> C
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="http://example.com/b",
            citation_type="direct"
        )
        citation_bc = Citation(
            source_resource_id=resource_b.id,
            target_resource_id=resource_c.id,
            target_url="http://example.com/c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_bc])
        db.commit()
        
        # Perform open discovery from A
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resource_a.id),
            limit=10,
            min_plausibility=0.0  # Low threshold to ensure we get results
        )
        
        # Verify C was discovered
        assert len(hypotheses) > 0
        
        # Find hypothesis for C
        hypothesis_c = next((h for h in hypotheses if h["c_resource"]["id"] == str(resource_c.id)), None)
        assert hypothesis_c is not None
        
        # Verify path structure
        assert hypothesis_c["path_length"] == 2
        assert len(hypothesis_c["b_resources"]) > 0
        assert any(b["id"] == str(resource_b.id) for b in hypothesis_c["b_resources"])
        
        # Verify plausibility components
        assert "plausibility_score" in hypothesis_c
        assert "path_strength" in hypothesis_c
        assert "common_neighbors" in hypothesis_c
        assert "semantic_similarity" in hypothesis_c
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_bc)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_direct_connection_exclusion(self, test_db):
        """Test that resources with direct A→C connections are excluded."""
        db = test_db()
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_c = Resource(
            title="Paper C (Direct)",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_d = Resource(
            title="Paper D (Indirect)",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add_all([resource_a, resource_b, resource_c, resource_d])
        db.commit()
        for r in [resource_a, resource_b, resource_c, resource_d]:
            db.refresh(r)
        
        # Create citations:
        # A -> C (direct)
        # A -> B -> D (indirect)
        citation_ac = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_c.id,
            target_url="http://example.com/c",
            citation_type="direct"
        )
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="http://example.com/b",
            citation_type="direct"
        )
        citation_bd = Citation(
            source_resource_id=resource_b.id,
            target_resource_id=resource_d.id,
            target_url="http://example.com/d",
            citation_type="direct"
        )
        db.add_all([citation_ac, citation_ab, citation_bd])
        db.commit()
        
        # Perform open discovery
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resource_a.id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Verify C is NOT in hypotheses (has direct connection)
        c_ids = [h["c_resource"]["id"] for h in hypotheses]
        assert str(resource_c.id) not in c_ids
        
        # Verify D IS in hypotheses (indirect connection)
        assert str(resource_d.id) in c_ids
        
        # Cleanup
        db.delete(citation_ac)
        db.delete(citation_ab)
        db.delete(citation_bd)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.delete(resource_d)
        db.commit()
        db.close()
    
    def test_plausibility_scoring(self, test_db):
        """Test that plausibility scores are calculated correctly."""
        db = test_db()
        
        if np is None:
            pytest.skip("numpy not installed")
        
        # Create resources with embeddings
        embedding_a = np.random.rand(128).tolist()
        embedding_c_similar = (np.array(embedding_a) + np.random.rand(128) * 0.1).tolist()
        
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004",
            embedding=embedding_a
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004",
            embedding=np.random.rand(128).tolist()
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004",
            embedding=embedding_c_similar
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="http://example.com/b",
            citation_type="direct"
        )
        citation_bc = Citation(
            source_resource_id=resource_b.id,
            target_resource_id=resource_c.id,
            target_url="http://example.com/c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_bc])
        db.commit()
        
        # Perform open discovery
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resource_a.id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Verify plausibility score is in valid range
        assert len(hypotheses) > 0
        for hypothesis in hypotheses:
            assert 0.0 <= hypothesis["plausibility_score"] <= 1.0
            assert 0.0 <= hypothesis["path_strength"] <= 1.0
            assert hypothesis["common_neighbors"] >= 0
            assert 0.0 <= hypothesis["semantic_similarity"] <= 1.0
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_bc)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_min_plausibility_filtering(self, test_db):
        """Test that min_plausibility threshold filters results."""
        db = test_db()
        
        # Create resources
        resources = []
        for i in range(5):
            resource = Resource(
                title=f"Paper {i}",
                type="article",
                language="en",
                classification_code="004"
            )
            db.add(resource)
            resources.append(resource)
        
        db.commit()
        for r in resources:
            db.refresh(r)
        
        # Create citations: 0 -> 1 -> 2, 0 -> 3 -> 4
        citations = []
        for i in range(len(resources) - 1):
            if i != 2:  # Skip 2 to create separate paths
                citation = Citation(
                    source_resource_id=resources[i].id,
                    target_resource_id=resources[i + 1].id,
                    target_url=f"http://example.com/{i+1}",
                    citation_type="direct"
                )
                db.add(citation)
                citations.append(citation)
        
        db.commit()
        
        # Perform open discovery with low threshold
        lbd_service = LBDService(db)
        hypotheses_low = lbd_service.open_discovery(
            a_resource_id=str(resources[0].id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Perform open discovery with high threshold
        hypotheses_high = lbd_service.open_discovery(
            a_resource_id=str(resources[0].id),
            limit=10,
            min_plausibility=0.8
        )
        
        # Verify high threshold returns fewer or equal results
        assert len(hypotheses_high) <= len(hypotheses_low)
        
        # Verify all high threshold results have plausibility >= 0.8
        for hypothesis in hypotheses_high:
            assert hypothesis["plausibility_score"] >= 0.8
        
        # Cleanup
        for citation in citations:
            db.delete(citation)
        for resource in resources:
            db.delete(resource)
        db.commit()
        db.close()
    
    def test_hypothesis_storage(self, test_db):
        """Test that hypotheses are stored in database."""
        db = test_db()
        
        # Create resources
        resource_a = Resource(
            title="Paper A",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_b = Resource(
            title="Paper B",
            type="article",
            language="en",
            classification_code="004"
        )
        resource_c = Resource(
            title="Paper C",
            type="article",
            language="en",
            classification_code="004"
        )
        db.add_all([resource_a, resource_b, resource_c])
        db.commit()
        for r in [resource_a, resource_b, resource_c]:
            db.refresh(r)
        
        # Create citations
        citation_ab = Citation(
            source_resource_id=resource_a.id,
            target_resource_id=resource_b.id,
            target_url="http://example.com/b",
            citation_type="direct"
        )
        citation_bc = Citation(
            source_resource_id=resource_b.id,
            target_resource_id=resource_c.id,
            target_url="http://example.com/c",
            citation_type="direct"
        )
        db.add_all([citation_ab, citation_bc])
        db.commit()
        
        # Perform open discovery
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resource_a.id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Verify hypotheses were returned
        assert len(hypotheses) > 0
        
        # Note: Hypothesis storage is handled by the API layer, not the service
        # This test verifies the service returns the data needed for storage
        for hypothesis in hypotheses:
            assert "c_resource" in hypothesis
            assert "b_resources" in hypothesis
            assert "plausibility_score" in hypothesis
            assert "path_strength" in hypothesis
            assert "path_length" in hypothesis
        
        # Cleanup
        db.delete(citation_ab)
        db.delete(citation_bc)
        db.delete(resource_a)
        db.delete(resource_b)
        db.delete(resource_c)
        db.commit()
        db.close()
    
    def test_ranking_by_plausibility(self, test_db):
        """Test that hypotheses are ranked by plausibility score."""
        db = test_db()
        
        # Create resources
        resources = []
        for i in range(6):
            resource = Resource(
                title=f"Paper {i}",
                type="article",
                language="en",
                classification_code="004"
            )
            db.add(resource)
            resources.append(resource)
        
        db.commit()
        for r in resources:
            db.refresh(r)
        
        # Create multiple paths from resource 0
        # 0 -> 1 -> 2
        # 0 -> 3 -> 4
        # 0 -> 1 -> 5
        citations = [
            Citation(source_resource_id=resources[0].id, target_resource_id=resources[1].id, 
                    target_url="http://example.com/1", citation_type="direct"),
            Citation(source_resource_id=resources[1].id, target_resource_id=resources[2].id,
                    target_url="http://example.com/2", citation_type="direct"),
            Citation(source_resource_id=resources[0].id, target_resource_id=resources[3].id,
                    target_url="http://example.com/3", citation_type="direct"),
            Citation(source_resource_id=resources[3].id, target_resource_id=resources[4].id,
                    target_url="http://example.com/4", citation_type="direct"),
            Citation(source_resource_id=resources[1].id, target_resource_id=resources[5].id,
                    target_url="http://example.com/5", citation_type="direct"),
        ]
        
        for citation in citations:
            db.add(citation)
        db.commit()
        
        # Perform open discovery
        lbd_service = LBDService(db)
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resources[0].id),
            limit=10,
            min_plausibility=0.0
        )
        
        # Verify hypotheses are sorted by plausibility (descending)
        if len(hypotheses) > 1:
            for i in range(len(hypotheses) - 1):
                assert hypotheses[i]["plausibility_score"] >= hypotheses[i + 1]["plausibility_score"]
        
        # Cleanup
        for citation in citations:
            db.delete(citation)
        for resource in resources:
            db.delete(resource)
        db.commit()
        db.close()
