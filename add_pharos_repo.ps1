# Add pharos repository to Neo Alexandria
# Run this script after getting your JWT token

Write-Host "Adding repository: https://github.com/ram-tewari/pharos" -ForegroundColor Cyan
Write-Host ""

# Prompt for JWT token
$token = Read-Host "Enter your JWT token (from browser DevTools or login response)"

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "Error: Token is required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Sending request to API..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    git_url = "https://github.com/ram-tewari/pharos"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "https://pharos.onrender.com/api/resources/ingest-repo" `
        -Method Post `
        -Headers $headers `
        -Body $body

    Write-Host ""
    Write-Host "✓ Repository ingestion started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task ID: $($response.task_id)" -ForegroundColor Cyan
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "Message: $($response.message)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The repository is being processed in the background." -ForegroundColor Yellow
    Write-Host "This may take a few minutes depending on repository size." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check status with:" -ForegroundColor White
    Write-Host "curl -H 'Authorization: Bearer $token' https://pharos.onrender.com/api/resources/ingest-status/$($response.task_id)" -ForegroundColor Gray

} catch {
    Write-Host ""
    Write-Host "✗ Error adding repository:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host ""
            Write-Host "Your token may be expired or invalid. Try logging in again." -ForegroundColor Yellow
        } elseif ($statusCode -eq 429) {
            Write-Host ""
            Write-Host "Rate limit exceeded. Please wait a minute and try again." -ForegroundColor Yellow
        }
    }
}
