# Complete OAuth and Authentication Fix Guide

## Current Issues

1. ❌ Google OAuth failing with `invalid_grant` error
2. ❌ Test user password login not working
3. ✅ Redirect URI verified in both Google Console and Render

## Issue Analysis

Since the redirect URI is verified and still failing, the issue is likely:

1. **Client Secret Mismatch** - The secret in Render doesn't match Google Console
2. **Empty Database** - SQLite database doesn't have the test user
3. **Authorization URL Mismatch** - The redirect_uri used during authorization doesn't match token exchange

## Complete Fix Steps

### Step 1: Verify Client Credentials Match

**In Google Cloud Console:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on OAuth 2.0 Client ID: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`
3. Note the **Client Secret** (it should start with `GOCSPX-`)

**In Render Dashboard:**
1. Go to: https://dashboard.render.com
2. Select: `neo-alexandria-cloud-api`
3. Go to "Environment" tab
4. Verify `GOOGLE_CLIENT_SECRET` matches EXACTLY what's in Google Console

### Step 2: Create Test User in Database

The SQLite database is empty after migration. Run this command to create the test user:

```bash
# SSH into Render or run locally against production database
python backend/scripts/create_test_user.py
```

This will create:
- Email: `test@example.com`
- Password: `testpassword123`
- Username: `testuser`

### Step 3: Check Render Logs for Detailed OAuth Info

After the enhanced logging, check Render logs for:

```
Google token exchange - redirect_uri: https://pharos.onrender.com/api/auth/google/callback
Google token exchange - client_id: 91993543328-r1aahn...
Google token exchange - code: 4/0ASc3gC3xKdukn...
```

This will show you EXACTLY what redirect_uri is being sent to Google.

### Step 4: Common OAuth Mismatch Scenarios

#### Scenario A: Environment Variable Has Wrong Value

**Symptom**: Logs show different redirect_uri than expected

**Fix**: Update `GOOGLE_REDIRECT_URI` in Render to:
```
https://pharos.onrender.com/api/auth/google/callback
```

#### Scenario B: Google Console Has Multiple URIs

**Symptom**: Google Console shows multiple redirect URIs

**Fix**: Ensure the EXACT URI is registered:
```
https://pharos.onrender.com/api/auth/google/callback
```

Remove any similar but different URIs like:
- `https://pharos.onrender.com/api/auth/google/callback/` (trailing slash)
- `http://pharos.onrender.com/api/auth/google/callback` (HTTP not HTTPS)
- `https://pharos.onrender.com/auth/google/callback` (missing /api)

#### Scenario C: Client Secret Mismatch

**Symptom**: `invalid_client` error (different from `invalid_grant`)

**Fix**: Regenerate client secret in Google Console and update Render

### Step 5: Test Password Login First

Before testing OAuth, verify basic auth works:

1. Create test user (Step 2)
2. Try password login at: `https://pharos.onrender.com/api/auth/login`
3. Use credentials:
   - username: `test@example.com`
   - password: `testpassword123`

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Step 6: Alternative - Use Local Frontend with Production Backend

If OAuth continues to fail, you can test with local frontend:

1. Update `GOOGLE_REDIRECT_URI` in Render to:
   ```
   http://localhost:8000/api/auth/google/callback
   ```

2. Add this URI to Google Console authorized redirect URIs

3. Run backend locally:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. Test OAuth flow locally where you can see detailed logs

## Diagnostic Commands

### Check if test user exists:
```bash
# In Render shell or locally
python -c "
import asyncio
from app.shared.database import get_db_session
from app.database.models import User
from sqlalchemy import select

async def check():
    async for db in get_db_session():
        result = await db.execute(select(User).where(User.email == 'test@example.com'))
        user = result.scalar_one_or_none()
        if user:
            print(f'User exists: {user.email}, Active: {user.is_active}')
        else:
            print('User does not exist')
        break

asyncio.run(check())
"
```

### Check environment variables:
```bash
# In Render shell
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_REDIRECT_URI
# Don't echo CLIENT_SECRET (sensitive)
```

### Test token exchange manually:
```bash
# Replace with actual values
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=YOUR_AUTH_CODE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://pharos.onrender.com/api/auth/google/callback"
```

## Expected Render Logs After Fix

```
INFO - Google token exchange - redirect_uri: https://pharos.onrender.com/api/auth/google/callback
INFO - Google token exchange - client_id: 91993543328-r1aahn...
INFO - Google token exchange - code: 4/0ASc3gC3xKdukn...
INFO - Successfully exchanged Google authorization code for token
INFO - Successfully retrieved Google user info for: your.email@gmail.com
INFO - Google OAuth2 login successful for user: Your Name
```

## Next Steps

1. ✅ Enhanced logging added to `backend/app/shared/oauth2.py`
2. ✅ Test user creation script created: `backend/scripts/create_test_user.py`
3. ⏳ **ACTION REQUIRED**: Run test user creation script
4. ⏳ **ACTION REQUIRED**: Verify client secret matches
5. ⏳ **ACTION REQUIRED**: Check Render logs for actual redirect_uri being sent
6. ⏳ Test password login first
7. ⏳ Test OAuth with fresh flow

## Files Modified

- `backend/app/shared/oauth2.py` - Added detailed logging
- `backend/scripts/create_test_user.py` - New script to create test user

## Commit and Deploy

```bash
git add backend/app/shared/oauth2.py backend/scripts/create_test_user.py OAUTH_AND_AUTH_COMPLETE_FIX.md
git commit -m "fix: add detailed OAuth logging and test user creation script"
git push origin master
```

Wait for Render to redeploy, then check logs during next OAuth attempt.
