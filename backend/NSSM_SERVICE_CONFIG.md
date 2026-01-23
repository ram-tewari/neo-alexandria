# NSSM Windows Service Configuration

This document describes the Windows service configuration for the Neo Alexandria Edge Worker using NSSM (Non-Sucking Service Manager).

## Prerequisites

- NSSM installed (download from https://nssm.cc/download or install via Chocolatey: `choco install nssm`)
- Python 3.8+ installed
- Edge worker dependencies installed (`pip install -r requirements-edge.txt`)
- `.env.edge` file configured with credentials

## Automatic Installation

The easiest way to install the service is to run the setup script:

```powershell
.\setup_edge.ps1
```

The script will:
1. Check Python and CUDA availability
2. Create virtual environment
3. Install dependencies
4. Optionally install as Windows service using NSSM

## Manual Installation

If you prefer to install the service manually:

### 1. Install NSSM

**Via Chocolatey:**
```powershell
choco install nssm -y
```

**Manual Download:**
1. Download from https://nssm.cc/download
2. Extract to a folder (e.g., `C:\nssm`)
3. Add to PATH or use full path to nssm.exe

### 2. Install Service

```powershell
# Navigate to backend directory
cd C:\path\to\neo-alexandria-2.0\backend

# Install service
nssm install NeoAlexandriaWorker "C:\path\to\neo-alexandria-2.0\backend\.venv\Scripts\python.exe" "worker.py"

# Configure service
nssm set NeoAlexandriaWorker AppDirectory "C:\path\to\neo-alexandria-2.0\backend"
nssm set NeoAlexandriaWorker DisplayName "Neo Alexandria Edge Worker"
nssm set NeoAlexandriaWorker Description "GPU-accelerated edge worker for Neo Alexandria knowledge management system"
nssm set NeoAlexandriaWorker Start SERVICE_AUTO_START
nssm set NeoAlexandriaWorker AppStdout "C:\path\to\neo-alexandria-2.0\backend\worker.log"
nssm set NeoAlexandriaWorker AppStderr "C:\path\to\neo-alexandria-2.0\backend\worker.error.log"
nssm set NeoAlexandriaWorker AppRotateFiles 1
nssm set NeoAlexandriaWorker AppRotateBytes 10485760
```

### 3. Start Service

```powershell
nssm start NeoAlexandriaWorker
```

## Service Management Commands

### Start Service
```powershell
nssm start NeoAlexandriaWorker
```

### Stop Service
```powershell
nssm stop NeoAlexandriaWorker
```

### Restart Service
```powershell
nssm restart NeoAlexandriaWorker
```

### Check Status
```powershell
nssm status NeoAlexandriaWorker
```

### View Logs
```powershell
# View last 50 lines and follow
Get-Content worker.log -Tail 50 -Wait

# View error log
Get-Content worker.error.log -Tail 50 -Wait
```

### Edit Service Configuration
```powershell
nssm edit NeoAlexandriaWorker
```

This opens a GUI where you can modify service settings.

### Remove Service
```powershell
nssm stop NeoAlexandriaWorker
nssm remove NeoAlexandriaWorker confirm
```

## Service Configuration Details

| Setting | Value | Description |
|---------|-------|-------------|
| Service Name | NeoAlexandriaWorker | Internal service name |
| Display Name | Neo Alexandria Edge Worker | Name shown in Services |
| Executable | `.venv\Scripts\python.exe` | Python interpreter |
| Arguments | `worker.py` | Worker script |
| Working Directory | Backend directory | Where worker.py is located |
| Startup Type | Automatic | Starts on boot |
| Log Rotation | Enabled | Rotates at 10MB |
| Restart Policy | Always | Restarts on failure |

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```powershell
   Get-Content worker.error.log -Tail 50
   ```

2. Verify Python path:
   ```powershell
   nssm get NeoAlexandriaWorker Application
   ```

3. Test worker manually:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python worker.py
   ```

### Service Starts But Doesn't Work

1. Check environment variables:
   ```powershell
   nssm get NeoAlexandriaWorker AppEnvironmentExtra
   ```

2. Verify `.env.edge` file exists and has correct credentials

3. Check Redis connectivity:
   ```powershell
   python -c "from upstash_redis import Redis; import os; from dotenv import load_dotenv; load_dotenv('.env.edge'); r = Redis(url=os.getenv('UPSTASH_REDIS_URL'), token=os.getenv('UPSTASH_REDIS_TOKEN')); print(r.ping())"
   ```

### High Memory Usage

The worker loads PyTorch and GPU models, which requires significant memory:
- Minimum: 4GB RAM
- Recommended: 8GB+ RAM
- GPU: 8GB+ VRAM for optimal performance

### Service Crashes on Startup

1. Check if another instance is running:
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*neo-alexandria*"}
   ```

2. Verify CUDA drivers (if using GPU):
   ```powershell
   nvidia-smi
   ```

3. Check for port conflicts (if worker uses ports)

## Log Rotation

NSSM automatically rotates logs when they reach 10MB. Old logs are renamed with a `.1`, `.2`, etc. suffix.

To change rotation size:
```powershell
nssm set NeoAlexandriaWorker AppRotateBytes 20971520  # 20MB
```

To disable rotation:
```powershell
nssm set NeoAlexandriaWorker AppRotateFiles 0
```

## Running Multiple Workers

To run multiple workers (e.g., for different projects):

```powershell
# Install second worker
nssm install NeoAlexandriaWorker2 "C:\path\to\.venv\Scripts\python.exe" "worker.py"
nssm set NeoAlexandriaWorker2 AppDirectory "C:\path\to\backend"
nssm set NeoAlexandriaWorker2 AppEnvironmentExtra "MODE=EDGE"

# Use different .env file
nssm set NeoAlexandriaWorker2 AppEnvironmentExtra "ENV_FILE=.env.edge2"
```

## Security Considerations

1. **Run as Limited User**: Don't run as Administrator
   ```powershell
   nssm set NeoAlexandriaWorker ObjectName ".\LimitedUser" "password"
   ```

2. **Protect Credentials**: Ensure `.env.edge` has restricted permissions
   ```powershell
   icacls .env.edge /inheritance:r /grant:r "$env:USERNAME:(R)"
   ```

3. **Monitor Logs**: Regularly check logs for errors or suspicious activity

## Performance Tuning

### GPU Optimization

Set environment variables for optimal GPU usage:
```powershell
nssm set NeoAlexandriaWorker AppEnvironmentExtra "CUDA_VISIBLE_DEVICES=0"
nssm set NeoAlexandriaWorker AppEnvironmentExtra "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512"
```

### CPU Affinity

Limit CPU cores used by worker:
```powershell
nssm set NeoAlexandriaWorker AppAffinity 0x0F  # Use first 4 cores
```

### Process Priority

Set process priority (use with caution):
```powershell
nssm set NeoAlexandriaWorker AppPriority ABOVE_NORMAL_PRIORITY_CLASS
```

## Uninstallation

To completely remove the service:

```powershell
# Stop service
nssm stop NeoAlexandriaWorker

# Remove service
nssm remove NeoAlexandriaWorker confirm

# Clean up logs (optional)
Remove-Item worker.log, worker.error.log
```

## Additional Resources

- NSSM Documentation: https://nssm.cc/usage
- Windows Services: https://docs.microsoft.com/en-us/windows/win32/services/services
- Neo Alexandria Documentation: See `backend/docs/`
