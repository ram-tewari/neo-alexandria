# Requirements Document

## Introduction

This document specifies the requirements for migrating Neo Alexandria 2.0 from SQLite to PostgreSQL as the primary production database. The migration addresses scalability, concurrency, and performance limitations inherent in SQLite while maintaining backward compatibility for development environments. The system currently uses SQLite for both development and production, with connection pooling configured for 60 concurrent connections (20 base + 40 overflow). PostgreSQL will provide superior concurrent write performance, advanced indexing capabilities, and production-grade reliability while preserving the existing data model and API contracts.

## Glossary

- **Neo Alexandria System**: The knowledge management application backend built with FastAPI and SQLAlchemy
- **SQLite Database**: The current file-based relational database system used for development and production
- **PostgreSQL Database**: The target production-grade relational database system with advanced concurrency support
- **Alembic Migration**: Database schema version control and migration tool integrated with SQLAlchemy
- **Connection Pool**: A cache of database connections maintained for reuse to improve performance
- **FTS5**: SQLite's full-text search extension (Full-Text Search version 5)
- **pg_trgm**: PostgreSQL extension for trigram-based text similarity search
- **Database URL**: Connection string specifying database type, credentials, and location
- **Async Engine**: SQLAlchemy's asynchronous database connection engine using asyncio
- **Sync Engine**: SQLAlchemy's synchronous database connection engine for background tasks
- **Docker Compose**: Multi-container orchestration tool for local development and deployment
- **Environment Variable**: Configuration value passed to the application at runtime
- **Migration Script**: Alembic-generated Python file defining database schema changes
- **Backward Compatibility**: Ability to continue supporting SQLite for development environments

## Requirements

### Requirement 1: Database Configuration Management

**User Story:** As a developer, I want flexible database configuration so that I can use SQLite for local development and PostgreSQL for production without code changes.

#### Acceptance Criteria

1. WHEN the Neo Alexandria System starts, THE Neo Alexandria System SHALL read the DATABASE_URL environment variable to determine the database type
2. WHERE the DATABASE_URL starts with "sqlite://", THE Neo Alexandria System SHALL configure SQLite-specific connection parameters
3. WHERE the DATABASE_URL starts with "postgresql://", THE Neo Alexandria System SHALL configure PostgreSQL-specific connection parameters
4. THE Neo Alexandria System SHALL support both synchronous and asynchronous database connections for PostgreSQL
5. THE Neo Alexandria System SHALL maintain connection pool configuration with 20 base connections and 40 overflow connections for PostgreSQL

### Requirement 2: Schema Migration and Compatibility

**User Story:** As a database administrator, I want automated schema migration from SQLite to PostgreSQL so that I can migrate production data without manual SQL scripting.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL provide an Alembic Migration that creates all tables in PostgreSQL with equivalent schema to SQLite
2. WHEN migrating from SQLite to PostgreSQL, THE Neo Alexandria System SHALL preserve all data types with appropriate PostgreSQL equivalents
3. THE Neo Alexandria System SHALL convert SQLite INTEGER PRIMARY KEY to PostgreSQL SERIAL or UUID types as appropriate
4. THE Neo Alexandria System SHALL convert SQLite TEXT columns to PostgreSQL VARCHAR or TEXT with appropriate length constraints
5. THE Neo Alexandria System SHALL convert SQLite JSON columns to PostgreSQL JSONB for improved query performance
6. THE Neo Alexandria System SHALL preserve all foreign key constraints and cascade behaviors in PostgreSQL

### Requirement 3: Full-Text Search Migration

**User Story:** As a user, I want full-text search to work identically in PostgreSQL so that I can find resources using the same search queries after migration.

#### Acceptance Criteria

1. WHERE the database is PostgreSQL, THE Neo Alexandria System SHALL use PostgreSQL's built-in full-text search instead of FTS5
2. THE Neo Alexandria System SHALL create GIN indexes on text search columns for PostgreSQL full-text search performance
3. THE Neo Alexandria System SHALL install and configure the pg_trgm extension for similarity search in PostgreSQL
4. THE Neo Alexandria System SHALL maintain search result ranking compatibility between SQLite FTS5 and PostgreSQL full-text search
5. WHERE the database is SQLite, THE Neo Alexandria System SHALL continue using FTS5 virtual tables for full-text search

### Requirement 4: Data Migration Tooling

**User Story:** As a system administrator, I want a data migration script so that I can transfer existing SQLite data to PostgreSQL with validation.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL provide a migration script that exports all data from SQLite to PostgreSQL
2. WHEN the migration script runs, THE Neo Alexandria System SHALL validate that all tables exist in both databases before data transfer
3. THE Neo Alexandria System SHALL transfer data in batches of 1000 records to prevent memory exhaustion
4. THE Neo Alexandria System SHALL preserve all UUID primary keys during data migration
5. THE Neo Alexandria System SHALL validate row counts match between source and destination after migration
6. IF any data transfer fails, THEN THE Neo Alexandria System SHALL log the error and continue with remaining tables
7. THE Neo Alexandria System SHALL generate a migration report showing record counts and any errors for each table

### Requirement 5: Connection Pool Optimization

**User Story:** As a performance engineer, I want optimized connection pooling for PostgreSQL so that the system handles concurrent requests efficiently.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL configure PostgreSQL connection pool with 20 base connections
2. THE Neo Alexandria System SHALL configure PostgreSQL connection pool with 40 overflow connections for burst traffic
3. THE Neo Alexandria System SHALL enable pool_pre_ping to validate connections before use
4. THE Neo Alexandria System SHALL set pool_recycle to 3600 seconds to prevent stale connections
5. THE Neo Alexandria System SHALL provide a monitoring endpoint that reports connection pool statistics
6. WHERE the database is SQLite, THE Neo Alexandria System SHALL use minimal connection pooling appropriate for file-based databases

