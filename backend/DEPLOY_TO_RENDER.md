# Deploy Neo Alexandria to Render - Step by Step

**Status**: Infrastructure ✅ | Ready to Deploy 🚀

## Prerequisites Complete ✅

- ✅ Upstash Redis configured and tested
- ✅ Neon PostgreSQL configured and tested
- ✅ Qdrant Cloud configured and tested
- ✅ `render.yaml` configuration file ready
- ✅ `requirements-cloud.txt` dependencies defined
- ✅ `runtime.txt` specifies Python 3.11.9 (compatible with all dependencies)

## Deployment Steps

### Step 1: Prepare Repository (2 minutes)

**Important**: Do NOT commit `.env.staging` - it contains secrets!

```powershell
# Check what will be committed
git status

# Add only the necessary files
git add render.yaml
git add requirements-cloud.txt
git add app/
git add docs/

# Commit
git commit -m "Add Phase 19 Cloud API deployment configuration"

# Push to GitHub
git push origin main
```

### Step 2: Create Render Account (if needed)

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

### Step 3: Deploy Using Blueprint (5 minutes)

1. **In Render Dashboard**:
   - Click "New" → "Blueprint"
   - Select your GitHub repository: `neo-alexandria-2.0`
   - Render will detect `render.yaml`
   - Click "Apply"

2. **Configure Environment Variables**:
   
   Render will prompt you to add the following environment variables. Copy these values from your `.env.staging` file:

   ```bash
   MODE=CLOUD
   
   # Database
   DATABASE_URL=postgresql://neondb_owner:npg_2Lv8pxVJzgyd@ep-fancy-grass-ah0xirjl-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   
   # Redis
   UPSTASH_REDIS_REST_URL=https://lucky-pug-47555.upstash.io
   UPSTASH_REDIS_REST_TOKEN=AbnDAAIncDFiZDgzMDAwZDNkNWU0YjFlYWFkZDc1ZTZhMjAxYmQyY3AxNDc1NTU
   
   # Qdrant
   QDRANT_URL=https://1387e31e-904c-48dc-8f3a-772c6da3621e.us-east4-0.gcp.cloud.qdrant.io
   QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.C-jSQs3q-hSN2Uw1O_Yu1CQFlOzyx1A5qA90orcOrhk
   
   # Authentication (CHANGE THIS FOR PRODUCTION!)
   PHAROS_ADMIN_TOKEN=staging-admin-token-change-me-in-production
   
   # Optional (has defaults)
   MAX_QUEUE_SIZE=10
   TASK_TTL_SECONDS=3600
   ```

3. **Click "Create"**:
   - Render will start building your application
   - Build time: ~5-10 minutes
   - You'll see build logs in real-time

### Step 4: Wait for Deployment (5-10 minutes)

Monitor the build process:
- ✅ Installing dependencies
- ✅ Building application
- ✅ Starting service
- ✅ Health check passing

Your app URL will be: `https://neo-alexandria-cloud-api.onrender.com`

### Step 5: Test Deployment (2 minutes)

Once deployed, test your endpoints:

```powershell
# Set your Render URL (replace with your actual URL)
$CLOUD_API_URL = "https://neo-alexandria-cloud-api.onrender.com"
$TOKEN = "staging-admin-token-change-me-in-production"

# Test 1: Health check (should return 200)
Invoke-RestMethod -Uri "$CLOUD_API_URL/health"

# Test 2: Authentication (should return 401 without token)
try {
    Invoke-RestMethod -Uri "$CLOUD_API_URL/api/v1/ingestion/worker/status"
} catch {
    Write-Host "✅ Authentication working (401 expected)"
}

# Test 3: With valid token (should return 200)
$headers = @{
    "Authorization" = "Bearer $TOKEN"
}
Invoke-RestMethod -Uri "$CLOUD_API_URL/api/v1/ingestion/worker/status" -Headers $headers

# Test 4: Submit test job
Invoke-RestMethod -Method Post `
    -Uri "$CLOUD_API_URL/api/v1/ingestion/ingest/github.com/octocat/Hello-World" `
    -Headers $headers
```

