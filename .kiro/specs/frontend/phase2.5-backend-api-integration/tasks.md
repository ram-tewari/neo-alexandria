# Implementation Plan: Phase 2.5 - Backend API Integration

## Overview

This plan integrates Phase 1 and Phase 2 frontend components with the live backend API at `https://pharos.onrender.com`. The implementation follows an incremental approach: configure the API client, update stores to use real data, add error handling, update tests, and verify integration.

## Tasks

- [x] 1. Configure API Client Foundation
  - Create core API client with axios instance
  - Add environment variable configuration
  - Implement request/response interceptors
  - Add retry logic with exponential backoff
  - Add authentication token management
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 1.1 Write unit tests for API client
  - Test interceptor behavior
  - Test retry logic
  - Test timeout handling
  - Test error transformation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create TypeScript Type Definitions
  - [x] 2.1 Define API request/response types
    - User, Resource, Annotation types
    - Chunk, Quality, Health types
    - Error types with discriminated unions
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 2.2 Define API client interfaces
    - workbenchApi interface
    - editorApi interface
    - Query key factories
    - _Requirements: 7.1, 7.4_
  
  - [x] 2.3 Add runtime type validation (development only)
    - Use zod for schema validation
    - Validate API responses in dev mode
    - _Requirements: 7.5_

- [ ] 3. Implement Phase 1 API Integration
  - [x] 3.1 Create workbench API client module
    - Implement getCurrentUser endpoint
    - Implement getResources endpoint
    - Implement getRateLimit endpoint
    - Implement health check endpoints
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 3.2 Create TanStack Query hooks for Phase 1
    - useCurrentUser hook
    - useResources hook with pagination
    - useSystemHealth hook with polling
    - useRateLimit hook
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 3.3 Update workbench store to use real data
    - Remove mock data from repository store
    - Integrate useResources hook
    - Add loading and error states
    - _Requirements: 2.2, 2.5, 2.6_
  
  - [x] 3.4 Write integration tests for Phase 1 flows
    - Test user authentication flow
    - Test resource list loading
    - Test health status polling
    - _Requirements: 10.5_

- [x] 4. Checkpoint - Verify Phase 1 Integration
  - Ensure all Phase 1 components display real data
  - Ensure repository switcher shows actual repositories
  - Ensure command palette shows health status
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Phase 2 Resource & Chunk API Integration
  - [x] 5.1 Create editor API client module (resources & chunks)
    - Implement getResource endpoint
    - Implement getResourceStatus endpoint
    - Implement getChunks endpoint
    - Implement getChunk endpoint
    - Implement triggerChunking endpoint
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 5.2 Create TanStack Query hooks for resources & chunks
    - useResource hook with caching
    - useResourceStatus hook with polling
    - useChunks hook
    - useChunk hook
    - useTriggerChunking mutation
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 5.3 Update editor store to use real resource data
    - Remove mock resource data
    - Integrate useResource hook
    - Add loading and error states
    - _Requirements: 3.1, 3.5, 3.6_
  
  - [x] 5.4 Update chunk store to use real chunk data
    - Remove mock chunk data
    - Integrate useChunks hook
    - Update SemanticChunkOverlay component
    - _Requirements: 3.2, 3.3, 3.5, 3.6_
  
  - [x] 5.5 Write integration tests for resource loading
    - Test resource fetch and display
    - Test chunk loading and overlay
    - Test processing status polling
    - _Requirements: 10.2_

- [ ] 6. Implement Annotation API Integration
  - [x] 6.1 Create annotation API client methods
    - Implement createAnnotation endpoint
    - Implement getAnnotations endpoint
    - Implement updateAnnotation endpoint
    - Implement deleteAnnotation endpoint
    - Implement search endpoints (fulltext, semantic, tags)
    - Implement export endpoints (markdown, json)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 6.2 Create TanStack Query hooks for annotations
    - useAnnotations hook
    - useCreateAnnotation mutation with optimistic updates
    - useUpdateAnnotation mutation with optimistic updates
    - useDeleteAnnotation mutation with optimistic updates
    - useSearchAnnotations hook
    - useExportAnnotations hook
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 6.3 Update annotation store to use real data
    - Remove mock annotation data
    - Integrate annotation query hooks
    - Update AnnotationGutter component
    - Update AnnotationPanel component
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.9, 4.10_
  
  - [x] 6.4 Write property test for optimistic updates
    - **Property 2: Optimistic Update Consistency**
    - **Validates: Requirements 4.10**
  
  - [x] 6.5 Write integration tests for annotation CRUD
    - Test complete annotation lifecycle
    - Test optimistic updates and rollback
    - Test search functionality
    - Test export functionality
    - _Requirements: 10.1_

- [x] 7. Checkpoint - Verify Phase 2 Core Integration
  - Ensure Monaco editor loads real file content
  - Ensure semantic chunks display correctly
  - Ensure annotations persist to backend
  - Ensure all tests pass, ask the user if questions arise.

