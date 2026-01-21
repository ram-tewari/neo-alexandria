# Render Deployment Checklist

**Date**: January 21, 2026  
**Status**: Ready to Deploy 🚀

## Pre-Deployment Verification ✅

- [x] Upstash Redis configured and tested
- [x] Neon PostgreSQL configured and tested
- [x] Qdrant Cloud configured and tested
- [x] `render.yaml` configuration file created
- [x] `requirements-cloud.txt` dependencies defined
- [x] `requirements-base.txt` dependencies defined
- [x] `.env.staging` file created (NOT committed)
- [x] Verification script passed all checks

## Deployment Steps

### 1. Repository Preparation

- [ ] Check git status: `git status`
- [ ] Verify `.env.staging` is NOT staged (should be in .gitignore)
- [ ] Add deployment files:
  ```powershell
  git add render.yaml
  git add requirements-cloud.txt
  git add requirements-base.txt
  git add app/
  ```
- [ ] Commit changes:
  ```powershell
  git commit -m "Add Phase 19 Cloud API deployment configuration"
  ```
- [ ] Push to GitHub:
  ```powershell
  git push origin main
  ```

### 2. Render Account Setup

- [ ] Go to https://render.com
- [ ] Sign up / Sign in (use GitHub for easy integration)
- [ ] Authorize Render to access your GitHub repositories

### 3. Deploy Using Blueprint

- [ ] In Render Dashboard, click "New" → "Blueprint"
- [ ] Select repository: `neo-alexandria-2.0`
- [ ] Render detects `render.yaml`
- [ ] Click "Apply"

### 4. Configure Environment Variables

Add these environment variables in Render dashboard:

#### Required Variables

- [ ] `MODE` = `CLOUD`
- [ ] `DATABASE_URL` = `postgresql://neondb_owner:npg_2Lv8pxVJzgyd@ep-fancy-grass-ah0xirjl-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require`
- [ ] `UPSTASH_REDIS_REST_URL` = `https://lucky-pug-47555.upstash.io`
- [ ] `UPSTASH_REDIS_REST_TOKEN` = `AbnDAAIncDFiZDgzMDAwZDNkNWU0YjFlYWFkZDc1ZTZhMjAxYmQyY3AxNDc1NTU`
- [ ] `QDRANT_URL` = `https://1387e31e-904c-48dc-8f3a-772c6da3621e.us-east4-0.gcp.cloud.qdrant.io`
- [ ] `QDRANT_API_KEY` = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.C-jSQs3q-hSN2Uw1O_Yu1CQFlOzyx1A5qA90orcOrhk`
- [ ] `PHAROS_ADMIN_TOKEN` = `staging-admin-token-change-me-in-production`

#### Optional Variables (have defaults)

- [ ] `MAX_QUEUE_SIZE` = `10`
- [ ] `TASK_TTL_SECONDS` = `3600`

### 5. Monitor Build

- [ ] Watch build logs in Render dashboard
- [ ] Wait for "Installing dependencies" phase (~2-3 minutes)
- [ ] Wait for "Starting service" phase (~1-2 minutes)
- [ ] Wait for "Health check passing" (~30 seconds)
- [ ] Note your app URL: `https://neo-alexandria-cloud-api.onrender.com`

### 6. Test Deployment

- [ ] Run test script:
  ```powershell
  cd backend
  .\test_render_deployment.ps1 -CloudApiUrl "https://neo-alexandria-cloud-api.onrender.com"
  ```

Expected results:
- [ ] ✅ Health check passes
- [ ] ✅ Authentication works (401 without token)
- [ ] ✅ Worker status retrieved with token
- [ ] ✅ Test job submitted successfully
- [ ] ✅ Queue status retrieved

### 7. Document Deployment

- [ ] Note your Render URL: `_______________________________`
- [ ] Update `PHASE19_QUICK_START.md` with actual URL
- [ ] Update `test_deployment.ps1` with actual URL
- [ ] Update `monitor_deployment.ps1` with actual URL

