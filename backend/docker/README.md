# Docker Configuration

This directory contains Docker configuration files for Neo Alexandria.

## Files

- **Dockerfile** - Container image definition for the FastAPI application
- **docker-compose.yml** - Multi-service orchestration (Redis, Celery workers, Beat, Flower)

## Quick Start

### Start All Services

```bash
cd backend/docker
docker-compose up -d
```

### Services

- **Redis** - Message broker and cache (port 6379)
- **Celery Workers** - 4 background task workers
- **Celery Beat** - Scheduled task scheduler
- **Flower** - Task monitoring dashboard (port 5555)

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

Access Flower dashboard at: http://localhost:5555

## Environment Variables

Required environment variables (set in docker-compose.yml):
- `DATABASE_URL` - Database connection string
- `CELERY_BROKER_URL` - Redis broker URL
- `CELERY_RESULT_BACKEND` - Redis result backend URL

## Notes

- Redis data is persisted in a Docker volume
- Workers automatically restart on failure
- Health checks ensure service availability
