# Model Fixes Complete

## Date: December 26, 2024

## Summary

Fixed 7 models in `backend/app/database/models.py` to match their migration schemas. All models now correctly reflect the database structure defined in Alembic migrations.

## Models Fixed

### 1. Annotation Model ✅

**Changes:**
- `selection_start/end` → `start_offset/end_offset`
- `selection_text` → `highlighted_text`
- `content` → `note`
- `is_private` → `is_shared`
- Added: `context_before`, `context_after`, `embedding`, `collection_ids`
- Removed: `annotation_type`, `page_number`
- Changed `tags` from JSON to Text

**Migration:** `e5b9f2c3d4e5_add_annotations_table_phase7_5.py`

### 2. Citation Model ✅

**Changes:**
- `source_id` → `source_resource_id`
- `target_id` → `target_resource_id` (now nullable)
- Added: `target_url` (required), `updated_at`
- `context` → `context_snippet`
- `confidence` → `importance_score`
- Added: `position`
- Made `citation_type` required with default 'reference'

**Migration:** `23fa08826047_add_citation_table_phase6.py`

### 3. GraphEdge Model ✅

**Changes:**
- `metadata` type: JSON → Text
- Added: `created_by` (required), `confidence`
- Updated indexes to use 'composite' naming

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

### 4. GraphEmbedding Model ✅

**Changes:**
- `embedding` → `structural_embedding` (nullable)
- Added: `fusion_embedding` (nullable)
- `algorithm` → `embedding_method`
- Added: `embedding_version` (required), `hnsw_index_id`
- Removed `algorithm` index

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

### 5. DiscoveryHypothesis Model ✅

**Complete redesign to match migration:**
- Removed: `hypothesis_text`, `confidence`, `supporting_resources`, `status`
- Added: `a_resource_id`, `c_resource_id`, `b_resource_ids`
- Added: `hypothesis_type`, `plausibility_score`, `path_strength`
- Added: `path_length`, `common_neighbors`, `discovered_at`
- Added: `user_id`, `is_validated`, `validation_notes`
- Updated indexes

**Migration:** `g7h8i9j0k1l2_add_graph_intelligence_tables_phase10.py`

### 6. TaxonomyNode Model ✅

**Changes:**
- `code` → `slug` (unique, indexed)
- `label` → `name`
- Added: `path` (required), `keywords`
- Added: `descendant_resource_count`, `is_leaf`, `allow_resources`
- Removed: `scheme`
- Changed `level` default to use server_default
- Updated indexes

**Migration:** `f6c3d5e7a8b9_add_taxonomy_tables_phase8_5.py`

### 7. ResourceTaxonomy Model ✅

**Changes:**
- Primary key: Composite (`resource_id`, `taxonomy_id`) → Single `id`
- `taxonomy_id` → `taxonomy_node_id`
- `is_manual` → `is_predicted` (inverted logic: manual=0, predicted=1)
- `assigned_at` → `created_at` + `updated_at`
- Added: `review_priority`
- Changed `confidence` default: 1.0 → 0.0
- Removed `confidence` index

**Migration:** `f6c3d5e7a8b9_add_taxonomy_tables_phase8_5.py`

## Impact Analysis

### Services That Need Verification

These services may use old field names and need to be audited:

1. **Citation Service**
   - `backend/app/services/citation_service.py`
   - `backend/app/modules/graph/citations.py`
   - Check for: `source_id` → `source_resource_id`, `target_id` → `target_resource_id`

2. **Graph Services**
   - `backend/app/services/graph_service.py`
   - `backend/app/modules/graph/service.py`
   - Check for: `metadata` JSON usage, `algorithm` → `embedding_method`

3. **Taxonomy Services**
   - `backend/app/services/taxonomy_service.py`
   - `backend/app/modules/taxonomy/service.py`
   - Check for: `code` → `slug`, `label` → `name`, `taxonomy_id` → `taxonomy_node_id`

4. **Discovery/Hypothesis Services**
   - Any code using DiscoveryHypothesis model
   - Complete redesign - will need major updates

### Tests That Need Updates

1. **Graph Tests**
   - `backend/tests/modules/test_graph_endpoints.py`
   - Update field names in test data

2. **Taxonomy Tests**
   - `backend/tests/modules/test_taxonomy_endpoints.py`
   - Update field names in test data

3. **Citation Tests**
   - Any tests using Citation model
   - Update field names

## Validation Steps

### 1. Check Model Imports
```bash
cd backend
grep -r "from.*models import" app/services/ app/modules/
```

### 2. Check Field Usage
```bash
# Check for old field names
grep -r "source_id" app/services/ app/modules/ | grep -i citation
grep -r "\.code" app/services/ app/modules/ | grep -i taxonomy
grep -r "taxonomy_id" app/services/ app/modules/
grep -r "algorithm" app/services/ app/modules/ | grep -i graph
```

### 3. Run Tests
```bash
# Run annotation tests (should pass now)
pytest backend/tests/modules/test_annotations_endpoints.py -v

# Run all module tests
pytest backend/tests/modules/ -v

# Check for model-related errors
pytest backend/tests/ -k "model" -v
```

## Next Steps

1. ✅ **Models Fixed** - All 7 models now match migrations
2. ⏭️ **Audit Services** - Check service code for old field names
3. ⏭️ **Update Tests** - Fix test data to use new field names
4. ⏭️ **Run Test Suite** - Verify all tests pass
5. ⏭️ **Update Documentation** - Document field name changes

## Prevention

To prevent this from happening again:

1. **Add Model-Migration Validation Test**
   ```python
   def test_models_match_migrations():
       """Verify all models match their migration schemas."""
       # Compare model columns with latest migration
       # Fail if mismatches found
   ```

2. **Update Development Process**
   - Always update model AND migration together
   - Review both files in PRs
   - Run validation tests before merging

3. **Documentation**
   - Keep FIELD_MAPPING_REFERENCE.md updated
   - Document breaking changes
   - Add migration notes to CHANGELOG

## Files Modified

- `backend/app/database/models.py` - 7 models fixed

## Estimated Impact

- **High**: Citation, TaxonomyNode, ResourceTaxonomy (used in multiple features)
- **Medium**: GraphEdge, GraphEmbedding (used in graph features)
- **Low**: DiscoveryHypothesis (advanced feature, may not be fully implemented)

## Success Criteria

- ✅ All models match their migrations
- ⏳ All tests pass
- ⏳ No runtime errors from field mismatches
- ⏳ Service code uses correct field names
