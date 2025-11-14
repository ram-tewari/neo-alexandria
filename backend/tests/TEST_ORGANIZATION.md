# Test Organization

This document describes the organization of tests in the Neo Alexandria backend.

## Directory Structure

Tests are organized by **test type**, then by **phase**, then by **feature**:

```
tests/
├── unit/                           # Unit tests (isolated component testing)
│   ├── core/                       # Core utilities and services
│   ├── phase1_ingestion/           # Phase 1: Content ingestion
│   ├── phase2_curation/            # Phase 2: Resource curation
│   ├── phase3_search/              # Phase 3: Search functionality
│   ├── phase4_hybrid_search/       # Phase 4: Hybrid search (dense + sparse)
│   ├── phase5_graph/               # Phase 5: Knowledge graph
│   ├── phase6_citations/           # Phase 6: Citation management
│   ├── phase7_collections/         # Phase 7: Collections & annotations
│   ├── phase8_classification/      # Phase 8: ML classification
│   ├── phase9_quality/             # Phase 9: Quality assessment
│   └── phase10_graph_intelligence/ # Phase 10: Graph intelligence & LBD
│
├── integration/                    # Integration tests (multiple components)
│   ├── workflows/                  # Cross-cutting workflow tests
│   ├── phase1_ingestion/           # Phase 1 integration tests
│   ├── phase2_curation/            # Phase 2 integration tests
│   ├── phase3_search/              # Phase 3 integration tests
│   ├── phase4_hybrid_search/       # Phase 4 integration tests
│   ├── phase5_graph/               # Phase 5 integration tests
│   ├── phase6_citations/           # Phase 6 integration tests
│   ├── phase7_collections/         # Phase 7 integration tests
│   ├── phase8_classification/      # Phase 8 integration tests
│   ├── phase9_quality/             # Phase 9 integration tests
│   └── phase10_graph_intelligence/ # Phase 10 integration tests
│
└── performance/                    # Performance and load tests
    ├── phase9_quality/             # Quality assessment performance
    └── phase10_graph_intelligence/ # Graph intelligence performance
```

## Test Types

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution
- High code coverage focus

### Integration Tests (`tests/integration/`)
- Test multiple components working together
- Use real database connections (test DB)
- Test API endpoints
- Verify data flow between services

### Performance Tests (`tests/performance/`)
- Measure execution time and resource usage
- Test scalability
- Identify bottlenecks
- Benchmark critical operations

## Phase Organization

### Core (`unit/core/`)
Foundational utilities and services used across all phases:
- `test_ai_core.py` - AI/LLM integration
- `test_authority_service.py` - Authority control
- `test_content_extractor.py` - Content extraction
- `test_resource_service.py` - Resource management
- `test_text_processor.py` - Text processing utilities

### Phase 1: Content Ingestion (`phase1_ingestion/`)
URL ingestion, content extraction, and archiving:
- `test_async_ingestion.py` - Async ingestion pipeline
- `test_pdf_ingestion.py` - PDF processing
- `test_resource_ingestion_classification.py` - Ingestion with classification

### Phase 2: Resource Curation (`phase2_curation/`)
Manual resource management and metadata editing:
- `test_curation_service.py` - Curation business logic
- `test_curation_endpoints.py` - Curation API

### Phase 3: Search (`phase3_search/`)
Full-text search and filtering:
- `test_search_service.py` - Search logic
- `test_enhanced_search_api.py` - Search API endpoints

### Phase 4: Hybrid Search (`phase4_hybrid_search/`)
Dense + sparse embeddings, reranking, and fusion:
- `test_sparse_embedding_service.py` - Sparse embedding generation
- `test_reranking_service.py` - Result reranking
- `test_reciprocal_rank_fusion_service.py` - RRF implementation
- `test_three_way_hybrid_search_integration.py` - Full hybrid search

### Phase 5: Knowledge Graph (`phase5_graph/`)
Graph construction and recommendations:
- `test_recommendation_config.py` - Recommendation configuration
- `test_phase55_recommendations.py` - Recommendation system

### Phase 6: Citations (`phase6_citations/`)
Citation extraction and scholarly metadata:
- `test_phase6_citations.py` - Citation management
- `test_phase6_5_scholarly.py` - Scholarly metadata

### Phase 7: Collections & Annotations (`phase7_collections/`)
User collections and annotations:
- `test_annotation_export.py` - Annotation export
- `test_annotation_retrieval.py` - Annotation queries
- `test_annotation_search.py` - Annotation search
- `test_phase7_migration.py` - Schema migrations

### Phase 8: ML Classification (`phase8_classification/`)
Machine learning-based taxonomy classification:
- `test_ml_classification_service.py` - ML classification
- `test_taxonomy_service.py` - Taxonomy management
- `test_active_learning.py` - Active learning
- `test_ml_training.py` - Model training

### Phase 9: Quality Assessment (`phase9_quality/`)
Multi-dimensional quality scoring:
- `test_quality_service.py` - Quality computation
- `test_quality_dimensions.py` - Individual quality dimensions
- `test_outlier_detection.py` - Outlier detection
- `test_degradation_monitoring.py` - Quality degradation tracking
- `test_summarization_evaluator.py` - Summary quality evaluation

### Phase 10: Graph Intelligence (`phase10_graph_intelligence/`)
Advanced graph algorithms and literature-based discovery:
- `test_phase10_graph_construction.py` - Graph building
- `test_phase10_graph_embeddings.py` - Graph embeddings
- `test_phase10_neighbor_discovery.py` - Neighbor discovery
- `test_phase10_lbd_discovery.py` - Literature-based discovery

## Running Tests

### Run all tests
```bash
pytest backend/tests/
```

### Run by test type
```bash
pytest backend/tests/unit/           # Unit tests only
pytest backend/tests/integration/    # Integration tests only
pytest backend/tests/performance/    # Performance tests only
```

### Run by phase
```bash
pytest backend/tests/unit/phase1_ingestion/
pytest backend/tests/integration/phase9_quality/
```

### Run specific test file
```bash
pytest backend/tests/unit/phase8_classification/test_ml_classification_service.py
```

### Run with coverage
```bash
pytest backend/tests/ --cov=backend/app --cov-report=html
```

## Test Naming Conventions

- Test files: `test_<feature>.py`
- Test classes: `Test<Feature>` or `Test<Feature><Aspect>`
- Test functions: `test_<scenario>_<expected_outcome>`

Examples:
- `test_async_ingestion.py`
- `class TestBackgroundIngestion`
- `def test_process_ingestion_success()`

## Adding New Tests

1. Determine test type (unit/integration/performance)
2. Identify the phase
3. Create test file in appropriate directory
4. Follow existing patterns and naming conventions
5. Update this README if adding new categories

## Migration Notes

Tests were reorganized on 2025-11-13 from a flat structure to this hierarchical organization. All test files from `backend/test_*.py` were moved into the appropriate subdirectories under `backend/tests/`.