- [-] 8. Implement Quality API Integration
  - [x] 8.1 Create quality API client methods
    - Implement recalculateQuality endpoint
    - Implement getQualityOutliers endpoint
    - Implement getQualityDegradation endpoint
    - Implement getQualityDistribution endpoint
    - Implement getQualityTrends endpoint
    - Implement getQualityDimensions endpoint
    - Implement getQualityReviewQueue endpoint
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [x] 8.2 Create TanStack Query hooks for quality data
    - useQualityDetails hook (from resource metadata)
    - useRecalculateQuality mutation
    - useQualityOutliers hook
    - useQualityDegradation hook
    - useQualityDistribution hook
    - useQualityTrends hook
    - useQualityDimensions hook
    - useQualityReviewQueue hook
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [x] 8.3 Update quality store to use real data
    - Remove mock quality data
    - Integrate quality query hooks
    - Update QualityBadgeGutter component
    - _Requirements: 5.1, 5.9, 5.10_
  
  - [x] 8.4 Write integration tests for quality data flow
    - Test quality badge display
    - Test quality recalculation
    - Test quality analytics endpoints
    - _Requirements: 10.3_

- [x] 9. Implement Graph Hover API Integration
  - [x] 9.1 Create hover API client method
    - Implement getHoverInfo endpoint
    - Add debouncing logic (300ms)
    - _Requirements: 6.1, 6.2_
  
  - [x] 9.2 Create TanStack Query hook for hover data
    - useHoverInfo hook with debouncing
    - Configure 30-minute cache
    - _Requirements: 6.1, 6.3, 6.4_
  
  - [x] 9.3 Update HoverCardProvider to use real data
    - Remove mock hover data
    - Integrate useHoverInfo hook
    - Add loading state
    - Add fallback for failures
    - _Requirements: 6.1, 6.3, 6.5_
  
  - [x] 9.4 Write property test for debouncing
    - **Property 8: Debounce Consistency**
    - **Validates: Requirements 6.2**

- [x] 10. Implement Error Handling and Loading States
  - [x] 10.1 Create error handling utilities
    - Error classification function
    - Error message mapping
    - Retry strategy implementation
    - Circuit breaker implementation
    - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 10.2 Create error UI components
    - ErrorToast component for transient errors
    - ErrorMessage component for inline errors
    - ErrorBoundary component for catastrophic errors
    - RetryButton component
    - _Requirements: 8.1, 8.8, 8.9_
  
  - [x] 10.3 Add loading states to all components
    - Add skeleton loaders to editor
    - Add loading spinners to panels
    - Add progress indicators for long operations
    - _Requirements: 2.5, 3.5, 8.1_
  
  - [x] 10.4 Write property tests for error handling
    - **Property 4: Error Code Mapping**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7**
  
  - [x] 10.5 Write integration tests for error recovery
    - Test network error recovery
    - Test 401 redirect to login
    - Test 429 rate limit handling
    - Test 500 server error retry
    - _Requirements: 10.4_

- [x] 11. Update MSW Test Mocks
  - [x] 11.1 Update mock handlers to match backend schemas
    - Update auth endpoint mocks
    - Update resource endpoint mocks
    - Update annotation endpoint mocks
    - Update quality endpoint mocks
    - Update graph endpoint mocks
    - _Requirements: 9.1, 9.2_
  
  - [x] 11.2 Add error scenario mocks
    - Mock 401/403/404/429/500 responses
    - Mock network failures
    - Mock timeout scenarios
    - _Requirements: 9.3_
  
  - [x] 11.3 Add delayed response mocks for loading states
    - Add configurable delays to test loading UI
    - _Requirements: 9.4_

- [x] 12. Write Property-Based Tests
  - [x] 12.1 Property test for authentication persistence
    - **Property 1: Authentication Token Persistence**
    - **Validates: Requirements 1.2**
  
  - [x] 12.2 Property test for cache invalidation
    - **Property 5: Cache Invalidation Correctness**
    - **Validates: Requirements 2.6, 3.6, 4.10**
  
  - [x] 12.3 Property test for type safety
    - **Property 6: Type Safety at Runtime**
    - **Validates: Requirements 7.5**
  
  - [x] 12.4 Property test for loading states
    - **Property 7: Loading State Visibility**
    - **Validates: Requirements 8.1**

- [x] 13. Final Integration Testing
  - [x] 13.1 Test complete user workflows
    - Test login → browse repositories → open file → annotate
    - Test quality recalculation workflow
    - Test annotation search and export workflow
    - _Requirements: 10.1, 10.2, 10.3, 10.5_
  
  - [x] 13.2 Test rate limiting workflow
    - Test rate limit detection
    - Test cooldown timer
    - Test retry after cooldown
    - _Requirements: 10.6_

- [x] 14. Final Checkpoint - Complete Integration Verification
  - Verify all Phase 1 components use real backend data
  - Verify all Phase 2 components use real backend data
  - Verify all error scenarios are handled gracefully
  - Verify all loading states display correctly
  - Verify all tests pass (unit, integration, property-based)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties
- Integration tests validate end-to-end workflows
- All API calls should include proper TypeScript types
- All mutations should use optimistic updates where appropriate
- All queries should use appropriate cache times
- Error handling should be consistent across all components
- **IMPORTANT**: When running tests, use a timeout (e.g., 30 seconds) and press 'q' to quit if tests hang or run in watch mode to avoid getting stuck
