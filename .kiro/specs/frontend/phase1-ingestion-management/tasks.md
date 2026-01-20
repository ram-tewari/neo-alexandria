# Implementation Plan: Phase 1 - Ingestion Management

## Overview

This implementation plan breaks down the Phase 1 ingestion management feature into discrete, incremental tasks. Each task builds on previous work and includes testing to validate functionality early. The plan follows the execution steps from the mega prompt: Types/API → Poller Hook → Data Table → Wizard → Route Integration.

## Tasks

- [x] 1. Set up project dependencies
  - Install @tanstack/react-table: `npm install @tanstack/react-table`
  - Install fast-check for property testing: `npm install -D fast-check`
  - Verify all shadcn/ui components are installed (Table, Dialog, Tabs, Form, Badge, Toast)
  - _Requirements: 10.1-10.10_

- [x] 2. Create type definitions and API client
  - [x] 2.1 Create src/core/types/resource.ts with Resource interface and ResourceStatus enum
    - Define ResourceStatus enum: 'pending', 'processing', 'completed', 'failed'
    - Define Resource interface with all required fields (id, title, url, status, quality_score, created_at, updated_at, classification_code)
    - Define ResourceListResponse, ResourceAccepted, ResourceStatusResponse, IngestResourcePayload interfaces
    - Use strict TypeScript (no 'any' types)
    - _Requirements: 4.1-4.3_

  - [x] 2.2 Write unit tests for type definitions
    - Test enum values are correct
    - Test interface structure with TypeScript compiler
    - _Requirements: 4.8_

  - [x] 2.3 Create src/features/resources/api.ts with API client functions
    - Implement fetchResources(params) with offset calculation: (page - 1) * limit
    - Implement sort parameter parsing: "created_at:desc" → sort_by="created_at", sort_dir="desc"
    - Implement ingestResource(payload) for POST /resources
    - Implement getResourceStatus(id) for GET /resources/{id}/status
    - Implement getResource(id) for GET /resources/{id}
    - Use apiClient from Phase 0 (already configured with token management)
    - _Requirements: 4.4-4.7, 1.7, 3.6_

  - [x] 2.4 Write unit tests for API client
    - Test offset calculation for various page/limit combinations
    - Test sort parameter parsing
    - Test query string construction
    - Test API calls with correct endpoints and payloads
    - _Requirements: 1.7, 3.6_

  - [x] 2.5 Write property test for API client parameter correctness
    - **Property 1: API Client Parameter Correctness**
    - **Validates: Requirements 1.7, 3.6**
    - Generate random page, limit, sort combinations
    - Verify offset = (page - 1) * limit
    - Verify sort_by and sort_dir extracted correctly
    - Run 100 iterations
    - _Requirements: 1.7, 3.6_

- [x] 3. Implement useResourcePoller hook
  - [x] 3.1 Create src/features/resources/hooks/useResourcePoller.ts
    - Use TanStack Query's useQuery with refetchInterval
    - Set enabled: !!resourceId
    - Set refetchInterval to 2000ms for pending/processing status
    - Stop polling (return false) for completed/failed status
    - Invalidate ['resources', 'list'] query on completion
    - Call onComplete callback on completion
    - Call onError callback on failure
    - Set staleTime: 0 for always fresh data
    - _Requirements: 2.1-2.7_

  - [x] 3.2 Write unit tests for useResourcePoller
    - Test polling starts for pending/processing status
    - Test polling stops for completed/failed status
    - Test query invalidation on completion
    - Test onComplete callback invoked
    - Test onError callback invoked on failure
    - _Requirements: 2.3-2.5_

  - [x] 3.3 Write property test for polling interval consistency
    - **Property 2: Polling Interval Consistency**
    - **Validates: Requirements 2.2**
    - Generate random pending/processing status
    - Record timestamps of API calls
    - Verify intervals are 2000ms ±100ms tolerance
    - Run 100 iterations
    - _Requirements: 2.2_

  - [x] 3.4 Write property test for polling termination
    - **Property 3: Polling Termination**
    - **Validates: Requirements 2.3**
    - Generate random completed/failed status
    - Verify polling stops after status change
    - Verify no additional API calls after termination
    - Run 100 iterations
    - _Requirements: 2.3_