## Post-Deployment Tasks

### 8. Set Up Edge Worker

- [ ] Copy `.env.edge.template` to `.env.edge`
- [ ] Update `.env.edge` with cloud credentials
- [ ] Install edge dependencies: `pip install -r requirements-edge.txt`
- [ ] Test worker: `python worker.py`

### 9. Run End-to-End Test

- [ ] Submit test repository via Cloud API
- [ ] Start Edge Worker locally
- [ ] Monitor job processing
- [ ] Verify embeddings in Qdrant
- [ ] Check job history

### 10. Monitor for 24-48 Hours

- [ ] Check Render logs for errors
- [ ] Monitor Redis queue size
- [ ] Monitor Qdrant storage usage
- [ ] Monitor Neon database connections
- [ ] Test with multiple repositories

## Troubleshooting

### Build Fails

**Issue**: "Could not find requirements-cloud.txt"
- [ ] Verify `rootDir: backend` in `render.yaml`
- [ ] Check file is committed to repository

**Issue**: "Module not found"
- [ ] Check `requirements-cloud.txt` has all dependencies
- [ ] Verify `requirements-base.txt` is included

### Health Check Fails

**Issue**: "Health check timeout"
- [ ] Check Render logs for startup errors
- [ ] Verify all environment variables are set
- [ ] Test Redis connection manually
- [ ] Test database connection manually
- [ ] Test Qdrant connection manually

### Authentication Issues

**Issue**: "401 Unauthorized"
- [ ] Verify `PHAROS_ADMIN_TOKEN` matches in Render and requests
- [ ] Check token is not empty or default value

### Worker Not Processing

**Issue**: "Jobs stuck in queue"
- [ ] Verify Edge Worker is running: `python worker.py`
- [ ] Check worker logs for errors
- [ ] Verify Redis connection in worker
- [ ] Check Qdrant connection in worker

## Success Criteria

- [x] Infrastructure verified (Redis, Neon, Qdrant)
- [ ] Cloud API deployed to Render
- [ ] Health check passing
- [ ] Authentication working
- [ ] Job submission working
- [ ] Edge Worker running locally
- [ ] End-to-end workflow tested
- [ ] Embeddings stored in Qdrant
- [ ] No errors in logs

## Timeline

- ✅ Infrastructure Setup: 30 minutes (Complete)
- ⏳ Render Deployment: 15 minutes (In Progress)
  - Repository prep: 2 minutes
  - Render setup: 5 minutes
  - Build & deploy: 5-10 minutes
  - Testing: 2 minutes
- ⏳ Edge Worker Setup: 10 minutes (Next)
- ⏳ End-to-End Test: 5 minutes (Next)
- ⏳ Monitoring: 24-48 hours (Next)

## Resources

- **Deployment Guide**: `DEPLOY_TO_RENDER.md`
- **Quick Start**: `PHASE19_QUICK_START.md`
- **Test Script**: `test_render_deployment.ps1`
- **Monitor Script**: `monitor_deployment.ps1`
- **Verify Script**: `verify_staging_setup.py`
- **API Docs**: `docs/api/ingestion.md`
- **Render Docs**: https://render.com/docs

## Notes

- Free tier has 512MB RAM limit - Cloud API is optimized for this
- First deploy may take longer (~10 minutes)
- Subsequent deploys are faster (~3-5 minutes)
- Health checks run every 30 seconds
- Auto-deploy enabled on push to main branch

## Next Phase

After successful deployment and 24-48 hours of monitoring:
- [ ] Review logs and metrics
- [ ] Fix any issues found
- [ ] Optimize performance if needed
- [ ] Plan production deployment
- [ ] Generate production credentials
- [ ] Deploy to production environment

---

**Ready to deploy!** Follow the checklist above step by step.
