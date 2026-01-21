# Phase 19 - Docker Quick Start Guide

## Prerequisites

- ✅ Docker installed (you have this)
- ✅ Docker Compose installed
- ⚠️ NVIDIA GPU + NVIDIA Docker runtime (optional, for GPU acceleration)

## Quick Start (5 minutes)

### Step 1: Build and Test

**Windows:**
```bash
cd backend
build-and-test-edge.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x build-and-test-edge.sh
./build-and-test-edge.sh
```

This will:
1. Check Docker installation
2. Check GPU availability
3. Build the Edge Worker Docker image (~5-10 minutes first time)
4. Run all tests inside the container
5. Show you the results

### Step 2: Set Up Environment Variables

Copy the template and fill in your credentials:

```bash
cp .env.edge.template .env.edge
```

Edit `.env.edge` with your actual credentials:
```bash
# Redis (Upstash)
UPSTASH_REDIS_URL=redis://default:your-password@your-redis.upstash.io:6379
UPSTASH_REDIS_TOKEN=your-token

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Database (Neon)
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Step 3: Run the Edge Worker

```bash
docker-compose -f docker-compose.edge.yml up -d
```

### Step 4: Monitor Logs

```bash
docker-compose -f docker-compose.edge.yml logs -f
```

Press `Ctrl+C` to stop following logs.

### Step 5: Stop the Worker

```bash
docker-compose -f docker-compose.edge.yml down
```

## What the Build Script Does

The `build-and-test-edge` script will:

1. ✅ **Check Docker** - Verify Docker is installed and running
2. ✅ **Check GPU** - Detect NVIDIA GPU and Docker GPU support
3. ✅ **Build Image** - Build Docker image with all dependencies
4. ✅ **Run Tests** - Execute all Phase 19 tests inside container:
   - Repository Parser tests (18 tests)
   - Neural Graph Service tests (7 tests)
   - End-to-end graph generation test
5. ✅ **Show Results** - Display test results and next steps

## Expected Test Results

### With GPU (CUDA available):
```
Repository Parser Tests: 18/18 PASS ✅
Neural Graph Service Tests: 7/7 PASS ✅
E2E Graph Generation: PASS ✅
```

### Without GPU (CPU only):
```
Repository Parser Tests: 18/18 PASS ✅
Neural Graph Service Tests: 1/7 PASS ⚠️ (6 require torch-cluster)
E2E Graph Generation: PARTIAL ⚠️ (training will be slow)
```

## Troubleshooting

### Issue: Docker build fails

**Solution**: Check Docker is running and you have internet connection.

```bash
docker ps
```

### Issue: GPU not detected

**Solution**: Install NVIDIA Docker runtime:

**Windows with WSL2:**
```bash
# In WSL2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**Linux:**
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

Test GPU access:
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Issue: Tests fail inside container

**Solution**: Run container interactively to debug:

```bash
docker run --rm -it neo-alexandria-edge:latest /bin/bash
```

Then inside container:
```bash
python -m pytest tests/test_repo_parser.py -v
python test_e2e_graph_generation.py
```

### Issue: Out of disk space

**Solution**: Clean up Docker:

```bash
docker system prune -a
```

## Manual Testing

### Run tests manually:

```bash
# With GPU
docker run --rm --gpus all neo-alexandria-edge:latest python -m pytest tests/test_repo_parser.py -v

# Without GPU
docker run --rm neo-alexandria-edge:latest python -m pytest tests/test_repo_parser.py -v
```

### Interactive shell:

```bash
# With GPU
docker run --rm -it --gpus all neo-alexandria-edge:latest /bin/bash

# Without GPU
docker run --rm -it neo-alexandria-edge:latest /bin/bash
```

### Run E2E test:

```bash
docker run --rm --gpus all \
  -e QDRANT_URL=your-url \
  -e QDRANT_API_KEY=your-key \
  neo-alexandria-edge:latest \
  python test_e2e_graph_generation.py
```

## Production Deployment

Once tests pass, deploy to production:

1. **Push image to registry** (optional):
```bash
docker tag neo-alexandria-edge:latest your-registry/neo-alexandria-edge:latest
docker push your-registry/neo-alexandria-edge:latest
```

2. **Deploy with docker-compose**:
```bash
docker-compose -f docker-compose.edge.yml up -d
```

3. **Monitor**:
```bash
docker-compose -f docker-compose.edge.yml logs -f edge-worker
```

4. **Check health**:
```bash
docker-compose -f docker-compose.edge.yml ps
```

## Performance Tips

### GPU Memory

If you encounter GPU memory issues, reduce batch sizes in `app/services/neural_graph.py`:

```python
self.batch_size = 64  # Reduce from 128
```

### CPU Performance

For CPU-only deployments, consider:
- Using smaller graphs
- Reducing number of epochs
- Increasing poll interval

## Next Steps

After successful Docker build and test:

1. ✅ Verify all tests pass
2. ✅ Set up environment variables
3. ✅ Deploy Edge Worker
4. ✅ Deploy Cloud API (separate task)
5. ✅ Test end-to-end workflow
6. ✅ Monitor and optimize

## Support

For issues:
- Check logs: `docker-compose -f docker-compose.edge.yml logs`
- Review documentation: `backend/docs/PHASE19_EDGE_ENVIRONMENT_SETUP.md`
- Check verification report: `backend/PHASE19_GRAPH_SERVICE_VERIFICATION.md`

---

**Ready to build?** Run `build-and-test-edge.bat` (Windows) or `./build-and-test-edge.sh` (Linux/Mac)