- [x] 4. Implement useResourceList and useIngestResource hooks
  - [x] 4.1 Create src/features/resources/hooks/useResourceList.ts
    - Use TanStack Query's useQuery
    - Set queryKey: ['resources', 'list', { page, limit, sort }]
    - Set keepPreviousData: true for smooth pagination
    - Set staleTime: 30000 (30 seconds cache)
    - _Requirements: 3.6_

  - [x] 4.2 Create src/features/resources/hooks/useIngestResource.ts
    - Use TanStack Query's useMutation
    - Call ingestResource API function
    - Invalidate ['resources', 'list'] query on success
    - _Requirements: 1.7, 7.1-7.2_

  - [x] 4.3 Write unit tests for useResourceList
    - Test query key includes page, limit, sort
    - Test keepPreviousData enabled
    - Test staleTime set correctly
    - _Requirements: 3.6_

  - [x] 4.4 Write unit tests for useIngestResource
    - Test mutation calls API with correct payload
    - Test query invalidation on success
    - Test error handling
    - _Requirements: 1.7, 7.2_

- [x] 5. Checkpoint - Verify hooks and API layer
  - Ensure all tests pass
  - Verify type safety (no 'any' types)
  - Ask the user if questions arise

- [x] 6. Implement StatusBadge component
  - [x] 6.1 Create src/features/resources/components/StatusBadge.tsx
    - Use shadcn Badge component
    - Map status to colors: pending → yellow, processing → blue, completed → green, failed → red
    - Use Lucide icons: Clock, Loader2, CheckCircle2, XCircle
    - Add spinning animation for processing status
    - Apply color classes: bg-yellow-100, bg-blue-100, bg-green-100, bg-red-100
    - _Requirements: 6.1-6.7, 3.3_

  - [x] 6.2 Write unit tests for StatusBadge
    - Test each status renders correct color
    - Test each status renders correct icon
    - Test processing status has spinning animation
    - Test accessibility (ARIA labels)
    - _Requirements: 6.2-6.5_

  - [x] 6.3 Write property test for status badge color mapping
    - **Property 4: Status Badge Color Mapping**
    - **Validates: Requirements 3.3, 6.2-6.5**
    - Generate random status values
    - Verify correct color class applied
    - Run 100 iterations
    - _Requirements: 3.3, 6.2-6.5_

- [x] 7. Implement ResourceDataTable component
  - [x] 7.1 Create src/features/resources/components/ResourceDataTable.tsx
    - Use @tanstack/react-table with useReactTable hook
    - Set manualPagination: true
    - Set manualSorting: true
    - Define columns: Status (Badge), Title (link), Classification (Badge), Quality (color-coded), Date
    - Use StatusBadge for status column
    - Make title a clickable link to /resources/{id}
    - Color-code quality: <0.5 red, 0.5-0.7 yellow, >0.7 green
    - Use shadcn Table components (Table, TableHeader, TableBody, TableRow, TableCell)
    - Add pagination controls with Previous/Next buttons
    - Disable Previous on first page, Next on last page
    - Display "Page X of Y (Z total resources)"
    - Show skeleton loader during isLoading
    - _Requirements: 3.1-3.11_

  - [x] 7.2 Create TableSkeleton component
    - Display 5 placeholder rows with animate-pulse
    - Match table structure
    - _Requirements: 3.10, 8.1-8.2_

  - [x] 7.3 Write unit tests for ResourceDataTable
    - Test all columns render correctly
    - Test pagination button states (first/last page)
    - Test skeleton loader during loading
    - Test empty state when no resources
    - Test title click navigation
    - _Requirements: 3.2, 3.5, 3.8-3.10_

  - [x] 7.4 Write property test for quality score color coding
    - **Property 5: Quality Score Color Coding**
    - **Validates: Requirements 3.4**
    - Generate random quality scores (0.0 to 1.0)
    - Verify correct color class applied based on thresholds
    - Run 100 iterations
    - _Requirements: 3.4_

