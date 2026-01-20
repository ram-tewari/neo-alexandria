# Requirements Document: Phase 17 - Production Hardening

## Introduction

Phase 17 focuses on hardening Neo Alexandria 2.0 for production deployment by implementing critical infrastructure improvements: PostgreSQL database support, API key authentication, granular task tracking for frontend integration, and Celery worker optimization. This phase transforms the system from a development prototype into a production-ready application.

## Glossary

- **System**: Neo Alexandria 2.0 backend application
- **API_Gateway**: FastAPI application entry point that handles HTTP requests
- **Auth_Service**: Authentication and authorization service using API keys
- **Status_Tracker**: Service for tracking long-running background task progress
- **Database_Service**: PostgreSQL database connection and session management
- **Worker**: Celery background task worker process
- **Shared_Kernel**: Cross-cutting concerns layer (database, cache, embeddings, AI)
- **Module**: Self-contained vertical slice (Resources, Search, etc.)
- **Docker_Infrastructure**: Containerized backing services (PostgreSQL, Redis)
- **Configuration_Service**: Application settings and environment management
- **Processing_Stage**: Distinct phase of resource processing (INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING)
- **Resource_Progress**: Real-time status of a resource through processing stages

## Requirements

### Requirement 1: Dockerized Development Infrastructure

**User Story:** As a developer, I want containerized backing services, so that I can run PostgreSQL and Redis without manual installation.

#### Acceptance Criteria

1. WHEN a developer runs `docker-compose -f docker-compose.dev.yml up`, THE System SHALL start PostgreSQL 15 and Redis 7 containers
2. THE PostgreSQL_Container SHALL expose port 5432 and persist data to a named volume
3. THE Redis_Container SHALL expose port 6379 for cache and message broker operations
4. THE Docker_Compose_File SHALL use environment variables for database credentials
5. THE Docker_Infrastructure SHALL NOT include the application service (app runs locally for debugging)
6. WHEN containers are stopped and restarted, THE System SHALL preserve all database data via volumes

### Requirement 2: PostgreSQL Database Support

**User Story:** As a system administrator, I want PostgreSQL support, so that I can deploy the application with a production-grade database.

#### Acceptance Criteria

1. THE Configuration_Service SHALL support both SQLite and PostgreSQL connection strings
2. WHEN POSTGRES_SERVER is configured, THE System SHALL construct an async PostgreSQL URI using asyncpg driver
3. THE Database_Service SHALL use the format `postgresql+asyncpg://user:pass@host:5432/db` for PostgreSQL connections
4. THE System SHALL maintain backward compatibility with SQLite for development and testing
5. WHEN the database connection fails, THE System SHALL log detailed error messages and fail gracefully
6. THE Configuration_Service SHALL validate database connection parameters at startup

### Requirement 3: Configuration Management Enhancement

**User Story:** As a developer, I want centralized configuration management, so that I can easily switch between development and production settings.

#### Acceptance Criteria

1. THE Configuration_Service SHALL use pydantic-settings for type-safe configuration
2. THE Configuration_Service SHALL provide fields for POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
3. THE Configuration_Service SHALL include JWT_SECRET_KEY field using SecretStr for token signing
4. THE Configuration_Service SHALL include JWT_ALGORITHM field (default: HS256)
5. THE Configuration_Service SHALL include ACCESS_TOKEN_EXPIRE_MINUTES field (default: 30)
6. THE Configuration_Service SHALL include REFRESH_TOKEN_EXPIRE_DAYS field (default: 7)
7. THE Configuration_Service SHALL include OAUTH2_PROVIDERS configuration for supported OAuth2 providers
8. THE Configuration_Service SHALL provide a TEST_MODE boolean flag
9. THE Configuration_Service SHALL implement a get_database_url() method that constructs the appropriate connection string
10. WHEN environment variables are missing, THE Configuration_Service SHALL use sensible defaults or raise validation errors
11. THE Configuration_Service SHALL support .env file loading for local development

### Requirement 4: JWT Token Authentication with OAuth2

**User Story:** As a system administrator, I want JWT-based authentication with OAuth2 support, so that I can provide secure, scalable access control with token expiration and refresh capabilities.

#### Acceptance Criteria

