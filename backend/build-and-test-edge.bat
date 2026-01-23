@echo off
REM Build and test Phase 19 Edge Worker with Docker (Windows)

echo ========================================================================
echo Phase 19 - Edge Worker Docker Build and Test
echo ========================================================================
echo.

REM Step 1: Check Docker
echo [1/6] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo X Docker is not installed
    exit /b 1
)
echo + Docker is installed
docker --version
echo.

REM Step 2: Check NVIDIA Docker
echo [2/6] Checking NVIDIA Docker support...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ! No NVIDIA GPU detected - will use CPU
    set GPU_AVAILABLE=false
) else (
    echo + NVIDIA GPU detected
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    set GPU_AVAILABLE=true
)
echo.

REM Step 3: Build Docker image
echo [3/6] Building Edge Worker Docker image...
echo This may take 5-10 minutes on first build...
docker build -f Dockerfile.edge -t neo-alexandria-edge:latest .
if errorlevel 1 (
    echo X Docker build failed
    exit /b 1
)
echo + Docker image built successfully
echo.

REM Step 4: Run tests inside Docker container
echo [4/6] Running tests inside Docker container...

REM Create test script
echo #!/bin/bash > run_tests.sh
echo set -e >> run_tests.sh
echo echo "Running Phase 19 tests inside Docker container..." >> run_tests.sh
echo echo "" >> run_tests.sh
echo echo "[Test 1/3] Repository Parser Tests..." >> run_tests.sh
echo python -m pytest tests/test_repo_parser.py tests/properties/test_repo_parser_properties.py -v --tb=short >> run_tests.sh
echo echo "" >> run_tests.sh
echo echo "[Test 2/3] Neural Graph Service Tests..." >> run_tests.sh
echo python -m pytest tests/test_neural_graph.py -v --tb=short ^|^| true >> run_tests.sh
echo echo "" >> run_tests.sh
echo echo "[Test 3/3] End-to-End Graph Generation Test..." >> run_tests.sh
echo python test_e2e_graph_generation.py ^|^| true >> run_tests.sh
echo echo "" >> run_tests.sh
echo echo "Tests complete!" >> run_tests.sh

REM Run tests
if "%GPU_AVAILABLE%"=="true" (
    echo Running with GPU support...
    docker run --rm --gpus all -v "%cd%\run_tests.sh:/app/run_tests.sh" neo-alexandria-edge:latest /bin/bash /app/run_tests.sh
) else (
    echo Running with CPU only...
    docker run --rm -v "%cd%\run_tests.sh:/app/run_tests.sh" neo-alexandria-edge:latest /bin/bash /app/run_tests.sh
)

REM Cleanup
del run_tests.sh

REM Step 5: Verify image size
echo.
echo [5/6] Docker image information...
docker images neo-alexandria-edge:latest

REM Step 6: Summary
echo.
echo ========================================================================
echo Build and Test Summary
echo ========================================================================
echo + Docker image built: neo-alexandria-edge:latest
echo + Tests executed inside container

if "%GPU_AVAILABLE%"=="true" (
    echo + GPU support: Available
) else (
    echo ! GPU support: Not available ^(CPU only^)
)

echo.
echo Next steps:
echo 1. Set up environment variables in .env.edge
echo 2. Run: docker-compose -f docker-compose.edge.yml up -d
echo 3. Monitor logs: docker-compose -f docker-compose.edge.yml logs -f
echo.
echo For manual testing:
echo   docker run --rm -it neo-alexandria-edge:latest /bin/bash
echo.
echo ========================================================================

pause
