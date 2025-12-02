# Design Document

## Overview

This design document outlines the architecture and implementation strategy for migrating Neo Alexandria 2.0 from SQLite to PostgreSQL. The migration maintains backward compatibility with SQLite for development while providing production-grade PostgreSQL support with enhanced concurrency, performance, and reliability.

### Migration Goals

1. **Zero Downtime Migration**: Provide tooling for seamless data migration with validation
2. **Backward Compatibility**: Maintain SQLite support for local development and testing
3. **Performance Optimization**: Leverage PostgreSQL-specific features for improved query performance
4. **Production Readiness**: Implement connection pooling, monitoring, and backup strategies
5. **Developer Experience**: Ensure transparent database switching via environment configuration

### Key Design Decisions

- **Database Abstraction**: Use SQLAlchemy ORM to maintain database-agnostic code
- **Conditional Features**: Implement database-specific optimizations (JSONB, full-text search) with runtime detection
- **Migration Strategy**: Provide both schema migration (Alembic) and data migration (custom script) tools
- **Testing Strategy**: Support running tests against both SQLite and PostgreSQL
- **Deployment Strategy**: Use Docker Compose for local PostgreSQL setup and production deployment

## Architecture

### Database Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLAlchemy ORM Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database URL Detection & Engine Configuration       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐       ┌──────────────────────┐
│   SQLite Engine      │       │  PostgreSQL Engine   │
│  ┌────────────────┐  │       │  ┌────────────────┐  │
│  │ File-based DB  │  │       │  │ Connection Pool│  │
│  │ FTS5 Search    │  │       │  │ Full-Text Search│ │
│  │ JSON Storage   │  │       │  │ JSONB Storage  │  │
│  └────────────────┘  │       │  │ pg_trgm        │  │
└──────────────────────┘       │  └────────────────┘  │
                               └──────────────────────┘
```

### Connection Management Architecture

**Async Engine (Primary)**
- Used for all FastAPI endpoint handlers
- Supports concurrent request handling
- Connection pool: 20 base + 40 overflow
- Automatic connection health checks (pool_pre_ping)

**Sync Engine (Background Tasks)**
- Used for Celery tasks and background processing
- Separate connection pool to avoid blocking async operations
- Same pool configuration as async engine

### Database-Specific Feature Detection

```python
def get_database_type(engine) -> str:
    """Detect database type from engine."""
    dialect_name = engine.dialect.name
    if dialect_name == 'sqlite':
        return 'sqlite'
    elif dialect_name == 'postgresql':
        return 'postgresql'
    else:
        raise ValueError(f"Unsupported database: {dialect_name}")

def supports_jsonb(engine) -> bool:
    """Check if database supports JSONB."""
    return get_database_type(engine) == 'postgresql'

def get_fulltext_search_method(engine) -> str:
    """Get appropriate full-text search method."""
    db_type = get_database_type(engine)
    if db_type == 'sqlite':
        return 'fts5'
    elif db_type == 'postgresql':
        return 'pg_tsvector'
    return 'basic'
```

## Components and Interfaces

### 1. Database Configuration Module

**File**: `backend/app/database/base.py`

**Enhancements**:

```python
# PostgreSQL-specific connection parameters
postgresql_params = {
    'pool_size': 20,
    'max_overflow': 40,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'echo_pool': True,
    'connect_args': {
        'statement_timeout': '30000',  # 30 seconds
        'options': '-c timezone=utc'
    }
}

