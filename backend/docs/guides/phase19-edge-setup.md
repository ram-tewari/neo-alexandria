# Phase 19 Edge Worker Setup Guide

## Overview

This guide covers setting up the Neo Alexandria Edge Worker on your local machine. The Edge Worker is a GPU-accelerated Python worker that processes repository ingestion tasks, trains graph neural networks, and uploads embeddings to Qdrant Cloud.

## Prerequisites

### Hardware Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8GB
- GPU: NVIDIA GPU with 4GB VRAM (optional, will fall back to CPU)
- Storage: 20GB free space

**Recommended**:
- CPU: Intel i9 or AMD Ryzen 9 (8+ cores)
- RAM: 16GB or more
- GPU: NVIDIA RTX 4070 or better (16GB VRAM)
- Storage: 50GB free space for repositories and models

### Software Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **Python**: 3.10 or 3.11
- **CUDA**: 11.8 or 12.1 (for GPU acceleration)
- **Git**: For repository cloning
- **Internet**: Stable connection for Redis/Qdrant

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/neo-alexandria-2.0.git
cd neo-alexandria-2.0/backend
```

### Step 2: Install CUDA (GPU Only)

#### Windows

1. Download CUDA Toolkit from [NVIDIA](https://developer.nvidia.com/cuda-downloads)
2. Install CUDA 11.8 or 12.1
3. Verify installation:
```powershell
nvcc --version
nvidia-smi
```

#### Linux

```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2004-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-12-1-local_12.1.0-530.30.02-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# Verify
nvcc --version
nvidia-smi
```

#### macOS

CUDA is not available on macOS. The worker will automatically fall back to CPU mode.

### Step 3: Create Python Environment

#### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate
```

#### Using conda

```bash
# Create environment
conda create -n neo-edge python=3.10

# Activate
conda activate neo-edge
```

### Step 4: Install Dependencies

```bash
# Install edge worker dependencies
pip install -r requirements-edge.txt

# Verify PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

# Verify PyTorch Geometric
python -c "import torch_geometric; print(f'PyG: {torch_geometric.__version__}')"
```

**Expected Output (GPU)**:
```
PyTorch: 2.1.0+cu118
CUDA Available: True
PyG: 2.4.0
```

**Expected Output (CPU)**:
```
PyTorch: 2.1.0
CUDA Available: False
PyG: 2.4.0
```

### Step 5: Configure Environment

Create `.env.edge` from template:

```bash
cp .env.edge.template .env.edge
```

Edit `.env.edge` with your credentials:

```bash
# Deployment Mode
MODE=EDGE

# Upstash Redis (same as Cloud API)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-rest-token

# Qdrant Cloud (same as Cloud API)
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your-api-key

# Optional: Neon Database (if worker needs metadata access)
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb
```

**Security Note**: Never commit `.env.edge` to Git. It's already in `.gitignore`.

## Running the Worker

### Manual Start

```bash
# Activate environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Start worker
python worker.py
```

**Expected Output**:
```
🔥 Edge Worker Online
   Hardware: NVIDIA GeForce RTX 4070
   Device: cuda
   VRAM: 16GB
   
⏳ Polling queue every 2 seconds...
```

### Test Mode

Test the worker without processing real jobs:

```bash
python worker.py --test
```

This will:
1. Verify CUDA availability
2. Test Redis connection
3. Test Qdrant connection
4. Exit without polling queue

### Background Mode

#### Linux (systemd)

Create service file:

```bash
sudo nano /etc/systemd/system/neo-alexandria-worker.service
```

Add configuration:

```ini
[Unit]
Description=Neo Alexandria Edge Worker
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/neo-alexandria-2.0/backend
Environment="MODE=EDGE"
EnvironmentFile=/path/to/.env.edge
ExecStart=/path/to/.venv/bin/python worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable neo-alexandria-worker
sudo systemctl start neo-alexandria-worker

# Check status
sudo systemctl status neo-alexandria-worker

# View logs
sudo journalctl -u neo-alexandria-worker -f
```

#### Windows (NSSM)

Install NSSM (Non-Sucking Service Manager):

```powershell
# Using Chocolatey
choco install nssm

# Or download from https://nssm.cc/download
```

Create service:

