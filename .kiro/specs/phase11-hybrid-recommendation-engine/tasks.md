# Implementation Plan: Phase 11 - Hybrid Recommendation Engine

## Task Overview

This implementation plan breaks down Phase 11 into discrete, manageable coding tasks. Each task builds incrementally on previous work and includes specific requirements references. The plan follows implementation-first development with optional testing tasks marked with `*`.

## Tasks

- [x] 1. Create database models for user profiles and interactions





  - Add UserProfile, UserInteraction, and RecommendationFeedback models to `app/database/models.py`
  - Add User model with basic fields (id, email, username, created_at)
  - Add relationship mappings between User, UserProfile, and interactions
  - Follow existing model patterns (GUID primary keys, timestamps, relationships)
  - Ensure all JSON fields use Text type with JSON serialization
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 9.1, 12.1_

- [x] 2. Create and test database migration





  - Generate Alembic migration for new tables: `alembic revision -m "add_user_profiles_interactions_phase11"`
  - Write upgrade() function creating user_profiles, user_interactions, recommendation_feedback tables
  - Add indexes: idx_user_profiles_user, idx_user_interactions_user_resource, idx_user_interactions_timestamp
  - Add check constraints for preference ranges (0.0-1.0)
  - Write downgrade() function for rollback
  - Test migration: `alembic upgrade head` and `alembic downgrade -1`
  - _Requirements: 1.5, 2.1, 10.4, 12.7_
-

- [x] 3. Implement User Profile Service



- [x] 3.1 Create UserProfileService class with profile management


  - Create `app/services/user_profile_service.py` with UserProfileService class
  - Implement `get_or_create_profile(user_id)` with default preferences (diversity=0.5, novelty=0.3, recency=0.5)
  - Implement `update_profile_settings()` with input validation for preference ranges
  - Add error handling with try/except and database rollback
  - Add logging for all operations
  - _Requirements: 1.1, 1.2, 1.5, 12.1, 12.7_


- [x] 3.2 Implement interaction tracking

  - Implement `track_interaction()` method to record user-resource interactions
  - Implement `_compute_interaction_strength()` for different interaction types (view, annotation, collection_add, export)
  - Handle duplicate interactions by updating return_visits and max interaction_strength
  - Update UserProfile.total_interactions and last_active_at on each interaction
  - Validate interaction_type against allowed values
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 12.2_


- [x] 3.3 Implement user embedding generation

  - Implement `get_user_embedding(user_id)` to compute weighted average of resource embeddings
  - Query positive interactions (is_positive=True) limited to 100 most recent
  - Handle cold start by returning zero vector (768-dim) when no interactions exist
  - Validate embedding dimensions and handle JSON parsing errors
  - Use interaction_strength as weights for averaging
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


- [x] 3.4 Implement preference learning

  - Implement `_update_learned_preferences(user_id)` to analyze interaction history
  - Query positive interactions from last 90 days, limited to 1000 records
  - Extract and count preferred authors from resource.authors JSON field
  - Update UserProfile with top 10 preferred authors as JSON array
  - Trigger learning every 10 interactions (check total_interactions % 10 == 0)
  - _Requirements: 1.3, 1.4, 12.4_

- [x] 3.5 Write unit tests for UserProfileService


  - Create `tests/unit/phase11_recommendations/test_user_profile_service.py`
  - Test profile creation with defaults
  - Test preference updates with valid and invalid ranges
  - Test interaction tracking for all interaction types
  - Test user embedding generation (cold start, single interaction, multiple interactions)
  - Test preference learning with mock interaction data
  - Use fixtures as function parameters, mock database queries
  - _Requirements: 13.1, 13.6, 13.7_
-

- [x] 4. Implement Neural Collaborative Filtering (NCF)



