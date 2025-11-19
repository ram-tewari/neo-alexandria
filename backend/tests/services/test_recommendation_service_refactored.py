"""
Tests for refactored recommendation_service.py using Strategy pattern.

Validates that the service correctly delegates to strategies and
maintains backward compatibility.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.app.services.recommendation_service import (
    generate_recommendations,
    get_graph_based_recommendations,
    generate_recommendations_with_graph_fusion,
    generate_user_profile_vector,
    recommend_based_on_annotations,
    get_top_subjects
)
from backend.app.domain.recommendation import Recommendation, RecommendationScore


class TestGenerateRecommendations:
    """Test the main generate_recommendations function."""
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_uses_strategy_factory(self, mock_factory):
        """Test that generate_recommendations uses the strategy factory."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.generate.return_value = []
        mock_factory.create.return_value = mock_strategy
        
        # Call function
        result = generate_recommendations(
            db=db,
            user_id=user_id,
            limit=10,
            strategy='hybrid'
        )
        
        # Verify factory was called
        mock_factory.create.assert_called_once_with(
            strategy_type='hybrid',
            db=db
        )
        
        # Verify strategy was used
        mock_strategy.generate.assert_called_once_with(
            user_id=user_id,
            limit=10
        )
        
        assert result == []
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_converts_recommendations_to_dict(self, mock_factory):
        """Test that recommendations are converted to dict format."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Create mock recommendation
        mock_rec = Mock(spec=Recommendation)
        mock_rec.to_dict.return_value = {
            'resource_id': 'resource_123',
            'score': 0.85
        }
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.generate.return_value = [mock_rec]
        mock_factory.create.return_value = mock_strategy
        
        # Call function
        result = generate_recommendations(
            db=db,
            user_id=user_id,
            limit=10,
            strategy='collaborative'
        )
        
        # Verify conversion
        assert len(result) == 1
        assert result[0]['resource_id'] == 'resource_123'
        assert result[0]['score'] == 0.85
        mock_rec.to_dict.assert_called_once()
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_handles_resource_id_fallback(self, mock_factory):
        """Test that resource_id is used as fallback for user_id."""
        db = Mock(spec=Session)
        resource_id = uuid4()
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.generate.return_value = []
        mock_factory.create.return_value = mock_strategy
        
        # Call function with resource_id instead of user_id
        result = generate_recommendations(
            db=db,
            resource_id=resource_id,
            limit=10,
            strategy='content'
        )
        
        # Verify strategy was called with resource_id as user_id
        mock_strategy.generate.assert_called_once_with(
            user_id=str(resource_id),
            limit=10
        )
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_returns_empty_list_without_user_id(self, mock_factory):
        """Test that empty list is returned when no user_id or resource_id."""
        db = Mock(spec=Session)
        
        # Call function without user_id or resource_id
        result = generate_recommendations(
            db=db,
            limit=10,
            strategy='hybrid'
        )
        
        # Should return empty list without calling factory
        assert result == []
        mock_factory.create.assert_not_called()
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_handles_invalid_strategy(self, mock_factory):
        """Test that ValueError is raised for invalid strategy."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Mock factory to raise ValueError
        mock_factory.create.side_effect = ValueError("Unknown strategy type")
        
        # Call function with invalid strategy
        with pytest.raises(ValueError):
            generate_recommendations(
                db=db,
                user_id=user_id,
                limit=10,
                strategy='invalid_strategy'
            )


class TestGetGraphBasedRecommendations:
    """Test the get_graph_based_recommendations function."""
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_uses_graph_strategy(self, mock_factory):
        """Test that function uses graph strategy."""
        db = Mock(spec=Session)
        resource_id = uuid4()
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.generate.return_value = []
        mock_factory.create.return_value = mock_strategy
        
        # Call function
        result = get_graph_based_recommendations(
            db=db,
            resource_id=resource_id,
            limit=10
        )
        
        # Verify graph strategy was created
        mock_factory.create.assert_called_once_with('graph', db)
        
        # Verify strategy was used
        mock_strategy.generate.assert_called_once_with(
            user_id=str(resource_id),
            limit=10
        )


