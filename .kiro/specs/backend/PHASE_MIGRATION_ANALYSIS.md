# Phase 1-13 to Phase 13.5-14 Migration Analysis

**Date**: December 26, 2025  
**Purpose**: Identify features from Phases 1-13 that haven't been fully migrated to the new modular architecture (Phases 13.5-14)

---

## Executive Summary

### Migration Status: 🟡 **PARTIALLY COMPLETE**

- ✅ **3 modules fully migrated**: Collections, Resources, Search
- 🟡 **9 modules partially migrated**: Have module structure but old routers still exist
- ❌ **0 modules missing**: All phase features have at least skeleton modules

### Key Finding

All features from Phases 1-13 have been **structurally migrated** (module directories exist with routers), but many still have **duplicate implementations** in both the old `app/routers/` directory and the new `app/modules/` directory.

---

## Phase-by-Phase Feature Analysis

### Phase 1: Core Resource Management ✅ MIGRATED
**Migration**: Phase 13.5 → `app/modules/resources/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Resource CRUD | `app/routers/resources.py` | `app/modules/resources/router.py` | ✅ Migrated |
| Resource ingestion | `app/services/resource_service.py` | `app/modules/resources/service.py` | ✅ Migrated |
| Resource models | `app/database/models.py` | `app/modules/resources/model.py` | ✅ Migrated |

**Endpoints**: 8 endpoints migrated
- POST /resources
- GET /resources
- GET /resources/{resource_id}
- GET /resources/{resource_id}/status
- PUT /resources/{resource_id}
- DELETE /resources/{resource_id}
- PUT /resources/{resource_id}/classify
- GET /resources/health

---

### Phase 2: Curation System 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/curation/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Review queue | `app/routers/curation.py` | `app/modules/curation/router.py` | 🟡 Both exist |
| Batch operations | `app/routers/curation.py` | `app/modules/curation/router.py` | 🟡 Both exist |
| Quality analysis | `app/routers/curation.py` | `app/modules/curation/service.py` | 🟡 Both exist |

**Endpoints**: 5 endpoints
- GET /curation/review-queue
- POST /curation/batch-update
- GET /curation/quality-analysis/{resource_id}
- GET /curation/low-quality
- POST /curation/bulk-quality-check

**Status**: Module structure exists but old router still in use

---

### Phase 3: Basic Search ✅ MIGRATED
**Migration**: Phase 13.5 → `app/modules/search/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Keyword search | `app/routers/search.py` | `app/modules/search/router.py` | ✅ Migrated |
| Semantic search | `app/services/search_service.py` | `app/modules/search/service.py` | ✅ Migrated |
| Search strategies | `app/services/search_service.py` | `app/modules/search/service.py` | ✅ Migrated |

**Endpoints**: 6 endpoints migrated
- POST /search
- GET /search/three-way-hybrid
- GET /search/compare-methods
- POST /search/evaluate
- POST /admin/sparse-embeddings/generate
- GET /search/health

---

### Phase 4: Content Extraction ✅ INTEGRATED
**Migration**: Integrated into Resources module

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| HTML extraction | `app/utils/content_extractor.py` | `app/utils/content_extractor.py` | ✅ Shared utility |
| PDF extraction | `app/utils/content_extractor.py` | `app/utils/content_extractor.py` | ✅ Shared utility |
| Metadata extraction | `app/services/metadata_extractor.py` | `app/modules/scholarly/extractor.py` | ✅ Migrated |

**Status**: Utilities remain shared, extraction integrated into resource ingestion

---

### Phase 5: Knowledge Graph (Basic) 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/graph/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Graph relationships | `app/routers/graph.py` | `app/modules/graph/router.py` | 🟡 Both exist |
| Neighbor queries | `app/services/graph_service.py` | `app/modules/graph/service.py` | 🟡 Both exist |

**Endpoints**: 2 endpoints
- GET /graph/resource/{resource_id}/neighbors
- GET /graph/overview

**Status**: Module structure exists but old router still in use

---

### Phase 6: Citation Network ✅ MIGRATED
**Migration**: Phase 14 → `app/modules/graph/citations.py`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Citation extraction | `app/routers/citations.py` | `app/modules/graph/citations_router.py` | ✅ Migrated |
| Citation graph | `app/services/citation_service.py` | `app/modules/graph/citations.py` | ✅ Migrated |
| Citation importance | `app/routers/citations.py` | `app/modules/graph/citations_router.py` | ✅ Migrated |

**Endpoints**: 5 endpoints migrated to graph module
- GET /citations/resources/{resource_id}/citations
- GET /citations/graph/citations
- POST /citations/resources/{resource_id}/citations/extract
- POST /citations/resolve
- POST /citations/importance/compute