- [x] 4.1 Create NCF model architecture


  - Create `app/services/collaborative_filtering_service.py` with CollaborativeFilteringService class
  - Define NCF PyTorch model: user embedding (64-dim) + item embedding (64-dim) → MLP (128→64→32→1)
  - Implement forward pass with concatenation and ReLU activations
  - Add CUDA availability check with CPU fallback
  - Add model checkpoint save/load with error handling
  - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [x] 4.2 Implement NCF training

  - Implement `train_model(epochs, batch_size)` method
  - Query positive interactions (is_positive=True) as training data
  - Implement negative sampling: sample non-interacted items as negatives
  - Use interaction_strength as continuous feedback signal (not binary)
  - Implement training loop with Adam optimizer and BCELoss
  - Save model checkpoint after training
  - _Requirements: 4.2, 4.3_

- [x] 4.3 Implement NCF prediction

  - Implement `predict_score(user_id, resource_id)` for single prediction
  - Implement `get_top_recommendations(user_id, candidate_ids, limit)` for batch scoring
  - Handle model not trained/unavailable by returning None
  - Convert PyTorch tensors to Python floats for JSON serialization
  - Add error handling for invalid user/resource IDs
  - _Requirements: 4.3, 4.6_

- [x] 4.4 Write unit tests for NCF service






  - Create `tests/unit/phase11_recommendations/test_collaborative_filtering.py`
  - Mock PyTorch model to avoid loading actual weights
  - Test model initialization (CUDA vs CPU)
  - Test training with mock interaction data
  - Test prediction with mocked model output
  - Test batch recommendation generation
  - _Requirements: 13.2, 13.5, 13.6_

-

- [x] 5. Implement Hybrid Recommendation Service


- [x] 5.1 Create candidate generation stage


  - Create `app/services/hybrid_recommendation_service.py` with HybridRecommendationService class
  - Implement `_generate_candidates(user_id, strategy)` method
  - Generate collaborative candidates: use NCF to score resources, select top 100
  - Generate content candidates: compute user embedding, find similar resources (cosine > 0.3), select top 100
  - Generate graph candidates: use GraphService.get_neighbors_multihop(hops=2), select top 100
  - Merge and deduplicate candidates while preserving source strategy metadata
  - _Requirements: 5.1, 5.2, 5.3, 5.6_

- [x] 5.2 Implement hybrid scoring and ranking


  - Implement `_rank_candidates(user_id, candidates)` method
  - Compute hybrid score: w_collab*collab + w_content*content + w_graph*graph + w_quality*quality + w_recency*recency
  - Use default weights: collab=0.35, content=0.30, graph=0.20, quality=0.10, recency=0.05
  - Allow user-specific weight overrides from UserProfile
  - Handle missing scores gracefully (default to 0.0)
  - Sort candidates by hybrid score descending
  - _Requirements: 5.4, 5.5, 5.7_

- [x] 5.3 Implement diversity optimization (MMR)


  - Implement `_apply_mmr(candidates, user_profile, limit)` method
  - Use Maximal Marginal Relevance algorithm: MMR = λ*relevance - (1-λ)*max_similarity
  - Use user.diversity_preference as λ parameter (default 0.5)
  - Iteratively select candidates maximizing MMR score
  - Handle empty candidate lists gracefully
  - Validate similarity scores are finite numbers
  - _Requirements: 6.1, 6.2, 6.3, 6.6, 6.7_

- [x] 5.4 Implement novelty promotion


  - Implement `_apply_novelty_boost(candidates, user_profile)` method
  - Compute novelty score: 1.0 - (view_count / median_view_count)
  - Boost scores for resources with novelty_score > user.novelty_preference
  - Apply boost: hybrid_score *= (1.0 + 0.2 * novelty_score)
  - Ensure at least 20% of recommendations are from outside top-viewed resources
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.5 Implement main recommendation generation


  - Implement `generate_recommendations(user_id, limit, strategy, filters)` main entry point
  - Check if user has ≥5 interactions for collaborative filtering eligibility
  - Call candidate generation → ranking → MMR → novelty boost pipeline
  - Apply quality filtering (exclude is_quality_outlier, apply min_quality threshold)
  - Handle cold start users (use content + graph only)
  - Return recommendations with scores breakdown and metadata
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.1, 8.2, 8.3, 8.4, 9.5_

