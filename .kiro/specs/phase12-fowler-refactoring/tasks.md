# Implementation Plan

- [x] 1. Create domain objects foundation








  - Create `backend/app/domain/` directory structure with `__init__.py`
  - Define base domain object classes with validation patterns
  - Implement serialization methods (to_dict, from_dict) for all domain objects
  - _Requirements: 3.1, 3.2, 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 2. Implement classification domain objects





  - Create `ClassificationPrediction` value object with confidence validation
  - Create `ClassificationResult` with prediction collection and metadata
  - Add methods for filtering high/low confidence predictions
  - Implement `to_dict()` for API compatibility
  - _Requirements: 3.1, 3.2, 3.3, 11.1, 11.2, 11.3_

- [x] 3. Implement search domain objects








  - Create `SearchQuery` value object with query text and configuration
  - Create `SearchResult` with ranking and metadata
  - Add query analysis methods (is_short_query, is_long_query)
  - _Requirements: 3.1, 3.2, 11.1, 11.2, 11.3_

- [x] 4. Implement quality domain objects


  - Create `QualityScore` with five dimensions (accuracy, completeness, consistency, timeliness, relevance)
  - Add dimension validation (0.0-1.0 range) in `__post_init__`
  - Implement `overall_score()` method with weighted calculation
  - Add `is_high_quality()` threshold method
  - _Requirements: 3.1, 3.2, 3.3, 11.1, 11.2, 11.3_


- [x] 5. Implement recommendation domain objects


  - Create `Recommendation` value object with resource_id and score
  - Create `RecommendationScore` with confidence and ranking
  - Add comparison methods for sorting recommendations
  - _Requirements: 3.1, 3.2, 11.1, 11.2, 11.3_


- [x] 6. Refactor ml_classification_service.py - Extract Function



  - Extract `_compute_metrics` helper methods from long functions
  - Break down `fine_tune()` into smaller methods (<30 lines each)
  - Extract `_load_model()` sub-methods for each loading step
  - Extract `_semi_supervised_iteration()` helper methods
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.2_
- [x] 7. Refactor ml_classification_service.py - Replace Primitive with Object




- [x] 7. Refactor ml_classification_service.py - Replace Primitive with Object

  - Replace dict return type in `predict()` with `ClassificationResult`
  - Update all call sites to use domain objects
  - Add backward compatibility layer with `to_dict()` method
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.2_

- [x] 8. Refactor ml_classification_service.py - Separate Query from Modifier





  - Split `predict()` into pure prediction and monitoring/logging
  - Create separate `_log_prediction()` modifier method
  - Ensure `predict()` has no side effects except logging
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.2_
-

- [x] 9. Refactor ml_classification_service.py - Add type hints and documentation




  - Add type hints to all public methods (100% coverage)
  - Add docstrings to all extracted functions
  - Replace magic numbers with named constants
  - _Requirements: 8.4, 10.1, 10.2, 10.3_

- [x] 9.1 Validate ml_classification_service.py refactoring


  - Run existing test suite for ml_classification_service
  - Verify all tests pass with refactored code
  - Check type hints with mypy
  - Verify test coverage maintained ≥85%
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_


- [x] 10. Refactor quality_service.py - Extract Function




  - Extract `_compute_accuracy_dimension()` from `compute_quality()`
  - Extract `_compute_completeness_dimension()` method
  - Extract `_compute_consistency_dimension()` method
  - Extract `_compute_timeliness_dimension()` method
  - Extract `_compute_relevance_dimension()` method
  - Extract helper methods for each dimension's sub-calculations
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.2_

- [x] 11. Refactor quality_service.py - Replace Primitive with Object





  - Replace dict return in `compute_quality()` with `QualityScore` object
  - Update all call sites to use `QualityScore`
  - Add `to_dict()` for API compatibility
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.2_
-

- [x] 12. Refactor quality_service.py - Replace Magic Numbers




  - Extract all weight constants to module-level constants
  - Create `QUALITY_WEIGHTS` configuration object
  - Document weight rationale in constants
  - _Requirements: 10.2, 10.3_

- [x] 12.1 Validate quality_service.py refactoring


  - Run existing test suite for quality_service
  - Verify all tests pass
  - Check type hints coverage
  - Verify test coverage maintained

  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_

