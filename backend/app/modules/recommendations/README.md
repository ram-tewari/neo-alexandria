# Recommendations Module

## Purpose

The Recommendations module provides intelligent, personalized resource recommendations using a hybrid approach that combines multiple recommendation strategies:

- **Content-Based Filtering**: Recommends resources similar to those the user has interacted with
- **Collaborative Filtering**: Recommends resources based on similar users' preferences
- **Neural Collaborative Filtering (NCF)**: Deep learning-based recommendations
- **Hybrid Strategies**: Combines multiple approaches with configurable weights

## Architecture

### Components

```
recommendations/
├── __init__.py           # Public interface
├── router.py             # API endpoints
├── service.py            # Main recommendation orchestration
├── strategies.py         # Recommendation strategy implementations
├── hybrid_service.py     # Hybrid recommendation engine
├── collaborative.py      # Collaborative filtering
├── ncf.py                # Neural collaborative filtering
├── user_profile.py       # User profile management
├── schema.py             # Pydantic schemas
├── model.py              # Database models
├── handlers.py           # Event handlers
└── README.md             # This file
```

### Database Models

- **UserProfile**: Stores user preferences, interests, and profile data
- **UserInteraction**: Records user interactions with resources (views, annotations, collections)
- **RecommendationFeedback**: Captures user feedback on recommendations

### Dependencies

**Shared Kernel**:
- `shared.embeddings`: For content-based similarity
- `shared.database`: For database access
- `shared.event_bus`: For event-driven communication

**No Direct Module Dependencies**: Communicates with other modules via events only

## Public Interface

### Router

```python
from app.modules.recommendations import recommendations_router

# Endpoints:
# GET /recommendations/personalized - Get personalized recommendations
# POST /recommendations/interactions - Record user interaction
# POST /recommendations/feedback - Submit recommendation feedback
# GET /recommendations/profile/{user_id} - Get user profile
# PUT /recommendations/profile/{user_id} - Update user profile
# GET /recommendations/similar/{resource_id} - Get similar resources
```

### Services

```python
from app.modules.recommendations import RecommendationService, UserProfileService

# Generate recommendations
recommendations = await recommendation_service.get_recommendations(
    user_id=user_id,
    strategy="hybrid",
    limit=10
)

# Update user profile
await user_profile_service.update_from_interaction(
    user_id=user_id,
    resource_id=resource_id,
    interaction_type="view"
)
```

## Event-Driven Communication

### Events Subscribed

| Event | Handler | Purpose |
|-------|---------|---------|
| `annotation.created` | `handle_annotation_created` | Update user profile based on annotation activity |
| `collection.resource_added` | `handle_collection_resource_added` | Update user profile based on collection activity |

### Events Emitted

| Event | Payload | When |
|-------|---------|------|
| `recommendation.generated` | `{user_id, resource_ids, strategy, timestamp}` | When recommendations are generated |
| `user.profile_updated` | `{user_id, profile_data, timestamp}` | When user profile is updated |
| `interaction.recorded` | `{user_id, resource_id, interaction_type, timestamp}` | When user interaction is recorded |

## Recommendation Strategies

### Content-Based

Recommends resources similar to those the user has interacted with, using:
- Embedding similarity
- Tag overlap
- Classification similarity

### Collaborative Filtering

Recommends resources based on similar users' preferences:
- User-based collaborative filtering
- Item-based collaborative filtering
- Matrix factorization

### Neural Collaborative Filtering (NCF)

Deep learning approach using:
- User and item embeddings
- Multi-layer perceptron
- Trained on interaction history

### Hybrid

Combines multiple strategies with configurable weights:
```python
hybrid_score = (
    w1 * content_based_score +
    w2 * collaborative_score +
    w3 * ncf_score
)
```

## Usage Examples

### Get Personalized Recommendations

```python
GET /recommendations/personalized?user_id=123&limit=10&strategy=hybrid

Response:
{
  "recommendations": [
    {
      "resource_id": 456,
      "score": 0.95,
      "reason": "Similar to resources you've annotated",
      "strategy": "content_based"
    },
    ...
  ],
  "strategy": "hybrid",
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### Record User Interaction

```python
POST /recommendations/interactions
{
  "user_id": 123,
  "resource_id": 456,
  "interaction_type": "view",
  "duration_seconds": 120
}

Response:
{
  "interaction_id": 789,
  "profile_updated": true
}
```

### Submit Feedback

```python
POST /recommendations/feedback
{
  "user_id": 123,
  "resource_id": 456,
  "feedback_type": "helpful",
  "rating": 5
}

Response:
{
  "feedback_id": 101,
  "model_updated": true
}
```

## Testing

### Unit Tests

```bash
pytest backend/app/modules/recommendations/tests/test_service.py
pytest backend/app/modules/recommendations/tests/test_strategies.py
pytest backend/app/modules/recommendations/tests/test_user_profile.py
```

### Integration Tests

```bash
pytest backend/app/modules/recommendations/tests/test_router.py
pytest backend/app/modules/recommendations/tests/test_handlers.py
```

## Configuration

Environment variables:
```bash
# Recommendation weights
RECOMMENDATION_CONTENT_WEIGHT=0.4
RECOMMENDATION_COLLABORATIVE_WEIGHT=0.3
RECOMMENDATION_NCF_WEIGHT=0.3

# NCF model
NCF_MODEL_PATH=models/ncf_model.pt
NCF_EMBEDDING_DIM=64

# Caching
RECOMMENDATION_CACHE_TTL=3600
```

## Performance Considerations

- **Caching**: Recommendations are cached per user with configurable TTL
- **Batch Processing**: User profile updates are batched for efficiency
- **Async Operations**: All database operations are async
- **Model Loading**: NCF model is loaded once at startup

## Future Enhancements

- Real-time recommendation updates
- A/B testing framework for strategies
- Explainable recommendations
- Multi-armed bandit for strategy selection
- Contextual recommendations (time, location, device)

## Related Modules

- **Resources**: Source of recommendable items
- **Collections**: User collection activity informs preferences
- **Annotations**: User annotation activity informs preferences
- **Quality**: Quality scores influence recommendation ranking
- **Graph**: Citation network can inform recommendations

## Version History

- **1.0.0** (Phase 14): Initial extraction from layered architecture