1. THE Auth_Service SHALL implement JWT token generation using the configured JWT_SECRET_KEY and algorithm
2. THE Auth_Service SHALL generate access tokens with configurable expiration (ACCESS_TOKEN_EXPIRE_MINUTES)
3. THE Auth_Service SHALL generate refresh tokens with configurable expiration (REFRESH_TOKEN_EXPIRE_DAYS)
4. THE Auth_Service SHALL implement a FastAPI OAuth2PasswordBearer dependency for token validation
5. WHEN a request includes a valid Bearer token, THE Auth_Service SHALL extract and validate the token claims
6. WHEN a request has an invalid or expired token, THE Auth_Service SHALL return HTTP 401 with error detail
7. THE Auth_Service SHALL implement token refresh endpoint that accepts refresh tokens and issues new access tokens
8. THE Auth_Service SHALL support OAuth2 authorization code flow for third-party providers (Google, GitHub)
9. THE Auth_Service SHALL store OAuth2 provider configurations (client_id, client_secret, redirect_uri)
10. THE Auth_Service SHALL implement OAuth2 callback handler to exchange authorization codes for tokens
11. THE API_Gateway SHALL apply authentication globally to all endpoints
12. THE API_Gateway SHALL exclude /docs, /openapi.json, /auth/*, and /monitoring/health from authentication
13. THE Auth_Service SHALL log authentication failures and token refresh events for security monitoring
14. WHEN TEST_MODE is enabled, THE Auth_Service SHALL optionally bypass authentication for testing
15. THE Auth_Service SHALL validate token signatures and expiration on every authenticated request

### Requirement 5: Rate Limiting per Token

**User Story:** As a system administrator, I want rate limiting per authentication token, so that I can prevent API abuse and ensure fair resource usage.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL track request counts per token in Redis with sliding window algorithm
2. THE Rate_Limiter SHALL implement configurable rate limits (requests per minute, requests per hour, requests per day)
3. WHEN a token exceeds rate limits, THE Rate_Limiter SHALL return HTTP 429 (Too Many Requests) with retry-after header
4. THE Rate_Limiter SHALL provide different rate limit tiers (free, premium, admin)
5. THE Rate_Limiter SHALL store rate limit tier information in JWT token claims
6. THE Rate_Limiter SHALL implement a FastAPI dependency for rate limit checking
7. THE Rate_Limiter SHALL apply rate limiting after authentication but before endpoint execution
8. THE Rate_Limiter SHALL exclude /monitoring/health from rate limiting
9. THE Rate_Limiter SHALL log rate limit violations for monitoring and abuse detection
10. THE Rate_Limiter SHALL provide endpoint to check current rate limit status for a token
11. WHEN Redis is unavailable, THE Rate_Limiter SHALL log warnings and allow requests (fail open)
12. THE Rate_Limiter SHALL reset rate limit counters based on configured time windows

**User Story:** As a frontend developer, I want real-time progress tracking for resource processing, so that I can display accurate status to users.

#### Acceptance Criteria

1. THE Status_Tracker SHALL define ProcessingStage enum with values: INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING
2. THE Status_Tracker SHALL define StageStatus enum with values: PENDING, PROCESSING, COMPLETED, FAILED
3. THE Status_Tracker SHALL provide a ResourceProgress model containing resource_id, overall_status, and stage dictionary
4. THE Status_Tracker SHALL implement set_progress(resource_id, stage, status) to update stage status in Redis
5. THE Status_Tracker SHALL implement get_progress(resource_id) to retrieve current progress from Redis
6. WHEN a processing stage completes, THE Module SHALL call set_progress with COMPLETED status
7. WHEN a processing stage fails, THE Module SHALL call set_progress with FAILED status and error details
8. THE Status_Tracker SHALL calculate overall_status based on all stage statuses
9. WHEN Redis is unavailable, THE Status_Tracker SHALL log warnings and return default progress states
10. THE Status_Tracker SHALL support TTL (time-to-live) for progress records to prevent memory bloat

### Requirement 6: Celery Worker Cold Start Optimization

**User Story:** As a system administrator, I want optimized Celery worker startup, so that background tasks execute faster without repeated model loading.

#### Acceptance Criteria

1. THE Worker SHALL use @worker_process_init signal to initialize services at startup
2. WHEN a worker process starts, THE Worker SHALL pre-load ML models into memory
3. THE Worker SHALL initialize EmbeddingService during the worker_process_init phase
4. WHEN tasks execute, THE Worker SHALL reuse pre-loaded models instead of loading per-task
5. THE Worker SHALL log initialization progress and memory usage
6. WHEN model loading fails during initialization, THE Worker SHALL log errors and retry with exponential backoff
7. THE Worker SHALL support graceful shutdown to release model resources

### Requirement 7: Module Isolation Compliance

**User Story:** As a system architect, I want zero circular dependencies, so that the modular architecture remains maintainable.

#### Acceptance Criteria

1. THE Auth_Service SHALL reside in app/shared/ as a cross-cutting concern
2. THE Status_Tracker SHALL reside in app/shared/ as a cross-cutting concern
3. THE Configuration_Service SHALL reside in app/config/ with no module dependencies
4. WHEN modules need authentication, THE Module SHALL import from app.shared.security
5. WHEN modules need status tracking, THE Module SHALL import from app.shared.status_tracker
6. THE System SHALL pass module isolation checks with zero violations
7. THE Shared_Kernel SHALL have no dependencies on domain modules

### Requirement 8: Error Handling and Resilience

**User Story:** As a system administrator, I want robust error handling, so that the system degrades gracefully when services are unavailable.

#### Acceptance Criteria

1. WHEN PostgreSQL is unavailable, THE System SHALL log connection errors and fail startup with clear messages
2. WHEN Redis is unavailable, THE Status_Tracker SHALL log warnings and continue operation with degraded functionality
3. WHEN authentication fails, THE Auth_Service SHALL return structured error responses with appropriate HTTP status codes
4. WHEN configuration is invalid, THE Configuration_Service SHALL raise validation errors at startup
5. THE System SHALL implement health checks that verify database and cache connectivity
6. WHEN a Celery task fails, THE Worker SHALL log detailed error information and update status tracking
7. THE System SHALL implement retry logic for transient failures (network timeouts, temporary unavailability)

### Requirement 9: Testing and Validation

**User Story:** As a developer, I want comprehensive tests for new infrastructure, so that I can verify production readiness.

#### Acceptance Criteria

1. THE Test_Suite SHALL include unit tests for Configuration_Service with various environment configurations
2. THE Test_Suite SHALL include unit tests for Auth_Service with valid and invalid API keys
3. THE Test_Suite SHALL include unit tests for Status_Tracker with Redis mocking
4. THE Test_Suite SHALL include integration tests for PostgreSQL connectivity
5. THE Test_Suite SHALL include integration tests for authenticated API endpoints
6. THE Test_Suite SHALL verify that TEST_MODE bypasses authentication correctly
7. THE Test_Suite SHALL verify that Docker infrastructure starts successfully
8. THE Test_Suite SHALL verify that Celery workers initialize models correctly

### Requirement 10: Documentation and Migration

**User Story:** As a developer, I want clear documentation, so that I can understand how to configure and deploy the new infrastructure.

#### Acceptance Criteria

1. THE Documentation SHALL include a setup guide for Docker infrastructure
2. THE Documentation SHALL include environment variable reference for all new configuration options
3. THE Documentation SHALL include API authentication guide with example requests
4. THE Documentation SHALL include PostgreSQL migration guide from SQLite
5. THE Documentation SHALL include status tracking API reference for frontend integration
6. THE Documentation SHALL include Celery worker configuration guide
7. THE Documentation SHALL include troubleshooting guide for common issues

## Non-Functional Requirements

### Performance

- Database connection pool: 5-20 connections for PostgreSQL
- Redis operations: < 10ms for status tracking operations
- Authentication overhead: < 5ms per request
- Worker initialization: < 30 seconds for model loading

### Security

- API keys stored as SecretStr (not logged or exposed)
- Database credentials loaded from environment variables only
- Authentication failures logged for security monitoring
- No sensitive data in error messages

### Scalability

- Support for multiple Celery workers with shared Redis state
- PostgreSQL connection pooling for concurrent requests
- Status tracking supports 10,000+ concurrent resource processing operations

### Reliability

- Graceful degradation when Redis is unavailable
- Clear error messages for configuration issues
- Health checks for all critical services
- Automatic retry for transient failures

## Success Metrics

- Zero circular dependency violations
- All tests passing with PostgreSQL and SQLite
- Authentication working on all protected endpoints
- Status tracking operational with < 10ms latency
- Celery workers starting in < 30 seconds
- Docker infrastructure starting in < 10 seconds
- 100% test coverage for new infrastructure code
