# Implementation Plan

- [x] 1. Project setup and configuration





  - Install additional dependencies (Framer Motion, Recharts)
  - Configure TailwindCSS with custom color scheme
  - Set up environment variables and API client
  - Configure TanStack Query client
  - _Requirements: 1.1, 12.3_

- [x] 1.1 Install animation and visualization dependencies


  - Install framer-motion for animations
  - Install recharts for data visualization
  - Install @tanstack/react-query-devtools for debugging
  - _Requirements: 1.2, 14.1_

- [x] 1.2 Configure TailwindCSS with custom color palette


  - Extend tailwind.config.js with charcoal grey, neutral blue, and accent blue colors
  - Add custom animation utilities and timing functions
  - Configure responsive breakpoints
  - _Requirements: 1.1, 11.1_

- [x] 1.3 Set up API client and interceptors


  - Create axios instance with base URL configuration
  - Implement request interceptor for auth tokens
  - Implement response interceptor for error handling
  - Create environment variable configuration
  - _Requirements: 12.5_

- [x] 1.4 Configure TanStack Query client


  - Set up QueryClient with caching strategies
  - Configure stale-while-revalidate behavior
  - Add QueryClientProvider to app root
  - _Requirements: 12.4_

- [x] 2. Core infrastructure and utilities





  - Create Zustand store for global state
  - Implement API service modules (resources, search, graph, collections, citations)
  - Create custom React hooks for data fetching
  - Build error handling utilities
  - _Requirements: 12.5_

- [x] 2.1 Create Zustand store with persistence


  - Define AppState interface with UI, user, and selection state
  - Implement store actions (toggleSidebar, setTheme, updatePreferences, toggleResourceSelection)
  - Configure persist middleware for localStorage
  - _Requirements: 7.2, 7.3, 7.4_

- [x] 2.2 Implement API service modules


  - Create resourcesApi with CRUD operations
  - Create searchApi with search and suggestions
  - Create graphApi for knowledge graph data
  - Create collectionsApi for collection management
  - Create citationsApi for citation network data
  - _Requirements: 3.2, 4.2, 5.3, 5.4, 10.3_

- [x] 2.3 Create custom React hooks for data fetching


  - Implement useResources, useResource, useCreateResource hooks
  - Implement useSearch hook with debouncing
  - Implement useKnowledgeGraph hook
  - Implement useCollections and useCollection hooks
  - Implement useCitations hook
  - _Requirements: 3.2, 4.2, 5.3, 9.2_

- [x] 2.4 Build error handling utilities


  - Create handleApiError function for axios errors
  - Implement ErrorBoundary component
  - Create toast notification system
  - _Requirements: 12.5_

- [x] 3. Shared UI components library




  - Build AnimatedCard component with hover effects
  - Create Button component with variants
  - Implement Modal component with animations
  - Build Dropdown and Tooltip components
  - Create SkeletonLoader and LoadingSpinner components
  - _Requirements: 1.2, 1.4, 12.2_

- [x] 3.1 Build AnimatedCard component


  - Create card with Framer Motion animations
  - Implement hover effects (scale, translateY, shadow)
  - Add variants for different card types
  - _Requirements: 1.2, 1.5_

- [x] 3.2 Create Button component with variants


  - Implement primary, secondary, and ghost button styles
  - Add loading state with spinner
  - Add disabled state styling
  - Implement hover and focus animations
  - _Requirements: 1.2, 1.5_

- [x] 3.3 Implement Modal component with animations


  - Create modal with backdrop and content
  - Add scale and fade animations on open/close
  - Implement focus trap and escape key handling
  - Add accessibility attributes (ARIA)
  - _Requirements: 1.4, 11.3_

- [x] 3.4 Build Dropdown and Tooltip components


  - Create Dropdown using Headless UI with animations
  - Implement Tooltip with positioning logic
  - Add keyboard navigation support
  - _Requirements: 1.2, 11.3_