### Requirement 6: Docker Compose Integration

**User Story:** As a developer, I want Docker Compose configuration for PostgreSQL so that I can run the complete stack locally with one command.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL provide a Docker Compose configuration that includes PostgreSQL 15 or higher
2. THE Neo Alexandria System SHALL configure PostgreSQL container with persistent volume for data storage
3. THE Neo Alexandria System SHALL expose PostgreSQL on port 5432 for external access during development
4. THE Neo Alexandria System SHALL configure health checks for the PostgreSQL container
5. THE Neo Alexandria System SHALL ensure the Neo Alexandria System container depends on PostgreSQL container startup
6. THE Neo Alexandria System SHALL provide environment variables for PostgreSQL credentials in docker-compose.yml

### Requirement 7: Environment-Specific Configuration

**User Story:** As a DevOps engineer, I want environment-specific database configuration so that I can use SQLite for testing and PostgreSQL for staging and production.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL support a TEST_DATABASE_URL environment variable for test environments
2. WHERE TEST_DATABASE_URL is set, THE Neo Alexandria System SHALL use that database for all test executions
3. THE Neo Alexandria System SHALL default to in-memory SQLite for tests when TEST_DATABASE_URL is not set
4. THE Neo Alexandria System SHALL provide example .env files for development, staging, and production environments
5. THE Neo Alexandria System SHALL document all database-related environment variables in README.md

### Requirement 8: Index Migration and Optimization

**User Story:** As a database administrator, I want all indexes migrated to PostgreSQL so that query performance matches or exceeds SQLite performance.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL create B-tree indexes on all foreign key columns in PostgreSQL
2. THE Neo Alexandria System SHALL create GIN indexes on JSONB columns for efficient JSON queries
3. THE Neo Alexandria System SHALL create composite indexes for common query patterns identified in the codebase
4. THE Neo Alexandria System SHALL create indexes on timestamp columns used for sorting and filtering
5. THE Neo Alexandria System SHALL document index strategy and rationale in migration comments

### Requirement 9: Transaction Isolation and Concurrency

**User Story:** As a backend developer, I want proper transaction isolation in PostgreSQL so that concurrent operations do not cause data corruption.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL use READ COMMITTED isolation level for PostgreSQL transactions
2. THE Neo Alexandria System SHALL handle PostgreSQL serialization errors with automatic retry logic
3. THE Neo Alexandria System SHALL use SELECT FOR UPDATE for row-level locking when updating resources
4. THE Neo Alexandria System SHALL configure statement timeout of 30 seconds for PostgreSQL queries
5. WHERE the database is SQLite, THE Neo Alexandria System SHALL continue using default SQLite transaction behavior

### Requirement 10: Monitoring and Observability

**User Story:** As a site reliability engineer, I want database metrics exposed so that I can monitor PostgreSQL health and performance.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL expose connection pool metrics via the /monitoring/database endpoint
2. THE Neo Alexandria System SHALL log slow queries exceeding 1 second to application logs
3. THE Neo Alexandria System SHALL track and report database query counts per endpoint
4. THE Neo Alexandria System SHALL expose PostgreSQL-specific metrics including cache hit ratio and transaction rate
5. WHERE the database is SQLite, THE Neo Alexandria System SHALL expose basic connection statistics

### Requirement 11: Backup and Recovery Strategy

**User Story:** As a database administrator, I want documented backup procedures for PostgreSQL so that I can recover from data loss.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL provide documentation for PostgreSQL backup using pg_dump
2. THE Neo Alexandria System SHALL provide documentation for point-in-time recovery configuration
3. THE Neo Alexandria System SHALL provide a backup script that creates timestamped database dumps
4. THE Neo Alexandria System SHALL document restore procedures for both full and partial data recovery
5. THE Neo Alexandria System SHALL recommend backup frequency and retention policies in documentation

### Requirement 12: Testing Infrastructure Updates

**User Story:** As a QA engineer, I want tests to run against both SQLite and PostgreSQL so that I can verify database compatibility.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL support running the test suite against PostgreSQL via TEST_DATABASE_URL
2. THE Neo Alexandria System SHALL provide pytest fixtures that work with both SQLite and PostgreSQL
3. THE Neo Alexandria System SHALL include database-specific tests for PostgreSQL features like JSONB queries
4. THE Neo Alexandria System SHALL validate that all existing tests pass with PostgreSQL backend
5. THE Neo Alexandria System SHALL document how to run tests against different database backends

### Requirement 13: Rollback and Contingency Planning

**User Story:** As a project manager, I want a rollback plan so that we can revert to SQLite if PostgreSQL migration encounters critical issues.

#### Acceptance Criteria

1. THE Neo Alexandria System SHALL maintain SQLite compatibility for at least one release after PostgreSQL migration
2. THE Neo Alexandria System SHALL provide documentation for reverting from PostgreSQL to SQLite
3. THE Neo Alexandria System SHALL provide a reverse migration script that exports PostgreSQL data to SQLite
4. THE Neo Alexandria System SHALL document known limitations when reverting from PostgreSQL to SQLite
5. THE Neo Alexandria System SHALL test rollback procedures in a staging environment before production migration
