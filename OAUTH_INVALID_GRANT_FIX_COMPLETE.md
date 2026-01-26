# OAuth Invalid Grant Fix - Complete Solution

## Problem Identified

From your logs:
```
Google token exchange - redirect_uri: https://pharos.onrender.com/api/auth/google/callback
Google token exchange failed: 400 - {"error": "invalid_grant","error_description": "Bad Request"}
```

**Root Cause**: The redirect URI `https://pharos.onrender.com/api/auth/google/callback` is not registered in your Google Cloud Console OAuth app.

## Quick Fix Steps

### Step 1: Add Redirect URI to Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`
5. Under **Authorized redirect URIs**, add:

```
https://pharos.onrender.com/api/auth/google/callback
```

6. Click **Save**
7. **Wait 5-10 minutes** for changes to propagate

### Step 2: Update Render Environment Variables

In your Render dashboard, add/update these environment variables:

```bash
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<get-from-json-file>
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
FRONTEND_URL=<your-frontend-url>
```

### Step 3: Extract Client Secret

Your downloaded JSON file contains the secret. To extract it:

**Option A - Manual:**
1. Open: `client_secret_91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com.json`
2. Find the `client_secret` field
3. Copy the value (format: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`)

**Option B - PowerShell:**
```powershell
$json = Get-Content "C:\Users\rooma\Downloads\client_secret_91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com.json" | ConvertFrom-Json
$json.web.client_secret
```

### Step 4: Update Backend Configuration

Update `backend/.env.staging`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-secret-here>
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback

# Frontend URL (for redirect after OAuth)
FRONTEND_URL=https://your-frontend-domain.com
```

## Complete Redirect URI List

Add ALL of these to Google Cloud Console for different environments:

```
# Production (Render)
https://pharos.onrender.com/api/auth/google/callback

# Local Development (Backend)
http://localhost:8000/api/auth/google/callback

# Local Development (Frontend dev server)
http://localhost:5173/auth/callback
```

## Testing

### Test on Render (Production)

1. Navigate to: `https://pharos.onrender.com/api/auth/google`
2. Should redirect to Google consent screen
3. After consent, should redirect to: `https://pharos.onrender.com/api/auth/google/callback`
4. Then redirect to frontend with tokens

### Test Locally

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Navigate to: `http://localhost:8000/api/auth/google`
3. Should redirect to Google consent screen
4. After consent, should redirect to: `http://localhost:8000/api/auth/google/callback`

## Verification Checklist

- [ ] Google Cloud Console has redirect URI: `https://pharos.onrender.com/api/auth/google/callback`
- [ ] Waited 5-10 minutes after Google Cloud Console update
- [ ] GOOGLE_CLIENT_ID set in Render environment variables
- [ ] GOOGLE_CLIENT_SECRET set in Render environment variables
- [ ] GOOGLE_REDIRECT_URI set in Render environment variables
- [ ] FRONTEND_URL set in Render environment variables
- [ ] Render service restarted after environment variable changes
- [ ] Test OAuth flow end-to-end

## Understanding the Flow

```
1. User clicks "Login with Google"
   → Frontend redirects to: GET /api/auth/google

2. Backend generates authorization URL
   → Returns: https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=https://pharos.onrender.com/api/auth/google/callback

3. User consents on Google
   → Google redirects to: https://pharos.onrender.com/api/auth/google/callback?code=...&state=...

4. Backend exchanges code for token
   → POST https://oauth2.googleapis.com/token
   → This is where it's failing because redirect_uri doesn't match

5. Backend gets user info
   → GET https://www.googleapis.com/oauth2/v2/userinfo

6. Backend creates JWT tokens
   → Redirects to: {FRONTEND_URL}/auth/callback?access_token=...&refresh_token=...
```

## Common Issues

### Issue 1: Still Getting "invalid_grant"
**Cause**: Google Cloud Console changes haven't propagated yet
**Solution**: Wait 10-15 minutes, clear browser cache, try again

### Issue 2: "redirect_uri_mismatch" 
**Cause**: Typo in redirect URI or not saved in Google Cloud Console
**Solution**: Double-check exact URI matches, including `/api` prefix

### Issue 3: CORS Error After OAuth
**Cause**: FRONTEND_URL not configured or CORS not enabled
**Solution**: Check `backend/app/main.py` has CORS middleware configured

### Issue 4: Frontend Not Receiving Tokens
**Cause**: FRONTEND_URL not set or incorrect
**Solution**: Verify FRONTEND_URL in Render environment variables

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit secrets to git**
   - Keep `.env` files in `.gitignore`
   - Use Render environment variables for production

2. **Use HTTPS in production**
   - All redirect URIs should use `https://` (except localhost)
   - Render provides HTTPS by default

3. **Validate state token**
   - The `state` parameter prevents CSRF attacks
   - Backend validates this automatically

4. **Rotate secrets if exposed**
   - If you accidentally commit secrets, rotate them immediately
   - Generate new client secret in Google Cloud Console

## Next Steps After Fix

1. ✅ Test OAuth flow on Render
2. ✅ Verify user creation in database
3. ✅ Test JWT token generation
4. ✅ Test protected endpoints with OAuth token
5. ✅ Test token refresh flow
6. ✅ Test logout flow

## Related Files

- `backend/app/modules/auth/router.py` - Auth endpoints (prefix: `/api/auth`)
- `backend/app/shared/oauth2.py` - OAuth provider implementation
- `backend/app/config/settings.py` - Configuration settings
- `backend/.env.staging` - Staging environment variables

## Support Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI OAuth2 Guide](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- Backend logs: Check Render dashboard for detailed error messages