- [x] 3.5 Create SkeletonLoader and LoadingSpinner


  - Build SkeletonLoader with shimmer animation
  - Create LoadingSpinner with rotation animation
  - Add variants for different content types
  - _Requirements: 1.4, 12.2_

- [x] 4. Layout and navigation components





  - Build AppLayout with routing structure
  - Create TransparentNavbar with scroll detection
  - Implement PageTransition wrapper
  - Build Footer component
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.1 Build AppLayout with routing structure


  - Create AppLayout component with Outlet for nested routes
  - Set up React Router with route configuration
  - Implement lazy loading for route components
  - Add Suspense boundaries with loading states
  - _Requirements: 2.4_

- [x] 4.2 Create TransparentNavbar with scroll detection


  - Implement scroll event listener with throttling
  - Add state for isScrolled and isMobileMenuOpen
  - Create transparent to solid background transition
  - Add backdrop blur effect when scrolled
  - Implement mobile hamburger menu
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 4.3 Implement PageTransition wrapper


  - Create transition component using Framer Motion
  - Add fade and slide animations for route changes
  - Configure animation variants and timing
  - _Requirements: 1.3_

- [x] 4.4 Build Footer component


  - Create footer with links and copyright
  - Add responsive layout
  - Style with color scheme
  - _Requirements: 1.1_

- [x] 5. Home page and dashboard




  - Create HomePage with hero section
  - Build RecommendationsFeed component
  - Implement QuickSearchPanel with autocomplete
  - Create RecentActivityTimeline component
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.1 Create HomePage with hero section


  - Build hero section with animated background gradient
  - Add welcome message and call-to-action
  - Implement stagger animations for content
  - _Requirements: 3.1, 1.3_

- [x] 5.2 Build RecommendationsFeed component


  - Fetch recommendations from API
  - Display recommendations in card grid
  - Add relevance scores and reasoning
  - Implement loading and error states
  - _Requirements: 3.2, 12.2, 12.5_

- [x] 5.3 Implement QuickSearchPanel with autocomplete


  - Create search input with debounced onChange
  - Fetch autocomplete suggestions from API
  - Display suggestions dropdown with keyboard navigation
  - Navigate to search results on submit
  - _Requirements: 3.3, 3.4_

- [x] 5.4 Create RecentActivityTimeline component


  - Fetch recent activity from local storage or API
  - Display timeline with resource cards
  - Add timestamps using date-fns
  - Implement click navigation to resources
  - _Requirements: 3.5_

- [x] 6. Library page and resource management





  - Create LibraryPage with grid/list view toggle
  - Build FacetedSearchSidebar with filters
  - Implement ResourceGrid and ResourceList components
  - Create ResourceCard component with actions
  - Build BulkActionBar for selected resources
  - Implement UploadResourceModal
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6.1 Create LibraryPage with view toggle


  - Build page layout with header and content area
  - Add grid/list view toggle button
  - Implement pagination controls
  - Fetch resources with filters and pagination
  - _Requirements: 4.1, 4.2_

- [x] 6.2 Build FacetedSearchSidebar with filters


  - Create sidebar with collapsible filter sections
  - Implement classification_code filter with checkboxes
  - Add type, language, read_status filters
  - Create quality_score range slider
  - Add subject filters with autocomplete
  - Update URL params on filter change
  - _Requirements: 4.3, 9.3_

- [x] 6.3 Implement ResourceGrid and ResourceList


  - Create ResourceGrid with responsive columns
  - Build ResourceList with compact row layout
  - Add selection checkboxes
  - Implement infinite scroll or pagination
  - _Requirements: 4.2_

- [x] 6.4 Create ResourceCard component with actions

  - Build card with resource metadata display
  - Add quality score badge with color coding
  - Display classification and read status badges
  - Implement quick actions menu (edit, delete, add to collection)
  - Add hover animations
  - _Requirements: 4.2, 1.5_

