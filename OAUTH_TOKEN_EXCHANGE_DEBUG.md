# OAuth Token Exchange Debugging

## Error: "Failed to exchange code for token"

### Current Status
- **Error Location**: `backend/app/shared/oauth2.py` - `GoogleOAuth2Provider.exchange_code_for_token()`
- **Error Message**: Generic "Failed to exchange code for token" without details
- **Impact**: Users cannot complete Google OAuth login

### Likely Causes

1. **Redirect URI Mismatch** (Most Common)
   - Google Console: `https://pharos.onrender.com/api/auth/google/callback`
   - Environment Variable: Check `GOOGLE_REDIRECT_URI` in Render
   - **Issue**: Must match EXACTLY (including trailing slashes, http vs https)

2. **Authorization Code Reuse**
   - OAuth codes are single-use only
   - Refreshing the callback page will fail
   - **Solution**: Start OAuth flow from beginning

3. **Client Credentials Mismatch**
   - Client ID: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`
   - Client Secret: `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`
   - **Issue**: Must match Google Cloud Console exactly

4. **Code Expiration**
   - OAuth codes expire after ~10 minutes
   - **Solution**: Complete flow quickly

### Environment Variables to Check

```bash
# In Render Dashboard
GOOGLE_CLIENT_ID=91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
```

### Google Cloud Console Settings

**Authorized redirect URIs** must include:
- `https://pharos.onrender.com/api/auth/google/callback` (production)
- `http://localhost:8000/api/auth/google/callback` (local testing)

### Actual Error from Google

```json
{
  "error": "invalid_grant",
  "error_description": "Bad Request"
}
```

**Root Cause**: `invalid_grant` error indicates redirect URI mismatch or code reuse.

### Diagnosis

The error `invalid_grant` from Google OAuth means:
1. **Redirect URI mismatch** (90% of cases) - The redirect URI in the token exchange request doesn't match what's registered in Google Cloud Console
2. **Code already used** - OAuth codes are single-use; refreshing the page will fail
3. **Code expired** - Codes expire after ~10 minutes

### Solution

**Check Render Environment Variable**:
```bash
GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback
```

**Must match EXACTLY in Google Cloud Console**:
- Go to: https://console.cloud.google.com/apis/credentials
- Edit OAuth 2.0 Client ID: `91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com`
- Under "Authorized redirect URIs", ensure it includes:
  - `https://pharos.onrender.com/api/auth/google/callback` (exact match, no trailing slash)

### Next Steps

1. ✅ Add detailed error logging to see actual Google error response
2. ✅ Identified error: `invalid_grant` - redirect URI mismatch
3. ⏳ **ACTION REQUIRED**: Verify `GOOGLE_REDIRECT_URI` in Render dashboard
4. ⏳ **ACTION REQUIRED**: Verify redirect URI in Google Cloud Console matches exactly
5. ⏳ Test with fresh OAuth flow (don't reuse codes)

### Enhanced Error Logging

Added detailed logging to capture:
- HTTP status code from Google
- Full error response body
- Request parameters (sanitized)
- Redirect URI being used

This will help identify the exact issue.
