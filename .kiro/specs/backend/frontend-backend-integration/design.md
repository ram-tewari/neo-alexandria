# Design Document: Frontend-Backend Integration

## Overview

This design document outlines the technical architecture for integrating the Neo Alexandria frontend with the FastAPI backend. The integration will be implemented in three phases:

- **Phase 1**: UI/UX enhancements and backend connection foundation
- **Phase 2**: Additional features (TBD)
- **Phase 3**: Full integration and end-to-end functionality

The design focuses on creating a modern, responsive interface with multiple view modes, keyboard-driven navigation, and seamless backend communication.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dashboard  │  │   Library    │  │ Knowledge    │      │
│  │     View     │  │     View     │  │  Graph View  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│         ┌──────────────────▼──────────────────┐             │
│         │      API Client Service              │             │
│         │  (Axios/Fetch + Type Safety)         │             │
│         └──────────────────┬──────────────────┘             │
└────────────────────────────┼──────────────────────────────┘
                             │ HTTP/REST
                             │
┌────────────────────────────▼──────────────────────────────┐
│                  Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Resources   │  │ Collections  │  │    Search    │    │
│  │   Router     │  │   Router     │  │    Router    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                               │
│         ┌──────────────────▼──────────────────┐           │
│         │      Service Layer                   │           │
│         └──────────────────┬──────────────────┘           │
│                            │                               │
│         ┌──────────────────▼──────────────────┐           │
│         │    Database (SQLite/PostgreSQL)     │           │
│         └──────────────────────────────────────┘           │
└────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18.2 with TypeScript
- Vite for build tooling
- Zustand for state management
- React Router for navigation
- Framer Motion for animations
- Lucide React for icons

**Backend:**
- FastAPI with Python 3.11+
- SQLAlchemy ORM
- Pydantic for validation
- SQLite/PostgreSQL database


## Components and Interfaces

### 1. API Client Service

**Purpose**: Centralized HTTP client for all backend communication with type safety and error handling.

**Location**: `frontend/src/services/api/`

**Structure**:
```typescript
// api/client.ts - Base HTTP client
class APIClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  
  async request<T>(config: RequestConfig): Promise<APIResponse<T>>;
  async get<T>(url: string, params?: QueryParams): Promise<T>;
  async post<T>(url: string, data: any): Promise<T>;
  async put<T>(url: string, data: any): Promise<T>;
  async delete<T>(url: string): Promise<T>;
}

// api/resources.ts - Resource-specific endpoints
export const resourcesAPI = {
  list: (params: ResourceListParams) => Promise<ResourceListResponse>,
  get: (id: string) => Promise<Resource>,
  create: (data: ResourceCreate) => Promise<Resource>,
  update: (id: string, data: ResourceUpdate) => Promise<Resource>,
  delete: (id: string) => Promise<void>,
  updateStatus: (id: string, status: ReadStatus) => Promise<Resource>
};

// api/collections.ts - Collection-specific endpoints
export const collectionsAPI = {
  list: (params: CollectionListParams) => Promise<CollectionListResponse>,
  get: (id: string) => Promise<CollectionDetail>,
  create: (data: CollectionCreate) => Promise<Collection>,
  update: (id: string, data: CollectionUpdate) => Promise<Collection>,
  delete: (id: string) => Promise<void>,
  addResources: (id: string, resourceIds: string[]) => Promise<void>,
  removeResources: (id: string, resourceIds: string[]) => Promise<void>
};

// api/search.ts - Search endpoints
export const searchAPI = {
  search: (query: string, filters: SearchFilters) => Promise<SearchResults>,
  suggestions: (query: string) => Promise<string[]>
};
```

**Error Handling**:
- Network errors → Retry with exponential backoff
- 4xx errors → Display user-friendly messages
- 5xx errors → Log and show generic error
- Timeout errors → Cancel and notify user

**Caching Strategy**:
- GET requests cached for 5 minutes
- Cache invalidation on mutations (POST/PUT/DELETE)
- Optimistic updates for better UX


### 2. State Management Architecture

**Purpose**: Manage application state with Zustand stores for different domains.

**Store Structure**:

