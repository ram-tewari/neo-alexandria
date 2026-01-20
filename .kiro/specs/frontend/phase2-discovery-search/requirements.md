# Requirements Document - Phase 2: Discovery & Search

## Introduction

Phase 2 builds on the Ingestion Management (Phase 1) to implement the "Consumer" side of Neo Alexandria. This phase enables users to discover and search their knowledge base using advanced Hybrid Search, view personalized recommendations, and understand search result relevance through score breakdowns.

## Glossary

- **Hybrid Search**: A search method combining semantic (vector) and keyword (BM25) approaches with configurable weighting
- **Semantic Search**: Vector-based similarity search using embeddings
- **Keyword Search**: Traditional BM25 full-text search
- **Hybrid Weight**: A value (0.0-1.0) controlling the balance between semantic and keyword search
- **Quality Score**: A computed metric (0.0-1.0) indicating resource quality
- **Score Breakdown**: Detailed explanation of why a search result was ranked (semantic score, keyword score, composite)
- **For You Feed**: Personalized recommendations displayed when no search query is active
- **Search Method**: User-selectable mode (Hybrid vs Semantic-only)

## Requirements

### Requirement 1: Hybrid Search API Integration

**User Story:** As a user, I want to search my knowledge base using natural language queries, so that I can find relevant resources quickly.

#### Acceptance Criteria

1. THE System SHALL define a SearchRequest interface with fields: text (string), hybrid_weight (number), filters (object), limit (number)
2. THE System SHALL define a SearchResult interface with fields: id, title, description, score, scores_breakdown, resource_type, quality_score, created_at
3. THE System SHALL define a ScoreBreakdown interface with fields: semantic_score (number), keyword_score (number), composite_score (number)
4. THE System SHALL implement searchResources(payload: SearchRequest) function in src/features/search/api.ts
5. THE searchResources function SHALL send POST /api/v1/search with the payload
6. THE searchResources function SHALL return Promise<SearchResult[]>
7. THE System SHALL use TanStack Query for caching search results with a 5-minute stale time
8. THE System SHALL handle 400 errors (invalid query) and 500 errors (search unavailable) gracefully

### Requirement 2: Real-Time Search with Debouncing

**User Story:** As a user, I want search results to update as I type, so that I can refine my query interactively.

#### Acceptance Criteria

1. THE System SHALL implement a useDebounce hook with 300ms delay
2. THE System SHALL implement a useSearch hook in src/features/search/hooks/useSearch.ts
3. THE useSearch hook SHALL return: query, filters, results, isLoading, error, setQuery, setFilter
4. WHEN the user types in the search input, THE System SHALL debounce the query for 300ms
5. WHEN the debounced query changes, THE System SHALL trigger a new search API call
6. WHEN the query is empty, THE System SHALL return null or empty array (not trigger API call)
7. WHEN a filter changes (e.g., Quality Slider), THE System SHALL trigger search immediately without debounce
8. THE System SHALL cancel in-flight requests when a new search is triggered
9. THE System SHALL use TanStack Query's enabled option to control when searches execute
10. THE System SHALL display loading state during the debounce period

### Requirement 3: Advanced Filter Panel

**User Story:** As a user, I want to filter search results by quality and search method, so that I can refine my results.

#### Acceptance Criteria

1. THE System SHALL create a FilterPanel component in src/features/search/components/FilterPanel.tsx
2. THE FilterPanel SHALL display a "Quality Score" filter using shadcn Slider component
3. THE Quality_Slider SHALL have range 0-100, mapped to 0.0-1.0 for the API
4. THE Quality_Slider SHALL display the current value next to the slider (e.g., "Min Quality: 0.7")
5. THE FilterPanel SHALL display a "Search Method" toggle using shadcn Switch or Tabs
6. THE Search_Method_Toggle SHALL have options: "Hybrid" (default) and "Semantic"
7. WHEN "Hybrid" is selected, THE System SHALL use hybrid_weight: 0.7
8. WHEN "Semantic" is selected, THE System SHALL use hybrid_weight: 1.0 (semantic only)
9. THE FilterPanel SHALL be positioned in a sidebar on desktop (left side)
10. THE FilterPanel SHALL be collapsible on mobile using a "Filters" button
11. THE FilterPanel SHALL use shadcn Separator to divide filter sections
12. THE System SHALL persist filter state in URL query parameters for shareability

### Requirement 4: Hybrid Score Visualization

**User Story:** As a user, I want to understand why a search result appeared, so that I can trust the search algorithm.

