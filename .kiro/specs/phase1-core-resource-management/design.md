# Design Document

## Overview

Phase 1 delivers the core resource management experience, transforming the basic library panel into a professional resource browser with upload capabilities and detailed viewing. The design emphasizes performance (infinite scroll, optimistic updates), polish (smooth animations, skeleton loading), and user control (filtering, batch operations, view customization).

### Key Features

1. **Library View Enhancements**: Infinite scroll, faceted filtering, batch selection, view density control
2. **Upload Flow**: Drag-and-drop, multi-file progress tracking, URL ingestion, queue management
3. **Resource Detail Page**: Tabbed interface, PDF viewer, quality visualization, quick actions

## Architecture

### Component Hierarchy

```
LibraryPage
├── FilterSidebar
│   ├── FilterCategory (Classification)
│   ├── FilterCategory (Quality)
│   ├── FilterCategory (Date)
│   └── FilterCategory (Type)
├── LibraryToolbar
│   ├── ViewDensityToggle
│   ├── UploadButton
│   └── BatchActionBar (conditional)
└── ResourceGrid
    ├── InfiniteScroll
    ├── ResourceCard (repeated)
    └── SkeletonCard (loading)

UploadZone
├── DragDropArea
├── URLInput
└── UploadQueue
    └── UploadProgressCard (repeated)

ResourceDetailPage
├── Breadcrumbs
├── QuickActionsToolbar
└── TabContainer
    ├── ContentTab (PDF Viewer)
    ├── AnnotationsTab
    ├── MetadataTab
    ├── GraphTab
    └── QualityTab (Radial Chart)
```

### State Management

**Server State (React Query)**
```typescript
// Resources with pagination
const useResources = (filters: ResourceFilters, page: number) => {
  return useInfiniteQuery(
    ['resources', filters],
    ({ pageParam = 0 }) => api.getResources(filters, pageParam),
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    }
  );
};

// Resource detail
const useResource = (id: string) => {
  return useQuery(['resource', id], () => api.getResource(id));
};

// Upload mutation
const useUploadResource = () => {
  return useMutation(api.uploadResource, {
    onSuccess: () => {
      queryClient.invalidateQueries(['resources']);
      toast.show({ type: 'success', message: 'Resource uploaded successfully' });
    },
  });
};
```

**Client State (Zustand)**
```typescript
interface LibraryState {
  filters: ResourceFilters;
  viewDensity: 'compact' | 'comfortable' | 'spacious';
  selectedResources: Set<string>;
  scrollPosition: number;
  
  setFilters: (filters: ResourceFilters) => void;
  setViewDensity: (density: ViewDensity) => void;
  toggleSelection: (id: string) => void;
  clearSelection: () => void;
  saveScrollPosition: (position: number) => void;
}

interface UploadState {
  uploads: Map<string, UploadProgress>;
  addUpload: (file: File | string) => string;
  updateProgress: (id: string, progress: UploadProgress) => void;
  removeUpload: (id: string) => void;
}
```

## Components and Interfaces

### Library View Components

**ResourceCard**
```typescript
interface ResourceCardProps {
  resource: Resource;
  density: 'compact' | 'comfortable' | 'spacious';
  isSelected: boolean;
  onSelect: (id: string) => void;
  onClick: (id: string) => void;
}

// Renders different layouts based on density
// Compact: Title, authors, quality badge
// Comfortable: + abstract preview, tags
// Spacious: + full metadata, larger preview
```

**FilterSidebar**
```typescript
interface FilterSidebarProps {
  filters: ResourceFilters;
  onChange: (filters: ResourceFilters) => void;
  resultCounts: Record<string, number>;
}

interface FilterCategory {
  name: string;
  options: FilterOption[];
  type: 'checkbox' | 'range' | 'date';
}

interface FilterOption {
  label: string;
  value: string;
  count: number;
  enabled: boolean;
}
```

**InfiniteScroll**
```typescript
interface InfiniteScrollProps {
  loadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  threshold: number; // 0.8 for 80%
  children: ReactNode;
}

// Uses Intersection Observer API
// Triggers loadMore when sentinel element is 80% visible
```

### Upload Components

**DragDropZone**
```typescript
interface DragDropZoneProps {
  onDrop: (files: File[]) => void;
  accept: string[]; // ['application/pdf', 'text/html']
  maxSize: number; // bytes
  multiple: boolean;
}

interface DragState {
  isDragging: boolean;
  isOver: boolean;
  error?: string;
}
```