```typescript
// store/resourceStore.ts
interface ResourceStore {
  // State
  resources: Resource[];
  selectedResource: Resource | null;
  viewMode: ViewMode;
  filters: ResourceFilters;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchResources: (params: FetchParams) => Promise<void>;
  selectResource: (id: string) => void;
  setViewMode: (mode: ViewMode) => void;
  updateFilters: (filters: Partial<ResourceFilters>) => void;
  updateResourceStatus: (id: string, status: ReadStatus) => Promise<void>;
  archiveResource: (id: string) => Promise<void>;
}

// store/collectionStore.ts
interface CollectionStore {
  // State
  collections: Collection[];
  activeCollection: Collection | null;
  collectionTree: CollectionNode[];
  isLoading: boolean;
  
  // Actions
  fetchCollections: () => Promise<void>;
  selectCollection: (id: string) => void;
  createCollection: (data: CollectionCreate) => Promise<Collection>;
  updateCollection: (id: string, data: CollectionUpdate) => Promise<void>;
  deleteCollection: (id: string) => Promise<void>;
  addResourcesToCollection: (collectionId: string, resourceIds: string[]) => Promise<void>;
}

// store/uiStore.ts
interface UIStore {
  // State
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
  theme: 'light' | 'dark';
  
  // Actions
  toggleSidebar: () => void;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

**State Persistence**:
- View mode preferences → localStorage
- Sidebar state → localStorage
- Theme preference → localStorage
- User filters → sessionStorage


### 3. Card-Based Dashboard Component

**Purpose**: Display resources in multiple view modes with quick actions.

**Component Hierarchy**:
```
Dashboard
├── ViewModeSelector
├── FilterBar
└── ResourceGallery
    ├── GridView
    │   └── ResourceCard[]
    ├── ListView
    │   └── ResourceListItem[]
    ├── HeadlinesView
    │   └── ResourceHeadline[]
    └── MasonryView
        └── ResourceCard[] (variable heights)
```

**ResourceCard Component**:
```typescript
interface ResourceCardProps {
  resource: Resource;
  viewMode: ViewMode;
  onRead: (id: string) => void;
  onArchive: (id: string) => void;
  onAnnotate: (id: string) => void;
  onShare: (id: string) => void;
}

// Features:
// - Preview image with lazy loading
// - Title with truncation
// - Quality score badge (color-coded)
// - Tag pills (max 3 visible, +N more)
// - Hover overlay with quick actions
// - Skeleton loader during fetch
```

**View Mode Specifications**:

1. **Grid View**:
   - Responsive columns: 2-6 based on screen width
   - Fixed card height: 280px
   - Image aspect ratio: 16:9
   - Gap: 16px

2. **List View**:
   - Single column
   - Horizontal layout
   - Image: 120x80px thumbnail
   - Full metadata visible
   - Compact spacing

3. **Headlines View**:
   - Text-only, no images
   - Title + description snippet
   - Quality score inline
   - Dense layout for scanning

4. **Masonry View**:
   - Variable card heights based on content
   - 2-4 columns responsive
   - Waterfall layout algorithm
   - Optimized for visual browsing


### 4. Command Palette Component

**Purpose**: Keyboard-driven interface for power users to execute commands quickly.

**Component Structure**:
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Command {
  id: string;
  label: string;
  icon: LucideIcon;
  keywords: string[];
  category: 'navigation' | 'action' | 'filter' | 'search';
  action: () => void | Promise<void>;
  shortcut?: string;
}

// Command categories:
// - Navigation: Go to Dashboard, Library, Graph, Collections
// - Actions: Create Resource, New Collection, Archive, Export
// - Filters: Filter by Quality, Filter by Date, Filter by Tags
// - Search: Search Resources, Search Collections
```

**Features**:
- Fuzzy search with Fuse.js or similar
- Keyboard navigation (↑↓ arrows, Enter to select, Esc to close)
- Recent commands history
- Command shortcuts display
- Category grouping
- Async command execution with loading states

**Keyboard Shortcuts**:
- `Cmd/Ctrl + K`: Open palette
- `Cmd/Ctrl + P`: Quick search resources
- `Cmd/Ctrl + Shift + P`: Quick search collections
- `Esc`: Close palette
- `↑↓`: Navigate commands
- `Enter`: Execute command
- `Tab`: Cycle through categories


### 5. Hybrid Sidebar + Gallery Layout

**Purpose**: Provide collection navigation with main content area for browsing.

**Component Structure**:
```
LibraryView
├── CollectionSidebar
│   ├── SidebarHeader (collapse toggle, search)
│   ├── CollectionTree
│   │   └── CollectionNode[] (recursive)
│   └── SidebarFooter (+ New Collection)
└── GalleryArea
    ├── GalleryHeader
    │   ├── Breadcrumbs
    │   ├── ViewModeToggle
    │   └── AddResourceButton
    ├── ResourceGallery (reused from Dashboard)
    └── RecommendationsPanel (collapsible)
```

