#!/bin/bash
# Neo Alexandria 2.0 - Quick Start Script

set -e

echo "🚀 Neo Alexandria 2.0 - Starting Deployment"
echo "============================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.production .env
    echo "⚠️  IMPORTANT: Edit .env and set your JWT_SECRET_KEY and POSTGRES_PASSWORD"
    echo "   Run: nano .env"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "✅ Deployment Complete!"
echo "============================================"
echo ""
echo "📍 API Documentation (Swagger): http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:        docker-compose logs -f backend"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart backend"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "Happy coding! 🎉"
