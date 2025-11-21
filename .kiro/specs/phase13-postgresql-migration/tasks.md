# Implementation Plan

- [x] 1. Enhance database configuration module for PostgreSQL support





  - Update `backend/app/database/base.py` to detect database type from connection URL
  - Add PostgreSQL-specific connection pool parameters (pool_size=20, max_overflow=40, pool_recycle=3600, pool_pre_ping=True)
  - Add SQLite-specific connection parameters for backward compatibility
  - Implement `get_database_type()` function to detect current database dialect

  - Implement `create_database_engine()` factory function with database-specific parameters
  - Add PostgreSQL statement_timeout and timezone configuration in connect_args
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1_


- [x] 2. Create PostgreSQL compatibility migration



  - Create new Alembic migration file `backend/alembic/versions/20250120_postgresql_compatibility.py`
  - Implement database type detection in migration upgrade() function
  - Add PostgreSQL extension installation (pg_trgm, uuid-ossp) for PostgreSQL databases
  - Add conditional JSONB conversion for subject, relation, embedding columns (PostgreSQL only)
  - Create GIN indexes on JSONB columns for efficient containment queries
  - Preserve JSON type for SQLite compatibility in else branch

  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 8.2_

- [x] 3. Implement full-text search abstraction layer




  - Create `FullTextSearchStrategy` abstract base class in `backend/app/services/search_service.py`
  - Implement `SQLiteFTS5Strategy` class maintaining existing FTS5 logic
  - Implement `PostgreSQLFullTextStrategy` class using tsvector and tsquery
  - Add `search_vector` TSVector column to Resource model (PostgreSQL only)
  - Create PostgreSQL trigger function `resources_search_vector_update()` to auto-update search_vector
  - Create GIN index on search_vector column for fast full-text search

  - Update SearchService to select strategy based on database type
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
-

- [x] 4. Create data migration script


  - Create `backend/scripts/migrate_sqlite_to_postgresql.py` script
  - Implement `DatabaseMigrator` class with source and target engine initialization
  - Implement `validate_schemas()` method to verify table existence in both databases
  - Implement `migrate_tables()` method with correct dependency order for foreign keys
  - Implement `migrate_table()` method with batch processing (1000 records per batch)
  - Add progress reporting during migration with row counts





  - Implement `validate_data()` method to compare row counts between source and target
  - Implement `generate_report()` method showing migration statistics and errors
  - Add command-line argument parsing for source URL, target URL, and validation flag
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_


- [x] 5. Optimize connection pool configuration and monitoring




  - Update async_engine creation in `backend/app/database/base.py` with PostgreSQL pool parameters
  - Update sync_engine creation with matching pool configuration
  - Enhance `get_pool_status()` function to return detailed PostgreSQL pool metrics
  - Create `/monitoring/database` endpoint in `backend/app/routers/monitoring.py`
  - Implement slow query logging with SQLAlchemy event listeners (threshold: 1 second)
  - Add connection pool usage middleware to warn when pool near capacity (>90%)

  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 10.1, 10.2, 10.3, 10.4, 10.5_
-

- [x] 6. Update Docker Compose configuration



  - Verify PostgreSQL 15 service exists in `backend/docker/docker-compose.yml`
  - Verify persistent volume configuration for postgres_data
  - Verify PostgreSQL port 5432 exposure for development access
  - Verify health check configuration for PostgreSQL container
  - Verify Neo Alexandria service depends_on PostgreSQL container

  - Verify environment variables for PostgreSQL credentials are set
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 7. Implement environment-specific configuration




  - Add TEST_DATABASE_URL environment variable support in `backend/app/config/settings.py`
  - Update test fixtures in `backend/tests/conftest.py` to use TEST_DATABASE_URL when set
  - Create `.env.development` example file with SQLite configuration
  - Create `.env.staging` example file with PostgreSQL configuration
  - Create `.env.production` example file with PostgreSQL configuration
  - Update `backend/README.md` with documentation of all database environment variables
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [x] 8. Create database indexes for PostgreSQL optimization



  - Add B-tree indexes on all foreign key columns in migration
  - Add GIN indexes on JSONB columns (subject, relation, embedding, sparse_embedding)
  - Add composite indexes for common query patterns (classification_code + quality_score, created_at + read_status)
  - Add indexes on timestamp columns (created_at, updated_at, ingestion_completed_at)
  - Add index usage documentation in migration file comments
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 9. Implement transaction isolation and concurrency handling







  - Configure READ COMMITTED isolation level for PostgreSQL in engine creation
  - Implement retry decorator for handling PostgreSQL serialization errors
  - Add SELECT FOR UPDATE locking for resource update operations
  - Configure statement_timeout of 30 seconds in PostgreSQL connect_args
  - Maintain default SQLite transaction behavior for SQLite databases
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

-

- [x] 10. Create backup and recovery documentation



  - Create `backend/docs/POSTGRESQL_BACKUP_GUIDE.md` documentation file
  - Document pg_dump backup procedures (full, compressed, custom format)
  - Document point-in-time recovery configuration steps
  - Create `backend/scripts/backup_postgresql.sh` automated backup script
  - Document restore procedures for full and partial recovery
  - Add backup frequency and retention policy recommendations
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_


- [x] 11. Update testing infrastructure for multi-database support




  - Update pytest fixtures in `backend/tests/conftest.py` to support TEST_DATABASE_URL
  - Create database-agnostic test fixtures that work with both SQLite and PostgreSQL
  - Create `@pytest.mark.postgresql` marker for PostgreSQL-specific tests
  - Add PostgreSQL JSONB containment query tests
  - Add PostgreSQL full-text search ranking tests
  - Update test documentation in `backend/tests/README.md` with multi-database testing instructions
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 12. Create rollback and contingency procedures





  - Create `backend/scripts/migrate_postgresql_to_sqlite.py` reverse migration script
  - Document rollback procedure in `backend/docs/POSTGRESQL_MIGRATION_GUIDE.md`
  - Document known limitations when reverting from PostgreSQL to SQLite
  - Add rollback testing steps to migration guide
  - Update application to maintain SQLite compatibility for one release cycle
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

-

- [ ] 13. Create comprehensive migration guide


  - Create `backend/docs/POSTGRESQL_MIGRATION_GUIDE.md` documentation file
  - Document prerequisites and system requirements
  - Write step-by-step migration procedure with validation checkpoints
  - Add troubleshooting section for common migration issues
  - Document performance tuning recommendations for PostgreSQL
  - Add example commands for local development and production deployment
  - _Requirements: All requirements_

- [x] 14. Update project documentation





  - Update `backend/README.md` with PostgreSQL setup instructions
  - Update `backend/docs/DEVELOPER_GUIDE.md` with database configuration options
  - Update `backend/docs/CHANGELOG.md` with Phase 13 migration notes
  - Update `.env.example` with PostgreSQL connection string examples
  - Add database selection guidance (SQLite vs PostgreSQL) for different use cases
  - _Requirements: All requirements_