**CollectionTree Component**:
```typescript
interface CollectionNode {
  id: string;
  name: string;
  resourceCount: number;
  children: CollectionNode[];
  isExpanded: boolean;
  depth: number;
}

// Features:
// - Recursive rendering for nested collections
// - Expand/collapse animations
// - Drag-and-drop reordering
// - Right-click context menu
// - Active collection highlighting
// - Resource count badges
```

**Sidebar Behavior**:
- Desktop (>1024px): Always visible, 280px width
- Tablet (768-1024px): Collapsible, 240px width
- Mobile (<768px): Overlay drawer, full width

**Recommendations Panel**:
- Positioned below gallery
- Shows 5-10 recommended resources
- Based on active collection context
- "Add to Collection" quick action
- Collapsible to save space


## Data Models

### Frontend TypeScript Interfaces

```typescript
// types/resource.ts
export interface Resource {
  id: string;
  title: string;
  description: string | null;
  creator: string | null;
  publisher: string | null;
  date_created: string | null;
  type: string | null;
  format: string | null;
  source: string | null;
  subject: string[];
  classification_code: string | null;
  read_status: 'unread' | 'in_progress' | 'completed' | 'archived';
  quality_score: number;
  url: string | null;
  created_at: string;
  updated_at: string;
  ingestion_status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface ResourceCreate {
  title: string;
  description?: string;
  creator?: string;
  publisher?: string;
  source?: string;
  subject?: string[];
  classification_code?: string;
}

export interface ResourceUpdate {
  title?: string;
  description?: string;
  read_status?: ReadStatus;
  subject?: string[];
  classification_code?: string;
}

export interface ResourceListParams {
  page?: number;
  limit?: number;
  sort_by?: 'created_at' | 'updated_at' | 'quality_score' | 'title';
  sort_order?: 'asc' | 'desc';
  read_status?: ReadStatus;
  quality_min?: number;
  quality_max?: number;
  search?: string;
  tags?: string[];
}

// types/collection.ts
export interface Collection {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id: string | null;
  resource_count: number;
  created_at: string;
  updated_at: string;
}

export interface CollectionDetail extends Collection {
  resources: ResourceSummary[];
  subcollections: Collection[];
}

export interface CollectionCreate {
  name: string;
  description?: string;
  visibility?: 'private' | 'shared' | 'public';
  parent_id?: string;
}

export interface CollectionNode extends Collection {
  children: CollectionNode[];
  isExpanded: boolean;
  depth: number;
}

// types/search.ts
export interface SearchFilters {
  quality_min?: number;
  quality_max?: number;
  date_from?: string;
  date_to?: string;
  types?: string[];
  tags?: string[];
  read_status?: ReadStatus[];
}

export interface SearchResults {
  resources: Resource[];
  total: number;
  page: number;
  limit: number;
  facets: SearchFacets;
}

export interface SearchFacets {
  types: { value: string; count: number }[];
  tags: { value: string; count: number }[];
  quality_ranges: { range: string; count: number }[];
}
```


### Backend API Endpoints

**Resources API** (`/api/resources`):
```
GET    /api/resources              - List resources with pagination/filters
POST   /api/resources              - Create new resource
GET    /api/resources/{id}         - Get resource details
PUT    /api/resources/{id}         - Update resource
DELETE /api/resources/{id}         - Delete resource
PATCH  /api/resources/{id}/status  - Update read status
POST   /api/resources/{id}/archive - Archive resource
```

**Collections API** (`/api/collections`):
```
GET    /api/collections                      - List all collections
POST   /api/collections                      - Create collection
GET    /api/collections/{id}                 - Get collection with resources
PUT    /api/collections/{id}                 - Update collection
DELETE /api/collections/{id}                 - Delete collection
POST   /api/collections/{id}/resources       - Add resources to collection
DELETE /api/collections/{id}/resources       - Remove resources from collection
GET    /api/collections/{id}/recommendations - Get recommendations for collection
```

**Search API** (`/api/search`):
```
GET    /api/search                 - Full-text search with filters
GET    /api/search/suggestions     - Search suggestions/autocomplete
```

**Tags API** (`/api/tags`):
```
GET    /api/tags                   - List all tags with usage counts
GET    /api/tags/{tag}/resources   - Get resources by tag
```

