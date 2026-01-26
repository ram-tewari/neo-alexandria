# SQLite Migration Guide - Temporary Fix for NeonDB Connection Issues

## Problem

NeonDB free tier auto-suspends after 5 minutes of inactivity, causing connection refused errors when the database needs to wake up. The retry logic cannot intercept SQLAlchemy's connection pool creation, resulting in failed OAuth callbacks and API requests.

## Solution

Temporarily switch to SQLite for the cloud deployment while we resolve the NeonDB connection issues.

## Steps to Migrate on Render

### 1. Unlink NeonDB Service (Critical!)

**In Render Dashboard:**
1. Go to your service: `neo-alexandria-cloud-api`
2. Navigate to "Environment" tab
3. Find the NeonDB integration/add-on
4. Click "Disconnect" or "Remove" to unlink the NeonDB service
5. This will remove the cached `DATABASE_URL` environment variable

### 2. Deploy Updated Configuration

The `render.yaml` has been updated to use SQLite:

```yaml
envVars:
  - key: DATABASE_URL
    value: sqlite:///./backend.db
```

**Deploy the changes:**
```bash
git add backend/render.yaml SQLITE_MIGRATION_GUIDE.md
git commit -m "Switch to SQLite temporarily to fix NeonDB connection issues"
git push origin master
```

### 3. Verify Deployment

**Check Render logs for:**
- ✅ `Database initialized successfully: sqlite`
- ✅ `aiosqlite` driver being used (not `asyncpg`)
- ❌ No more "Connection refused" errors

**Test endpoints:**
```bash
# Health check
curl https://pharos.onrender.com/health

# OAuth login (should work now)
# Visit: https://pharos.onrender.com/login
```

### 4. Add OAuth Environment Variables

Once SQLite is working, add these to Render environment variables:

```bash
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
FRONTEND_URL=https://pharos.onrender.com
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENV=prod
```

## SQLite Limitations

**Temporary solution only:**
- ⚠️ File-based storage (data persists in container filesystem)
- ⚠️ Limited concurrency (single writer at a time)
- ⚠️ No advanced PostgreSQL features (JSONB, full-text search)
- ⚠️ Data may be lost on container restart (Render free tier)

**For production, we need to:**
1. Fix NeonDB connection retry logic at pool level
2. Or switch to a different PostgreSQL provider (Supabase, Railway, etc.)
3. Or upgrade NeonDB to paid tier (no auto-suspend)

## Reverting to PostgreSQL Later

When ready to switch back:

1. **Update `render.yaml`:**
```yaml
envVars:
  - key: DATABASE_URL
    value: postgresql://user:pass@host:5432/db?sslmode=require
```

2. **Run migrations:**
```bash
# Migrations will auto-run on deployment
# Or manually: alembic upgrade head
```

3. **Verify:**
```bash
# Check logs for: "Database initialized successfully: postgresql"
```

## Current Status

- ✅ `render.yaml` updated to use SQLite
- ⏳ Waiting for deployment
- ⏳ Need to unlink NeonDB in Render dashboard
- ⏳ Need to add OAuth environment variables

## Next Steps

1. **Immediate:** Unlink NeonDB in Render dashboard
2. **Deploy:** Push changes and wait for deployment
3. **Verify:** Check logs for SQLite initialization
4. **Test:** Try OAuth login flow
5. **Configure:** Add OAuth environment variables
6. **Long-term:** Decide on permanent database solution

## Alternative Solutions (Future)

### Option 1: Fix NeonDB Retry Logic
- Implement custom connection pool with retry logic
- Override SQLAlchemy's `pool._invoke_creator()` method
- Complex but keeps PostgreSQL features

### Option 2: Switch to Supabase
- Similar to NeonDB but more stable free tier
- Better connection pooling
- Built-in auth features

### Option 3: Upgrade NeonDB
- Paid tier doesn't auto-suspend
- Better connection limits
- ~$19/month

### Option 4: Self-hosted PostgreSQL
- Full control over configuration
- No auto-suspend issues
- Requires infrastructure management

## Testing Checklist

After deployment:

- [ ] Health endpoint responds: `GET /health`
- [ ] Login page loads: `https://pharos.onrender.com/login`
- [ ] Google OAuth redirects correctly
- [ ] OAuth callback succeeds (no 500 error)
- [ ] JWT token is issued
- [ ] Protected routes work with token
- [ ] Database queries succeed
- [ ] No "Connection refused" errors in logs

## Rollback Plan

If SQLite causes issues:

1. Revert `render.yaml` to use NeonDB
2. Add connection retry at application level (not pool level)
3. Increase timeout values
4. Consider switching database providers

## Questions?

- Check Render logs: `https://dashboard.render.com/web/[service-id]/logs`
- Check database type in logs: Look for "Database initialized successfully: [type]"
- Test locally first: `DATABASE_URL=sqlite:///./backend.db uvicorn app.main:app`
