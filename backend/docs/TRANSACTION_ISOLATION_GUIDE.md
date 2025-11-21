# Transaction Isolation and Concurrency Handling Guide

This guide explains how to use the transaction isolation and concurrency handling features in Neo Alexandria 2.0.

## Overview

Neo Alexandria 2.0 provides PostgreSQL-specific transaction isolation features while maintaining SQLite compatibility:

- **READ COMMITTED isolation level** for PostgreSQL
- **Automatic retry logic** for serialization errors
- **Row-level locking** with SELECT FOR UPDATE
- **Statement timeout** configuration (30 seconds)
- **Backward compatibility** with SQLite

## Features

### 1. READ COMMITTED Isolation Level

PostgreSQL connections are automatically configured with READ COMMITTED isolation level, which provides a good balance between consistency and performance.

```python
# Configured automatically in engine creation
# No code changes needed - just use the database normally
```

### 2. Retry Decorator for Serialization Errors

Use the `@retry_on_serialization_error` decorator to automatically retry operations that fail due to PostgreSQL serialization errors or deadlocks.

```python
from backend.app.database.base import retry_on_serialization_error

@retry_on_serialization_error(max_retries=3, initial_backoff=0.1)
async def update_resource_safely(db: AsyncSession, resource_id: str, data: dict):
    """
    Update a resource with automatic retry on serialization errors.
    
    This operation will be retried up to 3 times if a deadlock or
    serialization error occurs.
    """
    resource = await db.get(Resource, resource_id)
    if resource:
        resource.title = data.get("title", resource.title)
        resource.description = data.get("description", resource.description)
        await db.commit()
    return resource
```

**Parameters:**
- `max_retries`: Maximum number of retry attempts (default: 3)
- `initial_backoff`: Initial delay in seconds before first retry (default: 0.1)
- `backoff_multiplier`: Multiplier for exponential backoff (default: 2.0)

**Behavior:**
- Only retries on PostgreSQL serialization errors and deadlocks
- Uses exponential backoff between retries
- Other errors are raised immediately without retry
- Works with both async and sync functions

### 3. Row-Level Locking

Use `with_row_lock()` to acquire a row-level lock before updating a record. This prevents race conditions in concurrent update scenarios.

#### Async Version

```python
from backend.app.database.base import with_row_lock
from backend.app.database.models import Resource

async def increment_view_count(db: AsyncSession, resource_id: str):
    """
    Safely increment a resource's view count using row-level locking.
    """
    # Lock the resource row to prevent concurrent updates
    resource = await with_row_lock(db, Resource, resource_id)
    
    if resource:
        resource.view_count += 1
        await db.commit()
    
    return resource
```

#### Synchronous Version

```python
from backend.app.database.base import with_row_lock_sync
from backend.app.database.models import Resource

def increment_view_count_sync(db: Session, resource_id: str):
    """
    Synchronous version for background tasks.
    """
    resource = with_row_lock_sync(db, Resource, resource_id)
    
    if resource:
        resource.view_count += 1
        db.commit()
    
    return resource
```

**Lock Modes:**
- `"update"` (default): Full row lock (FOR UPDATE)
- `"no_key_update"`: Lock without blocking key updates (FOR NO KEY UPDATE)

**Behavior:**
- PostgreSQL: Uses SELECT FOR UPDATE to lock the row
- SQLite: Returns the record without locking (SQLite uses database-level locking)
- Returns `None` if record not found

### 4. Combining Retry and Locking

For maximum safety in concurrent scenarios, combine both features:

```python
from backend.app.database.base import retry_on_serialization_error, with_row_lock

@retry_on_serialization_error(max_retries=3)
async def update_resource_with_lock(db: AsyncSession, resource_id: str, data: dict):
    """
    Update a resource with both row-level locking and retry logic.
    
    This provides maximum protection against concurrent update conflicts.
    """
    # Lock the row to prevent concurrent modifications
    resource = await with_row_lock(db, Resource, resource_id)
    
    if resource:
        # Update the resource
        resource.title = data.get("title", resource.title)
        resource.quality_score = data.get("quality_score", resource.quality_score)
        
        # Commit the transaction
        await db.commit()
        await db.refresh(resource)
    
    return resource
```

## Configuration

### Statement Timeout

PostgreSQL queries are automatically configured with a 30-second timeout:

```python
# Configured in backend/app/database/base.py
"connect_args": {
    "statement_timeout": "30000",  # 30 seconds in milliseconds
    "server_settings": {
        "timezone": "UTC"
    }
}
```

### Connection Pool Settings

PostgreSQL connection pool is configured for high concurrency:

