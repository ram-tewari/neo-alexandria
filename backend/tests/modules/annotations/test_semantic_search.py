"""
Annotations Module - Semantic Search Tests

Tests semantic search across annotations using embeddings with golden data.

Requirements: 9.2, 8.2, 8.3
"""

from unittest.mock import patch
from app.modules.annotations.service import AnnotationService
from tests.protocol import load_golden_data


def test_annotation_semantic_search(db_session, create_test_resource, create_test_annotation):
    """
    Test semantic search across annotations using golden data.
    
    This test verifies that:
    1. Query embedding is generated correctly
    2. Cosine similarity is computed for each annotation
    3. Results are ranked by similarity score
    4. Ranking matches golden data expectations
    
    Uses mock embeddings to ensure deterministic results.
    
    Requirements: 9.2, 8.2, 8.3
    """
    # Load golden data
    golden_data = load_golden_data("annotations_search")
    test_case = golden_data["semantic_search"]
    
    input_data = test_case["input"]
    expected_data = test_case["expected"]
    
    # Create test resource
    resource = create_test_resource(title="ML Research Paper")
    
    # Create annotations with mock embeddings from golden data
    annotations_data = []
    for ann_data in input_data["annotations"]:
        annotation = create_test_annotation(
            resource_id=resource.id,
            user_id="test_user",
            highlighted_text=ann_data["text"],
            start_offset=ann_data["id"] * 100,  # Arbitrary offsets
            end_offset=ann_data["id"] * 100 + len(ann_data["text"]),
            note=ann_data["text"],  # Use text as note for semantic search
            embedding=ann_data["embedding"]  # Set embedding directly
        )
        annotations_data.append((ann_data["id"], annotation))
    
    # Create service
    service = AnnotationService(db_session)
    
    # Mock the embedding generator to return query embedding from golden data
    with patch.object(service.embedding_generator, 'generate_embedding') as mock_embed:
        mock_embed.return_value = input_data["query_embedding"]
        
        # Perform semantic search
        results = service.search_annotations_semantic(
            user_id="test_user",
            query=input_data["query"],
            limit=10
        )
    
    # Verify mock was called with query
    mock_embed.assert_called_once_with(input_data["query"])
    
    # Extract annotation IDs from results
    # Map annotation objects back to their original IDs from golden data
    annotation_id_map = {ann.id: ann_id for ann_id, ann in annotations_data}
    actual_ranked_ids = [annotation_id_map[ann.id] for ann, score in results]
    
    # Verify ranking matches golden data
    expected_ranked_ids = expected_data["ranked_annotation_ids"]
    assert actual_ranked_ids == expected_ranked_ids, (
        f"Ranking mismatch: expected {expected_ranked_ids}, got {actual_ranked_ids}"
    )
    
    # Verify similarity scores are within tolerance
    expected_scores = expected_data["similarity_scores"]
    tolerance = expected_data["tolerance"]
    
    for ann, score in results:
        ann_id = annotation_id_map[ann.id]
        expected_score = expected_scores[str(ann_id)]
        
        assert abs(score - expected_score) <= tolerance, (
            f"Similarity score mismatch for annotation {ann_id}: "
            f"expected {expected_score}, got {score}"
        )
    
    # Verify results are sorted by score descending
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by score descending"


def test_annotation_semantic_search_no_embeddings(db_session, create_test_resource, create_test_annotation):
    """
    Test semantic search when annotations have no embeddings.
    
    Should return empty results gracefully.
    
    Requirements: 9.2
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Test Resource")
    
    # Create annotations without embeddings (no note)
    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Text without note",
        start_offset=0,
        end_offset=20,
        note=None  # No note means no embedding
    )
    
    # Mock embedding generator
    with patch.object(service.embedding_generator, 'generate_embedding') as mock_embed:
        mock_embed.return_value = [0.5, 0.5, 0.5, 0.5]
        
        results = service.search_annotations_semantic(
            user_id="test_user",
            query="test query",
            limit=10
        )
    
    # Should return empty results since no annotations have embeddings
    assert len(results) == 0


def test_annotation_semantic_search_empty_query(db_session, create_test_resource, create_test_annotation):
    """
    Test semantic search with empty query.
    
    Should return empty results gracefully.
    
    Requirements: 9.2
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Test Resource")
    
    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Test annotation",
        start_offset=0,
        end_offset=15,
        note="Test note",
        embedding=[0.1, 0.2, 0.3, 0.4]
    )
    
    # Search with empty query
    results = service.search_annotations_semantic(
        user_id="test_user",
        query="",
        limit=10
    )
    
    # Should return empty results
    assert len(results) == 0


def test_annotation_semantic_search_limit(db_session, create_test_resource, create_test_annotation):
    """
    Test that semantic search respects the limit parameter.
    
    Requirements: 9.2
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Test Resource")
    
    # Create 5 annotations with embeddings
    for i in range(5):
        create_test_annotation(
            resource_id=resource.id,
            user_id="test_user",
            highlighted_text=f"Annotation {i}",
            start_offset=i * 100,
            end_offset=i * 100 + 20,
            note=f"Note {i}",
            embedding=[0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i]
        )
    
    # Mock embedding generator
    with patch.object(service.embedding_generator, 'generate_embedding') as mock_embed:
        mock_embed.return_value = [0.5, 0.5, 0.5, 0.5]
        
        # Search with limit=3
        results = service.search_annotations_semantic(
            user_id="test_user",
            query="test query",
            limit=3
        )
    
    # Should return exactly 3 results
    assert len(results) == 3
    
    # Verify all results have scores
    for ann, score in results:
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


def test_annotation_semantic_search_user_isolation(db_session, create_test_resource, create_test_annotation):
    """
    Test that semantic search only returns annotations for the requesting user.
    
    Requirements: 9.2, 8.3
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Shared Resource")
    
    # Create annotations for user1
    create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="User 1 annotation",
        start_offset=0,
        end_offset=20,
        note="User 1 note",
        embedding=[0.8, 0.2, 0.7, 0.3]
    )
    
    # Create annotations for user2
    create_test_annotation(
        resource_id=resource.id,
        user_id="user2",
        highlighted_text="User 2 annotation",
        start_offset=30,
        end_offset=50,
        note="User 2 note",
        embedding=[0.7, 0.3, 0.8, 0.2]
    )
    
    # Mock embedding generator
    with patch.object(service.embedding_generator, 'generate_embedding') as mock_embed:
        mock_embed.return_value = [0.75, 0.25, 0.75, 0.25]
        
        # Search as user1
        results_user1 = service.search_annotations_semantic(
            user_id="user1",
            query="test query",
            limit=10
        )
        
        # Search as user2
        results_user2 = service.search_annotations_semantic(
            user_id="user2",
            query="test query",
            limit=10
        )
    
    # Each user should only see their own annotations
    assert len(results_user1) == 1
    assert results_user1[0][0].user_id == "user1"
    
    assert len(results_user2) == 1
    assert results_user2[0][0].user_id == "user2"
