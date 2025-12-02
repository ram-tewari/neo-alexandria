# Design Document

## Overview

Phase 12.5 transforms Neo Alexandria into an event-driven, horizontally scalable system with distributed task processing. This design replaces the monolithic request-response pattern with a decoupled architecture where components communicate through events, background tasks are processed reliably by Celery workers, and intelligent caching reduces computation by 50-70%.

### Core Design Principles

1. **Decoupling through Events**: Components emit events rather than calling each other directly
2. **Automatic Consistency**: Event hooks ensure derived data stays synchronized
3. **Reliability First**: All background operations use Celery with retries and persistence
4. **Cache Aggressively**: Multi-layer Redis caching with intelligent invalidation
5. **Scale Horizontally**: Add workers to increase throughput linearly

### Architecture Transformation

**Before (Phase 12):**
```
API Request → Service → Database → Compute (blocking) → Response
```

**After (Phase 12.5):**
```
API Request → Service → Database → Emit Event → Response (fast)
                                         ↓
                                    Event Hooks
                                         ↓
                                  Celery Task Queue
                                         ↓
                              Distributed Workers (async)
```

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Routers    │───▶│   Services   │───▶│  Event       │     │
│  │  (API Layer) │    │  (Business)  │    │  Emitter     │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                   │              │
└───────────────────────────────────────────────────┼─────────────┘
                                                    │ emit events
                                                    ▼
                ┌────────────────────────────────────────┐
                │         Event Hook Registry            │
                │  (Automatic Reactions to Events)       │
                └────────────┬───────────────────────────┘
                             │ queue tasks
                             ▼
                ┌────────────────────────────────────────┐
                │         Redis (Message Broker)         │
                │  ┌──────────────┐  ┌──────────────┐   │
                │  │ Task Queues  │  │    Cache     │   │
                │  │  - urgent    │  │  - queries   │   │
                │  │  - high      │  │  - embeddings│   │
                │  │  - normal    │  │  - quality   │   │
                │  │  - low       │  │  - resources │   │
                │  └──────┬───────┘  └──────────────┘   │
                └─────────┼──────────────────────────────┘
                          │ consume tasks
                          ▼
        ┌─────────────────────────────────────────────────┐
        │         Celery Worker Pool (Horizontal)         │
        │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│
        │  │Worker 1│  │Worker 2│  │Worker 3│  │Worker N││
        │  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘│
        └──────┼───────────┼───────────┼───────────┼──────┘
               │           │           │           │
               └───────────┴───────────┴───────────┘
                           │ execute tasks
                           ▼
                ┌──────────────────────────┐
                │   PostgreSQL Database    │
                │  (Connection Pool: 60)   │
                └──────────────────────────┘
```

### Component Interaction Flow

**Example: Resource Update Flow**

1. **API Request**: `PUT /resources/{id}` with updated content
2. **Service Layer**: `ResourceService.update()` saves to database
3. **Event Emission**: Service emits `resource.updated` and `resource.content_changed` events
4. **Event Hooks Triggered** (all happen automatically):
   - Hook 1: Queue embedding regeneration (HIGH priority, 5s delay)
   - Hook 2: Queue quality recomputation (MEDIUM priority, 10s delay)
   - Hook 3: Queue search index update (URGENT priority, 1s delay)
   - Hook 4: Invalidate caches (URGENT priority, immediate)
5. **API Response**: Returns immediately (< 100ms)
6. **Background Processing**: Celery workers process tasks asynchronously
7. **Data Consistency**: All derived data updated within seconds

## Components and Interfaces

### 1. Event System (`app/events/event_system.py`)

**Purpose**: Publisher-subscriber pattern for decoupled communication

**Key Classes**:

```python
class EventPriority(Enum):
    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25

@dataclass
class Event:
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: EventPriority
    correlation_id: str

class EventEmitter:
    """Singleton event dispatcher"""
    
    def on(event_name: str, handler: Callable, async_handler: bool = False)
    def off(event_name: str, handler: Callable)
    def emit(event_name: str, data: Dict, priority: EventPriority) -> Event
    def get_listeners(event_name: str) -> List[Callable]
    def get_event_history(limit: int = 100) -> List[Event]
