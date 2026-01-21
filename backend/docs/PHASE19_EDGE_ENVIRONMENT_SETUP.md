# Phase 19 - Edge Worker Environment Setup Guide

## Overview

This guide provides step-by-step instructions for setting up a proper Linux/Edge environment for the Phase 19 Edge Worker, including installation of torch-cluster and CUDA dependencies.

## Prerequisites

- Linux system (Ubuntu 20.04+ recommended) or WSL2
- NVIDIA GPU with CUDA support (optional but recommended)
- Python 3.8+
- Git

## Environment Options

### Option 1: Docker with Pre-built Wheels (Recommended)

This is the easiest and most reliable method for production deployments.

#### Step 1: Create Dockerfile for Edge Worker

```dockerfile
# Dockerfile.edge
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements-edge.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-edge.txt

# Install torch-cluster with pre-built wheels
RUN pip install torch-cluster -f https://data.pyg.org/whl/torch-2.1.0+cu121.html

# Copy application code
COPY . .

# Set environment variables
ENV MODE=EDGE
ENV PYTHONUNBUFFERED=1

# Run worker
CMD ["python", "worker.py"]
```

#### Step 2: Build Docker Image

```bash
cd backend
docker build -f Dockerfile.edge -t neo-alexandria-edge:latest .
```

#### Step 3: Run Edge Worker Container

```bash
docker run --gpus all \
  --env-file .env.edge \
  -v $(pwd)/logs:/app/logs \
  neo-alexandria-edge:latest
```

### Option 2: Conda Environment

Conda handles torch-cluster dependencies better than pip.

#### Step 1: Create Conda Environment

```bash
conda create -n neo-edge python=3.10
conda activate neo-edge
```

#### Step 2: Install PyTorch with CUDA

```bash
# For CUDA 12.1
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# For CUDA 11.8
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# For CPU only
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

#### Step 3: Install PyTorch Geometric and Dependencies

```bash
conda install pyg -c pyg
```

#### Step 4: Install Other Dependencies

```bash
pip install -r requirements-edge.txt
```

#### Step 5: Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "from torch_geometric.nn import Node2Vec; print('torch-cluster: OK')"
```

### Option 3: Manual Installation (Advanced)

For custom setups or when pre-built wheels aren't available.

#### Step 1: Install PyTorch

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Step 2: Install Build Dependencies

```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev
```

#### Step 3: Install torch-cluster from Source

```bash
# Set PyTorch version
export TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")

# Install torch-cluster
pip install torch-cluster -f https://data.pyg.org/whl/torch-${TORCH_VERSION}.html
```

If pre-built wheels aren't available:

```bash
# Clone and build from source
git clone https://github.com/rusty1s/pytorch_cluster.git
cd pytorch_cluster
pip install .
```

#### Step 4: Install Other Dependencies

```bash
pip install -r requirements-edge.txt
```

## CUDA Verification

### Check CUDA Availability

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA version
nvcc --version

# Check PyTorch CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA version: {torch.version.cuda}')"
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

### Expected Output

```
CUDA available: True
CUDA version: 12.1
GPU: NVIDIA GeForce RTX 4070 Laptop GPU
```

## GPU Detection Test

Create a test script to verify GPU detection:

```python
# test_gpu_detection.py
import torch
from app.services.neural_graph import NeuralGraphService

print("=" * 70)
print("GPU Detection Test")
print("=" * 70)

# Check PyTorch CUDA
print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("CUDA not available - will use CPU")

# Test NeuralGraphService initialization
print("\nInitializing NeuralGraphService...")
device = "cuda" if torch.cuda.is_available() else "cpu"
service = NeuralGraphService(device=device)
print(f"✓ Service initialized with device: {device}")

print("\n" + "=" * 70)
print("GPU Detection Test Complete")
print("=" * 70)
```

Run the test:

```bash
python test_gpu_detection.py
```

## Environment Variables

Create `.env.edge` file:

```bash
# Mode
MODE=EDGE

# Redis (Upstash)
UPSTASH_REDIS_URL=redis://default:your-password@your-redis.upstash.io:6379
UPSTASH_REDIS_TOKEN=your-token

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Database (Neon)
DATABASE_URL=postgresql://user:password@host:5432/database

# Worker Configuration
WORKER_POLL_INTERVAL=2
WORKER_MAX_RETRIES=3
WORKER_RETRY_DELAY=5

# Logging
LOG_LEVEL=INFO
```

## Troubleshooting

### Issue: torch-cluster Installation Fails

**Solution 1**: Use pre-built wheels
```bash
pip install torch-cluster -f https://data.pyg.org/whl/torch-2.1.0+cu121.html
```

**Solution 2**: Use conda
```bash
conda install pyg -c pyg
```

**Solution 3**: Use Docker with pre-built image

### Issue: CUDA Not Detected

**Check 1**: Verify NVIDIA driver
```bash
nvidia-smi
```

**Check 2**: Verify CUDA toolkit
```bash
nvcc --version
```

**Check 3**: Reinstall PyTorch with CUDA
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Issue: Out of Memory Errors

**Solution 1**: Reduce batch size in worker configuration

**Solution 2**: Clear GPU cache
```python
import torch
torch.cuda.empty_cache()
```

**Solution 3**: Use CPU fallback
```bash
export MODE=EDGE
export FORCE_CPU=true
```

### Issue: Import Errors

**Check 1**: Verify all dependencies installed
```bash
pip list | grep torch
```

**Check 2**: Verify Python path
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

**Check 3**: Reinstall dependencies
```bash
pip install --force-reinstall -r requirements-edge.txt
```

## Performance Optimization

### GPU Memory Management

```python
# In worker.py, add memory cleanup after each job
import torch

def process_job(task_data):
    try:
        # ... process job ...
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
```

### Batch Size Tuning

Adjust batch sizes based on available GPU memory:

- 4GB GPU: batch_size=64
- 8GB GPU: batch_size=128 (default)
- 16GB+ GPU: batch_size=256

### Multi-GPU Support (Future)

```python
# For multi-GPU setups
device = f"cuda:{gpu_id}"
service = NeuralGraphService(device=device)
```

## Production Deployment Checklist

- [ ] Docker image built and tested
- [ ] CUDA availability verified
- [ ] GPU detection working
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Worker starts successfully
- [ ] Can process test repository
- [ ] Embeddings uploaded to Qdrant
- [ ] Logs are being written
- [ ] Error handling tested
- [ ] Memory cleanup verified

## Recommended Production Setup

1. **Use Docker** for consistent environment
2. **Use CUDA 12.1** for best compatibility
3. **Use conda** if not using Docker
4. **Monitor GPU usage** with nvidia-smi
5. **Set up log rotation** for worker logs
6. **Configure systemd** for auto-restart
7. **Use health checks** to monitor worker status

## Next Steps

After environment setup:

1. Run unit tests: `pytest tests/test_neural_graph.py -v`
2. Run property tests: `pytest tests/properties/test_neural_graph_properties.py -v`
3. Run integration tests: `pytest tests/test_e2e_workflows.py -v`
4. Test with real repository
5. Monitor performance metrics
6. Deploy to production

## References

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [PyTorch Geometric Installation](https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html)
- [CUDA Toolkit Documentation](https://docs.nvidia.com/cuda/)
- [Docker GPU Support](https://docs.docker.com/config/containers/resource_constraints/#gpu)
