# Implementation Plan

- [x] 1. Set up Phase 1 infrastructure and API integration





  - Install required dependencies (@tanstack/react-query, react-pdf, nanoid)
  - Create API client modules for resources, quality, and graph endpoints
  - Set up React Query provider and configuration
  - Create TypeScript interfaces matching backend schemas
  - _Requirements: 14_


- [x] 1.1 Create typed API client for resources

  - Implement resourcesApi with list, get, create, update, delete, getStatus, batchUpdate methods
  - Add proper TypeScript types for all request/response shapes
  - Implement error handling with ApiError class
  - _Requirements: 14_


- [x] 1.2 Create API clients for quality and graph

  - Implement qualityApi.getDetails method
  - Implement graphApi.getNeighbors method
  - Add TypeScript interfaces for QualityDetails and GraphNeighbor
  - _Requirements: 14_


- [x] 1.3 Set up React Query configuration

  - Configure QueryClientProvider in app root
  - Set default staleTime and cacheTime values
  - Add React Query DevTools for development
  - _Requirements: 14, 19_

- [x] 2. Implement infinite scroll library view




- [ ] 2. Implement infinite scroll library view
  - Create useInfiniteScroll hook with IntersectionObserver
  - Implement useInfiniteResources hook with React Query
  - Update LibraryView component to use infinite scroll
  - Add sentinel element at 80% scroll height
  - Maintain scroll position on page load
  - _Requirements: 1, 16_


- [x] 2.1 Create useInfiniteScroll hook

  - Implement IntersectionObserver-based hook
  - Add threshold and rootMargin configuration
  - Handle cleanup and re-observation
  - _Requirements: 1_

- [x] 2.2 Implement infinite resource loading


  - Create useInfiniteResources hook with useInfiniteQuery
  - Implement getNextPageParam logic
  - Flatten pages into single array
  - Handle loading and error states
  - _Requirements: 1, 16_


- [x] 2.3 Update LibraryView with infinite scroll

  - Add sentinel element with ref
  - Display skeleton cards while loading next page
  - Show end-of-list indicator when no more pages
  - _Requirements: 1, 16_

- [x] 3. Build faceted filter sidebar



- [ ] 3. Build faceted filter sidebar
  - Create FilterSidebar component with filter sections
  - Implement useResourceFilters hook with URL sync
  - Add FilterOption and FilterSection components
  - Implement RangeSlider for quality filter
  - Fetch and display facet counts
  - Apply optimistic UI updates
  - _Requirements: 2, 19_

- [x] 3.1 Create filter state management hook


  - Implement useResourceFilters with URL synchronization
  - Parse filters from search params
  - Update URL when filters change
  - _Requirements: 2, 19_


- [x] 3.2 Build FilterSidebar component

  - Create sidebar layout with filter sections
  - Add classification, quality, type, language, and read status filters
  - Display result counts for each facet option
  - Implement "Clear All Filters" button
  - _Requirements: 2_


- [x] 3.3 Implement responsive filter sidebar

  - Fixed sidebar on desktop (≥768px)
  - Collapsible drawer on mobile (<768px)
  - Add filter button in header for mobile
  - _Requirements: 2, 18_


- [ ] 3.4 Create empty state component
  - Design empty state with illustration
  - Show when no resources match filters
  - Provide "Clear Filters" action
  - _Requirements: 2_


- [x] 4. Implement batch selection and operations



  - Create useBatchSelection hook
  - Add checkbox UI to ResourceCard in batch mode
  - Build BatchToolbar component
  - Implement batch update API calls
  - Add keyboard shortcuts (Cmd+A, Shift+Click, Escape)
  - _Requirements: 3, 15_

- [x] 4.1 Create batch selection hook


  - Implement useBatchSelection with Set-based state
  - Add toggleSelection, selectAll, clearSelection methods
  - _Requirements: 3_


- [x] 4.2 Add batch mode UI to library

  - Add batch mode toggle in LibraryHeader
  - Show checkboxes on ResourceCard when batch mode active
  - Implement checkbox selection logic
  - _Requirements: 3, 15_