- [x] 8. Implement IngestionWizard component
  - [x] 8.1 Create src/features/resources/components/IngestionWizard.tsx
    - Use shadcn Dialog component
    - Use shadcn Tabs component with 3 tabs: "Single URL", "File Upload", "Batch Paste"
    - Implement Single URL tab with Input and Button
    - Use react-hook-form for form handling
    - Validate URL format (must start with http:// or https://)
    - Show loading spinner on submit button during submission
    - Use useIngestResource hook for mutation
    - Display success toast on 201 response: "Ingestion Started"
    - Display error toast on 400/500 response with backend error message
    - Close dialog on successful submission
    - Reset form after submission
    - Mark File Upload and Batch Paste tabs as "Coming soon" (disabled)
    - _Requirements: 1.1-1.10_

  - [x] 8.2 Write unit tests for IngestionWizard
    - Test tab switching
    - Test form validation (URL format, required fields)
    - Test submit button disabled during loading
    - Test success toast on 201 response
    - Test error toast on 400/500 response
    - Test dialog closes on successful submission
    - Test form reset after submission
    - _Requirements: 1.5, 1.7-1.10_

- [x] 9. Implement Resources route
  - [x] 9.1 Create src/routes/_auth.resources.tsx
    - Use _auth layout for authentication protection
    - Add page title: "Resource Library"
    - Add page description: "Manage and browse your knowledge base"
    - Render IngestionWizard button in top right
    - Render ResourceDataTable as main content
    - Manage page state (useState for page number)
    - Manage sort state (useState for sort string, default: "created_at:desc")
    - Set limit to 25 resources per page
    - Pass page, limit, sort to ResourceDataTable
    - Handle onPageChange and onSortChange callbacks
    - _Requirements: 5.1-5.7_

  - [x] 9.2 Write integration test for route protection
    - Test unauthenticated users are redirected to login
    - Test authenticated users can access route
    - _Requirements: 5.4_

- [x] 10. Implement error handling
  - [x] 10.1 Add error handling to IngestionWizard
    - Handle network errors with toast: "Network error. Please check your connection."
    - Handle 400 errors with backend error message
    - Handle 429 errors with "Rate limit exceeded. Please try again in X seconds"
    - Handle 500 errors with "Server error. Please try again later"
    - Log all errors to console
    - _Requirements: 9.1-9.8_

  - [x] 10.2 Add error handling to useResourcePoller
    - Handle 404 errors (resource deleted): stop polling, show toast
    - Handle polling errors: retry up to 3 times with exponential backoff
    - Handle failed status: stop polling, show error badge, log error
    - _Requirements: 2.5_

  - [x] 10.3 Write unit tests for error handling
    - Test network error toast
    - Test 429 error message
    - Test 500 error message
    - Test error logging
    - _Requirements: 9.2, 9.5-9.7_

- [x] 11. Add loading states and performance optimizations
  - [x] 11.1 Add loading states to IngestionWizard
    - Disable submit button during submission
    - Show Loader2 icon with spinning animation
    - _Requirements: 1.10, 8.3_

  - [x] 11.2 Add minimum loading duration (200ms) to prevent flashing
    - Implement in ResourceDataTable skeleton loader
    - _Requirements: 8.4_

  - [x] 11.3 Add lazy loading for IngestionWizard dialog
    - Use React.lazy() to code-split the dialog
    - Wrap in Suspense boundary
    - _Requirements: 8.7_

  - [x] 11.4 Write unit tests for loading states
    - Test submit button disabled during loading
    - Test loading spinner appears
    - Test minimum loading duration
    - _Requirements: 8.3-8.4_

- [x] 12. Final checkpoint - Integration testing
  - [x] 12.1 Write integration test for complete ingestion flow
    - Open ingestion wizard
    - Submit URL
    - Verify POST request sent
    - Verify dialog closes
    - Verify toast appears
    - Verify table refreshes
    - Verify polling starts
    - Mock status changes
    - Verify badge updates
    - Verify polling stops on completion

  - [x] 12.2 Write integration test for pagination flow
    - Load initial page
    - Click "Next"
    - Verify API called with correct offset
    - Verify table updates
    - Verify "Previous" enabled
    - Navigate to last page
    - Verify "Next" disabled

  - [x] 12.3 Write integration test for error recovery flow
    - Submit invalid URL
    - Verify error toast
    - Correct URL
    - Resubmit
    - Verify success

- [x] 13. Final verification
  - Run all tests: `npm test`
  - Run property tests with 100 iterations
  - Verify 80% code coverage: `npm test -- --coverage`
  - Run type checking: `npm run type-check`
  - Verify no 'any' types in resource-related code
  - Test manually in browser
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional test tasks that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with 100 iterations
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- All tasks build incrementally on previous work
- No hanging or orphaned code - everything is integrated

## Testing Configuration

**Property-Based Testing**:
- Library: fast-check
- Iterations: 100 per property test
- Tag format: `// Feature: phase1-ingestion-management, Property X: [property text]`

**Unit Testing**:
- Framework: Vitest
- Component Testing: React Testing Library
- Coverage Goal: 80%

**Integration Testing**:
- Test complete user flows
- Mock API responses
- Verify state changes and UI updates
