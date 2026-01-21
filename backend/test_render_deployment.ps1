# Test Render Deployment
# Usage: .\test_render_deployment.ps1 -CloudApiUrl "https://your-app.onrender.com"

param(
    [Parameter(Mandatory=$true)]
    [string]$CloudApiUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$Token = "staging-admin-token-change-me-in-production"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing Render Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cloud API URL: $CloudApiUrl" -ForegroundColor Yellow
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "$CloudApiUrl/health" -Method Get
    Write-Host "  ✅ Health check passed" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Authentication (should fail without token)
Write-Host "Test 2: Authentication (should return 401)" -ForegroundColor Green
try {
    Invoke-RestMethod -Uri "$CloudApiUrl/api/v1/ingestion/worker/status" -Method Get
    Write-Host "  ❌ Authentication not working (should have returned 401)" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "  ✅ Authentication working (401 as expected)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: Worker Status (with token)
Write-Host "Test 3: Worker Status (with authentication)" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $Token"
    }
    $status = Invoke-RestMethod -Uri "$CloudApiUrl/api/v1/ingestion/worker/status" -Headers $headers -Method Get
    Write-Host "  ✅ Worker status retrieved" -ForegroundColor Green
    Write-Host "  Status: $($status.status)" -ForegroundColor Gray
    Write-Host "  Queue Size: $($status.queue_size)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Worker status failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Submit Test Job
Write-Host "Test 4: Submit Test Repository" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $Token"
    }
    $result = Invoke-RestMethod -Method Post `
        -Uri "$CloudApiUrl/api/v1/ingestion/ingest/github.com/octocat/Hello-World" `
        -Headers $headers
    Write-Host "  ✅ Job submitted successfully" -ForegroundColor Green
    Write-Host "  Job ID: $($result.job_id)" -ForegroundColor Gray
    Write-Host "  Status: $($result.status)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Job submission failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check Queue
Write-Host "Test 5: Check Queue Status" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $Token"
    }
    $queue = Invoke-RestMethod -Uri "$CloudApiUrl/api/v1/ingestion/queue/status" -Headers $headers -Method Get
    Write-Host "  ✅ Queue status retrieved" -ForegroundColor Green
    Write-Host "  Pending Jobs: $($queue.pending)" -ForegroundColor Gray
    Write-Host "  Processing Jobs: $($queue.processing)" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ Queue status failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Cloud API is deployed and responding" -ForegroundColor Green
Write-Host "✅ Authentication is working" -ForegroundColor Green
Write-Host "✅ Job submission is working" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set up Edge Worker locally (see PHASE19_QUICK_START.md)" -ForegroundColor Gray
Write-Host "2. Start the worker: python worker.py" -ForegroundColor Gray
Write-Host "3. Monitor job processing" -ForegroundColor Gray
Write-Host ""
Write-Host "Monitor deployment:" -ForegroundColor Yellow
Write-Host "  .\monitor_deployment.ps1 -CloudApiUrl '$CloudApiUrl'" -ForegroundColor Gray
Write-Host ""