```powershell
# Set paths
$pythonPath = "C:\path\to\.venv\Scripts\python.exe"
$workerPath = "C:\path\to\neo-alexandria-2.0\backend\worker.py"
$workingDir = "C:\path\to\neo-alexandria-2.0\backend"

# Install service
nssm install NeoAlexandriaWorker $pythonPath $workerPath
nssm set NeoAlexandriaWorker AppDirectory $workingDir
nssm set NeoAlexandriaWorker AppEnvironmentExtra MODE=EDGE
nssm set NeoAlexandriaWorker DisplayName "Neo Alexandria Edge Worker"
nssm set NeoAlexandriaWorker Description "GPU-accelerated worker for Neo Alexandria"
nssm set NeoAlexandriaWorker Start SERVICE_AUTO_START

# Start service
nssm start NeoAlexandriaWorker

# Check status
nssm status NeoAlexandriaWorker

# View logs
nssm set NeoAlexandriaWorker AppStdout C:\path\to\logs\worker-stdout.log
nssm set NeoAlexandriaWorker AppStderr C:\path\to\logs\worker-stderr.log
```

#### macOS (launchd)

Create plist file:

```bash
nano ~/Library/LaunchAgents/com.neoalexandria.worker.plist
```

Add configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.neoalexandria.worker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/.venv/bin/python</string>
        <string>/path/to/worker.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/neo-alexandria-2.0/backend</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>MODE</key>
        <string>EDGE</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/neo-worker-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/neo-worker-stderr.log</string>
</dict>
</plist>
```

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.neoalexandria.worker.plist
launchctl start com.neoalexandria.worker

# Check status
launchctl list | grep neoalexandria

# View logs
tail -f /tmp/neo-worker-stdout.log
```

## Monitoring

### Worker Status

Check worker status via Cloud API:

```bash
curl https://your-app.onrender.com/api/v1/ingestion/worker/status
```

Possible statuses:
- `"Idle"` - Waiting for tasks
- `"Training Graph on github.com/user/repo"` - Processing repository
- `"Error: {message}"` - Error occurred
- `"Offline"` - Worker not running

### GPU Monitoring

Monitor GPU utilization in real-time:

```bash
# Watch GPU usage
watch -n 1 nvidia-smi

# Or use nvidia-smi directly
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total --format=csv -l 1
```

**Expected During Training**:
- GPU Utilization: 70-90%
- Memory Usage: 4-8GB (depends on repository size)
- Temperature: 60-80°C

### System Monitoring

#### Linux

```bash
# CPU and memory
htop

# Disk usage
df -h

# Process monitoring
ps aux | grep worker.py
```

#### Windows

```powershell
# Task Manager
taskmgr

# Or PowerShell
Get-Process python | Select-Object CPU,WorkingSet,ProcessName
```

#### macOS

```bash
# Activity Monitor
open -a "Activity Monitor"

# Or terminal
top -pid $(pgrep -f worker.py)
```

### Log Monitoring

#### Manual Mode

Logs are printed to stdout/stderr. Redirect to file:

```bash
python worker.py > worker.log 2>&1
```

#### Systemd (Linux)

```bash
# Follow logs
sudo journalctl -u neo-alexandria-worker -f

# View recent logs
sudo journalctl -u neo-alexandria-worker -n 100

# Filter by time
sudo journalctl -u neo-alexandria-worker --since "1 hour ago"
```

#### NSSM (Windows)

Logs are written to configured files:

```powershell
# View stdout
Get-Content C:\path\to\logs\worker-stdout.log -Tail 50 -Wait

# View stderr
Get-Content C:\path\to\logs\worker-stderr.log -Tail 50 -Wait
```

## Troubleshooting

### CUDA Issues

**Problem**: `CUDA Available: False` despite having NVIDIA GPU

**Solution**:
1. Verify CUDA installation: `nvcc --version`
2. Verify GPU driver: `nvidia-smi`
3. Reinstall PyTorch with CUDA:
```bash
pip uninstall torch torch-geometric
pip install torch==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric
```

**Problem**: `RuntimeError: CUDA out of memory`

**Solution**:
1. Close other GPU applications
2. Reduce batch size in `neural_graph.py` (default: 128)
3. Process smaller repositories first
4. Upgrade GPU or use CPU mode

**Problem**: GPU temperature too high (>85°C)

**Solution**:
1. Improve laptop cooling (use cooling pad)
2. Clean dust from vents
3. Reduce GPU clock speed
4. Process fewer repositories concurrently

### Connection Issues

**Problem**: `ConnectionError: Cannot connect to Redis`

**Solution**:
1. Verify `.env.edge` has correct credentials
2. Test connection:
```bash
curl https://xxx.upstash.io/get/test \
  -H "Authorization: Bearer YOUR_REST_TOKEN"
```
3. Check firewall settings
4. Verify internet connection

**Problem**: `ConnectionError: Cannot connect to Qdrant`

**Solution**:
1. Verify Qdrant cluster is running
2. Test connection:
```bash
curl https://xxx.qdrant.io/collections \
  -H "api-key: YOUR_API_KEY"
```
3. Check API key is correct
4. Verify internet connection

