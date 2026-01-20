#!/bin/bash
# Docker build script with retry logic

set -e

echo "Building Neo Alexandria Backend Docker Image..."
echo "This may take several minutes due to large dependencies..."

# Build with BuildKit for better caching and parallel builds
DOCKER_BUILDKIT=1 docker-compose build --progress=plain

echo "Build complete!"
echo "To start services: docker-compose up -d"