**Database**: `Citation` table (migration: `23fa08826047_add_citation_table_phase6.py`)

---

### Phase 6.5: Scholarly Metadata 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/scholarly/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Equation parsing | `app/routers/scholarly.py` | `app/modules/scholarly/router.py` | 🟡 Both exist |
| Table extraction | `app/routers/scholarly.py` | `app/modules/scholarly/extractor.py` | 🟡 Both exist |
| Metadata completeness | `app/routers/scholarly.py` | `app/modules/scholarly/router.py` | 🟡 Both exist |

**Endpoints**: 5 endpoints
- GET /scholarly/resources/{resource_id}/metadata
- GET /scholarly/resources/{resource_id}/equations
- GET /scholarly/resources/{resource_id}/tables
- POST /scholarly/resources/{resource_id}/metadata/extract
- GET /scholarly/metadata/completeness-stats

**Database**: Scholarly metadata fields (migration: `c15f564b1ccd_add_scholarly_metadata_fields_phase6_5.py`)

**Status**: Module structure exists but old router still in use

---

### Phase 7: Collection Management ✅ MIGRATED
**Migration**: Phase 13.5 → `app/modules/collections/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Collection CRUD | `app/routers/collections.py` | `app/modules/collections/router.py` | ✅ Migrated |
| Collection service | `app/services/collection_service.py` | `app/modules/collections/service.py` | ✅ Migrated |
| Collection models | `app/database/models.py` | `app/modules/collections/model.py` | ✅ Migrated |

**Endpoints**: 8 endpoints migrated
- POST /collections
- GET /collections
- GET /collections/{collection_id}
- PUT /collections/{collection_id}
- DELETE /collections/{collection_id}
- PUT /collections/{collection_id}/resources
- GET /collections/{collection_id}/recommendations
- GET /collections/health

**Database**: `Collection`, `CollectionResource` tables (migration: `d4a8e9f1b2c3_add_collections_tables_phase7.py`)

---

### Phase 7.5: Annotation System 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/annotations/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Annotation CRUD | `app/routers/annotations.py` | `app/modules/annotations/router.py` | 🟡 Both exist |
| Annotation search | `app/routers/annotations.py` | `app/modules/annotations/router.py` | 🟡 Both exist |
| Annotation export | `app/routers/annotations.py` | `app/modules/annotations/router.py` | 🟡 Both exist |

**Endpoints**: 11 endpoints
- POST /resources/{resource_id}/annotations
- GET /resources/{resource_id}/annotations
- GET /annotations
- GET /annotations/{annotation_id}
- PUT /annotations/{annotation_id}
- DELETE /annotations/{annotation_id}
- GET /annotations/search/fulltext
- GET /annotations/search/semantic
- GET /annotations/search/tags
- GET /annotations/export/markdown
- GET /annotations/export/json

**Database**: `Annotation` table (migration: `e5b9f2c3d4e5_add_annotations_table_phase7_5.py`)

**Status**: Module structure exists but old router still in use

---

### Phase 8: Three-Way Hybrid Search ✅ MIGRATED
**Migration**: Phase 13.5 → `app/modules/search/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| FTS5 search | `app/services/search_service.py` | `app/modules/search/service.py` | ✅ Migrated |
| Dense vector search | `app/services/embedding_service.py` | `app/shared/embeddings.py` | ✅ Shared |
| Sparse vector (SPLADE) | `app/services/sparse_embedding_service.py` | `app/modules/search/service.py` | ✅ Migrated |
| RRF fusion | `app/services/reciprocal_rank_fusion_service.py` | `app/modules/search/service.py` | ✅ Migrated |

**Database**: Sparse embedding fields (migration: `10bf65d53f59_add_sparse_embedding_fields_phase8.py`)

---

### Phase 8.5: ML Classification & Taxonomy 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/taxonomy/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Taxonomy tree | `app/routers/taxonomy.py` | `app/modules/taxonomy/router.py` | 🟡 Both exist |
| ML classification | `app/routers/classification.py` | `app/modules/taxonomy/router.py` | 🟡 Both exist |
| Active learning | `app/routers/taxonomy.py` | `app/modules/taxonomy/router.py` | 🟡 Both exist |

**Endpoints**: 11 endpoints
- POST /taxonomy/nodes
- PUT /taxonomy/nodes/{node_id}
- DELETE /taxonomy/nodes/{node_id}
- POST /taxonomy/nodes/{node_id}/move
- GET /taxonomy/tree
- GET /taxonomy/nodes/{node_id}/ancestors
- GET /taxonomy/nodes/{node_id}/descendants
- POST /taxonomy/classify/{resource_id}
- GET /taxonomy/active-learning/uncertain
- POST /taxonomy/active-learning/feedback
- POST /taxonomy/train

