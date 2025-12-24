# Architecture Decision Records

Key architectural decisions for Neo Alexandria 2.0.

## ADR-001: Vertical Slice Architecture

**Status:** Accepted (Phase 13.5)

**Context:**
The original layered architecture (routers → services → models) led to:
- Tight coupling between components
- Circular import issues
- Difficult testing
- Hard to understand feature boundaries

**Decision:**
Adopt vertical slice architecture where each feature is a self-contained module with all layers.

**Consequences:**
- ✅ High cohesion within modules
- ✅ Low coupling between modules
- ✅ Easier to understand and test
- ✅ Modules can be extracted to microservices
- ⚠️ Some code duplication between modules
- ⚠️ Requires discipline to maintain boundaries

---

## ADR-002: Event-Driven Communication

**Status:** Accepted (Phase 12.5)

**Context:**
Direct service-to-service calls created:
- Circular dependencies
- Tight coupling
- Difficult to add new features

**Decision:**
Use publish-subscribe event bus for inter-module communication.

**Consequences:**
- ✅ Loose coupling between modules
- ✅ Easy to add new subscribers
- ✅ Supports async processing
- ⚠️ Eventual consistency (not immediate)
- ⚠️ Harder to trace execution flow
- ⚠️ Need to handle event failures

---

## ADR-003: Dual Database Support

**Status:** Accepted (Phase 13)

**Context:**
SQLite is convenient for development but has limitations:
- Single writer (no concurrent writes)
- No advanced indexing
- Not suitable for production

**Decision:**
Support both SQLite (development) and PostgreSQL (production) with automatic detection.

**Consequences:**
- ✅ Easy local development
- ✅ Production-grade database option
- ✅ Automatic configuration
- ⚠️ Must maintain compatibility
- ⚠️ Some features PostgreSQL-only
- ⚠️ Migration scripts needed

---

## ADR-004: Domain Objects for Business Logic

**Status:** Accepted (Phase 11)

**Context:**
Business logic was scattered across services with primitive types, making it hard to:
- Validate business rules
- Reuse logic
- Test in isolation

**Decision:**
Create domain objects (value objects, entities) to encapsulate business logic.

**Consequences:**
- ✅ Centralized validation
- ✅ Reusable business logic
- ✅ Self-documenting code
- ✅ Easier testing
- ⚠️ More classes to maintain
- ⚠️ Mapping between layers

---

## ADR-005: Hybrid Search Strategy

**Status:** Accepted (Phase 4, enhanced Phase 8)

**Context:**
Pure keyword search misses semantic meaning. Pure vector search misses exact matches.

**Decision:**
Implement hybrid search combining:
- FTS5 keyword search (BM25)
- Dense vector search (semantic)
- Sparse vector search (SPLADE) - Phase 8
- Reciprocal Rank Fusion for combining results

**Consequences:**
- ✅ Best of both approaches
- ✅ Configurable weighting
- ✅ Better search quality
- ⚠️ Higher latency
- ⚠️ More complex implementation
- ⚠️ Requires embedding generation

---

## ADR-006: Aggregate Embeddings for Collections

**Status:** Accepted (Phase 7)

**Context:**
Collections needed semantic representation for:
- Finding similar collections
- Recommending resources to add
- Collection-based search

**Decision:**
Compute aggregate embedding as normalized mean of member resource embeddings.

**Consequences:**
- ✅ Enables collection similarity
- ✅ Supports recommendations
- ✅ Simple algorithm
- ⚠️ Must recompute on membership changes
- ⚠️ Large collections may dilute signal

---

## ADR-007: Multi-Dimensional Quality Assessment

**Status:** Accepted (Phase 9)

**Context:**
Single quality score didn't capture different aspects of resource quality.

**Decision:**
Implement 5-dimensional quality assessment:
- Accuracy (30%)
- Completeness (25%)
- Consistency (20%)
- Timeliness (15%)
- Relevance (10%)

**Consequences:**
- ✅ Granular quality insights
- ✅ Actionable improvement suggestions
- ✅ Configurable weights
- ⚠️ More complex computation
- ⚠️ Requires more storage

---

## ADR-008: Strategy Pattern for Recommendations

**Status:** Accepted (Phase 10-11)

**Context:**
Different recommendation approaches work better for different scenarios.

**Decision:**
Use strategy pattern with multiple recommendation strategies:
- Collaborative filtering
- Content-based
- Graph-based
- Hybrid (combines all)

**Consequences:**
- ✅ Flexible recommendation system
- ✅ Easy to add new strategies
- ✅ Can tune per user/context
- ⚠️ More complex architecture
- ⚠️ Need to balance strategies

---

## ADR-009: Materialized Paths for Taxonomy

**Status:** Accepted (Phase 8.5)

**Context:**
Hierarchical taxonomy queries (ancestors, descendants) were slow with recursive queries.

**Decision:**
Use materialized path pattern storing full path in each node (e.g., `/science/computer-science/ml`).

**Consequences:**
- ✅ O(1) ancestor queries
- ✅ O(1) descendant queries via LIKE
- ✅ Simple breadcrumb generation
- ⚠️ Must update paths on move
- ⚠️ Path length limits

---

## ADR-010: Async Ingestion Pipeline

**Status:** Accepted (Phase 3.5)

**Context:**
Content ingestion involves slow operations:
- HTTP fetching
- PDF extraction
- AI summarization
- Embedding generation

**Decision:**
Make ingestion asynchronous with status tracking.

**Consequences:**
- ✅ Fast API response
- ✅ Can process in background
- ✅ Supports batch ingestion
- ⚠️ Need status polling
- ⚠️ Error handling complexity

---

## Decision Template

```markdown
## ADR-XXX: [Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]

**Context:**
[What is the issue that we're seeing that is motivating this decision?]

**Decision:**
[What is the change that we're proposing and/or doing?]

**Consequences:**
[What becomes easier or more difficult to do because of this change?]
- ✅ Positive consequence
- ⚠️ Trade-off or risk
```

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [Modules](modules.md) - Vertical slice details
- [Event System](event-system.md) - Event-driven communication
