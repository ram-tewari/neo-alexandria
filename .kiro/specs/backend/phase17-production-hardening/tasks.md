# Implementation Plan: Phase 17 - Production Hardening

## Overview

This implementation plan breaks down Phase 17 into discrete, incremental tasks focusing on JWT authentication with OAuth2, rate limiting, PostgreSQL support, status tracking, and Celery optimization. Each task builds on previous work and includes testing to validate functionality.

## Tasks

- [x] 1. Set up Docker infrastructure for backing services
  - Create `docker-compose.dev.yml` with PostgreSQL 15 and Redis 7
  - Configure environment variables for database credentials
  - Add health checks for both services
  - Test container startup and data persistence
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Enhance configuration service with PostgreSQL and JWT settings
  - [x] 2.1 Add PostgreSQL configuration fields to Settings class
    - Add POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
    - Implement get_database_url() method for dynamic URL construction
    - Test with both SQLite and PostgreSQL URLs
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 2.2 Add JWT authentication configuration fields
    - Add JWT_SECRET_KEY (SecretStr), JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS
    - Add OAuth2 provider fields (Google and GitHub client IDs, secrets, redirect URIs)
    - Add rate limiting configuration (RATE_LIMIT_FREE_TIER, RATE_LIMIT_PREMIUM_TIER, RATE_LIMIT_ADMIN_TIER)
    - Add TEST_MODE boolean flag
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [x] 2.3 Write unit tests for configuration service


    - Test get_database_url() with SQLite URLs (unchanged)
    - Test get_database_url() with PostgreSQL configuration
    - Test validation errors for invalid configurations
    - Test default values for optional fields
    - Test SecretStr masking for sensitive fields
    - _Requirements: 2.6, 3.6_

- [x] 3. Implement JWT authentication service
  - [x] 3.1 Create password hashing utilities
    - Implement password hashing using passlib with bcrypt
    - Implement password verification function
    - Test password hashing and verification
    - _Requirements: 4.1_
  
  - [x] 3.2 Implement JWT token creation and validation
    - Create create_access_token() function with expiration
    - Create create_refresh_token() function with longer expiration
    - Implement token signature validation
    - Add token type checking (access vs refresh)
    - _Requirements: 4.2, 4.3, 4.9_
  
  - [x] 3.3 Implement token revocation system
    - Create is_token_revoked() function using Redis
    - Create revoke_token() function to add tokens to revocation list
    - Set appropriate TTL for revoked tokens
    - _Requirements: 4.10_
  
  - [x] 3.4 Create get_current_user() FastAPI dependency
    - Implement OAuth2PasswordBearer scheme
    - Extract and validate JWT from Authorization header
    - Check token revocation status
    - Return TokenData with user_id, username, scopes, tier
    - Handle TEST_MODE bypass
    - _Requirements: 4.6, 4.13, 4.14, 4.15_
  
  - [x] 3.5 Write unit tests for JWT authentication
    - Test token creation with valid data
    - Test token validation with valid tokens
    - Test token validation with expired tokens
    - Test token validation with invalid signatures
    - Test token revocation
    - Test TEST_MODE bypass
    - _Requirements: 4.2, 4.3, 4.6, 4.9, 4.10, 4.14_

- [x] 4. Implement OAuth2 provider integration
  - [x] 4.1 Create OAuth2Provider base class
    - Define interface for get_authorization_url(), exchange_code_for_token(), get_user_info()
    - _Requirements: 4.8_
  
  - [x] 4.2 Implement GoogleOAuth2Provider
    - Implement Google OAuth2 authorization URL generation
    - Implement code-to-token exchange
    - Implement user info retrieval
    - _Requirements: 4.8, 4.9, 4.10_
  
  - [x] 4.3 Implement GitHubOAuth2Provider
    - Implement GitHub OAuth2 authorization URL generation
    - Implement code-to-token exchange
    - Implement user info retrieval
    - _Requirements: 4.8, 4.9, 4.10_
  
  - [x] 4.4 Write unit tests for OAuth2 providers
    - Test authorization URL generation
    - Test code exchange (with mocked HTTP responses)
    - Test user info retrieval (with mocked HTTP responses)
    - _Requirements: 4.8, 4.9, 4.10_