**Database**: `TaxonomyNode`, `ResourceClassification` tables (migration: `f6c3d5e7a8b9_add_taxonomy_tables_phase8_5.py`)

**Status**: Module structure exists but old routers still in use

---

### Phase 9: Quality Assessment 🟡 PARTIAL
**Migration**: Phase 14 → `app/modules/quality/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Quality scoring | `app/routers/quality.py` | `app/modules/quality/router.py` | 🟡 Both exist |
| Quality dimensions | `app/services/quality_service.py` | `app/modules/quality/service.py` | 🟡 Both exist |
| Quality monitoring | `app/routers/quality.py` | `app/modules/quality/router.py` | 🟡 Both exist |

**Endpoints**: 9 endpoints
- GET /quality/resources/{resource_id}/quality-details
- POST /quality/recalculate
- GET /quality/outliers
- GET /quality/degradation
- POST /quality/summaries/{resource_id}/evaluate
- GET /quality/distribution
- GET /quality/trends
- GET /quality/dimensions
- GET /quality/review-queue

**Database**: Quality assessment fields (migration: `a1b2c3d4e5f6_add_quality_assessment_fields_phase9.py`)

**Status**: Module structure exists but old router still in use

---

### Phase 10: Advanced Graph Intelligence ✅ MIGRATED
**Migration**: Phase 14 → `app/modules/graph/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Literature-based discovery | `app/routers/discovery.py` | `app/modules/graph/discovery_router.py` | ✅ Migrated |
| Graph embeddings | `app/services/graph_embeddings_service.py` | `app/modules/graph/service.py` | ✅ Migrated |
| Hypothesis generation | `app/routers/discovery.py` | `app/modules/graph/discovery_router.py` | ✅ Migrated |

**Endpoints**: 5 endpoints migrated
- GET /discovery/open
- POST /discovery/closed
- GET /discovery/graph/resources/{resource_id}/neighbors
- GET /discovery/hypotheses
- POST /discovery/hypotheses/{hypothesis_id}/validate

**Database**: Graph intelligence tables (migration: `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`)

---

### Phase 11: Hybrid Recommendation Engine ✅ MIGRATED
**Migration**: Phase 14 → `app/modules/recommendations/`

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Collaborative filtering | `app/routers/recommendation.py` | `app/modules/recommendations/router.py` | ✅ Migrated |
| NCF model | `app/services/ncf_service.py` | `app/modules/recommendations/ncf.py` | ✅ Migrated |
| User profiles | `app/services/user_profile_service.py` | `app/modules/recommendations/service.py` | ✅ Migrated |

**Endpoints**: 6 endpoints migrated
- GET /recommendations
- POST /recommendations/interactions
- GET /recommendations/profile
- PUT /recommendations/profile
- POST /recommendations/feedback
- GET /recommendations/metrics

**Database**: User profiles, interactions (migration: `7c607a7908f4_add_user_profiles_interactions_phase11.py`)

**Note**: Old `app/routers/recommendation.py` still exists but appears to be legacy

---

### Phase 12: Fowler Refactoring ✅ COMPLETE
**Migration**: Architectural improvements, no new features

| Feature | Status |
|---------|--------|
| Extract Method | ✅ Applied throughout codebase |
| Replace Conditional with Polymorphism | ✅ Applied in search strategies |
| Introduce Parameter Object | ✅ Applied in domain objects |

**Status**: Refactoring patterns applied, no migration needed

---

### Phase 12.5: Event-Driven Architecture ✅ COMPLETE
**Migration**: Foundation for Phase 13.5

| Feature | Old Location | New Location | Status |
|---------|-------------|--------------|--------|
| Event bus | N/A | `app/shared/event_bus.py` | ✅ Created |
| Event types | N/A | `app/events/event_types.py` | ✅ Created |
| Event hooks | N/A | `app/events/hooks.py` | ✅ Created |

**Status**: Event system fully implemented and used by all modules

---

### Phase 13: PostgreSQL Migration ✅ COMPLETE
**Migration**: Database infrastructure, no feature migration needed

| Feature | Status |
|---------|--------|
| PostgreSQL support | ✅ Complete |
| SQLite compatibility | ✅ Maintained |
| Connection pooling | ✅ Complete |
| FTS abstraction | ✅ Complete |
| Migration tools | ✅ Complete |

**Status**: All database features working in both old and new architecture

---

## Module Migration Status Summary

### ✅ Fully Migrated (3 modules)
1. **Collections** - Phase 7 → `app/modules/collections/`
2. **Resources** - Phase 1 → `app/modules/resources/`
3. **Search** - Phase 3, 8 → `app/modules/search/`

### 🟡 Partially Migrated (9 modules)
Module structure exists, but old routers still in use:

1. **Annotations** - Phase 7.5 → `app/modules/annotations/`
   - Old router: `app/routers/annotations.py` ❌ Still exists
   - New router: `app/modules/annotations/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

2. **Authority** - Phase 8.5 → `app/modules/authority/`
   - Old router: `app/routers/authority.py` ❌ Still exists
   - New router: `app/modules/authority/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

3. **Curation** - Phase 2 → `app/modules/curation/`
   - Old router: `app/routers/curation.py` ❌ Still exists
   - New router: `app/modules/curation/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

4. **Graph** - Phase 5, 6, 10 → `app/modules/graph/`
   - Old routers: `app/routers/graph.py`, `citations.py`, `discovery.py` ❌ Still exist
   - New routers: `app/modules/graph/router.py`, `citations_router.py`, `discovery_router.py` ✅ Exist
   - **Action needed**: Remove old routers, update main.py

5. **Monitoring** - Phase 12.5 → `app/modules/monitoring/`
   - Old router: `app/routers/monitoring.py` ❌ Still exists
   - New router: `app/modules/monitoring/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

6. **Quality** - Phase 9 → `app/modules/quality/`
   - Old router: `app/routers/quality.py` ❌ Still exists
   - New router: `app/modules/quality/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

7. **Recommendations** - Phase 11 → `app/modules/recommendations/`
   - Old routers: `app/routers/recommendation.py`, `recommendations.py` ❌ Still exist
   - New router: `app/modules/recommendations/router.py` ✅ Exists
   - **Action needed**: Remove old routers, update main.py

8. **Scholarly** - Phase 6.5 → `app/modules/scholarly/`
   - Old router: `app/routers/scholarly.py` ❌ Still exists
   - New router: `app/modules/scholarly/router.py` ✅ Exists
   - **Action needed**: Remove old router, update main.py

9. **Taxonomy** - Phase 8.5 → `app/modules/taxonomy/`
   - Old routers: `app/routers/taxonomy.py`, `classification.py` ❌ Still exist
   - New router: `app/modules/taxonomy/router.py` ✅ Exists
   - **Action needed**: Remove old routers, update main.py

---

## Recommended Actions

### Priority 1: Complete Module Migration (Phase 14)

Create a spec for completing the vertical slice refactor:

**Spec**: `.kiro/specs/backend/phase14-complete-vertical-slice-refactor/`

**Tasks**:
1. ✅ Verify all 9 partially migrated modules have complete implementations
2. ❌ Update `app/main.py` to use new module routers
3. ❌ Remove old routers from `app/routers/`
4. ❌ Update all tests to use new module structure
5. ❌ Update documentation to reflect new architecture
6. ❌ Run full test suite to verify no regressions

### Priority 2: Clean Up Legacy Code

**Tasks**:
1. Remove `app/routers/` directory (after migration complete)
2. Remove duplicate service files
3. Update imports throughout codebase
4. Clean up circular dependency workarounds

### Priority 3: Documentation Updates

**Tasks**:
1. Update API documentation to reflect module structure
2. Update architecture diagrams
3. Create module-specific documentation
4. Update developer guide

---

## Migration Checklist

### For Each Module:

- [ ] **Annotations Module**
  - [ ] Verify router.py has all endpoints
  - [ ] Verify service.py has all business logic
  - [ ] Verify model.py has all database models
  - [ ] Verify schema.py has all Pydantic schemas
  - [ ] Verify handlers.py has all event handlers
  - [ ] Update main.py to include module router
  - [ ] Remove old router from app/routers/
  - [ ] Update tests
  - [ ] Update documentation

- [ ] **Authority Module**
  - [ ] (Same checklist as above)

- [ ] **Curation Module**
  - [ ] (Same checklist as above)

- [ ] **Graph Module**
  - [ ] (Same checklist as above)

- [ ] **Monitoring Module**
  - [ ] (Same checklist as above)

- [ ] **Quality Module**
  - [ ] (Same checklist as above)

- [ ] **Recommendations Module**
  - [ ] (Same checklist as above)

- [ ] **Scholarly Module**
  - [ ] (Same checklist as above)

- [ ] **Taxonomy Module**
  - [ ] (Same checklist as above)

---

## Conclusion

All features from Phases 1-13 have been **structurally migrated** to the new modular architecture, but the migration is **incomplete**:

- ✅ **Structure**: All 12 modules exist with proper structure
- 🟡 **Implementation**: 3 modules fully migrated, 9 partially migrated
- ❌ **Cleanup**: Old routers still exist and may be in use

**Next Step**: Create a comprehensive spec for Phase 14 to complete the vertical slice refactor by:
1. Verifying all module implementations are complete
2. Switching main.py to use new module routers
3. Removing old routers
4. Updating tests and documentation

This will complete the architectural transformation started in Phase 13.5.
