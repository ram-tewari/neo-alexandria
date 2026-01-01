# Event Catalog

Complete reference for all events in Neo Alexandria 2.0's event-driven architecture.

> **Phase 14 Complete**: This catalog documents all 25+ events used for inter-module communication in the fully modular vertical slice architecture.

---

## Table of Contents

1. [Overview](#overview)
2. [Event Naming Conventions](#event-naming-conventions)
3. [Event Categories](#event-categories)
4. [Complete Event Reference](#complete-event-reference)
5. [Event Flow Diagrams](#event-flow-diagrams)
6. [Best Practices](#best-practices)
7. [Monitoring Events](#monitoring-events)

---

## Overview

### What Are Events?

Events are the primary mechanism for communication between modules in Neo Alexandria 2.0. Instead of modules directly calling each other (which creates tight coupling), modules emit events when something significant happens, and other modules subscribe to events they care about.

### Benefits of Event-Driven Architecture

1. **Loose Coupling**: Modules don't need to know about each other
2. **Scalability**: Easy to add new subscribers without modifying emitters
3. **Testability**: Modules can be tested in isolation
4. **Flexibility**: Event handlers can be added/removed dynamically
5. **Auditability**: All inter-module communication is logged

### Event Bus

The event bus is implemented in `app/shared/event_bus.py` and provides:
- **Synchronous delivery**: Events are delivered immediately in the same process
- **Error isolation**: Handler failures don't affect other handlers
- **Metrics tracking**: Events emitted, delivered, and errors are tracked
- **Type safety**: Events have defined types and payloads

---

## Event Naming Conventions

### Pattern

All events follow the pattern: `{domain}.{action}`

- **domain**: The module or entity that owns the event (lowercase, singular)
- **action**: The action that occurred (past tense, snake_case)

### Examples

```
resource.created          # Resource module created a resource
resource.updated          # Resource module updated a resource
resource.deleted          # Resource module deleted a resource
collection.updated        # Collection module updated a collection
quality.computed          # Quality module computed quality scores
quality.outlier_detected  # Quality module detected an outlier
annotation.created        # Annotation module created an annotation
```

### Guidelines

1. **Use past tense**: Events describe what happened, not what will happen
2. **Be specific**: `resource.created` not `resource.changed`
3. **Use snake_case**: `outlier_detected` not `outlierDetected`
4. **Keep it short**: Prefer concise names that are still clear
5. **Avoid abbreviations**: `metadata.extracted` not `meta.ext`

---

## Event Categories

### Resource Lifecycle Events

Events related to resource creation, modification, and deletion.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `resource.created` | Resources | New resource added to system |
| `resource.updated` | Resources | Resource metadata or content changed |
| `resource.deleted` | Resources | Resource removed from system |

### Collection Events

Events related to collection management.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `collection.updated` | Collections | Collection metadata changed |
| `collection.deleted` | Collections | Collection removed |
| `collection.resource_added` | Collections | Resource added to collection |
| `collection.resource_removed` | Collections | Resource removed from collection |

**Payload Examples**:

`collection.resource_added`:
```python
{
    "collection_id": str,      # UUID of collection
    "resource_id": str,        # UUID of added resource
    "user_id": str             # UUID of user who added it
}
```

`collection.resource_removed`:
```python
{
    "collection_id": str,      # UUID of collection
    "resource_id": str,        # UUID of removed resource
    "user_id": str | None,     # UUID of user who removed it (optional)
    "reason": str              # Reason (user_removed, resource_deleted)
}
```

### Annotation Events

Events related to user annotations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `annotation.created` | Annotations | User created annotation |
| `annotation.updated` | Annotations | User modified annotation |
| `annotation.deleted` | Annotations | User deleted annotation |

**Payload Examples**:

`annotation.created`:
```python
{
    "annotation_id": str,      # UUID of created annotation
    "resource_id": str,        # UUID of annotated resource
    "user_id": str,            # UUID of user who created it
    "has_note": bool           # Whether annotation includes a note
}
```

`annotation.updated`:
```python
{
    "annotation_id": str,      # UUID of updated annotation
    "resource_id": str,        # UUID of annotated resource
    "user_id": str,            # UUID of user who updated it
    "changes": list            # List of changed field names
}
```

`annotation.deleted`:
```python
{
    "annotation_id": str,      # UUID of deleted annotation
    "resource_id": str,        # UUID of annotated resource
    "user_id": str,            # UUID of user who deleted it
    "reason": str              # Reason for deletion (user_deleted, resource_deleted)
}
```

### Quality Events

Events related to quality assessment.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `quality.computed` | Quality | Quality scores calculated |
| `quality.outlier_detected` | Quality | Anomalous quality detected |
| `quality.degradation_detected` | Quality | Quality decreased over time |

**Payload Examples**:

`quality.computed`:
```python
{
    "resource_id": str,        # UUID of assessed resource
    "quality_score": float,    # Overall quality score (0.0-1.0)
    "dimensions": dict,        # Dimension scores (accuracy, completeness, etc.)
    "computation_version": str # Version of quality algorithm
}
```

`quality.outlier_detected`:
```python
{
    "resource_id": str,        # UUID of outlier resource
    "quality_score": float,    # Overall quality score
    "outlier_score": float,    # Outlier detection score (-1 for outlier)
    "dimensions": dict,        # Dimension scores
    "reason": str              # Reason for outlier detection
}
```

### Taxonomy Events

Events related to classification and taxonomy.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `resource.classified` | Taxonomy | Resource auto-classified |
| `taxonomy.node_created` | Taxonomy | New taxonomy node added |
| `taxonomy.model_trained` | Taxonomy | ML model retrained |

**Payload Examples**:

`resource.classified`:
```python
{
    "resource_id": str,        # UUID of classified resource
    "classification_code": str, # Assigned classification code
    "confidence": float,       # Classification confidence (0.0-1.0)
    "method": str,             # Method (rule_based, ml, hybrid)
    "taxonomy_version": str    # Optional taxonomy version
}
```

`taxonomy.model_trained`:
```python
{
    "model_type": str,         # Type (random_forest, svm, neural_network, etc.)
    "training_samples": int,   # Number of training samples
    "accuracy": float,         # Model accuracy on validation set
    "model_version": str,      # Version identifier
    "features_used": list      # Optional list of features
}
```

### Graph Events

Events related to knowledge graph and citations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `citation.extracted` | Graph | Citations parsed from resource |
| `graph.updated` | Graph | Graph structure changed |
| `hypothesis.discovered` | Graph | LBD found new connection |

**Payload Examples**:

`citation.extracted`:
```python
{
    "resource_id": str,        # UUID of resource with citations
    "citations": list,         # List of citation dictionaries
    "count": int               # Number of citations extracted
}
```

`graph.updated`:
```python
{
    "update_type": str,        # Type (node_added, edge_added, bulk_update, etc.)
    "node_count": int,         # Number of nodes affected
    "edge_count": int,         # Number of edges affected
    "affected_nodes": list     # Optional list of affected node IDs
}
```

`hypothesis.discovered`:
```python
{
    "hypothesis_id": str,      # UUID of discovered hypothesis
    "concept_a": str,          # Starting concept
    "concept_c": str,          # Target concept
    "bridging_concepts": list, # List of bridging concepts (B)
    "plausibility_score": float, # Plausibility score
    "evidence_count": int      # Number of evidence chains
}
```

### Recommendation Events

Events related to recommendations and user profiles.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `recommendation.generated` | Recommendations | Recommendations produced |
| `user.profile_updated` | Recommendations | User preferences changed |
| `interaction.recorded` | Recommendations | User interaction logged |

**Payload Examples**:

`recommendation.generated`:
```python
{
    "user_id": str,            # UUID of user receiving recommendations
    "count": int,              # Number of recommendations generated
    "strategy": str,           # Strategy used (collaborative, content, graph, hybrid)
    "resource_ids": list,      # List of recommended resource IDs
    "timestamp": str           # ISO 8601 timestamp
}
```

`user.profile_updated`:
```python
{
    "user_id": str,            # UUID of user
    "update_type": str,        # Type (annotation, collection, interaction)
    "preferences": dict,       # Updated preference vector or topics
    "timestamp": str           # ISO 8601 timestamp
}
```

`interaction.recorded`:
```python
{
    "user_id": str,            # UUID of user
    "resource_id": str,        # UUID of resource
    "interaction_type": str,   # Type (view, bookmark, rate, download, click)
    "rating": int,             # Optional rating (1-5)
    "duration_seconds": int,   # Optional duration for views
    "timestamp": str           # ISO 8601 timestamp
}
```

### Scholarly Events

Events related to academic metadata.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `metadata.extracted` | Scholarly | Academic metadata parsed |
| `equations.parsed` | Scholarly | Mathematical equations found |
| `tables.extracted` | Scholarly | Tables extracted from content |

**Payload Examples**:

`metadata.extracted`:
```python
{
    "resource_id": str,        # UUID of resource
    "metadata": dict,          # Extracted metadata dictionary
    "equation_count": int,     # Number of equations extracted
    "table_count": int,        # Number of tables extracted
    "figure_count": int        # Number of figures extracted
}
```

`equations.parsed`:
```python
{
    "resource_id": str,        # UUID of resource
    "equations": list,         # List of equation dictionaries
    "equation_count": int      # Number of equations parsed
}
```

`tables.extracted`:
```python
{
    "resource_id": str,        # UUID of resource
    "tables": list,            # List of table dictionaries
    "table_count": int         # Number of tables extracted
}
```

### Curation Events

Events related to content review.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `curation.reviewed` | Curation | Content reviewed by curator |
| `curation.approved` | Curation | Content approved |
| `curation.rejected` | Curation | Content rejected |
| `curation.flagged` | Curation | Content flagged for review |

**Payload Examples**:

`curation.reviewed`:
```python
{
    "review_id": str,          # UUID of review record
    "resource_id": str,        # UUID of reviewed resource
    "reviewer_id": str,        # User ID of reviewer
    "status": str,             # Status (pending, approved, rejected, needs_revision)
    "quality_rating": float,   # Optional quality rating (0.0-1.0)
    "notes": str               # Optional reviewer notes
}
```

`curation.approved`:
```python
{
    "review_id": str,          # UUID of review record
    "resource_id": str,        # UUID of approved resource
    "reviewer_id": str,        # User ID of reviewer
    "approval_notes": str,     # Optional approval notes
    "timestamp": str           # ISO 8601 timestamp
}
```

`curation.rejected`:
```python
{
    "review_id": str,          # UUID of review record
    "resource_id": str,        # UUID of rejected resource
    "reviewer_id": str,        # User ID of reviewer
    "rejection_reason": str,   # Reason for rejection
    "timestamp": str           # ISO 8601 timestamp
}
```

### Search Events

Events related to search operations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `search.executed` | Search | Search query executed |

**Payload Example**:

`search.executed`:
```python
{
    "query": str,              # Search query text
    "search_type": str,        # Type (fulltext, semantic, hybrid, three_way_hybrid)
    "result_count": int,       # Number of results returned
    "execution_time": float,   # Query execution time in seconds
    "user_id": str | None,     # Optional user ID
    "filters": dict | None     # Optional filters applied
}
```

---

## Complete Event Reference

### resource.created

**Emitter**: Resources Module  
**Subscribers**: Annotations, Quality, Taxonomy, Graph, Scholarly  
**Purpose**: Trigger processing for newly created resources

**Payload**:
```python
{
    "resource_id": str,        # UUID of created resource
    "title": str,              # Resource title
    "content": str,            # Resource content (may be truncated)
    "content_type": str,       # MIME type (e.g., "text/html")
    "url": str | None,         # Source URL if applicable
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.created", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Introduction to Machine Learning",
    "content": "Machine learning is...",
    "content_type": "text/html",
    "url": "https://example.com/ml-intro",
    "timestamp": "2024-01-15T10:30:00Z"
})
```

**Subscribers React By**:
- **Quality**: Computing initial quality scores
- **Taxonomy**: Auto-classifying the resource
- **Graph**: Extracting citations
- **Scholarly**: Extracting academic metadata
- **Annotations**: (No immediate action, but enables annotation creation)

---

### resource.updated

**Emitter**: Resources Module  
**Subscribers**: Quality, Search  
**Purpose**: Update dependent data when resource changes

**Payload**:
```python
{
    "resource_id": str,        # UUID of updated resource
    "changed_fields": list,    # List of field names that changed
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.updated", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "changed_fields": ["title", "content", "tags"],
    "timestamp": "2024-01-15T11:00:00Z"
})
```

**Subscribers React By**:
- **Quality**: Recomputing quality scores
- **Search**: Reindexing the resource

---

### resource.deleted

**Emitter**: Resources Module  
**Subscribers**: Collections, Annotations, Graph  
**Purpose**: Cascade cleanup when resource is removed

**Payload**:
```python
{
    "resource_id": str,        # UUID of deleted resource
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.deleted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T12:00:00Z"
})
```

**Subscribers React By**:
- **Collections**: Removing resource from all collections
- **Annotations**: Deleting all annotations on the resource
- **Graph**: Removing resource from knowledge graph

---

### collection.updated

**Emitter**: Collections Module  
**Subscribers**: Search  
**Purpose**: Reindex collection when metadata changes

**Payload**:
```python
{
    "collection_id": str,      # UUID of updated collection
    "resource_count": int,     # Number of resources in collection
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("collection.updated", {
    "collection_id": "456e7890-e89b-12d3-a456-426614174000",
    "resource_count": 42,
    "timestamp": "2024-01-15T13:00:00Z"
})
```

**Subscribers React By**:
- **Search**: Reindexing the collection

---

### collection.resource_added

**Emitter**: Collections Module  
**Subscribers**: Recommendations  
**Purpose**: Update user preferences based on collection additions

**Payload**:
```python
{
    "collection_id": str,      # UUID of collection
    "resource_id": str,        # UUID of added resource
    "user_id": str,            # UUID of user who added it
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("collection.resource_added", {
    "collection_id": "456e7890-e89b-12d3-a456-426614174000",
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T14:00:00Z"
})
```

**Subscribers React By**:
- **Recommendations**: Updating user profile with new preferences

---

### annotation.created

**Emitter**: Annotations Module  
**Subscribers**: Recommendations  
**Purpose**: Update user profile based on annotation activity

**Payload**:
```python
{
    "annotation_id": str,      # UUID of created annotation
    "resource_id": str,        # UUID of annotated resource
    "user_id": str,            # UUID of user who created it
    "text": str,               # Annotation text
    "tags": list,              # List of tags
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("annotation.created", {
    "annotation_id": "abc12345-e89b-12d3-a456-426614174000",
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "text": "Important concept for my research",
    "tags": ["machine-learning", "research"],
    "timestamp": "2024-01-15T15:00:00Z"
})
```

**Subscribers React By**:
- **Recommendations**: Updating user profile with annotation topics

---

### quality.computed

**Emitter**: Quality Module  
**Subscribers**: Monitoring  
**Purpose**: Track quality metrics across the system

**Payload**:
```python
{
    "resource_id": str,        # UUID of assessed resource
    "overall_score": float,    # Overall quality score (0-1)
    "dimensions": dict,        # Scores by dimension
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("quality.computed", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "overall_score": 0.85,
    "dimensions": {
        "completeness": 0.9,
        "accuracy": 0.8,
        "readability": 0.85
    },
    "timestamp": "2024-01-15T16:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Aggregating quality statistics

---

### quality.outlier_detected

**Emitter**: Quality Module  
**Subscribers**: Curation  
**Purpose**: Flag resources with anomalous quality for review

**Payload**:
```python
{
    "resource_id": str,        # UUID of outlier resource
    "outlier_score": float,    # How anomalous (higher = more anomalous)
    "reasons": list,           # List of reasons for outlier status
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("quality.outlier_detected", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "outlier_score": 0.95,
    "reasons": [
        "Completeness score 3 std devs below mean",
        "Readability score in bottom 5%"
    ],
    "timestamp": "2024-01-15T17:00:00Z"
})
```

**Subscribers React By**:
- **Curation**: Adding resource to review queue with high priority

---

### resource.classified

**Emitter**: Taxonomy Module  
**Subscribers**: Search  
**Purpose**: Update search index with classification results

**Payload**:
```python
{
    "resource_id": str,        # UUID of classified resource
    "classifications": list,   # List of classification results
    "model_version": str,      # ML model version used
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.classified", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "classifications": [
        {"category": "cs.AI", "confidence": 0.92},
        {"category": "cs.LG", "confidence": 0.85}
    ],
    "model_version": "v2.0",
    "timestamp": "2024-01-15T18:00:00Z"
})
```

**Subscribers React By**:
- **Search**: Updating search index with classification tags

---

### citation.extracted

**Emitter**: Graph Module  
**Subscribers**: Monitoring  
**Purpose**: Track citation network growth

**Payload**:
```python
{
    "resource_id": str,        # UUID of resource with citations
    "citation_count": int,     # Number of citations found
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("citation.extracted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "citation_count": 15,
    "timestamp": "2024-01-15T19:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Tracking citation network statistics

---

### recommendation.generated

**Emitter**: Recommendations Module  
**Subscribers**: Monitoring  
**Purpose**: Track recommendation quality and usage

**Payload**:
```python
{
    "user_id": str,            # UUID of user receiving recommendations
    "count": int,              # Number of recommendations generated
    "strategy": str,           # Strategy used (e.g., "hybrid")
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("recommendation.generated", {
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "count": 10,
    "strategy": "hybrid",
    "timestamp": "2024-01-15T20:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Aggregating recommendation metrics

---

### metadata.extracted

**Emitter**: Scholarly Module  
**Subscribers**: Monitoring  
**Purpose**: Track metadata extraction completeness

**Payload**:
```python
{
    "resource_id": str,        # UUID of resource
    "metadata_fields": list,   # List of extracted field names
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("metadata.extracted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "metadata_fields": ["authors", "abstract", "doi", "publication_date"],
    "timestamp": "2024-01-15T21:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Tracking metadata completeness statistics

---

## Event Flow Diagrams

### Resource Creation Flow

```
User creates resource via API
        ↓
┌───────────────────┐
│ Resources Module  │
│ ├─ Save to DB     │
│ ├─ Emit event     │
│ └─ Return response│
└───────────────────┘
        │
        │ resource.created
        ↓
┌───────────────────────────────────────────────────────┐
│              Event Bus Distribution                    │
└───────────────────────────────────────────────────────┘
        │
        ├──────────┬──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Quality │ │Taxonomy│ │ Graph  │ │Scholarly│ │Annot.  │
   │        │ │        │ │        │ │        │ │        │
   │Compute │ │Auto-   │ │Extract │ │Extract │ │(Ready) │
   │quality │ │classify│ │citations│ │metadata│ │        │
   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
        │          │          │          │
        ↓          ↓          ↓          ↓
   quality.   resource.  citation.  metadata.
   computed   classified extracted  extracted
```

### Quality Outlier Detection Flow

```
Quality Module computes scores
        ↓
Detects outlier (score > threshold)
        ↓
┌───────────────────┐
│  Quality Module   │
│ Emit event        │
└───────────────────┘
        │
        │ quality.outlier_detected
        ↓
┌───────────────────┐
│ Curation Module   │
│ ├─ Add to queue   │
│ ├─ Set priority   │
│ └─ Notify curator │
└───────────────────┘
        │
        │ curation.reviewed (when reviewed)
        ↓
┌───────────────────┐
│ Monitoring Module │
│ Track metrics     │
└───────────────────┘
```

### User Interaction Flow

```
User adds annotation
        ↓
┌───────────────────┐
│Annotations Module │
│ ├─ Save annotation│
│ ├─ Emit event     │
│ └─ Return response│
└───────────────────┘
        │
        │ annotation.created
        ↓
┌───────────────────────┐
│ Recommendations Module│
│ ├─ Update profile     │
│ ├─ Adjust preferences │
│ ├─ Emit event         │
│ └─ Refresh recs       │
└───────────────────────┘
        │
        │ user.profile_updated
        ↓
┌───────────────────┐
│ Monitoring Module │
│ Track engagement  │
└───────────────────┘
```

### Resource Deletion Cascade

```
User deletes resource
        ↓
┌───────────────────┐
│ Resources Module  │
│ ├─ Delete from DB │
│ ├─ Emit event     │
│ └─ Return 204     │
└───────────────────┘
        │
        │ resource.deleted
        ↓
┌───────────────────────────────────────┐
│       Event Bus Distribution          │
└───────────────────────────────────────┘
        │
        ├──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Collect.│ │Annot.  │ │ Graph  │ │Monitor.│
   │        │ │        │ │        │ │        │
   │Remove  │ │Delete  │ │Remove  │ │Track   │
   │from    │ │all     │ │from    │ │deletion│
   │colls   │ │annots  │ │graph   │ │        │
   └────────┘ └────────┘ └────────┘ └────────┘
```

---

## Best Practices

### For Event Emitters

1. **Emit after commit**: Always emit events AFTER database commits succeed
   ```python
   # Good
   db.commit()
   event_bus.emit("resource.created", payload)
   
   # Bad - event emitted before commit
   event_bus.emit("resource.created", payload)
   db.commit()  # Could fail!
   ```

2. **Include sufficient context**: Provide enough information for subscribers
   ```python
   # Good - includes all relevant data
   event_bus.emit("resource.created", {
       "resource_id": str(resource.id),
       "title": resource.title,
       "content_type": resource.content_type,
       "timestamp": datetime.now(timezone.utc).isoformat()
   })
   
   # Bad - insufficient context
   event_bus.emit("resource.created", {
       "resource_id": str(resource.id)
   })
   ```

3. **Use ISO 8601 timestamps**: Always include timestamps in ISO 8601 format
   ```python
   from datetime import datetime, timezone
   
   "timestamp": datetime.now(timezone.utc).isoformat()
   ```

4. **Don't emit on failures**: Only emit events for successful operations
   ```python
   try:
       resource = create_resource(data)
       db.commit()
       event_bus.emit("resource.created", payload)
   except Exception as e:
       db.rollback()
       # Don't emit event on failure
       raise
   ```

### For Event Subscribers

1. **Create fresh database sessions**: Always create new sessions in handlers
   ```python
   def handle_resource_created(payload: dict):
       from app.shared.database import SessionLocal
       
       db = SessionLocal()  # Fresh session
       try:
           # Process event
           pass
       finally:
           db.close()  # Always close
   ```

2. **Catch all exceptions**: Don't let handler failures affect other handlers
   ```python
   def handle_event(payload: dict):
       try:
           # Process event
           pass
       except Exception as e:
           logger.error(f"Handler error: {e}", exc_info=True)
           # Don't re-raise - let other handlers continue
       finally:
           db.close()
   ```

3. **Keep handlers fast**: Aim for <100ms execution time
   ```python
   # Good - quick processing
   def handle_event(payload: dict):
       resource_id = payload["resource_id"]
       update_cache(resource_id)  # Fast operation
   
   # Bad - slow processing
   def handle_event(payload: dict):
       resource_id = payload["resource_id"]
       recompute_all_embeddings()  # Slow! Use Celery instead
   ```

4. **Make handlers idempotent**: Safe to run multiple times
   ```python
   def handle_resource_created(payload: dict):
       resource_id = payload["resource_id"]
       
       # Check if already processed
       if already_processed(resource_id):
           return
       
       # Process event
       process_resource(resource_id)
       mark_as_processed(resource_id)
   ```

5. **Log all processing**: Include event type and payload in logs
   ```python
   def handle_event(payload: dict):
       logger.info(f"Processing event: {payload}")
       try:
           # Process
           logger.info(f"Successfully processed: {payload}")
       except Exception as e:
           logger.error(f"Failed to process: {payload}", exc_info=True)
   ```

### Event Payload Guidelines

1. **Use UUIDs as strings**: Always convert UUIDs to strings
   ```python
   "resource_id": str(resource.id)  # Good
   "resource_id": resource.id       # Bad - not JSON serializable
   ```

2. **Keep payloads small**: Don't include large content
   ```python
   # Good - reference only
   "resource_id": "123e4567-e89b-12d3-a456-426614174000"
   
   # Bad - includes full content
   "content": "..." # 10MB of text
   ```

3. **Use consistent field names**: Follow naming conventions
   ```python
   # Good - snake_case
   "resource_id", "user_id", "created_at"
   
   # Bad - mixed case
   "resourceId", "userId", "createdAt"
   ```

4. **Include metadata**: Add context for debugging
   ```python
   {
       "resource_id": "...",
       "timestamp": "2024-01-15T10:00:00Z",
       "source": "api",  # Where did this come from?
       "user_id": "..."  # Who triggered it?
   }
   ```

---

## Monitoring Events

### Event Bus Metrics

Check event bus health and metrics:

```bash
curl http://localhost:8000/monitoring/events
```

Response:
```json
{
  "events_emitted": 1523,
  "events_delivered": 4569,
  "handler_errors": 3,
  "event_types": {
    "resource.created": 234,
    "resource.updated": 1289,
    "quality.computed": 234,
    "resource.classified": 234
  },
  "latency_ms": {
    "p50": 0.8,
    "p95": 2.3,
    "p99": 5.1
  }
}
```

### Event History

View recent events:

```bash
curl http://localhost:8000/monitoring/events/history?limit=10
```

Response:
```json
{
  "events": [
    {
      "type": "resource.created",
      "timestamp": "2024-01-15T10:00:00Z",
      "payload": {"resource_id": "..."},
      "handlers_called": 5,
      "latency_ms": 1.2
    }
  ]
}
```

### Debugging Event Issues

1. **Check if event is being emitted**:
   ```python
   # Add logging in emitter
   logger.info(f"Emitting event: {event_type}")
   event_bus.emit(event_type, payload)
   ```

2. **Check if handlers are registered**:
   ```bash
   curl http://localhost:8000/monitoring/events
   # Look at handler_count per event type
   ```

3. **Check handler errors**:
   ```bash
   curl http://localhost:8000/monitoring/events/history
   # Look for events with errors
   ```

4. **Enable debug logging**:
   ```python
   # In app/shared/event_bus.py
   logger.setLevel(logging.DEBUG)
   ```

---

## Related Documentation

- [Architecture Overview](overview.md) - System architecture
- [Event System](event-system.md) - Event bus implementation details
- [Module Documentation](modules.md) - Module-specific event usage
- [Migration Guide](../MIGRATION_GUIDE.md) - Event-driven migration patterns
- [Development Workflows](../guides/workflows.md) - Working with events

---

*Last Updated: Phase 14 Complete - December 2024*
