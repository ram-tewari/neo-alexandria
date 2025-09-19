# Phase 5.5 Recommendation System Test Suite

This document describes the comprehensive test suite for the Phase 5.5 Personalized Recommendation Engine.

## Overview

The recommendation system test suite provides comprehensive coverage of:
- **Unit Tests**: Core functions and utilities
- **Integration Tests**: End-to-end recommendation generation
- **API Tests**: HTTP endpoint functionality
- **Edge Cases**: Error handling and boundary conditions
- **Performance Tests**: Scalability and caching behavior

## Test Structure

### Test Files

- `test_phase55_recommendations.py` - Main test suite
- `test_recommendation_config.py` - Test utilities and helpers
- `run_recommendation_tests.py` - Specialized test runner
- `conftest.py` - Enhanced with recommendation-specific fixtures

### Test Markers

The test suite uses pytest markers for organization:

- `@pytest.mark.recommendation` - All recommendation tests
- `@pytest.mark.recommendation_unit` - Unit tests for components
- `@pytest.mark.recommendation_integration` - Integration tests
- `@pytest.mark.recommendation_api` - API endpoint tests
- `@pytest.mark.recommendation_performance` - Performance tests
- `@pytest.mark.recommendation_edge_cases` - Edge case tests
- `@pytest.mark.slow` - Tests that take longer to run

## Test Categories

### 1. Unit Tests (15 tests)

**TestCosineSimilarity** - Vector similarity computation
- `test_identical_vectors()` - Identical vectors = 1.0 similarity
- `test_orthogonal_vectors()` - Orthogonal vectors = 0.0 similarity
- `test_opposite_vectors()` - Opposite vectors clamped to 0.0
- `test_zero_vector_handling()` - Zero vectors handled gracefully
- `test_different_length_vectors()` - Mismatched dimensions = 0.0
- `test_score_clamping()` - Scores properly clamped to [0,1]

**TestVectorConversion** - Vector utility functions
- `test_to_numpy_vector_valid()` - Valid list conversion
- `test_to_numpy_vector_empty()` - Empty list handling
- `test_to_numpy_vector_none()` - None value handling
- `test_to_numpy_vector_invalid()` - Invalid data handling

**TestUserProfileGeneration** - Profile vector creation
- `test_generate_profile_with_embeddings()` - Valid embeddings
- `test_generate_profile_empty_library()` - Empty library handling
- `test_generate_profile_no_embeddings()` - No embeddings case

**TestTopSubjectsExtraction** - Seed keyword extraction
- `test_get_top_subjects()` - Top subjects by usage count
- `test_get_top_subjects_empty()` - Empty authority table

### 2. Integration Tests (3 tests)

**TestRecommendationService** - Complete recommendation flow
- `test_generate_recommendations_full_flow()` - End-to-end generation
- `test_generate_recommendations_empty_library()` - Empty library
- `test_generate_recommendations_single_resource()` - Single resource

### 3. API Tests (7 tests)

**TestRecommendationAPI** - HTTP endpoint functionality
- `test_get_recommendations_success()` - Successful retrieval
- `test_get_recommendations_with_limit()` - Custom limit handling
- `test_get_recommendations_invalid_limit()` - Validation errors
- `test_get_recommendations_empty_library()` - Empty library response
- `test_duplicate_filtering()` - URL deduplication
- `test_relevance_score_ordering()` - Score-based ordering
- `test_recommendations_endpoint_basic()` - Legacy basic test

### 4. Edge Cases (3 tests)

**TestEdgeCases** - Error handling and boundary conditions
- `test_malformed_embeddings()` - Invalid embedding data
- `test_mixed_embedding_dimensions()` - Different vector sizes
- `test_search_provider_failure()` - External service failures

### 5. Performance Tests (2 tests)

**TestPerformance** - Scalability and efficiency
- `test_large_library_performance()` - 100+ resources (marked as slow)
- `test_caching_behavior()` - Search result caching

### 6. Legacy Tests (2 tests)

- `test_recommendations_endpoint_basic()` - Original basic functionality
- `test_profile_sensitivity()` - Profile change detection