- [x] 13. Refactor search_service.py - Combine Functions into Class




  - Create `HybridSearchQuery` class encapsulating search pipeline
  - Move search methods into class as private methods
  - Add `execute()` method for pipeline execution
  - Add `get_diagnostic_info()` for debugging
  - _Requirements: 2.1, 2.2, 8.2_

- [x] 14. Refactor search_service.py - Replace Primitive with Object





  - Replace query parameters with `SearchQuery` object
  - Update search methods to accept `SearchQuery`
  - Add query analysis methods to `SearchQuery`
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


- [x] 15. Refactor search_service.py - Split Phase




  - Separate candidate retrieval phase from fusion phase
  - Create intermediate data structure for candidates
  - Separate fusion from reranking phase
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 15.1 Validate search_service.py refactoring


  - Run existing test suite for search_service
  - Verify all tests pass
  - Check performance benchmarks maintained
  - Verify test coverage maintained
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_

-

- [x] 16. Implement recommendation strategy pattern



  - Create `RecommendationStrategy` abstract base class
  - Implement `CollaborativeFilteringStrategy` concrete class
  - Implement `ContentBasedStrategy` concrete class
  - Implement `GraphBasedStrategy` concrete class
  - Implement `HybridStrategy` with weighted fusion
  - Create `RecommendationStrategyFactory` for strategy creation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 17. Refactor recommendation_service.py - Replace Conditional with Polymorphism





  - Replace conditional logic with strategy pattern
  - Update `generate_recommendations()` to use factory
  - Remove all repeated switch statements
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.2_



- [ ] 17.1 Validate recommendation_service.py refactoring
  - Run existing test suite for recommendation_service
  - Verify all tests pass
  - Verify strategy pattern works correctly
  - Verify test coverage maintained
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_

- [x] 18. Refactor graph_service.py - Extract Function





  - Extract graph traversal helper methods
  - Break down complex traversal algorithms into steps
  - Extract neighbor scoring methods
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.2_

- [x] 19. Refactor graph_service.py - Encapsulate Collection





  - Encapsulate node collections with add/remove methods
  - Make collections private with accessor methods
  - Add validation in collection modification methods
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 19.1 Validate graph_service.py refactoring


  - Run existing test suite for graph_service
  - Verify all tests pass
  - Verify test coverage maintained
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_
-

- [x] 20. Refactor taxonomy_service.py - Extract Function



  - Extract taxonomy hierarchy traversal methods
  - Break down classification logic into smaller functions
  - Extract validation methods
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.2_

- [ ] 20.1 Validate taxonomy_service.py refactoring
  - Run existing test suite for taxonomy_service
  - Verify all tests pass
  - Verify test coverage maintained
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_

-

- [x] 21. Refactor resource_service.py - Separate Query from Modifier



  - Split CRUD operations into query and modifier methods
  - Ensure query methods have no side effects
  - Ensure modifier methods return None
  - Add logging to all modifier methods
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.2_

- [x] 21.1 Validate resource_service.py refactoring


  - Run existing test suite for resource_service
  - Verify all tests pass
  - Verify test coverage maintained
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 8.5_


- [x] 22. Refactor remaining 25 service modules



  - Apply established patterns to each remaining service
  - Extract long functions (<30 lines)
  - Replace primitives with domain objects where applicable
  - Add type hints and documentation
  - Validate each service after refactoring
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
- [x] 23. Create refactoring validation framework








- [ ] 23. Create refactoring validation framework

  - Implement automated code smell detection
  - Create function length checker
  - Create class size checker
  - Implement type hint coverage checker
  - Create code duplication detector
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.2, 8.3_

-





- [-] 24. Run comprehensive validation suite



  - Run all tests across all refactored services
  - Verify 100% tests passing
  - Check type hint coverage (100% on public methods)
  - Verify test coverage ≥85%
  - Run code smell detection on all services
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 8.4, 8.5_


-



- [x] 25. Generate refactoring documentation



  - Document all Fowler techniques applied per service
  - Create before/after code examples for major refactorings
  - List all code smells eliminated
  - Generate metrics report (before/after comparison)
  - Create pattern guide for future development
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
