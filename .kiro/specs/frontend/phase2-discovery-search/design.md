# Design Document - Phase 2: Discovery & Search

## Architecture Overview

Phase 2 implements a sophisticated search and discovery system using React, TypeScript, TanStack Query, and shadcn/ui. The architecture follows a feature-based structure with clear separation of concerns.

```
src/
├── features/
│   ├── search/
│   │   ├── api.ts                    # Search API client
│   │   ├── types.ts                  # TypeScript interfaces
│   │   ├── hooks/
│   │   │   ├── useSearch.ts          # Main search state machine
│   │   │   └── useDebounce.ts        # Debounce utility hook
│   │   └── components/
│   │       ├── SearchInput.tsx       # Large search input field
│   │       ├── FilterPanel.tsx       # Quality + Method filters
│   │       ├── SearchResultItem.tsx  # Individual result card
│   │       └── HybridScoreBadge.tsx  # Score visualization
│   └── recommendations/
│       ├── api.ts                    # Recommendations API client
│       ├── types.ts                  # TypeScript interfaces
│       └── components/
│           └── RecommendationsWidget.tsx  # "For You" feed
├── routes/
│   └── _auth.search.tsx              # Main search route
└── lib/
    └── hooks/
        └── useDebounce.ts            # Shared debounce hook
```

## Technical Stack

### Core Technologies
- **React 18**: UI library with hooks and concurrent features
- **TypeScript 5**: Type safety and developer experience
- **TanStack Query v5**: Server state management, caching, and data fetching
- **React Router 6**: Client-side routing with URL state sync
- **Vite 5**: Build tool and dev server

### UI Components
- **shadcn/ui**: Headless component library
  - Slider: Quality score filter
  - Badge: Status and score indicators
  - HoverCard: Score breakdown tooltip
  - Skeleton: Loading states
  - Separator: Visual dividers
  - Switch: Search method toggle
  - Sheet: Mobile filter drawer
  - Card: Result containers
  - Input: Search field
  - Alert: Error messages

### Icons
- **Lucide React**: Icon library
  - Search: Search input and keyword indicator
  - SlidersHorizontal: Filter panel toggle
  - Sparkles: Semantic search and recommendations
  - BookOpen: Book resource type
  - FileText: Article resource type
  - Globe: Website resource type
  - X: Clear button

## Data Flow

### Search Flow
```
User Input → Debounce (300ms) → useSearch Hook → TanStack Query → API Call → Results → UI Update
                                      ↓
                                 URL Sync (query params)
```

### Filter Flow
```
Filter Change → useSearch Hook → Immediate API Call (no debounce) → Results → UI Update
                                      ↓
                                 URL Sync (query params)
```

### Recommendations Flow
```
Page Load → useQuery (recommendations) → API Call → Cache (10min) → Display when query empty
```

## Component Design

### 1. SearchInput Component

**Purpose**: Large, prominent search input with real-time feedback

**Props**:
```typescript
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  isLoading: boolean;
  placeholder?: string;
}
```

**Features**:
- Auto-focus on mount
- Keyboard shortcut (Cmd+K / Ctrl+K)
- Clear button when value exists
- Loading spinner during search
- Search icon prefix
- 48px height for prominence

**State Management**:
- Controlled component (value from useSearch hook)
- Debounced onChange handler
- Focus management with useRef

### 2. FilterPanel Component

**Purpose**: Sidebar with quality and search method filters

**Props**:
```typescript
interface FilterPanelProps {
  filters: SearchFilters;
  onFilterChange: (key: string, value: any) => void;
  isMobile?: boolean;
}
```

**Features**:
- Quality Score slider (0-100, mapped to 0.0-1.0)
- Current value display ("Min Quality: 0.7")
- Search Method toggle (Hybrid / Semantic)
- Responsive layout (sidebar on desktop, drawer on mobile)
- Visual separators between sections

**State Management**:
- Controlled by useSearch hook
- Immediate updates (no debounce)
- URL sync for shareability

### 3. SearchResultItem Component

**Purpose**: Display individual search result with metadata

**Props**:
```typescript
interface SearchResultItemProps {
  result: SearchResult;
  onClick: (id: string) => void;
}
```