### Repository Cloning Issues

**Problem**: `GitCommandError: Failed to clone repository`

**Solution**:
1. Verify repository URL is correct
2. Check if repository is public (private repos need authentication)
3. Verify Git is installed: `git --version`
4. Check disk space: `df -h` (Linux/macOS) or `Get-PSDrive` (Windows)
5. Check network connectivity

**Problem**: `PermissionError: Cannot write to temp directory`

**Solution**:
1. Check disk permissions
2. Verify temp directory exists and is writable
3. Run worker with appropriate permissions
4. Check disk space

### Performance Issues

**Problem**: Processing is very slow (>10 minutes per repository)

**Solution**:
1. Verify GPU is being used: `nvidia-smi`
2. Check GPU utilization (should be >70%)
3. Reduce repository size (skip large files)
4. Upgrade hardware
5. Check for CPU throttling (thermal issues)

**Problem**: Worker crashes frequently

**Solution**:
1. Check logs for error messages
2. Verify sufficient RAM (16GB recommended)
3. Check for memory leaks
4. Update dependencies: `pip install -r requirements-edge.txt --upgrade`
5. Restart worker service

### Service Issues

**Problem**: Systemd service won't start

**Solution**:
1. Check service status: `sudo systemctl status neo-alexandria-worker`
2. View logs: `sudo journalctl -u neo-alexandria-worker -n 50`
3. Verify paths in service file
4. Check permissions: `ls -la /path/to/worker.py`
5. Test manual start: `python worker.py`

**Problem**: NSSM service won't start

**Solution**:
1. Check service status: `nssm status NeoAlexandriaWorker`
2. View logs in configured log files
3. Verify Python path: `where python`
4. Test manual start: `python worker.py`
5. Check Windows Event Viewer for errors

## Performance Optimization

### GPU Optimization

**Increase Batch Size** (if you have VRAM):

Edit `app/services/neural_graph.py`:

```python
self.batch_size = 256  # Default: 128
```

**Use Mixed Precision** (for newer GPUs):

```python
# In train_embeddings method
with torch.cuda.amp.autocast():
    loss = model.loss(pos_rw, neg_rw)
```

### CPU Optimization

**Increase Worker Threads**:

Edit `worker.py`:

```python
# For CPU mode, use multiple workers
loader = model.loader(
    batch_size=self.batch_size,
    shuffle=True,
    num_workers=4  # Default: 0
)
```

### Disk Optimization

**Use SSD for Temp Directory**:

Edit `app/utils/repo_parser.py`:

```python
# Use specific temp directory on SSD
temp_dir = tempfile.mkdtemp(prefix="neo_repo_", dir="/path/to/ssd")
```

## Scaling

### Multiple Workers

Run multiple workers on different machines:

1. Set up each machine with edge worker
2. Configure same Redis/Qdrant credentials
3. Start workers on each machine
4. Workers will automatically share the queue

**Load Balancing**:
- Workers poll queue independently
- First worker to LPOP gets the task
- No coordination needed

### Dedicated GPU Server

For production, consider:

1. **Cloud GPU** (AWS, GCP, Azure):
   - More expensive but scalable
   - No local hardware maintenance
   - Pay per use

2. **Dedicated Server**:
   - One-time hardware cost
   - Full control
   - Better for high volume

3. **Hybrid Approach**:
   - Local worker for development
   - Cloud worker for production
   - Both share same queue

## Maintenance

### Updates

Update worker code:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements-edge.txt --upgrade

# Restart worker
sudo systemctl restart neo-alexandria-worker  # Linux
nssm restart NeoAlexandriaWorker              # Windows
```

### Cleanup

Clean up old repositories:

```bash
# Find temp directories
find /tmp -name "neo_repo_*" -type d

# Remove old temp directories (older than 1 day)
find /tmp -name "neo_repo_*" -type d -mtime +1 -exec rm -rf {} \;
```

### Backup

Backup worker configuration:

```bash
# Backup .env.edge
cp .env.edge .env.edge.backup

# Backup service file (Linux)
sudo cp /etc/systemd/system/neo-alexandria-worker.service ~/neo-worker-service.backup
```

## Next Steps

- [Cloud Deployment Guide](phase19-deployment.md) - Deploy Cloud API
- [Monitoring Guide](phase19-monitoring.md) - Monitor system health
- [Troubleshooting Guide](troubleshooting.md) - Common issues

## Support

- **Documentation**: [Neo Alexandria Docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/neo-alexandria-2.0/issues)
- **CUDA Support**: [NVIDIA Documentation](https://docs.nvidia.com/cuda/)
- **PyTorch Support**: [PyTorch Forums](https://discuss.pytorch.org/)