- [x] 4.3 Build BatchToolbar component

  - Create floating toolbar with selected count
  - Add batch action buttons (Add to Collection, Change Status, Update Tags)
  - Implement slide-up animation with Framer Motion
  - Call batchUpdate API on action
  - _Requirements: 3_


- [x] 4.4 Add batch selection keyboard shortcuts

  - Implement Cmd/Ctrl+A for select all
  - Add Shift+Click for range selection
  - Add Escape to clear selection
  - _Requirements: 3, 15_

- [x] 5. Create view density toggle



- [ ] 5. Create view density toggle
  - Add density toggle to LibraryHeader
  - Implement density configurations (compact, comfortable, spacious)
  - Persist density preference in localStorage
  - Animate layout transitions smoothly
  - _Requirements: 4_

- [x] 5.1 Build DensityToggle component


  - Create three-option toggle (compact, comfortable, spacious)
  - Style active state with background and shadow
  - _Requirements: 4_



- [ ] 5.2 Apply density to resource grid
  - Define density configurations for gap and padding
  - Apply density classes to grid layout
  - Animate transitions with Framer Motion layout prop

  - _Requirements: 4_

- [x] 6. Build file upload system




  - Create UploadZone component with drag-and-drop
  - Implement useUploadQueue hook
  - Build UploadQueue and UploadItem components
  - Add file validation (type, size)
  - Implement upload progress tracking
  - Poll ingestion status until completion
  - _Requirements: 5, 6, 8, 16_


- [x] 6.1 Create UploadZone component

  - Implement drag-and-drop handlers
  - Add visual feedback for drag-over state
  - Validate file types and sizes
  - Show error toasts for invalid files
  - _Requirements: 5_

- [x] 6.2 Implement upload queue management


  - Create useUploadQueue hook with queue state
  - Implement addFiles and addURL methods
  - Handle concurrent uploads (max 3)
  - Track upload progress with onUploadProgress
  - _Requirements: 6, 16_

- [x] 6.3 Build upload status polling


  - Implement pollStatus function with 5s intervals
  - Update item status based on ingestion_status
  - Handle timeout after 60 attempts (5 minutes)
  - Show success toast on completion
  - _Requirements: 6, 8_

- [x] 6.4 Create UploadQueue UI components


  - Build UploadQueue component with progress summary
  - Create UploadItem component with status icons
  - Add progress bar with animated width
  - Show stage labels (downloading, extracting, analyzing)
  - Implement retry and cancel actions

  - _Requirements: 6, 8_


- [x] 7. Add URL ingestion feature


  - Create URLIngestion component with input form
  - Validate URL format before submission
  - Add URL to upload queue
  - Display URL-specific status indicators
  - _Requirements: 7, 8_

- [x] 7.1 Build URLIngestion component


  - Create form with URL input field
  - Implement URL validation
  - Add submit button with loading state
  - Show validation errors inline
  - _Requirements: 7_

- [x] 7.2 Integrate URL ingestion with upload queue


  - Call addURL method from useUploadQueue
  - Display URL items in upload queue
  - Handle URL-specific errors
  - _Requirements: 7, 8_
-

- [x] 8. Create resource detail page structure



  - Build ResourceDetailPage with routing
  - Create ResourceHeader component
  - Implement Breadcrumbs component
  - Add FloatingActionButton with scroll detection
  - Set up tab navigation with URL sync
  - _Requirements: 9, 10_

- [x] 8.1 Build ResourceDetailPage layout


  - Set up page route at /resources/:id
  - Fetch resource data with useQuery
  - Display breadcrumbs and header
  - Add tab navigation
  - _Requirements: 9, 10_


- [x] 8.2 Create ResourceHeader component

  - Display title, creator, type, date, language
  - Show subject tags as pills
  - Style with proper typography and spacing
  - _Requirements: 9_



- [x] 8.3 Implement ResourceTabs component

  - Create tab list with Content, Annotations, Metadata, Graph, Quality tabs
  - Sync active tab with URL query parameter
  - Implement ARIA roles and attributes
  - Add keyboard navigation (arrow keys)
  - _Requirements: 10, 15_