- [x] 6.5 Build BulkActionBar for selected resources


  - Create sticky action bar that appears when resources selected
  - Add bulk delete action with confirmation
  - Implement bulk edit metadata modal
  - Add bulk add to collection action
  - Add bulk classify action
  - Display selected count
  - _Requirements: 4.4_

- [x] 6.6 Implement UploadResourceModal


  - Create modal with URL input form
  - Add validation for URL format
  - Submit resource creation request
  - Poll for ingestion status updates
  - Display progress indicator
  - Show success/error notifications
  - _Requirements: 4.5, 13.1, 13.2, 13.3, 13.4_

- [x] 7. Resource detail page




  - Create ResourceDetailPage layout
  - Build ResourceHeader with metadata and actions
  - Implement ContentViewer with annotation support
  - Create KnowledgeGraphPanel with visualization
  - Build CitationNetworkPanel
  - Implement VersionHistoryTimeline
  - Create QualityMetricsCard
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.1 Create ResourceDetailPage layout


  - Build page with sidebar and main content area
  - Fetch resource data by ID
  - Implement loading skeleton
  - Handle 404 errors
  - _Requirements: 5.1, 5.2_

- [x] 7.2 Build ResourceHeader with metadata and actions


  - Display title, creator, publisher, source
  - Show classification badge and quality score
  - Add action buttons (edit, delete, add to collection)
  - Display read status with update dropdown
  - _Requirements: 5.1_

- [x] 7.3 Implement ContentViewer with annotation support


  - Display resource description and summary
  - Add annotation toolbar
  - Implement text selection and highlight
  - Store annotations in local storage
  - Display existing annotations with highlights
  - _Requirements: 5.5_

- [x] 7.4 Create KnowledgeGraphPanel with visualization


  - Fetch graph neighbors from API
  - Render force-directed graph using react-force-graph-2d
  - Color nodes by classification_code
  - Size nodes by quality_score
  - Add hover tooltips with resource info
  - Implement click navigation to resources
  - _Requirements: 5.3, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.5 Build CitationNetworkPanel


  - Fetch citations from API
  - Display inbound and outbound citations in tabs
  - Show citation type badges
  - Display importance scores
  - Add context snippets
  - Implement click navigation to cited resources
  - _Requirements: 5.4, 14.2_

- [x] 7.6 Implement VersionHistoryTimeline


  - Fetch version history (if available from API)
  - Display timeline with dates and changes
  - Add visual timeline connector
  - _Requirements: 5.5_

- [x] 7.7 Create QualityMetricsCard


  - Display quality score with radial progress
  - Show metadata completeness percentage
  - Display readability metrics
  - Add quality suggestions list
  - _Requirements: 5.5, 14.1_

- [x] 8. Search and discovery page








  - Create SearchPage with advanced search form
  - Build SearchResults component with facets
  - Implement HybridWeightSlider
  - Create FacetPanel with counts
  - Add sort and filter controls
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


- [x] 8.1 Create SearchPage with advanced search form



  - Build search input with submit button
  - Add hybrid weight slider (0.0 to 1.0)
  - Implement advanced filters panel
  - Fetch search results on form submit
  - Update URL with search params
  - _Requirements: 9.1, 9.4_

- [x] 8.2 Build SearchResults component with facets

  - Display search results in grid/list view
  - Show relevance scores on cards
  - Display total results count
  - Implement pagination
  - _Requirements: 9.2_

- [x] 8.3 Implement HybridWeightSlider

  - Create slider component with labels
  - Show "Keyword" at 0.0, "Balanced" at 0.5, "Semantic" at 1.0
  - Update search on slider change with debounce
  - _Requirements: 9.4_

- [x] 8.4 Create FacetPanel with counts

  - Display facets from search response
  - Show counts for each facet value
  - Implement checkbox selection
  - Update search filters on selection
  - _Requirements: 9.3_

- [x] 8.5 Add sort and filter controls

  - Create sort dropdown (relevance, date, quality, title)
  - Add sort direction toggle
  - Update search on sort change
  - _Requirements: 9.5_

