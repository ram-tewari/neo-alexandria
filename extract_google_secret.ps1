# Extract Google OAuth Client Secret from JSON file
# Usage: .\extract_google_secret.ps1

$jsonPath = "C:\Users\rooma\Downloads\client_secret_91993543328-r1aahn2r13g53jm7e89taf5qaovlhm51.apps.googleusercontent.com.json"

if (Test-Path $jsonPath) {
    Write-Host "Reading Google OAuth credentials..." -ForegroundColor Green
    
    $json = Get-Content $jsonPath | ConvertFrom-Json
    
    Write-Host "`nClient ID:" -ForegroundColor Yellow
    Write-Host $json.web.client_id
    
    Write-Host "`nClient Secret:" -ForegroundColor Yellow
    Write-Host $json.web.client_secret
    
    Write-Host "`nAuthorized Redirect URIs (currently configured):" -ForegroundColor Yellow
    $json.web.redirect_uris | ForEach-Object { Write-Host "  - $_" }
    
    Write-Host "`n=== Add These to Render Environment Variables ===" -ForegroundColor Cyan
    Write-Host "GOOGLE_CLIENT_ID=$($json.web.client_id)"
    Write-Host "GOOGLE_CLIENT_SECRET=$($json.web.client_secret)"
    Write-Host "GOOGLE_REDIRECT_URI=https://pharos.onrender.com/api/auth/google/callback"
    
    Write-Host "`n=== Add This to Google Cloud Console ===" -ForegroundColor Cyan
    Write-Host "https://pharos.onrender.com/api/auth/google/callback"
    
} else {
    Write-Host "Error: JSON file not found at: $jsonPath" -ForegroundColor Red
    Write-Host "Please update the path in this script." -ForegroundColor Yellow
}
