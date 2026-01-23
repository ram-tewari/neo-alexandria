# Check Render Deployment Status
# Run this script to verify the cloud deployment is working

$RENDER_URL = "https://pharos.onrender.com"

Write-Host "🔍 Checking Render Deployment Status..." -ForegroundColor Cyan
Write-Host ""

# Check health endpoint
Write-Host "1. Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RENDER_URL/health" -Method GET -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Health check passed" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check docs endpoint
Write-Host "2. Testing /docs endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RENDER_URL/docs" -Method GET -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API docs accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ API docs failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check if ingestion endpoint exists (will return 401 without token, which is expected)
Write-Host "3. Testing /api/v1/ingestion endpoint (expect 401)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$RENDER_URL/api/v1/ingestion/worker/status" -Method GET -TimeoutSec 30
    Write-Host "   ✓ Ingestion endpoint accessible" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✓ Ingestion endpoint exists (401 = auth required, as expected)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Unexpected response: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📊 Deployment Status Summary:" -ForegroundColor Cyan
Write-Host "   URL: $RENDER_URL" -ForegroundColor Gray
Write-Host "   Check Render dashboard for detailed logs" -ForegroundColor Gray
Write-Host "   https://dashboard.render.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "   1. Check Render logs for 'Deployment mode: CLOUD'" -ForegroundColor Gray
Write-Host "   2. Verify no torch import errors" -ForegroundColor Gray
Write-Host "   3. Test ingestion with: curl -X POST $RENDER_URL/api/v1/ingestion/ingest/github.com/user/repo -H 'Authorization: Bearer \$PHAROS_ADMIN_TOKEN'" -ForegroundColor Gray