- [x] 9. Classification browser page




  - Create ClassificationPage layout
  - Build ClassificationTree component
  - Implement ResourceListByClassification
  - Create BulkClassifyModal
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9.1 Create ClassificationPage layout





  - Build page with tree sidebar and content area
  - Fetch classification tree from API
  - Implement loading state
  - _Requirements: 6.1_

- [x] 9.2 Build ClassificationTree component


  - Render hierarchical tree with expand/collapse
  - Display classification codes and names
  - Show resource counts per classification
  - Highlight selected classification
  - Implement click to select classification
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 9.3 Implement ResourceListByClassification


  - Fetch resources filtered by selected classification
  - Display resources in grid/list view
  - Add selection checkboxes
  - Implement pagination
  - _Requirements: 6.4_

- [x] 9.4 Create BulkClassifyModal


  - Build modal with classification tree selector
  - Allow selecting target classification
  - Submit bulk classify request
  - Show success/error notifications
  - Refresh resource list on success
  - _Requirements: 6.5_

- [x] 10. Collections management





  - Create CollectionsPage with collection list
  - Build CollectionCard component
  - Implement CreateCollectionModal
  - Create CollectionDetailPage
  - Build AddToCollectionModal
  - Implement CollectionRecommendations component
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 10.1 Create CollectionsPage with collection list


  - Fetch collections from API
  - Display collections in grid with cards
  - Show collection hierarchy with indentation
  - Add create collection button
  - Implement search/filter for collections
  - _Requirements: 10.2_

- [x] 10.2 Build CollectionCard component


  - Display collection name and description
  - Show resource count
  - Display visibility badge
  - Add hover animations
  - Implement click navigation to detail page
  - _Requirements: 10.2_

- [x] 10.3 Implement CreateCollectionModal


  - Build form with name, description, visibility inputs
  - Add parent collection selector (hierarchical)
  - Validate form inputs
  - Submit create collection request
  - Navigate to new collection on success
  - _Requirements: 10.1, 10.5_

- [x] 10.4 Create CollectionDetailPage


  - Fetch collection with resources
  - Display collection metadata
  - Show resources in grid/list view
  - Add remove from collection action
  - Display subcollections
  - Show collection recommendations
  - _Requirements: 10.3, 10.4_

- [x] 10.5 Build AddToCollectionModal


  - Display list of user's collections
  - Add search/filter for collections
  - Allow selecting multiple collections
  - Submit add resources request
  - Show success notification
  - _Requirements: 10.3_


- [x] 10.6 Implement CollectionRecommendations component

  - Fetch recommendations for collection
  - Display resource recommendations with relevance scores
  - Display collection recommendations
  - Add "Add to collection" quick action
  - _Requirements: 10.4_
-

- [x] 11. User profile and settings




  - Create ProfilePage with tabs
  - Build PreferencesPanel
  - Implement AccountSettingsPanel
  - Create NotificationPreferencesPanel
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11.1 Create ProfilePage with tabs


  - Build page layout with tab navigation
  - Implement tab switching with animations
  - Load user preferences from store
  - _Requirements: 7.1_


- [x] 11.2 Build PreferencesPanel

  - Create subject preferences multi-select
  - Add language preferences checkboxes
  - Implement recommendation settings
  - Add save button with loading state
  - Update Zustand store on save
  - _Requirements: 7.2, 7.3_

- [x] 11.3 Implement AccountSettingsPanel


  - Display user ID input (for demo purposes)
  - Add theme toggle (dark/light)
  - Add default view preference (grid/list)
  - Add items per page selector
  - Save settings to store
  - _Requirements: 7.4_

- [x] 11.4 Create NotificationPreferencesPanel


  - Add toggle for ingestion completion notifications
  - Add toggle for quality update notifications
  - Add toggle for recommendation notifications
  - Save preferences to store
  - _Requirements: 7.5_

