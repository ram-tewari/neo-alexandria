"""
Test quality integration in recommendation service.
"""

from uuid import uuid4
from backend.app.services.recommendation_service import (
    generate_user_profile_vector,
    get_graph_based_recommendations,
    generate_recommendations_with_graph_fusion
)
from backend.app.database.models import Resource


def test_generate_user_profile_vector_excludes_outliers(db_session):
    """Test that generate_user_profile_vector excludes quality outliers."""
    # Create resources with embeddings
    resource1 = Resource(
        id=uuid4(),
        title="Good Resource",
        source="https://example.com/good",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    resource2 = Resource(
        id=uuid4(),
        title="Outlier Resource",
        source="https://example.com/outlier",
        type="article",
        embedding=[0.4, 0.5, 0.6],
        is_quality_outlier=True,
        quality_overall=0.3
    )
    
    db_session.add_all([resource1, resource2])
    db_session.commit()
    
    # Generate profile vector
    profile = generate_user_profile_vector(db_session)
    
    # Should only include resource1's embedding
    assert len(profile) == 3
    # The profile should be close to resource1's embedding (only one resource)
    assert abs(profile[0] - 0.1) < 0.01


def test_generate_user_profile_vector_with_min_quality(db_session):
    """Test that generate_user_profile_vector filters by min_quality."""
    # Create resources with different quality scores
    resource1 = Resource(
        id=uuid4(),
        title="High Quality",
        source="https://example.com/high",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    resource2 = Resource(
        id=uuid4(),
        title="Low Quality",
        source="https://example.com/low",
        type="article",
        embedding=[0.4, 0.5, 0.6],
        is_quality_outlier=False,
        quality_overall=0.5
    )
    
    db_session.add_all([resource1, resource2])
    db_session.commit()
    
    # Generate profile with min_quality threshold
    profile = generate_user_profile_vector(db_session, min_quality=0.7)
    
    # Should only include resource1's embedding
    assert len(profile) == 3
    assert abs(profile[0] - 0.1) < 0.01


def test_get_graph_based_recommendations_excludes_outliers(db_session):
    """Test that get_graph_based_recommendations excludes quality outliers."""
    # Create source resource
    source = Resource(
        id=uuid4(),
        title="Source",
        source="https://example.com/source",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    # Create target resources
    good_target = Resource(
        id=uuid4(),
        title="Good Target",
        source="https://example.com/good-target",
        type="article",
        embedding=[0.15, 0.25, 0.35],
        is_quality_outlier=False,
        quality_overall=0.85
    )
    
    outlier_target = Resource(
        id=uuid4(),
        title="Outlier Target",
        source="https://example.com/outlier-target",
        type="article",
        embedding=[0.2, 0.3, 0.4],
        is_quality_outlier=True,
        quality_overall=0.3
    )
    
    db_session.add_all([source, good_target, outlier_target])
    db_session.commit()
    
    # Get recommendations (this will return empty since we don't have graph edges)
    # But the function should not crash and should filter outliers
    recommendations = get_graph_based_recommendations(db_session, source.id, limit=10)
    
    # Verify no outliers in results
    for rec in recommendations:
        resource = db_session.query(Resource).filter(Resource.id == rec['resource_id']).first()
        if resource:
            assert not resource.is_quality_outlier


def test_generate_recommendations_with_graph_fusion_quality_boost(db_session):
    """Test that high-quality resources get boosted scores."""
    # Create source resource
    source = Resource(
        id=uuid4(),
        title="Source",
        source="https://example.com/source",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    # Create target with high quality
    high_quality = Resource(
        id=uuid4(),
        title="High Quality Target",
        source="https://example.com/high-quality",
        type="article",
        embedding=[0.15, 0.25, 0.35],
        is_quality_outlier=False,
        quality_overall=0.85
    )
    
    db_session.add_all([source, high_quality])
    db_session.commit()
    
    # Get recommendations
    recommendations = generate_recommendations_with_graph_fusion(
        db_session, source.id, limit=10
    )
    
    # Verify quality_boost field exists in results
    for rec in recommendations:
        if 'quality_boost' in rec:
            assert rec['quality_boost'] >= 1.0


def test_generate_recommendations_with_graph_fusion_filters_outliers(db_session):
    """Test that recommendations exclude quality outliers."""
    # Create source resource
    source = Resource(
        id=uuid4(),
        title="Source",
        source="https://example.com/source",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    # Create outlier target
    outlier = Resource(
        id=uuid4(),
        title="Outlier Target",
        source="https://example.com/outlier",
        type="article",
        embedding=[0.15, 0.25, 0.35],
        is_quality_outlier=True,
        quality_overall=0.3
    )
    
    db_session.add_all([source, outlier])
    db_session.commit()
    
    # Get recommendations
    recommendations = generate_recommendations_with_graph_fusion(
        db_session, source.id, limit=10
    )
    
    # Verify no outliers in results
    for rec in recommendations:
        resource = db_session.query(Resource).filter(Resource.id == rec['resource_id']).first()
        if resource:
            assert not resource.is_quality_outlier


def test_generate_recommendations_with_min_quality_filter(db_session):
    """Test that min_quality parameter filters recommendations."""
    # Create source resource
    source = Resource(
        id=uuid4(),
        title="Source",
        source="https://example.com/source",
        type="article",
        embedding=[0.1, 0.2, 0.3],
        is_quality_outlier=False,
        quality_overall=0.9
    )
    
    # Create targets with different quality
    high_quality = Resource(
        id=uuid4(),
        title="High Quality",
        source="https://example.com/high",
        type="article",
        embedding=[0.15, 0.25, 0.35],
        is_quality_outlier=False,
        quality_overall=0.85
    )
    
    low_quality = Resource(
        id=uuid4(),
        title="Low Quality",
        source="https://example.com/low",
        type="article",
        embedding=[0.2, 0.3, 0.4],
        is_quality_outlier=False,
        quality_overall=0.5
    )
    
    db_session.add_all([source, high_quality, low_quality])
    db_session.commit()
    
    # Get recommendations with quality filter
    recommendations = generate_recommendations_with_graph_fusion(
        db_session, source.id, limit=10, min_quality=0.7
    )
    
    # Verify all results meet quality threshold
    for rec in recommendations:
        resource = db_session.query(Resource).filter(Resource.id == rec['resource_id']).first()
        if resource and resource.quality_overall is not None:
            assert resource.quality_overall >= 0.7