**UploadProgressCard**
```typescript
interface UploadProgressCardProps {
  upload: UploadProgress;
  onCancel: (id: string) => void;
  onRetry: (id: string) => void;
}

interface UploadProgress {
  id: string;
  filename: string;
  status: 'pending' | 'downloading' | 'extracting' | 'analyzing' | 'complete' | 'error';
  progress: number; // 0-100
  error?: string;
  startTime: number;
  estimatedTimeRemaining?: number;
}

// Progress ring animation
// Stage labels with icons
// Error state with retry/details buttons
```

### Detail Page Components

**PDFViewer**
```typescript
interface PDFViewerProps {
  url: string;
  initialPage?: number;
  onPageChange?: (page: number) => void;
}

interface PDFViewerState {
  numPages: number;
  currentPage: number;
  scale: number;
  isLoading: boolean;
}

// Uses react-pdf library
// Zoom controls: 50%, 75%, 100%, 125%, 150%, 200%
// Page navigation: prev, next, jump to page
```

**QualityChart**
```typescript
interface QualityChartProps {
  score: number; // 0-100
  dimensions: QualityDimension[];
  animate: boolean;
}

interface QualityDimension {
  name: string;
  score: number;
  weight: number;
  suggestions?: string[];
}

// Radial chart with clockwise sweep animation
// Color coding: red (<50), yellow (50-75), green (>75)
// Dimension breakdown with suggestions
```

**TabContainer**
```typescript
interface TabContainerProps {
  tabs: Tab[];
  defaultTab: string;
  onTabChange?: (tabId: string) => void;
}

interface Tab {
  id: string;
  label: string;
  icon?: ReactNode;
  content: ReactNode;
  badge?: number; // e.g., annotation count
}

// Fade transition between tabs (200ms)
// Lazy load tab content
// Keyboard navigation (arrow keys)
```

## Data Models

### Resource Model

```typescript
interface Resource {
  id: string;
  title: string;
  authors: string[];
  abstract?: string;
  type: 'pdf' | 'url' | 'epub' | 'markdown';
  classification: string;
  quality_score: number;
  quality_dimensions: QualityDimension[];
  tags: string[];
  created_at: string;
  updated_at: string;
  file_size?: number;
  page_count?: number;
  metadata: ResourceMetadata;
}

interface ResourceMetadata {
  doi?: string;
  isbn?: string;
  publication_date?: string;
  publisher?: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  url?: string;
  [key: string]: any;
}
```

### Filter Model

```typescript
interface ResourceFilters {
  classification?: string[];
  quality_min?: number;
  quality_max?: number;
  date_from?: string;
  date_to?: string;
  type?: ResourceType[];
  tags?: string[];
  search?: string;
}

// Filters are combined with AND logic
// Multiple values within a category use OR logic
// Example: (classification=AI OR classification=ML) AND quality_min=80
```

### Upload Model