- [x] 12. Data visualization components





  - Create QualityScoreRadial component
  - Build CitationNetworkGraph component
  - Implement ClassificationDistributionChart
  - Create TemporalTrendsChart
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 12.1 Create QualityScoreRadial component





  - Build radial progress indicator using SVG
  - Color code by quality level (red, yellow, green)
  - Add animated fill on mount
  - Display percentage in center
  - _Requirements: 14.1, 14.5_

- [x] 12.2 Build CitationNetworkGraph component


  - Render citation graph using react-force-graph-2d
  - Size nodes by importance score (PageRank)
  - Color nodes by citation type
  - Add hover tooltips
  - Implement click navigation
  - _Requirements: 14.2, 14.5_

- [x] 12.3 Implement ClassificationDistributionChart


  - Create bar chart using Recharts
  - Display classification codes on x-axis
  - Show resource counts on y-axis
  - Add hover tooltips with details
  - Implement click to filter by classification
  - _Requirements: 14.3, 14.5_

- [x] 12.4 Create TemporalTrendsChart


  - Build line chart using Recharts
  - Display dates on x-axis
  - Show resource creation counts on y-axis
  - Add multiple series for different types
  - Implement zoom and pan interactions
  - _Requirements: 14.4, 14.5_


- [x] 13. Responsive design and mobile optimization






  - Implement responsive navbar with mobile menu
  - Create mobile-optimized card layouts
  - Add touch-friendly interaction targets
  - Implement swipe gestures for mobile
  - Test on various screen sizes
  - _Requirements: 11.1, 11.2_

- [x] 13.1 Implement responsive navbar with mobile menu


  - Add hamburger menu button for mobile
  - Create slide-in mobile menu with animations
  - Stack navigation items vertically
  - Add close button
  - _Requirements: 2.5, 11.1_

- [x] 13.2 Create mobile-optimized card layouts


  - Adjust card padding and spacing for mobile
  - Stack card content vertically on small screens
  - Increase touch target sizes to 44x44px minimum
  - _Requirements: 11.1, 11.2_

- [x] 13.3 Add touch-friendly interaction targets


  - Ensure all buttons meet minimum size requirements
  - Add touch feedback animations
  - Implement swipe-to-delete for mobile lists
  - _Requirements: 11.2_

- [x] 13.4 Test responsive design on multiple devices






  - Test on mobile (320px, 375px, 414px widths)
  - Test on tablet (768px, 1024px widths)
  - Test on desktop (1280px, 1920px widths)
  - Verify touch interactions on actual devices
  - _Requirements: 11.1_

- [x] 14. Accessibility implementation





  - Add ARIA labels to all interactive elements
  - Implement keyboard navigation
  - Add focus indicators
  - Test with screen readers
  - Implement skip links
  - _Requirements: 11.3, 11.4, 11.5_

- [x] 14.1 Add ARIA labels and semantic HTML


  - Add aria-label to icon buttons
  - Use semantic HTML elements (nav, main, article)
  - Add aria-describedby for form inputs
  - Implement aria-live regions for dynamic content
  - _Requirements: 11.5_

- [x] 14.2 Implement keyboard navigation


  - Ensure all interactive elements are keyboard accessible
  - Add keyboard shortcuts for common actions
  - Implement focus trap in modals
  - Add escape key to close modals and dropdowns
  - _Requirements: 11.3_

- [x] 14.3 Add focus indicators


  - Style focus rings with accent blue color
  - Ensure focus indicators are visible on all elements
  - Add focus-visible for keyboard-only focus
  - _Requirements: 11.4_

- [x] 14.4 Implement skip links


  - Add "Skip to main content" link at top
  - Add "Skip to navigation" link
  - Style skip links to be visible on focus
  - _Requirements: 11.3_

- [x] 14.5 Test with screen readers






  - Test with NVDA on Windows
  - Test with VoiceOver on macOS
  - Verify all content is announced correctly
  - Test form validation announcements
  - _Requirements: 11.5_