- [x] 8.4 Add FloatingActionButton

  - Show button when scrolled past 200px
  - Animate with scale transition
  - Position fixed at bottom-right
  - _Requirements: 9_
-

- [x] 9. Implement Content tab with PDF viewer



  - Create ContentTab component
  - Build PDFViewer component with react-pdf
  - Add zoom controls (+, -, preset levels)
  - Implement page navigation (prev, next, jump-to)
  - Make responsive for different screen sizes
  - _Requirements: 11, 18_

- [x] 9.1 Build PDFViewer component


  - Integrate react-pdf Document and Page components
  - Implement zoom state and controls
  - Add page navigation state and controls
  - Create toolbar with controls
  - _Requirements: 11_


- [x] 9.2 Make PDF viewer responsive

  - Adjust scale for mobile devices
  - Stack controls vertically on small screens
  - Ensure touch-friendly controls (44x44px)
  - _Requirements: 11, 18_

-

- [x] 10. Create Quality tab with visualization



  - Build QualityTab component
  - Create QualityChart component with radial chart
  - Display dimension breakdown with progress bars
  - Fetch quality data from API
  - Show outlier warning if applicable
  - Animate chart sweep on mount
  - _Requirements: 12, 16_


- [x] 10.1 Build QualityChart component

  - Create SVG radial chart with animated stroke
  - Implement sweep animation with Framer Motion
  - Display score in center
  - _Requirements: 12_


- [x] 10.2 Create QualityTab layout

  - Fetch quality details with useQuery
  - Display overall score chart
  - Show dimension breakdown in grid
  - Animate dimension progress bars
  - Add outlier warning card
  - _Requirements: 12_
-

- [x] 11. Implement Metadata tab




  - Create MetadataTab component
  - Display all Dublin Core fields
  - Show ingestion status and timestamps
  - Format dates and values properly
  - _Requirements: 10_



- [x] 12. Create Graph and Annotations tab placeholders


  - Build GraphTab component with placeholder message
  - Create AnnotationsTab component with placeholder
  - Structure components for future implementation
  - _Requirements: 10, 13_


- [x] 13. Add error boundaries and error handling




  - Create FeatureErrorBoundary component
  - Wrap major features with error boundaries
  - Implement ApiError class
  - Add error handling to all API calls
  - Display user-friendly error messages
  - _Requirements: 17_


- [x] 13.1 Create error boundary component

  - Implement FeatureErrorBoundary with error state
  - Display error UI with retry button
  - Log errors to console
  - _Requirements: 17_


- [x] 13.2 Add error handling to API clients

  - Create ApiError class with status and data
  - Implement handleApiError function
  - Add try-catch blocks to all API calls
  - _Requirements: 17_


- [x] 13.3 Display error states in components

  - Show error messages in LibraryView
  - Display upload errors in UploadItem
  - Handle resource detail 404 errors

  - _Requirements: 17_
-

- [x] 14. Implement responsive design



  - Make filter sidebar responsive (drawer on mobile)
  - Adapt resource grid columns for screen sizes
  - Stack resource detail tabs on mobile
  - Adjust upload zone for touch interfaces
  - Ensure all touch targets are 44x44px minimum
  - _Requirements: 18_


- [x] 14.1 Make library view responsive

  - Implement drawer for filter sidebar on mobile
  - Adjust grid columns: 1 (mobile), 2 (tablet), 3 (desktop)
  - Add filter button in mobile header
  - _Requirements: 18_

- [x] 14.2 Make resource detail responsive


  - Stack tabs vertically on mobile
  - Adjust header layout for small screens
  - Make floating action button mobile-friendly
  - _Requirements: 18_


- [x] 14.3 Make upload interface responsive

  - Adjust drop zone size for mobile

  - Stack upload queue items on small screens
  - Ensure touch-friendly controls
  - _Requirements: 18_
-