**Quality API** (`/api/quality`):
```
GET    /api/quality/stats          - Quality score statistics
POST   /api/quality/recompute/{id} - Recompute quality score for resource
```

### API Response Formats

**Success Response**:
```json
{
  "data": { /* resource/collection object */ },
  "meta": {
    "timestamp": "2025-11-15T10:30:00Z",
    "version": "2.0.0"
  }
}
```

**List Response**:
```json
{
  "data": [ /* array of items */ ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "pages": 8
  }
}
```

**Error Response**:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource with ID xyz not found",
    "details": { /* optional additional context */ }
  }
}
```


## Error Handling

### Frontend Error Handling Strategy

**Error Boundaries**:
```typescript
// components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  // Catches React component errors
  // Displays fallback UI
  // Logs errors to monitoring service
}

// Usage: Wrap major sections
<ErrorBoundary fallback={<ErrorFallback />}>
  <Dashboard />
</ErrorBoundary>
```

**API Error Handling**:
```typescript
// services/api/errorHandler.ts
export class APIError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
  }
}

export function handleAPIError(error: any): APIError {
  if (error.response) {
    // Server responded with error status
    return new APIError(
      error.response.status,
      error.response.data.error.code,
      error.response.data.error.message,
      error.response.data.error.details
    );
  } else if (error.request) {
    // Request made but no response
    return new APIError(0, 'NETWORK_ERROR', 'Network connection failed');
  } else {
    // Something else happened
    return new APIError(0, 'UNKNOWN_ERROR', error.message);
  }
}
```

**User-Facing Error Messages**:
- Network errors: "Connection lost. Please check your internet."
- 404 errors: "Resource not found. It may have been deleted."
- 403 errors: "You don't have permission to access this."
- 500 errors: "Something went wrong. Please try again later."
- Validation errors: Display specific field errors inline

**Toast Notifications**:
```typescript
// Use toast library for non-blocking notifications
toast.error('Failed to archive resource');
toast.success('Resource added to collection');
toast.info('Syncing with server...');
toast.warning('Quality score below threshold');
```

### Backend Error Handling

**Consistent Error Responses**:
```python
# app/utils/errors.py
class APIException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

# Exception handler
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
```

**Validation Errors**:
- Use Pydantic validation
- Return 422 with field-specific errors
- Include helpful error messages


## Testing Strategy

### Frontend Testing

**Unit Tests** (Vitest):
- API client functions
- State management stores
- Utility functions
- Custom hooks

```typescript
// Example: resourceStore.test.ts
describe('ResourceStore', () => {
  it('should fetch resources and update state', async () => {
    const store = useResourceStore.getState();
    await store.fetchResources({ page: 1, limit: 20 });
    expect(store.resources).toHaveLength(20);
    expect(store.isLoading).toBe(false);
  });
  
  it('should handle fetch errors gracefully', async () => {
    // Mock API error
    const store = useResourceStore.getState();
    await store.fetchResources({ page: 1 });
    expect(store.error).toBeTruthy();
  });
});
```

**Component Tests** (React Testing Library):
- ResourceCard rendering
- Command Palette interactions
- Collection Tree navigation
- View mode switching

```typescript
// Example: ResourceCard.test.tsx
describe('ResourceCard', () => {
  it('should display resource information', () => {
    render(<ResourceCard resource={mockResource} viewMode="grid" />);
    expect(screen.getByText(mockResource.title)).toBeInTheDocument();
    expect(screen.getByText(`${mockResource.quality_score}`)).toBeInTheDocument();
  });
  
  it('should show quick actions on hover', async () => {
    render(<ResourceCard resource={mockResource} viewMode="grid" />);
    const card = screen.getByTestId('resource-card');
    await userEvent.hover(card);
    expect(screen.getByText('Read')).toBeVisible();
    expect(screen.getByText('Archive')).toBeVisible();
  });
});
```

**Integration Tests**:
- Full user flows (search → filter → view resource)
- Collection management workflows
- Command palette navigation

**E2E Tests** (Playwright - Optional):
- Critical user journeys
- Cross-browser compatibility
- Mobile responsiveness

### Backend Testing

**Unit Tests** (pytest):
- Service layer functions
- Data validation
- Business logic

**API Tests**:
- Endpoint responses
- Error handling
- Authentication/authorization

**Integration Tests**:
- Database operations
- Full request/response cycles
- External service mocking

### Testing Coverage Goals

- Frontend: 70%+ coverage for critical paths
- Backend: 80%+ coverage for services and routers
- Focus on user-facing functionality
- Prioritize integration tests over unit tests for UI


## Performance Optimizations

### Frontend Performance

**Code Splitting**:
- Lazy load route components
- Dynamic imports for heavy libraries
- Separate vendor bundles

**Image Optimization**:
- Lazy loading with Intersection Observer
- Responsive images (srcset)
- WebP format with fallbacks
- Thumbnail generation on backend

**Virtual Scrolling**:
- Implement for lists >100 items
- Use react-window or react-virtual
- Maintain scroll position on navigation

**Memoization**:
```typescript
// Memoize expensive computations
const filteredResources = useMemo(() => {
  return resources.filter(r => matchesFilters(r, filters));
}, [resources, filters]);

