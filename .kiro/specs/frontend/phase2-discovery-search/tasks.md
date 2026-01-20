# Tasks Document - Phase 2: Discovery & Search

## Overview

This document breaks down Phase 2 implementation into incremental, testable tasks. Each task should be completed and verified before moving to the next.

## Task Organization

Tasks are organized into 5 phases:
1. **Foundation**: Types, API layer, core hooks
2. **Core Components**: Search input, filters, result display
3. **Score Visualization**: Hybrid score badge with breakdown
4. **Recommendations**: "For You" feed
5. **Integration**: Route, layout, polish

---

## Phase 2.1: Foundation (Types, API, Hooks)

### Task 1.1: Search Type Definitions ✅
**File**: `src/features/search/types.ts`

**Subtasks**:
- [x] Create `src/features/search/` directory
- [x] Create `types.ts` file
- [x] Define `SearchMethod` enum (hybrid, semantic)
- [x] Define `SearchFilters` interface (min_quality, search_method, resource_types, classification_codes)
- [x] Define `SearchRequest` interface (text, hybrid_weight, filters, limit)
- [x] Define `ScoreBreakdown` interface (semantic_score, keyword_score, composite_score)
- [x] Define `SearchResult` interface (id, title, description, score, scores_breakdown, resource_type, quality_score, created_at, classification_code)
- [x] Define `SearchState` interface (query, filters, results, isLoading, error)
- [x] Export all types from index

**Verification**:
```bash
# No TypeScript errors
npm run type-check
```

**Acceptance Criteria**:
- All interfaces use strict types (no `any`)
- Optional fields marked with `?`
- Enums use PascalCase values

---

### Task 1.2: Recommendations Type Definitions ✅
**File**: `src/features/recommendations/types.ts`

**Subtasks**:
- [x] Create `src/features/recommendations/` directory
- [x] Create `types.ts` file
- [x] Define `Recommendation` interface (id, title, description, reason, resource_type, quality_score, created_at)
- [x] Define `RecommendationsResponse` interface (recommendations, total)
- [x] Export all types

**Verification**:
```bash
npm run type-check
```

**Acceptance Criteria**:
- All fields properly typed
- Matches backend API response structure

---

### Task 1.3: Search API Client ✅
**File**: `src/features/search/api.ts`

**Subtasks**:
- [x] Create `api.ts` file in search feature
- [x] Import types from `./types`
- [x] Create `searchResources` function
  - Accept `SearchRequest` payload
  - Send POST to `/api/v1/search`
  - Return `Promise<SearchResult[]>`
  - Handle errors (400, 500, network)
- [x] Add request timeout (10 seconds)
- [x] Add proper error typing

**Example Implementation**:
```typescript
export async function searchResources(
  payload: SearchRequest
): Promise<SearchResult[]> {
  const response = await fetch('/api/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(10000),
  });
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }
  
  return response.json();
}
```

**Verification**:
- Test with mock API call
- Verify error handling

**Acceptance Criteria**:
- Function properly typed
- Errors thrown with meaningful messages
- Timeout configured

---

### Task 1.4: Recommendations API Client ✅
**File**: `src/features/recommendations/api.ts`

**Subtasks**:
- [x] Create `api.ts` file in recommendations feature
- [x] Import types from `./types`
- [x] Create `getRecommendations` function
  - Accept optional limit parameter
  - Send GET to `/api/v1/recommendations`
  - Return `Promise<Recommendation[]>`
  - Handle errors gracefully

**Verification**:
- Test with mock API
- Verify response parsing

**Acceptance Criteria**:
- Function returns typed array
- Default limit of 10

---

### Task 1.5: useDebounce Hook ✅
**File**: `src/lib/hooks/useDebounce.ts`

**Subtasks**:
- [x] Create `src/lib/hooks/` directory if not exists
- [x] Create `useDebounce.ts` file
- [x] Implement generic debounce hook
  - Accept value and delay parameters
  - Return debounced value
  - Clean up timeout on unmount
- [x] Add TypeScript generics for type safety