## Alternative: Manual Deployment (if Blueprint doesn't work)

### Option B: Manual Web Service Creation

1. **In Render Dashboard**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select branch: `main`

2. **Configure Service**:
   ```
   Name: neo-alexandria-cloud-api
   Environment: Python 3
   Region: Oregon (or closest to you)
   Branch: main
   Build Command: pip install -r requirements-cloud.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Add Environment Variables** (same as above)

4. **Click "Create Web Service"**

## Troubleshooting

### Build Fails

**Error**: "Could not find a version that satisfies the requirement qdrant-client==1.7.0"
- **Fix**: Python version mismatch. Ensure `runtime.txt` exists with `python-3.11.9`
- Render will automatically use this version instead of defaulting to 3.13

**Error**: "Could not find requirements-cloud.txt"
- **Fix**: Make sure you're in the `backend` directory in your repo
- Update `render.yaml` to specify `rootDir: backend`

**Error**: "Module not found"
- **Fix**: Check `requirements-cloud.txt` has all dependencies
- Verify Python version is 3.11+

### Health Check Fails

**Error**: "Health check timeout"
- **Fix**: Check Render logs for startup errors
- Verify all environment variables are set
- Check Redis/Database/Qdrant connections

### Authentication Issues

**Error**: "401 Unauthorized"
- **Fix**: Verify `PHAROS_ADMIN_TOKEN` is set correctly
- Check you're using the same token in requests

## Post-Deployment

### 1. Note Your URLs

```
Cloud API: https://neo-alexandria-cloud-api.onrender.com
Health: https://neo-alexandria-cloud-api.onrender.com/health
API Docs: https://neo-alexandria-cloud-api.onrender.com/docs
```

### 2. Update Documentation

Update these files with your actual Render URL:
- `PHASE19_QUICK_START.md`
- `test_deployment.ps1`
- `monitor_deployment.ps1`

### 3. Set Up Edge Worker

See `PHASE19_QUICK_START.md` section "Set Up Edge Worker Locally"

### 4. Run End-to-End Test

```powershell
# Submit a test repository
$CLOUD_API_URL = "https://neo-alexandria-cloud-api.onrender.com"
$TOKEN = "staging-admin-token-change-me-in-production"

Invoke-RestMethod -Method Post `
    -Uri "$CLOUD_API_URL/api/v1/ingestion/ingest/github.com/octocat/Hello-World" `
    -Headers @{"Authorization"="Bearer $TOKEN"}

# Monitor worker status
Invoke-RestMethod -Uri "$CLOUD_API_URL/api/v1/ingestion/worker/status" `
    -Headers @{"Authorization"="Bearer $TOKEN"}
```

## Expected Timeline

- ✅ Infrastructure Setup: Complete (30 minutes)
- ⏳ Render Deployment: In Progress (15 minutes)
  - Repository prep: 2 minutes
  - Render setup: 5 minutes
  - Build & deploy: 5-10 minutes
  - Testing: 2 minutes
- ⏳ Edge Worker Setup: Next (10 minutes)
- ⏳ End-to-End Test: Next (5 minutes)

## Next Steps After Deployment

1. ✅ Deploy Cloud API to Render
2. ⏳ Set up Edge Worker locally
3. ⏳ Run end-to-end workflow test
4. ⏳ Monitor for 24-48 hours
5. ⏳ Fix any issues
6. ⏳ Deploy to production

## Support Resources

- **Render Docs**: https://render.com/docs
- **Deployment Guide**: `docs/guides/phase19-deployment.md`
- **API Documentation**: `docs/api/ingestion.md`
- **Monitoring Guide**: `docs/guides/phase19-monitoring.md`

---

**Ready to deploy!** 🚀

Follow the steps above and you'll have your Cloud API running in ~15 minutes.
