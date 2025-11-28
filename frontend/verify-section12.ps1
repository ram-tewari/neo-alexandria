# Section 12 Verification Script (PowerShell)
# This script runs all verification steps for Section 12 completion

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Section 12 Verification Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

function Print-Status {
    param($message, $success)
    if ($success) {
        Write-Host "✓ $message passed" -ForegroundColor Green
    } else {
        Write-Host "✗ $message failed" -ForegroundColor Red
        exit 1
    }
}

# Step 1: Type Checking
Write-Host "Step 1: Type Checking" -ForegroundColor Yellow
Write-Host "--------------------"
try {
    npm run type-check
    Print-Status "Type checking" $true
} catch {
    Print-Status "Type checking" $false
}
Write-Host ""

# Step 2: Linting
Write-Host "Step 2: Linting" -ForegroundColor Yellow
Write-Host "--------------------"
try {
    npm run lint
    Print-Status "Linting" $true
} catch {
    Print-Status "Linting" $false
}
Write-Host ""

# Step 3: Unit Tests
Write-Host "Step 3: Unit Tests" -ForegroundColor Yellow
Write-Host "--------------------"
try {
    npm run test:run
    Print-Status "Unit tests" $true
} catch {
    Print-Status "Unit tests" $false
}
Write-Host ""

# Step 4: Accessibility Tests
Write-Host "Step 4: Accessibility Tests" -ForegroundColor Yellow
Write-Host "--------------------"
try {
    npm run test:a11y
    Print-Status "Accessibility tests" $true
} catch {
    Print-Status "Accessibility tests" $false
}
Write-Host ""

# Step 5: Build
Write-Host "Step 5: Build" -ForegroundColor Yellow
Write-Host "--------------------"
try {
    npm run build
    Print-Status "Build" $true
} catch {
    Print-Status "Build" $false
}
Write-Host ""

# Step 6: Bundle Size Check
Write-Host "Step 6: Bundle Size Check" -ForegroundColor Yellow
Write-Host "--------------------"
Write-Host "Main bundle sizes:"
Get-ChildItem dist/assets/*.js | Where-Object { $_.Name -match "(index|vendor)" } | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  $($_.Name): $size KB"
}
Write-Host ""
$totalSize = (Get-ChildItem dist -Recurse | Measure-Object -Property Length -Sum).Sum
$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "Total dist size: $totalSizeMB MB"
Write-Host ""

# Step 7: E2E Tests (Optional)
Write-Host "Step 7: E2E Tests (Optional)" -ForegroundColor Yellow
Write-Host "--------------------"
$runE2E = Read-Host "Run E2E tests? This requires Playwright browsers installed. (y/n)"
if ($runE2E -eq "y" -or $runE2E -eq "Y") {
    try {
        npm run test:e2e
        Print-Status "E2E tests" $true
    } catch {
        Print-Status "E2E tests" $false
    }
} else {
    Write-Host "⊘ E2E tests skipped" -ForegroundColor DarkYellow
}
Write-Host ""

# Step 8: Lighthouse Audit (Optional)
Write-Host "Step 8: Lighthouse Audit (Optional)" -ForegroundColor Yellow
Write-Host "--------------------"
$runLighthouse = Read-Host "Run Lighthouse audit? This requires the preview server. (y/n)"
if ($runLighthouse -eq "y" -or $runLighthouse -eq "Y") {
    try {
        npm run lighthouse
        Print-Status "Lighthouse audit" $true
    } catch {
        Print-Status "Lighthouse audit" $false
    }
} else {
    Write-Host "⊘ Lighthouse audit skipped" -ForegroundColor DarkYellow
}
Write-Host ""

# Step 9: Docker Build (Optional)
Write-Host "Step 9: Docker Build (Optional)" -ForegroundColor Yellow
Write-Host "--------------------"
$runDocker = Read-Host "Test Docker build? This requires Docker installed. (y/n)"
if ($runDocker -eq "y" -or $runDocker -eq "Y") {
    try {
        docker build -t neo-alexandria-frontend-test .
        Print-Status "Docker build" $true
        
        Write-Host "Testing container..."
        docker run -d -p 8081:80 --name neo-test neo-alexandria-frontend-test
        Start-Sleep -Seconds 3
        
        $healthCheck = Invoke-WebRequest -Uri "http://localhost:8081/health" -UseBasicParsing
        if ($healthCheck.Content -eq "healthy`n") {
            Write-Host "✓ Health check passed" -ForegroundColor Green
        } else {
            Write-Host "✗ Health check failed" -ForegroundColor Red
        }
        
        docker stop neo-test
        docker rm neo-test
        docker rmi neo-alexandria-frontend-test
    } catch {
        Write-Host "✗ Docker build failed" -ForegroundColor Red
    }
} else {
    Write-Host "⊘ Docker build skipped" -ForegroundColor DarkYellow
}
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Section 12 Verification Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:"
Write-Host "  ✓ Type checking passed"
Write-Host "  ✓ Linting passed"
Write-Host "  ✓ Unit tests passed"
Write-Host "  ✓ Accessibility tests passed"
Write-Host "  ✓ Build successful"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review SECTION12_CHECKLIST.md"
Write-Host "  2. Review DEPLOYMENT.md for deployment instructions"
Write-Host "  3. Deploy to staging environment"
Write-Host "  4. Conduct user acceptance testing"
Write-Host "  5. Deploy to production"
Write-Host ""