#### Acceptance Criteria

1. THE System SHALL create a HybridScoreBadge component in src/features/search/components/HybridScoreBadge.tsx
2. THE HybridScoreBadge SHALL display the composite_score as a percentage (e.g., "92%")
3. THE HybridScoreBadge SHALL use shadcn Badge component with color coding: >80% (Green), 60-80% (Yellow), <60% (Gray)
4. THE HybridScoreBadge SHALL wrap the badge in a shadcn HoverCard component
5. WHEN the user hovers over the badge, THE System SHALL display the score breakdown
6. THE Score_Breakdown_Tooltip SHALL show: "Semantic Match: 0.85", "Keyword Match: 0.40", "Composite: 0.92"
7. THE Score_Breakdown_Tooltip SHALL use visual indicators (progress bars or colored dots) for each score
8. THE HybridScoreBadge SHALL be displayed on each SearchResultItem card
9. THE System SHALL handle missing score_breakdown gracefully (show only composite score)
10. THE HybridScoreBadge SHALL use Lucide React icons (Sparkles for semantic, Search for keyword)

### Requirement 5: Search Result Display

**User Story:** As a user, I want to see search results in a clean, scannable format, so that I can quickly identify relevant resources.

#### Acceptance Criteria

1. THE System SHALL create a SearchResultItem component in src/features/search/components/SearchResultItem.tsx
2. THE SearchResultItem SHALL display: Title (bold, 18px), Description (clamped to 2 lines), Metadata footer
3. THE Metadata_Footer SHALL display: Resource Type badge, Quality Score, HybridScoreBadge, Created Date
4. THE Resource_Type_Badge SHALL use color coding: Article (Blue), Paper (Purple), Book (Green), Website (Gray)
5. THE Description SHALL use CSS line-clamp to truncate at 2 lines with ellipsis
6. THE SearchResultItem SHALL be clickable and navigate to /resources/{id} on click
7. THE SearchResultItem SHALL use shadcn Card component for layout
8. THE SearchResultItem SHALL display a hover effect (subtle shadow or border)
9. THE SearchResultItem SHALL use Lucide React icons for resource types (BookOpen, FileText, Globe)
10. THE System SHALL display search results in a vertical list with 16px spacing

### Requirement 6: Personalized Recommendations Feed

**User Story:** As a user, I want to see personalized recommendations when I'm not searching, so that I can discover relevant content.

#### Acceptance Criteria

1. THE System SHALL create a RecommendationsWidget component in src/features/recommendations/components/RecommendationsWidget.tsx
2. THE System SHALL implement getRecommendations() function in src/features/recommendations/api.ts
3. THE getRecommendations function SHALL call GET /api/v1/recommendations
4. THE getRecommendations function SHALL return Promise<Recommendation[]>
5. THE RecommendationsWidget SHALL display a grid of recommendation cards (2 columns on desktop, 1 on mobile)
6. THE Recommendation_Card SHALL display: Title, Description (clamped to 3 lines), Reason badge
7. THE Reason_Badge SHALL explain why the resource was recommended (e.g., "Similar to X", "Popular in Y")
8. THE RecommendationsWidget SHALL display a section header "For You" with Sparkles icon
9. THE RecommendationsWidget SHALL show skeleton loaders while fetching recommendations
10. THE RecommendationsWidget SHALL only be visible when the search query is empty
11. THE System SHALL use TanStack Query to cache recommendations with a 10-minute stale time

### Requirement 7: Search Route and Layout

**User Story:** As a user, I want a dedicated search page with intuitive layout, so that I can focus on discovery.

#### Acceptance Criteria

1. THE System SHALL create a route at /search using src/routes/_auth.search.tsx
2. THE Search_Route SHALL use the _auth layout (requires authentication)
3. THE Search_Route SHALL display SearchInput at the top (centered, full width)
4. THE Search_Route SHALL display FilterPanel on the left sidebar (desktop only, 280px width)
5. THE Search_Route SHALL display main content area on the right (flexible width)
6. WHEN isLoading is true, THE System SHALL display 5 skeleton cards matching SearchResultItem layout
7. WHEN query is empty, THE System SHALL display RecommendationsWidget in the main area
8. WHEN query is not empty and results exist, THE System SHALL display list of SearchResultItem components
9. WHEN query is not empty and results are empty, THE System SHALL display "No results found" message
10. THE Search_Route SHALL be accessible from the main navigation menu with Search icon
11. THE Search_Route SHALL use responsive layout (stack vertically on mobile)

### Requirement 8: Search Input Component

