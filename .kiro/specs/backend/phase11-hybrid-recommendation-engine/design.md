# Design Document: Phase 11 - Hybrid Recommendation Engine

## Overview

Phase 11 transforms Neo Alexandria's basic content-based recommendation system into a state-of-the-art hybrid recommendation engine. The system combines Neural Collaborative Filtering (NCF), graph-based recommendations, and content similarity with sophisticated ranking, diversity optimization, and personalized user profiles.

### Design Goals

1. **Multi-Strategy Recommendations**: Combine collaborative filtering, content-based, and graph-based approaches
2. **Personalization**: Learn user preferences from interaction history and adapt recommendations
3. **Diversity & Novelty**: Prevent filter bubbles by promoting diverse and novel content
4. **Cold Start Handling**: Provide relevant recommendations for new users with minimal data
5. **Performance**: Generate 20 recommendations in <200ms with efficient caching
6. **Continuous Improvement**: Track feedback and improve recommendation quality over time

### Success Metrics

- **Relevance**: 40%+ improvement in click-through rate (CTR) vs baseline
- **Diversity**: Gini coefficient <0.3 for recommendation sets
- **Novelty**: 20%+ recommendations from outside top-viewed resources
- **Cold Start**: Relevant recommendations within 5 user interactions
- **Performance**: <200ms latency for 20 recommendations

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  /api/recommendations  /api/interactions  /api/profile      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│              Recommendation Service (Hybrid)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Two-Stage Pipeline                                   │  │
│  │  1. Candidate Generation (Multi-Strategy)            │  │
│  │  2. Ranking & Reranking (Hybrid Scoring + MMR)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────┬──────────────┬──────────────┬────────────────────────┘
      │              │              │
      ├──────────────┐   ├──────────────┐   ├──────────────┐
      │ Collaborative│   │   Content    │   │    Graph     │
      │  Filtering   │   │    Based     │   │    Based     │
      │   (NCF)      │   │  (Embedding) │   │  (GraphSvc)  │
      └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
             │                  │                  │
┌────────────┴──────────────────┴──────────────────┴────────┐
│              User Profile Service                          │
│  - Profile Management    - Interaction Tracking            │
│  - Preference Learning   - User Embedding Generation       │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────┐
│                   Database Layer                           │
│  UserProfile  UserInteraction  RecommendationFeedback      │
│  Resource     GraphEdge        ResourceTaxonomy            │
└────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Interaction** → Track in UserInteraction table → Update UserProfile
2. **Recommendation Request** → Generate candidates from 3 strategies → Rank & diversify → Return results
3. **Feedback Loop** → Track clicks/ratings → Update NCF model → Improve future recommendations

## Components and Interfaces

### 1. Database Models

#### UserProfile Model

Stores user preferences and learned patterns:
- **Research Context**: `research_domains`, `active_domain` (JSON arrays)
- **Learned Preferences**: `preferred_taxonomy_ids`, `preferred_authors`, `preferred_sources`, `excluded_sources` (JSON arrays)
- **Settings**: `diversity_preference`, `novelty_preference`, `recency_bias` (floats 0.0-1.0)
- **Metrics**: `total_interactions`, `avg_session_duration`, `last_active_at`
- **Relationships**: One-to-one with User (to be created)

**Design Decision**: Store preferences as JSON strings for flexibility. SQLite doesn't have native JSON operators, but this allows easy serialization/deserialization.

#### UserInteraction Model

Tracks all user-resource interactions with implicit feedback signals:
- **Core Fields**: `user_id`, `resource_id`, `interaction_type`, `interaction_strength` (0.0-1.0)
- **Implicit Signals**: `dwell_time` (seconds), `scroll_depth` (0.0-1.0), `annotation_count`, `return_visits`
- **Explicit Feedback**: `rating` (1-5 stars, optional)
- **Context**: `session_id`, `interaction_timestamp`
- **Derived**: `is_positive` (strength > 0.4), `confidence` (0.0-1.0)

**Interaction Strength Computation**:
```
view: 0.1 + min(0.3, dwell_time/1000) + 0.1*scroll_depth (max 0.5)
annotation: 0.7
collection_add: 0.8
export: 0.9
rating: 0.5 (baseline, adjusted by rating value)
```

#### RecommendationFeedback Model

Tracks recommendation performance for continuous improvement:
- **Context**: `recommendation_strategy`, `recommendation_score`, `rank_position`
- **Feedback**: `was_clicked`, `was_useful`, `feedback_notes`
- **Timestamps**: `recommended_at`, `feedback_at`

### 2. User Profile Service

**Class**: `UserProfileService(db: Session)`

**Key Methods**:

- `get_or_create_profile(user_id: str) -> UserProfile`: Get existing profile or create with defaults
- `update_profile_settings(user_id, diversity_preference, novelty_preference, recency_bias, excluded_sources) -> UserProfile`: Update user preferences
- `track_interaction(user_id, resource_id, interaction_type, dwell_time, scroll_depth, session_id) -> UserInteraction`: Record interaction
- `get_user_embedding(user_id: str) -> np.ndarray`: Compute user embedding from interaction history
- `_compute_interaction_strength(interaction_type, dwell_time, scroll_depth) -> float`: Calculate strength score
- `_update_learned_preferences(user_id: str)`: Learn preferences from recent interactions (triggered every 10 interactions)

**Design Decisions**:
1. **Automatic Profile Creation**: Profiles created on first interaction to reduce friction
2. **Periodic Learning**: Update preferences every 10 interactions to balance freshness and performance
3. **Weighted Embedding**: User embedding = weighted average of interacted resource embeddings (weights = interaction_strength)
4. **Cold Start**: Return zero vector for users with no positive interactions

### 3. Neural Collaborative Filtering (NCF)

**Class**: `CollaborativeFilteringService(db: Session)`

**Architecture**: Multi-layer perceptron combining user and item embeddings

```
User ID → User Embedding (64-dim)  ┐
                                    ├→ Concatenate → MLP (128→64→32) → Score
Item ID → Item Embedding (64-dim)  ┘
```

**Training Data**: Positive interactions (is_positive=True) with interaction_strength as implicit feedback

**Key Methods**:
- `train_model(epochs=10, batch_size=256)`: Train NCF on interaction history
- `predict_score(user_id, resource_id) -> float`: Predict user-item affinity
- `get_top_recommendations(user_id, candidate_ids, limit) -> List[Dict]`: Batch score candidates

**Design Decisions**:
1. **PyTorch Implementation**: Use PyTorch for flexibility and GPU support (with CPU fallback)
2. **Implicit Feedback**: Use interaction_strength as continuous feedback signal (not binary)
3. **Negative Sampling**: Sample non-interacted items as negatives during training
4. **Model Persistence**: Save checkpoints to disk, load on service initialization
5. **Fallback Strategy**: If model unavailable/untrained, fall back to content-based recommendations

**Cold Start Handling**: For new users, skip collaborative filtering and rely on content + graph strategies

### 4. Hybrid Recommendation Service

**Class**: `HybridRecommendationService(db: Session)`

**Two-Stage Pipeline**:

#### Stage 1: Candidate Generation

Generate candidates from multiple strategies in parallel:

1. **Collaborative Filtering** (if user has ≥5 interactions):
   - Use NCF to score all resources
   - Select top 100 candidates

2. **Content-Based**:
   - Compute user embedding from interaction history
   - Find resources with cosine similarity > 0.3
   - Select top 100 candidates

3. **Graph-Based**:
   - Use existing GraphService.get_neighbors_multihop()
   - Get 2-hop neighbors with quality filtering
   - Select top 100 candidates

**Candidate Deduplication**: Merge lists, remove duplicates, preserve source strategy metadata

#### Stage 2: Ranking & Reranking

**Hybrid Scoring Formula**:
```python
hybrid_score = (
    w_collab * collaborative_score +
    w_content * content_score +
    w_graph * graph_score +
    w_quality * quality_score +
    w_recency * recency_score
)
```

**Default Weights** (user-adjustable via profile):
- `w_collab = 0.35` (collaborative filtering)
- `w_content = 0.30` (content similarity)
- `w_graph = 0.20` (graph structure)
- `w_quality = 0.10` (quality score from Phase 9)
- `w_recency = 0.05` (publication recency)

**Diversity Optimization (MMR)**:

Apply Maximal Marginal Relevance to final ranking:

```python
MMR_score = λ * relevance_score - (1-λ) * max_similarity_to_selected

where λ = user.diversity_preference (default 0.5)
```

**Algorithm**:
1. Start with empty result set
2. Select highest-scoring candidate
3. For remaining candidates, compute MMR score considering already-selected items
4. Select candidate with highest MMR score
5. Repeat until limit reached

**Novelty Boosting**:

Boost scores for novel resources:
```python
if resource.view_count < median_view_count:
    novelty_score = 1.0 - (resource.view_count / median_view_count)
    if novelty_score > user.novelty_preference:
        hybrid_score *= (1.0 + 0.2 * novelty_score)
```

**Key Methods**:
- `generate_recommendations(user_id, limit, strategy, filters) -> List[Dict]`: Main entry point
- `_generate_candidates(user_id, strategy) -> List[Dict]`: Stage 1 candidate generation
- `_rank_candidates(user_id, candidates) -> List[Dict]`: Stage 2 hybrid scoring
- `_apply_mmr(candidates, user_profile, limit) -> List[Dict]`: Diversity optimization
- `_apply_novelty_boost(candidates, user_profile) -> List[Dict]`: Novelty promotion