**Features**:
- Title (bold, 18px, clickable)
- Description (2-line clamp with ellipsis)
- Resource type badge (color-coded)
- Quality score indicator
- HybridScoreBadge with breakdown
- Created date
- Hover effect (shadow/border)
- Click to navigate to /resources/{id}

**Layout**:
```
┌─────────────────────────────────────────┐
│ [Icon] Title (Bold)          [Score 92%]│
│                                          │
│ Description text clamped to two lines... │
│                                          │
│ [Article] Quality: 0.85  Jan 8, 2026    │
└─────────────────────────────────────────┘
```

### 4. HybridScoreBadge Component

**Purpose**: Visualize search relevance with breakdown

**Props**:
```typescript
interface HybridScoreBadgeProps {
  score: number;
  breakdown?: ScoreBreakdown;
}
```

**Features**:
- Display composite score as percentage (92%)
- Color coding: >80% (Green), 60-80% (Yellow), <60% (Gray)
- HoverCard with detailed breakdown
- Breakdown shows: Semantic Match, Keyword Match, Composite
- Visual indicators (progress bars or colored dots)
- Icons for each score type (Sparkles, Search)

**Breakdown Layout**:
```
┌─────────────────────────────────┐
│ Score Breakdown                 │
│                                 │
│ ✨ Semantic Match:    85%       │
│ ████████████████░░░░             │
│                                 │
│ 🔍 Keyword Match:     40%       │
│ ████████░░░░░░░░░░░░             │
│                                 │
│ 📊 Composite Score:   92%       │
│ ██████████████████░░             │
└─────────────────────────────────┘
```

### 5. RecommendationsWidget Component

**Purpose**: Display personalized "For You" feed

**Props**:
```typescript
interface RecommendationsWidgetProps {
  onResourceClick: (id: string) => void;
}
```

**Features**:
- Section header "For You" with Sparkles icon
- Grid layout (2 columns desktop, 1 mobile)
- Recommendation cards with title, description, reason
- Reason badge (e.g., "Similar to X", "Popular in Y")
- Skeleton loaders during fetch
- Only visible when search query is empty

**Layout**:
```
┌─────────────────────────────────────────┐
│ ✨ For You                              │
│                                         │
│ ┌──────────────┐  ┌──────────────┐    │
│ │ Card 1       │  │ Card 2       │    │
│ │ Title        │  │ Title        │    │
│ │ Description  │  │ Description  │    │
│ │ [Similar]    │  │ [Popular]    │    │
│ └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

## State Management

### useSearch Hook

**Purpose**: Central state machine for search functionality

**Return Type**:
```typescript
interface UseSearchReturn {
  query: string;
  filters: SearchFilters;
  results: SearchResult[] | null;
  isLoading: boolean;
  error: Error | null;
  setQuery: (query: string) => void;
  setFilter: (key: string, value: any) => void;
  clearFilters: () => void;
}
```

**Implementation Strategy**:

1. **State Management**:
   - Use `useState` for query and filters
   - Use `useDebounce` for query (300ms delay)
   - Use TanStack Query for API calls and caching

2. **Debounce Logic**:
   ```typescript
   const debouncedQuery = useDebounce(query, 300);
   ```

3. **Query Execution**:
   ```typescript
   const { data, isLoading, error } = useQuery({
     queryKey: ['search', debouncedQuery, filters],
     queryFn: () => searchResources({ 
       text: debouncedQuery, 
       ...filters 
     }),
     enabled: debouncedQuery.length > 0,
     staleTime: 5 * 60 * 1000, // 5 minutes
     keepPreviousData: true,
   });
   ```

4. **Filter Updates**:
   - Immediate execution (no debounce)
   - Invalidate query cache on filter change
   - Sync to URL query parameters

5. **URL Synchronization**:
   ```typescript
   const [searchParams, setSearchParams] = useSearchParams();
   
   useEffect(() => {
     setSearchParams({
       q: query,
       quality: filters.min_quality.toString(),
       method: filters.search_method,
     });
   }, [query, filters]);
   ```

### useDebounce Hook

**Purpose**: Delay execution of rapid updates

**Implementation**:
```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

## API Layer

### Search API

**Endpoint**: `POST /api/v1/search`

**Request**:
```typescript
interface SearchRequest {
  text: string;
  hybrid_weight: number;  // 0.0-1.0
  filters: {
    min_quality?: number;  // 0.0-1.0
    resource_types?: string[];
    classification_codes?: string[];
  };
  limit: number;  // Default: 20
}
```