**User Story:** As a user, I want a prominent search input that's easy to use, so that I can start searching immediately.

#### Acceptance Criteria

1. THE System SHALL create a SearchInput component in src/features/search/components/SearchInput.tsx
2. THE SearchInput SHALL use shadcn Input component with large size (48px height)
3. THE SearchInput SHALL display a Search icon prefix (Lucide React)
4. THE SearchInput SHALL display placeholder text: "Search your knowledge base..."
5. THE SearchInput SHALL display a loading spinner suffix when isLoading is true
6. THE SearchInput SHALL display a clear button (X icon) when query is not empty
7. WHEN the clear button is clicked, THE System SHALL clear the query and focus the input
8. THE SearchInput SHALL auto-focus on page load
9. THE SearchInput SHALL support keyboard shortcuts (Cmd+K or Ctrl+K to focus)
10. THE SearchInput SHALL use the useSearch hook for state management

### Requirement 9: Error Handling and Empty States

**User Story:** As a user, I want clear feedback when search fails or returns no results, so that I understand what happened.

#### Acceptance Criteria

1. WHEN the search API returns a 500 error, THE System SHALL display a banner: "Search unavailable. Please try again later."
2. WHEN the search API returns a 400 error, THE System SHALL display: "Invalid search query. Please try different terms."
3. WHEN search returns zero results, THE System SHALL display an empty state with: "No results found for '{query}'"
4. THE Empty_State SHALL suggest: "Try adjusting your filters or using different keywords"
5. THE Empty_State SHALL display a "Clear Filters" button if any filters are active
6. WHEN recommendations API fails, THE System SHALL display: "Recommendations unavailable" (not crash)
7. THE System SHALL log all errors to console for debugging
8. THE System SHALL use shadcn Alert component for error messages
9. THE System SHALL provide a "Retry" button for failed searches
10. THE System SHALL handle network timeouts gracefully (10-second timeout)

### Requirement 10: Performance and Loading States

**User Story:** As a user, I want smooth loading experiences, so that the interface feels responsive.

#### Acceptance Criteria

1. THE System SHALL use shadcn Skeleton component for loading states
2. THE Skeleton_Loader SHALL mimic the SearchResultItem layout (title, description, footer)
3. THE System SHALL display 5 skeleton cards during initial search load
4. THE System SHALL display a subtle loading indicator in the SearchInput during debounce
5. THE System SHALL use React.Suspense for lazy loading the search route
6. THE System SHALL prefetch recommendations on page load (before user clears search)
7. THE System SHALL use TanStack Query's keepPreviousData option to prevent layout shift
8. THE System SHALL display loading states for a minimum of 200ms to prevent flashing
9. THE System SHALL cancel in-flight requests when component unmounts
10. THE System SHALL use optimistic UI updates for filter changes (show results immediately, then update)

### Requirement 11: Type Safety and API Layer

**User Story:** As a developer, I want strict TypeScript types for all search data, so that I can catch errors at compile time.

#### Acceptance Criteria

1. THE System SHALL define all types in src/features/search/types.ts
2. THE System SHALL define SearchRequest, SearchResult, ScoreBreakdown, SearchFilters interfaces
3. THE System SHALL define SearchMethod enum with values: 'hybrid', 'semantic'
4. THE System SHALL define Recommendation interface in src/features/recommendations/types.ts
5. THE System SHALL use no 'any' types in search-related code
6. THE System SHALL use Zod schemas for runtime validation of API responses
7. THE System SHALL export all types from a central index.ts file
8. THE System SHALL use TypeScript strict mode for all search modules
9. THE System SHALL define API error types (SearchError, RecommendationError)
10. THE System SHALL use discriminated unions for search states (idle, loading, success, error)

### Requirement 12: Accessibility and Keyboard Navigation

**User Story:** As a user with accessibility needs, I want to navigate search using keyboard only, so that I can use the interface effectively.

#### Acceptance Criteria

1. THE SearchInput SHALL be focusable and support Tab navigation
2. THE System SHALL support Cmd+K / Ctrl+K to focus the search input from anywhere
3. THE System SHALL support Escape key to clear the search query
4. THE System SHALL support Arrow keys to navigate between search results
5. THE System SHALL support Enter key to open the selected search result
6. THE FilterPanel controls SHALL be keyboard accessible (Tab, Arrow keys for slider)
7. THE System SHALL use ARIA labels for all interactive elements
8. THE System SHALL announce search results count to screen readers
9. THE System SHALL use semantic HTML (nav, main, aside) for layout
10. THE System SHALL maintain focus management (return focus to input after clearing)

