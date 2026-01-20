# Search Feature

Advanced hybrid search interface with semantic and keyword search capabilities.

## Overview

The search feature provides a sophisticated search experience combining:
- **Hybrid Search**: Blends semantic (AI-powered) and keyword matching
- **Real-time Results**: Debounced search with instant feedback
- **Advanced Filters**: Quality score and search method filters
- **Score Visualization**: Detailed breakdown of search relevance scores
- **URL State Sync**: Shareable search URLs with query parameters

## Architecture

```
search/
├── api.ts                    # Search API client
├── types.ts                  # TypeScript interfaces
├── index.ts                  # Public exports
├── hooks/
│   └── useSearch.ts          # Main search state machine
├── components/
│   ├── SearchInput.tsx       # Search input with shortcuts
│   ├── FilterPanel.tsx       # Quality and method filters
│   ├── SearchResultItem.tsx  # Individual result card
│   └── HybridScoreBadge.tsx  # Score visualization
└── __tests__/                # Unit tests
```

## Components

### SearchInput

Large, prominent search input with real-time feedback.

**Features**:
- Auto-focus on mount
- Keyboard shortcut (Cmd+K / Ctrl+K)
- Clear button
- Loading indicator
- ARIA labels for accessibility

**Usage**:
```tsx
import { SearchInput } from '@/features/search';

<SearchInput
  value={query}
  onChange={setQuery}
  onClear={() => setQuery('')}
  isLoading={isLoading}
/>
```

### FilterPanel

Sidebar with quality score and search method filters.

**Features**:
- Quality score slider (0-100%)
- Search method toggle (Hybrid/Semantic)
- Real-time filter application
- Mobile-responsive layout

**Usage**:
```tsx
import { FilterPanel } from '@/features/search';

<FilterPanel
  filters={filters}
  method={method}
  onFilterChange={setFilter}
  onMethodChange={setMethod}
/>
```

### SearchResultItem

Display individual search result with metadata.

**Features**:
- Resource type badges with color coding
- Quality and match scores
- Description truncation (2 lines)
- Tags display
- Hover effects
- Click navigation

**Usage**:
```tsx
import { SearchResultItem } from '@/features/search';

<SearchResultItem
  result={result}
  onClick={(id) => navigate(`/resources/${id}`)}
/>
```

### HybridScoreBadge

Score visualization with hover breakdown.

**Features**:
- Color-coded badges (green >80%, yellow 60-80%, gray <60%)
- Hover tooltip with score breakdown
- Progress bars for semantic, keyword, and composite scores
- Handles missing breakdown data

**Usage**:
```tsx
import { HybridScoreBadge } from '@/features/search';

<HybridScoreBadge
  score={result.score}
  breakdown={result.scores_breakdown}
/>
```

## Hooks

### useSearch

Core state machine for search functionality.

**Features**:
- Query debouncing (300ms)
- Filter state management
- TanStack Query integration
- URL state synchronization
- Error handling

**Usage**:
```tsx
import { useSearch } from '@/features/search';

function SearchPage() {
  const {
    query,
    filters,
    method,
    results,
    isLoading,
    error,
    setQuery,
    setFilter,
    setMethod,
    clearFilters,
  } = useSearch();

  // Use search state...
}
```

**Return Values**:
- `query`: Current search query string
- `filters`: Active filters (min_quality, etc.)
- `method`: Search method ('hybrid' | 'semantic')
- `results`: Search results array or null
- `isLoading`: Loading state boolean
- `error`: Error object or null
- `setQuery`: Update query function
- `setFilter`: Update filter function
- `setMethod`: Update method function
- `clearFilters`: Reset filters function

## API

### searchResources

Search resources using hybrid search.

**Parameters**:
```typescript
interface SearchRequest {
  text: string;
  hybrid_weight?: number;  // 0.0-1.0, default 0.7
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
}
```

**Returns**:
```typescript
Promise<SearchResult[]>
```

**Error Handling**:
- 400: Invalid search query
- 500: Search service unavailable
- Network: Connection failed
- Timeout: Request timed out (10s)

## Types

### SearchResult

```typescript
interface SearchResult {
  id: number;
  title: string;
  description: string;
  content?: string;
  url?: string;
  resource_type: string;
  score: number;
  scores_breakdown?: ScoreBreakdown;
  quality_score?: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
}
```

### ScoreBreakdown

```typescript
interface ScoreBreakdown {
  semantic_score?: number;
  keyword_score?: number;
  content_match?: number;
  metadata_match?: number;
}
```

### SearchFilters

```typescript
interface SearchFilters {
  min_quality?: number;  // 0.0-1.0
  resource_type?: string[];
  tags?: string[];
}
```

## Testing

Run tests:
```bash
npm test -- search
```

Test coverage:
```bash
npm test -- search --coverage
```

## Performance

- **Query Debouncing**: 300ms delay to reduce API calls
- **Stale Time**: 5 minutes for cached results
- **Request Timeout**: 10 seconds
- **Previous Data**: Kept during refetch for smooth UX

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus management
- Semantic HTML structure

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Related

- [Recommendations Feature](../recommendations/README.md)
- [Resources Feature](../resources/README.md)
- [Search Route](/src/routes/_auth.search.tsx)
