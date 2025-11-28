# Design Document

## Overview

The Neo Alexandria Frontend Roadmap is a 10-phase, 25-week development plan that transforms a minimal frontend into a comprehensive research knowledge management system. The design emphasizes incremental delivery, maintaining production-readiness at every milestone while integrating UI polish directly into feature development.

### Core Design Principles

1. **Always Production Ready**: Each phase ends with a deployable application
2. **UI Polish First**: Visual refinements integrated into feature development, not retrofitted
3. **Progressive Enhancement**: Core functionality works without JavaScript where possible
4. **Performance Budget**: Every feature meets defined performance thresholds
5. **Accessibility Default**: WCAG compliance built in from the start
6. **Mobile Consideration**: Responsive design throughout

## Architecture

### Phase Dependency Graph

```
Phase 0 (Foundation)
    ↓
Phase 1 (Resources) ← Phase 2 (Search)
    ↓                      ↓
Phase 4 (Collections) → Phase 3 (Recommendations)
    ↓                      ↓
Phase 5 (Annotations) → Phase 6 (Knowledge Graph)
    ↓                      ↓
Phase 7 (Quality) ← Phase 8 (Taxonomy)
    ↓
Phase 9 (Monitoring)
    ↓
Phase 10 (Polish)
```

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **State Management**: React Query for server state, Zustand for client state
- **Routing**: React Router v6
- **Styling**: Tailwind CSS with CSS variables for theming
- **Animation**: Framer Motion with reduced-motion support
- **Testing**: Vitest + React Testing Library + fast-check (PBT)
- **Build**: Vite with code splitting
- **Accessibility**: radix-ui primitives for complex components

## Components and Interfaces

### Shared Component Library (Phase 0)


**Toast Notification System**
```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  action?: { label: string; onClick: () => void };
}

interface ToastManager {
  show(toast: Omit<Toast, 'id'>): string;
  dismiss(id: string): void;
  dismissAll(): void;
}
```

**Skeleton Loading Components**
```typescript
interface SkeletonProps {
  variant: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}
```

**Animation Utilities**
```typescript
interface AnimationConfig {
  duration: number; // milliseconds
  easing: string;
  respectMotionPreference: boolean;
}

const animations = {
  fade: (config?: Partial<AnimationConfig>) => MotionProps;
  slide: (direction: 'up' | 'down' | 'left' | 'right', config?: Partial<AnimationConfig>) => MotionProps;
  scale: (config?: Partial<AnimationConfig>) => MotionProps;
};
```

**Command Palette**
```typescript
interface CommandPaletteAction {
  id: string;
  label: string;
  keywords: string[];
  icon?: ReactNode;
  shortcut?: string[];
  onExecute: () => void | Promise<void>;
}

interface CommandPaletteProps {
  actions: CommandPaletteAction[];
  placeholder?: string;
  onClose: () => void;
}
```

### Phase-Specific Interfaces

**Resource Management (Phase 1)**
```typescript
interface Resource {
  id: string;
  title: string;
  authors: string[];
  type: 'pdf' | 'url' | 'epub' | 'markdown';
  classification: string;
  quality_score: number;
  created_at: string;
  metadata: Record<string, any>;
}

interface ResourceUpload {
  file?: File;
  url?: string;
  status: 'pending' | 'downloading' | 'extracting' | 'analyzing' | 'complete' | 'error';
  progress: number;
  error?: string;
}
```

**Search (Phase 2)**
```typescript
interface SearchQuery {
  query: string;
  method: 'fts5' | 'vector' | 'hybrid';
  weights?: { keyword: number; semantic: number };
  filters?: ResourceFilters;
}

interface SearchResult {
  resource: Resource;
  score: number;
  highlights: string[];
  explanation?: string;
}
```

**Collections (Phase 4)**
```typescript
interface Collection {
  id: string;
  name: string;
  description?: string;
  type: 'manual' | 'smart';
  rules?: CollectionRule[];
  resource_count: number;
  created_at: string;
}

interface CollectionRule {
  field: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than';
  value: any;
}
```

**Annotations (Phase 5)**
```typescript
interface Annotation {
  id: string;
  resource_id: string;
  type: 'highlight' | 'note';
  content: string;
  color?: string;
  tags: string[];
  position: AnnotationPosition;
  created_at: string;
}

interface AnnotationPosition {
  page?: number;
  start: number;
  end: number;
  text: string;
}
```

## Data Models

### State Management Strategy

**Server State (React Query)**
- Resources, collections, annotations, search results
- Cache invalidation on mutations
- Optimistic updates for better UX
- Background refetching for stale data