- [ ] 15. Performance optimization
  - Implement code splitting for routes
  - Add React.memo to expensive components
  - Optimize images with lazy loading
  - Implement virtual scrolling for large lists
  - Add service worker for caching
  - _Requirements: 12.1, 12.3, 12.4_

- [ ] 15.1 Implement code splitting for routes
  - Use React.lazy for route components
  - Add Suspense boundaries with loading fallbacks
  - Configure Vite for optimal chunk splitting
  - _Requirements: 12.3_

- [ ] 15.2 Add React.memo to expensive components
  - Memoize ResourceCard component
  - Memoize graph visualization components
  - Memoize chart components
  - Use useMemo for expensive computations
  - Use useCallback for event handlers
  - _Requirements: 12.1_

- [ ] 15.3 Optimize images with lazy loading
  - Add loading="lazy" to image elements
  - Implement blur-up technique for images
  - Use WebP format with fallbacks
  - _Requirements: 12.1_

- [ ] 15.4 Implement virtual scrolling for large lists
  - Use react-window for resource lists
  - Configure item size and overscan
  - Add scroll restoration
  - _Requirements: 12.1_

- [ ] 15.5 Add service worker for caching

  - Configure Vite PWA plugin
  - Cache static assets
  - Implement offline fallback page
  - Add cache invalidation strategy
  - _Requirements: 12.4_

- [ ] 16. Animation polish and micro-interactions
  - Add page transition animations
  - Implement stagger animations for lists
  - Create loading state animations
  - Add success/error animation feedback
  - Implement scroll-triggered animations
  - _Requirements: 1.2, 1.3, 1.4, 1.5_

- [ ] 16.1 Add page transition animations
  - Implement fade and slide transitions between routes
  - Add exit animations for leaving pages
  - Configure transition timing
  - _Requirements: 1.3_

- [ ] 16.2 Implement stagger animations for lists
  - Add stagger effect to resource grids
  - Animate list items on mount
  - Use Framer Motion's staggerChildren
  - _Requirements: 1.3_

- [ ] 16.3 Create loading state animations
  - Enhance skeleton loaders with shimmer
  - Add pulse animation to loading spinners
  - Animate progress bars
  - _Requirements: 1.4_

- [ ] 16.4 Add success/error animation feedback
  - Create success checkmark animation
  - Add error shake animation
  - Implement toast slide-in animations
  - _Requirements: 1.2_

- [ ] 16.5 Implement scroll-triggered animations
  - Add fade-in on scroll for sections
  - Implement parallax effect for hero section
  - Use Intersection Observer for performance
  - Respect prefers-reduced-motion
  - _Requirements: 1.2_

- [ ] 17. Final integration and polish
  - Connect all pages to API endpoints
  - Test complete user workflows
  - Fix any remaining bugs
  - Optimize bundle size
  - Add error boundaries to all routes
  - _Requirements: All_

- [ ] 17.1 Connect all pages to API endpoints
  - Verify all API calls are working
  - Test error handling for failed requests
  - Ensure loading states display correctly
  - Validate data transformations
  - _Requirements: All_

- [ ] 17.2 Add error boundaries to all routes
  - Wrap each route with ErrorBoundary
  - Create fallback UI for errors
  - Log errors to console (or service)
  - Add retry functionality
  - _Requirements: 12.5_

- [ ] 17.3 Test complete user workflows

  - Test resource upload and ingestion flow
  - Test search and filter workflow
  - Test collection creation and management
  - Test knowledge graph navigation
  - Test mobile responsive behavior
  - _Requirements: All_

- [ ] 17.4 Optimize bundle size

  - Analyze bundle with vite-bundle-visualizer
  - Remove unused dependencies
  - Optimize imports (tree-shaking)
  - Compress assets
  - _Requirements: 12.3_

- [ ] 17.5 Final UI polish
  - Review all animations for smoothness
  - Verify color scheme consistency
  - Check spacing and alignment
  - Test dark theme throughout app
  - Ensure all hover states work correctly
  - _Requirements: 1.1, 1.2, 1.5_
