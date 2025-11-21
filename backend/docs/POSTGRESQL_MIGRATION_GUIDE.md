# PostgreSQL Migration Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Migration Procedure](#migration-procedure)
5. [Validation and Testing](#validation-and-testing)
6. [Rollback Procedures](#rollback-procedures)
7. [Known Limitations](#known-limitations)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)
10. [Post-Migration Tasks](#post-migration-tasks)

## Overview

This guide provides step-by-step instructions for migrating Neo Alexandria 2.0 from SQLite to PostgreSQL. The migration includes:

- Schema migration using Alembic
- Data migration with validation
- Full-text search conversion (FTS5 → PostgreSQL tsvector)
- JSON to JSONB optimization
- Connection pool configuration
- Rollback procedures for contingency scenarios

**Migration Goals:**
- Zero data loss
- Minimal downtime
- Backward compatibility with SQLite for development
- Enhanced performance and concurrency with PostgreSQL

**Estimated Time:**
- Small database (<10K resources): 15-30 minutes
- Medium database (10K-100K resources): 1-2 hours
- Large database (>100K resources): 2-4 hours

## Prerequisites

### System Requirements

**PostgreSQL Server:**
- PostgreSQL 15 or higher
- Minimum 4GB RAM (8GB+ recommended for production)
- SSD storage recommended
- Network connectivity from application server

**Application Server:**
- Python 3.11+
- SQLAlchemy 2.0+
- psycopg2-binary or asyncpg driver
- Alembic for schema migrations

### Required Software

```bash
# Install PostgreSQL client tools
# Ubuntu/Debian
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Database Access

Ensure you have:
- PostgreSQL superuser or database owner credentials
- Ability to create databases and extensions
- Network access to PostgreSQL server (port 5432)
- Sufficient disk space (2x current SQLite database size recommended)

### Backup Current Database

**CRITICAL: Always backup your SQLite database before migration!**

```bash
# Create timestamped backup
cp backend.db backend.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup integrity
sqlite3 backend.db.backup_* "PRAGMA integrity_check;"
```

## Pre-Migration Checklist

- [ ] PostgreSQL server installed and running
- [ ] Database credentials configured
- [ ] SQLite database backed up
- [ ] Application stopped (for production migration)
- [ ] Sufficient disk space available
- [ ] Network connectivity verified
- [ ] Migration scripts tested in staging environment
- [ ] Rollback plan reviewed and understood
- [ ] Stakeholders notified of maintenance window

## Migration Procedure

### Step 1: Provision PostgreSQL Database

**Option A: Using Docker Compose (Development)**

```bash
cd backend/docker
docker-compose up -d postgres

# Verify PostgreSQL is running
docker-compose ps
docker-compose logs postgres
```

**Option B: Managed Service (Production)**

Use a managed PostgreSQL service:
- AWS RDS for PostgreSQL
- Google Cloud SQL for PostgreSQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases

**Option C: Self-Hosted (Production)**

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE neo_alexandria;
CREATE USER neo_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE neo_alexandria TO neo_user;
\q
```

### Step 2: Configure Environment Variables

Update your `.env` file or environment configuration:

```bash
# Development (.env.development)
DATABASE_URL=postgresql://neo_user:password@localhost:5432/neo_alexandria

# Staging (.env.staging)
DATABASE_URL=postgresql://neo_user:password@staging-db.example.com:5432/neo_alexandria

# Production (.env.production)
DATABASE_URL=postgresql://neo_user:password@prod-db.example.com:5432/neo_alexandria?sslmode=require
```

**Security Best Practices:**
- Use strong passwords (16+ characters, mixed case, numbers, symbols)
- Enable SSL/TLS for production connections (`sslmode=require`)
- Store credentials in secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Restrict database access by IP address
- Use read-only replicas for reporting queries

### Step 3: Run Schema Migration

Apply Alembic migrations to create PostgreSQL schema:

```bash
cd backend

# Verify current migration status
alembic current

# Run migrations
alembic upgrade head

# Verify migration success
alembic current
# Should show: 20250120_postgresql_compatibility (head)
```

**What This Does:**
- Creates all tables with PostgreSQL-optimized schema
- Installs PostgreSQL extensions (pg_trgm, uuid-ossp)
- Converts JSON columns to JSONB
- Creates GIN indexes on JSONB columns
- Sets up full-text search with tsvector columns
- Creates triggers for automatic search vector updates
- Adds optimized indexes for common query patterns

### Step 4: Validate Schema

Verify that all tables and indexes were created correctly:

```bash
# Connect to PostgreSQL
psql -h localhost -U neo_user -d neo_alexandria

-- List all tables
\dt

-- Check installed extensions
\dx

-- Verify indexes
\di

-- Check table structure for resources
\d resources

-- Exit
\q
```

**Expected Output:**
- All tables from SQLite should exist
- Extensions: pg_trgm, uuid-ossp
- JSONB columns: subject, relation, embedding, sparse_embedding
- TSVector column: search_vector (on resources table)
- Multiple GIN indexes on JSONB and tsvector columns

### Step 5: Run Data Migration

Execute the data migration script:

```bash
cd backend

# Dry run first (validation only, no data transfer)
python scripts/migrate_sqlite_to_postgresql.py \
    --source sqlite:///backend.db \
    --target postgresql://neo_user:password@localhost:5432/neo_alexandria \
    --dry-run \
    --verbose

# If dry run succeeds, run actual migration
python scripts/migrate_sqlite_to_postgresql.py \
    --source sqlite:///backend.db \
    --target postgresql://neo_user:password@localhost:5432/neo_alexandria \
    --validate \
    --verbose
```

**Migration Script Features:**
- Respects foreign key dependencies
- Batch processing (1000 records per batch)
- Progress reporting
- Automatic data validation
- Detailed error logging
- Migration report generation

**Monitor Progress:**
The script will output:
- Connection status
- Schema validation results
- Per-table migration progress
- Row counts and percentages
- Validation results
- Final migration report

**Migration Report:**
A detailed report is saved to `migration_report_YYYYMMDD_HHMMSS.txt` containing:
- Summary statistics
- Per-table row counts
- Success/failure status
- Error details (if any)
- Migration duration

### Step 6: Verify Data Integrity

After migration completes, verify data integrity:

```bash
# Check row counts match
psql -h localhost -U neo_user -d neo_alexandria -c "
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY tablename;
"

# Compare with SQLite counts
sqlite3 backend.db "
SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=t.name) as count
FROM sqlite_master t
WHERE type='table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
"
```

**Validation Checklist:**
- [ ] Row counts match between SQLite and PostgreSQL
- [ ] No errors in migration report
- [ ] All foreign key relationships intact
- [ ] JSONB data properly converted
- [ ] Full-text search indexes created
- [ ] No NULL values in required columns

## Validation and Testing

### Functional Testing

Test core application functionality:

```bash
# Start application with PostgreSQL
export DATABASE_URL=postgresql://neo_user:password@localhost:5432/neo_alexandria
uvicorn backend.app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/resources?limit=10
curl http://localhost:8000/api/v1/search?q=machine+learning
```

### Performance Testing

Compare query performance:

```sql
-- Test full-text search performance
EXPLAIN ANALYZE
SELECT * FROM resources
WHERE search_vector @@ to_tsquery('english', 'machine & learning')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'machine & learning')) DESC
LIMIT 25;

-- Test JSONB containment query
EXPLAIN ANALYZE
SELECT * FROM resources
WHERE subject @> '["Machine Learning"]'::jsonb
LIMIT 25;

-- Test index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Run Test Suite

Execute the full test suite against PostgreSQL:

```bash
cd backend

# Set test database URL
export TEST_DATABASE_URL=postgresql://neo_user:password@localhost:5432/neo_alexandria_test

# Create test database
psql -h localhost -U neo_user -c "CREATE DATABASE neo_alexandria_test;"

# Run migrations on test database
DATABASE_URL=$TEST_DATABASE_URL alembic upgrade head

# Run tests
pytest tests/ -v

# Run PostgreSQL-specific tests
pytest tests/ -m postgresql -v
```

## Rollback Procedures

### When to Rollback

Consider rolling back if:
- Data validation fails (row count mismatches)
- Critical application functionality broken
- Unacceptable performance degradation
- Data corruption detected
- Migration errors cannot be resolved quickly

### Rollback Decision Matrix

| Issue | Severity | Action |
|-------|----------|--------|
| Row count mismatch <1% | Low | Investigate and fix specific tables |
| Row count mismatch >1% | High | Rollback and investigate |
| Application errors | Medium | Check logs, may need rollback |
| Performance degradation >50% | High | Rollback and optimize |
| Data corruption | Critical | Immediate rollback |

### Rollback Procedure

**Step 1: Stop Application**

```bash
# Docker Compose
docker-compose down

# Systemd
sudo systemctl stop neo-alexandria

# Manual
pkill -f "uvicorn backend.app.main:app"
```

**Step 2: Restore SQLite Database**

```bash
# Restore from backup
cp backend.db.backup_YYYYMMDD_HHMMSS backend.db

# Verify integrity
sqlite3 backend.db "PRAGMA integrity_check;"
```

**Step 3: Update Environment Configuration**

```bash
# Revert to SQLite in .env
DATABASE_URL=sqlite:///backend.db
```

**Step 4: Restart Application**

```bash
# Docker Compose
docker-compose up -d

# Systemd
sudo systemctl start neo-alexandria

# Manual
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**Step 5: Verify Application**

```bash
# Check health endpoint
curl http://localhost:8000/health

# Verify data access
curl http://localhost:8000/api/v1/resources?limit=10
```

### Alternative: Reverse Migration (PostgreSQL → SQLite)

If you need to migrate data back from PostgreSQL to SQLite:

```bash
cd backend

# Run reverse migration script
python scripts/migrate_postgresql_to_sqlite.py \
    --source postgresql://neo_user:password@localhost:5432/neo_alexandria \
    --target sqlite:///backend_restored.db \
    --validate \
    --verbose

# Verify restored database
sqlite3 backend_restored.db "SELECT COUNT(*) FROM resources;"

# If validation passes, replace main database
mv backend.db backend.db.old
mv backend_restored.db backend.db
```

**⚠️ WARNING: Reverse Migration Limitations**

The reverse migration script has the following limitations:

1. **JSONB → JSON Conversion**
   - JSONB binary format is converted to JSON text
   - No performance optimization from JSONB
   - Queries using JSONB operators must be rewritten

2. **Full-Text Search Loss**
   - PostgreSQL tsvector columns are not migrated
   - Must rebuild FTS5 virtual tables in SQLite
   - Search ranking may differ

3. **Index Loss**
   - GIN indexes on JSONB columns cannot be recreated
   - Must recreate SQLite-compatible indexes
   - Some query performance may degrade

4. **Array Type Conversion**
   - PostgreSQL arrays converted to JSON arrays
   - Array operators not available in SQLite

5. **Constraint Differences**
   - Some PostgreSQL-specific constraints may be lost
   - Check constraints may need manual recreation

### Rollback Testing

**Test rollback procedure in staging BEFORE production migration:**

```bash
# 1. Perform test migration to PostgreSQL
# 2. Verify application works
# 3. Perform rollback to SQLite
# 4. Verify application still works
# 5. Document any issues encountered
# 6. Update rollback procedure if needed
```

## Known Limitations

### PostgreSQL → SQLite Conversion Limitations

When reverting from PostgreSQL to SQLite, be aware of:

#### 1. Data Type Conversions

| PostgreSQL Type | SQLite Type | Notes |
|----------------|-------------|-------|
| JSONB | TEXT (JSON) | Binary optimization lost |
| TSVector | Not migrated | Full-text search must be rebuilt |
| UUID | TEXT | String representation |
| ARRAY | TEXT (JSON) | Array operators not available |
| TIMESTAMP WITH TIMEZONE | TEXT | Timezone info preserved as string |

#### 2. Feature Loss

**Full-Text Search:**
- PostgreSQL tsvector/tsquery → SQLite FTS5
- Search ranking algorithms differ
- Must rebuild FTS5 virtual tables manually
- Query syntax differences

**JSONB Queries:**
```sql
-- PostgreSQL (JSONB operators)
SELECT * FROM resources WHERE subject @> '["AI"]'::jsonb;

-- SQLite (JSON functions)
SELECT * FROM resources WHERE json_extract(subject, '$') LIKE '%AI%';
```

**Array Operations:**
```sql
-- PostgreSQL (array operators)
SELECT * FROM resources WHERE 'AI' = ANY(subject);

-- SQLite (JSON functions)
SELECT * FROM resources WHERE EXISTS (
    SELECT 1 FROM json_each(subject) WHERE value = 'AI'
);
```

#### 3. Performance Implications

- JSONB queries in PostgreSQL use GIN indexes (fast)
- JSON queries in SQLite require full table scans (slow)
- Full-text search in PostgreSQL uses GIN indexes
- FTS5 in SQLite uses separate virtual tables

#### 4. Concurrency Limitations

- PostgreSQL: MVCC, row-level locking, high concurrency
- SQLite: Database-level locking, limited write concurrency
- May experience write contention after rollback

### SQLite Compatibility Maintenance

To maintain SQLite compatibility for one release cycle:

**1. Keep Database-Agnostic Code:**
```python
# Good: Works with both databases
resources = db.query(Resource).filter(Resource.title.like('%AI%')).all()

# Avoid: PostgreSQL-specific
resources = db.query(Resource).filter(
    Resource.subject.op('@>')(cast(['AI'], JSONB))
).all()
```

**2. Use Abstraction Layers:**
```python
# Use search service abstraction
search_service = SearchService(db)
results = search_service.search("machine learning")

# Service automatically selects SQLite FTS5 or PostgreSQL tsvector
```

**3. Test Against Both Databases:**
```bash
# Run tests with SQLite
pytest tests/

# Run tests with PostgreSQL
TEST_DATABASE_URL=postgresql://... pytest tests/
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Connection Pool Exhausted

**Symptoms:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 40 reached
```

**Solution:**
```python
# Increase pool size in backend/app/database/base.py
postgresql_params = {
    'pool_size': 30,  # Increase from 20
    'max_overflow': 60,  # Increase from 40
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

#### Issue: Slow Query Performance

**Symptoms:**
- Queries taking >1 second
- High CPU usage
- Slow API responses

**Solution:**
```sql
-- Check for missing indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND idx_scan = 0;

-- Analyze query performance
EXPLAIN ANALYZE SELECT ...;

-- Update table statistics
ANALYZE resources;
```

#### Issue: Migration Script Fails

**Symptoms:**
```
Error migrating table 'resources': foreign key constraint violation
```

**Solution:**
```bash
# Check table order in migration script
# Ensure parent tables are migrated before child tables

# Temporarily disable foreign key checks (PostgreSQL)
psql -h localhost -U neo_user -d neo_alexandria -c "
SET session_replication_role = replica;
-- Run migration
SET session_replication_role = DEFAULT;
"
```

#### Issue: Full-Text Search Not Working

**Symptoms:**
- Search returns no results
- Search vector column is NULL

**Solution:**
```sql
-- Manually update search vectors
UPDATE resources
SET search_vector = 
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(array_to_string(subject, ' '), '')), 'C');

-- Verify trigger exists
SELECT tgname, tgtype, tgenabled
FROM pg_trigger
WHERE tgrelid = 'resources'::regclass;
```

#### Issue: JSONB Conversion Errors

**Symptoms:**
```
Error: invalid input syntax for type json
```

**Solution:**
```python
# Validate JSON before migration
import json

def validate_json_column(value):
    if value is None:
        return None
    try:
        if isinstance(value, str):
            json.loads(value)
        return value
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON: {value}")
        return None
```

#### Issue: SSL Connection Errors

**Symptoms:**
```
psycopg2.OperationalError: SSL connection has been closed unexpectedly
```

**Solution:**
```bash
# Update connection string with SSL parameters
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require&sslrootcert=/path/to/ca-cert.pem

# Or disable SSL for development
DATABASE_URL=postgresql://user:pass@localhost:5432/db?sslmode=disable
```

### Getting Help

If you encounter issues not covered here:

1. Check application logs: `tail -f backend/logs/app.log`
2. Check PostgreSQL logs: `docker-compose logs postgres` or `/var/log/postgresql/`
3. Review migration report: `migration_report_*.txt`
4. Check database status: `psql -h localhost -U neo_user -d neo_alexandria`
5. Consult PostgreSQL documentation: https://www.postgresql.org/docs/
6. Open an issue on GitHub with:
   - Error messages
   - Migration report
   - Database versions
   - Steps to reproduce

## Performance Tuning

### PostgreSQL Configuration

Optimize PostgreSQL for Neo Alexandria workload:

```sql
-- postgresql.conf settings

-- Memory settings (adjust based on available RAM)
shared_buffers = 2GB                    -- 25% of RAM
effective_cache_size = 6GB              -- 75% of RAM
work_mem = 16MB                         -- Per-operation memory
maintenance_work_mem = 512MB            -- For VACUUM, CREATE INDEX

-- Connection settings
max_connections = 100                   -- Adjust based on load
superuser_reserved_connections = 3

-- Query planner settings
random_page_cost = 1.1                  -- For SSD storage
effective_io_concurrency = 200          -- For SSD storage

-- Write-ahead log settings
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 1GB

-- Logging settings
log_min_duration_statement = 1000       -- Log queries >1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

-- Autovacuum settings
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
```

### Index Optimization

Monitor and optimize indexes:

```sql
-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public' AND idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find missing indexes (queries with sequential scans)
SELECT schemaname, tablename, seq_scan, seq_tup_read,
       idx_scan, idx_tup_fetch,
       seq_tup_read / seq_scan as avg_seq_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public' AND seq_scan > 0
ORDER BY seq_tup_read DESC;

-- Check index bloat
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Query Optimization

Optimize slow queries:

```sql
-- Enable query timing
\timing on

-- Analyze query plan
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) 
SELECT * FROM resources 
WHERE subject @> '["Machine Learning"]'::jsonb
LIMIT 25;

-- Update table statistics
ANALYZE resources;

-- Reindex if needed
REINDEX TABLE resources;
```

### Connection Pool Tuning

Optimize connection pool settings:

```python
# backend/app/database/base.py

# Calculate optimal pool size
# Formula: pool_size = (number_of_cpu_cores * 2) + effective_spindle_count
# For 4 cores + SSD: (4 * 2) + 1 = 9

# Conservative settings (current)
pool_size = 20
max_overflow = 40

# Aggressive settings (high concurrency)
pool_size = 30
max_overflow = 60

# Monitor pool usage
@app.get("/monitoring/database")
async def database_metrics():
    pool_status = get_pool_status()
    return {
        "pool_size": pool_status['size'],
        "connections_in_use": pool_status['checked_out'],
        "connections_available": pool_status['checked_in'],
        "overflow_connections": pool_status['overflow'],
    }
```

## Post-Migration Tasks

### 1. Update Documentation

- [ ] Update README.md with PostgreSQL setup instructions
- [ ] Update DEVELOPER_GUIDE.md with database configuration
- [ ] Update API documentation if any changes
- [ ] Update CHANGELOG.md with migration notes

### 2. Monitor Performance

```bash
# Set up monitoring
# - Connection pool metrics
# - Query performance
# - Database size growth
# - Index usage statistics

# Create monitoring dashboard
# - Grafana + Prometheus
# - pgAdmin
# - Custom monitoring endpoint
```

### 3. Schedule Maintenance

```bash
# Set up automated backups
# See POSTGRESQL_BACKUP_GUIDE.md

# Schedule VACUUM ANALYZE
# Add to cron:
0 2 * * * psql -h localhost -U neo_user -d neo_alexandria -c "VACUUM ANALYZE;"

# Monitor database size
# Add to cron:
0 0 * * * psql -h localhost -U neo_user -d neo_alexandria -c "SELECT pg_size_pretty(pg_database_size('neo_alexandria'));"
```

### 4. Optimize Queries

- Review slow query logs
- Add missing indexes
- Optimize N+1 queries
- Implement query result caching

### 5. Security Hardening

```bash
# Restrict database access
# Update pg_hba.conf:
# host    neo_alexandria    neo_user    10.0.0.0/8    md5

# Enable SSL/TLS
# ssl = on
# ssl_cert_file = '/path/to/server.crt'
# ssl_key_file = '/path/to/server.key'

# Rotate credentials
# Update passwords regularly
# Use secrets manager
```

### 6. Decommission SQLite (After Stability Period)

After 1-2 release cycles of stable PostgreSQL operation:

- [ ] Remove SQLite-specific code paths
- [ ] Remove FTS5 search strategy
- [ ] Remove SQLite connection parameters
- [ ] Update tests to PostgreSQL only
- [ ] Archive SQLite backup files
- [ ] Update documentation to remove SQLite references

## Conclusion

This migration guide provides comprehensive instructions for migrating Neo Alexandria 2.0 from SQLite to PostgreSQL. Key takeaways:

- **Always backup** before migration
- **Test in staging** before production
- **Have a rollback plan** ready
- **Monitor performance** after migration
- **Maintain SQLite compatibility** for one release cycle

For additional support:
- Review PostgreSQL documentation: https://www.postgresql.org/docs/
- Consult SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Check application logs and migration reports
- Open GitHub issues for bugs or questions

**Next Steps:**
1. Review this guide thoroughly
2. Test migration in staging environment
3. Schedule production migration window
4. Execute migration following this guide
5. Monitor application performance
6. Document any issues or improvements