```typescript
interface UploadRequest {
  source: File | string; // File object or URL
  type: 'file' | 'url';
  metadata?: Partial<ResourceMetadata>;
}

interface UploadResponse {
  id: string;
  status: UploadStatus;
  resource_id?: string;
  error?: UploadError;
}

interface UploadError {
  code: string;
  message: string;
  details?: any;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Loading State Display During Infinite Scroll
*For any* infinite scroll operation, when additional resources are being loaded, skeleton cards should be displayed at the bottom of the list.
**Validates: Requirements 1.2**

### Property 2: Scroll Request Deduplication
*For any* sequence of rapid scroll events, only one load request should be in flight at a time, preventing duplicate fetches.
**Validates: Requirements 1.4**

### Property 3: Scroll Position Preservation
*For any* navigation away from and back to the library view, the scroll position should be restored to its previous value.
**Validates: Requirements 1.5, 9.5**

### Property 4: Filter Response Time
*For any* filter application, the UI should update and display result counts within 200ms.
**Validates: Requirements 2.2**

### Property 5: Multi-Filter AND Logic
*For any* set of applied filters, the displayed resources should match all filter criteria (AND logic).
**Validates: Requirements 2.3**

### Property 6: Filter Clear Restoration
*For any* library state with applied filters, clearing all filters should restore the full unfiltered resource list.
**Validates: Requirements 2.5**

### Property 7: Selection State Management
*For any* resource checkbox click, the resource should be added to or removed from the selection set correctly.
**Validates: Requirements 3.1**

### Property 8: View Density Persistence
*For any* view density change, the preference should persist across sessions (round-trip property).
**Validates: Requirements 4.5**

### Property 9: Invalid File Type Rejection
*For any* non-supported file type dragged to the upload zone, a warning message should be displayed.
**Validates: Requirements 5.3**

### Property 10: Upload Queue Ordering
*For any* set of multiple files dropped simultaneously, they should be queued and processed in a consistent order.
**Validates: Requirements 5.4**

### Property 11: Upload Stage Progression
*For any* file upload, the status should progress through valid stages only (pending → downloading → extracting → analyzing → complete/error).
**Validates: Requirements 6.2**

### Property 12: Independent Upload Progress
*For any* set of concurrent uploads, each should have independent progress tracking without interference.
**Validates: Requirements 6.5**

### Property 13: URL Validation
*For any* string pasted into the URL ingestion input, invalid URL formats should be rejected with appropriate error messages.
**Validates: Requirements 7.1**

### Property 14: Tab Loading States
*For any* tab content that loads asynchronously, a skeleton loading state should be displayed while loading.
**Validates: Requirements 9.4**

### Property 15: Breadcrumb Collection Reflection
*For any* resource belonging to collections, the breadcrumbs should include all parent collection names.
**Validates: Requirements 13.2**

### Property 16: Optimistic Update Timing
*For any* user action with optimistic updates, the UI should update immediately before the server responds.
**Validates: Requirements 14.1**

### Property 17: Optimistic Update Reconciliation
*For any* optimistic update where the server response differs, the UI should reconcile and display the correct state.
**Validates: Requirements 14.2**

### Property 18: Optimistic Update Rollback
*For any* failed mutation with optimistic updates, the UI should revert to the previous state and display an error.
**Validates: Requirements 14.3**

### Property 19: Batch Optimistic Updates
*For any* batch operation, the UI should update optimistically for all selected items simultaneously.
**Validates: Requirements 14.4**

## Error Handling

### Network Errors

**Retry Strategy**
```typescript
const retryConfig = {
  retries: 3,
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  retryCondition: (error) => {
    return error.response?.status >= 500 || error.code === 'NETWORK_ERROR';
  },
};
```

**Offline Detection**
```typescript
const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
};
```

### Upload Errors

**Error Types**
- File too large
- Unsupported file type
- Network timeout
- Server processing error
- Insufficient storage

**Error Recovery**
```typescript
interface UploadErrorHandler {
  onError: (error: UploadError, upload: UploadProgress) => {
    action: 'retry' | 'skip' | 'abort';
    message: string;
  };
}

// Automatic retry for transient errors
// User prompt for permanent errors
// Detailed error messages with suggestions
```

### Validation Errors

**Client-Side Validation**
- URL format validation
- File type validation
- File size validation
- Required field validation

**Server-Side Validation**
- Duplicate detection
- Metadata validation
- Content extraction validation

## Testing Strategy

### Unit Testing

**Component Tests**
- ResourceCard renders correctly for all density modes
- FilterSidebar applies filters correctly
- UploadProgressCard displays correct status and progress
- PDFViewer handles zoom and navigation
- QualityChart animates correctly

**Hook Tests**
- useInfiniteScroll triggers at correct threshold
- useOptimisticUpdate handles success and failure
- useUploadQueue manages concurrent uploads
- useFilters combines multiple filters with AND logic

**Utility Tests**
- URL validation function
- File type detection
- Progress calculation
- Filter logic

### Property-Based Testing

**Testing Framework**: fast-check for TypeScript

**Configuration**: Minimum 100 iterations per property test

**Test Tagging Format**: `// Feature: phase1-core-resource-management, Property X: [description]`

**Key Properties to Test**:

```typescript
// Property 5: Multi-Filter AND Logic
// Feature: phase1-core-resource-management, Property 5: Multi-Filter AND Logic
test('filtered resources match all criteria', () => {
  fc.assert(
    fc.property(
      fc.array(resourceArbitrary),
      fc.record({
        classification: fc.array(fc.string()),
        quality_min: fc.integer(0, 100),
        type: fc.array(fc.constantFrom('pdf', 'url', 'epub', 'markdown')),
      }),
      (resources, filters) => {
        const filtered = applyFilters(resources, filters);
        return filtered.every(r => 
          (filters.classification.length === 0 || filters.classification.includes(r.classification)) &&
          r.quality_score >= filters.quality_min &&
          (filters.type.length === 0 || filters.type.includes(r.type))
        );
      }
    ),
    { numRuns: 100 }
  );
});

// Property 11: Upload Stage Progression
// Feature: phase1-core-resource-management, Property 11: Upload Stage Progression
test('upload status transitions are valid', () => {
  fc.assert(
    fc.property(
      fc.array(fc.constantFrom('pending', 'downloading', 'extracting', 'analyzing', 'complete', 'error')),
      (statusSequence) => {
        const validTransitions = {
          'pending': ['downloading', 'error'],
          'downloading': ['extracting', 'error'],
          'extracting': ['analyzing', 'error'],
          'analyzing': ['complete', 'error'],
          'complete': [],
          'error': [],
        };
        
        for (let i = 0; i < statusSequence.length - 1; i++) {
          const current = statusSequence[i];
          const next = statusSequence[i + 1];
          if (!validTransitions[current].includes(next)) {
            return false;
          }
        }
        return true;
      }
    ),
    { numRuns: 100 }
  );
});

// Property 13: URL Validation
// Feature: phase1-core-resource-management, Property 13: URL Validation
test('invalid URLs are rejected', () => {
  fc.assert(
    fc.property(
      fc.string(),
      (input) => {
        const isValid = validateURL(input);
        if (isValid) {
          // If marked valid, should parse as URL
          try {
            new URL(input);
            return true;
          } catch {
            return false;
          }
        }
        return true; // Invalid URLs correctly rejected
      }
    ),
    { numRuns: 100 }
  );
});

// Property 18: Optimistic Update Rollback
// Feature: phase1-core-resource-management, Property 18: Optimistic Update Rollback
test('failed mutations revert optimistic updates', () => {
  fc.assert(
    fc.property(
      fc.array(resourceArbitrary),
      fc.record({ id: fc.string(), updates: fc.object() }),
      async (initialResources, mutation) => {
        const store = createStore(initialResources);
        const previousState = store.getState();
        
        // Apply optimistic update
        store.applyOptimistic(mutation);
        
        // Simulate failure
        await store.rejectMutation(mutation, new Error('Server error'));
        
        // State should be reverted
        return JSON.stringify(store.getState()) === JSON.stringify(previousState);
      }
    ),
    { numRuns: 100 }
  );
});
```

### Integration Testing

**User Flows**
1. Upload → View in Library → Filter → Select → Batch Operation
2. Browse Library → Infinite Scroll → Click Resource → View Details → Navigate Tabs
3. Drag Files → Monitor Progress → Handle Errors → Retry Failed Uploads
4. Apply Filters → Change View Density → Select Resources → Clear Filters

**Performance Tests**
- Infinite scroll with 10,000+ resources
- Concurrent upload of 50+ files
- Filter application on large datasets
- Tab switching responsiveness

### Accessibility Testing

**Keyboard Navigation**
- Tab through all interactive elements
- Arrow keys for list navigation
- Enter/Space for selection
- Escape to close modals

**Screen Reader**
- Resource cards announce title, authors, quality
- Filter changes announce result counts
- Upload progress announces status changes
- Tab switches announce new content

**ARIA Labels**
- `role="region"` for major sections
- `aria-label` for icon buttons
- `aria-live="polite"` for status updates
- `aria-busy="true"` during loading

## Performance Optimization

### Infinite Scroll Optimization

**Virtual Scrolling**
```typescript
// Use react-window for large lists
import { FixedSizeGrid } from 'react-window';

<FixedSizeGrid
  columnCount={3}
  columnWidth={350}
  height={800}
  rowCount={Math.ceil(resources.length / 3)}
  rowHeight={400}
  width={1200}
>
  {({ columnIndex, rowIndex, style }) => (
    <div style={style}>
      <ResourceCard resource={resources[rowIndex * 3 + columnIndex]} />
    </div>
  )}
</FixedSizeGrid>
```

**Intersection Observer**
```typescript
const observerOptions = {
  root: null,
  rootMargin: '200px', // Load before reaching bottom
  threshold: 0.8,
};

const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting && hasMore && !isLoading) {
    loadMore();
  }
}, observerOptions);
```

### Upload Optimization

**Concurrent Uploads**
```typescript
const MAX_CONCURRENT_UPLOADS = 3;

const uploadQueue = new PQueue({ concurrency: MAX_CONCURRENT_UPLOADS });

files.forEach(file => {
  uploadQueue.add(() => uploadFile(file));
});
```

