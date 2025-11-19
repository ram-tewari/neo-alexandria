"""
Tests for recommendation strategy pattern implementation.

Tests the Strategy pattern refactoring that replaces conditional logic
with polymorphic strategies for recommendation generation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from backend.app.services.recommendation_strategies import (
    RecommendationStrategy,
    CollaborativeFilteringStrategy,
    ContentBasedStrategy,
    GraphBasedStrategy,
    HybridStrategy,
    RecommendationStrategyFactory
)
from backend.app.domain.recommendation import Recommendation, RecommendationScore


class TestRecommendationStrategyFactory:
    """Test the strategy factory."""
    
    def test_create_collaborative_strategy(self):
        """Test creating collaborative filtering strategy."""
        db = Mock(spec=Session)
        strategy = RecommendationStrategyFactory.create('collaborative', db)
        
        assert isinstance(strategy, CollaborativeFilteringStrategy)
        assert strategy.get_strategy_name() == 'collaborative_filtering'
    
    def test_create_content_strategy(self):
        """Test creating content-based strategy."""
        db = Mock(spec=Session)
        strategy = RecommendationStrategyFactory.create('content', db)
        
        assert isinstance(strategy, ContentBasedStrategy)
        assert strategy.get_strategy_name() == 'content_based'
    
    def test_create_graph_strategy(self):
        """Test creating graph-based strategy."""
        db = Mock(spec=Session)
        strategy = RecommendationStrategyFactory.create('graph', db)
        
        assert isinstance(strategy, GraphBasedStrategy)
        assert strategy.get_strategy_name() == 'graph_based'
    
    def test_create_hybrid_strategy(self):
        """Test creating hybrid strategy."""
        db = Mock(spec=Session)
        strategy = RecommendationStrategyFactory.create('hybrid', db)
        
        assert isinstance(strategy, HybridStrategy)
        assert strategy.get_strategy_name() == 'hybrid'
    
    def test_create_unknown_strategy_raises_error(self):
        """Test that unknown strategy type raises ValueError."""
        db = Mock(spec=Session)
        
        with pytest.raises(ValueError, match="Unknown strategy type"):
            RecommendationStrategyFactory.create('unknown', db)
    
    def test_get_available_strategies(self):
        """Test getting list of available strategies."""
        strategies = RecommendationStrategyFactory.get_available_strategies()
        
        assert 'collaborative' in strategies
        assert 'content' in strategies
        assert 'graph' in strategies
        assert 'hybrid' in strategies
    
    def test_create_all_strategies(self):
        """Test creating all strategies at once."""
        db = Mock(spec=Session)
        all_strategies = RecommendationStrategyFactory.create_all_strategies(db)
        
        assert len(all_strategies) == 4
        assert 'collaborative' in all_strategies
        assert 'content' in all_strategies
        assert 'graph' in all_strategies
        assert 'hybrid' in all_strategies


class TestCollaborativeFilteringStrategy:
    """Test collaborative filtering strategy."""
    
    def test_strategy_name(self):
        """Test strategy returns correct name."""
        db = Mock(spec=Session)
        strategy = CollaborativeFilteringStrategy(db)
        
        assert strategy.get_strategy_name() == 'collaborative_filtering'
    
    @patch('backend.app.services.ncf_service.NCFService')
    def test_generate_with_trained_model(self, mock_ncf_service_class):
        """Test generating recommendations with trained NCF model."""
        db = Mock(spec=Session)
        strategy = CollaborativeFilteringStrategy(db)
        
        # Mock NCF service
        mock_ncf = MagicMock()
        mock_ncf.is_model_trained.return_value = True
        mock_ncf.get_top_recommendations.return_value = [
            ('resource_1', 0.9),
            ('resource_2', 0.8),
            ('resource_3', 0.7)
        ]
        mock_ncf_service_class.return_value = mock_ncf
        
        # Generate recommendations
        recommendations = strategy.generate('user_123', limit=3)
        
        # Verify results
        assert len(recommendations) == 3
        assert all(isinstance(rec, Recommendation) for rec in recommendations)
        assert recommendations[0].resource_id == 'resource_1'
        assert recommendations[0].get_rank() == 1
        assert recommendations[0].strategy == 'collaborative_filtering'
    
    @patch('backend.app.services.ncf_service.NCFService')
    def test_generate_without_trained_model(self, mock_ncf_service_class):
        """Test generating recommendations without trained model."""
        db = Mock(spec=Session)
        strategy = CollaborativeFilteringStrategy(db)
        
        # Mock NCF service with no trained model
        mock_ncf = MagicMock()
        mock_ncf.is_model_trained.return_value = False
        mock_ncf_service_class.return_value = mock_ncf
        
        # Generate recommendations
        recommendations = strategy.generate('user_123', limit=10)
        
        # Should return empty list
        assert recommendations == []


class TestContentBasedStrategy:
    """Test content-based strategy."""
    
    def test_strategy_name(self):
        """Test strategy returns correct name."""
        db = Mock(spec=Session)
        strategy = ContentBasedStrategy(db)
        
        assert strategy.get_strategy_name() == 'content_based'
    
    def test_generate_with_no_interactions(self):
        """Test generating recommendations with no user interactions."""
        db = Mock(spec=Session)
        strategy = ContentBasedStrategy(db)
        
        # Mock empty interactions
        db.query.return_value.filter.return_value.all.return_value = []
        
        # Generate recommendations
        recommendations = strategy.generate('user_123', limit=10)
        
        # Should return empty list
        assert recommendations == []


class TestGraphBasedStrategy:
    """Test graph-based strategy."""
    
    def test_strategy_name(self):
        """Test strategy returns correct name."""
        db = Mock(spec=Session)
        strategy = GraphBasedStrategy(db)
        
        assert strategy.get_strategy_name() == 'graph_based'
    
    def test_generate_with_no_interactions(self):
        """Test generating recommendations with no user interactions."""
        db = Mock(spec=Session)
        strategy = GraphBasedStrategy(db)
        
        # Mock empty interactions
        db.query.return_value.filter.return_value.all.return_value = []
        
        # Generate recommendations
        recommendations = strategy.generate('user_123', limit=10)
        
        # Should return empty list
        assert recommendations == []


class TestHybridStrategy:
    """Test hybrid strategy."""
    
    def test_strategy_name(self):
        """Test strategy returns correct name."""
        db = Mock(spec=Session)
        strategy = HybridStrategy(db)
        
        assert strategy.get_strategy_name() == 'hybrid'
    
    def test_initialization_with_custom_strategies(self):
        """Test initializing with custom strategies and weights."""
        db = Mock(spec=Session)
        
        mock_strategy1 = Mock(spec=RecommendationStrategy)
        mock_strategy2 = Mock(spec=RecommendationStrategy)
        
        strategy = HybridStrategy(
            db,
            strategies=[mock_strategy1, mock_strategy2],
            weights=[0.6, 0.4]
        )
        
        assert len(strategy.strategies) == 2
        assert len(strategy.weights) == 2
        assert abs(sum(strategy.weights) - 1.0) < 0.001  # Weights sum to 1
    
    def test_initialization_with_mismatched_weights(self):
        """Test that mismatched weights raise error."""
        db = Mock(spec=Session)
        
        mock_strategy1 = Mock(spec=RecommendationStrategy)
        mock_strategy2 = Mock(spec=RecommendationStrategy)
        
        with pytest.raises(ValueError, match="Number of weights"):
            HybridStrategy(
                db,
                strategies=[mock_strategy1, mock_strategy2],
                weights=[0.5]  # Only one weight for two strategies
            )
    
    def test_generate_fuses_multiple_strategies(self):
        """Test that hybrid strategy fuses results from multiple strategies."""
        db = Mock(spec=Session)
        
        # Create mock strategies
        mock_strategy1 = Mock(spec=RecommendationStrategy)
        mock_strategy1.get_strategy_name.return_value = 'strategy1'
        mock_strategy1.generate.return_value = [
            Recommendation(
                resource_id='resource_1',
                user_id='user_123',
                recommendation_score=RecommendationScore(0.9, 0.9, 1),
                strategy='strategy1'
            )
        ]
        
        mock_strategy2 = Mock(spec=RecommendationStrategy)
        mock_strategy2.get_strategy_name.return_value = 'strategy2'
        mock_strategy2.generate.return_value = [
            Recommendation(
                resource_id='resource_1',
                user_id='user_123',
                recommendation_score=RecommendationScore(0.8, 0.8, 1),
                strategy='strategy2'
            ),
            Recommendation(
                resource_id='resource_2',
                user_id='user_123',
                recommendation_score=RecommendationScore(0.7, 0.7, 2),
                strategy='strategy2'
            )
        ]
        
        # Create hybrid strategy
        strategy = HybridStrategy(
            db,
            strategies=[mock_strategy1, mock_strategy2],
            weights=[0.5, 0.5]
        )
        
        # Generate recommendations
        recommendations = strategy.generate('user_123', limit=10)
        
        # Verify fusion occurred
        assert len(recommendations) > 0
        assert all(isinstance(rec, Recommendation) for rec in recommendations)
        assert all(rec.strategy == 'hybrid' for rec in recommendations)


class TestRecommendationStrategyBase:
    """Test base strategy class functionality."""
    
    def test_create_recommendation_helper(self):
        """Test the _create_recommendation helper method."""
        db = Mock(spec=Session)
        
        # Create a concrete strategy to test the helper
        strategy = CollaborativeFilteringStrategy(db)
        
        # Create a recommendation using the helper
        rec = strategy._create_recommendation(
            resource_id='resource_123',
            user_id='user_456',
            score=0.85,
            confidence=0.9,
            rank=1,
            reason='Test reason',
            metadata={'key': 'value'}
        )
        
        # Verify recommendation
        assert isinstance(rec, Recommendation)
        assert rec.resource_id == 'resource_123'
        assert rec.user_id == 'user_456'
        assert rec.get_score() == 0.85
        assert rec.get_confidence() == 0.9
        assert rec.get_rank() == 1
        assert rec.reason == 'Test reason'
        assert rec.metadata['key'] == 'value'
        assert rec.strategy == 'collaborative_filtering'
