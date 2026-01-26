# URGENT: OAuth Redirect URI Fix

## THE PROBLEM (FOUND!)

Google is redirecting to:
```
http://localhost:8000/auth/google/callback
```

Instead of:
```
https://pharos.onrender.com/api/auth/google/callback
```

## ROOT CAUSE

The `GOOGLE_REDIRECT_URI` environment variable in Render is set to **localhost** instead of the production URL.

## THE FIX

### Step 1: Update Render Environment Variable

1. Go to: https://dashboard.render.com
2. Select service: `neo-alexandria-cloud-api`
3. Go to "Environment" tab
4. Find `GOOGLE_REDIRECT_URI`
5. Change from:
   ```
   http://localhost:8000/auth/google/callback
   ```
   To:
   ```
   https://pharos.onrender.com/api/auth/google/callback
   ```
6. Click "Save Changes"
7. Render will auto-redeploy

### Step 2: Verify Google Console Has Both URIs

In Google Cloud Console, ensure BOTH URIs are registered:
- `https://pharos.onrender.com/api/auth/google/callback` (production)
- `http://localhost:8000/api/auth/google/callback` (local development)

This allows testing both locally and in production.

## Why This Happened

The environment variable was likely set during local development and never updated for production deployment.

## After Fix

Once the environment variable is updated and Render redeploys:
1. Try OAuth login again
2. Google will redirect to the correct production URL
3. OAuth flow should complete successfully

## Additional Fix: MCP Module Import

Also fixed in this commit:
- Changed `backend.app.modules.mcp.schema` to `.schema` (relative import)
- Changed `backend.app.modules.mcp.service` to `.service` (relative import)

This was causing deployment failures.

## Timeline

1. ✅ MCP import fixed
2. ⏳ **ACTION REQUIRED**: Update `GOOGLE_REDIRECT_URI` in Render to production URL
3. ⏳ Wait for Render redeploy (~3-5 min)
4. ⏳ Test OAuth login
5. ✅ OAuth should work!
