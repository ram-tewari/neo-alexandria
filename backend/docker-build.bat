@echo off
REM Docker build script for Windows

echo Building Neo Alexandria Backend Docker Image...
echo This may take several minutes due to large dependencies...

REM Build with BuildKit for better caching
set DOCKER_BUILDKIT=1
docker-compose build --progress=plain

if %ERRORLEVEL% EQU 0 (
    echo Build complete!
    echo To start services: docker-compose up -d
) else (
    echo Build failed. Check the error messages above.
    echo.
    echo Common fixes:
    echo 1. Check your internet connection
    echo 2. Try again - network timeouts can be temporary
    echo 3. Use: docker-compose build --no-cache
    exit /b 1
)
