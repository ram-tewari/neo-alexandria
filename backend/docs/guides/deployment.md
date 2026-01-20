# Neo Alexandria 2.0 - Deployment Guide

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL running on host (port 5432)
- At least 4GB RAM available
- 10GB disk space

### Build Time Expectations

**First-time build**: 10-15 minutes
- Downloads ~1GB of ML libraries (PyTorch 797MB, transformers, spaCy, etc.)
- Installs all Python dependencies
- Builds Docker image layers

**Subsequent starts**: 10-30 seconds
- Uses cached Docker image
- Only starts containers

**Rebuilds after code changes**: 30-60 seconds
- Only rebuilds changed layers
- Dependencies remain cached

**Note**: The initial build is slow due to large ML libraries. After the first build, Docker's layer caching makes subsequent starts very fast.

### Step 1: Configure Environment

```bash
cd backend

# Copy production environment template
cp .env.production .env

# Edit .env with your actual values
# IMPORTANT: Change JWT_SECRET_KEY and POSTGRES_PASSWORD
nano .env
```

### Step 2: Build and Start Services

```bash
# Build the Docker image
docker-compose build

# Start all services (Redis, Backend, Celery Worker)
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### Step 3: Run Database Migrations

```bash
# Run migrations to create/update database schema
docker-compose exec backend alembic upgrade head
```

### Step 4: Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","redis":"connected"}
```

### Step 5: Access Swagger Documentation

Open your browser and navigate to:
```
http://localhost:8000/docs
```

This will show the interactive API documentation where you can test all endpoints.

---

## Configuration Details

### Database Connection

The backend connects to your existing PostgreSQL database on the host machine:

```yaml
POSTGRES_SERVER: host.docker.internal  # Docker's host gateway
POSTGRES_PORT: 5432
POSTGRES_USER: neo_user
POSTGRES_PASSWORD: your_password
POSTGRES_DB: neo_alexandria
```

**Note**: `host.docker.internal` allows Docker containers to access services running on the host machine.

### Advanced RAG Features

Chunking is **enabled by default** for automatic processing:

```yaml
CHUNK_ON_RESOURCE_CREATE: true        # Auto-chunk on upload
CHUNKING_STRATEGY: semantic           # Semantic chunking
CHUNK_SIZE: 500                       # 500 words per chunk
CHUNK_OVERLAP: 50                     # 50 words overlap
GRAPH_EXTRACTION_ENABLED: true        # Extract knowledge graph
GRAPH_EXTRACT_ON_CHUNK: true          # Auto-extract after chunking
```

### Rate Limiting

Three tiers configured:

- **Free**: 100 requests/minute
- **Premium**: 1000 requests/minute
- **Admin**: Unlimited (0 = no limit)

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Backend    │  │    Redis     │  │    Celery    │ │
│  │   (FastAPI)  │  │   (Cache)    │  │   (Worker)   │ │
│  │   Port 8000  │  │   Port 6379  │  │              │ │
│  └──────┬───────┘  └──────────────┘  └──────────────┘ │
│         │                                               │
└─────────┼───────────────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │  PostgreSQL  │
   │  (Host DB)   │
   │  Port 5432   │
   └──────────────┘
```

---

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f redis
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Check current migration version
docker-compose exec backend alembic current

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Maintenance

```bash
# Rebuild after code changes
docker-compose build backend
docker-compose up -d backend

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Access backend shell
docker-compose exec backend bash

# Access Python shell
docker-compose exec backend python
```

---

## Testing the Deployment

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "modules": {
    "resources": "healthy",
    "search": "healthy",
    "auth": "healthy"
  }
}
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Save the `access_token` from the response.

### 4. Create a Resource

```bash
curl -X POST http://localhost:8000/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Test Document",
    "content": "This is a test document for Neo Alexandria.",
    "resource_type": "article"
  }'
```

### 5. Search Resources

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "test document",
    "search_type": "hybrid"
  }'
```

---

## Swagger UI Testing

### Access Swagger

Navigate to: `http://localhost:8000/docs`

### Using Swagger

1. **Authorize**: Click the "Authorize" button (top right)
2. **Login**: Use `/auth/login` endpoint to get a token
3. **Copy Token**: Copy the `access_token` from the response
4. **Paste Token**: Paste into the authorization dialog
5. **Test Endpoints**: Try any endpoint with the "Try it out" button

### Recommended Test Flow

1. **POST /auth/register** - Create a user
2. **POST /auth/login** - Get access token
3. **Authorize** - Add token to Swagger
4. **POST /resources** - Create a resource
5. **GET /resources** - List resources
6. **POST /search** - Search resources
7. **POST /collections** - Create a collection
8. **POST /annotations** - Add an annotation

---

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow new logs
docker-compose logs -f --tail=0 backend
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Network info
docker network inspect backend_neo-network
```

### Health Monitoring

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## Troubleshooting

### Backend Won't Start

**Check logs**:
```bash
docker-compose logs backend
```

**Common issues**:
1. Database connection failed
   - Verify PostgreSQL is running on host
   - Check credentials in `.env`
   - Ensure port 5432 is accessible

2. Redis connection failed
   - Check Redis container: `docker-compose ps redis`
   - Restart Redis: `docker-compose restart redis`

3. Port 8000 already in use
   - Change port in `docker-compose.yml`: `"8001:8000"`

### Database Migration Errors

```bash
# Check current version
docker-compose exec backend alembic current

# Try manual migration
docker-compose exec backend alembic upgrade head

# If stuck, rollback and retry
docker-compose exec backend alembic downgrade -1
docker-compose exec backend alembic upgrade head
```

### Celery Worker Not Processing Tasks

```bash
# Check worker logs
docker-compose logs celery-worker

# Restart worker
docker-compose restart celery-worker

# Check Redis connection
docker-compose exec celery-worker python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > Increase to 8GB

# Or limit container memory in docker-compose.yml:
# mem_limit: 2g
```

---

## Production Hardening

### Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Use strong `POSTGRES_PASSWORD`
- [ ] Enable HTTPS (use nginx reverse proxy)
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure OAuth2 (optional)
- [ ] Set up monitoring and alerting

### Performance Optimization

- [ ] Use PostgreSQL connection pooling
- [ ] Configure Redis persistence
- [ ] Set up Celery autoscaling
- [ ] Enable gzip compression
- [ ] Configure CDN for static files
- [ ] Set up database indexes
- [ ] Monitor query performance

### Backup Strategy

```bash
# Backup PostgreSQL database
docker-compose exec backend pg_dump -U neo_user neo_alexandria > backup.sql

# Backup Redis data
docker-compose exec redis redis-cli SAVE

# Backup uploaded files
tar -czf storage_backup.tar.gz storage/
```

---

## Scaling

### Horizontal Scaling

```yaml
# Scale Celery workers
docker-compose up -d --scale celery-worker=3

# Scale backend (requires load balancer)
docker-compose up -d --scale backend=2
```

### Load Balancer (nginx)

```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

---

## Next Steps

1. **Test all endpoints** using Swagger UI
2. **Monitor logs** for any errors
3. **Set up backups** for database and files
4. **Configure OAuth2** if needed
5. **Enable HTTPS** for production
6. **Set up monitoring** (Sentry, Prometheus)
7. **Load test** with realistic traffic

---

## Support

- **Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Logs**: `docker-compose logs -f backend`
- **Issues**: Check GitHub repository

---

**Deployment Status**: ✅ Ready for Staging  
**Production Ready**: ⚠️ Needs hardening (see checklist above)  
**Last Updated**: January 6, 2026