class TestGenerateRecommendationsWithGraphFusion:
    """Test the generate_recommendations_with_graph_fusion function."""
    
    @patch('backend.app.services.recommendation_strategies.HybridStrategy')
    @patch('backend.app.services.recommendation_strategies.GraphBasedStrategy')
    @patch('backend.app.services.recommendation_strategies.ContentBasedStrategy')
    @patch('backend.app.services.recommendation_strategies.CollaborativeFilteringStrategy')
    def test_creates_hybrid_with_custom_weights(
        self,
        mock_collab,
        mock_content,
        mock_graph,
        mock_hybrid
    ):
        """Test that function creates hybrid strategy with custom weights."""
        db = Mock(spec=Session)
        resource_id = uuid4()
        graph_weight = 0.4
        
        # Mock strategies
        mock_collab_instance = Mock()
        mock_content_instance = Mock()
        mock_graph_instance = Mock()
        mock_hybrid_instance = Mock()
        mock_hybrid_instance.generate.return_value = []
        
        mock_collab.return_value = mock_collab_instance
        mock_content.return_value = mock_content_instance
        mock_graph.return_value = mock_graph_instance
        mock_hybrid.return_value = mock_hybrid_instance
        
        # Call function
        result = generate_recommendations_with_graph_fusion(
            db=db,
            resource_id=resource_id,
            limit=10,
            graph_weight=graph_weight
        )
        
        # Verify hybrid strategy was created with correct weights
        mock_hybrid.assert_called_once()
        call_args = mock_hybrid.call_args
        
        # Check strategies list
        strategies = call_args[0][1]
        assert len(strategies) == 3
        
        # Check weights
        weights = call_args[0][2]
        assert len(weights) == 3
        assert weights[2] == graph_weight  # Graph weight
        assert abs(sum(weights) - 1.0) < 0.001  # Weights sum to 1


class TestGenerateUserProfileVector:
    """Test the generate_user_profile_vector function."""
    
    @patch('backend.app.services.recommendation_strategies.ContentBasedStrategy')
    def test_uses_content_strategy(self, mock_content_class):
        """Test that function uses content-based strategy."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Mock interactions query
        db.query.return_value.filter.return_value.all.return_value = [Mock()]
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy._build_user_profile.return_value = [0.1] * 768
        mock_content_class.return_value = mock_strategy
        
        # Call function
        result = generate_user_profile_vector(db, user_id)
        
        # Verify result
        assert len(result) == 768
        assert result[0] == 0.1
    
    def test_returns_zero_vector_for_no_interactions(self):
        """Test that zero vector is returned when no interactions."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Mock empty interactions
        db.query.return_value.filter.return_value.all.return_value = []
        
        # Call function
        result = generate_user_profile_vector(db, user_id)
        
        # Verify zero vector
        assert len(result) == 768
        assert all(x == 0.0 for x in result)


class TestRecommendBasedOnAnnotations:
    """Test the recommend_based_on_annotations function."""
    
    @patch('backend.app.services.recommendation_service.RecommendationStrategyFactory')
    def test_uses_content_strategy(self, mock_factory):
        """Test that function uses content-based strategy."""
        db = Mock(spec=Session)
        user_id = str(uuid4())
        
        # Mock strategy
        mock_strategy = Mock()
        mock_strategy.generate.return_value = []
        mock_factory.create.return_value = mock_strategy
        
        # Call function
        result = recommend_based_on_annotations(
            db=db,
            user_id=user_id,
            limit=10
        )
        
        # Verify content strategy was created
        mock_factory.create.assert_called_once_with('content', db)


class TestGetTopSubjects:
    """Test the get_top_subjects function."""
    
    def test_returns_top_subjects_by_count(self):
        """Test that function returns subjects sorted by frequency."""
        db = Mock(spec=Session)
        
        # Create mock resources with subjects
        resource1 = Mock()
        resource1.subject = ['AI', 'ML']
        
        resource2 = Mock()
        resource2.subject = ['AI', 'Python']
        
        resource3 = Mock()
        resource3.subject = ['ML']
        
        # Mock query
        db.query.return_value.filter.return_value.all.return_value = [
            resource1, resource2, resource3
        ]
        
        # Call function
        result = get_top_subjects(db, limit=3)
        
        # Verify results (AI: 2, ML: 2, Python: 1)
        assert len(result) <= 3
        # AI and ML should be first (tied at 2 occurrences)
        assert 'AI' in result
        assert 'ML' in result
    
    def test_returns_empty_list_for_no_resources(self):
        """Test that empty list is returned when no resources."""
        db = Mock(spec=Session)
        
        # Mock empty query
        db.query.return_value.filter.return_value.all.return_value = []
        
        # Call function
        result = get_top_subjects(db, limit=10)
        
        # Verify empty list
        assert result == []
