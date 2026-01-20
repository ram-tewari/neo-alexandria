# Docker Configuration

This directory contains Docker configuration files for Neo Alexandria.

## Files

- **Dockerfile** - Container image definition for the FastAPI application
- **docker-compose.yml** - Full production stack (app, PostgreSQL, Redis, Celery, monitoring)
- **docker-compose.dev.yml** - Development backing services only (PostgreSQL, Redis)

## Quick Start

### Development Mode (Recommended for Local Development)

Start only PostgreSQL and Redis, run the application locally for debugging:

```bash
# From backend directory
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.dev.yml down -v
```

Then run the application locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://postgres:devpassword@localhost:5432/neo_alexandria_dev

# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --reload
```

### Production Mode (Full Stack)

Start all services including the application, workers, and monitoring:

```bash
cd backend/docker
docker-compose up -d
```

### Services

#### Development Mode (docker-compose.dev.yml)
- **PostgreSQL 15** - Production-grade database (port 5432)
- **Redis 7** - Cache and message broker (port 6379)

#### Production Mode (docker-compose.yml)
- **Neo Alexandria App** - FastAPI application (port 8000)
- **PostgreSQL 15** - Production-grade database (port 5432)
- **Redis 7** - Cache and message broker (port 6379)
- **Celery Workers** - 4 background task workers
- **Celery Beat** - Scheduled task scheduler
- **Flower** - Task monitoring dashboard (port 5555)
- **Prometheus** - Metrics collection (port 9090)
- **Grafana** - Metrics visualization (port 3000)

### View Logs

```bash
docker-compose logs -f celery_worker
docker-compose logs -f redis
```

### Scale Workers

```bash
docker-compose up -d --scale celery_worker=8
```

### Stop Services

```bash
docker-compose down
```

## Monitoring

### Development Mode
- PostgreSQL: `psql -h localhost -U postgres -d neo_alexandria_dev`
- Redis: `redis-cli -h localhost -p 6379`

### Production Mode
- Flower dashboard: http://localhost:5555
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Environment Variables

### Development Mode (.env.dev)

Copy `.env.dev` to `.env` and customize:

```bash
# PostgreSQL
POSTGRES_DB=neo_alexandria_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=devpassword
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
REDIS_HOST=localhost
```

### Production Mode (docker-compose.yml)

Required environment variables (set in docker-compose.yml):
- `DATABASE_URL` - Database connection string
- `CELERY_BROKER_URL` - Redis broker URL
- `CELERY_RESULT_BACKEND` - Redis result backend URL
- `REDIS_HOST` - Redis hostname
- `REDIS_PORT` - Redis port

## Notes

### Development Mode
- PostgreSQL and Redis data persisted in named volumes
- Application runs locally for hot-reload and debugging
- Use `docker-compose.dev.yml` for local development
- Health checks ensure services are ready before connecting

### Production Mode
- Redis data is persisted in a Docker volume
- Workers automatically restart on failure
- Health checks ensure service availability
- Includes monitoring stack (Prometheus, Grafana)

## Data Persistence

### View Volumes

```bash
docker volume ls | grep neo-alexandria
```

### Backup PostgreSQL Data

```bash
# Development
docker exec neo-alexandria-postgres-dev pg_dump -U postgres neo_alexandria_dev > backup.sql

# Production
docker exec neo-alexandria-postgres pg_dump -U postgres backend > backup.sql
```

### Restore PostgreSQL Data

```bash
# Development
docker exec -i neo-alexandria-postgres-dev psql -U postgres neo_alexandria_dev < backup.sql

# Production
docker exec -i neo-alexandria-postgres psql -U postgres backend < backup.sql
```

## Troubleshooting

### Services Won't Start

Check logs:
```bash
docker-compose -f docker-compose.dev.yml logs
```

### PostgreSQL Connection Refused

Ensure PostgreSQL is healthy:
```bash
docker-compose -f docker-compose.dev.yml ps
```

Wait for health check to pass (may take 10-15 seconds on first start).

### Redis Connection Issues

Test Redis connectivity:
```bash
docker exec neo-alexandria-redis-dev redis-cli ping
```

Should return `PONG`.

### Port Already in Use

Change ports in `.env` file:
```bash
POSTGRES_PORT=5433
REDIS_PORT=6380
```
