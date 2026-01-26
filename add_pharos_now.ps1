# Add pharos repository - Ready to run!
# Your token is already included

$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMzYzZjYjAtNGMxMC00NmJhLWI5YWQtOGNhODJmYzAwOGZhIiwidXNlcm5hbWUiOiJSYW0gVGV3YXJpIiwidGllciI6ImZyZWUiLCJzY29wZXMiOltdLCJleHAiOjE3Njk0NjExMzUsInR5cGUiOiJhY2Nlc3MifQ.vXNvB1r-HWv7KcLlL-qEQ90nkA8Ty_FKwNZHbdAPREc"

Write-Host "Adding repository: https://github.com/ram-tewari/pharos" -ForegroundColor Cyan
Write-Host "User: Ram Tewari (ram.tewari.2023@gmail.com)" -ForegroundColor Gray
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    git_url = "https://github.com/ram-tewari/pharos"
} | ConvertTo-Json

try {
    Write-Host "Sending request..." -ForegroundColor Yellow
    
    $response = Invoke-RestMethod `
        -Uri "https://pharos.onrender.com/api/resources/ingest-repo" `
        -Method Post `
        -Headers $headers `
        -Body $body

    Write-Host ""
    Write-Host "✓ SUCCESS! Repository ingestion started" -ForegroundColor Green
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Task ID:  $($response.task_id)" -ForegroundColor White
    Write-Host "Status:   $($response.status)" -ForegroundColor White
    Write-Host "Message:  $($response.message)" -ForegroundColor White
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "What's happening now:" -ForegroundColor Yellow
    Write-Host "  1. Cloning your repository from GitHub" -ForegroundColor Gray
    Write-Host "  2. Scanning all files" -ForegroundColor Gray
    Write-Host "  3. Creating resources in your library" -ForegroundColor Gray
    Write-Host "  4. Processing in background (may take a few minutes)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Check status:" -ForegroundColor Yellow
    Write-Host "  curl -H 'Authorization: Bearer $token' \" -ForegroundColor Gray
    Write-Host "    https://pharos.onrender.com/api/resources/ingest-status/$($response.task_id)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or view in browser:" -ForegroundColor Yellow
    Write-Host "  https://pharos.onrender.com/repositories" -ForegroundColor Gray

} catch {
    Write-Host ""
    Write-Host "✗ ERROR" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host ""
            Write-Host "Token expired or invalid. Please get a new token." -ForegroundColor Yellow
        } elseif ($statusCode -eq 429) {
            Write-Host ""
            Write-Host "Rate limit exceeded. Wait a minute and try again." -ForegroundColor Yellow
        } elseif ($statusCode -eq 400) {
            Write-Host ""
            Write-Host "Bad request. Check if repository URL is correct." -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
