# Recommendations Module

## Features

- **Content-Based Filtering**: Recommends resources similar to those the user has interacted with
- **Collaborative Filtering**: Recommends resources based on similar users' preferences
- **Neural Collaborative Filtering (NCF)**: Deep learning-based recommendations
- **Hybrid Strategies**: Combines multiple approaches with configurable weights
- **User Profile Tracking** (Task 14 - Phase 16.7): Comprehensive interaction tracking and preference learning
- **Temporal Weighting**: Recent interactions weighted more heavily (30-day half-life)
- **Cold Start Handling**: Graceful handling of new users with no interaction history

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
  - `interest_vector`: Learned embedding from interaction history
  - `topics`: Frequent topics from interacted resources
  - `tags`: Frequent tags from user annotations
  - `interaction_counts`: Counts by interaction type
  - `settings`: Diversity, novelty, and recency preferences (0.0-1.0)
  - `total_interactions`: Total number of tracked interactions
  - `last_active_at`: Timestamp of last interaction
  
- **UserInteraction**: Records user interactions with resources (views, annotations, collections)
  - `interaction_type`: view, annotation, collection_add, export, rating
  - `interaction_strength`: 0.0-1.0 based on engagement signals
  - `dwell_time_seconds`: Time spent viewing (for view interactions)
  - `scroll_depth`: Percentage scrolled (for view interactions)
  - `return_visits`: Number of times user returned to same resource
  - `created_at`: Timestamp for temporal weighting
  
- **RecommendationFeedback**: Captures user feedback on recommendations
  - `feedback_type`: helpful, not_helpful, irrelevant
  - `rating`: 1-5 star rating (optional)
  - Used for active learning and model improvement

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

## User Profile Tracking (Task 14 - Phase 16.7)

### Interaction Types and Strengths

The system tracks various user interactions with implicit feedback signals:

| Interaction Type | Strength | Signals Used |
|-----------------|----------|--------------|
| **View** | 0.1-0.5 | Dwell time (>30s), scroll depth (>50%) |
| **Annotation** | 0.7 | Creating highlights or notes |
| **Collection Add** | 0.8 | Adding resource to collection |
| **Export** | 0.9 | Exporting annotations (high intent) |
| **Rating** | 0.2-1.0 | Explicit 1-5 star rating |

### Temporal Weighting

Recent interactions are weighted more heavily using exponential decay:

```python
weight = 0.5 ^ (age_days / 30)
```

- **Recent interactions** (0-7 days): weight ≈ 0.87-1.0
- **Medium age** (30 days): weight = 0.5
- **Old interactions** (90 days): weight ≈ 0.125

### Profile Computation

User profiles are automatically computed from interaction history:

1. **Interest Vector**: Mean of resource embeddings, weighted by interaction strength and recency
2. **Frequent Topics**: Top topics from interacted resources
3. **Frequent Tags**: Top tags from user annotations
4. **Interaction Counts**: Breakdown by interaction type

Profiles are recomputed every 10 interactions for efficiency.

### Cold Start Handling

For new users with no interaction history:
- Interest vector: Zero vector (512 dimensions)
- Topics: Empty list
- Tags: Empty list
- Recommendations: Fall back to popularity-based or content-based only

### Caching Strategy

- **Embedding cache**: In-memory cache with 5-minute TTL
- **Cache invalidation**: On profile updates
- **Performance**: <10ms for cached embeddings, <50ms for cache miss

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

### Track User Interactions

```python
from app.modules.recommendations import UserProfileService

profile_service = UserProfileService(db)

# Track view interaction with engagement signals
await profile_service.track_interaction(
    user_id="user-123",
    resource_id="resource-456",
    interaction_type="view",
    dwell_time_seconds=120,  # 2 minutes
    scroll_depth=0.75  # Scrolled 75%
)
# Strength calculated: 0.1 + (120/300)*0.2 + 0.75*0.2 = 0.33

# Track annotation creation
await profile_service.track_interaction(
    user_id="user-123",
    resource_id="resource-456",
    interaction_type="annotation"
)
# Strength: 0.7 (fixed)

# Track collection add
await profile_service.track_interaction(
    user_id="user-123",
    resource_id="resource-456",
    interaction_type="collection_add"
)
# Strength: 0.8 (fixed)

# Track explicit rating
await profile_service.track_interaction(
    user_id="user-123",
    resource_id="resource-456",
    interaction_type="rating",
    rating=5
)
# Strength: 1.0 (5 stars)
```

### Get User Profile

```python
# Get or create user profile
profile = await profile_service.get_or_create_profile(user_id="user-123")

# Profile structure:
{
    "user_id": "user-123",
    "interest_vector": [0.1, 0.2, ...],  # 512-dim embedding
    "topics": ["machine learning", "nlp", "computer vision"],
    "tags": ["important", "research", "todo"],
    "interaction_counts": {
        "view": 45,
        "annotation": 12,
        "collection_add": 8,
        "export": 3,
        "rating": 5
    },
    "total_interactions": 73,
    "last_active_at": "2024-12-31T12:00:00Z",
    "settings": {
        "diversity_preference": 0.5,
        "novelty_preference": 0.3,
        "recency_preference": 0.7
    }
}
```

### Update Profile Settings

```python
# Update user preferences
await profile_service.update_profile_settings(
    user_id="user-123",
    diversity_preference=0.7,  # More diverse recommendations
    novelty_preference=0.5,    # Balance familiar and novel
    recency_preference=0.8     # Prefer recent content
)
```

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

### Get Personalized Recommendations (continued)

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