- [x] 5. Create authentication router and endpoints
  - [x] 5.1 Create auth module structure
    - Create backend/app/modules/auth/ directory
    - Create __init__.py, router.py, service.py, schema.py
    - _Requirements: 4.1_
  
  - [x] 5.2 Implement login endpoint (OAuth2 password flow)
    - Create POST /auth/login endpoint
    - Accept OAuth2PasswordRequestForm
    - Authenticate user credentials
    - Return JWT access and refresh tokens
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 5.3 Implement token refresh endpoint
    - Create POST /auth/refresh endpoint
    - Validate refresh token
    - Issue new access token
    - _Requirements: 4.4, 4.8_
  
  - [x] 5.4 Implement logout endpoint
    - Create POST /auth/logout endpoint
    - Revoke current access token
    - _Requirements: 4.10_
  
  - [x] 5.5 Implement OAuth2 Google endpoints
    - Create GET /auth/google endpoint (initiate flow)
    - Create GET /auth/google/callback endpoint (handle callback)
    - Create or link user account
    - Return JWT tokens
    - _Requirements: 4.8, 4.9, 4.10_
  
  - [x] 5.6 Implement OAuth2 GitHub endpoints
    - Create GET /auth/github endpoint (initiate flow)
    - Create GET /auth/github/callback endpoint (handle callback)
    - Create or link user account
    - Return JWT tokens
    - _Requirements: 4.8, 4.9, 4.10_
  
  - [x] 5.7 Implement user info and rate limit status endpoints
    - Create GET /auth/me endpoint (current user info)
    - Create GET /auth/rate-limit endpoint (rate limit status)
    - _Requirements: 4.1_
  
  - [x] 5.8 Write integration tests for auth endpoints
    - Test login with valid credentials
    - Test login with invalid credentials
    - Test token refresh
    - Test logout
    - Test OAuth2 flows (with mocked providers)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.8, 4.10_

- [x] 6. Implement rate limiting service
  - [x] 6.1 Create RateLimiter class with sliding window algorithm
    - Implement check_rate_limit() method
    - Use Redis for request counting with TTL
    - Calculate remaining requests and reset time
    - Generate rate limit headers
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [x] 6.2 Implement rate limit tiers
    - Support free, premium, and admin tiers
    - Read tier from JWT token claims
    - Apply appropriate limits per tier
    - _Requirements: 5.5, 5.6_
  
  - [x] 6.3 Create rate_limit_dependency for FastAPI
    - Implement FastAPI dependency function
    - Check rate limits before endpoint execution
    - Raise HTTP 429 when limit exceeded
    - Add rate limit headers to responses
    - Handle Redis unavailability (fail open)
    - _Requirements: 5.3, 5.7, 5.8, 5.11_
  
  - [x] 6.4 Write unit tests for rate limiting
    - Test rate limit checking with various tiers
    - Test sliding window algorithm
    - Test HTTP 429 responses
    - Test rate limit headers
    - Test graceful degradation when Redis unavailable
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.8, 5.11_

