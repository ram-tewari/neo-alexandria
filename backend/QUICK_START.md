# 🚀 Neo Alexandria 2.0 - Quick Start

## TL;DR - Get Running in 3 Commands

```bash
cd backend
cp .env.production .env
# Edit .env: Set JWT_SECRET_KEY and POSTGRES_PASSWORD
docker-compose up -d
```

Then open: **http://localhost:8000/docs**

---

## What You Get

- ✅ **97+ API endpoints** across 13 modules
- ✅ **Automatic chunking** on resource upload
- ✅ **Knowledge graph extraction**
- ✅ **Hybrid search** (keyword + semantic)
- ✅ **JWT authentication** with rate limiting
- ✅ **Swagger UI** for testing
- ✅ **Health monitoring**

---

## Prerequisites

- Docker & Docker Compose
- PostgreSQL running on localhost:5432
- 4GB RAM minimum

## ⏱️ Build Time Expectations

- **First build**: 10-15 minutes (downloads ~1GB of ML libraries)
- **Subsequent starts**: 10-30 seconds (uses cached image)
- **After code changes**: 30-60 seconds (only rebuilds changed layers)

The initial build is slow due to PyTorch (797MB) and other ML dependencies. After that, Docker caching makes restarts very fast!

---

## Step-by-Step

### 1. Configure

```bash
cd backend
cp .env.production .env
```

Edit `.env` and set:
- `JWT_SECRET_KEY` - Use a strong random value
- `POSTGRES_PASSWORD` - Your actual PostgreSQL password
- `POSTGRES_USER` - Your PostgreSQL user (default: neo_user)
- `POSTGRES_DB` - Your database name (default: neo_alexandria)

### 2. Deploy

**Windows**:
```cmd
start.bat
```

**Linux/Mac**:
```bash
chmod +x start.sh
./start.sh
```

### 3. Test

Open browser: **http://localhost:8000/docs**

---

## First API Call

### 1. Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Copy the `access_token` from response.

### 3. Create Resource

```bash
curl -X POST http://localhost:8000/resources \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "content": "This will be automatically chunked and indexed.",
    "resource_type": "article"
  }'
```

### 4. Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test",
    "search_type": "hybrid"
  }'
```

---

## Using Swagger UI

1. Go to: **http://localhost:8000/docs**
2. Click **"Authorize"** (top right)
3. Use `/auth/login` to get token
4. Paste token in authorization dialog
5. Test any endpoint with "Try it out"

---

## Common Commands

```bash
# View logs
docker-compose logs -f backend

# Restart
docker-compose restart backend

# Stop
docker-compose down

# Health check
curl http://localhost:8000/health
```

---

## Troubleshooting

**Backend won't start?**
- Check logs: `docker-compose logs backend`
- Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check `.env` credentials

**Can't connect to database?**
- Verify `POSTGRES_PASSWORD` in `.env`
- Ensure PostgreSQL allows connections from Docker

**Port 8000 in use?**
- Change port in `docker-compose.yml`: `"8001:8000"`

---

## What's Next?

1. ✅ Test endpoints in Swagger
2. ✅ Create resources and test chunking
3. ✅ Try hybrid search
4. ✅ Create collections and annotations
5. ⚠️ Configure OAuth2 (optional)
6. ⚠️ Set up HTTPS for production
7. ⚠️ Configure backups

---

## Documentation

- **Full Deployment Guide**: `docs/guides/deployment.md`
- **API Reference**: `http://localhost:8000/docs`
- **Architecture**: `docs/architecture/overview.md`

---

**Status**: ✅ Ready to Test  
**Swagger**: http://localhost:8000/docs  
**Health**: http://localhost:8000/health