**Client State (Zustand)**
- UI state (modals, sidebars, theme)
- User preferences (view density, filters)
- Command palette state
- Toast notification queue

### API Integration Patterns

All phases follow consistent patterns:
```typescript
// Query hooks
const useResources = (filters?: ResourceFilters) => {
  return useQuery(['resources', filters], () => api.getResources(filters));
};

// Mutation hooks with optimistic updates
const useCreateResource = () => {
  const queryClient = useQueryClient();
  return useMutation(api.createResource, {
    onMutate: async (newResource) => {
      await queryClient.cancelQueries(['resources']);
      const previous = queryClient.getQueryData(['resources']);
      queryClient.setQueryData(['resources'], (old) => [...old, newResource]);
      return { previous };
    },
    onError: (err, newResource, context) => {
      queryClient.setQueryData(['resources'], context.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries(['resources']);
    },
  });
};
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Phase Completion Maintains Deployability
*For any* completed phase, the application should pass all build checks, have no console errors, and successfully render all existing routes.
**Validates: Requirements 1.1**

### Property 2: Loading State Consistency
*For any* async operation, a loading state should be displayed before data arrives, and removed when data is available or an error occurs.
**Validates: Requirements 2.1, 13.3**

### Property 3: Keyboard Navigation Completeness
*For any* interactive element, it should be reachable and operable via keyboard alone without requiring mouse interaction.
**Validates: Requirements 2.4, 12.4**

### Property 4: Animation Motion Preference Respect
*For any* animation, when the user has reduced-motion preferences enabled, the animation should either be disabled or use a reduced variant.
**Validates: Requirements 2.5**

### Property 5: Filter Application Consistency
*For any* set of filters applied to a resource list, the displayed results should match the filter criteria exactly.
**Validates: Requirements 3.2**

### Property 6: Upload Progress Accuracy
*For any* file upload, the progress percentage should monotonically increase from 0 to 100, and status should transition through valid states only.
**Validates: Requirements 3.3**

### Property 7: Search Result Relevance
*For any* search query, results should be ordered by descending relevance score, and all results should contain the query terms or be semantically similar.
**Validates: Requirements 4.4**

### Property 8: Smart Collection Rule Evaluation
*For any* smart collection with defined rules, the resources in the collection should exactly match those satisfying all rules.
**Validates: Requirements 6.3, 6.4**

### Property 9: Annotation Position Preservation
*For any* annotation created on a document, retrieving and rendering it should highlight the exact same text at the same position.
**Validates: Requirements 7.2**

### Property 10: Graph Node Relationship Consistency
*For any* two nodes connected in the knowledge graph, there should exist a documented relationship (citation, similarity, co-occurrence) in the backend data.
**Validates: Requirements 8.2**

### Property 11: Quality Score Bounds
*For any* resource quality score displayed, it should be within the valid range [0, 100] and match the backend calculation.
**Validates: Requirements 9.2**

### Property 12: Taxonomy Hierarchy Integrity
*For any* taxonomy node, it should have at most one parent, and moving a node should not create cycles in the tree.
**Validates: Requirements 10.2**

### Property 13: Performance Budget Compliance
*For any* page load, First Contentful Paint should occur within 1.5 seconds and Time to Interactive within 3.5 seconds on standard hardware.
**Validates: Requirements 12.1, 12.2**

### Property 14: ARIA Label Completeness
*For any* interactive element or dynamic content region, it should have appropriate ARIA labels or roles for screen reader users.
**Validates: Requirements 12.5**

### Property 15: Toast Notification Queue Ordering
*For any* sequence of toast notifications, they should be displayed in the order they were triggered and respect maximum queue size.
**Validates: Requirements 2.3**

## Error Handling

### Error Boundary Strategy

**Component-Level Boundaries**
- Wrap each major feature in an error boundary
- Display user-friendly error messages with recovery actions
- Log errors to monitoring service

**Network Error Handling**
- Retry logic with exponential backoff for transient failures
- Clear error messages for 4xx/5xx responses
- Offline detection with queue for mutations

**Validation Errors**
- Inline validation feedback on form fields
- Prevent submission until validation passes
- Clear error messages explaining requirements

### Error Recovery Patterns

```typescript
interface ErrorBoundaryProps {
  fallback: (error: Error, reset: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

// Network error recovery
const handleNetworkError = (error: Error) => {
  if (error.message.includes('network')) {
    toast.show({
      type: 'error',
      message: 'Network error. Retrying...',
      action: { label: 'Retry Now', onClick: () => queryClient.refetchQueries() }
    });
  }
};
```

## Testing Strategy

### Unit Testing

**Component Testing**
- Test each component in isolation with React Testing Library
- Focus on user interactions and accessibility
- Mock API calls and external dependencies

**Hook Testing**
- Test custom hooks with @testing-library/react-hooks
- Verify state updates and side effects
- Test error handling paths

**Utility Testing**
- Test animation utilities with different motion preferences
- Test filter logic and data transformations
- Test validation functions

### Property-Based Testing

**Testing Framework**: fast-check for TypeScript property-based testing

**Configuration**: Each property test runs a minimum of 100 iterations

**Test Tagging**: Each property-based test includes a comment referencing the design document property:
```typescript
// Feature: neo-alexandria-frontend-roadmap, Property 5: Filter Application Consistency
test('filtered resources match criteria', () => {
  fc.assert(
    fc.property(
      fc.array(resourceArbitrary),
      fc.record({ classification: fc.string(), quality_min: fc.integer(0, 100) }),
      (resources, filters) => {
        const filtered = applyFilters(resources, filters);
        return filtered.every(r => 
          r.classification === filters.classification &&
          r.quality_score >= filters.quality_min
        );
      }
    ),
    { numRuns: 100 }
  );
});
```

**Key Properties to Test**:
- Filter consistency (Property 5)
- Upload progress monotonicity (Property 6)
- Smart collection rule evaluation (Property 8)
- Annotation position preservation (Property 9)
- Quality score bounds (Property 11)
- Taxonomy hierarchy integrity (Property 12)
- Toast queue ordering (Property 15)

### Integration Testing

**End-to-End Flows**
- Complete user journeys (upload → view → annotate → organize)
- Cross-phase interactions (search → add to collection → view graph)
- Error recovery scenarios

**Performance Testing**
- Lighthouse CI in GitHub Actions
- Bundle size monitoring
- Render performance profiling

### Accessibility Testing

**Automated Testing**
- axe-core integration in component tests
- ARIA attribute validation
- Color contrast checking

**Manual Testing**
- Keyboard navigation audit
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Focus management verification

## Phase Implementation Details

### Phase 0: Foundation Enhancement (1 week)

**Deliverables**:
- Toast notification system with queue management
- Skeleton loading components (text, card, list variants)
- Animation utility library with motion preferences
- Command palette with fuzzy search
- Focus management utilities

**Success Criteria**:
- All existing pages use skeleton loading
- Command palette accessible via Cmd+K
- Keyboard navigation works on all interactive elements
- Theme transitions smooth (200ms)

### Phase 1: Core Resource Management (3 weeks)

**Deliverables**:
- Library view with infinite scroll and filtering
- Drag-and-drop upload with progress tracking
- Resource detail page with tabbed interface
- Batch selection and operations

**Success Criteria**:
- Users can upload and view resources
- Filtering updates results in real-time
- Detail page loads in under 1 second
- Batch operations work on 100+ items

### Phase 2-10: [Detailed in phase-specific specs]

Each subsequent phase will have its own detailed spec document following this master design.

## Performance Optimization Strategy

### Code Splitting
- Route-based splitting for each major feature
- Dynamic imports for heavy components (PDF viewer, graph visualization)
- Lazy loading for below-the-fold content

### Bundle Optimization
- Tree shaking for unused code
- Compression (gzip/brotli)
- CDN for static assets
- Image optimization (WebP, lazy loading)

### Runtime Optimization
- Virtual scrolling for large lists (react-window)
- Memoization for expensive computations
- Debouncing for search and filter inputs
- Request deduplication with React Query

## Accessibility Implementation

### Keyboard Navigation
- Tab order follows visual order
- Skip links for main content
- Escape key closes modals/overlays
- Arrow keys for list navigation

### Screen Reader Support
- Semantic HTML elements
- ARIA labels for dynamic content
- Live regions for status updates
- Descriptive link text

### Visual Accessibility
- Color contrast ratio ≥ 4.5:1 for text
- Focus indicators visible and clear
- Text resizable to 200% without loss of functionality
- No information conveyed by color alone

## Monitoring and Observability

### Frontend Metrics
- Core Web Vitals (LCP, FID, CLS)
- JavaScript error rate
- API response times
- User interaction events

### User Analytics
- Feature usage tracking
- User flow analysis
- Search query patterns
- Error encounter rates

### Performance Monitoring
- Real User Monitoring (RUM)
- Synthetic monitoring for critical paths
- Bundle size tracking over time
- Lighthouse CI scores

## Migration and Rollout Strategy

### Feature Flags
- Gradual rollout of new phases
- A/B testing for UI variations
- Quick rollback capability

### Backward Compatibility
- API versioning for breaking changes
- Graceful degradation for older browsers
- Progressive enhancement approach

### User Communication
- In-app announcements for new features
- Changelog documentation
- User feedback collection
