"""Tests for HybridSearchQuery class refactoring."""

import pytest
from datetime import datetime, timedelta, timezone

from backend.app.database.models import Resource
from backend.app.services.search_service import HybridSearchQuery
from backend.app.domain.search import SearchQuery


# sample_resources fixture is now in services/conftest.py


class TestHybridSearchQuery:
    """Test HybridSearchQuery class functionality."""
    
    def test_initialization(self, test_db):
        """Test HybridSearchQuery initialization."""
        db = test_db()
        query = SearchQuery(query_text="machine learning", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=True,
            adaptive_weighting=True
        )
        
        assert hybrid_query.db == db
        assert hybrid_query.query == query
        assert hybrid_query.enable_reranking is True
        assert hybrid_query.adaptive_weighting is True
        assert isinstance(hybrid_query._diagnostics, dict)
        
        db.close()
    
    def test_execute_returns_correct_structure(self, test_db, sample_resources):
        """Test that execute() returns the correct tuple structure."""
        db = test_db()
        query = SearchQuery(query_text="machine learning", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        result = hybrid_query.execute()
        
        # Should return 5-tuple
        assert len(result) == 5
        resources, total, facets, snippets, metadata = result
        
        # Check types
        assert isinstance(resources, list)
        assert isinstance(total, int)
        assert isinstance(snippets, dict)
        assert isinstance(metadata, dict)
        
        # Check metadata structure
        assert 'latency_ms' in metadata
        assert 'method_contributions' in metadata
        assert 'weights_used' in metadata
        assert 'reranking_enabled' in metadata
        assert 'adaptive_weighting' in metadata
        
        db.close()
    
    def test_get_diagnostic_info(self, test_db, sample_resources):
        """Test get_diagnostic_info() method."""
        db = test_db()
        query = SearchQuery(query_text="machine learning", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        # Execute the search
        hybrid_query.execute()
        
        # Get diagnostic info
        diagnostics = hybrid_query.get_diagnostic_info()
        
        # Check diagnostic structure
        assert isinstance(diagnostics, dict)
        assert 'query_analysis' in diagnostics
        assert 'retrieval_times' in diagnostics
        assert 'method_results' in diagnostics
        assert 'fusion_time' in diagnostics
        assert 'total_time' in diagnostics
        
        # Check query analysis
        assert isinstance(diagnostics['query_analysis'], dict)
        assert 'word_count' in diagnostics['query_analysis']
        assert 'is_short' in diagnostics['query_analysis']
        assert 'is_long' in diagnostics['query_analysis']
        
        # Check retrieval times
        assert isinstance(diagnostics['retrieval_times'], dict)
        assert 'total' in diagnostics['retrieval_times']
        assert 'fts5' in diagnostics['retrieval_times']
        assert 'dense' in diagnostics['retrieval_times']
        assert 'sparse' in diagnostics['retrieval_times']
        
        # Check method results
        assert isinstance(diagnostics['method_results'], dict)
        assert 'fts5' in diagnostics['method_results']
        assert 'dense' in diagnostics['method_results']
        assert 'sparse' in diagnostics['method_results']
        
        # Check timing values are reasonable
        assert diagnostics['total_time'] > 0
        assert diagnostics['fusion_time'] >= 0
        
        db.close()
    
    def test_diagnostic_info_is_copy(self, test_db):
        """Test that get_diagnostic_info() returns a copy, not reference."""
        db = test_db()
        query = SearchQuery(query_text="test", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=False
        )
        
        hybrid_query.execute()
        
        # Get diagnostics twice
        diagnostics1 = hybrid_query.get_diagnostic_info()
        diagnostics2 = hybrid_query.get_diagnostic_info()
        
        # Modify first copy
        diagnostics1['test_key'] = 'test_value'
        
        # Second copy should not be affected
        assert 'test_key' not in diagnostics2
        
        db.close()
    
    def test_with_reranking_disabled(self, test_db, sample_resources):
        """Test execution with reranking disabled."""
        db = test_db()
        query = SearchQuery(query_text="machine learning", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        result = hybrid_query.execute()
        resources, total, facets, snippets, metadata = result
        
        # Check that reranking was disabled
        assert metadata['reranking_enabled'] is False
        
        # Check diagnostics
        diagnostics = hybrid_query.get_diagnostic_info()
        # Reranking time should be 0 or not set when disabled
        assert diagnostics['reranking_time'] == 0.0
        
        db.close()
    
    def test_with_adaptive_weighting_disabled(self, test_db, sample_resources):
        """Test execution with adaptive weighting disabled."""
        db = test_db()
        query = SearchQuery(query_text="machine learning", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=False
        )
        
        result = hybrid_query.execute()
        resources, total, facets, snippets, metadata = result
        
        # Check that adaptive weighting was disabled
        assert metadata['adaptive_weighting'] is False
        
        # Weights should be equal when adaptive weighting is off
        weights = metadata['weights_used']
        assert len(weights) == 3
        # All weights should be approximately equal (1/3 each)
        for weight in weights:
            assert abs(weight - 1.0/3) < 0.01
        
        db.close()
    
    def test_empty_query(self, test_db):
        """Test execution with empty query."""
        db = test_db()
        query = SearchQuery(query_text="", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        result = hybrid_query.execute()
        resources, total, facets, snippets, metadata = result
        
        # Should handle empty query gracefully
        assert isinstance(resources, list)
        assert isinstance(metadata, dict)
        
        db.close()
    
    def test_private_methods_encapsulation(self, test_db):
        """Test that private methods are properly encapsulated."""
        db = test_db()
        query = SearchQuery(query_text="test", limit=10)
        
        hybrid_query = HybridSearchQuery(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=False
        )
        
        # Check that private methods exist
        assert hasattr(hybrid_query, '_ensure_tables_exist')
        assert hasattr(hybrid_query, '_check_services_available')
        assert hasattr(hybrid_query, '_analyze_query')
        # Phase-based methods (Split Phase refactoring)
        assert hasattr(hybrid_query, '_execute_retrieval_phase')
        assert hasattr(hybrid_query, '_execute_fusion_phase')
        assert hasattr(hybrid_query, '_execute_reranking_phase')
        # Individual retrieval methods
        assert hasattr(hybrid_query, '_search_fts5')
        assert hasattr(hybrid_query, '_search_dense')
        assert hasattr(hybrid_query, '_search_sparse')
        assert hasattr(hybrid_query, '_compute_weights')
        assert hasattr(hybrid_query, '_compute_method_contributions')
        assert hasattr(hybrid_query, '_fetch_paginated_resources')
        assert hasattr(hybrid_query, '_compute_facets')
        assert hasattr(hybrid_query, '_generate_snippets')
        
        # Check that all private methods are callable
        assert callable(hybrid_query._ensure_tables_exist)
        assert callable(hybrid_query._check_services_available)
        assert callable(hybrid_query._analyze_query)
        assert callable(hybrid_query._execute_retrieval_phase)
        assert callable(hybrid_query._execute_fusion_phase)
        assert callable(hybrid_query._execute_reranking_phase)
        
        db.close()
