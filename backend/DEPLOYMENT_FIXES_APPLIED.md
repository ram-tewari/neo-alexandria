# Deployment Fixes Applied - January 21, 2026

## Problem

Render deployment was failing with:
```
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'redis'
```

The application was trying to load ALL modules including ML-heavy ones (recommendations, neural_graph) that require torch, which isn't available in the cloud deployment.

## Root Cause

Phase 19 implements a **hybrid edge-cloud architecture**:
- **Cloud API (Render)**: Lightweight control plane - should NOT have torch
- **Edge Worker (Local)**: GPU-accelerated compute plane - has torch for ML

However, the module registration was loading ALL modules regardless of deployment mode, causing the cloud API to try importing torch-dependent modules.

## Fixes Applied

### 1. Made Redis Import Optional (`app/shared/cache.py`)

**Changes**:
- Wrapped `import redis` in try/except block
- Added `REDIS_AVAILABLE` flag
- Made all cache methods check if redis is available before operating
- Gracefully degrades to no-op when redis unavailable

**Impact**: Cloud API can start even if redis library is missing (uses upstash-redis instead)

### 2. Added redis to Base Requirements (`requirements-base.txt`)

**Changes**:
- Added `redis==5.2.1` to base requirements

**Rationale**: The standard redis client is needed for the cache service. Upstash-redis is for the REST API, but the cache service uses the standard client.

### 3. Made Torch Import Optional (`app/modules/recommendations/collaborative.py`)

**Changes**:
- Wrapped torch imports in try/except block
- Added `TORCH_AVAILABLE` flag
- Module will fail gracefully if torch is missing

**Impact**: Recommendations module won't crash the entire app if torch is unavailable

### 4. Conditional Module Loading (`app/__init__.py`)

**Changes**:
- Split modules into three categories:
  - `base_modules`: Core modules that work without torch/redis
  - `edge_only_modules`: Modules requiring torch (recommendations)
  - `redis_modules`: Modules requiring redis (monitoring)
  
- Load modules conditionally based on `settings.MODE`:
  - **CLOUD mode**: Load base + redis modules, skip torch modules
  - **EDGE mode**: Load all modules

- Added ingestion router registration for cloud API

**Impact**: Cloud deployment only loads modules it can actually run

## Deployment Architecture

### Cloud API (Render Free Tier)
```
MODE=CLOUD
Dependencies: requirements-cloud.txt
- fastapi, uvicorn, pydantic
- psycopg2-binary (Neon Postgres)
- qdrant-client (Qdrant Cloud)
- upstash-redis (task queue)
- redis (cache service)
- NO torch, NO transformers

Modules Loaded:
✓ collections, resources, search
✓ annotations, scholarly, authority
✓ curation, quality, taxonomy, graph
✓ auth
✓ ingestion (Phase 19)
✗ recommendations (requires torch)
⚠ monitoring (requires redis, may fail gracefully)
```

### Edge Worker (Local GPU)
```
MODE=EDGE
Dependencies: requirements-edge.txt
- All cloud dependencies
- torch, torch-geometric
- tree-sitter parsers
- Full ML stack

Modules Loaded:
✓ All modules including recommendations
✓ Neural graph service
✓ Repository parser
```

## Testing

### Verify Cloud Deployment
```bash
# Check Render logs for:
✓ "Deployment mode: CLOUD"
✓ "Cloud mode: Skipping torch-dependent modules"
✓ "Registered ingestion router for cloud API"
✓ "Module registration complete: X modules registered"

# Test health endpoint
curl https://pharos.onrender.com/health

# Test ingestion endpoint (requires auth)
curl -X POST https://pharos.onrender.com/api/v1/ingestion/ingest/github.com/user/repo \
  -H "Authorization: Bearer $PHAROS_ADMIN_TOKEN"
```

### Verify Edge Worker
```bash
# Set MODE=EDGE in .env
MODE=EDGE

# Run worker
python backend/worker.py

# Should see:
🔥 Edge Worker Online
   Hardware: NVIDIA GeForce RTX 4070
   Device: cuda
```

## Next Steps

1. **Push to Render**: Commit and push these changes
2. **Monitor Deployment**: Watch Render logs for successful startup
3. **Test Endpoints**: Verify /health and /api/v1/ingestion work
4. **Start Edge Worker**: Run worker.py locally to process tasks
5. **End-to-End Test**: Submit a repo ingestion and verify it completes

## Files Modified

- `backend/app/shared/cache.py` - Optional redis import
- `backend/requirements-base.txt` - Added redis dependency
- `backend/app/modules/recommendations/collaborative.py` - Optional torch import
- `backend/app/__init__.py` - Conditional module loading based on MODE

## Related Documentation

- Phase 19 Design: `.kiro/specs/backend/phase19-hybrid-edge-cloud-orchestration/design.md`
- Deployment Guide: `backend/PHASE19_DEPLOYMENT_README.md`
- Requirements Strategy: `backend/REQUIREMENTS_STRATEGY.md`