### 5. API Endpoints

**Router**: `app/routers/recommendations.py`

#### GET /api/recommendations

Get personalized recommendations for authenticated user.

**Query Parameters**:
- `limit` (int, default=20, max=100): Number of recommendations
- `strategy` (str, default="hybrid"): "collaborative" | "content" | "graph" | "hybrid"
- `diversity` (float, 0.0-1.0): Override user's diversity preference
- `min_quality` (float, 0.0-1.0): Minimum quality threshold

**Response**:
```json
{
  "recommendations": [
    {
      "resource_id": "uuid",
      "title": "string",
      "score": 0.85,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.9,
        "content": 0.8,
        "graph": 0.7,
        "quality": 0.85,
        "recency": 0.6
      },
      "rank": 1,
      "novelty_score": 0.3
    }
  ],
  "metadata": {
    "total": 20,
    "strategy": "hybrid",
    "diversity_applied": true,
    "gini_coefficient": 0.25
  }
}
```

#### POST /api/interactions

Track user-resource interaction.

**Request Body**:
```json
{
  "resource_id": "uuid",
  "interaction_type": "view",
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "session_id": "string"
}
```

**Response**: `201 Created` with interaction details

#### GET /api/profile

Get user profile settings.

**Response**:
```json
{
  "user_id": "string",
  "diversity_preference": 0.5,
  "novelty_preference": 0.3,
  "recency_bias": 0.5,
  "research_domains": ["AI", "ML"],
  "total_interactions": 150
}
```

#### PUT /api/profile

Update user profile settings.

**Request Body**:
```json
{
  "diversity_preference": 0.7,
  "novelty_preference": 0.5,
  "excluded_sources": ["example.com"]
}
```

## Data Models

### Database Schema

**New Tables**:

1. **user_profiles**: User preference storage
2. **user_interactions**: Interaction tracking with implicit feedback
3. **recommendation_feedback**: Recommendation performance tracking

**Note**: User model needs to be created as part of this phase. For now, we'll use `user_id` as a string identifier (email or username).

### Indexes

Critical indexes for performance:
- `idx_user_profiles_user` on `user_profiles(user_id)` (unique)
- `idx_user_interactions_user_resource` on `user_interactions(user_id, resource_id)`
- `idx_user_interactions_timestamp` on `user_interactions(interaction_timestamp)`
- `idx_recommendation_feedback_user` on `recommendation_feedback(user_id)`

### Constraints

- `ck_user_profiles_diversity_range`: diversity_preference BETWEEN 0.0 AND 1.0
- `ck_user_profiles_novelty_range`: novelty_preference BETWEEN 0.0 AND 1.0
- `ck_user_profiles_recency_range`: recency_bias BETWEEN 0.0 AND 1.0

## Error Handling

### Input Validation

1. **Preference Ranges**: Validate all preference values are in [0.0, 1.0]
2. **Interaction Types**: Validate against allowed set: ["view", "annotation", "collection_add", "export", "rating"]
3. **Resource Existence**: Check resource exists before creating interaction
4. **User Existence**: Check user exists before operations (or auto-create profile)

### Error Recovery

1. **NCF Model Unavailable**: Fall back to content + graph strategies
2. **Empty Embeddings**: Return zero vector for cold start users
3. **No Candidates**: Return popular resources as fallback
4. **Database Errors**: Roll back transactions, log errors, return 500 with message

### Logging

Log all errors with context:
```python
logger.error(f"Error in generate_recommendations for user {user_id}: {str(e)}", 
             exc_info=True, extra={"user_id": user_id, "strategy": strategy})
```

## Testing Strategy

### Unit Tests

1. **UserProfileService**:
   - Profile creation with defaults
   - Preference updates with validation
   - Interaction tracking with strength computation
   - User embedding generation (cold start, normal, weighted average)

2. **CollaborativeFilteringService**:
   - Model training (mocked)
   - Score prediction (mocked model)
   - Batch recommendation generation

3. **HybridRecommendationService**:
   - Candidate generation from each strategy
   - Hybrid scoring with different weights
   - MMR diversity optimization
   - Novelty boosting

### Integration Tests

1. **End-to-End Recommendation Flow**:
   - New user → cold start recommendations
   - User with interactions → personalized recommendations
   - Feedback loop → improved recommendations

2. **API Endpoints**:
   - GET /api/recommendations with various parameters
   - POST /api/interactions with different interaction types
   - Profile CRUD operations

### Performance Tests

1. **Latency**: Measure recommendation generation time (target <200ms)
2. **Throughput**: Concurrent recommendation requests
3. **Database Load**: Query count and execution time

### Test Data

