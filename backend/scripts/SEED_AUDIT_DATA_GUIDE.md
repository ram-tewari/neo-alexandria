# Seed Audit Data Guide

## Purpose

This script solves the "cold start" problem for retrieval auditing by generating synthetic test data with known ground truth. It creates 12 resources across 3 distinct clusters (Coding, Cooking, History) with 24 annotations.

## Why Synthetic Data?

- **Known Ground Truth**: We know exactly which results should match which queries
- **Vector Space Validation**: Three distinct clusters ensure embeddings are properly separated
- **Architecture Testing**: Tests FTS, Vector, and Hybrid retrieval without real corpus
- **Reproducible**: Same data every time for consistent benchmarking

## Prerequisites

```bash
# Install ML dependencies if not already installed
pip install sentence-transformers FlagEmbedding
```

**Note**: First run will download models (~2.5GB total):
- Nomic Embed Text v1: ~500MB
- BGE-M3: ~2GB

## Running the Seeder

```bash
# From backend directory
cd backend

# Run the seeder
python scripts/seed_audit_data.py
```

**Expected Output**:
```
============================================================
SEEDING AUDIT DATA
============================================================
--> Loading Dense Model (Nomic)...
--> Loading Sparse Model (BGE-M3)...
--> Models Loaded. Generating Data...
   + Added: Understanding Python Asyncio
   + Added: Database Indexing Strategies
   + Added: REST API Design Principles
   + Added: Docker Container Orchestration
   + Added: The Science of Sourdough
   + Added: Techniques for Carbonara
   + Added: Knife Skills for Chefs
   + Added: Sous Vide Cooking Method
   + Added: The Fall of Rome
   + Added: The Renaissance Period
   + Added: The Industrial Revolution
   + Added: World War II Timeline
============================================================
SUCCESS: Created 12 Resources and 24 Annotations.
You can now run 'python backend/scripts/audit_retrieval.py'
============================================================
```

## Data Structure

### Clusters

1. **CODING** (4 resources, 8 annotations)
   - Python Asyncio
   - Database Indexing
   - REST API Design
   - Docker Containers

2. **COOKING** (4 resources, 8 annotations)
   - Sourdough Science
   - Carbonara Technique
   - Knife Skills
   - Sous Vide Method

3. **HISTORY** (4 resources, 8 annotations)
   - Fall of Rome
   - Renaissance Period
   - Industrial Revolution
   - World War II

### Annotation Types

Each resource has 2 annotations:
- **Exact Match**: Contains specific keywords for FTS testing
- **Semantic Match**: Paraphrased content for vector search testing

## Running the Audit

After seeding, run the audit script:

```bash
python scripts/audit_retrieval.py --sample-size 100
```

**Note**: Script will automatically reduce sample size to 24 (number of annotations created).

## Expected Results

### FTS (Full-Text Search)
- ✅ Should find exact keyword matches
- ❌ Should miss semantic paraphrases
- **Expected Precision**: ~50% (finds half the annotations)

### Vector Search
- ✅ Should find semantic matches
- ✅ Should find exact matches (embeddings capture both)
- **Expected Precision**: ~80-90%

### Hybrid Search
- ✅ Should find both exact and semantic matches
- ✅ Best overall performance
- **Expected Precision**: ~85-95%

## Troubleshooting

### "CRITICAL: ml-dependencies not found"
```bash
pip install sentence-transformers FlagEmbedding
```

### "Out of Memory" during model loading
- Reduce batch size in script
- Use CPU instead of GPU (slower but works)
- Close other applications

### "No module named 'app'"
```bash
# Make sure you're in the backend directory
cd backend
python scripts/seed_audit_data.py
```

### Database locked error
```bash
# Stop any running backend servers
# Then retry
python scripts/seed_audit_data.py
```

## Cleaning Up

To remove synthetic data and start fresh:

```bash
# Backup current database
cp backend.db backend.db.backup

# Delete and recreate
rm backend.db
alembic upgrade head

# Re-run seeder
python scripts/seed_audit_data.py
```

## Next Steps

1. ✅ Run seeder to populate database
2. ✅ Run audit script to validate retrieval
3. ✅ Review metrics (Precision, Recall, F1)
4. ✅ Identify architecture issues if any
5. ✅ Fix issues and re-run audit

## What the Audit Will Tell You

- **FTS Working**: Finds exact keyword matches
- **Vector Working**: Finds semantic matches across clusters
- **Hybrid Working**: Combines both effectively
- **Embeddings Valid**: Vector space properly separated by cluster
- **Architecture Sound**: All retrieval modes functional

## Integration with Real Data

Once validated with synthetic data:
1. Keep synthetic data for regression testing
2. Add real corpus alongside synthetic data
3. Run audit on both datasets
4. Compare metrics to ensure consistency
