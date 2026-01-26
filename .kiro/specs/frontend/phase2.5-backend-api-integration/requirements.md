# Requirements Document: Phase 2.5 - Backend API Integration

## Introduction

Phase 2.5 connects the frontend components built in Phase 1 (Workbench & Navigation) and Phase 2 (Living Code Editor) to the live backend API at `https://pharos.onrender.com`. This phase replaces all mock data with real backend calls, adds proper error handling, and ensures the frontend can operate with production data.

## Glossary

- **Frontend**: React/TypeScript application built with Vite
- **Backend**: FastAPI Python application deployed at `https://pharos.onrender.com`
- **API_Client**: Axios-based HTTP client for backend communication
- **Zustand_Store**: State management library used for client-side state
- **MSW**: Mock Service Worker for testing API interactions
- **Phase_1_Components**: WorkbenchLayout, CommandPalette, RepositorySwitcher, Theme system
- **Phase_2_Components**: MonacoEditorWrapper, SemanticChunkOverlay, QualityBadgeGutter, AnnotationGutter, ReferenceGutter, HoverCardProvider
- **TanStack_Query**: Data fetching and caching library (React Query)

## Requirements

### Requirement 1: API Client Configuration

**User Story:** As a developer, I want a properly configured API client, so that all frontend components can communicate with the backend reliably.

#### Acceptance Criteria

1. THE API_Client SHALL use the base URL from environment variables
2. THE API_Client SHALL include authentication tokens in all requests
3. THE API_Client SHALL handle request timeouts with a 30-second default
4. THE API_Client SHALL include request/response interceptors for error handling
5. THE API_Client SHALL retry failed requests up to 3 times with exponential backoff
6. THE API_Client SHALL log all API errors to the console in development mode

### Requirement 2: Phase 1 API Integration

**User Story:** As a user, I want the workbench navigation to display real data from the backend, so that I can see my actual repositories and system status.

#### Acceptance Criteria

1. WHEN the application loads, THE Frontend SHALL fetch current user info from `/api/auth/me`
2. WHEN the repository switcher opens, THE Frontend SHALL fetch the resource list from `/resources`
3. WHEN the command palette opens, THE Frontend SHALL display health status from `/api/monitoring/health`
4. WHEN rate limit information is needed, THE Frontend SHALL fetch from `/api/auth/rate-limit`
5. THE Frontend SHALL display loading states while fetching Phase 1 data
6. IF any Phase 1 API call fails, THEN THE Frontend SHALL display an error message and retry

### Requirement 3: Phase 2 Editor API Integration

**User Story:** As a user, I want the code editor to load real file content and metadata, so that I can view and annotate actual code files.

#### Acceptance Criteria

1. WHEN a resource is selected, THE Frontend SHALL fetch content from `/resources/{resource_id}`
2. WHEN semantic chunks are needed, THE Frontend SHALL fetch from `/resources/{resource_id}/chunks`
3. WHEN a specific chunk is selected, THE Frontend SHALL fetch details from `/chunks/{chunk_id}`
4. WHEN processing status is needed, THE Frontend SHALL poll `/resources/{resource_id}/status`
5. THE Frontend SHALL display loading states while fetching editor data
6. IF any editor API call fails, THEN THE Frontend SHALL display an error and allow retry

### Requirement 4: Annotation API Integration

**User Story:** As a user, I want to create, read, update, and delete annotations, so that I can persist my notes and highlights to the backend.

#### Acceptance Criteria

1. WHEN a user creates an annotation, THE Frontend SHALL POST to `/annotations` with annotation data
2. WHEN annotations are loaded, THE Frontend SHALL GET from `/annotations` filtered by resource
3. WHEN a user updates an annotation, THE Frontend SHALL PUT to `/annotations/{annotation_id}`
4. WHEN a user deletes an annotation, THE Frontend SHALL DELETE `/annotations/{annotation_id}`
5. WHEN searching annotations by text, THE Frontend SHALL GET from `/annotations/search/fulltext`
6. WHEN searching annotations semantically, THE Frontend SHALL GET from `/annotations/search/semantic`
7. WHEN searching by tags, THE Frontend SHALL GET from `/annotations/search/tags`
8. WHEN exporting annotations, THE Frontend SHALL GET from `/annotations/export/markdown` or `/annotations/export/json`
9. THE Frontend SHALL optimistically update the UI before API confirmation
10. IF annotation operations fail, THEN THE Frontend SHALL revert optimistic updates and show errors

