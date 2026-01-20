# Requirements Document - Phase 1: Ingestion Management

## Introduction

Phase 1 builds on the SPA foundation (Phase 0) to implement the core resource ingestion workflow. This phase enables users to add resources to their library via URL submission, monitor ingestion progress in real-time, and view their resource library with filtering and sorting capabilities.

## Glossary

- **Resource**: A document, article, or web page ingested into the system
- **Ingestion**: The process of fetching, processing, and storing a resource
- **Ingestion_Status**: Current state of resource processing (pending, processing, completed, failed)
- **Resource_Library**: The main view displaying all user resources
- **Upload_Form**: UI component for submitting new resource URLs

## Requirements

### Requirement 1: Ingestion Wizard Dialog

**User Story:** As a user, I want to submit resources through multiple methods (URL, file upload, batch paste), so that I can add content to my library flexibly.

#### Acceptance Criteria

1. THE Ingestion_Wizard SHALL be displayed as a Dialog component
2. THE Ingestion_Wizard SHALL contain Tabs for different ingestion methods: "Single URL", "File Upload", "Batch Paste"
3. THE Single_URL_Tab SHALL display an input field for entering a resource URL
4. THE Single_URL_Tab SHALL display an "Ingest" submit button
5. THE File_Upload_Tab SHALL display a file input restricted to PDF and TXT formats
6. THE Batch_Paste_Tab SHALL display a textarea for pasting multiple URLs (one per line)
7. WHEN a user submits via any tab, THE System SHALL send a POST request to /api/v1/resources
8. WHEN the backend accepts the resource (201 status), THE System SHALL close the dialog and display a toast "Ingestion Started"
9. WHEN the backend returns an error (400/500), THE System SHALL display the error message in a toast
10. THE System SHALL show a loading state on the submit button during submission

### Requirement 2: Real-Time Ingestion Polling

**User Story:** As a user, I want to see real-time updates on ingestion progress, so that I know when my resources are ready.

#### Acceptance Criteria

1. THE System SHALL implement a useResourcePoller hook for tracking ingestion status
2. THE Poller SHALL call GET /api/v1/resources/{id}/status every 2 seconds
3. THE Poller SHALL only run when resource status is "pending" or "processing"
4. WHEN status changes to "completed", THE Poller SHALL stop and invalidate the resources list query
5. WHEN status changes to "failed", THE Poller SHALL stop and display an error notification
6. THE Poller SHALL display progress information if available from the backend
7. THE Poller SHALL use TanStack Query with refetchInterval for automatic polling

### Requirement 3: Resource Data Table

**User Story:** As a user, I want to view all my resources in a data table with server-side pagination and sorting, so that I can efficiently browse large libraries.

#### Acceptance Criteria

1. THE Resource_Table SHALL use @tanstack/react-table with manualPagination enabled
2. THE Resource_Table SHALL display columns: Status (Badge), Title (Bold link), Classification (Tag), Quality (Color-coded), Date
3. THE Status_Column SHALL use Badge components with colors: Pending (Yellow), Processing (Blue), Completed (Green), Failed (Red)
4. THE Quality_Column SHALL display quality_score with color coding: <0.5 (Red), 0.5-0.7 (Yellow), >0.7 (Green)
5. THE Title_Column SHALL be a clickable link that navigates to /resources/{id}
6. THE Resource_Table SHALL fetch data from GET /api/v1/resources with query parameters: page, limit, sort
7. THE Resource_Table SHALL display pagination controls: Previous, Page X of Y, Next
8. WHEN on the first page, THE System SHALL disable the "Previous" button
9. WHEN on the last page, THE System SHALL disable the "Next" button
10. THE Resource_Table SHALL show a skeleton loader while fetching data
11. THE Resource_Table SHALL support server-side sorting by clicking column headers

### Requirement 4: Type Safety and API Layer

**User Story:** As a developer, I want strict TypeScript types for all resource data, so that I can catch errors at compile time.

#### Acceptance Criteria

1. THE System SHALL define a Resource interface in src/core/types/resource.ts
2. THE Resource interface SHALL include: id (string), title (string), url (string), status (ResourceStatus), quality_score (number), created_at (string), classification_code (string | null)
3. THE System SHALL define a ResourceStatus enum with values: 'pending', 'processing', 'completed', 'failed'
4. THE System SHALL define API functions in src/features/resources/api.ts
5. THE fetchResources function SHALL accept parameters: page, limit, sort and return Promise<ResourceListResponse>
6. THE ingestResource function SHALL accept payload and return Promise<ResourceAccepted>
7. THE getResourceStatus function SHALL accept id and return Promise<ResourceStatus>
8. THE System SHALL use no 'any' types in resource-related code

