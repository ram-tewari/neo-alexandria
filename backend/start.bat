@echo off
REM Neo Alexandria 2.0 - Quick Start Script for Windows

echo 🚀 Neo Alexandria 2.0 - Starting Deployment
echo ============================================

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env from template...
    copy .env.production .env
    echo ⚠️  IMPORTANT: Edit .env and set your JWT_SECRET_KEY and POSTGRES_PASSWORD
    echo    Run: notepad .env
    exit /b 1
)

REM Build and start services
echo 🔨 Building Docker images...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak > nul

REM Run migrations
echo 📊 Running database migrations...
docker-compose exec -T backend alembic upgrade head

echo.
echo ✅ Deployment Complete!
echo ============================================
echo.
echo 📍 API Documentation (Swagger): http://localhost:8000/docs
echo 📍 Health Check: http://localhost:8000/health
echo.
echo 📋 Useful Commands:
echo    View logs:        docker-compose logs -f backend
echo    Stop services:    docker-compose down
echo    Restart:          docker-compose restart backend
echo.
echo 🧪 Test the API:
echo    curl http://localhost:8000/health
echo.
echo Happy coding! 🎉