### Requirement 5: Quality Data API Integration

**User Story:** As a user, I want to see real quality scores and analytics, so that I can assess code quality accurately.

#### Acceptance Criteria

1. WHEN quality badges are displayed, THE Frontend SHALL fetch quality data from resource metadata
2. WHEN quality recalculation is triggered, THE Frontend SHALL POST to `/quality/recalculate`
3. WHEN viewing quality outliers, THE Frontend SHALL GET from `/quality/outliers`
4. WHEN viewing quality degradation, THE Frontend SHALL GET from `/quality/degradation`
5. WHEN viewing quality distribution, THE Frontend SHALL GET from `/quality/distribution`
6. WHEN viewing quality trends, THE Frontend SHALL GET from `/quality/trends`
7. WHEN viewing dimension scores, THE Frontend SHALL GET from `/quality/dimensions`
8. WHEN viewing review queue, THE Frontend SHALL GET from `/quality/review-queue`
9. THE Frontend SHALL cache quality data for 15 minutes
10. IF quality API calls fail, THEN THE Frontend SHALL display cached data with a warning

### Requirement 6: Graph Hover API Integration

**User Story:** As a user, I want to see hover information for code symbols, so that I can understand relationships and context.

#### Acceptance Criteria

1. WHEN hovering over a code symbol, THE Frontend SHALL POST to `/api/graph/hover` with symbol information
2. THE Frontend SHALL debounce hover requests by 300ms to avoid excessive API calls
3. THE Frontend SHALL display loading state while fetching hover data
4. THE Frontend SHALL cache hover responses for 30 minutes
5. IF hover API calls fail, THEN THE Frontend SHALL display a minimal fallback hover card

### Requirement 7: TypeScript Type Definitions

**User Story:** As a developer, I want TypeScript types matching backend schemas, so that I have type safety and autocomplete.

#### Acceptance Criteria

1. THE Frontend SHALL define TypeScript interfaces for all API request payloads
2. THE Frontend SHALL define TypeScript interfaces for all API response schemas
3. THE Frontend SHALL use discriminated unions for API error types
4. THE Frontend SHALL export all types from a central types file
5. THE Frontend SHALL validate API responses match expected types in development mode

### Requirement 8: Error Handling and Loading States

**User Story:** As a user, I want clear feedback when API calls fail or are in progress, so that I understand the application state.

#### Acceptance Criteria

1. WHEN any API call is in progress, THE Frontend SHALL display a loading indicator
2. WHEN an API call fails with a 401 error, THE Frontend SHALL redirect to login
3. WHEN an API call fails with a 403 error, THE Frontend SHALL display "Access Denied"
4. WHEN an API call fails with a 404 error, THE Frontend SHALL display "Not Found"
5. WHEN an API call fails with a 429 error, THE Frontend SHALL display rate limit information
6. WHEN an API call fails with a 500 error, THE Frontend SHALL display "Server Error" and retry
7. WHEN an API call fails with a network error, THE Frontend SHALL display "Connection Lost" and retry
8. THE Frontend SHALL provide a "Retry" button for failed requests
9. THE Frontend SHALL log all API errors with request/response details

### Requirement 9: Test Mock Updates

**User Story:** As a developer, I want test mocks to match real API responses, so that tests accurately reflect production behavior.

#### Acceptance Criteria

1. THE Frontend SHALL update MSW handlers in `test/mocks/handlers.ts` to match backend schemas
2. THE Frontend SHALL use realistic test data matching production data structures
3. THE Frontend SHALL test error scenarios with appropriate HTTP status codes
4. THE Frontend SHALL test loading states with delayed mock responses
5. THE Frontend SHALL test retry logic with intermittent failures

### Requirement 10: Integration Testing

**User Story:** As a developer, I want integration tests for critical API flows, so that I can verify end-to-end functionality.

#### Acceptance Criteria

1. THE Frontend SHALL test the complete annotation creation flow (create → read → update → delete)
2. THE Frontend SHALL test the resource loading flow (fetch resource → fetch chunks → display)
3. THE Frontend SHALL test the quality data flow (fetch quality → recalculate → refresh)
4. THE Frontend SHALL test error recovery (API failure → retry → success)
5. THE Frontend SHALL test authentication flow (login → fetch user → access protected resources)
6. THE Frontend SHALL test rate limiting (exceed limit → display warning → retry after cooldown)