- [x] 5.6 Write unit tests for hybrid recommendation service


  - Create `tests/unit/phase11_recommendations/test_hybrid_recommendations.py`
  - Test candidate generation from each strategy
  - Test hybrid scoring with different weight combinations
  - Test MMR diversity optimization
  - Test novelty boosting
  - Test cold start handling
  - Mock NCF service, GraphService, and database queries
  - _Requirements: 13.3, 13.4, 13.5, 13.6, 13.7_


- [x] 6. Create API endpoints















- [x] 6.1 Implement GET /api/recommendations endpoint


  - Create `app/routers/recommendations.py` with FastAPI router
  - Implement GET /api/recommendations with query params: limit, strategy, diversity, min_quality
  - Validate limit (default=20, max=100), strategy (collaborative|content|graph|hybrid)
  - Call HybridRecommendationService.generate_recommendations()
  - Convert all UUID objects to strings with str()
  - Return recommendations with scores breakdown and metadata (total, strategy, diversity_applied, gini_coefficient)
  - _Requirements: 11.1, 11.2, 11.6, 11.8_



- [x] 6.2 Implement POST /api/interactions endpoint

  - Implement POST /api/interactions with request body: resource_id, interaction_type, dwell_time, scroll_depth, session_id
  - Validate request body using Pydantic schema
  - Call UserProfileService.track_interaction()
  - Return 201 Created with interaction details
  - Wrap service call in try/except, return appropriate HTTP error codes
  - _Requirements: 11.3, 11.7, 11.8_




- [x] 6.3 Implement profile management endpoints
  - Implement GET /api/profile to retrieve user profile settings
  - Implement PUT /api/profile to update preferences (diversity, novelty, recency, excluded_sources)
  - Validate preference ranges (0.0-1.0) using Pydantic schema
  - Call UserProfileService methods
  - Return profile data with all settings
  - _Requirements: 11.4, 11.5, 11.7, 11.8_





- [x] 6.4 Implement recommendation feedback endpoint
  - Implement POST /api/recommendations/feedback with request body: resource_id, was_clicked, was_useful, feedback_notes
  - Create RecommendationFeedback record with recommendation context
  - Update feedback_at timestamp when user provides feedback
  - Use for computing CTR and strategy performance metrics
  - _Requirements: 9.1, 9.2, 9.3, 9.4_



- [x] 6.5 Write integration tests for API endpoints







  - Create `tests/integration/phase11_recommendations/test_recommendation_api.py`
  - Test GET /api/recommendations with various parameters
  - Test POST /api/interactions with different interaction types
  - Test profile CRUD operations
  - Test recommendation feedback submission
  - Use test database with fixtures

  - _Requirements: 13.4, 13.8_


- [x] 7. Implement performance optimizations



- [x] 7.1 Add caching for user embeddings


  - Implement in-memory cache (dict) for user embeddings with 5-minute TTL
  - Add cache key: f"user_embedding:{user_id}"
  - Check cache before computing embedding
  - Store computed embedding in cache with timestamp
  - Clear expired entries periodically
  - _Requirements: 10.1_

- [x] 7.2 Optimize database queries


  - Add `.limit()` to all queries to prevent memory issues
  - Use `.in_()` for batch resource lookups instead of loops
  - Add indexes verification: user_id, resource_id, interaction_timestamp
  - Use query.count() instead of len(query.all()) for counting
  - _Requirements: 10.2, 10.4_

- [x] 7.3 Add performance monitoring


  - Add timing decorators to key methods (generate_recommendations, track_interaction)
  - Log slow queries (>100ms)
  - Track recommendation generation time (target <200ms)
  - Add metrics: cache hit rate, candidate counts, scoring time
  - _Requirements: 10.1, 10.5_

- [x] 8. Add quality and diversity metrics





- [x] 8.1 Implement Gini coefficient calculation

  - Create `app/utils/recommendation_metrics.py` with metrics functions
  - Implement `compute_gini_coefficient(scores)` to measure diversity
  - Use in recommendation response metadata
  - Target: Gini coefficient <0.3 for diverse recommendations
  - _Requirements: 6.4, 9.5_