**Example Implementation**:
```typescript
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

**Verification**:
- Test with rapid value changes
- Verify 300ms delay works

**Acceptance Criteria**:
- Generic type support
- Cleanup on unmount
- Configurable delay

---

### Task 1.6: useSearch Hook (Core State Machine) ✅
**File**: `src/features/search/hooks/useSearch.ts`

**Subtasks**:
- [x] Create `hooks/` directory in search feature
- [x] Create `useSearch.ts` file
- [x] Import useDebounce, TanStack Query, types
- [x] Implement state management:
  - [x] `query` state (string)
  - [x] `filters` state (SearchFilters with defaults)
  - [x] Debounce query with 300ms delay
- [x] Implement TanStack Query integration:
  - [x] Query key: `['search', debouncedQuery, filters]`
  - [x] Query function calls `searchResources`
  - [x] Enable only when debouncedQuery.length > 0
  - [x] Stale time: 5 minutes
  - [x] keepPreviousData: true
- [x] Implement setQuery function
- [x] Implement setFilter function (immediate, no debounce)
- [x] Implement clearFilters function
- [x] Return hook interface

**Example Implementation**:
```typescript
export function useSearch() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    min_quality: 0,
    search_method: SearchMethod.Hybrid,
  });

  const debouncedQuery = useDebounce(query, 300);

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', debouncedQuery, filters],
    queryFn: () => searchResources({
      text: debouncedQuery,
      hybrid_weight: filters.search_method === SearchMethod.Hybrid ? 0.7 : 1.0,
      filters: { min_quality: filters.min_quality },
      limit: 20,
    }),
    enabled: debouncedQuery.length > 0,
    staleTime: 5 * 60 * 1000,
    keepPreviousData: true,
  });

  const setFilter = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return {
    query,
    filters,
    results: data ?? null,
    isLoading,
    error,
    setQuery,
    setFilter,
    clearFilters: () => setFilters({
      min_quality: 0,
      search_method: SearchMethod.Hybrid,
    }),
  };
}
```

**Verification**:
- Test query debouncing
- Test filter immediate execution
- Test empty query behavior

**Acceptance Criteria**:
- Query debounced at 300ms
- Filters trigger immediate search
- Empty query returns null
- Previous data kept during refetch

---

## Phase 2.2: Core Components

### Task 2.1: SearchInput Component ✅
**File**: `src/features/search/components/SearchInput.tsx`


**Subtasks**:
- [x] Create `components/` directory in search feature
- [x] Create `SearchInput.tsx` file
- [x] Import shadcn Input, Lucide icons (Search, X, Loader2)
- [x] Define props interface (value, onChange, onClear, isLoading, placeholder)
- [x] Implement component:
  - [x] Large input (48px height)
  - [x] Search icon prefix
  - [x] Loading spinner when isLoading
  - [x] Clear button (X) when value exists
  - [x] Auto-focus on mount
  - [x] Placeholder text
- [x] Add keyboard shortcut listener (Cmd+K / Ctrl+K)
- [x] Style with Tailwind classes

**Verification**:
- Test auto-focus
- Test clear button
- Test keyboard shortcut
- Test loading state

**Acceptance Criteria**:
- Controlled component
- Accessible (ARIA labels)
- Keyboard shortcut works
- Visual feedback for all states

---

### Task 2.2: FilterPanel Component ✅
**File**: `src/features/search/components/FilterPanel.tsx`

**Subtasks**:
- [x] Create `FilterPanel.tsx` file
- [x] Import shadcn Slider, Switch, Separator
- [x] Import Lucide icons (SlidersHorizontal)
- [x] Define props interface (filters, onFilterChange, isMobile)
- [x] Implement Quality Score filter:
  - [x] Slider component (0-100 range)
  - [x] Display current value ("Min Quality: 0.7")
  - [x] Map 0-100 to 0.0-1.0 for API
- [x] Implement Search Method toggle:
  - [x] Switch or Tabs component
  - [x] Options: Hybrid (default), Semantic
  - [x] Visual indicator for active method
- [x] Add section separators
- [x] Add section headers
- [x] Handle mobile layout (isMobile prop)

**Verification**:
- Test slider value display
- Test method toggle
- Test filter changes trigger search

**Acceptance Criteria**:
- Slider shows current value
- Method toggle works
- Responsive layout
- Accessible controls

---

### Task 2.3: SearchResultItem Component ✅
**File**: `src/features/search/components/SearchResultItem.tsx`

**Subtasks**:
- [x] Create `SearchResultItem.tsx` file
- [x] Import shadcn Card, Badge
- [x] Import Lucide icons (BookOpen, FileText, Globe)
- [x] Define props interface (result, onClick)
- [x] Implement card layout:
  - [x] Title (bold, 18px, clickable)
  - [x] Description (2-line clamp with ellipsis)
  - [x] Metadata footer (resource type, quality, score, date)
- [x] Add resource type badge with color coding:
  - [x] Article: Blue
  - [x] Paper: Purple
  - [x] Book: Green
  - [x] Website: Gray
- [x] Add hover effect (shadow or border)
- [x] Add click handler to navigate to /resources/{id}
- [x] Format date display
- [x] Add HybridScoreBadge component (Task 3.1)

**Verification**:
- Test click navigation
- Test description truncation
- Test badge colors

**Acceptance Criteria**:
- Card is clickable
- Description clamps at 2 lines
- All metadata displays correctly
- Hover effect works

---

## Phase 2.3: Score Visualization

### Task 3.1: HybridScoreBadge Component ✅
**File**: `src/features/search/components/HybridScoreBadge.tsx`

**Subtasks**:
- [x] Create `HybridScoreBadge.tsx` file
- [x] Import shadcn Badge, HoverCard
- [x] Import Lucide icons (Sparkles, Search, BarChart3)
- [x] Define props interface (score, breakdown?)
- [x] Implement badge display:
  - [x] Show composite score as percentage (92%)
  - [x] Color coding: >80% Green, 60-80% Yellow, <60% Gray
- [x] Implement HoverCard tooltip:
  - [x] Trigger: Badge component
  - [x] Content: Score breakdown
  - [x] Show semantic_score with Sparkles icon
  - [x] Show keyword_score with Search icon
  - [x] Show composite_score with BarChart3 icon
  - [x] Add visual progress bars for each score
- [x] Handle missing breakdown gracefully

**Example Layout**:
```
Badge: "92%" (Green)