```

**Design Decisions**:
- Singleton pattern ensures single event bus across application
- Supports both sync and async handlers for flexibility
- Event history (last 1000) enables debugging and audit trails
- Error isolation: Handler failures don't affect other handlers

### 2. Event Types (`app/events/event_types.py`)

**Purpose**: Centralized registry of all system events

**Naming Convention**: `{entity}.{action}`

**Event Categories**:
- Resource lifecycle: `resource.created`, `resource.updated`, `resource.deleted`
- Content changes: `resource.content_changed`, `resource.metadata_changed`
- Processing: `ingestion.completed`, `embedding.generated`, `quality.computed`
- Search: `search.executed`, `search.index_updated`
- Graph: `graph.edge_added`, `graph.cache_invalidated`
- User: `user.interaction_tracked`, `user.profile_updated`
- Cache: `cache.hit`, `cache.miss`, `cache.invalidated`
- System: `background_task.started`, `background_task.completed`

**Design Decisions**:
- String enum for type safety and IDE autocomplete
- Consistent naming enables pattern matching
- Comprehensive coverage of all system state changes

### 3. Event Hooks (`app/events/hooks.py`)

**Purpose**: Automatic reactions to events for data consistency

**Hook Architecture**:

```python
def on_content_changed_regenerate_embedding(event: Event):
    """Hook: content change → regenerate embedding"""
    resource_id = event.data.get("resource_id")
    regenerate_embedding_task.apply_async(
        args=[resource_id],
        priority=7,  # HIGH
        countdown=5  # 5-second debounce
    )