# SQLite-specific connection parameters
sqlite_params = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_pre_ping': False,
    'connect_args': {
        'check_same_thread': False,
        'timeout': 30
    }
}
```

**New Functions**:
- `get_database_type()`: Detect current database type
- `get_pool_status()`: Return connection pool metrics (already exists, enhance for PostgreSQL)
- `create_database_engine()`: Factory function for engine creation with appropriate parameters

### 2. Schema Migration (Alembic)

**New Migration**: `backend/alembic/versions/20250120_postgresql_compatibility.py`

**Schema Changes**:

1. **JSON to JSONB Conversion** (PostgreSQL only)
   - Convert `subject`, `relation`, `embedding`, `sparse_embedding` columns
   - Create GIN indexes on JSONB columns for efficient queries
   - Maintain JSON type for SQLite compatibility

2. **Full-Text Search Setup** (PostgreSQL only)
   - Create `tsvector` columns for searchable text fields
   - Create GIN indexes on tsvector columns
   - Create trigger functions to auto-update tsvector on INSERT/UPDATE
   - Install pg_trgm extension for similarity search

3. **Index Optimization**
   - Add composite indexes for common query patterns
   - Add indexes on foreign keys
   - Add indexes on timestamp columns for sorting

**Migration Structure**:
```python
def upgrade():
    # Detect database type
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    if dialect == 'postgresql':
        # PostgreSQL-specific upgrades
        upgrade_postgresql()
    else:
        # SQLite-specific upgrades (if any)
        upgrade_sqlite()

def upgrade_postgresql():
    # Install extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Convert JSON to JSONB
    # Create full-text search columns
    # Create indexes
    pass

def downgrade():
    # Reverse migration logic
    pass
```

### 3. Data Migration Script

**File**: `backend/scripts/migrate_sqlite_to_postgresql.py`

**Architecture**:

```python
class DatabaseMigrator:
    def __init__(self, source_url: str, target_url: str):
        self.source_engine = create_engine(source_url)
        self.target_engine = create_engine(target_url)
        self.batch_size = 1000
        self.stats = {}
    
    def migrate(self):
        """Execute full migration with validation."""
        self.validate_schemas()
        self.migrate_tables()
        self.validate_data()
        self.generate_report()
    
    def migrate_tables(self):
        """Migrate all tables in dependency order."""
        # Order matters due to foreign keys
        tables = [
            'classification_codes',
            'authority_subjects',
            'authority_creators',
            'authority_publishers',
            'users',
            'user_profiles',
            'resources',
            'citations',
            'collections',
            'collection_resources',
            'taxonomy_nodes',
            'resource_taxonomy',
            'annotations',
            'graph_edges',
            'graph_embeddings',
            'discovery_hypotheses',
            'user_interactions',
            'recommendation_feedback',
            'model_versions',
            'ab_test_experiments',
            'prediction_logs',
            'retraining_runs'
        ]
        
        for table_name in tables:
            self.migrate_table(table_name)
    
    def migrate_table(self, table_name: str):
        """Migrate single table with batching."""
        source_session = Session(self.source_engine)
        target_session = Session(self.target_engine)
        
        # Get table model
        table = Base.metadata.tables[table_name]
        
        # Count source rows
        source_count = source_session.execute(
            select(func.count()).select_from(table)
        ).scalar()
        
        # Migrate in batches
        offset = 0
        migrated = 0
        
        while offset < source_count:
            batch = source_session.execute(
                select(table).limit(self.batch_size).offset(offset)
            ).fetchall()
            
            # Insert batch into target
            target_session.execute(
                table.insert(),
                [dict(row._mapping) for row in batch]
            )
            target_session.commit()
            
            migrated += len(batch)
            offset += self.batch_size
            
            print(f"Migrated {migrated}/{source_count} rows from {table_name}")
        
        # Validate counts
        target_count = target_session.execute(
            select(func.count()).select_from(table)
        ).scalar()
        
        self.stats[table_name] = {
            'source_count': source_count,
            'target_count': target_count,
            'success': source_count == target_count
        }
```

**Features**:
- Batch processing to prevent memory exhaustion
- Progress reporting for long-running migrations
- Validation of row counts after migration
- Error handling with detailed logging
- Dry-run mode for testing

### 4. Full-Text Search Abstraction

**File**: `backend/app/services/search_service.py`

**Search Strategy Pattern**:

```python
class FullTextSearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str, limit: int) -> List[Resource]:
        pass

class SQLiteFTS5Strategy(FullTextSearchStrategy):
    def search(self, query: str, limit: int) -> List[Resource]:
        # Use FTS5 virtual table
        # Implementation remains unchanged
        pass