- [x] 15. Integrate with Phase 0 features



  - Add Phase 1 commands to command palette
  - Use Phase 0 toast system for all notifications
  - Apply Phase 0 theme variables to new components
  - Reuse Phase 0 UI primitives (Button, Card, Input, Skeleton)
  - Maintain Phase 0 keyboard shortcuts
  - _Requirements: 20_


- [x] 15.1 Add commands to command palette

  - Register upload-file command
  - Register upload-url command
  - Register filter-resources command
  - Register batch-mode toggle command
  - _Requirements: 20_


- [x] 15.2 Use Phase 0 components consistently

  - Replace any custom buttons with Phase 0 Button
  - Use Phase 0 Card for all card layouts
  - Use Phase 0 Input for form fields
  - Use Phase 0 Skeleton for loading states
  - _Requirements: 20_


- [x] 15.3 Apply Phase 0 theme to new components

  - Use CSS variables for colors
  - Apply transition timing from Phase 0
  - Ensure dark mode support
  - _Requirements: 20_



- [ ] 16. Implement accessibility features



  - Add keyboard navigation to all interactive elements
  - Implement ARIA attributes for tabs and dialogs
  - Add screen reader announcements for dynamic content
  - Ensure visible focus indicators (2px outline, 2px offset)
  - Add skip links and landmark regions

  - _Requirements: 15_

- [x] 16.1 Add keyboard navigation

  - Implement Tab navigation for all controls
  - Add arrow key navigation for filters and tabs
  - Add Enter/Space for selection in batch mode
  - Add keyboard shortcuts for common actions
  - _Requirements: 15_


- [x] 16.2 Implement ARIA attributes

  - Add role="tablist" and role="tab" to tabs
  - Add role="tabpanel" to tab content
  - Add aria-live regions for dynamic updates
  - Add aria-label to icon-only buttons
  - _Requirements: 15_


- [x] 16.3 Add screen reader support

  - Announce filter changes
  - Announce upload progress
  - Announce batch selection count
  - Add sr-only text for context
  - _Requirements: 15_

-


- [ ] 17. Optimize performance
  - Implement React.memo for ResourceCard
  - Add debouncing to filter inputs (300ms)
  - Implement request cancellation on filter change
  - Add prefetching for next page on hover
  - Use stale-while-revalidate for resource data
  - _Requirements: 16, 19_

- [ ] 17.1 Add memoization
  - Wrap ResourceCard with React.memo
  - Memoize expensive filter computations
  - Use useMemo for derived state
  - _Requirements: 16_

- [ ] 17.2 Implement debouncing and throttling
  - Debounce filter input changes
  - Throttle scroll event handlers
  - Cancel in-flight requests on new filter
  - _Requirements: 16, 19_

- [ ] 17.3 Configure React Query caching
  - Set staleTime to 5 minutes
  - Set cacheTime to 10 minutes
  - Implement optimistic updates for mutations
  - Add prefetching for common navigation paths
  - _Requirements: 19_

- [ ] 18. Write unit tests for hooks and utilities
  - Test useInfiniteScroll hook
  - Test useResourceFilters hook
  - Test useBatchSelection hook
  - Test useUploadQueue hook
  - Test API client functions
  - _Requirements: 14, 16_

- [ ] 19. Write integration tests for features
  - Test library view with filters and infinite scroll
  - Test upload flow from file selection to completion
  - Test batch selection and operations
  - Test resource detail page navigation
  - _Requirements: 1, 2, 3, 5, 6, 9, 10_

- [ ] 20. Write E2E tests for critical flows
  - Test complete upload flow
  - Test filter and browse flow
  - Test batch operation flow
  - Test resource detail navigation
  - _Requirements: 1, 2, 3, 5, 6, 9_

- [ ] 21. Performance testing and optimization
  - Run Lighthouse audits
  - Measure FCP, TTI, and other metrics
  - Optimize bundle size
  - Test with large datasets (1000+ resources)
  - _Requirements: 16_

- [ ] 22. Accessibility audit
  - Run axe-core automated tests
  - Perform manual keyboard navigation testing
  - Test with screen readers
  - Verify color contrast ratios
  - _Requirements: 15_
