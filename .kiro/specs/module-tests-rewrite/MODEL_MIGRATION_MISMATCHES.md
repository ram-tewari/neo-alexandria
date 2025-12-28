# Critical: Model-Migration Schema Mismatches

## Date: December 26, 2024

## Overview

Multiple models in `backend/app/database/models.py` do NOT match their migration schemas. This causes runtime errors, test failures, and data integrity issues.

## Status Summary

| Model | Status | Priority |
|-------|--------|----------|
| Annotation | ✅ FIXED | Critical |
| Citation | ❌ MISMATCH | High |
| GraphEdge | ❌ MISMATCH | High |
| GraphEmbedding | ❌ MISMATCH | High |
| DiscoveryHypothesis | ❌ MISMATCH | High |
| TaxonomyNode | ❌ MISMATCH | High |
| ResourceTaxonomy | ❌ MISMATCH | High |
| Resource | ✅ OK | - |
| Collection | ✅ OK | - |
| User | ✅ OK | - |

## Detailed Mismatches

### 1. Annotation Model ✅ FIXED

**Migration:** `e5b9f2c3d4e5_add_annotations_table_phase7_5.py`

**Fixed Fields:**
- ✅ `start_offset`, `end_offset`, `highlighted_text`, `note`
- ✅ `is_shared` (INTEGER), `context_before`, `context_after`
- ✅ `embedding`, `collection_ids`

### 2. Citation Model ❌ MISMATCH

**Migration:** `23fa08826047_add_citation_table_phase6.py`

**Migration Schema:**
```python
- source_resource_id (UUID/String(36))
- target_resource_id (UUID/String(36), nullable)
- target_url (String, NOT NULL)
- citation_type (String, default='reference')
- context_snippet (Text, nullable)
- position (Integer, nullable)
- importance_score (Float, nullable)
```

**Current Model:**
```python
- source_id (UUID)
- target_id (UUID)
- citation_type (String(50), nullable)
- context (Text, nullable)
- confidence (Float, default=1.0)
```

**Issues:**
- Field names don't match (`source_id` vs `source_resource_id`)
- Missing `target_url`, `position`, `importance_score`
- Has `confidence` instead of `importance_score`
- `context` vs `context_snippet`

### 3. GraphEdge Model ❌ MISMATCH

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

**Migration Schema:**
```python
- metadata (Text, nullable)
- created_by (String(100), NOT NULL)
- confidence (Float, nullable)
```

**Current Model:**
```python
- metadata (JSON, nullable)
- weight (Float, default=1.0)
```

**Issues:**
- `metadata` type mismatch (Text vs JSON)
- Missing `created_by` and `confidence`
- Has `weight` field not in migration

### 4. GraphEmbedding Model ❌ MISMATCH

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

**Migration Schema:**
```python
- structural_embedding (JSON, nullable)
- fusion_embedding (JSON, nullable)
- embedding_method (String(50), NOT NULL)
- embedding_version (String(20), NOT NULL)
- hnsw_index_id (Integer, nullable)
```

**Current Model:**
```python
- embedding (JSON, NOT NULL)
- algorithm (String(50), NOT NULL)
```

**Issues:**
- Single `embedding` vs two separate embeddings
- `algorithm` vs `embedding_method`
- Missing `embedding_version`, `hnsw_index_id`

### 5. DiscoveryHypothesis Model ❌ MISMATCH

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

**Migration Schema:**
```python
- a_resource_id (UUID, NOT NULL)
- c_resource_id (UUID, NOT NULL)
- b_resource_ids (Text, NOT NULL)
- hypothesis_type (String(20), NOT NULL)
- plausibility_score (Float, NOT NULL)
- path_strength (Float, NOT NULL)
- path_length (Integer, NOT NULL)
- common_neighbors (Integer, default=0)
- discovered_at (DateTime)
- user_id (String(255), nullable)
- is_validated (Integer, nullable)
- validation_notes (Text, nullable)
```

**Current Model:**
```python
- hypothesis_text (Text, NOT NULL)
- confidence (Float, NOT NULL)
- supporting_resources (JSON, default=[])
- status (String(20), default="pending")
```

**Issues:**
- Completely different schema
- Missing A-B-C resource structure
- Missing path analysis fields
- Different purpose/design

### 6. TaxonomyNode Model ❌ MISMATCH

**Migration:** `f6c3d5e7a8b9_add_taxonomy_tables_phase8_5.py`

**Migration Schema:**
```python
- name (String(255), NOT NULL)
- slug (String(255), NOT NULL, unique)
- parent_id (UUID, nullable)
- level (Integer, default=0)
- path (String(1000), NOT NULL)
- description (Text, nullable)
- keywords (JSON, nullable)
- resource_count (Integer, default=0)
- descendant_resource_count (Integer, default=0)
- is_leaf (Integer, default=1)
- allow_resources (Integer, default=1)
```