```

**Implemented Hooks**:

| Hook | Trigger Event | Action | Priority | Delay |
|------|---------------|--------|----------|-------|
| Embedding Regen | `resource.content_changed` | Regenerate embeddings | HIGH (7) | 5s |
| Quality Rescore | `resource.metadata_changed` | Recompute quality | MEDIUM (5) | 10s |
| Search Index Sync | `resource.updated` | Update FTS5 index | URGENT (9) | 1s |
| Graph Update | `citations.extracted` | Add citation edges | MEDIUM (5) | 30s |
| Cache Invalidation | `resource.updated` | Clear stale caches | URGENT (9) | 0s |
| Recommendation Refresh | `user.interaction_tracked` | Update user profile | LOW (3) | 300s |
| Classification | `resource.created` | Suggest categories | MEDIUM (5) | 20s |
| Author Normalization | `authors.extracted` | Normalize names | LOW (3) | 60s |

**Design Decisions**:
- Debounce delays prevent duplicate work from rapid updates
- Priority levels ensure critical tasks (search, cache) execute first
- Batch delays (30s, 60s) allow grouping similar operations
- Hooks registered at startup via `register_all_hooks()`

### 4. Celery Application (`app/tasks/celery_app.py`)

**Purpose**: Distributed task queue configuration

**Configuration**:

```python
celery_app = Celery(
    "neo_alexandria",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

# Task routing
task_routes = {
    "regenerate_embedding_task": {"queue": "high_priority"},
    "update_search_index_task": {"queue": "urgent"},
    "classify_resource_task": {"queue": "ml_tasks"},
    "batch_process_task": {"queue": "batch"}
}

# Priority queuing
task_queue_max_priority = 10
task_default_priority = 5

# Reliability
task_acks_late = True  # Acknowledge after completion
task_reject_on_worker_lost = True  # Requeue on crash

# Worker optimization
worker_prefetch_multiplier = 4  # Prefetch 4 tasks
worker_max_tasks_per_child = 1000  # Restart after 1000 tasks
```

**Scheduled Tasks (Celery Beat)**:

```python
beat_schedule = {
    "monitor-quality-degradation": {
        "task": "monitor_quality_degradation",
        "schedule": crontab(hour=2, minute=0)  # Daily 2 AM
    },
    "detect-quality-outliers": {
        "task": "detect_quality_outliers",
        "schedule": crontab(day_of_week=0, hour=3)  # Sunday 3 AM
    },
    "retrain-classification-model": {
        "task": "retrain_classification_model",
        "schedule": crontab(day_of_month=1, hour=0)  # Monthly
    },
    "cleanup-expired-cache": {
        "task": "cleanup_expired_cache",
        "schedule": crontab(hour=4, minute=0)  # Daily 4 AM
    }
}
```

**Design Decisions**:
- Redis as broker: Fast, reliable, supports priority queues
- Multiple queues: Separate urgent, high, normal, low, ML, batch
- Late acknowledgment: Tasks requeued if worker crashes
- Worker recycling: Prevents memory leaks from long-running workers
- Scheduled tasks: Automated maintenance without manual intervention

### 5. Celery Tasks (`app/tasks/celery_tasks.py`)

**Purpose**: Background task implementations with retry logic

**Base Task Class**:

```python
class DatabaseTask(Task):
    """Base task with automatic DB session management"""
    
    def __call__(self, *args, **kwargs):
        db = next(get_db())
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()
```

**Task Implementations**:


**1. Embedding Regeneration Task**:
```python
@celery_app.task(bind=True, base=DatabaseTask, max_retries=3, default_retry_delay=60)
def regenerate_embedding_task(self, resource_id: str, db=None):
    """Regenerate embeddings with exponential backoff on transient errors"""
    try:
        embedding_service = EmbeddingService(db)
        embedding_service.generate_and_store_embedding(resource_id)
    except Exception as e:
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        raise
```

**2. Quality Recomputation Task**:
```python
@celery_app.task(bind=True, base=DatabaseTask, max_retries=2)
def recompute_quality_task(self, resource_id: str, db=None):
    """Recompute quality scores"""
    quality_service = QualityService(db)
    quality_service.compute_quality(resource_id)
```

**3. Search Index Update Task**:
```python
@celery_app.task(bind=True, base=DatabaseTask, max_retries=3, priority=9)
def update_search_index_task(self, resource_id: str, db=None):
    """Update FTS5 index (URGENT priority)"""
    search_service = SearchService(db)
    search_service.update_fts5_index(resource_id)
```

**4. Cache Invalidation Task**:
```python
@celery_app.task(priority=9)
def invalidate_cache_task(cache_keys: list):
    """Invalidate cache keys (URGENT priority)"""
    from app.cache.redis_cache import cache
    for key in cache_keys:
        if "*" in key:
            cache.delete_pattern(key)
        else:
            cache.delete(key)
```

**5. Batch Processing Task**:
```python
@celery_app.task(bind=True, base=DatabaseTask)
def batch_process_resources_task(self, resource_ids: list, operation: str, db=None):
    """Batch process with progress tracking"""
    total = len(resource_ids)
    for i, resource_id in enumerate(resource_ids):
        self.update_state(
            state='PROCESSING',
            meta={'current': i + 1, 'total': total}
        )
        # Execute operation
        if operation == "regenerate_embeddings":
            regenerate_embedding_task.apply_async(args=[resource_id])
    return {'status': 'completed', 'processed': total}
```

**Design Decisions**:
- Bind tasks to access `self.retry()` and `self.update_state()`
- DatabaseTask base class manages DB sessions automatically
- Exponential backoff for transient errors (network, timeout)
- No retry on permanent errors (validation, not found)
- Progress tracking for long-running batch operations

### 6. Redis Cache Layer (`app/cache/redis_cache.py`)

**Purpose**: Multi-layer caching with intelligent invalidation

**Cache Architecture**:

```python
class RedisCache:
    """Redis-based caching with TTL and pattern invalidation"""
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_CACHE_DB,
            decode_responses=True
        )
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = self.redis.get(key)
        if value:
            self.stats.record_hit()
            return json.loads(value)
        self.stats.record_miss()
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value with TTL"""
        self.redis.setex(
            key,
            ttl or self.get_default_ttl(key),
            json.dumps(value)
        )
    
    def delete(self, key: str):
        """Delete single key"""
        self.redis.delete(key)
        self.stats.record_invalidation()
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
            self.stats.record_invalidation(len(keys))
    
    def get_default_ttl(self, key: str) -> int:
        """Get TTL based on key type"""
        if key.startswith("embedding:"):
            return 3600  # 1 hour
        elif key.startswith("quality:"):
            return 1800  # 30 minutes
        elif key.startswith("search_query:"):
            return 300  # 5 minutes
        elif key.startswith("resource:"):
            return 600  # 10 minutes
        return 300  # Default 5 minutes
```

**Cache Key Patterns**:
- `embedding:{resource_id}` - Embedding vectors
- `quality:{resource_id}` - Quality scores
- `search_query:{hash}` - Search results
- `resource:{resource_id}` - Full resource data
- `graph:neighbors:{resource_id}` - Graph neighbors
- `recommendations:{user_id}` - User recommendations

**Cache Statistics**:
```python
class CacheStats:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.invalidations = 0
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

**Design Decisions**:
- Different TTLs based on data volatility
- Pattern invalidation for bulk cache clearing
- Statistics tracking for monitoring cache effectiveness
- JSON serialization for complex objects
- Automatic TTL selection based on key prefix

### 7. Database Connection Pooling (`app/database.py`)

**Purpose**: Optimized connection management for high concurrency

**Configuration**:

```python
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Base connections
    max_overflow=40,        # Additional connections
    pool_recycle=3600,      # Recycle after 1 hour
    pool_pre_ping=True,     # Health check before use
    echo_pool=True          # Log pool events
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Dependency injection for DB sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Pool Monitoring**:
```python
def get_pool_status():
    """Get connection pool statistics"""
    return {
        "size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total": engine.pool.size() + engine.pool.overflow()
    }
```

**Design Decisions**:
- 60 total connections (20 + 40) supports high concurrency
- Pre-ping prevents "MySQL server has gone away" errors
- Connection recycling prevents stale connections
- Pool monitoring enables capacity planning

## Data Models

### Event Data Model

```python
@dataclass
class Event:
    """Represents a system event"""
    name: str                    # Event type (e.g., "resource.updated")
    data: Dict[str, Any]         # Event payload
    timestamp: datetime          # When event occurred
    priority: EventPriority      # Processing priority
    correlation_id: str = None   # For tracking event chains
```

**Event Payload Examples**:

```python
# Resource updated event
{
    "resource_id": "uuid-123",
    "changed_fields": ["content", "title"],
    "user_id": "user-456"
}

# Ingestion completed event
{
    "ingestion_id": "ing-789",
    "resource_id": "uuid-123",
    "duration_seconds": 45.2,
    "success": True
}

# User interaction event
{
    "user_id": "user-456",
    "resource_id": "uuid-123",
    "interaction_type": "view",
    "total_interactions": 42
}
```

### Task Result Model

```python
class TaskResult:
    """Celery task result stored in Redis"""
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
    result: Any
    traceback: str
    date_done: datetime
    meta: Dict[str, Any]  # Progress info for long tasks
```

### Cache Entry Model

```python
class CacheEntry:
    """Redis cache entry"""
    key: str
    value: str  # JSON-serialized
    ttl: int    # Seconds until expiration
    created_at: datetime
```

## Error Handling

### Task Retry Strategy

**Transient Errors** (retry with backoff):
- Network timeouts
- Database connection errors
- Redis connection errors
- External API rate limits

**Permanent Errors** (fail immediately):
- Validation errors
- Resource not found
- Invalid parameters
- Business logic violations

**Retry Configuration**:
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
```

### Event Handler Error Isolation

```python
def emit(self, event_name: str, data: Dict) -> Event:
    """Emit event with error isolation"""
    for handler in self._listeners[event_name]:
        try:
            handler(event)
        except Exception as e:
            # Log error but continue with other handlers
            logger.error(f"Handler error for {event_name}: {e}", exc_info=True)
```

**Design Decision**: Handler failures don't cascade - one broken hook doesn't break others

### Dead Letter Queue

```python
@celery_app.task
def handle_failed_task(task_id: str, exc: Exception, traceback: str):
    """Handle permanently failed tasks"""
    # Log to monitoring system
    logger.error(f"Task {task_id} failed permanently: {exc}")
    
    # Store in dead letter queue for manual review
    db.add(FailedTask(
        task_id=task_id,
        exception=str(exc),
        traceback=traceback,
        timestamp=datetime.utcnow()
    ))
```

## Testing Strategy

### Unit Tests

**Event System Tests**:
```python
def test_event_emission():
    """Test event emitter dispatches to handlers"""
    emitter = EventEmitter()
    handler_called = False
    
    def handler(event):
        nonlocal handler_called
        handler_called = True
    
    emitter.on("test.event", handler)
    emitter.emit("test.event", {"data": "value"})
    
    assert handler_called

def test_event_handler_error_isolation():
    """Test handler errors don't affect other handlers"""
    emitter = EventEmitter()
    handler2_called = False
    
    def handler1(event):
        raise Exception("Handler 1 error")
    
    def handler2(event):
        nonlocal handler2_called
        handler2_called = True
    
    emitter.on("test.event", handler1)
    emitter.on("test.event", handler2)
    emitter.emit("test.event")
    
    assert handler2_called  # Handler 2 still executed
