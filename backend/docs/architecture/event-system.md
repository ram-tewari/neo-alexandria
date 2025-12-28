# Event System Architecture

Event-driven communication, Celery task queue, and Redis caching for Neo Alexandria 2.0.

> **Last Updated**: Phase 14 - Complete Vertical Slice Refactor

## Table of Contents

1. [Overview](#overview)
2. [Event System Core](#event-system-core)
3. [Celery Distributed Task Queue](#celery-distributed-task-queue)
4. [Redis Caching Architecture](#redis-caching-architecture)
5. [Event Hooks](#event-hooks)
6. [Service Integration](#service-integration)
7. [Docker Compose Orchestration](#docker-compose-orchestration)
8. [Performance Characteristics](#performance-characteristics)

---

## Overview

The event system enables loose coupling between modules through publish-subscribe messaging. Modules emit events when significant actions occur, and other modules can subscribe to react to these events.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN ARCHITECTURE (Phase 12.5)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Event System Core                           │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                     EventEmitter (Singleton)                 │   │    │
│  │  │  • on(event_type, handler) - Register listener               │   │    │
│  │  │  • off(event_type, handler) - Unregister listener            │   │    │
│  │  │  • emit(event_type, data, priority) - Dispatch event         │   │    │
│  │  │  • get_event_history(limit) - Retrieve event log             │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    SystemEvent Enum                          │   │    │
│  │  │  Resource: created, updated, deleted, content_changed        │   │    │
│  │  │  Processing: ingestion, embedding, quality, classification   │   │    │
│  │  │  User: interaction_tracked, profile_updated                  │   │    │
│  │  │  System: cache_invalidated, search_index_updated             │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event System Core

### Event Bus Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVENT BUS (Pub/Sub)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Publishers                    Event Bus                  Subscribers   │
│  ──────────                    ─────────                  ───────────   │
│                                                                         │
│  ┌──────────┐                ┌───────────┐              ┌──────────┐    │
│  │Resources │──publish──────►│           │──notify─────►│Collections│   │
│  │ Module   │                │           │              │  Module   │   │
│  └──────────┘                │           │              └──────────┘    │
│                              │  Event    │                              │
│  ┌──────────┐                │   Bus     │              ┌──────────┐    │
│  │Collections│──publish─────►│           │──notify─────►│ Search   │    │
│  │  Module  │                │           │              │  Module  │    │
│  └──────────┘                │           │              └──────────┘    │
│                              │           │                              │
│  ┌──────────┐                │           │              ┌──────────┐    │
│  │ Search   │──publish──────►│           │──notify─────►│Analytics │    │
│  │  Module  │                └───────────┘              │ (future) │    │
│  └──────────┘                                           └──────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Event Types

#### Resource Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `resource.created` | `{resource_id, title, ...}` | New resource ingested |
| `resource.updated` | `{resource_id, changes}` | Resource metadata updated |
| `resource.deleted` | `{resource_id}` | Resource deleted |
| `resource.content_changed` | `{resource_id}` | Content modified |
| `resource.metadata_changed` | `{resource_id}` | Metadata modified |
| `resource.classified` | `{resource_id, taxonomy_ids}` | Classification assigned |
| `resource.quality_computed` | `{resource_id, score}` | Quality score calculated |

#### Collection Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `collection.created` | `{collection_id, name}` | New collection created |
| `collection.updated` | `{collection_id, changes}` | Collection metadata updated |
| `collection.deleted` | `{collection_id}` | Collection deleted |
| `collection.resource_added` | `{collection_id, resource_ids}` | Resources added |
| `collection.resource_removed` | `{collection_id, resource_ids}` | Resources removed |

#### Search Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `search.executed` | `{query, results_count, latency}` | Search performed |
| `search.facets_computed` | `{query, facets}` | Facets calculated |

#### Processing Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `ingestion.started` | `{url, resource_id}` | Ingestion begins |
| `ingestion.completed` | `{resource_id, status}` | Ingestion finishes |
| `citations.extracted` | `{resource_id, citation_ids}` | Citations parsed |
| `authors.extracted` | `{resource_id, author_names}` | Authors identified |

### Event Bus Implementation

```python
# app/shared/event_bus.py
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a handler from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

# Global event bus instance
event_bus = EventBus()
```

---

## Celery Distributed Task Queue

### Task Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CELERY TASK HIERARCHY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌──────────────────┐                                 │
│                        │  DatabaseTask    │                                 │
│                        │  (Base Class)    │                                 │
│                        │  • __call__()    │                                 │
│                        │  • Session mgmt  │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│         ┌───────────────────────┼───────────────────────┐                   │
│         │                       │                       │                   │
│  ┌──────▼──────────┐   ┌────────▼─────────┐   ┌─────────▼────────┐          │
│  │ regenerate_     │   │ recompute_       │   │ update_search_   │          │
│  │ embedding_task  │   │ quality_task     │   │ index_task       │          │
│  ├─────────────────┤   ├──────────────────┤   ├──────────────────┤          │
│  │ • max_retries=3 │   │ • max_retries=2  │   │ • priority=9     │          │
│  │ • retry_delay=60│   │ • priority=5     │   │ • max_retries=3  │          │
│  │ • priority=7    │   │ • countdown=10   │   │ • countdown=1    │          │
│  │ • countdown=5   │   └──────────────────┘   └──────────────────┘          │
│  └─────────────────┘                                                        │
│                                                                             │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐         │
│  │ update_graph_    │   │ classify_        │   │ invalidate_      │         │
│  │ edges_task       │   │ resource_task    │   │ cache_task       │         │
│  ├──────────────────┤   ├──────────────────┤   ├──────────────────┤         │
│  │ • priority=5     │   │ • max_retries=2  │   │ • priority=9     │         │
│  │ • countdown=30   │   │ • priority=5     │   │ • countdown=0    │         │
│  │ • batch_delay    │   │ • countdown=20   │   │ • pattern support│         │
│  └──────────────────┘   └──────────────────┘   └──────────────────┘         │
│                                                                             │
│  ┌──────────────────┐   ┌──────────────────────────────────────────┐        │
│  │ refresh_         │   │ batch_process_resources_task             │        │
│  │ recommendation_  │   ├──────────────────────────────────────────┤        │
│  │ profile_task     │   │ • Progress tracking with update_state()  │        │
│  ├──────────────────┤   │ • Operations: regenerate_embeddings,     │        │
│  │ • priority=3     │   │   recompute_quality                      │        │
│  │ • countdown=300  │   │ • Returns: processed_count, status       │        │
│  └──────────────────┘   └──────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Task Routing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Task Routing                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  • urgent queue (priority 9) - Search index, cache invalidation         │
│  • high_priority queue (priority 7) - Embeddings                        │
│  • ml_tasks queue (priority 5) - Classification, quality                │
│  • batch queue (priority 3) - Batch processing                          │
│  • default queue (priority 5) - General tasks                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Redis Caching Architecture

### Multi-Layer Caching

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-LAYER REDIS CACHING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         RedisCache Class                            │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Methods:                                                    │   │    │
│  │  │  • get(key) → value | None                                   │   │    │
│  │  │  • set(key, value, ttl) → None                               │   │    │
│  │  │  • delete(key) → None                                        │   │    │
│  │  │  • delete_pattern(pattern) → int (count)                     │   │    │
│  │  │  • get_default_ttl(key) → int (seconds)                      │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    CacheStats Tracking                       │   │    │
│  │  │  • hits: int                                                 │   │    │
│  │  │  • misses: int                                               │   │    │
│  │  │  • invalidations: int                                        │   │    │
│  │  │  • hit_rate() → float (0.0-1.0)                              │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Cache Key Strategy                           │    │
│  │                                                                     │    │
│  │  embedding:{resource_id}           TTL: 3600s (1 hour)              │    │
│  │  quality:{resource_id}             TTL: 1800s (30 minutes)          │    │
│  │  search_query:{hash}               TTL: 300s (5 minutes)            │    │
│  │  resource:{resource_id}            TTL: 600s (10 minutes)           │    │
│  │  graph:{resource_id}:neighbors     TTL: 1800s (30 minutes)          │    │
│  │  user:{user_id}:profile            TTL: 600s (10 minutes)           │    │
│  │  classification:{resource_id}      TTL: 3600s (1 hour)              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Cache Invalidation Patterns                      │    │
│  │                                                                     │    │
│  │  resource:{resource_id}:*          → All resource-related caches    │    │
│  │  search_query:*                    → All search result caches       │    │
│  │  graph:*                           → All graph caches               │    │
│  │  user:{user_id}:*                  → All user-related caches        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event Hooks

### Auto-Consistency Hooks

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Event Hooks (Auto-Consistency)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  resource.content_changed ──► regenerate_embedding_task (5s delay)      │
│  resource.metadata_changed ─► recompute_quality_task (10s delay)        │
│  resource.updated ──────────► update_search_index_task (1s delay)       │
│  citations.extracted ────────► update_graph_edges_task (30s delay)      │
│  resource.updated ──────────► invalidate_cache_task (immediate)         │
│  user.interaction_tracked ───► refresh_profile_task (every 10)          │
│  resource.created ───────────► classify_resource_task (20s delay)       │
│  authors.extracted ──────────► normalize_names_task (60s delay)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Service Integration

### ResourceService Event Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ResourceService                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  create(data) → Resource                                                │
│    1. Create resource in database                                       │
│    2. Emit: resource.created                                            │
│    3. Hooks trigger: classify_resource_task                             │
│                                                                         │
│  update(id, data) → Resource                                            │
│    1. Update resource in database                                       │
│    2. Detect changes (content vs metadata)                              │
│    3. Emit: resource.updated                                            │
│    4. Emit: resource.content_changed (if content changed)               │
│    5. Emit: resource.metadata_changed (if metadata changed)             │
│    6. Hooks trigger:                                                    │
│       - regenerate_embedding_task (if content)                          │
│       - recompute_quality_task (if metadata)                            │
│       - update_search_index_task (always)                               │
│       - invalidate_cache_task (always)                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### IngestionService Event Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      IngestionService                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  process(url) → Resource                                                │
│    1. Emit: ingestion.started                                           │
│    2. Fetch and extract content                                         │
│    3. Generate embeddings                                               │
│    4. Extract citations → Emit: citations.extracted                     │
│    5. Extract authors → Emit: authors.extracted                         │
│    6. Compute quality                                                   │
│    7. Create resource → Emit: resource.created                          │
│    8. Emit: ingestion.completed                                         │
│    9. Hooks trigger all downstream tasks                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### UserInteractionTracking

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   UserInteractionTracking                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  track_interaction(user_id, resource_id, type) → None                   │
│    1. Record interaction in database                                    │
│    2. Get total interaction count for user                              │
│    3. Emit: user.interaction_tracked                                    │
│    4. Hook checks: if count % 10 == 0                                   │
│       → refresh_recommendation_profile_task                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Docker Compose Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DOCKER COMPOSE ORCHESTRATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                            Redis                                    │    │
│  │  • Image: redis:7-alpine                                            │    │
│  │  • Memory: 2GB with allkeys-lru eviction                            │    │
│  │  • Persistence: appendonly yes                                      │    │
│  │  • Port: 6379                                                       │    │
│  │  • Health check: redis-cli ping                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                         │
│                    ┌──────────────┼──────────────┐                          │
│                    │              │              │                          │
│  ┌─────────────────▼──┐  ┌────────▼────────┐  ┌──▼──────────────────┐       │
│  │  Celery Workers    │  │  Celery Beat    │  │     Flower          │       │
│  │  (4 replicas)      │  │  (Scheduler)    │  │   (Monitoring)      │       │
│  ├────────────────────┤  ├─────────────────┤  ├─────────────────────┤       │
│  │ • Concurrency: 4   │  │ • Schedules:    │  │ • Port: 5555        │       │
│  │ • CPU: 2 cores     │  │   - Daily 2 AM  │  │ • Web dashboard     │       │
│  │ • Memory: 2GB      │  │   - Weekly Sun  │  │ • Task monitoring   │       │
│  │ • Queues: all      │  │   - Monthly 1st │  │ • Worker stats      │       │
│  │ • Auto-restart     │  │   - Daily 4 AM  │  │ • Real-time graphs  │       │
│  └────────────────────┘  └─────────────────┘  └─────────────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FastAPI Application                         │    │
│  │  • Depends on: Redis                                                │    │
│  │  • Environment: CELERY_BROKER_URL, CELERY_RESULT_BACKEND            │    │
│  │  • Startup: register_all_hooks(), initialize Redis cache            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 12.5 PERFORMANCE METRICS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scalability:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 100+ concurrent ingestions without degradation                   │    │
│  │  • Linear throughput scaling with worker count                      │    │
│  │  • Horizontal scaling across multiple machines                      │    │
│  │  • 4 workers → 400 tasks/minute                                     │    │
│  │  • 8 workers → 800 tasks/minute (linear)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Cache Performance:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 60-70% cache hit rate for repeated operations                    │    │
│  │  • 50-70% computation reduction through caching                     │    │
│  │  • Sub-millisecond cache lookups                                    │    │
│  │  • Pattern-based invalidation in <10ms                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Task Reliability:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • <1% task failure rate with automatic retries                     │    │
│  │  • Exponential backoff for transient errors                         │    │
│  │  • Dead letter queue for permanent failures                         │    │
│  │  • Task acknowledgment after completion                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Search Index Updates:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Complete within 5 seconds of resource updates                    │    │
│  │  • URGENT priority ensures immediate searchability                  │    │
│  │  • Automatic retry on failure                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Database Connection Pooling:                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 20 base connections + 40 overflow = 60 total                     │    │
│  │  • Connection recycling after 1 hour                                │    │
│  │  • Pre-ping health checks                                           │    │
│  │  • Handles 100+ concurrent requests                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### Event Design

- Keep payloads minimal (IDs, not full objects)
- Include timestamp for ordering
- Use past tense for event names (`created`, not `create`)
- Make events idempotent when possible

### Handler Design

- Handlers should be fast (<100ms)
- Use background tasks for slow operations
- Handle errors gracefully (don't crash on failure)
- Log all event processing

### Testing Events

```python
def test_resource_deletion_updates_collections(db, event_bus):
    # Create resource and collection
    resource = create_resource(db, {...})
    collection = create_collection(db, {...})
    add_resource_to_collection(db, collection.id, resource.id)
    
    # Delete resource (triggers event)
    delete_resource(db, resource.id)
    
    # Verify collection updated
    updated = get_collection(db, collection.id)
    assert resource.id not in [r.id for r in updated.resources]
```

---

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [Modules](modules.md) - Vertical slice architecture
- [Database](database.md) - Schema and models
- [Event-Driven Refactoring](../EVENT_DRIVEN_REFACTORING.md) - Migration details