// Memoize callbacks
const handleArchive = useCallback((id: string) => {
  archiveResource(id);
}, [archiveResource]);
```

**Debouncing & Throttling**:
- Search input: 300ms debounce
- Scroll events: 100ms throttle
- Window resize: 200ms throttle

### Backend Performance

**Database Optimization**:
- Proper indexing on frequently queried fields
- Pagination for large result sets
- Eager loading for relationships
- Query result caching

**API Response Optimization**:
- Gzip compression
- Field selection (sparse fieldsets)
- Batch endpoints for multiple resources
- ETags for conditional requests

**Caching Strategy**:
- Redis for frequently accessed data
- Cache collection trees (5 min TTL)
- Cache search results (2 min TTL)
- Invalidate on mutations

### Network Optimization

**Request Batching**:
- Combine multiple resource fetches
- Batch collection updates
- GraphQL-style field selection

**Prefetching**:
- Prefetch next page on scroll
- Prefetch collection resources on hover
- Preload critical resources

**Compression**:
- Gzip/Brotli for text responses
- Optimize JSON payloads
- Remove unnecessary fields


## Mobile Responsiveness

### Breakpoints

```css
/* Mobile First Approach */
--mobile: 0-767px      /* Single column, touch-optimized */
--tablet: 768-1023px   /* 2 columns, hybrid touch/mouse */
--desktop: 1024-1439px /* 3-4 columns, mouse-optimized */
--wide: 1440px+        /* 4-6 columns, full features */
```

### Mobile Adaptations

**Navigation**:
- Hamburger menu for sidebar
- Bottom navigation bar for main sections
- Swipe gestures for navigation

**Card Layout**:
- Single column on mobile
- 2 columns on tablet
- Touch-friendly tap targets (44x44px minimum)

**Command Palette**:
- Full-screen overlay on mobile
- Larger touch targets
- Virtual keyboard optimization

**Quick Actions**:
- Replace hover with tap-to-reveal
- Swipe gestures for common actions:
  - Swipe left: Archive
  - Swipe right: Mark as read
  - Long press: Show context menu

**Images**:
- Smaller thumbnails on mobile
- Progressive loading
- Reduced quality for cellular connections

### Touch Interactions

```typescript
// Swipe gesture handler
const handleSwipe = (direction: 'left' | 'right', resourceId: string) => {
  if (direction === 'left') {
    archiveResource(resourceId);
  } else if (direction === 'right') {
    markAsRead(resourceId);
  }
};

