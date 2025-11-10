"""
Test suite for Phase 5 - Hybrid Knowledge Graph functionality.

Tests the hybrid graph scoring service and API endpoints that compute
and expose a graph of resources using weighted blend of vector similarity,
shared canonical subjects, and shared classification codes.
"""

import pytest
import uuid

from fastapi.testclient import TestClient

from backend.app.database import models as db_models
from backend.app.services.graph_service import (
    cosine_similarity,
    compute_tag_overlap_score,
    compute_classification_match_score,
    compute_hybrid_weight,
    find_hybrid_neighbors,
)
from backend.app.main import app


class TestCosineSimilarity:
    """Test cosine similarity computation with NumPy."""
    
    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors equals 1.0."""
        vec_a = [1.0, 2.0, 3.0]
        vec_b = [1.0, 2.0, 3.0]
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)
    
    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors equals 0.0."""
        vec_a = [1.0, 0.0]
        vec_b = [0.0, 1.0]
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(0.0)
    
    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors equals -1.0."""
        vec_a = [1.0, 0.0]
        vec_b = [-1.0, 0.0]
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(-1.0)
    
    def test_zero_vector_handling(self):
        """Test that zero vectors return 0.0 similarity."""
        vec_a = [0.0, 0.0, 0.0]
        vec_b = [1.0, 2.0, 3.0]
        assert cosine_similarity(vec_a, vec_b) == 0.0
        
        vec_c = [1.0, 2.0, 3.0]
        vec_d = [0.0, 0.0, 0.0]
        assert cosine_similarity(vec_c, vec_d) == 0.0
    
    def test_empty_vectors(self):
        """Test that empty vectors return 0.0 similarity."""
        assert cosine_similarity([], [1.0, 2.0]) == 0.0
        assert cosine_similarity([1.0, 2.0], []) == 0.0
        assert cosine_similarity([], []) == 0.0
    
    def test_different_length_vectors(self):
        """Test that vectors of different lengths return 0.0 similarity."""
        vec_a = [1.0, 2.0]
        vec_b = [1.0, 2.0, 3.0]
        assert cosine_similarity(vec_a, vec_b) == 0.0
    
    def test_normalized_vectors(self):
        """Test cosine similarity with normalized vectors."""
        # Normalized unit vectors
        vec_a = [0.6, 0.8]  # magnitude = 1.0
        vec_b = [0.8, 0.6]  # magnitude = 1.0
        
        # Expected: (0.6*0.8 + 0.8*0.6) / (1.0 * 1.0) = 0.96
        expected = 0.6 * 0.8 + 0.8 * 0.6
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(expected)


class TestTagOverlapScore:
    """Test tag overlap scoring with diminishing returns heuristic."""
    
    def test_no_overlap(self):
        """Test that no shared subjects returns 0.0 score."""
        subjects_a = ["machine learning", "python"]
        subjects_b = ["cooking", "recipes"]
        score, shared = compute_tag_overlap_score(subjects_a, subjects_b)
        assert score == 0.0
        assert shared == []
    
    def test_single_overlap(self):
        """Test that single shared subject returns 0.5 score."""
        subjects_a = ["machine learning", "python"]
        subjects_b = ["python", "web development"]
        score, shared = compute_tag_overlap_score(subjects_a, subjects_b)
        assert score == 0.5
        assert shared == ["python"]
    
    def test_multiple_overlap(self):
        """Test diminishing returns for multiple overlaps."""
        subjects_a = ["python", "machine learning", "data science"]
        subjects_b = ["python", "machine learning", "statistics"]
        score, shared = compute_tag_overlap_score(subjects_a, subjects_b)
        # 2 shared: 0.5 + (2-1)*0.1 = 0.6
        assert score == 0.6
        assert set(shared) == {"python", "machine learning"}
    
    def test_many_overlaps_capped(self):
        """Test that many overlaps are capped at 1.0."""
        subjects_a = ["a", "b", "c", "d", "e", "f", "g"]
        subjects_b = ["a", "b", "c", "d", "e", "f", "h"]
        score, shared = compute_tag_overlap_score(subjects_a, subjects_b)
        # 6 shared: 0.5 + (6-1)*0.1 = 1.0 (capped)
        assert score == 1.0
        assert len(shared) == 6
    
    def test_empty_subjects(self):
        """Test that empty subject lists return 0.0 score."""
        assert compute_tag_overlap_score([], ["python"]) == (0.0, [])
        assert compute_tag_overlap_score(["python"], []) == (0.0, [])
        assert compute_tag_overlap_score([], []) == (0.0, [])
    
    def test_case_sensitivity(self):
        """Test that overlap matching is case-sensitive."""
        subjects_a = ["Python", "Machine Learning"]
        subjects_b = ["python", "machine learning"]
        score, shared = compute_tag_overlap_score(subjects_a, subjects_b)
        assert score == 0.0
        assert shared == []


class TestClassificationMatchScore:
    """Test binary classification code matching."""
    
    def test_exact_match(self):
        """Test that identical codes return 1.0."""
        assert compute_classification_match_score("004", "004") == 1.0
    
    def test_no_match(self):
        """Test that different codes return 0.0."""
        assert compute_classification_match_score("004", "100") == 0.0
    
    def test_none_values(self):
        """Test that None values return 0.0."""
        assert compute_classification_match_score(None, "004") == 0.0
        assert compute_classification_match_score("004", None) == 0.0
        assert compute_classification_match_score(None, None) == 0.0


class TestHybridWeight:
    """Test hybrid weight computation with configurable weights."""
    
    def test_default_weights(self):
        """Test hybrid weight with default weights (0.6, 0.3, 0.1)."""
        vector_score = 0.8  # High similarity
        tag_score = 0.6     # 2 shared subjects
        classification_score = 1.0  # Match
        
        # Expected: 0.6*0.8 + 0.3*0.6 + 0.1*1.0 = 0.48 + 0.18 + 0.1 = 0.76
        expected = 0.6 * 0.8 + 0.3 * 0.6 + 0.1 * 1.0
        result = compute_hybrid_weight(vector_score, tag_score, classification_score)
        assert result == pytest.approx(expected)
    
    def test_custom_weights(self):
        """Test hybrid weight with custom weights."""
        vector_score = 0.5
        tag_score = 0.8
        classification_score = 0.0
        
        # Custom weights: equal weighting
        weight_v = weight_t = weight_c = 1.0 / 3.0
        expected = weight_v * 0.5 + weight_t * 0.8 + weight_c * 0.0
        result = compute_hybrid_weight(
            vector_score, tag_score, classification_score,
            weight_v, weight_t, weight_c
        )
        assert result == pytest.approx(expected)
    
    def test_negative_vector_clamping(self):
        """Test that negative vector scores are clamped to 0."""
        vector_score = -0.3  # Anti-aligned vectors
        tag_score = 0.5
        classification_score = 0.0
        
        # Should clamp vector_score to 0.0
        expected = 0.6 * 0.0 + 0.3 * 0.5 + 0.1 * 0.0
        result = compute_hybrid_weight(vector_score, tag_score, classification_score)
        assert result == pytest.approx(expected)
    
    def test_range_bounds(self):
        """Test that hybrid weight is bounded in [0, 1]."""
        # Test lower bound
        result = compute_hybrid_weight(-1.0, 0.0, 0.0)
        assert 0.0 <= result <= 1.0
        
        # Test upper bound  
        result = compute_hybrid_weight(1.0, 1.0, 1.0)
        assert 0.0 <= result <= 1.0


@pytest.mark.usefixtures("test_db")
class TestGraphService:
    """Test graph service functions with database interactions."""
    
    def test_find_neighbors_empty_database(self, test_db):
        """Test neighbor finding with empty database."""
        db = test_db()
        fake_id = uuid.uuid4()
        
        graph = find_hybrid_neighbors(db, fake_id, limit=5)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_find_neighbors_nonexistent_resource(self, test_db):
        """Test neighbor finding for non-existent resource."""
        db = test_db()
        fake_id = uuid.uuid4()
        
        # Add some other resources to the database
        resource1 = db_models.Resource(
            title="Test Resource 1",
            subject=["python", "programming"],
            classification_code="004",
            embedding=[0.1, 0.2, 0.3]
        )
        db.add(resource1)
        db.commit()
        
        graph = find_hybrid_neighbors(db, fake_id, limit=5)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_find_neighbors_with_vector_similarity(self, test_db):
        """Test neighbor finding based on vector similarity."""
        db = test_db()
        
        # Create source resource
        source = db_models.Resource(
            title="Source Resource",
            subject=["python"],
            embedding=[1.0, 0.0, 0.0]  # Unit vector along x-axis
        )
        db.add(source)
        db.flush()
        
        # Create similar resource (high cosine similarity)
        similar = db_models.Resource(
            title="Similar Resource",
            subject=["javascript"],
            embedding=[0.8, 0.6, 0.0]  # Closer to source
        )
        db.add(similar)
        
        # Create dissimilar resource (low cosine similarity)
        dissimilar = db_models.Resource(
            title="Dissimilar Resource", 
            subject=["cooking"],
            embedding=[0.0, 0.0, 1.0]  # Orthogonal to source
        )
        db.add(dissimilar)
        db.commit()
        
        graph = find_hybrid_neighbors(db, source.id, limit=5)
        
        # Should find both neighbors
        assert len(graph.nodes) == 3  # source + 2 neighbors
        assert len(graph.edges) == 2
        
        # Similar resource should have higher weight than dissimilar
        edge_weights = {edge.target: edge.weight for edge in graph.edges}
        assert edge_weights[similar.id] > edge_weights[dissimilar.id]
    
    def test_find_neighbors_with_shared_subjects(self, test_db):
        """Test neighbor finding based on shared subjects."""
        db = test_db()
        
        # Create source resource
        source = db_models.Resource(
            title="Python Guide",
            subject=["python", "programming", "tutorial"],
            classification_code="004"
        )
        db.add(source)
        db.flush()
        
        # Create resource with many shared subjects (should rank higher)
        multi_shared = db_models.Resource(
            title="Python Programming Basics",
            subject=["python", "programming", "beginner"],
            classification_code="100"
        )
        db.add(multi_shared)
        
        # Create resource with one shared subject (should rank lower)
        single_shared = db_models.Resource(
            title="Web Development",
            subject=["python", "web", "django"],
            classification_code="200"
        )
        db.add(single_shared)
        db.commit()
        
        graph = find_hybrid_neighbors(db, source.id, limit=5)
        
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        
        # Multi-shared should outrank single-shared due to tag overlap
        edge_weights = {edge.target: edge.weight for edge in graph.edges}
        assert edge_weights[multi_shared.id] > edge_weights[single_shared.id]
        
        # Check edge details include shared subjects
        for edge in graph.edges:
            if edge.target == multi_shared.id:
                assert "python" in edge.details.shared_subjects
                assert "programming" in edge.details.shared_subjects
                assert edge.details.connection_type == "topical"
    
    def test_find_neighbors_classification_match(self, test_db):
        """Test that classification matches boost neighbor ranking."""
        db = test_db()
        
        # Create source resource
        source = db_models.Resource(
            title="Programming Fundamentals",
            subject=["programming"],
            classification_code="004",
            embedding=[1.0, 0.0]
        )
        db.add(source)
        db.flush()
        
        # Create resource with same classification but lower vector similarity
        same_class = db_models.Resource(
            title="Software Engineering",
            subject=["software"],
            classification_code="004",  # Same classification
            embedding=[0.5, 0.5]  # Lower similarity to source
        )
        db.add(same_class)
        
        # Create resource with higher vector similarity but different classification
        diff_class = db_models.Resource(
            title="Programming Concepts",
            subject=["concepts"],
            classification_code="100",  # Different classification
            embedding=[0.9, 0.1]  # Higher similarity to source
        )
        db.add(diff_class)
        db.commit()
        
        graph = find_hybrid_neighbors(db, source.id, limit=5)
        
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        
        # Classification match might boost same_class higher despite lower vector sim
        # This tests the hybrid nature where multiple factors contribute
        edge_details = {edge.target: edge.details for edge in graph.edges}
        
        # same_class should have classification connection type
        same_class_edge = edge_details[same_class.id]
        assert same_class_edge.connection_type == "classification"


class TestGraphAPIEndpoints:
    """Test the graph API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_resources(self, test_db):
        """Create sample resources for testing."""
        db = test_db()
        
        resources = []
        
        # Resource 1: AI/ML focus
        res1 = db_models.Resource(
            title="Machine Learning Fundamentals",
            subject=["machine learning", "artificial intelligence", "python"],
            classification_code="004",
            embedding=[0.8, 0.6, 0.1, 0.0]
        )
        db.add(res1)
        resources.append(res1)
        
        # Resource 2: Similar to res1 
        res2 = db_models.Resource(
            title="Deep Learning with Python",
            subject=["deep learning", "neural networks", "python"],
            classification_code="004",
            embedding=[0.7, 0.7, 0.1, 0.1]
        )
        db.add(res2)
        resources.append(res2)
        
        # Resource 3: Different topic
        res3 = db_models.Resource(
            title="Cooking Basics",
            subject=["cooking", "recipes", "food"],
            classification_code="641",
            embedding=[0.1, 0.1, 0.8, 0.6]
        )
        db.add(res3)
        resources.append(res3)
        
        db.commit()
        # Return resource IDs to avoid detached instance issues
        return [str(r.id) for r in resources]
    
    def test_get_neighbors_success(self, client, sample_resources):
        """Test successful neighbor retrieval."""
        source_resource_id = sample_resources[0]
        
        response = client.get(f"/graph/resource/{source_resource_id}/neighbors")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 1  # At least the source node
        
        # Source node should be present
        node_ids = [node["id"] for node in data["nodes"]]
        assert source_resource_id in node_ids
    
    def test_get_neighbors_with_limit(self, client, sample_resources):
        """Test neighbor retrieval with custom limit."""
        source_resource_id = sample_resources[0]
        
        response = client.get(f"/graph/resource/{source_resource_id}/neighbors?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        # Should have source + at most 1 neighbor
        assert len(data["nodes"]) <= 2
        assert len(data["edges"]) <= 1
    
    def test_get_neighbors_nonexistent(self, client, sample_resources):
        """Test neighbor retrieval for non-existent resource."""
        fake_id = uuid.uuid4()
        
        response = client.get(f"/graph/resource/{fake_id}/neighbors")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_neighbors_invalid_uuid(self, client):
        """Test neighbor retrieval with invalid UUID."""
        response = client.get("/graph/resource/invalid-uuid/neighbors")
        assert response.status_code == 422  # Validation error
    
    def test_get_global_overview_success(self, client, sample_resources):
        """Test successful global overview retrieval."""
        response = client.get("/graph/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        
        # With 3 resources, we should have some connections
        if len(data["edges"]) > 0:
            # Verify edge structure
            for edge in data["edges"]:
                assert "source" in edge
                assert "target" in edge
                assert "weight" in edge
                assert "details" in edge
                assert 0.0 <= edge["weight"] <= 1.0
    
    def test_get_global_overview_with_params(self, client, sample_resources):
        """Test global overview with custom parameters."""
        response = client.get("/graph/overview?limit=10&vector_threshold=0.9")
        assert response.status_code == 200
        
        data = response.json()
        # With high threshold, might have fewer edges
        assert len(data["edges"]) <= 10
    
    def test_edge_details_accuracy(self, client, sample_resources):
        """Test that edge details accurately reflect connection reasons."""
        source_resource_id = sample_resources[0]  # ML resource
        
        response = client.get(f"/graph/resource/{source_resource_id}/neighbors")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["edges"]:
            for edge in data["edges"]:
                details = edge["details"]
                
                # Should have connection type
                assert details["connection_type"] in ["semantic", "topical", "classification"]
                
                # If vector similarity is present, should be in [0,1]
                if details.get("vector_similarity") is not None:
                    assert 0.0 <= details["vector_similarity"] <= 1.0
                
                # shared_subjects should be a list
                assert isinstance(details["shared_subjects"], list)
    
    def test_hybrid_ranking_demonstration(self, test_db, client):
        """Test that hybrid ranking shows multi-tag overlaps can outrank higher cosine similarity."""
        db = test_db()
        
        # Create source resource
        source = db_models.Resource(
            title="Python Programming",
            subject=["python", "programming", "development"],
            classification_code="004",
            embedding=[1.0, 0.0, 0.0, 0.0]
        )
        db.add(source)
        db.flush()
        
        # High cosine similarity but no shared subjects
        high_cosine = db_models.Resource(
            title="Mathematics Research",
            subject=["mathematics", "research"],
            classification_code="510",
            embedding=[0.95, 0.1, 0.05, 0.0]  # Very similar vector
        )
        db.add(high_cosine)
        
        # Lower cosine similarity but multiple shared subjects
        multi_tags = db_models.Resource(
            title="Python Development Guide",
            subject=["python", "programming", "tutorial", "guide"],
            classification_code="004",
            embedding=[0.6, 0.6, 0.3, 0.1]  # Lower similarity
        )
        db.add(multi_tags)
        db.commit()
        
        response = client.get(f"/graph/resource/{source.id}/neighbors")
        assert response.status_code == 200
        
        data = response.json()
        
        if len(data["edges"]) >= 2:
            # Find edges by target
            edge_by_target = {edge["target"]: edge for edge in data["edges"]}
            
            high_cosine_edge = edge_by_target.get(str(high_cosine.id))
            multi_tags_edge = edge_by_target.get(str(multi_tags.id))
            
            if high_cosine_edge and multi_tags_edge:
                # Multi-tag resource should outrank high-cosine resource
                # due to shared subjects and classification match
                assert multi_tags_edge["weight"] > high_cosine_edge["weight"]
                
                # Verify connection types
                assert multi_tags_edge["details"]["connection_type"] == "classification"
                assert len(multi_tags_edge["details"]["shared_subjects"]) >= 2
                
                assert high_cosine_edge["details"]["connection_type"] == "semantic"
                assert len(high_cosine_edge["details"]["shared_subjects"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])