## Test Fixtures

### Core Fixtures

- `test_db()` - Database session for testing
- `client()` - FastAPI test client
- `recommendation_test_data()` - Comprehensive test data
- `mock_ddgs_search()` - Mocked search provider
- `mock_ai_core()` - Mocked AI embedding generation
- `empty_library()` - Empty database state
- `single_resource_library()` - Minimal test data

### Test Data

The `recommendation_test_data` fixture provides:
- **10 Authority Subjects** with varying usage counts
- **7 Resources** with embeddings and quality scores
- **High-quality resources** (top 5 by quality)
- **Low-quality resources** (for comparison)

## Running Tests

### Using the Specialized Runner

```bash
# Run all recommendation tests
python tests/run_recommendation_tests.py all

# Run only unit tests
python tests/run_recommendation_tests.py unit

# Run with coverage
python tests/run_recommendation_tests.py coverage

# Run performance tests
python tests/run_recommendation_tests.py performance
```

### Using pytest directly

```bash
# All recommendation tests
python -m pytest -m recommendation

# Unit tests only
python -m pytest -m recommendation_unit

# API tests only
python -m pytest -m recommendation_api

# Integration tests only
python -m pytest -m recommendation_integration

# Edge cases only
python -m pytest -m recommendation_edge_cases

# Performance tests (includes slow tests)
python -m pytest -m recommendation_performance

# Quick tests (excludes slow)
python -m pytest -m "recommendation and not slow"
```

### Coverage Reports

```bash
# Generate HTML coverage report
python -m pytest -m recommendation --cov=backend.app.services.recommendation_service --cov-report=html:htmlcov_recommendations

# Terminal coverage report
python -m pytest -m recommendation --cov=backend.app.services.recommendation_service --cov-report=term-missing
```

## Test Assertions

### Recommendation Quality Validation

- **Structure Validation**: All required fields present
- **Score Range**: Relevance scores in [0,1]
- **Ordering**: Results sorted by relevance score (descending)
- **Deduplication**: No duplicate URLs
- **Reasoning**: Contains expected seed keywords

### Performance Benchmarks

- **Large Library**: 100+ resources processed in <10 seconds
- **Caching**: Search results cached for 5 minutes
- **Memory**: Efficient vector operations with NumPy

## Mocking Strategy

### External Dependencies

- **DDGS Search**: Mocked with deterministic results
- **AI Core**: Mocked with hash-based embeddings
- **Database**: In-memory SQLite for isolation

### Test Isolation

- Each test uses fresh database state
- Mocks are reset between tests
- No external network calls during testing

## Continuous Integration

The test suite is designed for CI/CD pipelines:

- **Fast Tests**: Unit and API tests run quickly
- **Slow Tests**: Performance tests marked appropriately
- **Coverage**: Comprehensive coverage reporting
- **Parallel Execution**: Support for parallel test runs

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies installed
2. **Database Issues**: Check SQLite file permissions
3. **Mock Failures**: Verify mock setup in fixtures
4. **Performance**: Adjust timeouts for slower systems

### Debug Mode

```bash
# Verbose output with full tracebacks
python -m pytest -m recommendation -v -s --tb=long

# Run specific test with debugging
python -m pytest tests/test_phase55_recommendations.py::TestCosineSimilarity::test_identical_vectors -v -s
```

## Test Coverage

The test suite provides comprehensive coverage of:

- ✅ **Core Functions**: 100% coverage of utility functions
- ✅ **Service Layer**: Full recommendation generation flow
- ✅ **API Layer**: All endpoint scenarios
- ✅ **Error Handling**: Graceful failure modes
- ✅ **Edge Cases**: Boundary conditions and invalid data
- ✅ **Performance**: Scalability and caching behavior

## Future Enhancements

Potential additions to the test suite:

- **Load Testing**: High-concurrency scenarios
- **Integration Testing**: Real external service testing
- **Property-Based Testing**: Randomized input validation
- **Visual Testing**: Recommendation quality assessment
- **A/B Testing**: Recommendation algorithm comparison