// Long press handler
const handleLongPress = (resourceId: string) => {
  showContextMenu(resourceId);
};
```

### Performance on Mobile

- Reduce animations on low-end devices
- Lazy load images aggressively
- Minimize JavaScript bundle size
- Use CSS transforms for animations (GPU-accelerated)
- Implement service worker for offline support


## Phase Implementation Plan

### Phase 1: Foundation & UI/UX (Current Focus)

**Goals**:
- Establish backend connection infrastructure
- Implement core UI components
- Identify missing backend endpoints
- Create responsive layouts

**Deliverables**:
1. API client service with type safety
2. Zustand stores for state management
3. Card-based dashboard with 4 view modes
4. Command palette with keyboard navigation
5. Hybrid sidebar + gallery layout
6. Mobile-responsive design
7. Error handling and loading states
8. Documentation of required backend endpoints

**Backend Endpoints Needed** (to be implemented if missing):
- `GET /api/resources` with pagination and filters
- `PATCH /api/resources/{id}/status` for quick status updates
- `POST /api/resources/{id}/archive` for archiving
- `GET /api/collections/{id}/recommendations` for recommendation panel
- `GET /api/tags` for tag management
- `GET /api/search/suggestions` for autocomplete

### Phase 2: Additional Features (TBD)

**Placeholder for future features**:
- User will provide specific requirements
- May include: annotations, sharing, advanced search, etc.

### Phase 3: Full Integration & Polish

**Goals**:
- Connect all features to backend
- End-to-end testing
- Performance optimization
- Bug fixes and refinements

**Deliverables**:
1. All features working with real backend data
2. Comprehensive error handling
3. Loading states and optimistic updates
4. Performance benchmarks met
5. Mobile testing complete
6. User acceptance testing
7. Production-ready deployment

## Design Decisions & Rationale

### Why Zustand over Redux?
- Simpler API with less boilerplate
- Better TypeScript support
- Smaller bundle size
- Easier to learn and maintain
- Sufficient for application complexity

### Why Multiple View Modes?
- Different users have different preferences
- Context-dependent: scanning vs. deep reading
- Accessibility: some users prefer text-heavy layouts
- Competitive feature (Raindrop, Pocket, Readwise all have this)

### Why Command Palette?
- Power users demand keyboard efficiency
- Reduces UI clutter
- Discoverable through Cmd+K (industry standard)
- Extensible for future commands
- Improves accessibility

### Why Hybrid Sidebar Layout?
- Best of both worlds: navigation + content
- Industry standard (Notion, Obsidian, Raindrop)
- Supports hierarchical organization
- Collapsible for focus mode
- Mobile-friendly with drawer pattern

## Security Considerations

### Frontend Security

**XSS Prevention**:
- React's built-in escaping
- Sanitize user-generated content
- Content Security Policy headers

**CSRF Protection**:
- CSRF tokens for mutations
- SameSite cookie attributes
- Verify origin headers

**Authentication**:
- JWT tokens in httpOnly cookies
- Token refresh mechanism
- Automatic logout on expiry

### Backend Security

**Input Validation**:
- Pydantic schemas for all inputs
- SQL injection prevention (SQLAlchemy ORM)
- File upload validation

**Rate Limiting**:
- Per-endpoint rate limits
- IP-based throttling
- Authenticated user quotas

**CORS Configuration**:
- Whitelist frontend origins
- Credentials support
- Preflight caching

## Monitoring & Observability

### Frontend Monitoring

**Error Tracking**:
- Sentry or similar for error reporting
- Source maps for production debugging
- User context in error reports

**Performance Monitoring**:
- Core Web Vitals tracking
- API response time metrics
- Bundle size monitoring

**User Analytics**:
- Page view tracking
- Feature usage metrics
- User flow analysis

### Backend Monitoring

**Logging**:
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging

**Metrics**:
- Request rate and latency
- Error rates by endpoint
- Database query performance

**Health Checks**:
- `/health` endpoint for uptime monitoring
- Database connection checks
- External service status

## Deployment Considerations

### Frontend Deployment

**Build Process**:
```bash
npm run build
# Outputs to dist/
# Static files ready for CDN
```

**Hosting Options**:
- Vercel (recommended for Vite)
- Netlify
- AWS S3 + CloudFront
- Self-hosted Nginx

**Environment Variables**:
```
VITE_API_BASE_URL=https://api.example.com
VITE_ENVIRONMENT=production
```

### Backend Deployment

**Containerization**:
- Docker image with Python 3.11+
- Multi-stage build for optimization
- Health check endpoint

**Hosting Options**:
- AWS ECS/Fargate
- Google Cloud Run
- DigitalOcean App Platform
- Self-hosted with Gunicorn + Nginx

**Environment Variables**:
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
CORS_ORIGINS=https://app.example.com
```

### CI/CD Pipeline

**Frontend**:
1. Run tests (Vitest)
2. Build production bundle
3. Deploy to hosting platform
4. Invalidate CDN cache

**Backend**:
1. Run tests (pytest)
2. Build Docker image
3. Push to container registry
4. Deploy to hosting platform
5. Run database migrations

## Conclusion

This design provides a comprehensive blueprint for integrating the Neo Alexandria frontend with the backend API. The architecture emphasizes:

- **Type safety** through TypeScript interfaces
- **Performance** through optimization strategies
- **User experience** through multiple view modes and responsive design
- **Maintainability** through clear separation of concerns
- **Scalability** through efficient state management and caching

Phase 1 focuses on establishing the foundation with core UI components and backend connectivity. Subsequent phases will build upon this foundation to deliver a complete, production-ready application.