```

**Cache Tests**:
```python
def test_cache_get_set():
    """Test cache storage and retrieval"""
    cache = RedisCache()
    cache.set("test:key", {"value": 123})
    result = cache.get("test:key")
    assert result == {"value": 123}

def test_cache_pattern_invalidation():
    """Test pattern-based cache clearing"""
    cache = RedisCache()
    cache.set("search_query:abc", {"results": []})
    cache.set("search_query:def", {"results": []})
    cache.delete_pattern("search_query:*")
    
    assert cache.get("search_query:abc") is None
    assert cache.get("search_query:def") is None
```

### Integration Tests

**Hook Integration Tests**:
```python
@pytest.mark.integration
def test_content_change_triggers_embedding_regen(db_session):
    """Test content change hook queues embedding task"""
    # Create resource
    resource = create_test_resource(db_session)
    
    # Update content
    resource.content = "New content"
    db_session.commit()
    
    # Emit event
    event_emitter.emit("resource.content_changed", {
        "resource_id": resource.id
    })
    
    # Verify task queued
    # (Check Celery queue or use test mode)
    assert regenerate_embedding_task.delay.called
```

**End-to-End Tests**:
```python
@pytest.mark.e2e
def test_resource_update_full_flow(client, db_session):
    """Test complete resource update flow"""
    # Create resource
    resource = create_test_resource(db_session)
    
    # Update via API
    response = client.put(f"/resources/{resource.id}", json={
        "content": "Updated content"
    })
    assert response.status_code == 200
    
    # Wait for background tasks
    time.sleep(2)
    
    # Verify embedding updated
    embedding = db_session.query(Embedding).filter_by(
        resource_id=resource.id
    ).first()
    assert embedding is not None
    
    # Verify search index updated
    search_results = client.get("/search", params={
        "query": "Updated content"
    }).json()
    assert resource.id in [r["id"] for r in search_results]