class PostgreSQLFullTextStrategy(FullTextSearchStrategy):
    def search(self, query: str, limit: int) -> List[Resource]:
        # Use tsvector and tsquery
        search_query = func.to_tsquery('english', query)
        
        results = db.query(Resource).filter(
            Resource.search_vector.op('@@')(search_query)
        ).order_by(
            func.ts_rank(Resource.search_vector, search_query).desc()
        ).limit(limit).all()
        
        return results

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.strategy = self._get_search_strategy()
    
    def _get_search_strategy(self) -> FullTextSearchStrategy:
        db_type = get_database_type(self.db.bind)
        if db_type == 'sqlite':
            return SQLiteFTS5Strategy(self.db)
        elif db_type == 'postgresql':
            return PostgreSQLFullTextStrategy(self.db)
        else:
            raise ValueError(f"Unsupported database: {db_type}")
    
    def search(self, query: str, limit: int = 25) -> List[Resource]:
        return self.strategy.search(query, limit)
```

**PostgreSQL Full-Text Search Setup**:

1. **Add tsvector column to Resource model**:
```python
search_vector: Mapped[str | None] = mapped_column(
    TSVector,
    nullable=True
)
```

2. **Create trigger to auto-update search_vector**:
```sql
CREATE OR REPLACE FUNCTION resources_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.subject, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resources_search_vector_trigger
BEFORE INSERT OR UPDATE ON resources
FOR EACH ROW EXECUTE FUNCTION resources_search_vector_update();
```

3. **Create GIN index**:
```sql
CREATE INDEX idx_resources_search_vector ON resources USING GIN(search_vector);
```

### 5. JSONB Optimization (PostgreSQL)

**Enhanced Query Performance**:

```python
# Before (JSON): Requires full column scan
resources = db.query(Resource).filter(
    Resource.subject.contains(['Machine Learning'])
).all()

# After (JSONB): Uses GIN index
resources = db.query(Resource).filter(
    Resource.subject.op('@>')(cast(['Machine Learning'], JSONB))
).all()
```

**JSONB Operators**:
- `@>`: Contains (uses GIN index)
- `?`: Key exists
- `?|`: Any key exists
- `?&`: All keys exist
- `||`: Concatenate
- `-`: Delete key

**Index Creation**:
```sql
-- Index for subject array containment queries
CREATE INDEX idx_resources_subject_gin ON resources USING GIN(subject jsonb_path_ops);

-- Index for embedding similarity (if using pgvector extension)
CREATE INDEX idx_resources_embedding_gin ON resources USING GIN(embedding jsonb_path_ops);
```

## Data Models

### Enhanced Resource Model

**PostgreSQL-Specific Columns** (added conditionally):

```python
# Full-text search vector (PostgreSQL only)
if dialect == 'postgresql':
    search_vector: Mapped[str | None] = mapped_column(
        TSVector,
        nullable=True
    )
    
    __table_args__ = (
        Index('idx_resources_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_resources_subject_gin', 'subject', postgresql_using='gin'),
        Index('idx_resources_embedding_gin', 'embedding', postgresql_using='gin'),
    )
```

### Type Mapping Strategy

| SQLite Type | PostgreSQL Type | Notes |
|-------------|-----------------|-------|
| INTEGER | INTEGER | Direct mapping |
| TEXT | TEXT / VARCHAR | Use VARCHAR with length for constrained fields |
| REAL | DOUBLE PRECISION | Direct mapping |
| BLOB | BYTEA | For binary data |
| JSON | JSONB | Enhanced performance with GIN indexes |
| CHAR(36) | UUID | Native UUID type in PostgreSQL |

## Error Handling

### Connection Pool Exhaustion

**Detection**:
```python
@app.middleware("http")
async def monitor_pool_usage(request: Request, call_next):
    pool_status = get_pool_status()
    
    if pool_status['checked_out'] > pool_status['size'] * 0.9:
        logger.warning(f"Connection pool near capacity: {pool_status}")
    
    response = await call_next(request)
    return response
```

**Mitigation**:
- Increase pool size if consistently high usage
- Implement request queuing
- Add circuit breaker for database operations
- Monitor slow queries and optimize

### Transaction Deadlocks (PostgreSQL)

**Retry Logic**:
```python
from sqlalchemy.exc import OperationalError
import time

