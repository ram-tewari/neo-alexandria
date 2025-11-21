# SQLite Compatibility Maintenance Guide

## Overview

This document outlines the strategy for maintaining SQLite compatibility in Neo Alexandria 2.0 for one release cycle after the PostgreSQL migration. This ensures a smooth transition and provides a reliable rollback path if issues arise.

## Compatibility Period

**Duration:** One release cycle (approximately 3-6 months)

**Start Date:** PostgreSQL migration completion  
**End Date:** After stable PostgreSQL operation confirmed

## Maintained Compatibility Features

### 1. Database Detection and Configuration

The application automatically detects the database type from the connection URL and applies appropriate configuration:

**File:** `backend/app/database/base.py`

```python
def get_database_type(database_url: str | None = None) -> Literal["sqlite", "postgresql"]:
    """Detect database type from connection URL."""
    url = database_url or settings.DATABASE_URL
    
    if url.startswith("sqlite"):
        return "sqlite"
    elif url.startswith("postgresql"):
        return "postgresql"
    else:
        raise ValueError(f"Unsupported database type in URL: {url}")
```

**Usage:**
```bash
# SQLite (development)
DATABASE_URL=sqlite:///backend.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:pass@localhost:5432/neo_alexandria
```

### 2. Connection Pool Configuration

Database-specific connection pool parameters are automatically applied:

**SQLite Configuration:**
- Pool size: 5 connections
- Max overflow: 10 connections
- No pre-ping (not needed for file-based DB)
- Thread safety enabled (`check_same_thread=False`)
- 30-second lock timeout

**PostgreSQL Configuration:**
- Pool size: 20 connections
- Max overflow: 40 connections
- Pre-ping enabled (health checks)
- Connection recycling: 3600 seconds
- Statement timeout: 30 seconds
- READ COMMITTED isolation level

### 3. Full-Text Search Abstraction

The search service uses a strategy pattern to support both SQLite FTS5 and PostgreSQL tsvector:

**File:** `backend/app/services/search_service.py`

**Strategy Classes:**
- `SQLiteFTS5Strategy`: Uses SQLite FTS5 virtual tables
- `PostgreSQLFullTextStrategy`: Uses PostgreSQL tsvector and tsquery

**Automatic Selection:**
```python
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
```

### 4. Transaction Isolation and Concurrency

Database-specific transaction handling:

**SQLite:**
- Database-level locking (default behavior)
- No row-level locking
- No retry logic needed

**PostgreSQL:**
- Row-level locking with `SELECT FOR UPDATE`
- Automatic retry on serialization errors
- READ COMMITTED isolation level

**Implementation:**
```python
async def with_row_lock(session: AsyncSession, model_class, record_id):
    """
    Acquire row-level lock (PostgreSQL only).
    For SQLite, returns record without locking.
    """
    db_type = get_database_type()
    stmt = select(model_class).where(model_class.id == record_id)
    
    if db_type == "postgresql":
        stmt = stmt.with_for_update()
    
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

### 5. Schema Compatibility

Alembic migrations support both databases:

**File:** `backend/alembic/versions/20250120_postgresql_compatibility.py`

```python
def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    if dialect == 'postgresql':
        upgrade_postgresql()
    else:
        upgrade_sqlite()

def upgrade_postgresql():
    # PostgreSQL-specific upgrades
    # - Install extensions (pg_trgm, uuid-ossp)
    # - Convert JSON to JSONB
    # - Create tsvector columns
    # - Create GIN indexes
    pass

def upgrade_sqlite():
    # SQLite-specific upgrades (if any)
    # - Maintain JSON columns
    # - Use FTS5 virtual tables
    pass