```python
{
    "pool_size": 20,              # Base connections
    "max_overflow": 40,           # Additional connections (total: 60)
    "pool_recycle": 3600,         # Recycle connections after 1 hour
    "pool_pre_ping": True,        # Health check before using connection
    "isolation_level": "READ COMMITTED"  # Transaction isolation level
}
```

## Monitoring

### Check Pool Status

```python
from backend.app.database.base import get_pool_status

pool_stats = get_pool_status()
print(f"Database: {pool_stats['database_type']}")
print(f"Pool usage: {pool_stats['pool_usage_percent']}%")
print(f"Connections in use: {pool_stats['checked_out']}")
print(f"Connections available: {pool_stats['connections_available']}")

# PostgreSQL-specific metrics
if pool_stats['database_type'] == 'postgresql':
    print(f"Isolation level: {pool_stats['isolation_level']}")
    print(f"Statement timeout: {pool_stats['statement_timeout_ms']}ms")
```

### Slow Query Logging

Queries exceeding 1 second are automatically logged:

```python
# Configured automatically via SQLAlchemy event listeners
# Check application logs for slow query warnings
```

## Best Practices

### 1. Use Retry Decorator for Write Operations

```python
# Good: Retry on serialization errors
@retry_on_serialization_error(max_retries=3)
async def update_data(db: AsyncSession, ...):
    # Update logic here
    pass

# Avoid: No retry protection
async def update_data(db: AsyncSession, ...):
    # Update logic here - may fail on concurrent updates
    pass
```

### 2. Use Row Locking for Critical Updates

```python
# Good: Lock before updating
resource = await with_row_lock(db, Resource, resource_id)
resource.view_count += 1

# Avoid: No locking - race condition possible
resource = await db.get(Resource, resource_id)
resource.view_count += 1  # May lose updates from concurrent requests
```

### 3. Keep Transactions Short

```python
# Good: Short transaction
async def update_resource(db: AsyncSession, resource_id: str, title: str):
    resource = await with_row_lock(db, Resource, resource_id)
    resource.title = title
    await db.commit()

# Avoid: Long transaction holding locks
async def update_resource(db: AsyncSession, resource_id: str, title: str):
    resource = await with_row_lock(db, Resource, resource_id)
    # Don't do expensive operations while holding locks
    await expensive_api_call()  # Bad!
    resource.title = title
    await db.commit()
```

### 4. Handle Lock Timeouts Gracefully

```python
from sqlalchemy.exc import OperationalError

try:
    resource = await with_row_lock(db, Resource, resource_id)
    # Update logic
except OperationalError as e:
    if "timeout" in str(e).lower():
        # Handle timeout gracefully
        logger.warning(f"Lock timeout for resource {resource_id}")
        raise HTTPException(status_code=503, detail="Resource temporarily unavailable")
    raise
```

## Database Compatibility

### PostgreSQL

All features are fully supported:
- ✅ READ COMMITTED isolation level
- ✅ Retry on serialization errors
- ✅ Row-level locking with SELECT FOR UPDATE
- ✅ Statement timeout
- ✅ Connection pool monitoring

### SQLite

Limited support for development:
- ✅ Retry decorator (works but rarely needed)
- ⚠️ Row-level locking (no-op, returns record without locking)
- ⚠️ Isolation level (uses SQLite defaults)
- ✅ Connection pool monitoring (basic stats)

## Troubleshooting

### Serialization Errors

If you see frequent serialization errors:

1. **Check for long transactions**: Keep transactions short
2. **Review query patterns**: Reduce contention on hot rows
3. **Increase retry attempts**: Adjust `max_retries` parameter
4. **Add delays**: Increase `initial_backoff` for heavily contended resources

### Deadlocks

If deadlocks occur:

1. **Consistent lock ordering**: Always lock resources in the same order
2. **Use row-level locking**: Reduce lock scope with `with_row_lock()`
3. **Keep transactions short**: Release locks quickly
4. **Review concurrent operations**: Identify conflicting update patterns

### Connection Pool Exhaustion

If pool reaches capacity:

1. **Check slow queries**: Review slow query logs
2. **Monitor pool usage**: Use `get_pool_status()` endpoint
3. **Optimize queries**: Add indexes, reduce query complexity
4. **Increase pool size**: Adjust `pool_size` and `max_overflow` if needed

## Examples

See `backend/tests/test_transaction_isolation.py` for comprehensive examples of all features.

## Related Documentation

- [PostgreSQL Migration Guide](POSTGRESQL_MIGRATION_GUIDE.md)
- [Database Configuration](../app/database/base.py)
- [Developer Guide](DEVELOPER_GUIDE.md)