**Chunked Upload for Large Files**
```typescript
const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks

async function uploadLargeFile(file: File) {
  const chunks = Math.ceil(file.size / CHUNK_SIZE);
  
  for (let i = 0; i < chunks; i++) {
    const chunk = file.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE);
    await uploadChunk(chunk, i, chunks);
    updateProgress((i + 1) / chunks * 100);
  }
}
```

### Filter Optimization

**Debounced Filter Application**
```typescript
const debouncedFilter = useMemo(
  () => debounce((filters: ResourceFilters) => {
    applyFilters(filters);
  }, 200),
  []
);
```

**Memoized Filter Results**
```typescript
const filteredResources = useMemo(() => {
  return resources.filter(resource => {
    return matchesFilters(resource, filters);
  });
}, [resources, filters]);
```

## UI Polish Details

### Animations

**Timing Functions**
- Ease-out for entrances: `cubic-bezier(0.0, 0.0, 0.2, 1)`
- Ease-in for exits: `cubic-bezier(0.4, 0.0, 1, 1)`
- Ease-in-out for transitions: `cubic-bezier(0.4, 0.0, 0.2, 1)`

**Durations**
- Micro-interactions: 100ms (hover, focus)
- Standard transitions: 200ms (tab switch, filter apply)
- Complex animations: 300ms (card reorder, modal open)
- Emphasis animations: 500ms (success confetti, quality chart)

**Motion Preferences**
```typescript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const animationConfig = {
  duration: prefersReducedMotion ? 0 : 200,
  easing: 'ease-out',
};
```

### Loading States

**Skeleton Variants**
- Text: Animated gradient shimmer
- Card: Full card outline with shimmer
- List: Multiple card skeletons
- Chart: Circular skeleton for radial chart

**Skeleton Timing**
- Show immediately (no delay)
- Minimum display time: 300ms (prevent flash)
- Fade out when content loads: 150ms

### Micro-interactions

**Hover Effects**
- Resource cards: Subtle elevation increase (2px → 4px shadow)
- Buttons: Background color shift (10% lighter/darker)
- Filter options: Background highlight

**Focus Indicators**
- 2px solid outline
- Color: Primary color with 50% opacity
- Offset: 2px from element
- Border radius matches element

**Success Animations**
- Upload complete: Subtle confetti burst (10-15 particles)
- Batch operation complete: Green checkmark with scale animation
- Filter applied: Brief highlight pulse on result count

## Backend Integration

### API Endpoints

**Resources**
```typescript
GET /api/resources?page=0&limit=20&classification=AI&quality_min=80
Response: {
  resources: Resource[],
  total: number,
  nextCursor: string | null
}

GET /api/resources/:id
Response: Resource

POST /api/resources/upload
Body: FormData with file or { url: string }
Response: { id: string, status: UploadStatus }

GET /api/resources/:id/status
Response: { status: UploadStatus, progress: number, error?: string }

PUT /api/resources/batch
Body: { ids: string[], operation: string, params: any }
Response: { succeeded: string[], failed: { id: string, error: string }[] }
```

**Filters**
```typescript
GET /api/resources/filters/counts?classification=AI
Response: {
  quality: { min: number, max: number, distribution: number[] },
  types: { pdf: number, url: number, epub: number, markdown: number },
  dates: { min: string, max: string }
}
```

### WebSocket Events (Future Enhancement)

```typescript
// Real-time upload progress
socket.on('upload:progress', (data: { id: string, progress: number, status: UploadStatus }) => {
  updateUploadProgress(data);
});

// Real-time resource updates
socket.on('resource:updated', (resource: Resource) => {
  queryClient.setQueryData(['resource', resource.id], resource);
});
```

## Deployment Considerations

### Code Splitting

```typescript
// Route-based splitting
const LibraryPage = lazy(() => import('./pages/LibraryPage'));
const ResourceDetailPage = lazy(() => import('./pages/ResourceDetailPage'));

// Component-based splitting for heavy components
const PDFViewer = lazy(() => import('./components/PDFViewer'));
const QualityChart = lazy(() => import('./components/QualityChart'));
```

### Bundle Size Targets

- Initial bundle: < 200KB gzipped
- Library page chunk: < 150KB gzipped
- Detail page chunk: < 100KB gzipped
- PDF viewer chunk: < 300KB gzipped (includes pdf.js)

### Performance Budgets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- First Input Delay: < 100ms

### Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: iOS Safari 14+, Chrome Android 90+

### Progressive Enhancement

- Core functionality works without JavaScript (server-rendered fallback)
- Graceful degradation for older browsers
- Feature detection for modern APIs (Intersection Observer, File API)