- [x] 7. Integrate authentication and rate limiting globally
  - [x] 7.1 Update main.py to apply authentication globally
    - Add get_current_user dependency to FastAPI app
    - Exclude /auth/*, /docs, /openapi.json, /monitoring/health from authentication
    - _Requirements: 4.11, 4.12_
  
  - [x] 7.2 Add rate limiting middleware
    - Apply rate_limit_dependency after authentication
    - Exclude /monitoring/health from rate limiting
    - Add rate limit headers to all responses
    - _Requirements: 5.7, 5.8_
  
  - [x] 7.3 Update module routers to use authentication
    - Verify all protected endpoints require authentication
    - Test authentication on sample endpoints
    - _Requirements: 4.11_
  
  - [x] 7.4 Write integration tests for global authentication and rate limiting
    - Test protected endpoints require valid JWT
    - Test excluded endpoints are accessible without JWT
    - Test rate limiting applies to authenticated requests
    - Test rate limit headers in responses
    - _Requirements: 4.11, 4.12, 5.7_

- [x] 8. Create user management system
  - [x] 8.1 Create User database model
    - Add users table with id, username, email, hashed_password, tier, is_active
    - Add oauth_accounts table for linking OAuth providers
    - Create Alembic migration
    - _Requirements: 4.1_
  
  - [x] 8.2 Implement user service functions
    - Create authenticate_user() function
    - Create get_user_by_id() function
    - Create get_or_create_oauth_user() function
    - _Requirements: 4.1, 4.8_
  
  - [x] 8.3 Write unit tests for user service
    - Test user authentication
    - Test user retrieval
    - Test OAuth user creation/linking
    - _Requirements: 4.1, 4.8_

- [-] 9. Implement status tracking service
  - [x] 9.1 Create status tracking schemas
    - Define ProcessingStage enum (INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING)
    - Define StageStatus enum (PENDING, PROCESSING, COMPLETED, FAILED)
    - Define ResourceProgress Pydantic model
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 9.2 Implement StatusTracker service
    - Create StatusTracker class using CacheService
    - Implement set_progress() method with Redis storage
    - Implement get_progress() method with Redis retrieval
    - Implement _calculate_overall_status() method
    - Set TTL for progress records (24 hours)
    - Handle Redis unavailability gracefully
    - _Requirements: 6.4, 6.5, 6.8, 6.9, 6.10_
  
  - [x] 9.3 Write unit tests for status tracking
    - Test set_progress() stores data in Redis
    - Test get_progress() retrieves data from Redis
    - Test round-trip (set then get)
    - Test overall status calculation with various stage combinations
    - Test TTL is set on Redis keys
    - Test graceful degradation when Redis unavailable
    - _Requirements: 6.4, 6.5, 6.8, 6.9, 6.10_

- [x] 10. Optimize Celery worker initialization
  - [x] 10.1 Update worker.py with worker_process_init signal
    - Register @worker_process_init.connect handler
    - Pre-load EmbeddingService in signal handler
    - Log initialization progress and memory usage
    - Handle model loading failures with retry logic
    - _Requirements: 7.1, 7.2, 7.3, 7.5, 7.6_
  
  - [x] 10.2 Create get_embedding_service() helper function
    - Return pre-loaded embedding service instance
    - Raise error if service not initialized
    - _Requirements: 7.4_
  
  - [x] 10.3 Write tests for worker initialization
    - Test worker_process_init signal handler registration
    - Test embedding service pre-loading
    - Test model reuse across multiple tasks
    - Test error handling for model loading failures
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6_

- [x] 11. Update database connection for PostgreSQL
  - [x] 11.1 Update database initialization to use get_database_url()
    - Modify shared/database.py to use settings.get_database_url()
    - Test connection with SQLite (backward compatibility)
    - Test connection with PostgreSQL
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 11.2 Handle database connection errors gracefully
    - Log detailed error messages for connection failures
    - Fail application startup with clear messages
    - _Requirements: 8.1_
  
  - [x] 11.3 Write integration tests for database connections
    - Test SQLite connection
    - Test PostgreSQL connection
    - Test connection error handling
    - _Requirements: 2.1, 2.4, 8.1_

- [x] 12. Checkpoint - Core infrastructure complete
  - Verify Docker containers start successfully
  - Verify PostgreSQL and Redis connectivity
  - Verify JWT authentication works end-to-end
  - Verify rate limiting applies correctly
  - Verify status tracking stores and retrieves data
  - Verify Celery workers pre-load models
  - Run all tests and ensure they pass
  - Ask user if any issues or questions arise

- [x] 13. Add comprehensive error handling
  - [x] 13.1 Implement authentication error responses
    - Return structured HTTP 401 for invalid/expired tokens
    - Return structured HTTP 403 for insufficient permissions
    - Log authentication failures
    - _Requirements: 4.7, 4.13, 8.3_
  
  - [x] 13.2 Implement rate limiting error responses
    - Return HTTP 429 with Retry-After header
    - Include rate limit headers in error response
    - Log rate limit violations
    - _Requirements: 5.3, 5.9_
  
  - [x] 13.3 Implement configuration validation errors
    - Raise ValidationError for invalid configuration at startup
    - Include field name and expected type in error messages
    - _Requirements: 8.4_
  
  - [x] 13.4 Write tests for error handling
    - Test authentication error responses
    - Test rate limiting error responses
    - Test configuration validation errors
    - _Requirements: 4.7, 5.3, 8.3, 8.4_

- [x] 14. Create health check endpoints
  - [x] 14.1 Update monitoring/health endpoint
    - Add database connectivity check
    - Add Redis connectivity check
    - Add Celery worker status check
    - Return detailed health status
    - _Requirements: 8.5_
  
  - [x] 14.2 Write tests for health checks
    - Test health check with all services available
    - Test health check with database unavailable
    - Test health check with Redis unavailable
    - _Requirements: 8.5_

- [ ] 15. Write property-based tests
  - [ ] 15.1 Property test: Database URL construction
    - Generate random valid PostgreSQL configurations
    - Verify constructed URL matches expected format
    - Verify URL is parseable by SQLAlchemy
    - Run 100 iterations
    - **Property 1: Database URL Construction Correctness**
    - **Validates: Requirements 2.2, 2.3**
  
  - [ ] 15.2 Property test: JWT token round-trip
    - Generate random user data
    - Create access token
    - Validate and decode token
    - Verify decoded data matches original
    - Run 100 iterations
    - **Property 4: Authentication Success**
    - **Validates: Requirements 4.2, 4.6**
  
  - [ ] 15.3 Property test: Authentication failure
    - Generate random invalid tokens
    - Verify authentication fails with 401
    - Verify error response structure
    - Run 100 iterations
    - **Property 5: Authentication Failure**
    - **Validates: Requirements 4.3, 4.7**
  
  - [ ] 15.4 Property test: Status tracking round-trip
    - Generate random resource IDs, stages, and statuses
    - Call set_progress then get_progress
    - Verify retrieved data matches set data
    - Run 100 iterations
    - **Property 8: Status Tracking Round-Trip**
    - **Validates: Requirements 6.4, 6.5**
  
  - [ ] 15.5 Property test: Overall status calculation
    - Generate random combinations of stage statuses
    - Calculate overall status
    - Verify calculation follows rules (FAILED > PROCESSING > COMPLETED > PENDING)
    - Run 100 iterations
    - **Property 9: Overall Status Calculation**
    - **Validates: Requirements 6.8**

- [x] 16. Update documentation
  - [x] 16.1 Update Docker setup guide (backend/DOCKER_SETUP_GUIDE.md)
    - Add docker-compose.dev.yml usage instructions
    - Document environment variable configuration for PostgreSQL and Redis
    - Document data persistence and volumes
    - Add troubleshooting section for common Docker issues
    - _Requirements: 10.1_
  
  - [x] 16.2 Update API overview documentation (backend/docs/api/overview.md)
    - Add authentication section with JWT Bearer token format
    - Document rate limiting headers (X-RateLimit-*)
    - Add authentication error responses (401, 403, 429)
    - Document excluded endpoints (public access)
    - _Requirements: 10.3, 10.4_
  
  - [x] 16.3 Create authentication API documentation (backend/docs/api/auth.md)
    - Document all /auth/* endpoints (login, refresh, logout, OAuth2)
    - Document JWT token structure and claims
    - Document OAuth2 flows (Google, GitHub)
    - Provide curl examples with Bearer tokens
    - Document rate limiting per tier
    - _Requirements: 10.3, 10.4_
  
  - [x] 16.4 Update architecture overview (backend/docs/architecture/overview.md)
    - Add authentication middleware to system architecture diagram
    - Add rate limiting middleware to request flow
    - Document auth module in vertical slices section
    - Update shared kernel section with security and rate_limiter
    - _Requirements: 10.3_
  
  - [x] 16.5 Update modules documentation (backend/docs/architecture/modules.md)
    - Add auth module to module list (14th module)
    - Document auth module structure and responsibilities
    - Update module count from 13 to 14
    - Add authentication middleware to cross-cutting concerns
    - _Requirements: 10.3_
  
  - [x] 16.6 Update database documentation (backend/docs/architecture/database.md)
    - Add users table schema
    - Add oauth_accounts table schema
    - Document authentication-related fields
    - Add Phase 17 migration reference
    - _Requirements: 10.4_
  
  - [x] 16.7 Update PostgreSQL migration guide (backend/docs/POSTGRESQL_MIGRATION_GUIDE.md)
    - Add Phase 17 authentication tables migration steps
    - Document new environment variables for JWT and OAuth2
    - Update connection string examples
    - Add rate limiting Redis configuration
    - _Requirements: 10.4_
  
  - [x] 16.8 Create authentication module README (backend/app/modules/auth/README.md)
    - Document module purpose and responsibilities
    - Document endpoints and their usage
    - Document JWT token lifecycle
    - Document OAuth2 integration
    - Provide code examples
    - _Requirements: 10.3, 10.5_
  
  - [x] 16.9 Update main README (backend/README.md)
    - Add JWT authentication to features list
    - Add rate limiting to features list
    - Update quick start with authentication setup
    - Update environment variables section
    - Add authentication examples
    - Update module count from 13 to 14
    - _Requirements: 10.2, 10.3_
  
  - [x] 16.10 Update CHANGELOG (backend/docs/CHANGELOG.md)
    - Add Phase 17 - Production Hardening section
    - Document JWT authentication with OAuth2 support
    - Document rate limiting with tiered access
    - Document global authentication middleware
    - Document PostgreSQL support enhancements
    - List all new endpoints and features
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [x] 16.11 Update .env.example (backend/.env.example)
    - Add JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_EXPIRE_DAYS
    - Add OAuth2 provider configurations (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, etc.)
    - Add rate limiting tier configurations (RATE_LIMIT_FREE_TIER, RATE_LIMIT_PREMIUM_TIER)
    - Add TEST_MODE flag
    - Document each variable with inline comments
    - _Requirements: 10.2_
  
  - [x] 16.12 Update documentation index (backend/docs/index.md)
    - Add link to auth API documentation
    - Update module list to include auth module
    - Add authentication guide section
    - Update architecture links
    - _Requirements: 10.3_

- [x] 17. Final checkpoint and validation
  - Run full test suite (unit, property, integration)
  - Verify zero circular dependency violations
  - Test complete authentication flow (login, refresh, logout)
  - Test OAuth2 flows with Google and GitHub
  - Test rate limiting with different tiers
  - Test status tracking end-to-end
  - Test PostgreSQL and SQLite compatibility
  - Test Celery worker optimization
  - Verify all performance targets met (< 5ms auth, < 10ms status tracking, < 30s worker init)
  - Review documentation completeness
  - Ask user for final review and approval

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- All authentication and rate limiting code resides in shared kernel (app/shared/)
- Zero circular dependencies maintained throughout implementation
