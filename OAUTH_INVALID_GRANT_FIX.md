# OAuth "invalid_grant" Error - Fix Guide

## Error Details

**Error from Google**: `{"error": "invalid_grant", "error_description": "Bad Request"}`

**Location**: Token exchange step in OAuth flow

**Impact**: Users cannot complete Google OAuth login

## Root Cause

The `invalid_grant` error from Google OAuth2 indicates a **redirect URI mismatch**. This happens when:
- The redirect URI used during authorization doesn't match the redirect URI used during token exchange
- The redirect URI doesn't match what's registered in Google Cloud Console

## Current Configuration

### Backend Code
- Authorization URL generation: Uses `GOOGLE_REDIRECT_URI` from environment
- Token exchange: Uses `GOOGLE_REDIRECT_URI` from environment
- **File**: `backend/app/shared/oauth2.py`

### Environment Variables (Render)
```bash
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
```

### Google Cloud Console
**Project**: Neo Alexandria
**OAuth Client ID**: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`

## Fix Steps

### Step 1: Verify Google Cloud Console Configuration

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find OAuth 2.0 Client ID: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`
3. Click "Edit"
4. Under "Authorized redirect URIs", ensure it includes **EXACTLY**:
   ```
   https://pharos.onrender.com/api/auth/google/callback
   ```
   - No trailing slash
   - Must be HTTPS (not HTTP)
   - Must match character-for-character

5. If not present, add it and click "Save"

### Step 2: Verify Render Environment Variable

1. Go to Render Dashboard: https://dashboard.render.com
2. Select service: `neo-alexandria-cloud-api`
3. Go to "Environment" tab
4. Verify `GOOGLE_REDIRECT_URI` is set to:
   ```
   https://pharos.onrender.com/api/auth/google/callback
   ```
5. If incorrect, update and redeploy

### Step 3: Test OAuth Flow

1. Clear browser cookies/cache for `pharos.onrender.com`
2. Start fresh OAuth flow from beginning
3. Click "Sign in with Google"
4. Complete authorization
5. Should redirect successfully with tokens

## Common Mistakes

### ❌ Wrong: Trailing Slash
```
https://pharos.onrender.com/api/auth/google/callback/
```

### ✅ Correct: No Trailing Slash
```
https://pharos.onrender.com/api/auth/google/callback
```

### ❌ Wrong: HTTP Instead of HTTPS
```
http://pharos.onrender.com/api/auth/google/callback
```

### ✅ Correct: HTTPS
```
https://pharos.onrender.com/api/auth/google/callback
```

### ❌ Wrong: Missing /api Prefix
```
https://pharos.onrender.com/auth/google/callback
```

### ✅ Correct: With /api Prefix
```
https://pharos.onrender.com/api/auth/google/callback
```

## Verification Checklist

- [ ] Google Cloud Console has redirect URI: `https://pharos.onrender.com/api/auth/google/callback`
- [ ] Render environment variable `GOOGLE_REDIRECT_URI` matches exactly
- [ ] No trailing slashes in either location
- [ ] Using HTTPS (not HTTP)
- [ ] Service redeployed after environment variable changes
- [ ] Testing with fresh OAuth flow (not reusing old codes)

## Alternative: Use Password Login

While fixing OAuth, users can still login with username/password:

**Test Credentials**:
- Username: `test@example.com`
- Password: `testpassword123`

## Additional Notes

### OAuth Code Reuse
- OAuth authorization codes are **single-use only**
- Refreshing the callback page will always fail
- Must start OAuth flow from beginning each time

### Code Expiration
- OAuth codes expire after ~10 minutes
- Complete the flow quickly after authorization

### Multiple Redirect URIs
You can register multiple redirect URIs in Google Cloud Console:
- `https://pharos.onrender.com/api/auth/google/callback` (production)
- `http://localhost:8000/api/auth/google/callback` (local development)

## Status

- ✅ Error identified: `invalid_grant` from Google
- ✅ Root cause: Redirect URI mismatch
- ⏳ **ACTION REQUIRED**: Verify Google Cloud Console configuration
- ⏳ **ACTION REQUIRED**: Verify Render environment variable
- ⏳ Test with fresh OAuth flow

## Related Files

- `backend/app/shared/oauth2.py` - OAuth provider implementation
- `backend/app/modules/auth/router.py` - OAuth callback endpoint
- `backend/app/config/settings.py` - Environment variable configuration
- `OAUTH_TOKEN_EXCHANGE_DEBUG.md` - Detailed debugging information
