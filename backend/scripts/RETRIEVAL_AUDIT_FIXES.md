# Retrieval Audit Script - Critical Fixes Applied

## Date: January 27, 2026

## Problem Statement

The original `audit_retrieval.py` script had two fatal flaws that would produce misleading results:

### Flaw 1: Rigged Baseline (FTS5)
**Issue**: The FTS5 baseline used raw SQLAlchemy `.contains()` which translates to SQL `LIKE '%text%'` - a slow substring scan, NOT actual FTS5 token-based inverted index lookup (BM25).

**Impact**: 
- The baseline would fail not because FTS5 is bad, but because the query was wrong
- Only searched `Resource.title` and `Resource.description`, missing annotation content
- Would return 0 results 100% of the time for deep document annotations
- ML models would win by default, giving false confidence

**Fix Applied**:
```python
# BEFORE (Wrong - uses LIKE)
resources = (
    self.db.query(Resource)
    .filter(Resource.title.contains(query_text) | Resource.description.contains(query_text))
    .limit(10)
    .all()
)

# AFTER (Correct - uses production FTS5 pipeline)
fts_results = AdvancedSearchService._execute_fts_search(
    db=self.db,
    query=query_text,
    limit=10
)
```

### Flaw 2: Cold Start Contamination
**Issue**: Model loading time (3+ seconds for PyTorch) was lumped into "Average Latency". First query takes 3s, next 99 take 50ms, average shows ~80ms, masking initialization cost.

**Impact**:
- Latency metrics were misleading
- Couldn't distinguish between model load time and actual query time
- Made ML models appear faster than they really are

**Fix Applied**:
```python
def _warmup_model(self, method_name: str):
    """Run a dummy query to load lazy models into memory."""
    print(f"   [Warmup] Initializing {method_name} models...")
    try:
        dummy_query = SearchQuery(text="warmup", filters=SearchFilters(), limit=1)
        AdvancedSearchService.search_three_way_hybrid(
            db=self.db,
            query=dummy_query,
            enable_reranking=False
        )
    except Exception:
        pass  # Ignore errors, just want to trigger imports
```

## Changes Made

### 1. Fixed FTS5 Evaluation Method
- **File**: `backend/scripts/audit_retrieval.py`
- **Method**: `_evaluate_fts5()`
- **Change**: Now uses `AdvancedSearchService._execute_fts_search()` instead of raw SQL
- **Benefit**: Tests actual production FTS5 implementation with proper indexing

### 2. Added Warmup Method
- **File**: `backend/scripts/audit_retrieval.py`
- **Method**: `_warmup_model()`
- **Purpose**: Isolates cold start costs from query latency
- **Usage**: Called before vector and hybrid evaluations

### 3. Updated Vector Evaluation
- **File**: `backend/scripts/audit_retrieval.py`
- **Method**: `_evaluate_vector()`
- **Changes**:
  - Added warmup call before timing
  - Uses `AdvancedSearchService._execute_dense_search()` directly
  - Moved embedding check before warmup

### 4. Updated Hybrid Evaluation
- **File**: `backend/scripts/audit_retrieval.py`
- **Method**: `_evaluate_hybrid()`
- **Change**: Added warmup call before timing

## Verification Steps

### Before Running Audit
1. Ensure database has annotations with text
2. Ensure resources have embeddings generated
3. Verify FTS5 index exists (SQLite) or tsvector (PostgreSQL)

### Run Command
```bash
python backend/scripts/audit_retrieval.py --sample-size 50
```

### Expected Output
```
================================================================================
RETRIEVAL QUALITY AUDIT
================================================================================
Sample Size: 50
Database: sqlite:///./backend.db

================================================================================
STEP 1: Fetching Annotation Samples
================================================================================
Total annotations with text: 150
✓ Sampled 50 annotations
  Average text length: 85.3 chars

================================================================================
STEP 2: Evaluating FTS5 (Production Pipeline)
================================================================================
  Progress: 10/50
  Progress: 20/50
  ...
✓ FTS5 Evaluation Complete
  MRR: 0.4523
  Recall@5: 0.6800 (34/50)
  Recall@10: 0.7600 (38/50)
  Avg Latency: 45.2ms

================================================================================
STEP 3: Evaluating Vector (Dense Embedding) Search
================================================================================
Resources with embeddings: 120
   [Warmup] Initializing Vector Search models...
  Progress: 10/50
  ...
✓ Vector Evaluation Complete
  MRR: 0.5234
  Recall@5: 0.7400 (37/50)
  Recall@10: 0.8200 (41/50)
  Avg Latency: 125.3ms

================================================================================
STEP 4: Evaluating Hybrid (Three-Way) Search
================================================================================
   [Warmup] Initializing Hybrid Search models...
  Progress: 10/50
  ...
✓ Hybrid Evaluation Complete
  MRR: 0.5891
  Recall@5: 0.8000 (40/50)
  Recall@10: 0.8800 (44/50)
  Avg Latency: 185.7ms

================================================================================
COMPARISON RESULTS
================================================================================

Method          MRR   Recall@5   Recall@10   Latency (ms)
--------------------------------------------------------------------------------
FTS5           0.4523     0.6800      0.7600           45.2
VECTOR         0.5234     0.7400      0.8200          125.3
HYBRID         0.5891     0.8000      0.8800          185.7
--------------------------------------------------------------------------------

ANALYSIS:
✓ PASS: Hybrid search outperforms both FTS5 and Vector
  Hybrid improves MRR by 30.2% over FTS5

LATENCY ANALYSIS:
  FTS5: 45.2ms - ✓ Excellent
  VECTOR: 125.3ms - ✓ Acceptable
  HYBRID: 185.7ms - ✓ Acceptable

✓ Results saved to: retrieval_audit_results.json

✓ AUDIT PASSED: ML models add value
```

## Decision Criteria

### If FTS5 Wins (MRR > Hybrid)
**Action**: Delete ML models, use FTS5 only
**Reasoning**: ML overhead not justified by performance gain
**Cost Savings**: Eliminate GPU requirements, reduce latency

### If Hybrid Wins by <10%
**Action**: Consider cost/benefit analysis
**Reasoning**: Small improvement may not justify ML complexity
**Recommendation**: Run stress tests to evaluate at scale

### If Hybrid Wins by >10%
**Action**: Keep ML architecture
**Reasoning**: Significant improvement justifies complexity
**Next Steps**: Proceed to Phase 3 stress testing

## Next Steps

1. **Run the audit**: `python backend/scripts/audit_retrieval.py --sample-size 50`
2. **Review results**: Check MRR, Recall@5, Recall@10 for all methods
3. **Analyze latency**: Ensure acceptable performance (<500ms)
4. **Make decision**: Keep or remove ML based on results
5. **Document findings**: Update architecture docs with decision rationale

## Files Modified

- `backend/scripts/audit_retrieval.py` - Fixed FTS5 evaluation and added warmup

## Testing

```bash
# Syntax check
python -m py_compile backend/scripts/audit_retrieval.py

# Run audit with small sample
python backend/scripts/audit_retrieval.py --sample-size 10

# Run full audit
python backend/scripts/audit_retrieval.py --sample-size 100
```

## Notes

- Warmup only affects vector and hybrid methods (FTS5 has no model loading)
- Warmup errors are silently ignored (expected if models not available)
- Results saved to `retrieval_audit_results.json` for analysis
- Exit code 0 = ML models add value, Exit code 1 = ML models don't help
