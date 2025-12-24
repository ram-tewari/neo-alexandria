# Deployment Guide

Docker and production deployment for Neo Alexandria 2.0.

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/neo_alexandria
    depends_on:
      - db
    volumes:
      - ./storage:/app/storage

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=neo_alexandria
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### Build and Run

```bash
# Build image
docker build -t neo-alexandria .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -v $(pwd)/storage:/app/storage \
  neo-alexandria
```

## Production Configuration

### Gunicorn Settings

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4  # (2 * CPU cores) + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:password@host:5432/neo_alexandria
DEBUG=false
LOG_LEVEL=WARNING

# AI Models
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn

# Search
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=5000

# Security (future)
# API_KEY_REQUIRED=true
# CORS_ORIGINS=https://your-domain.com
```

### PostgreSQL Production Setup

```bash
# Create database
createdb neo_alexandria

# Create user with limited privileges
psql -c "CREATE USER neo_app WITH PASSWORD 'secure_password';"
psql -c "GRANT CONNECT ON DATABASE neo_alexandria TO neo_app;"
psql -c "GRANT USAGE ON SCHEMA public TO neo_app;"
psql -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO neo_app;"

# Run migrations
DATABASE_URL=postgresql://neo_app:secure_password@localhost:5432/neo_alexandria \
  alembic upgrade head
```

## Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/neo-alexandria
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (if any)
    location /static {
        alias /app/static;
        expires 30d;
    }
}
```

## Systemd Service

```ini
# /etc/systemd/system/neo-alexandria.service
[Unit]
Description=Neo Alexandria API
After=network.target postgresql.service

[Service]
User=neo-app
Group=neo-app
WorkingDirectory=/opt/neo-alexandria
Environment="PATH=/opt/neo-alexandria/.venv/bin"
Environment="DATABASE_URL=postgresql://user:pass@localhost:5432/neo_alexandria"
ExecStart=/opt/neo-alexandria/.venv/bin/gunicorn app.main:app -c gunicorn.conf.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable neo-alexandria
sudo systemctl start neo-alexandria
sudo systemctl status neo-alexandria
```

## Health Checks

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /monitoring/status
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Backup Strategy

### Automated PostgreSQL Backup

```bash
#!/bin/bash
# /opt/neo-alexandria/scripts/backup.sh

BACKUP_DIR=/var/backups/neo-alexandria
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup
pg_dump -h localhost -U postgres neo_alexandria | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Remove old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

```bash
# Cron job (daily at 2 AM)
0 2 * * * /opt/neo-alexandria/scripts/backup.sh
```

### Storage Backup

```bash
# Backup storage directory
rsync -avz /opt/neo-alexandria/storage/ /backup/storage/
```

## Monitoring

### Prometheus Metrics (Planned)

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'neo-alexandria'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

### Log Aggregation

```bash
# Send logs to centralized logging
docker-compose logs -f | logger -t neo-alexandria
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  api:
    deploy:
      replicas: 3
    
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - api
```

### Database Connection Pooling

For high-traffic deployments, use PgBouncer:

```ini
# pgbouncer.ini
[databases]
neo_alexandria = host=localhost dbname=neo_alexandria

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## Related Documentation

- [Setup Guide](setup.md) - Development setup
- [Database Architecture](../architecture/database.md) - Database configuration
- [Troubleshooting](troubleshooting.md) - Common issues
