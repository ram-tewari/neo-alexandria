# Model Rollback Script
# This script rolls back to a previous model version

param(
    [Parameter(Mandatory=$false)]
    [string]$Version,
    
    [Parameter(Mandatory=$false)]
    [string]$Reason = "Manual rollback",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Model Rollback Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Version) {
    Write-Host "Target version: $Version"
} else {
    Write-Host "Target version: Previous production version"
}
Write-Host "Reason: $Reason"
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Change to backend directory
Push-Location $BackendDir

try {
    # Confirm rollback (unless forced)
    if (-not $Force) {
        Write-Host "⚠ WARNING: This will rollback the production model" -ForegroundColor Yellow
        Write-Host ""
        $confirmation = Read-Host "Are you sure you want to proceed? (yes/no)"
        
        if ($confirmation -ne "yes") {
            Write-Host "Rollback cancelled" -ForegroundColor Yellow
            exit 0
        }
        Write-Host ""
    }
    
    # Step 1: Load previous version
    Write-Host "Step 1: Loading previous version..." -ForegroundColor Yellow
    Write-Host "----------------------------------------"
    
    if ($Version) {
        Write-Host "Rolling back to specified version: $Version"
    } else {
        Write-Host "Rolling back to previous production version"
    }
    
    Write-Host ""
    
    # Step 2: Switch traffic
    Write-Host "Step 2: Switching traffic..." -ForegroundColor Yellow
    Write-Host "----------------------------------------"
    
    if ($Version) {
        # Rollback to specific version using model versioning
        python scripts/deployment/model_versioning.py promote --version $Version
    } else {
        # Rollback to previous version using rollback monitor
        python scripts/deployment/rollback_monitor.py rollback --reason $Reason
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ Rollback failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "✓ Traffic switched to previous version" -ForegroundColor Green
    Write-Host ""
    
    # Step 3: Verify health
    Write-Host "Step 3: Verifying health..." -ForegroundColor Yellow
    Write-Host "----------------------------------------"
    
    Write-Host "Checking production metrics..."
    python scripts/deployment/rollback_monitor.py metrics
    
    Write-Host ""
    Write-Host "✓ Health check complete" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ Rollback Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($Version) {
        Write-Host "Rolled back to version: $Version"
    } else {
        Write-Host "Rolled back to previous production version"
    }
    Write-Host "Reason: $Reason"
    Write-Host ""
    
    # Post-rollback steps
    Write-Host "Post-rollback checklist:" -ForegroundColor Yellow
    Write-Host "  [ ] Monitor metrics for stability"
    Write-Host "  [ ] Check error logs"
    Write-Host "  [ ] Investigate root cause"
    Write-Host "  [ ] Update incident report"
    Write-Host "  [ ] Notify team"
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "✗ Rollback failed with error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    # Return to original directory
    Pop-Location
}
