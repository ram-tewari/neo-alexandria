# Deployment Checklist - SQLite Migration

## Status: ⏳ In Progress

### ✅ Completed Steps

1. ✅ Updated `render.yaml` to use SQLite instead of NeonDB
2. ✅ Created migration guide documentation
3. ✅ Committed and pushed changes to GitHub
4. ✅ Deployment triggered on Render

### ⏳ Next Steps (Manual Actions Required)

#### 1. Unlink NeonDB in Render Dashboard (CRITICAL!)

**Why:** Render is caching the NeonDB `DATABASE_URL` even though we changed `render.yaml`. You must unlink the NeonDB service to clear the cached value.

**Steps:**
1. Go to: https://dashboard.render.com
2. Select service: `neo-alexandria-cloud-api`
3. Click "Environment" tab
4. Look for NeonDB integration/add-on
5. Click "Disconnect" or "Remove" to unlink
6. This will remove the cached `DATABASE_URL`

#### 2. Wait for Deployment to Complete

**Monitor at:** https://dashboard.render.com/web/[your-service-id]/deploys

**Look for in logs:**
- ✅ `Database initialized successfully: sqlite`
- ✅ `aiosqlite` driver being used
- ❌ No "Connection refused" errors
- ❌ No `asyncpg` references (that's PostgreSQL)

**Expected deployment time:** 3-5 minutes

#### 3. Verify SQLite is Working

**Test health endpoint:**
```bash
curl https://pharos.onrender.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "database_type": "sqlite"
}
```

**Test login page:**
- Visit: https://pharos.onrender.com/login
- Should load without errors
- Should show Google OAuth button

#### 4. Add OAuth Environment Variables

**In Render Dashboard → Environment tab, add:**

```bash
# Google OAuth
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback

# Frontend
FRONTEND_URL=https://pharos.onrender.com

# JWT (generate a secure key!)
JWT_SECRET_KEY=<run: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENV=prod
```

**To generate JWT secret:**
```bash
openssl rand -hex 32
```

**After adding variables:**
- Click "Save Changes"
- Render will automatically redeploy (2-3 minutes)

#### 5. Test OAuth Login Flow

**Steps:**
1. Visit: https://pharos.onrender.com/login
2. Click "Sign in with Google"
3. Authorize with your Google account
4. Should redirect to: `https://pharos.onrender.com/api/auth/google/callback`
5. Should receive JWT token
6. Should redirect to dashboard/home page

**Expected behavior:**
- ✅ No 500 Internal Server Error
- ✅ No "Connection refused" errors
- ✅ Successful OAuth callback
- ✅ JWT token issued
- ✅ Redirect to authenticated page

#### 6. Test Password Login (Optional)

**Test credentials:**
- Email: `test@example.com`
- Password: `testpassword123`

**Steps:**
1. Visit: https://pharos.onrender.com/login
2. Enter test credentials
3. Click "Sign in"
4. Should receive JWT token
5. Should redirect to dashboard

### 🔍 Troubleshooting

#### If deployment fails:

**Check Render logs for:**
```bash
# Good signs:
✅ "Database initialized successfully: sqlite"
✅ "Starting server..."
✅ "Application startup complete"

# Bad signs:
❌ "Connection refused"
❌ "asyncpg" (means still using PostgreSQL)
❌ "Failed to initialize database"
```

#### If still seeing NeonDB errors:

1. **Verify NeonDB is unlinked:**
   - Go to Render Dashboard → Environment
   - Should NOT see NeonDB in integrations
   - `DATABASE_URL` should be `sqlite:///./backend.db`

2. **Force redeploy:**
   - Go to Render Dashboard
   - Click "Manual Deploy" → "Clear build cache & deploy"

3. **Check environment variables:**
   - Ensure `DATABASE_URL=sqlite:///./backend.db`
   - No other database-related variables

#### If OAuth fails:

1. **Check redirect URI (MOST COMMON ISSUE):**
   - **Error**: `{"error": "invalid_grant", "error_description": "Bad Request"}`
   - **Cause**: Redirect URI mismatch
   - **Fix**: See `OAUTH_INVALID_GRANT_FIX.md` for detailed steps
   - Must be: `https://pharos.onrender.com/api/auth/google/callback`
   - Must match Google Cloud Console settings EXACTLY (no trailing slash)
   - Must be HTTPS (not HTTP)

2. **Check environment variables:**
   - All OAuth variables added?
   - JWT_SECRET_KEY generated?
   - FRONTEND_URL correct?

3. **Check Render logs:**
   - Look for OAuth-related errors
   - Check for missing environment variables

4. **OAuth code reuse:**
   - OAuth codes are single-use only
   - Refreshing callback page will fail
   - Start OAuth flow from beginning

### 📊 Success Criteria

- [ ] Render deployment completes successfully
- [ ] Health endpoint returns 200 OK
- [ ] Logs show "Database initialized successfully: sqlite"
- [ ] No "Connection refused" errors in logs
- [ ] Login page loads without errors
- [ ] Google OAuth button appears
- [ ] OAuth login flow completes successfully
- [ ] JWT token is issued
- [ ] User is redirected to authenticated page

### 📝 Notes

**SQLite Limitations (Temporary):**
- File-based storage (data in container filesystem)
- Limited concurrency (single writer)
- No PostgreSQL features (JSONB, full-text search)
- Data may be lost on container restart (Render free tier)

**This is a temporary solution** to unblock OAuth testing. For production, we need to:
1. Fix NeonDB connection retry at pool level, OR
2. Switch to different PostgreSQL provider (Supabase, Railway), OR
3. Upgrade NeonDB to paid tier (no auto-suspend)

### 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com
- **Render Logs:** https://dashboard.render.com/web/[service-id]/logs
- **Health Check:** https://pharos.onrender.com/health
- **Login Page:** https://pharos.onrender.com/login
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials

### 📚 Documentation

- [SQLITE_MIGRATION_GUIDE.md](./SQLITE_MIGRATION_GUIDE.md) - Complete migration guide
- [NEONDB_CONNECTION_FIX.md](./NEONDB_CONNECTION_FIX.md) - Original retry logic (kept for reference)
- [AUTH_TOKEN_SETUP.md](./AUTH_TOKEN_SETUP.md) - OAuth setup guide

---

**Last Updated:** January 26, 2026
**Status:** Waiting for manual steps in Render Dashboard