**Response**:
```typescript
interface SearchResult {
  id: string;
  title: string;
  description: string;
  score: number;
  scores_breakdown: {
    semantic_score: number;
    keyword_score: number;
    composite_score: number;
  };
  resource_type: string;
  quality_score: number;
  created_at: string;
  classification_code?: string;
}
```

**Error Handling**:
- 400: Invalid query → Display "Invalid search query"
- 500: Server error → Display "Search unavailable"
- Network timeout (10s) → Display "Request timed out"

### Recommendations API

**Endpoint**: `GET /api/v1/recommendations`

**Query Parameters**:
```typescript
interface RecommendationsParams {
  limit?: number;  // Default: 10
  user_id?: string;  // Optional for personalization
}
```

**Response**:
```typescript
interface Recommendation {
  id: string;
  title: string;
  description: string;
  reason: string;  // "Similar to X", "Popular in Y"
  resource_type: string;
  quality_score: number;
  created_at: string;
}
```

**Caching Strategy**:
- Stale time: 10 minutes
- Cache key: `['recommendations', userId]`
- Prefetch on page load

## Routing

### Search Route

**Path**: `/search`

**Layout**: `_auth` (requires authentication)

**Component Structure**:
```tsx
<div className="flex h-screen">
  {/* Desktop Sidebar */}
  <aside className="hidden md:block w-[280px] border-r">
    <FilterPanel />
  </aside>

  {/* Main Content */}
  <main className="flex-1 flex flex-col">
    {/* Search Input */}
    <div className="p-6 border-b">
      <SearchInput />
    </div>

    {/* Results Area */}
    <div className="flex-1 overflow-y-auto p-6">
      {isLoading && <SkeletonResults />}
      {!query && <RecommendationsWidget />}
      {query && results.length > 0 && (
        <div className="space-y-4">
          {results.map(result => (
            <SearchResultItem key={result.id} result={result} />
          ))}
        </div>
      )}
      {query && results.length === 0 && <EmptyState />}
    </div>
  </main>

  {/* Mobile Filter Button */}
  <Sheet>
    <SheetTrigger className="md:hidden">
      <Button variant="outline">
        <SlidersHorizontal /> Filters
      </Button>
    </SheetTrigger>
    <SheetContent>
      <FilterPanel isMobile />
    </SheetContent>
  </Sheet>
</div>
```

## Type Definitions

### Core Types

```typescript
// src/features/search/types.ts

export enum SearchMethod {
  Hybrid = 'hybrid',
  Semantic = 'semantic',
}

export interface SearchFilters {
  min_quality: number;  // 0.0-1.0
  search_method: SearchMethod;
  resource_types?: string[];
  classification_codes?: string[];
}

export interface SearchRequest {
  text: string;
  hybrid_weight: number;
  filters: Partial<SearchFilters>;
  limit: number;
}

export interface ScoreBreakdown {
  semantic_score: number;
  keyword_score: number;
  composite_score: number;
}

export interface SearchResult {
  id: string;
  title: string;
  description: string;
  score: number;
  scores_breakdown?: ScoreBreakdown;
  resource_type: string;
  quality_score: number;
  created_at: string;
  classification_code?: string;
}

export interface SearchState {
  query: string;
  filters: SearchFilters;
  results: SearchResult[] | null;
  isLoading: boolean;
  error: Error | null;
}
```

### Recommendations Types

```typescript
// src/features/recommendations/types.ts

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  reason: string;
  resource_type: string;
  quality_score: number;
  created_at: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  total: number;
}
```

## Performance Optimizations

### 1. Debouncing
- Search input: 300ms delay
- Prevents excessive API calls
- Cancels in-flight requests

### 2. Caching
- Search results: 5-minute stale time
- Recommendations: 10-minute stale time
- Query key includes all parameters

### 3. Prefetching
- Prefetch recommendations on page load
- Prefetch next page of results (future)

### 4. Code Splitting
- Lazy load search route
- Lazy load filter panel on mobile
- Lazy load HoverCard content

### 5. Optimistic Updates
- Show previous results during refetch
- Use `keepPreviousData` option
- Prevent layout shift

### 6. Skeleton Loaders
- Minimum 200ms display time
- Prevent flashing
- Match result card layout