**Current Model:**
```python
- code (String(50), NOT NULL, unique)
- label (String(255), NOT NULL)
- description (Text, nullable)
- parent_id (UUID, nullable)
- level (Integer, default=0)
- scheme (String(50), default="custom")
- resource_count (Integer, default=0)
```

**Issues:**
- `name`/`slug` vs `code`/`label`
- Missing `path`, `keywords`, `descendant_resource_count`
- Missing `is_leaf`, `allow_resources`
- Has `scheme` not in migration

### 7. ResourceTaxonomy Model ❌ MISMATCH

**Migration:** `f6c3d5e7a8b9_add_taxonomy_tables_phase8_5.py`

**Migration Schema:**
```python
- id (UUID, primary key)
- resource_id (UUID, NOT NULL)
- taxonomy_node_id (UUID, NOT NULL)
- confidence (Float, default=0.0)
- is_predicted (Integer, default=1)
- predicted_by (String(100), nullable)
- needs_review (Integer, default=0)
- review_priority (Float, nullable)
```

**Current Model:**
```python
- resource_id (UUID, primary key)
- taxonomy_id (UUID, primary key)
- confidence (Float, default=1.0)
- is_manual (Integer, default=0)
- assigned_at (DateTime)
- needs_review (Integer, default=0)
- predicted_by (String(100), nullable)
```

**Issues:**
- Primary key structure different (single vs composite)
- `taxonomy_node_id` vs `taxonomy_id`
- `is_predicted` vs `is_manual` (inverted logic)
- Missing `review_priority`
- Has `assigned_at` not in migration

## Root Cause Analysis

### Why This Happened

1. **Models were updated manually** without corresponding migrations
2. **Migrations were created** but models weren't updated to match
3. **Different developers** worked on models vs migrations
4. **No validation** to ensure model-migration consistency

### Impact

1. **Runtime Errors**: Services fail when accessing non-existent fields
2. **Test Failures**: Tests can't create/query data correctly
3. **Data Integrity**: Inconsistent data structure
4. **Type Errors**: Boolean/Integer mismatches in PostgreSQL
5. **Foreign Key Errors**: Wrong field names in relationships

## Action Plan

### Phase 1: Critical Fixes (Immediate)
1. ✅ Fix Annotation model (DONE)
2. ❌ Fix Citation model
3. ❌ Fix GraphEdge model
4. ❌ Fix GraphEmbedding model
5. ❌ Fix DiscoveryHypothesis model

### Phase 2: Taxonomy Fixes (High Priority)
6. ❌ Fix TaxonomyNode model
7. ❌ Fix ResourceTaxonomy model

### Phase 3: Service Code Audit
8. ❌ Audit all service code for field name usage
9. ❌ Update services to use correct field names
10. ❌ Fix any broken relationships

### Phase 4: Testing
11. ❌ Run all tests to verify fixes
12. ❌ Add model-migration validation tests
13. ❌ Document correct field names

## Prevention Strategy

### 1. Add Model-Migration Validation
Create a test that compares model definitions with migration schemas:

```python
def test_models_match_migrations():
    """Verify all models match their migration schemas."""
    # Compare each model's columns with migration
    # Fail if mismatches found
```

### 2. Update Development Process
- Always update model AND migration together
- Review both files in PRs
- Run validation tests before merging

### 3. Documentation
- Document correct field names in each module
- Add field mapping reference
- Keep FIELD_MAPPING_REFERENCE.md updated

## Files Requiring Updates

### Models
- `backend/app/database/models.py` - 6 models need fixing

### Services (Need Audit)
- `backend/app/modules/graph/service.py`
- `backend/app/modules/graph/citations.py`
- `backend/app/modules/taxonomy/service.py`
- `backend/app/services/graph_service.py`
- `backend/app/services/citation_service.py`
- `backend/app/services/taxonomy_service.py`

### Tests (Need Updates)
- `backend/tests/modules/test_graph_endpoints.py`
- `backend/tests/modules/test_taxonomy_endpoints.py`
- All graph-related tests
- All taxonomy-related tests

## Estimated Effort

- Model fixes: 2-3 hours
- Service code audit: 3-4 hours
- Test updates: 2-3 hours
- Validation: 1-2 hours
- **Total**: 8-12 hours

## Priority Order

1. **Annotation** ✅ (DONE - needed for current tests)
2. **Citation** (High - used in graph features)
3. **TaxonomyNode** (High - used in classification)
4. **ResourceTaxonomy** (High - used in classification)
5. **GraphEdge** (Medium - used in graph features)
6. **GraphEmbedding** (Medium - used in graph features)
7. **DiscoveryHypothesis** (Low - advanced feature)

## Next Steps

1. Continue with Citation model fix
2. Then TaxonomyNode and ResourceTaxonomy
3. Audit service code for field usage
4. Update tests
5. Add validation tests
