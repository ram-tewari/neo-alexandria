# Repository Ingestion Status

## Issue Encountered

When attempting to add repository `https://github.com/ram-tewari/pharos`:

**Error**: HTTP 500 Internal Server Error

**Endpoint**: `POST https://pharos.onrender.com/resources/ingest-repo`

## Root Cause

The repository ingestion endpoint requires Celery background workers to process repositories asynchronously. The current Render deployment is configured as a **Cloud API only** (lightweight control plane) without Celery workers.

From the architecture:
- **Cloud API (Render)**: Lightweight, 512MB RAM, 0.1 CPU - handles API requests only
- **Edge Worker (Local)**: GPU-accelerated compute for ML-intensive tasks

Repository ingestion is an ML-intensive task that should run on the Edge Worker, not the Cloud API.

## Current Architecture Limitation

The `/resources/ingest-repo` endpoint tries to start a Celery task:
```python
from ...tasks.celery_tasks import ingest_repo_task
```

But Celery is not running on the Render deployment because:
1. Render free tier doesn't support background workers
2. The deployment is intentionally lightweight (Cloud API only)
3. ML-intensive tasks are meant for the Edge Worker

## Solutions

### Option 1: Use Edge Worker (Recommended)

If you have the Edge Worker running locally:

1. **Start Edge Worker**:
   ```bash
   cd backend
   python worker.py
   ```

2. **Add repository via Edge Worker**:
   ```bash
   curl -X POST http://localhost:8000/resources/ingest-repo \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"git_url": "https://github.com/ram-tewari/pharos"}'
   ```

### Option 2: Direct Resource Creation

Add files individually via the resources API:

```bash
curl -X POST https://pharos.onrender.com/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "pharos README",
    "content": "...",
    "url": "https://github.com/ram-tewari/pharos/blob/main/README.md",
    "resource_type": "PRACTICE"
  }'
```

### Option 3: Enable Celery on Render (Requires Paid Plan)

1. Upgrade to Render paid plan
2. Add Celery worker service
3. Configure Redis for task queue
4. Deploy worker alongside API

### Option 4: Use Ingestion Endpoint (When Available)

The `/ingest` endpoint (Phase 19) is designed for cloud ingestion:

```bash
curl -X POST https://pharos.onrender.com/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer PHAROS_ADMIN_TOKEN" \
  -d '{
    "repo_url": "https://github.com/ram-tewari/pharos",
    "user_id": "1c3c6cb0-4c10-46ba-b9ad-8ca82fc008fa"
  }'
```

This queues the task in Upstash Redis for the Edge Worker to process.

## Recommended Workflow

For now, the best approach is:

1. **Use the frontend UI** when it's implemented (Phase 2.5+)
2. **Or run Edge Worker locally** for repository ingestion
3. **Or add resources individually** via the resources API

## Technical Details

### Why 500 Error?

The endpoint code tries to import Celery tasks:
```python
from ...tasks.celery_tasks import ingest_repo_task
```

But `celery_tasks.py` likely doesn't exist or Celery isn't configured on Render, causing an import error that results in a 500 response.

### Architecture Decision

The Phase 19 architecture intentionally separates:
- **Cloud API**: Lightweight, handles CRUD operations
- **Edge Worker**: Heavy compute, handles ML tasks

Repository ingestion is a heavy compute task (cloning, parsing, embedding generation) that belongs on the Edge Worker.

## Next Steps

1. **Check if Edge Worker is running**: `python backend/worker.py`
2. **Use Edge Worker for ingestion**: Connect to `http://localhost:8000`
3. **Or wait for frontend UI**: Phase 2.5 will provide a proper UI for this
4. **Or use direct resource creation**: Add files one by one via API

## Related Documentation

- `backend/docs/architecture/phase19-hybrid.md` - Hybrid architecture
- `backend/docs/guides/phase19-edge-setup.md` - Edge Worker setup
- `backend/docs/api/ingestion.md` - Ingestion API documentation
- `ADD_REPOSITORY_GUIDE.md` - Repository addition guide

## User Information

- **User**: Ram Tewari (ram.tewari.2023@gmail.com)
- **User ID**: 1c3c6cb0-4c10-46ba-b9ad-8ca82fc008fa
- **Tier**: free
- **Repository**: https://github.com/ram-tewari/pharos