## Accessibility

### Keyboard Navigation
- Tab: Navigate between elements
- Cmd+K / Ctrl+K: Focus search input
- Escape: Clear search query
- Arrow keys: Navigate results (future)
- Enter: Open selected result (future)

### ARIA Labels
- Search input: `aria-label="Search knowledge base"`
- Filter panel: `aria-label="Search filters"`
- Results: `aria-live="polite"` for result count
- Loading: `aria-busy="true"`

### Semantic HTML
- `<nav>` for navigation
- `<main>` for content area
- `<aside>` for filter panel
- `<article>` for result cards

### Focus Management
- Auto-focus search input on load
- Return focus to input after clearing
- Trap focus in mobile filter drawer

## Error Handling

### Error Types
```typescript
enum SearchErrorType {
  InvalidQuery = 'INVALID_QUERY',
  ServerError = 'SERVER_ERROR',
  NetworkError = 'NETWORK_ERROR',
  Timeout = 'TIMEOUT',
}

interface SearchError {
  type: SearchErrorType;
  message: string;
  retryable: boolean;
}
```

### Error Display
- Alert component for critical errors
- Toast for transient errors
- Inline message for validation errors
- Retry button for retryable errors

### Error Recovery
- Automatic retry for network errors (3 attempts)
- Exponential backoff (1s, 2s, 4s)
- Fallback to cached results if available
- Graceful degradation (show recommendations)

## Mobile Responsiveness

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Mobile Layout
- Stack vertically (no sidebar)
- Filter panel in Sheet (slide-in drawer)
- Full-width search input
- Single-column results
- Touch-friendly tap targets (44x44px)

### Tablet Layout
- Collapsible sidebar
- 2-column recommendations grid
- Larger search input

### Desktop Layout
- Fixed sidebar (280px)
- 3-column recommendations grid
- Spacious layout

## Testing Strategy

### Unit Tests
- useSearch hook logic
- useDebounce hook
- API functions
- Type guards and validators

### Component Tests
- SearchInput interactions
- FilterPanel state changes
- SearchResultItem rendering
- HybridScoreBadge tooltip

### Integration Tests
- Full search flow (input → results)
- Filter application
- URL synchronization
- Error handling

### E2E Tests
- User searches and finds resource
- User applies filters
- User clicks recommendation
- Mobile filter drawer

## Security Considerations

### Input Validation
- Sanitize search queries (XSS prevention)
- Validate filter values (range checks)
- Escape special characters in URLs

### API Security
- Use HTTPS for all requests
- Include authentication tokens
- Implement rate limiting
- Validate response schemas

### Data Privacy
- Anonymize analytics data
- No PII in logs
- Secure token storage
- GDPR compliance

## Future Enhancements

### Phase 3 (Future)
- Search history and saved searches
- Advanced filters (date range, author, tags)
- Faceted search (category filters)
- Search suggestions and autocomplete
- Export search results
- Voice search
- Multi-language search

### Performance
- Virtual scrolling for large result sets
- Infinite scroll pagination
- Service worker for offline search
- IndexedDB for local caching

### Analytics
- Search analytics dashboard
- A/B testing for search algorithms
- User behavior tracking
- Search quality metrics

## Dependencies

### Required Packages
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.17.0",
    "lucide-react": "^0.300.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

### shadcn/ui Components
```bash
npx shadcn-ui@latest add slider
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add hover-card
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add alert
```

## Implementation Phases

### Phase 2.1: Foundation (Step 1-2)
- Type definitions
- API layer
- useDebounce hook
- useSearch hook

### Phase 2.2: Core Components (Step 3-4)
- SearchInput
- FilterPanel
- HybridScoreBadge
- SearchResultItem

### Phase 2.3: Integration (Step 5)
- Search route
- Layout and responsive design
- URL synchronization
- Error handling

### Phase 2.4: Recommendations
- RecommendationsWidget
- API integration
- Conditional display logic

### Phase 2.5: Polish
- Loading states
- Empty states
- Accessibility
- Mobile optimization
- Performance tuning

## Success Criteria

- All 15 requirements met
- TypeScript strict mode with no errors
- 80%+ test coverage
- Lighthouse score > 90
- WCAG 2.1 AA compliance
- P95 search latency < 500ms
- Zero console errors
- Mobile-friendly (responsive design)
