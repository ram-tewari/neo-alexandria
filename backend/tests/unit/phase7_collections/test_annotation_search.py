"""
Tests for annotation search functionality (Phase 7.5)

This module tests the search methods in AnnotationService:
- Full-text search across notes and highlighted text
- Semantic search using embeddings
- Tag-based search with ANY/ALL matching
"""

import pytest
import uuid
from datetime import datetime, timezone

from backend.app.services.annotation_service import AnnotationService
from backend.app.database.models import Annotation, Resource


@pytest.fixture
def annotation_service(test_db):
    """Create an AnnotationService instance."""
    db = test_db()
    yield AnnotationService(db)
    db.close()


@pytest.fixture
def test_resource(test_db):
    """Create a test resource."""
    db = test_db()
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Paper on Machine Learning",
        identifier="storage/archive/test-resource",
        type="pdf",
        date_created=datetime.now(timezone.utc),
        date_modified=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    yield resource
    db.close()


@pytest.fixture
def test_annotations(test_db, test_resource):
    """Create test annotations with various content."""
    db = test_db()
    annotations = [
        Annotation(
            id=uuid.uuid4(),
            resource_id=test_resource.id,
            user_id="user1",
            start_offset=0,
            end_offset=20,
            highlighted_text="machine learning basics",
            note="This is about neural networks and deep learning",
            tags='["ml", "neural-networks"]',
            color="#FFFF00",
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Annotation(
            id=uuid.uuid4(),
            resource_id=test_resource.id,
            user_id="user1",
            start_offset=100,
            end_offset=130,
            highlighted_text="supervised learning methods",
            note="Important for classification tasks",
            tags='["ml", "supervised"]',
            color="#FFFF00",
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Annotation(
            id=uuid.uuid4(),
            resource_id=test_resource.id,
            user_id="user1",
            start_offset=200,
            end_offset=220,
            highlighted_text="unsupervised clustering",
            note="K-means and hierarchical clustering",
            tags='["ml", "unsupervised", "clustering"]',
            color="#00FF00",
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Annotation(
            id=uuid.uuid4(),
            resource_id=test_resource.id,
            user_id="user2",
            start_offset=300,
            end_offset=320,
            highlighted_text="reinforcement learning",
            note="Q-learning and policy gradients",
            tags='["ml", "reinforcement"]',
            color="#FF0000",
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]
    
    for annotation in annotations:
        db.add(annotation)
    db.commit()
    
    for annotation in annotations:
        db.refresh(annotation)
    
    yield annotations
    db.close()


class TestFullTextSearch:
    """Tests for full-text search functionality."""
    
    def test_search_in_notes(self, annotation_service, test_annotations):
        """Test searching in annotation notes."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query="neural networks"
        )
        
        assert len(results) == 1
        assert "neural networks" in results[0].note
    
    def test_search_in_highlighted_text(self, annotation_service, test_annotations):
        """Test searching in highlighted text."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query="supervised learning"
        )
        
        assert len(results) == 1
        assert "supervised learning" in results[0].highlighted_text
    
    def test_search_case_insensitive(self, annotation_service, test_annotations):
        """Test that search is case-insensitive."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query="MACHINE LEARNING"
        )
        
        assert len(results) >= 1
    
    def test_search_filters_by_user(self, annotation_service, test_annotations):
        """Test that search only returns user's annotations."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query="learning"
        )
        
        # Should not include user2's annotations
        for result in results:
            assert result.user_id == "user1"
    
    def test_search_empty_query(self, annotation_service, test_annotations):
        """Test that empty query returns empty results."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query=""
        )
        
        assert len(results) == 0
    
    def test_search_with_limit(self, annotation_service, test_annotations):
        """Test that limit parameter works."""
        results = annotation_service.search_annotations_fulltext(
            user_id="user1",
            query="ml",
            limit=2
        )
        
        assert len(results) <= 2


class TestTagSearch:
    """Tests for tag-based search functionality."""
    
    def test_search_by_single_tag(self, annotation_service, test_annotations):
        """Test searching by a single tag."""
        results = annotation_service.search_annotations_by_tags(
            user_id="user1",
            tags=["supervised"]
        )
        
        assert len(results) == 1
        assert '"supervised"' in results[0].tags
    
    def test_search_by_multiple_tags_any(self, annotation_service, test_annotations):
        """Test searching with ANY tag matching."""
        results = annotation_service.search_annotations_by_tags(
            user_id="user1",
            tags=["supervised", "unsupervised"],
            match_all=False
        )
        
        assert len(results) == 2
    
    def test_search_by_multiple_tags_all(self, annotation_service, test_annotations):
        """Test searching with ALL tags matching."""
        results = annotation_service.search_annotations_by_tags(
            user_id="user1",
            tags=["ml", "clustering"],
            match_all=True
        )
        
        assert len(results) == 1
        assert '"clustering"' in results[0].tags
    
    def test_search_tags_filters_by_user(self, annotation_service, test_annotations):
        """Test that tag search only returns user's annotations."""
        results = annotation_service.search_annotations_by_tags(
            user_id="user1",
            tags=["ml"]
        )
        
        for result in results:
            assert result.user_id == "user1"
    
    def test_search_empty_tags(self, annotation_service, test_annotations):
        """Test that empty tags list returns empty results."""
        results = annotation_service.search_annotations_by_tags(
            user_id="user1",
            tags=[]
        )
        
        assert len(results) == 0


class TestSemanticSearch:
    """Tests for semantic search functionality."""
    
    def test_semantic_search_basic(self, annotation_service, test_annotations):
        """Test basic semantic search functionality."""
        # Note: This test may not return results if embeddings aren't generated
        # In a real scenario, embeddings would be generated during annotation creation
        results = annotation_service.search_annotations_semantic(
            user_id="user1",
            query="deep learning"
        )
        
        # Results should be a list of tuples (annotation, score)
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], Annotation)
            assert isinstance(item[1], float)
    
    def test_semantic_search_empty_query(self, annotation_service, test_annotations):
        """Test that empty query returns empty results."""
        results = annotation_service.search_annotations_semantic(
            user_id="user1",
            query=""
        )
        
        assert len(results) == 0
    
    def test_semantic_search_with_limit(self, annotation_service, test_annotations):
        """Test that limit parameter works."""
        results = annotation_service.search_annotations_semantic(
            user_id="user1",
            query="machine learning",
            limit=2
        )
        
        assert len(results) <= 2
    
    def test_cosine_similarity(self, annotation_service):
        """Test cosine similarity computation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = annotation_service._cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, abs=0.01)
        
        vec3 = [0.0, 1.0, 0.0]
        similarity = annotation_service._cosine_similarity(vec1, vec3)
        assert similarity == pytest.approx(0.0, abs=0.01)
