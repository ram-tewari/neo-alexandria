# Retrieval Audit Script - Ready to Run

## Status: ✅ FIXES APPLIED

The critical fixes have been applied to `backend/scripts/audit_retrieval.py`. The script is now ready to run once the database is properly set up.

## Fixes Applied

### 1. ✅ Fixed FTS5 Baseline (No Longer Rigged)
- **Before**: Used raw SQL `LIKE '%text%'` (substring scan)
- **After**: Uses `AdvancedSearchService._execute_fts_search()` (actual FTS5/tsvector)
- **Impact**: Now tests real production search pipeline

### 2. ✅ Added Model Warmup (Isolates Cold Start)
- **Before**: Model loading time included in average latency
- **After**: Warmup call before timing vector/hybrid searches
- **Impact**: Accurate latency measurements

### 3. ✅ Fixed Field Names
- **Before**: Used `Annotation.text` (doesn't exist)
- **After**: Uses `Annotation.highlighted_text` (correct field)
- **Impact**: Script will actually run

## Prerequisites

Before running the audit, ensure:

### 1. Database Migrations Are Current
```bash
cd backend
alembic upgrade head
```

**Check for**: The database needs the `curation_status` column on resources table.

### 2. Database Has Test Data
You need:
- At least 10 annotations with `highlighted_text`
- Resources with embeddings generated
- Resources indexed for FTS5 search

**Check with**:
```bash
cd backend
python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Annotation, Resource
import os

engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///./backend.db'))
Session = sessionmaker(bind=engine)
db = Session()

try:
    ann_count = db.query(Annotation).filter(
        Annotation.highlighted_text.isnot(None),
        Annotation.highlighted_text != ''
    ).count()
    
    res_count = db.query(Resource).count()
    
    emb_count = db.query(Resource).filter(
        Resource.embedding.isnot(None)
    ).count()
    
    print(f'✓ Annotations with text: {ann_count}')
    print(f'✓ Total resources: {res_count}')
    print(f'✓ Resources with embeddings: {emb_count}')
    
    if ann_count < 10:
        print(f'⚠️  WARNING: Need at least 10 annotations, found {ann_count}')
    if emb_count == 0:
        print(f'⚠️  WARNING: No embeddings found, vector search will fail')
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    print('Run migrations: alembic upgrade head')
finally:
    db.close()
"
```

### 3. Environment Variables Set
```bash
# Required
DATABASE_URL=sqlite:///./backend.db  # or PostgreSQL URL

# Optional (for ML models)
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
```

## Running the Audit

### Quick Test (10 samples)
```bash
cd backend
python scripts/audit_retrieval.py --sample-size 10
```

### Standard Audit (50 samples)
```bash
cd backend
python scripts/audit_retrieval.py --sample-size 50
```

### Full Audit (100 samples)
```bash
cd backend
python scripts/audit_retrieval.py --sample-size 100
```

### Custom Output Location
```bash
cd backend
python scripts/audit_retrieval.py --sample-size 50 --output results/audit_2026-01-27.json
```

## Expected Output

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
  Progress: 30/50
  Progress: 40/50
  Progress: 50/50

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
  Progress: 20/50
  Progress: 30/50
  Progress: 40/50
  Progress: 50/50

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
  Progress: 20/50
  Progress: 30/50
  Progress: 40/50
  Progress: 50/50

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

## Interpreting Results

### Metrics Explained

**MRR (Mean Reciprocal Rank)**:
- Average of 1/rank for first correct result
- Higher is better (max 1.0)
- Example: If target is rank 3, contributes 1/3 = 0.333

**Recall@5**:
- Percentage of queries where target appears in top 5
- Higher is better (max 1.0)
- Example: 0.68 = 68% of queries found target in top 5

**Recall@10**:
- Percentage of queries where target appears in top 10
- Higher is better (max 1.0)
- Example: 0.76 = 76% of queries found target in top 10

**Latency**:
- Average query time in milliseconds
- Lower is better
- Excludes model loading time (warmup)

### Decision Matrix

| Scenario | Action | Reasoning |
|----------|--------|-----------|
| FTS5 wins (MRR > Hybrid) | ❌ Delete ML models | ML overhead not justified |
| Hybrid wins by <10% | ⚠️ Cost/benefit analysis | Small improvement, high cost |
| Hybrid wins by 10-20% | ✅ Keep ML, optimize | Good improvement, worth it |
| Hybrid wins by >20% | ✅ Keep ML, invest more | Significant value add |

### Latency Thresholds

| Latency | Rating | Action |
|---------|--------|--------|
| <100ms | ✓ Excellent | No action needed |
| 100-500ms | ✓ Acceptable | Monitor, optimize if possible |
| 500-2000ms | ⚠️ Slow | Investigate bottlenecks |
| >2000ms | ❌ Unacceptable | Major optimization required |

## Troubleshooting

### Error: "Insufficient annotations for evaluation"
**Solution**: Create more test annotations or reduce `--sample-size`

### Error: "No embeddings found"
**Solution**: Generate embeddings for resources:
```bash
cd backend
python scripts/generate_embeddings.py
```

### Error: "no such column: resources.curation_status"
**Solution**: Run database migrations:
```bash
cd backend
alembic upgrade head
```

### Error: "Module not found"
**Solution**: Ensure you're in the backend directory and virtual environment is activated:
```bash
cd backend
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## Next Steps

1. **Run migrations**: `alembic upgrade head`
2. **Check data**: Verify annotations and embeddings exist
3. **Run audit**: `python scripts/audit_retrieval.py --sample-size 50`
4. **Review results**: Check MRR, Recall, and Latency
5. **Make decision**: Keep or remove ML based on results
6. **Document**: Update architecture docs with findings

## Files Modified

- ✅ `backend/scripts/audit_retrieval.py` - Fixed FTS5, added warmup, fixed field names
- ✅ `backend/scripts/RETRIEVAL_AUDIT_FIXES.md` - Detailed fix documentation
- ✅ `backend/scripts/AUDIT_READY_TO_RUN.md` - This file

## References

- Original issue: Fatal flaws in baseline implementation
- Fix 1: Use real FTS5 service, not raw SQL
- Fix 2: Add warmup to isolate cold start
- Fix 3: Use correct field name (`highlighted_text`)