- [x] 8.2 Implement CTR tracking

  - Implement `compute_ctr(user_id, time_window_days)` to calculate click-through rate
  - Query RecommendationFeedback for was_clicked=True vs total recommendations
  - Track CTR by strategy (collaborative, content, graph, hybrid)
  - Target: 40% improvement over baseline
  - _Requirements: 9.4, 9.5_



- [x] 8.3 Implement novelty metrics

  - Implement `compute_novelty_score(recommendations)` to measure discovery
  - Calculate percentage of recommendations from outside top-viewed resources
  - Target: 20%+ novel recommendations
  - _Requirements: 7.3, 9.5_
- [x] 9. Update documentation







- [x] 9. Update documentation

- [x] 9.1 Update API documentation


  - Update `backend/docs/API_DOCUMENTATION.md` with new endpoints
  - Document request/response schemas for all endpoints
  - Add example requests and responses
  - Document query parameters and validation rules
  - _Requirements: 14.1_

- [x] 9.2 Update developer guide


  - Update `backend/docs/DEVELOPER_GUIDE.md` with Phase 11 architecture
  - Document NCF model training and deployment process
  - Explain hybrid scoring formula and weights
  - Document MMR diversity optimization algorithm
  - _Requirements: 14.2, 14.3, 14.5_

- [x] 9.3 Update changelog


  - Add Phase 11 entry to `backend/docs/CHANGELOG.md`
  - List all new features: hybrid recommendations, user profiles, NCF, diversity optimization
  - Document breaking changes (if any)
  - Note performance improvements and metrics
  - _Requirements: 14.4_

- [x] 10. Deploy and monitor





- [x] 10.1 Run database migration in production


  - Backup production database before migration
  - Run `alembic upgrade head` on production
  - Verify tables created: user_profiles, user_interactions, recommendation_feedback
  - Monitor migration time (expect <1 minute)
  - Test rollback plan: `alembic downgrade -1`
  - _Requirements: 10.4_


- [x] 10.2 Train initial NCF model

  - Query existing interaction data (if available)
  - Train NCF model with default hyperparameters
  - Save model checkpoint to disk
  - Validate model predictions on test set
  - Deploy model checkpoint to production
  - _Requirements: 4.2, 4.5_


- [x] 10.3 Set up monitoring dashboards

  - Track recommendation quality metrics: CTR, diversity, novelty
  - Monitor performance: latency, error rates, cache hit rates
  - Track user engagement: interaction counts, session duration
  - Monitor NCF model health: prediction distribution, training loss
  - Set up alerts for degraded performance
  - _Requirements: 9.5, 10.1, 10.5_

## Implementation Notes

### Dependencies

Ensure these packages are installed:
```bash
pip install torch numpy scikit-learn
```

### Testing Guidelines

- Use pytest fixtures as function parameters (never call directly)
- Mock all ML models to avoid loading actual weights
- Use only valid Resource fields from models.py
- Convert UUIDs to strings in assertions
- Limit verification attempts to 2 tries maximum

### Safety Checklist

Before committing each task:
- [ ] All database queries use ORM (no raw SQL)
- [ ] All inputs validated before use
- [ ] All ranges checked (0.0-1.0 for preferences)
- [ ] All queries have limits (prevent memory issues)
- [ ] All errors logged and handled
- [ ] All transactions rolled back on error
- [ ] All JSON parsing wrapped in try/except
- [ ] All array dimensions validated
- [ ] All UUID objects converted to strings in JSON responses

### Performance Targets

- Recommendation generation: <200ms for 20 recommendations
- Database queries: <50ms per query
- User embedding computation: <10ms
- NCF prediction: <5ms per resource
- Cache hit rate: >80% for user embeddings

---

**Implementation Plan Version**: 1.0  
**Total Tasks**: 10 major tasks, 30 subtasks  
**Estimated Effort**: 3-4 weeks  
**Status**: Ready for Execution
