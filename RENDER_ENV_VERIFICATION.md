# Render Environment Variables Verification Guide

## Current Status

You have **12 environment variables** currently set in Render. Let's verify and add the necessary ones for SQLite + OAuth.

## Required Environment Variables Checklist

### ✅ Already Set (Verify These)

Check that these exist and have correct values:

1. **MODE**
   - Should be: `CLOUD`
   - Purpose: Tells backend to run in cloud mode

2. **UPSTASH_REDIS_REST_URL**
   - Should be: `https://lucky-pug-47555.upstash.io`
   - Purpose: Redis queue management

3. **UPSTASH_REDIS_REST_TOKEN**
   - Should be: `AbnDAAIncDFiZDgzMDAwZDNkNWU0YjFlYWFkZDc1ZTZhMjAxYmQyY3AxNDc1NTU`
   - Purpose: Redis authentication

4. **PHAROS_ADMIN_TOKEN**
   - Should be: Any secure token (e.g., `staging-admin-token-change-me-in-production`)
   - Purpose: Admin API authentication

5. **MAX_QUEUE_SIZE**
   - Should be: `10`
   - Purpose: Queue configuration

6. **TASK_TTL_SECONDS**
   - Should be: `3600`
   - Purpose: Task timeout

7. **QDRANT_URL**
   - Should be: `https://1387e31e-904c-48dc-8f3a-772c6da3621e.us-east4-0.gcp.cloud.qdrant.io`
   - Purpose: Vector database

8. **QDRANT_API_KEY**
   - Should be: Your Qdrant API key
   - Purpose: Vector database authentication

### ⚠️ CRITICAL: Check DATABASE_URL

**This is the most important one!**

9. **DATABASE_URL**
   - ❌ **OLD (WRONG):** `postgresql://neondb_owner:npg_2Lv8pxVJzgyd@ep-fancy-grass-ah0xirjl-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require`
   - ✅ **NEW (CORRECT):** `sqlite:///./backend.db`
   - Purpose: Database connection

**Action Required:**
- If it still shows PostgreSQL URL, you need to:
  1. **Delete the DATABASE_URL variable completely**
  2. **Unlink NeonDB integration** (if present)
  3. **Add new DATABASE_URL** with SQLite value
  4. **Save and redeploy**

### ❌ Missing: OAuth Environment Variables

These need to be **ADDED** (not present in your current 12 variables):

10. **GOOGLE_CLIENT_ID**
    ```
    91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
    ```

11. **GOOGLE_CLIENT_SECRET**
    ```
    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
    ```

12. **GOOGLE_REDIRECT_URI**
    ```
    https://pharos.onrender.com/api/auth/google/callback
    ```

13. **FRONTEND_URL**
    ```
    https://pharos.onrender.com
    ```

14. **JWT_SECRET_KEY**
    ```
    <Generate with: openssl rand -hex 32>
    ```
    Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`

15. **JWT_ALGORITHM** (optional, has default)
    ```
    HS256
    ```

16. **JWT_ACCESS_TOKEN_EXPIRE_MINUTES** (optional, has default)
    ```
    30
    ```

17. **JWT_REFRESH_TOKEN_EXPIRE_DAYS** (optional, has default)
    ```
    7
    ```

18. **ENV**
    ```
    prod
    ```

## Step-by-Step Instructions

### Step 1: Check DATABASE_URL

1. In Render Dashboard, find the `DATABASE_URL` variable
2. Click to reveal its value
3. **If it shows PostgreSQL URL:**
   - Click the trash/delete icon to remove it
   - Look for "NeonDB" integration in the sidebar
   - If found, click "Disconnect" or "Remove"

### Step 2: Add DATABASE_URL with SQLite

1. Click "Add Environment Variable"
2. Key: `DATABASE_URL`
3. Value: `sqlite:///./backend.db`
4. Click "Save"

### Step 3: Generate JWT Secret

**On your local machine, run:**
```bash
openssl rand -hex 32
```

**Example output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Copy this value** - you'll use it in the next step.

### Step 4: Add OAuth Variables

Click "Add Environment Variable" for each of these:

| Key | Value |
|-----|-------|
| `GOOGLE_CLIENT_ID` | `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `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` |
| `GOOGLE_REDIRECT_URI` | `https://pharos.onrender.com/api/auth/google/callback` |
| `FRONTEND_URL` | `https://pharos.onrender.com` |
| `JWT_SECRET_KEY` | `<paste-your-generated-secret>` |
| `ENV` | `prod` |

### Step 5: Save and Deploy

1. Click "Save Changes" at the bottom
2. Render will automatically trigger a new deployment
3. Wait 3-5 minutes for deployment to complete

## Verification After Deployment

### Check Logs

Look for these in Render logs:

✅ **Good signs:**
```
Database initialized successfully: sqlite
Starting server...
Application startup complete
```

❌ **Bad signs:**
```
Connection refused
asyncpg (means still using PostgreSQL)
Failed to initialize database
```

### Test Endpoints

**Health Check:**
```bash
curl https://pharos.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "database_type": "sqlite"
}
```

**Login Page:**
Visit: https://pharos.onrender.com/login
- Should load without errors
- Should show "Sign in with Google" button

**OAuth Flow:**
1. Click "Sign in with Google"
2. Authorize with Google
3. Should redirect to callback URL
4. Should receive JWT token
5. Should redirect to dashboard (no 500 error!)

## Expected Final Count

After adding all variables, you should have approximately **18-20 environment variables** total:

- 8 existing (MODE, Redis, Qdrant, etc.)
- 1 updated (DATABASE_URL → SQLite)
- 6-8 new (OAuth + JWT variables)

## Troubleshooting

### If DATABASE_URL won't change:

1. **Delete the variable completely** (don't just edit)
2. **Check for NeonDB integration** in sidebar
3. **Disconnect NeonDB** if present
4. **Add DATABASE_URL fresh** with SQLite value
5. **Force redeploy:** Manual Deploy → Clear build cache & deploy

### If OAuth fails:

1. **Verify all 6 OAuth variables** are added
2. **Check JWT_SECRET_KEY** is generated (not placeholder)
3. **Check GOOGLE_REDIRECT_URI** matches exactly:
   - Must be: `https://pharos.onrender.com/api/auth/google/callback`
   - Must match Google Cloud Console settings

### If deployment fails:

1. **Check Render logs** for specific errors
2. **Verify DATABASE_URL** is `sqlite:///./backend.db`
3. **Ensure no NeonDB integration** is linked
4. **Try manual deploy** with cache clear

## Quick Copy-Paste Values

For easy copying:

```bash
# Database
DATABASE_URL=sqlite:///./backend.db

# OAuth
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
FRONTEND_URL=https://pharos.onrender.com
ENV=prod

# JWT (generate your own!)
JWT_SECRET_KEY=<run: openssl rand -hex 32>
```

## Next Steps After Setup

1. ✅ Verify deployment completes successfully
2. ✅ Check health endpoint returns 200 OK
3. ✅ Test login page loads
4. ✅ Test Google OAuth login flow
5. ✅ Verify JWT token is issued
6. ✅ Test protected routes work

---

**Need Help?**
- Check `DEPLOYMENT_CHECKLIST.md` for detailed steps
- Check `SQLITE_MIGRATION_GUIDE.md` for migration details
- Check Render logs for specific errors