### Requirement 13: URL State Synchronization

**User Story:** As a user, I want to share search URLs with specific queries and filters, so that others can see the same results.

#### Acceptance Criteria

1. THE System SHALL sync search query to URL query parameter: ?q=search+term
2. THE System SHALL sync filters to URL: ?q=term&quality=0.7&method=hybrid
3. WHEN the page loads with URL parameters, THE System SHALL initialize search state from URL
4. WHEN search state changes, THE System SHALL update URL without page reload (pushState)
5. THE System SHALL support browser back/forward navigation (popState)
6. THE System SHALL encode special characters in URL properly
7. THE System SHALL validate URL parameters and fallback to defaults if invalid
8. THE System SHALL preserve URL state when navigating away and returning
9. THE System SHALL use React Router's useSearchParams hook for URL management
10. THE System SHALL debounce URL updates to prevent excessive history entries

### Requirement 14: Mobile Responsiveness

**User Story:** As a mobile user, I want a responsive search interface, so that I can search on any device.

#### Acceptance Criteria

1. THE Search_Route SHALL use responsive layout (stack vertically on <768px)
2. THE FilterPanel SHALL be hidden by default on mobile
3. THE System SHALL display a "Filters" button (SlidersHorizontal icon) on mobile
4. WHEN the Filters button is clicked, THE System SHALL open FilterPanel in a Sheet (slide-in drawer)
5. THE SearchInput SHALL be full width on mobile (no sidebar)
6. THE SearchResultItem cards SHALL be full width on mobile
7. THE RecommendationsWidget SHALL display 1 column on mobile, 2 on tablet, 3 on desktop
8. THE System SHALL use touch-friendly tap targets (minimum 44x44px)
9. THE System SHALL support swipe gestures to close the filter drawer
10. THE System SHALL test on viewport widths: 375px (mobile), 768px (tablet), 1024px (desktop)

### Requirement 15: Analytics and Telemetry

**User Story:** As a product owner, I want to track search usage, so that I can improve the search experience.

#### Acceptance Criteria

1. THE System SHALL log search queries (anonymized) for analytics
2. THE System SHALL track search result clicks (which results users select)
3. THE System SHALL track filter usage (which filters are most used)
4. THE System SHALL track search method preference (hybrid vs semantic)
5. THE System SHALL track "no results" queries for improvement
6. THE System SHALL track search latency (time from query to results)
7. THE System SHALL track recommendation clicks
8. THE System SHALL use a privacy-respecting analytics approach (no PII)
9. THE System SHALL provide opt-out mechanism for analytics
10. THE System SHALL send analytics events to a dedicated endpoint (not block UI)

## Non-Functional Requirements

### Performance
- Search API response time: P95 < 500ms
- Debounce delay: 300ms
- Skeleton display minimum: 200ms
- Page load time: < 2 seconds
- Time to interactive: < 3 seconds

### Scalability
- Support 10,000+ resources in search index
- Handle 100+ concurrent search requests
- Cache search results for 5 minutes
- Prefetch recommendations on idle

### Security
- Validate all user input (XSS prevention)
- Sanitize search queries before API calls
- Use HTTPS for all API requests
- Implement rate limiting on search endpoint

### Usability
- Search input auto-focus on page load
- Clear visual feedback for all actions
- Consistent error messaging
- Responsive design for all screen sizes

## Success Metrics

- Search usage: 80% of users perform at least one search per session
- Search success rate: 70% of searches result in a click
- Filter usage: 30% of users adjust filters
- Recommendation engagement: 20% of users click recommendations
- Mobile usage: 40% of searches from mobile devices
- Search latency: P95 < 500ms
- Zero-result rate: < 10% of searches

## Dependencies

- Phase 0: SPA Foundation (authentication, routing, layout)
- Phase 1: Ingestion Management (resources exist in database)
- Backend: Search API (POST /api/v1/search)
- Backend: Recommendations API (GET /api/v1/recommendations)
- shadcn/ui components: Slider, Badge, HoverCard, Skeleton, Separator, Switch, Sheet
- TanStack Query for data fetching and caching
- React Router for URL state management

## Out of Scope

- Advanced filters (date range, author, tags) - Future phase
- Search history and saved searches - Future phase
- Search suggestions and autocomplete - Future phase
- Faceted search (category filters) - Future phase
- Export search results - Future phase
- Search analytics dashboard - Future phase
- Multi-language search - Future phase
- Voice search - Future phase