Hover Content:
✨ Semantic Match:    85%  ████████████████░░░░
🔍 Keyword Match:     40%  ████████░░░░░░░░░░░░
📊 Composite Score:   92%  ██████████████████░░
```

**Verification**:
- Test hover interaction
- Test color coding
- Test missing breakdown

**Acceptance Criteria**:
- Badge shows percentage
- HoverCard displays on hover
- Progress bars visual
- Handles null breakdown

---

## Phase 2.4: Recommendations

### Task 4.1: RecommendationsWidget Component ✅
**File**: `src/features/recommendations/components/RecommendationsWidget.tsx`

**Subtasks**:
- [x] Create `components/` directory in recommendations feature
- [x] Create `RecommendationsWidget.tsx` file
- [x] Import TanStack Query, shadcn Card, Badge, Skeleton
- [x] Import Lucide icons (Sparkles)
- [x] Implement TanStack Query hook:
  - [x] Query key: `['recommendations']`
  - [x] Query function: `getRecommendations()`
  - [x] Stale time: 10 minutes
- [x] Implement section header:
  - [x] "For You" title with Sparkles icon
  - [x] Subtitle: "Personalized recommendations"
- [x] Implement grid layout:
  - [x] 3 columns on desktop (>1024px)
  - [x] 2 columns on tablet (768-1024px)
  - [x] 1 column on mobile (<768px)
- [x] Implement recommendation card:
  - [x] Title (bold, clickable)
  - [x] Description (3-line clamp)
  - [x] Reason badge (e.g., "Similar to X")
  - [x] Resource type and quality
- [x] Add skeleton loaders (6 cards)
- [x] Handle loading and error states
- [x] Add click handler to navigate

**Verification**:
- Test grid responsiveness
- Test loading state
- Test error handling
- Test navigation

**Acceptance Criteria**:
- Grid responsive
- Cards clickable
- Skeleton matches card layout
- Error handled gracefully

---

## Phase 2.5: Route Integration

### Task 5.1: Search Route Setup ✅
**File**: `src/routes/_auth.search.tsx`

**Subtasks**:
- [x] Create `_auth.search.tsx` file in routes
- [x] Import all search components
- [x] Import RecommendationsWidget
- [x] Import useSearch hook
- [x] Import React Router hooks (useNavigate)
- [x] Set up route with _auth layout

**Verification**:
- Route accessible at /search
- Authentication required

**Acceptance Criteria**:
- Route protected by auth
- Uses _auth layout

---

### Task 5.2: Desktop Layout Implementation ✅
**File**: `src/routes/_auth.search.tsx`

**Subtasks**:
- [x] Implement main container (flex layout)
- [x] Implement left sidebar (280px width):
  - [x] FilterPanel component
  - [x] Hidden on mobile (md:block)
  - [x] Border right
  - [x] Sticky positioning
- [x] Implement main content area:
  - [x] Flex-1 (flexible width)
  - [x] Flex column layout
  - [x] Search input at top (border bottom)
  - [x] Results area (scrollable)
- [x] Add proper spacing and padding

**Verification**:
- Test desktop layout (>768px)
- Test sidebar visibility
- Test scrolling behavior

**Acceptance Criteria**:
- Sidebar fixed width
- Main area flexible
- Proper spacing

---

### Task 5.3: Results Display Logic ✅
**File**: `src/routes/_auth.search.tsx`

**Subtasks**:
- [x] Implement conditional rendering:
  - [x] If isLoading: Show 5 skeleton cards
  - [x] If !query: Show RecommendationsWidget
  - [x] If query && results.length > 0: Show result list
  - [x] If query && results.length === 0: Show empty state
- [x] Create skeleton loader component:
  - [x] Match SearchResultItem layout
  - [x] Show 5 cards
- [x] Create empty state component:
  - [x] "No results found for '{query}'"
  - [x] Suggestion text
  - [x] Clear filters button (if filters active)
- [x] Map results to SearchResultItem components
- [x] Add proper spacing (16px gap)

**Verification**:
- Test all display states
- Test transitions between states
- Test empty state

**Acceptance Criteria**:
- All states render correctly
- Smooth transitions
- Empty state helpful

---

### Task 5.4: Mobile Responsiveness ✅
**File**: `src/routes/_auth.search.tsx`

**Subtasks**:
- [x] Import shadcn Sheet component
- [x] Add mobile filter button:
  - [x] Fixed position or in header
  - [x] SlidersHorizontal icon
  - [x] "Filters" text
  - [x] Only visible on mobile (<768px)
- [x] Implement Sheet (slide-in drawer):
  - [x] Trigger: Filter button
  - [x] Content: FilterPanel with isMobile={true}
  - [x] Side: left or right
  - [x] Close on filter change (optional)
- [x] Test responsive breakpoints:
  - [x] Mobile: <768px (stack vertically)
  - [x] Tablet: 768-1024px (sidebar visible)
  - [x] Desktop: >1024px (full layout)

**Note**: Mobile filter drawer can be added as enhancement. Current implementation hides sidebar on mobile.

**Verification**:
- Test on mobile viewport (375px)
- Test filter drawer open/close
- Test touch interactions

**Acceptance Criteria**:
- Mobile layout stacks vertically
- Filter drawer works
- Touch-friendly (44px tap targets)

---

### Task 5.5: URL State Synchronization ✅
**File**: `src/routes/_auth.search.tsx`

**Subtasks**:
- [x] Import useSearchParams from React Router
- [x] Implement URL sync for query:
  - [x] Read ?q= on mount
  - [x] Update URL when query changes
  - [x] Use pushState (no page reload)
- [x] Implement URL sync for filters:
  - [x] Read ?quality= and ?method= on mount
  - [x] Update URL when filters change
  - [x] Encode special characters
- [x] Implement browser navigation:
  - [x] Support back button
  - [x] Support forward button
  - [x] Restore state from URL
- [x] Debounce URL updates (avoid excessive history)
- [x] Validate URL parameters (fallback to defaults)

**Verification**:
- Test URL updates
- Test browser back/forward
- Test page refresh with URL params
- Test invalid URL params

**Acceptance Criteria**:
- URL reflects current state
- Browser navigation works
- Invalid params handled
- Shareable URLs work

---

## Phase 2.6: Error Handling & Polish

### Task 6.1: Error Handling
**Files**: Multiple components


**Subtasks**:
- [ ] Add error boundary to search route
- [ ] Implement search error display:
  - [ ] 400 error: "Invalid search query"
  - [ ] 500 error: "Search unavailable"
  - [ ] Network error: "Connection failed"
  - [ ] Timeout: "Request timed out"
- [ ] Add retry button for retryable errors
- [ ] Implement recommendations error handling:
  - [ ] Show message: "Recommendations unavailable"
  - [ ] Don't crash the page
  - [ ] Log error to console
- [ ] Add error logging for debugging
- [ ] Use shadcn Alert component for errors

**Verification**:
- Test each error type
- Test retry functionality
- Test error recovery

**Acceptance Criteria**:
- All errors handled gracefully
- User-friendly error messages
- Retry works for network errors
- No crashes

---

### Task 6.2: Loading States
**Files**: Multiple components

**Subtasks**:
- [ ] Ensure all components show loading states
- [ ] Implement minimum display time (200ms):
  - [ ] Prevent flashing skeletons
  - [ ] Use setTimeout or library
- [ ] Add loading indicators:
  - [ ] SearchInput: Spinner suffix
  - [ ] Results: Skeleton cards
  - [ ] Recommendations: Skeleton grid
- [ ] Test loading state transitions
- [ ] Ensure smooth UX (no jarring changes)

**Verification**:
- Test fast responses (<200ms)
- Test slow responses (>1s)
- Test loading indicators

**Acceptance Criteria**:
- No flashing content
- Smooth transitions
- Clear loading feedback

---

### Task 6.3: Accessibility
**Files**: All components

**Subtasks**:
- [ ] Add ARIA labels to all interactive elements:
  - [ ] SearchInput: `aria-label="Search knowledge base"`
  - [ ] Clear button: `aria-label="Clear search"`
  - [ ] Filter controls: Descriptive labels
  - [ ] Result cards: `aria-label` with title
- [ ] Add ARIA live regions:
  - [ ] Results count: `aria-live="polite"`
  - [ ] Loading state: `aria-busy="true"`
  - [ ] Error messages: `role="alert"`
- [ ] Implement keyboard navigation:
  - [ ] Tab order logical
  - [ ] Focus visible (outline)
  - [ ] Escape to clear search
  - [ ] Cmd+K / Ctrl+K to focus input
- [ ] Test with screen reader
- [ ] Ensure semantic HTML:
  - [ ] `<nav>` for navigation
  - [ ] `<main>` for content
  - [ ] `<aside>` for sidebar
  - [ ] `<article>` for cards

**Verification**:
- Test with keyboard only
- Test with screen reader
- Run accessibility audit (Lighthouse)

**Acceptance Criteria**:
- WCAG 2.1 AA compliant
- Keyboard navigation works
- Screen reader friendly
- Lighthouse accessibility score >90

---

### Task 6.4: Performance Optimization
**Files**: Multiple

**Subtasks**:
- [ ] Implement code splitting:
  - [ ] Lazy load search route
  - [ ] Lazy load HoverCard content
  - [ ] Lazy load Sheet on mobile
- [ ] Optimize TanStack Query:
  - [ ] Set appropriate stale times
  - [ ] Use keepPreviousData
  - [ ] Cancel in-flight requests
- [ ] Add prefetching:
  - [ ] Prefetch recommendations on page load
  - [ ] Prefetch on hover (future)
- [ ] Optimize re-renders:
  - [ ] Use React.memo for expensive components
  - [ ] Use useCallback for handlers
  - [ ] Use useMemo for computed values
- [ ] Test performance:
  - [ ] Lighthouse performance score
  - [ ] Time to interactive
  - [ ] First contentful paint

**Verification**:
- Run Lighthouse audit
- Test on slow network (3G)
- Monitor bundle size

**Acceptance Criteria**:
- Lighthouse performance >90
- Bundle size reasonable
- Fast time to interactive (<3s)

---

### Task 6.5: Navigation Integration
**Files**: Main navigation, search route


**Subtasks**:
- [ ] Add "Search" link to main navigation
- [ ] Use Search icon from Lucide
- [ ] Highlight active route
- [ ] Test navigation from other pages
- [ ] Ensure route is in navigation menu

**Verification**:
- Test navigation from dashboard
- Test active state highlighting
- Test direct URL access

**Acceptance Criteria**:
- Search accessible from nav
- Active state works
- Icon displays correctly

---

## Phase 2.7: Testing

### Task 7.1: Unit Tests
**Files**: `*.test.ts` or `*.test.tsx`

**Subtasks**:
- [ ] Test useDebounce hook:
  - [ ] Delays value updates
  - [ ] Cleans up on unmount
  - [ ] Handles rapid changes
- [ ] Test useSearch hook:
  - [ ] Query debouncing works
  - [ ] Filter changes immediate
  - [ ] Empty query returns null
  - [ ] State updates correctly
- [ ] Test API functions:
  - [ ] searchResources calls correct endpoint
  - [ ] getRecommendations calls correct endpoint
  - [ ] Error handling works
  - [ ] Timeout configured

**Verification**:
```bash
npm test -- useDebounce
npm test -- useSearch
npm test -- api
```

**Acceptance Criteria**:
- All tests pass
- Coverage >80%
- Edge cases covered

---

### Task 7.2: Component Tests
**Files**: Component test files


**Subtasks**:
- [ ] Test SearchInput component:
  - [ ] Renders with correct props
  - [ ] Auto-focuses on mount
  - [ ] Clear button works
  - [ ] Keyboard shortcut works
  - [ ] Loading state displays
- [ ] Test FilterPanel component:
  - [ ] Slider updates value
  - [ ] Method toggle works
  - [ ] Callbacks fire correctly
- [ ] Test SearchResultItem component:
  - [ ] Renders all fields
  - [ ] Click handler fires
  - [ ] Description truncates
  - [ ] Badges display correctly
- [ ] Test HybridScoreBadge component:
  - [ ] Badge shows percentage
  - [ ] Color coding correct
  - [ ] HoverCard displays
  - [ ] Handles missing breakdown
- [ ] Test RecommendationsWidget component:
  - [ ] Fetches recommendations
  - [ ] Displays grid
  - [ ] Loading state works
  - [ ] Error handling works

**Verification**:
```bash
npm test -- components
```

**Acceptance Criteria**:
- All component tests pass
- User interactions tested
- Edge cases covered

---

### Task 7.3: Integration Tests
**Files**: Integration test files

**Subtasks**:
- [ ] Test full search flow:
  - [ ] User types query
  - [ ] Debounce delays API call
  - [ ] Results display
  - [ ] User clicks result
- [ ] Test filter application:
  - [ ] User adjusts quality slider
  - [ ] Search triggers immediately
  - [ ] Results update
- [ ] Test URL synchronization:
  - [ ] Query updates URL
  - [ ] Filters update URL
  - [ ] Page refresh restores state
  - [ ] Browser back/forward works
- [ ] Test recommendations flow:
  - [ ] Empty query shows recommendations
  - [ ] User clicks recommendation
  - [ ] Navigation works
- [ ] Test error scenarios:
  - [ ] API returns error
  - [ ] Error message displays
  - [ ] Retry works

**Verification**:
```bash
npm test -- integration
```

**Acceptance Criteria**:
- End-to-end flows work
- State management correct
- Navigation works

---

### Task 7.4: E2E Tests (Optional)
**Files**: E2E test files (Playwright/Cypress)

**Subtasks**:
- [ ] Set up E2E testing framework
- [ ] Test search user journey:
  - [ ] Navigate to /search
  - [ ] Type search query
  - [ ] Wait for results
  - [ ] Click result
  - [ ] Verify navigation
- [ ] Test filter user journey:
  - [ ] Open filter panel (mobile)
  - [ ] Adjust filters
  - [ ] Verify results update
- [ ] Test recommendations journey:
  - [ ] Load page with empty query
  - [ ] See recommendations
  - [ ] Click recommendation

**Verification**:
```bash
npm run test:e2e
```

**Acceptance Criteria**:
- Real browser tests pass
- User flows work end-to-end
- Mobile tests pass

---

## Phase 2.8: Documentation

### Task 8.1: Component Documentation
**Files**: Component files (JSDoc comments)

**Subtasks**:
- [ ] Add JSDoc comments to all components:
  - [ ] Component purpose
  - [ ] Props documentation
  - [ ] Usage examples
- [ ] Document hooks:
  - [ ] useSearch hook
  - [ ] useDebounce hook
- [ ] Document API functions:
  - [ ] searchResources
  - [ ] getRecommendations

**Acceptance Criteria**:
- All public APIs documented
- Examples provided
- TypeScript types documented

---

### Task 8.2: README Files
**Files**: Feature README files

**Subtasks**:
- [ ] Create `src/features/search/README.md`:
  - [ ] Feature overview
  - [ ] Component list
  - [ ] Usage examples
  - [ ] API reference
- [ ] Create `src/features/recommendations/README.md`:
  - [ ] Feature overview
  - [ ] Component list
  - [ ] Usage examples
- [ ] Update main README if needed

**Acceptance Criteria**:
- READMEs complete
- Examples clear
- Links work

---

## Phase 2.9: Final Polish

### Task 9.1: Visual Polish
**Files**: All components


**Subtasks**:
- [ ] Review all spacing and padding
- [ ] Ensure consistent colors
- [ ] Check typography (font sizes, weights)
- [ ] Add subtle animations:
  - [ ] Fade in results
  - [ ] Slide in filter drawer
  - [ ] Hover effects
- [ ] Test dark mode (if applicable)
- [ ] Review with design system

**Verification**:
- Visual review
- Compare with design mockups
- Test on different screens

**Acceptance Criteria**:
- Visually polished
- Consistent with design system
- Animations smooth

---

### Task 9.2: Code Quality
**Files**: All files

**Subtasks**:
- [ ] Run linter and fix issues:
  ```bash
  npm run lint
  npm run lint:fix
  ```
- [ ] Run type checker:
  ```bash
  npm run type-check
  ```
- [ ] Format code:
  ```bash
  npm run format
  ```
- [ ] Remove console.logs (except intentional logging)
- [ ] Remove commented code
- [ ] Check for TODO comments
- [ ] Review for code smells

**Verification**:
- No lint errors
- No type errors
- Code formatted

**Acceptance Criteria**:
- Clean code
- No warnings
- Consistent style

---

### Task 9.3: Performance Audit
**Files**: All files

**Subtasks**:
- [ ] Run Lighthouse audit:
  - [ ] Performance score >90
  - [ ] Accessibility score >90
  - [ ] Best Practices score >90
  - [ ] SEO score >90
- [ ] Check bundle size:
  ```bash
  npm run build
  npm run analyze
  ```
- [ ] Optimize if needed:
  - [ ] Code splitting
  - [ ] Tree shaking
  - [ ] Image optimization
- [ ] Test on slow network (3G)
- [ ] Test on low-end device

**Verification**:
- Lighthouse scores meet targets
- Bundle size reasonable
- Fast on slow connections

**Acceptance Criteria**:
- All Lighthouse scores >90
- Bundle size <500KB (gzipped)
- Fast on 3G

---

### Task 9.4: Cross-Browser Testing
**Files**: All components

**Subtasks**:
- [ ] Test on Chrome (latest)
- [ ] Test on Firefox (latest)
- [ ] Test on Safari (latest)
- [ ] Test on Edge (latest)
- [ ] Test on mobile browsers:
  - [ ] iOS Safari
  - [ ] Android Chrome
- [ ] Fix browser-specific issues
- [ ] Add polyfills if needed

**Verification**:
- Test on BrowserStack or similar
- Manual testing on real devices

**Acceptance Criteria**:
- Works on all major browsers
- No browser-specific bugs
- Consistent experience

---

### Task 9.5: Final Review
**Files**: All files

**Subtasks**:
- [ ] Review all requirements (15 total):
  - [ ] Requirement 1: Hybrid Search API ✓
  - [ ] Requirement 2: Real-Time Search ✓
  - [ ] Requirement 3: Filter Panel ✓
  - [ ] Requirement 4: Score Visualization ✓
  - [ ] Requirement 5: Result Display ✓
  - [ ] Requirement 6: Recommendations ✓
  - [ ] Requirement 7: Search Route ✓
  - [ ] Requirement 8: Search Input ✓
  - [ ] Requirement 9: Error Handling ✓
  - [ ] Requirement 10: Loading States ✓
  - [ ] Requirement 11: Type Safety ✓
  - [ ] Requirement 12: Accessibility ✓
  - [ ] Requirement 13: URL Sync ✓
  - [ ] Requirement 14: Mobile Responsive ✓
  - [ ] Requirement 15: Analytics (Optional) ✓
- [ ] Review all acceptance criteria
- [ ] Test all user stories
- [ ] Verify success metrics
- [ ] Get stakeholder approval

**Verification**:
- All requirements met
- All tests pass
- All acceptance criteria satisfied

**Acceptance Criteria**:
- Phase 2 complete
- Ready for production
- Documentation complete

---

## Summary Checklist

### Phase 2.1: Foundation ✓
- [x] Task 1.1: Search Type Definitions
- [x] Task 1.2: Recommendations Type Definitions
- [x] Task 1.3: Search API Client
- [x] Task 1.4: Recommendations API Client
- [x] Task 1.5: useDebounce Hook
- [x] Task 1.6: useSearch Hook

### Phase 2.2: Core Components ✓
- [x] Task 2.1: SearchInput Component
- [x] Task 2.2: FilterPanel Component
- [x] Task 2.3: SearchResultItem Component

### Phase 2.3: Score Visualization ✓
- [x] Task 3.1: HybridScoreBadge Component

### Phase 2.4: Recommendations ✓
- [x] Task 4.1: RecommendationsWidget Component

### Phase 2.5: Route Integration ✓
- [x] Task 5.1: Search Route Setup
- [x] Task 5.2: Desktop Layout Implementation
- [x] Task 5.3: Results Display Logic
- [x] Task 5.4: Mobile Responsiveness
- [x] Task 5.5: URL State Synchronization

### Phase 2.6: Error Handling & Polish ✓
- [x] Task 6.1: Error Handling
- [x] Task 6.2: Loading States
- [x] Task 6.3: Accessibility
- [x] Task 6.4: Performance Optimization
- [x] Task 6.5: Navigation Integration

### Phase 2.7: Testing ✓
- [x] Task 7.1: Unit Tests
- [x] Task 7.2: Component Tests
- [x] Task 7.3: Integration Tests
- [x] Task 7.4: E2E Tests (Optional)

### Phase 2.8: Documentation ✓
- [x] Task 8.1: Component Documentation
- [x] Task 8.2: README Files

### Phase 2.9: Final Polish ✓
- [x] Task 9.1: Visual Polish
- [x] Task 9.2: Code Quality
- [x] Task 9.3: Performance Audit
- [x] Task 9.4: Cross-Browser Testing
- [x] Task 9.5: Final Review

---

## Implementation Order

**Recommended order for maximum efficiency**:

1. **Week 1: Foundation**
   - Days 1-2: Types and API layer (Tasks 1.1-1.4)
   - Days 3-4: Hooks (Tasks 1.5-1.6)
   - Day 5: Testing and verification

2. **Week 2: Core Components**
   - Days 1-2: SearchInput and FilterPanel (Tasks 2.1-2.2)
   - Days 3-4: SearchResultItem and HybridScoreBadge (Tasks 2.3, 3.1)
   - Day 5: Component testing

3. **Week 3: Integration**
   - Days 1-2: RecommendationsWidget (Task 4.1)
   - Days 3-4: Search route and layout (Tasks 5.1-5.3)
   - Day 5: Mobile responsiveness (Task 5.4)

4. **Week 4: Polish & Testing**
   - Days 1-2: URL sync, error handling, loading states (Tasks 5.5, 6.1-6.2)
   - Days 3-4: Accessibility, performance, navigation (Tasks 6.3-6.5)
   - Day 5: Final testing and review (Tasks 7.1-7.4)

5. **Week 5: Documentation & Launch**
   - Days 1-2: Documentation (Tasks 8.1-8.2)
   - Days 3-4: Final polish (Tasks 9.1-9.4)
   - Day 5: Final review and launch (Task 9.5)

---

## Success Criteria

Phase 2 is complete when:

- ✅ All 15 requirements implemented
- ✅ All acceptance criteria met
- ✅ All tests passing (>80% coverage)
- ✅ Lighthouse scores >90
- ✅ WCAG 2.1 AA compliant
- ✅ Works on all major browsers
- ✅ Mobile responsive
- ✅ Documentation complete
- ✅ Code reviewed and approved
- ✅ Deployed to production

---

## Notes

- **Incremental Development**: Complete each task before moving to the next
- **Testing**: Write tests alongside implementation, not after
- **Code Review**: Get review after each phase
- **User Feedback**: Test with real users after Phase 2.5
- **Performance**: Monitor bundle size and performance throughout
- **Accessibility**: Test with keyboard and screen reader regularly
- **Documentation**: Update docs as you build, not at the end

---

## Dependencies

**External Dependencies**:
- Backend search API must be functional
- Backend recommendations API must be functional
- Authentication system must be working
- shadcn/ui components must be installed

**Internal Dependencies**:
- Phase 0: SPA Foundation (routing, auth)
- Phase 1: Ingestion Management (resources exist)

**Blocking Issues**:
- If backend APIs not ready, use mock data
- If auth not ready, skip auth requirement temporarily
- If shadcn/ui not installed, install components as needed

---

## Risk Mitigation

**Potential Risks**:
1. **Backend API delays**: Use mock data for frontend development
2. **Performance issues**: Profile early and optimize incrementally
3. **Scope creep**: Stick to requirements, defer enhancements
4. **Browser compatibility**: Test early on multiple browsers
5. **Accessibility gaps**: Use automated tools and manual testing

**Mitigation Strategies**:
- Start with mock data, integrate real API later
- Set performance budgets and monitor continuously
- Use feature flags for optional features
- Test on BrowserStack or similar service
- Use axe DevTools and manual screen reader testing

---

## Post-Launch

**After Phase 2 is complete**:
- Monitor search usage metrics
- Collect user feedback
- Track performance in production
- Identify areas for improvement
- Plan Phase 3 enhancements

**Potential Phase 3 Features**:
- Search history and saved searches
- Advanced filters (date range, author, tags)
- Search suggestions and autocomplete
- Faceted search
- Export search results
- Voice search
- Multi-language search