- Mock NCF models (don't load actual weights)
- Use pytest fixtures for database setup
- Create test users with varying interaction histories
- Validate only fields present in models.py

## Performance Optimization

### Caching Strategy

1. **User Embeddings**: Cache for 5 minutes (Redis or in-memory)
2. **NCF Model**: Load once on service initialization
3. **Popular Resources**: Cache top 100 for fallback recommendations

### Database Optimization

1. **Batch Queries**: Use `.in_()` for bulk resource lookups
2. **Query Limits**: Always add `.limit()` to prevent memory issues
3. **Eager Loading**: Use `joinedload()` for relationships when needed
4. **Index Usage**: Ensure all foreign key and timestamp columns are indexed

### Computation Optimization

1. **Numpy Vectorization**: Use numpy for all vector operations
2. **Parallel Candidate Generation**: Generate candidates from strategies in parallel (future: use asyncio)
3. **Early Termination**: Stop MMR when diversity threshold reached

## Security Considerations

### Input Sanitization

1. **SQL Injection**: Use ORM exclusively, no raw SQL
2. **JSON Injection**: Validate JSON before parsing, handle JSONDecodeError
3. **XSS Prevention**: Sanitize user-provided strings (excluded_sources, feedback_notes)

### Data Privacy

1. **User Isolation**: Ensure users can only access their own profiles and interactions
2. **Sensitive Data**: Don't log user_id in public logs
3. **GDPR Compliance**: Support profile deletion (cascade delete interactions)

### Rate Limiting

1. **Recommendation Requests**: Limit to 100/hour per user
2. **Interaction Tracking**: Limit to 1000/hour per user
3. **Profile Updates**: Limit to 10/hour per user

## Deployment Considerations

### Database Migration

1. Create Alembic migration for new tables
2. Test migration on copy of production database
3. Plan rollback strategy (downgrade script)
4. Monitor migration performance (expect <1 minute for empty tables)

### Model Deployment

1. **Initial Model**: Train NCF on existing data (if available)
2. **Model Updates**: Retrain weekly, deploy new checkpoint
3. **A/B Testing**: Compare old vs new model performance
4. **Rollback**: Keep previous model checkpoint for quick rollback

### Monitoring

1. **Recommendation Quality**: Track CTR, diversity, novelty metrics
2. **Performance**: Monitor latency, error rates, cache hit rates
3. **User Engagement**: Track interaction counts, session duration
4. **Model Health**: Monitor NCF prediction distribution, training loss

## Future Enhancements

### Phase 11.5: Advanced Features

1. **Context-Aware Recommendations**: Consider time of day, device, location
2. **Multi-Armed Bandits**: Explore-exploit tradeoff for recommendation strategies
3. **Deep Learning Embeddings**: Use transformer-based user/item embeddings
4. **Real-Time Updates**: Update recommendations as user interacts
5. **Explanation Generation**: Provide reasons for each recommendation

### Phase 12: Social Features

1. **Collaborative Filtering 2.0**: User-user similarity for social recommendations
2. **Expert Recommendations**: Identify and weight expert users
3. **Trending Topics**: Surface emerging research areas
4. **Recommendation Sharing**: Allow users to share recommendation lists

## References

### Academic Papers

1. He et al. (2017): "Neural Collaborative Filtering" - NCF architecture
2. Carbonell & Goldstein (1998): "Maximal Marginal Relevance" - Diversity optimization
3. Koren et al. (2009): "Matrix Factorization Techniques" - Collaborative filtering foundations

### Implementation Guides

1. PyTorch NCF Tutorial: https://pytorch.org/tutorials/beginner/basics/intro.html
2. Scikit-learn Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
3. FastAPI Best Practices: https://fastapi.tiangolo.com/tutorial/

## Appendix: Configuration

### Settings (app/config/settings.py)

```python
# Recommendation settings
RECOMMENDATION_DEFAULT_LIMIT = 20
RECOMMENDATION_MAX_LIMIT = 100
RECOMMENDATION_CACHE_TTL = 300  # 5 minutes

# NCF settings
NCF_EMBEDDING_DIM = 64
NCF_HIDDEN_LAYERS = [128, 64, 32]
NCF_LEARNING_RATE = 0.001
NCF_BATCH_SIZE = 256
NCF_EPOCHS = 10

# Hybrid weights
HYBRID_WEIGHT_COLLABORATIVE = 0.35
HYBRID_WEIGHT_CONTENT = 0.30
HYBRID_WEIGHT_GRAPH = 0.20
HYBRID_WEIGHT_QUALITY = 0.10
HYBRID_WEIGHT_RECENCY = 0.05

# Diversity settings
MMR_DEFAULT_LAMBDA = 0.5
NOVELTY_BOOST_FACTOR = 0.2

# Cold start threshold
COLD_START_INTERACTION_THRESHOLD = 5
```

---

**Design Version**: 1.0  
**Last Updated**: 2025-11-15  
**Status**: Ready for Implementation