### Requirement 5: Route Integration

**User Story:** As a user, I want to access the resource management interface from the dashboard, so that I can manage my library.

#### Acceptance Criteria

1. THE System SHALL create a route at /resources or integrate into /dashboard
2. THE Route SHALL render the Ingestion Wizard button in the top right
3. THE Route SHALL render the Resource Data Table as the main content
4. THE Route SHALL be protected by authentication (requires login)
5. THE Route SHALL use the _auth layout from Phase 0
6. THE Route SHALL display a page title "Resource Library" or "My Resources"
7. THE Route SHALL be accessible from the main navigation menu

### Requirement 6: Status Badge Visualization

**User Story:** As a user, I want clear visual indicators for resource status, so that I can quickly identify the state of each resource.

#### Acceptance Criteria

1. THE System SHALL use shadcn Badge component for status display
2. WHEN status is "pending", THE System SHALL display a Yellow badge with "Pending" text
3. WHEN status is "processing", THE System SHALL display a Blue badge with "Processing" text and animated spinner
4. WHEN status is "completed", THE System SHALL display a Green badge with "Ready" text
5. WHEN status is "failed", THE System SHALL display a Red badge with "Failed" text and error icon
6. THE Badge SHALL be consistent across the data table and detail views
7. THE System SHALL use Lucide React icons for status indicators

### Requirement 7: Optimistic UI Updates

**User Story:** As a user, I want immediate feedback when I submit a resource, so that the interface feels responsive.

#### Acceptance Criteria

1. WHEN a resource is submitted successfully, THE System SHALL optionally add a temporary "Processing" row to the table
2. WHEN the poller detects status change to "completed", THE System SHALL invalidate the ['resources', 'list'] query key
3. WHEN the query is invalidated, THE System SHALL automatically refetch the resource list
4. THE System SHALL use TanStack Query's optimistic update pattern for immediate feedback
5. THE System SHALL handle race conditions between optimistic updates and server responses
6. WHEN an optimistic update fails, THE System SHALL rollback to the previous state
7. THE System SHALL display a toast notification for successful ingestion start

### Requirement 9: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages and feedback, so that I understand what's happening and can take action.

#### Acceptance Criteria

1. WHEN ingestion fails, THE System SHALL display a toast.error with the backend error message
2. WHEN a network request fails, THE System SHALL display a toast notification with retry option
3. WHEN the API returns a 401 error, THE System SHALL trigger token refresh automatically
4. WHEN token refresh fails, THE System SHALL redirect to the login page
5. WHEN the API returns a 429 error, THE System SHALL display "Rate limit exceeded. Please try again in X seconds"
6. WHEN the API returns a 500 error, THE System SHALL display "Server error. Please try again later"
7. THE System SHALL log all errors to the browser console for debugging
8. THE System SHALL use shadcn Toast component for all notifications

### Requirement 8: Performance and Loading States

**User Story:** As a user, I want smooth loading experiences, so that the interface feels polished and responsive.

#### Acceptance Criteria

1. THE Resource_Table SHALL use TanStack Query's isLoading state to show skeleton loaders
2. THE Skeleton_Loader SHALL display placeholder rows matching the table structure
3. THE Ingestion_Wizard SHALL disable the submit button and show a spinner during submission
4. THE System SHALL display loading states for a minimum of 200ms to prevent flashing
5. WHEN a request takes longer than 5 seconds, THE System SHALL display a "Taking longer than expected" message
6. THE System SHALL use React.Suspense for code splitting where appropriate
7. THE System SHALL lazy load the Ingestion Wizard dialog to reduce initial bundle size

### Requirement 10: shadcn/ui Component Usage

**User Story:** As a developer, I want to use shadcn/ui components consistently, so that the UI has a cohesive design system.

#### Acceptance Criteria

1. THE System SHALL use shadcn Table component for the resource data table
2. THE System SHALL use shadcn Dialog component for the ingestion wizard
3. THE System SHALL use shadcn Tabs component for ingestion method selection
4. THE System SHALL use shadcn Form component for input validation
5. THE System SHALL use shadcn Badge component for status indicators
6. THE System SHALL use shadcn Button component for all actions
7. THE System SHALL use shadcn Toast component for notifications
8. THE System SHALL use shadcn Progress component for ingestion progress (if available)
9. THE System SHALL use Lucide React icons throughout the interface
10. THE System SHALL follow shadcn/ui theming and styling conventions
