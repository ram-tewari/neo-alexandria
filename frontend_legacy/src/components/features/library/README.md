# Library Feature Components

This directory contains components for the library view with faceted filtering capabilities.

## Components

### FilterSidebar

The main filter sidebar component that displays filter options with result counts.

**Features:**
- Classification filter
- Quality range filter (min/max sliders)
- Resource type filter
- Language filter
- Read status filter
- Clear all filters button
- Displays result counts for each option

**Usage:**
```tsx
import { FilterSidebar } from './components/features/library';
import { useResourceFilters } from './lib/hooks';

const MyComponent = () => {
  const [filters, setFilters] = useResourceFilters();
  
  const facets = {
    classifications: [
      { label: 'Computer Science', value: 'cs', count: 42 },
      { label: 'Mathematics', value: 'math', count: 28 },
    ],
    types: [
      { label: 'Article', value: 'article', count: 35 },
      { label: 'Book', value: 'book', count: 15 },
    ],
    languages: [
      { label: 'English', value: 'en', count: 50 },
    ],
  };

  return (
    <FilterSidebar
      filters={filters}
      onChange={setFilters}
      facets={facets}
    />
  );
};
```

### ResponsiveFilterSidebar

A responsive wrapper around FilterSidebar that adapts to different screen sizes:
- **Desktop (≥768px)**: Fixed sidebar on the left
- **Mobile (<768px)**: Collapsible drawer with backdrop

**Features:**
- Automatic responsive behavior
- Smooth transitions
- Keyboard accessible (Escape to close)
- Focus trap when drawer is open
- Backdrop click to close

**Usage:**
```tsx
import { ResponsiveFilterSidebar, FilterButton } from './components/features/library';
import { useResourceFilters, useActiveFilterCount } from './lib/hooks';

const MyComponent = () => {
  const [filters, setFilters] = useResourceFilters();
  const [isOpen, setIsOpen] = useState(false);
  const activeCount = useActiveFilterCount(filters);

  return (
    <div className="flex h-full">
      <ResponsiveFilterSidebar
        filters={filters}
        onChange={setFilters}
        facets={facets}
        isOpen={isOpen}
        onOpenChange={setIsOpen}
      />
      
      {/* Mobile filter button */}
      <div className="md:hidden">
        <FilterButton
          activeCount={activeCount}
          onClick={() => setIsOpen(true)}
        />
      </div>
      
      {/* Main content */}
      <div className="flex-1">
        {/* Your content here */}
      </div>
    </div>
  );
};
```

### EmptyState

Displays a friendly message when no resources match the current filters.

**Features:**
- Different messages for filtered vs. empty library
- Clear filters action
- Responsive illustration
- Accessible with ARIA live regions

**Usage:**
```tsx
import { EmptyState } from './components/features/library';
import { useResourceFilters } from './lib/hooks';

const MyComponent = () => {
  const [filters, setFilters] = useResourceFilters();
  const resources = []; // Your resources

  if (resources.length === 0) {
    return (
      <EmptyState
        filters={filters}
        onClearFilters={() => setFilters({})}
      />
    );
  }

  return <ResourceList resources={resources} />;
};
```

### LibraryView

A complete library view that integrates all the components above.

**Features:**
- Responsive filter sidebar
- Empty state handling
- Integration with LibraryPanel
- Mobile filter button
- URL-synced filters

**Usage:**
```tsx
import { LibraryView } from './components/features/library';

const LibraryPage = () => {
  const facets = {
    // Your facet data
  };

  return (
    <LibraryView
      facets={facets}
      onResourceClick={(resource) => {
        console.log('Resource clicked:', resource);
      }}
    />
  );
};
```

## Hooks

### useResourceFilters

Manages filter state with URL synchronization.

**Features:**
- Parses filters from URL search parameters
- Updates URL when filters change
- Type-safe filter state
- Shareable/bookmarkable filter URLs

**Usage:**
```tsx
import { useResourceFilters } from './lib/hooks';

const MyComponent = () => {
  const [filters, setFilters] = useResourceFilters();

  // Update a single filter
  const handleTypeChange = (type: string) => {
    setFilters({ ...filters, type });
  };

  // Clear all filters
  const handleClearAll = () => {
    setFilters({});
  };

  return (
    <div>
      <p>Current filters: {JSON.stringify(filters)}</p>
      <button onClick={() => handleTypeChange('article')}>
        Filter by Article
      </button>
      <button onClick={handleClearAll}>Clear All</button>
    </div>
  );
};
```

### useActiveFilterCount

Returns the number of active filters.

**Usage:**
```tsx
import { useActiveFilterCount } from './lib/hooks';

const MyComponent = () => {
  const [filters] = useResourceFilters();
  const count = useActiveFilterCount(filters);

  return <span>Active filters: {count}</span>;
};
```

### useHasActiveFilters

Returns whether any filters are active.

**Usage:**
```tsx
import { useHasActiveFilters } from './lib/hooks';

const MyComponent = () => {
  const [filters] = useResourceFilters();
  const hasFilters = useHasActiveFilters(filters);

  return hasFilters ? <ClearButton /> : null;
};
```

## Types

### ResourceFilters

```typescript
interface ResourceFilters {
  q?: string;                    // Text search query
  classification_code?: string;  // Classification filter
  type?: string;                 // Resource type filter
  language?: string;             // Language filter
  read_status?: ReadStatus;      // Read status filter
  min_quality?: number;          // Minimum quality score (0-1)
  max_quality?: number;          // Maximum quality score (0-1)
  subject?: string;              // Subject filter
}
```

### FilterFacets

```typescript
interface FilterFacets {
  classifications?: FilterFacet[];
  types?: FilterFacet[];
  languages?: FilterFacet[];
  readStatuses?: FilterFacet[];
}

interface FilterFacet {
  label: string;  // Display label
  value: string;  // Filter value
  count: number;  // Number of resources with this value
}
```

## Styling

All components use Tailwind CSS classes and support dark mode out of the box. They follow the design system established in Phase 0 and integrate with existing UI components (Button, Card, etc.).

## Accessibility

All components are built with accessibility in mind:
- Keyboard navigation support
- ARIA attributes for screen readers
- Focus management
- Visible focus indicators
- Touch-friendly controls on mobile (44x44px minimum)

## Performance

The filter sidebar implements several performance optimizations:
- Optimistic UI updates
- Debounced filter changes (via URL sync)
- Memoized filter state
- Efficient re-renders with React.memo where appropriate