```

### Performance Tests

```python
@pytest.mark.performance
def test_concurrent_ingestions(client):
    """Test 100 concurrent ingestions"""
    import concurrent.futures
    
    def ingest_resource():
        return client.post("/ingest", json={
            "url": "https://example.com/paper.pdf"
        })
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(ingest_resource) for _ in range(100)]
        results = [f.result() for f in futures]
    
    # All should succeed
    assert all(r.status_code == 202 for r in results)
    
    # Wait for processing
    time.sleep(60)
    
    # Verify all completed
    # (Check task results)
```

### Load Tests

```python
# locustfile.py
from locust import HttpUser, task, between

class NeoAlexandriaUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def search(self):
        self.client.get("/search", params={"query": "machine learning"})
    
    @task(1)
    def get_resource(self):
        self.client.get(f"/resources/{random_resource_id()}")
    
    @task(1)
    def update_resource(self):
        self.client.put(f"/resources/{random_resource_id()}", json={
            "title": "Updated title"
        })
```

## Deployment Architecture

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Redis (Cache + Message Broker)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: neo_alexandria
      POSTGRES_USER: neo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U neo"]
      interval: 10s
      timeout: 3s
      retries: 3

  # FastAPI Application
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://neo:${DB_PASSWORD}@postgres:5432/neo_alexandria
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  # Celery Workers (4 instances)
  worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: postgresql://neo:${DB_PASSWORD}@postgres:5432/neo_alexandria
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 2G

  # Celery Beat (Scheduler)
  beat:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - redis

  # Flower (Monitoring)
  flower:
    build: .
    command: celery -A app.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - redis

volumes:
  redis_data:
  postgres_data:
```

### Scaling Strategy

**Horizontal Scaling**:
```bash
# Scale workers to 8 instances
docker-compose up --scale worker=8

# Scale workers on different machines
docker-compose -f docker-compose.prod.yml up worker --scale worker=4
```