def retry_on_deadlock(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except OperationalError as e:
            if 'deadlock detected' in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            raise
```

### Migration Failures

**Rollback Strategy**:
1. Keep SQLite database as backup during migration
2. Test migration on staging environment first
3. Implement checkpoint system for resumable migrations
4. Provide rollback script to revert to SQLite

## Testing Strategy

### Database-Agnostic Tests

**Pytest Fixtures**:
```python
@pytest.fixture(scope="session")
def db_engine():
    """Create database engine based on TEST_DATABASE_URL."""
    test_db_url = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    engine = create_engine(test_db_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create database session for tests."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

### Database-Specific Tests

**PostgreSQL Feature Tests**:
```python
@pytest.mark.postgresql
def test_jsonb_containment_query(db_session):
    """Test JSONB containment operator."""
    if get_database_type(db_session.bind) != 'postgresql':
        pytest.skip("PostgreSQL-specific test")
    
    # Test @> operator
    resource = Resource(
        title="Test",
        subject=['Machine Learning', 'AI']
    )
    db_session.add(resource)
    db_session.commit()
    
    results = db_session.query(Resource).filter(
        Resource.subject.op('@>')(cast(['AI'], JSONB))
    ).all()
    
    assert len(results) == 1

@pytest.mark.postgresql
def test_full_text_search_ranking(db_session):
    """Test PostgreSQL full-text search ranking."""
    if get_database_type(db_session.bind) != 'postgresql':
        pytest.skip("PostgreSQL-specific test")
    
    # Test ts_rank function
    # Implementation...
```

### Running Tests Against Different Databases

```bash
# Run tests with SQLite (default)
pytest backend/tests/

# Run tests with PostgreSQL
TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db pytest backend/tests/

# Run only PostgreSQL-specific tests
TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db pytest -m postgresql
```

## Deployment Guide

### Local Development Setup

**1. Start PostgreSQL with Docker Compose**:
```bash
cd backend/docker
docker-compose up -d postgres
```

**2. Configure Environment**:
```bash
# .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/backend
```

**3. Run Migrations**:
```bash
alembic upgrade head
```

**4. Start Application**:
```bash
uvicorn backend.app.main:app --reload
```

### Production Deployment

**1. Provision PostgreSQL Database**:
- Use managed service (AWS RDS, Google Cloud SQL, Azure Database)
- Or self-hosted with replication and backups

**2. Configure Connection String**:
```bash
DATABASE_URL=postgresql://user:password@db-host:5432/production_db
```

**3. Run Migrations**:
```bash
alembic upgrade head
```

**4. Migrate Data** (if migrating from SQLite):
```bash
python backend/scripts/migrate_sqlite_to_postgresql.py \
    --source sqlite:///backend.db \
    --target postgresql://user:password@db-host:5432/production_db \
    --validate
```

**5. Deploy Application**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoring and Maintenance

**Connection Pool Monitoring**:
```python
@app.get("/monitoring/database")
async def database_metrics():
    pool_status = get_pool_status()
    
    return {
        "database_type": get_database_type(sync_engine),
        "pool_size": pool_status['size'],
        "connections_in_use": pool_status['checked_out'],
        "connections_available": pool_status['checked_in'],
        "overflow_connections": pool_status['overflow'],
        "total_connections": pool_status['total']
    }
```

**Slow Query Logging**:
```python
import logging
from sqlalchemy import event

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - context._query_start_time
    
    if total_time > 1.0:  # Log queries slower than 1 second
        logger.warning(f"Slow query ({total_time:.2f}s): {statement}")
```

### Backup Strategy

**PostgreSQL Backup**:
```bash
# Full database backup
pg_dump -h localhost -U postgres -d backend > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -h localhost -U postgres -d backend | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Custom format (supports parallel restore)
pg_dump -h localhost -U postgres -d backend -Fc > backup_$(date +%Y%m%d_%H%M%S).dump
```

**Automated Backup Script**:
```bash
#!/bin/bash
# backup_postgresql.sh

BACKUP_DIR="/var/backups/postgresql"
RETENTION_DAYS=30
DB_NAME="backend"
DB_USER="postgres"
DB_HOST="localhost"

# Create backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.dump"

pg_dump -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -Fc > ${BACKUP_FILE}

# Compress old backups
find ${BACKUP_DIR} -name "*.dump" -mtime +7 -exec gzip {} \;

# Delete old backups
find ${BACKUP_DIR} -name "*.dump.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**Restore Procedure**:
```bash
# Restore from custom format
pg_restore -h localhost -U postgres -d backend -c backup_20250120_120000.dump

# Restore from SQL dump
psql -h localhost -U postgres -d backend < backup_20250120_120000.sql
```

## Performance Considerations

### Connection Pool Sizing

**Formula**:
```
pool_size = (number_of_cpu_cores * 2) + effective_spindle_count
```

For Neo Alexandria:
- 4 CPU cores
- SSD storage (effective_spindle_count = 1)
- Recommended pool_size = (4 * 2) + 1 = 9

Current configuration (20 base + 40 overflow) is conservative and suitable for high-concurrency scenarios.

### Query Optimization

**Use EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE
SELECT * FROM resources
WHERE subject @> '["Machine Learning"]'::jsonb
ORDER BY created_at DESC
LIMIT 25;
```

**Index Usage Verification**:
```sql
-- Check index usage statistics
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Caching Strategy

**Query Result Caching** (Redis):
```python
from functools import wraps
import json
import hashlib

def cache_query(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"query:{func.__name__}:{hashlib.md5(json.dumps(kwargs).encode()).hexdigest()}"
            
            # Check cache
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute query
            result = await func(*args, **kwargs)
            
            # Store in cache
            await redis.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

## Security Considerations

### Connection String Security

**Environment Variables**:
```bash
# Never commit credentials to version control
DATABASE_URL=postgresql://user:password@host:5432/db

# Use secrets management in production
DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id db-credentials --query SecretString --output text)
```

### SQL Injection Prevention

**Always use parameterized queries**:
```python
# SAFE: Parameterized query
db.query(Resource).filter(Resource.title == user_input).all()

# UNSAFE: String concatenation
db.execute(f"SELECT * FROM resources WHERE title = '{user_input}'")
```

### Connection Encryption

**SSL/TLS Configuration**:
```python
# PostgreSQL with SSL
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=require

# Connection args for SSL
connect_args = {
    'sslmode': 'require',
    'sslcert': '/path/to/client-cert.pem',
    'sslkey': '/path/to/client-key.pem',
    'sslrootcert': '/path/to/ca-cert.pem'
}
```

## Rollback Plan

### Reverting to SQLite

**1. Stop Application**:
```bash
docker-compose down
```

**2. Update Environment**:
```bash
# .env file
DATABASE_URL=sqlite:///backend.db
```

**3. Restore SQLite Backup**:
```bash
cp backend.db.backup backend.db
```

**4. Restart Application**:
```bash
docker-compose up -d
```

### Data Export from PostgreSQL to SQLite

**Export Script**: `backend/scripts/migrate_postgresql_to_sqlite.py`

```python
# Reverse migration (PostgreSQL → SQLite)
python backend/scripts/migrate_postgresql_to_sqlite.py \
    --source postgresql://user:password@host:5432/db \
    --target sqlite:///backend.db \
    --validate
```

**Limitations**:
- JSONB data converted to JSON strings
- Full-text search reverts to FTS5
- Some PostgreSQL-specific features may not transfer

## Documentation Updates

### Files to Update

1. **README.md**: Add PostgreSQL setup instructions
2. **DEVELOPER_GUIDE.md**: Document database configuration options
3. **API_DOCUMENTATION.md**: Note any API behavior changes
4. **CHANGELOG.md**: Document migration in release notes
5. **.env.example**: Add PostgreSQL connection string examples

### Migration Guide for Users

**Document**: `backend/docs/POSTGRESQL_MIGRATION_GUIDE.md`

Contents:
- Prerequisites and requirements
- Step-by-step migration procedure
- Validation and testing steps
- Troubleshooting common issues
- Rollback procedures
- Performance tuning recommendations
