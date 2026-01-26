# OAuth Redirect URI Fix

## Problem
Google OAuth error: `redirect_uri_mismatch` - The redirect URI in your request doesn't match what's configured in Google Cloud Console.

## Root Cause
Your application is sending a redirect URI that doesn't match the authorized redirect URIs in your Google OAuth app configuration.

## Current Configuration

### Backend Settings (settings.py)
```python
GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
```

### Staging Environment (.env.staging)
No GOOGLE_REDIRECT_URI specified - using default from settings.py

## Solution Steps

### Step 1: Determine Your Actual Redirect URI

Your application needs to use ONE of these redirect URIs consistently:

**For Local Development:**
```
http://localhost:8000/auth/google/callback
```

**For Render Deployment (Production):**
```
https://pharos.onrender.com/auth/google/callback
```

**For Frontend Development:**
```
http://localhost:5173/auth/google/callback
```

### Step 2: Configure Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add ALL of these:

```
http://localhost:8000/auth/google/callback
http://localhost:5173/auth/google/callback
https://pharos.onrender.com/auth/google/callback
```

6. Click **Save**

### Step 3: Update Backend Environment Variables

#### For Local Development (backend/.env or backend/config/.env)
```bash
# Google OAuth
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-secret-from-json-file>
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173
```

#### For Render Deployment (Environment Variables in Render Dashboard)
```bash
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-secret-from-json-file>
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/auth/google/callback
FRONTEND_URL=https://your-frontend-domain.com
```

### Step 4: Extract Client Secret from JSON File

Your downloaded JSON file contains the client secret. Extract it:

1. Open the file: `client_secret_91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com.json`
2. Find the `client_secret` field
3. Copy the value (it looks like: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`)
4. Add it to your environment variables

### Step 5: Update Staging Configuration

Add to `backend/.env.staging`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-secret-from-json-file>
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/auth/google/callback
```

## Testing

### Test Locally
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Navigate to: `http://localhost:8000/auth/google/login`
3. Should redirect to Google consent screen
4. After consent, should redirect back to: `http://localhost:8000/auth/google/callback`

### Test on Render
1. Deploy to Render
2. Navigate to: `https://pharos.onrender.com/auth/google/login`
3. Should redirect to Google consent screen
4. After consent, should redirect back to: `https://pharos.onrender.com/auth/google/callback`

## Common Issues

### Issue 1: Still Getting redirect_uri_mismatch
**Solution**: Wait 5-10 minutes after updating Google Cloud Console. Changes can take time to propagate.

### Issue 2: Different Error After Fix
**Solution**: Check backend logs for detailed error messages:
```bash
# Local
tail -f backend/logs/app.log

# Render
Check Render dashboard logs
```

### Issue 3: CORS Error
**Solution**: Ensure FRONTEND_URL is set correctly and CORS is configured in backend:
```python
# backend/app/main.py should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Verification Checklist

- [ ] Google Cloud Console has all redirect URIs added
- [ ] GOOGLE_CLIENT_ID is set in environment
- [ ] GOOGLE_CLIENT_SECRET is set in environment
- [ ] GOOGLE_REDIRECT_URI matches one of the authorized URIs
- [ ] FRONTEND_URL is set correctly
- [ ] Backend is restarted after environment changes
- [ ] Waited 5-10 minutes after Google Cloud Console changes

## Next Steps

After fixing the redirect URI:

1. Test OAuth flow locally
2. Test OAuth flow on Render
3. Verify user creation in database
4. Test JWT token generation
5. Test protected endpoints with OAuth token

## Related Files

- `backend/app/shared/oauth2.py` - OAuth provider implementation
- `backend/app/config/settings.py` - Configuration settings
- `backend/.env.staging` - Staging environment variables
- `backend/app/routers/auth.py` - Authentication endpoints (if exists)

## Security Notes

⚠️ **Never commit secrets to git!**
- Keep `.env` files in `.gitignore`
- Use Render environment variables for production
- Rotate secrets if accidentally exposed

## Support

If issues persist:
1. Check Google Cloud Console audit logs
2. Enable debug logging in oauth2.py
3. Verify network connectivity to Google OAuth endpoints
4. Check for firewall/proxy issues
