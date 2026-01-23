# Neo Alexandria Edge Worker Setup Script for Windows
# This script sets up the edge worker environment and optionally installs it as a Windows service using NSSM

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Neo Alexandria Edge Worker Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
    
    # Verify minimum version
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "ERROR: Python 3.8 or higher is required" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check for CUDA
Write-Host "Checking CUDA availability..." -ForegroundColor Yellow
try {
    $nvidiaInfo = nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ NVIDIA GPU detected:" -ForegroundColor Green
        Write-Host $nvidiaInfo
        $cudaAvailable = $true
    } else {
        throw "nvidia-smi not found"
    }
} catch {
    Write-Host "⚠ No NVIDIA GPU detected. Worker will run on CPU (slower)." -ForegroundColor Yellow
    $cudaAvailable = $false
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing edge worker dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements-edge.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Verify PyTorch installation
Write-Host "Verifying PyTorch installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
Write-Host ""

# Check for .env.edge file
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env.edge")) {
    Write-Host "⚠ .env.edge file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.edge.template") {
        Copy-Item ".env.edge.template" ".env.edge"
        Write-Host "✓ Created .env.edge from template" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Edit .env.edge and add your credentials:" -ForegroundColor Yellow
        Write-Host "  - UPSTASH_REDIS_URL"
        Write-Host "  - UPSTASH_REDIS_TOKEN"
        Write-Host "  - QDRANT_URL"
        Write-Host "  - QDRANT_API_KEY"
        Write-Host ""
    } else {
        Write-Host "ERROR: .env.edge.template not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ .env.edge file found" -ForegroundColor Green
    Write-Host ""
}

# Test worker startup
Write-Host "Testing worker startup..." -ForegroundColor Yellow
try {
    python -c "from worker import main; print('✓ Worker imports successfully')"
    Write-Host "✓ Worker is ready to run" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Worker failed to import. Check dependencies." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Ask about service installation
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Service Installation (Optional)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Would you like to install the edge worker as a Windows service?"
Write-Host "This requires NSSM (Non-Sucking Service Manager) and will make the worker start automatically."
Write-Host ""
$installService = Read-Host "Install as service? (y/n)"

if ($installService -eq "y" -or $installService -eq "Y") {
    # Check if NSSM is installed
    Write-Host "Checking for NSSM..." -ForegroundColor Yellow
    try {
        $nssmPath = (Get-Command nssm -ErrorAction Stop).Source
        Write-Host "✓ NSSM found at: $nssmPath" -ForegroundColor Green
    } catch {
        Write-Host "⚠ NSSM not found. Installing NSSM..." -ForegroundColor Yellow
        
        # Check if Chocolatey is available
        try {
            choco --version | Out-Null
            Write-Host "Installing NSSM via Chocolatey..." -ForegroundColor Yellow
            choco install nssm -y
            $nssmPath = (Get-Command nssm).Source
        } catch {
            Write-Host ""
            Write-Host "ERROR: NSSM is required but not installed." -ForegroundColor Red
            Write-Host "Please install NSSM manually:" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://nssm.cc/download" -ForegroundColor Yellow
            Write-Host "  2. Extract and add to PATH" -ForegroundColor Yellow
            Write-Host "  3. Or install via Chocolatey: choco install nssm" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Then run this script again." -ForegroundColor Yellow
            exit 1
        }
    }
    Write-Host ""
    
    # Get absolute paths
    $workerDir = Get-Location
    $pythonPath = Join-Path $workerDir ".venv\Scripts\python.exe"
    $workerScript = Join-Path $workerDir "worker.py"
    $serviceName = "NeoAlexandriaWorker"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "⚠ Service '$serviceName' already exists. Removing..." -ForegroundColor Yellow
        nssm stop $serviceName
        nssm remove $serviceName confirm
    }
    
    # Install service
    Write-Host "Installing Windows service..." -ForegroundColor Yellow
    nssm install $serviceName $pythonPath $workerScript
    nssm set $serviceName AppDirectory $workerDir
    nssm set $serviceName DisplayName "Neo Alexandria Edge Worker"
    nssm set $serviceName Description "GPU-accelerated edge worker for Neo Alexandria knowledge management system"
    nssm set $serviceName Start SERVICE_AUTO_START
    nssm set $serviceName AppStdout "$workerDir\worker.log"
    nssm set $serviceName AppStderr "$workerDir\worker.error.log"
    nssm set $serviceName AppRotateFiles 1
    nssm set $serviceName AppRotateBytes 10485760  # 10MB
    
    Write-Host "✓ Windows service installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service commands:" -ForegroundColor Cyan
    Write-Host "  Start:   nssm start $serviceName" -ForegroundColor White
    Write-Host "  Stop:    nssm stop $serviceName" -ForegroundColor White
    Write-Host "  Restart: nssm restart $serviceName" -ForegroundColor White
    Write-Host "  Status:  nssm status $serviceName" -ForegroundColor White
    Write-Host "  Remove:  nssm remove $serviceName confirm" -ForegroundColor White
    Write-Host "  Logs:    Get-Content worker.log -Tail 50 -Wait" -ForegroundColor White
    Write-Host ""
    
    # Ask to start service now
    $startNow = Read-Host "Start the service now? (y/n)"
    if ($startNow -eq "y" -or $startNow -eq "Y") {
        nssm start $serviceName
        Write-Host "✓ Service started" -ForegroundColor Green
        Start-Sleep -Seconds 2
        nssm status $serviceName
    }
} else {
    Write-Host "Skipping service installation." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env.edge with your credentials (if not done already)"
Write-Host "2. Run the worker:"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python worker.py"
Write-Host ""
Write-Host "Or if installed as service, start it with: nssm start NeoAlexandriaWorker"
Write-Host ""