```

### 6. Testing Infrastructure

Tests can run against both databases:

**File:** `backend/tests/conftest.py`

```python
@pytest.fixture(scope="session")
def db_engine():
    """Create database engine based on TEST_DATABASE_URL."""
    test_db_url = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
    engine = create_engine(test_db_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

**Usage:**
```bash
# Run tests with SQLite (default)
pytest backend/tests/

# Run tests with PostgreSQL
TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_db pytest backend/tests/

# Run PostgreSQL-specific tests only
TEST_DATABASE_URL=postgresql://... pytest -m postgresql backend/tests/
```

## Code Guidelines for Compatibility

### DO: Write Database-Agnostic Code

✅ **Good Examples:**

```python
# Use SQLAlchemy ORM queries
resources = db.query(Resource).filter(Resource.title.like('%AI%')).all()

# Use abstraction layers
search_service = SearchService(db)
results = search_service.search("machine learning")

# Use database detection for conditional logic
db_type = get_database_type()
if db_type == "postgresql":
    # PostgreSQL-specific optimization
    pass
else:
    # SQLite fallback
    pass
```

### DON'T: Write Database-Specific Code

❌ **Bad Examples:**

```python
# Don't use PostgreSQL-specific operators without fallback
resources = db.query(Resource).filter(
    Resource.subject.op('@>')(cast(['AI'], JSONB))
).all()

# Don't use raw SQL without database detection
db.execute("SELECT * FROM resources WHERE search_vector @@ to_tsquery('AI')")

# Don't assume PostgreSQL features are available
stmt = select(Resource).with_for_update()  # Fails on SQLite
```

### Best Practices

1. **Use Abstraction Layers:**
   - Search: Use `SearchService` instead of direct FTS queries
   - Locking: Use `with_row_lock()` instead of raw `FOR UPDATE`
   - Configuration: Use `get_database_type()` for conditional logic

2. **Test Against Both Databases:**
   ```bash
   # Local development with SQLite
   pytest backend/tests/
   
   # CI/CD with PostgreSQL
   TEST_DATABASE_URL=postgresql://... pytest backend/tests/
   ```

3. **Document Database-Specific Features:**
   - Add comments explaining why database detection is used
   - Document fallback behavior for SQLite
   - Note performance differences between databases

4. **Avoid Database-Specific Extensions:**
   - Don't rely on PostgreSQL extensions in core logic
   - Provide SQLite alternatives for PostgreSQL features
   - Use feature detection instead of database detection when possible

## Migration Path to PostgreSQL-Only

After the compatibility period ends and PostgreSQL is stable:

### Phase 1: Deprecation Warnings (Release N+1)

1. Add deprecation warnings for SQLite usage:
   ```python
   if get_database_type() == "sqlite":
       logger.warning(
           "SQLite support is deprecated and will be removed in the next release. "
           "Please migrate to PostgreSQL."
       )
   ```

2. Update documentation:
   - Mark SQLite as deprecated in README
   - Emphasize PostgreSQL as the recommended database
   - Provide migration guide

### Phase 2: Remove SQLite Support (Release N+2)

1. **Remove SQLite-specific code:**
   - Remove `SQLiteFTS5Strategy` class
   - Remove SQLite connection parameters
   - Remove SQLite-specific tests
   - Remove FTS5 virtual table migrations

2. **Simplify database configuration:**
   ```python
   # Before (supports both)
   def get_database_type(database_url: str) -> Literal["sqlite", "postgresql"]:
       if url.startswith("sqlite"):
           return "sqlite"
       elif url.startswith("postgresql"):
           return "postgresql"
   
   # After (PostgreSQL only)
   def validate_database_url(database_url: str) -> None:
       if not url.startswith("postgresql"):
           raise ValueError("Only PostgreSQL is supported")
   ```

3. **Remove abstraction layers:**
   - Replace `FullTextSearchStrategy` with direct PostgreSQL implementation
   - Remove database type detection from search service
   - Simplify connection pool configuration

4. **Update tests:**
   - Remove SQLite test fixtures
   - Remove `TEST_DATABASE_URL` environment variable support
   - Update CI/CD to use PostgreSQL only

5. **Update documentation:**
   - Remove SQLite references from README
   - Remove SQLite setup instructions
   - Update developer guide to PostgreSQL only
   - Archive SQLite compatibility documentation

### Phase 3: PostgreSQL Optimization (Release N+3)

1. **Leverage PostgreSQL-specific features:**
   - Use JSONB operators directly (no abstraction)
   - Use PostgreSQL-specific indexes (GiST, BRIN)
   - Use advanced PostgreSQL features (CTEs, window functions)
   - Use PostgreSQL extensions (pg_trgm, pgvector)

2. **Optimize for PostgreSQL:**
   - Remove SQLite compatibility overhead
   - Optimize queries for PostgreSQL query planner
   - Use PostgreSQL-specific data types
   - Implement PostgreSQL-specific caching strategies

## Monitoring Compatibility

### Metrics to Track

1. **Database Usage:**
   - Number of SQLite deployments
   - Number of PostgreSQL deployments
   - Migration completion rate

2. **Performance Comparison:**
   - Query performance (SQLite vs PostgreSQL)
   - Connection pool usage
   - Error rates by database type

3. **Support Burden:**
   - SQLite-related issues reported
   - PostgreSQL-related issues reported
   - Migration support requests

### Decision Criteria for Ending Compatibility

End SQLite compatibility when:
- [ ] All production deployments migrated to PostgreSQL
- [ ] PostgreSQL stable for 2+ months in production
- [ ] No critical SQLite-specific issues reported
- [ ] Migration documentation complete and tested
- [ ] Rollback procedures validated
- [ ] Team consensus on ending support

## Rollback Considerations

During the compatibility period, maintain the ability to rollback:

1. **Keep SQLite backups:**
   - Backup before migration
   - Periodic backups during compatibility period
   - Test backup restoration regularly

2. **Test rollback procedure:**
   - Document rollback steps
   - Test rollback in staging
   - Validate data integrity after rollback

3. **Monitor for rollback triggers:**
   - Data corruption in PostgreSQL
   - Unacceptable performance degradation
   - Critical bugs specific to PostgreSQL
   - Migration issues affecting users

## Support and Documentation

### User Communication

1. **Migration Announcement:**
   - Announce PostgreSQL migration in release notes
   - Provide migration guide and timeline
   - Offer migration support

2. **Deprecation Notice:**
   - Warn users about SQLite deprecation
   - Provide migration deadline
   - Offer assistance with migration

3. **End of Support:**
   - Final warning before removing SQLite support
   - Provide migration resources
   - Document breaking changes

### Internal Documentation

1. **Developer Guide:**
   - Database compatibility guidelines
   - Testing procedures for both databases
   - Migration timeline and milestones

2. **Architecture Documentation:**
   - Database abstraction layer design
   - Strategy pattern implementation
   - Future PostgreSQL-only architecture

3. **Runbooks:**
   - Database switching procedures
   - Rollback procedures
   - Troubleshooting guides

## Conclusion

Maintaining SQLite compatibility for one release cycle provides:
- **Safety:** Reliable rollback path if issues arise
- **Flexibility:** Users can migrate at their own pace
- **Confidence:** Proven stability before removing fallback
- **Support:** Time to address migration issues

After the compatibility period, removing SQLite support will:
- **Simplify:** Reduce code complexity and maintenance burden
- **Optimize:** Enable PostgreSQL-specific optimizations
- **Focus:** Concentrate efforts on single database platform
- **Improve:** Better performance and features with PostgreSQL

**Timeline:**
- **Release N:** PostgreSQL migration, maintain SQLite compatibility
- **Release N+1:** Deprecate SQLite, encourage migration
- **Release N+2:** Remove SQLite support, PostgreSQL only
- **Release N+3:** Optimize for PostgreSQL, leverage advanced features