**Resource Allocation**:
- API: 2 CPU, 4GB RAM
- Worker: 2 CPU, 2GB RAM each
- Redis: 4 CPU, 4GB RAM
- PostgreSQL: 4 CPU, 8GB RAM

## Monitoring and Observability

### Flower Dashboard

Access: `http://localhost:5555`

**Metrics**:
- Active tasks by queue
- Task success/failure rates
- Worker status and utilization
- Task execution times
- Queue depths

### API Endpoints

**Event History**:
```python
@router.get("/events/history")
def get_event_history(limit: int = 100):
    """Get recent events"""
    return event_emitter.get_event_history(limit)
```

**Cache Statistics**:
```python
@router.get("/cache/stats")
def get_cache_stats():
    """Get cache performance metrics"""
    return {
        "hit_rate": cache.stats.hit_rate(),
        "hits": cache.stats.hits,
        "misses": cache.stats.misses,
        "invalidations": cache.stats.invalidations
    }
```

**Worker Health**:
```python
@router.get("/workers/status")
def get_worker_status():
    """Get Celery worker status"""
    inspect = celery_app.control.inspect()
    return {
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "stats": inspect.stats()
    }
```

**Database Pool**:
```python
@router.get("/db/pool")
def get_db_pool_status():
    """Get connection pool status"""
    return get_pool_status()
```

### Logging Strategy

```python
# Structured logging
logger.info("Task started", extra={
    "task_id": task_id,
    "resource_id": resource_id,
    "priority": priority
})

logger.info("Task completed", extra={
    "task_id": task_id,
    "duration_ms": duration,
    "success": True
})
```

## Migration Plan

### Phase 1: Infrastructure Setup (Week 1)

1. Deploy Redis container
2. Configure Celery application
3. Set up Celery workers (1 initially)
4. Deploy Flower monitoring
5. Configure connection pooling

### Phase 2: Event System (Week 1-2)

1. Implement EventEmitter
2. Define all event types
3. Register event hooks
4. Add event emission to services

### Phase 3: Task Migration (Week 2-3)

1. Convert embedding generation to Celery
2. Convert quality computation to Celery
3. Convert search indexing to Celery
4. Convert classification to Celery
5. Remove BackgroundTasks usage

### Phase 4: Caching Layer (Week 3)

1. Implement Redis cache
2. Add caching to embedding service
3. Add caching to quality service
4. Add caching to search service
5. Implement cache invalidation

### Phase 5: Testing & Optimization (Week 4)

1. Run performance tests
2. Tune worker count
3. Optimize cache TTLs
4. Load testing (100+ concurrent)
5. Monitor and adjust

### Rollback Strategy

- Keep BackgroundTasks code temporarily
- Feature flag for Celery vs BackgroundTasks
- Monitor error rates closely
- Quick rollback if issues detected

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Computation Reduction | 50-70% | Cache hit rate × computation time |
| Concurrent Ingestions | 100+ | Load test with 100 simultaneous uploads |
| Cache Hit Rate | >60% | Redis stats after 1 week |
| Search Index Update | <5 seconds | Time from update to searchable |
| Task Failure Rate | <1% | Failed tasks / total tasks |
| API Response Time | <100ms | P95 for cached queries |
| Worker Utilization | 60-80% | Active tasks / total capacity |

## Security Considerations

1. **Redis Security**:
   - Bind to localhost only
   - Require password authentication
   - Use separate DB numbers for cache vs broker

2. **Task Security**:
   - Validate all task parameters
   - Sanitize user input before processing
   - Rate limit task submission

3. **Cache Security**:
   - Don't cache sensitive data
   - Encrypt cache values if needed
   - Implement cache key namespacing per user

4. **Worker Security**:
   - Run workers with minimal permissions
   - Isolate worker network access
   - Monitor for suspicious task patterns

## Future Enhancements

1. **Advanced Caching**:
   - Predictive cache warming
   - Multi-tier caching (Redis + in-memory)
   - Cache compression for large objects

2. **Task Optimization**:
   - Task result caching
   - Smart batching of similar tasks
   - Priority adjustment based on load

3. **Monitoring**:
   - Prometheus metrics export
   - Grafana dashboards
   - Alert rules for failures

4. **Scalability**:
   - Auto-scaling workers based on queue depth
   - Geographic distribution of workers
   - Task routing based on data locality
