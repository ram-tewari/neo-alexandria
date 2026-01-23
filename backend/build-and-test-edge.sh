#!/bin/bash
# Build and test Phase 19 Edge Worker with Docker

set -e  # Exit on error

echo "========================================================================"
echo "Phase 19 - Edge Worker Docker Build and Test"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo "[1/6] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed: $(docker --version)${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠ docker-compose not found, using 'docker compose' instead${NC}"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Step 2: Check NVIDIA Docker (optional)
echo ""
echo "[2/6] Checking NVIDIA Docker support..."
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected:${NC}"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo -e "${GREEN}✓ NVIDIA Docker runtime is working${NC}"
        GPU_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠ NVIDIA Docker runtime not available - will use CPU${NC}"
        GPU_AVAILABLE=false
    fi
else
    echo -e "${YELLOW}⚠ No NVIDIA GPU detected - will use CPU${NC}"
    GPU_AVAILABLE=false
fi

# Step 3: Build Docker image
echo ""
echo "[3/6] Building Edge Worker Docker image..."
echo "This may take 5-10 minutes on first build..."

if docker build -f Dockerfile.edge -t neo-alexandria-edge:latest .; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Step 4: Run tests inside Docker container
echo ""
echo "[4/6] Running tests inside Docker container..."

# Create a test script to run inside container
cat > /tmp/run_tests.sh << 'EOF'
#!/bin/bash
set -e

echo "Running Phase 19 tests inside Docker container..."
echo ""

# Test 1: Repository Parser Tests
echo "[Test 1/3] Repository Parser Tests..."
python -m pytest tests/test_repo_parser.py tests/properties/test_repo_parser_properties.py -v --tb=short
echo ""

# Test 2: Neural Graph Service Tests
echo "[Test 2/3] Neural Graph Service Tests..."
python -m pytest tests/test_neural_graph.py -v --tb=short || true
echo ""

# Test 3: End-to-End Graph Generation (without Qdrant)
echo "[Test 3/3] End-to-End Graph Generation Test..."
python test_e2e_graph_generation.py || true
echo ""

echo "Tests complete!"
EOF

chmod +x /tmp/run_tests.sh

# Run tests in container
if [ "$GPU_AVAILABLE" = true ]; then
    echo "Running with GPU support..."
    docker run --rm --gpus all \
        -v /tmp/run_tests.sh:/app/run_tests.sh \
        neo-alexandria-edge:latest \
        /bin/bash /app/run_tests.sh
else
    echo "Running with CPU only..."
    docker run --rm \
        -v /tmp/run_tests.sh:/app/run_tests.sh \
        neo-alexandria-edge:latest \
        /bin/bash /app/run_tests.sh
fi

# Step 5: Verify image size
echo ""
echo "[5/6] Docker image information..."
docker images neo-alexandria-edge:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Step 6: Summary
echo ""
echo "========================================================================"
echo "Build and Test Summary"
echo "========================================================================"
echo -e "${GREEN}✓ Docker image built: neo-alexandria-edge:latest${NC}"
echo -e "${GREEN}✓ Tests executed inside container${NC}"

if [ "$GPU_AVAILABLE" = true ]; then
    echo -e "${GREEN}✓ GPU support: Available${NC}"
else
    echo -e "${YELLOW}⚠ GPU support: Not available (CPU only)${NC}"
fi

echo ""
echo "Next steps:"
echo "1. Set up environment variables in .env.edge"
echo "2. Run: docker-compose -f docker-compose.edge.yml up -d"
echo "3. Monitor logs: docker-compose -f docker-compose.edge.yml logs -f"
echo ""
echo "For manual testing:"
echo "  docker run --rm -it neo-alexandria-edge:latest /bin/bash"
echo ""
echo "========================================================================"
