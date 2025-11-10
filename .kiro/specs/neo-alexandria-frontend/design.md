# Design Document

## Overview

The Neo Alexandria 2.0 Frontend is a sophisticated React-based single-page application that provides researchers with a futuristic, highly animated interface for knowledge management. The design emphasizes visual elegance through a carefully crafted 60:30:10 color scheme, extensive micro-interactions, and smooth transitions while maintaining professional functionality and accessibility.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Client)                         │
├─────────────────────────────────────────────────────────────┤
│  React Application (SPA)                                     │
│  ├── React Router (Navigation)                               │
│  ├── TanStack Query (Data Fetching & Caching)               │
│  ├── Zustand (Global State Management)                      │
│  ├── Axios (HTTP Client)                                     │
│  └── Framer Motion (Animation Engine)                       │
├─────────────────────────────────────────────────────────────┤
│  Component Layer                                             │
│  ├── Pages (Route Components)                                │
│  ├── Features (Domain-Specific Components)                   │
│  ├── UI Components (Reusable Primitives)                    │
│  └── Layouts (Page Structures)                              │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                              │
│  ├── API Client (Backend Communication)                     │
│  ├── Storage Service (LocalStorage/SessionStorage)          │
│  └── Analytics Service (User Tracking)                      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                           │
│  Port: 8000                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core Framework:**
- React 18.3.1 - UI library with concurrent features
- TypeScript 5.6.2 - Type-safe development
- Vite 5.4.7 - Fast build tool and dev server

**State Management:**
- Zustand 5.0.0 - Lightweight global state
- TanStack Query 5.56.2 - Server state management with caching

**Routing:**
- React Router DOM 6.26.2 - Client-side routing with nested routes

**Styling:**
- TailwindCSS 3.4.12 - Utility-first CSS framework
- Custom CSS variables for color scheme
- Tailwind Merge 2.5.2 - Class name merging utility

**Animation:**
- Framer Motion 11.x (to be added) - Production-ready animation library
- CSS transitions for simple animations
- GSAP 3.x (to be added) - Advanced timeline animations

**Data Visualization:**
- D3.js 7.9.0 - Low-level visualization primitives
- React Force Graph 2D 1.25.4 - Force-directed graph visualization
- Recharts 2.x (to be added) - React chart library

**UI Components:**
- Headless UI 2.1.8 - Unstyled accessible components
- Heroicons 2.1.5 - Icon library
- Lucide React 0.441.0 - Additional icon set

**HTTP & Data:**
- Axios 1.7.7 - HTTP client with interceptors
- date-fns 4.1.0 - Date manipulation

## Components and Interfaces

### Component Hierarchy

```
App
├── AppLayout
│   ├── TransparentNavbar
│   │   ├── NavLogo (animated)
│   │   ├── NavLinks (with hover effects)
│   │   ├── SearchBar (quick search)
│   │   └── UserMenu (dropdown)
│   ├── PageTransition (route wrapper)
│   └── Footer
│
├── Pages
│   ├── HomePage
│   │   ├── HeroSection (animated background)
│   │   ├── RecommendationsFeed
│   │   ├── QuickSearchPanel
│   │   └── RecentActivityTimeline
│   │
│   ├── LibraryPage
│   │   ├── LibraryHeader (filters, view toggle)
│   │   ├── FacetedSearchSidebar
│   │   ├── ResourceGrid/ResourceList
│   │   ├── BulkActionBar
│   │   └── UploadResourceModal
│   │
│   ├── ResourceDetailPage
│   │   ├── ResourceHeader (metadata, actions)
│   │   ├── ContentViewer (with annotations)
│   │   ├── KnowledgeGraphPanel
│   │   ├── CitationNetworkPanel
│   │   ├── VersionHistoryTimeline
│   │   └── QualityMetricsCard
│   │
│   ├── ClassificationPage
│   │   ├── ClassificationTree (expandable)
│   │   ├── ResourceListByClassification
│   │   └── BulkClassifyModal
│   │
│   └── ProfilePage
│       ├── PreferencesPanel
│       ├── AccountSettingsPanel
│       └── NotificationPreferencesPanel
│
└── Shared Components
    ├── AnimatedCard
    ├── SkeletonLoader
    ├── LoadingSpinner
    ├── ErrorBoundary
    ├── Toast/Notification
    ├── Modal
    ├── Dropdown
    ├── Tooltip
    └── Button (with variants)
```

### Key Component Specifications

#### TransparentNavbar Component

**Props:**
```typescript
interface TransparentNavbarProps {
  className?: string;
}
```

**State:**
- `isScrolled: boolean` - Tracks scroll position
- `isMobileMenuOpen: boolean` - Mobile menu state

**Behavior:**
- Listens to scroll events with throttling (100ms)
- Transitions background from transparent to solid at 50px scroll
- Applies backdrop-blur-md when solid
- Collapses to hamburger menu on mobile (<768px)

**Styling:**
- Transparent: `bg-transparent`
- Scrolled: `bg-charcoal-grey-900/95 backdrop-blur-md shadow-lg`
- Transition: `transition-all duration-200 ease-in-out`

#### KnowledgeGraphPanel Component

**Props:**
```typescript
interface KnowledgeGraphPanelProps {
  resourceId: string;
  maxNodes?: number; // default: 50
  onNodeClick?: (nodeId: string) => void;
}
```

**Data Structure:**
```typescript
interface GraphNode {
  id: string;
  title: string;
  type: string;
  classification_code: string;
}

interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  details: {
    connection_type: string;
    vector_similarity?: number;
    shared_subjects?: string[];
  };
}
```

**Visualization:**
- Uses react-force-graph-2d for rendering
- Node size based on importance/quality score
- Node color based on classification_code
- Edge thickness based on weight
- Hover tooltips with resource details
- Click navigation to resource detail

#### ResourceCard Component

**Props:**
```typescript
interface ResourceCardProps {
  resource: Resource;
  variant?: 'grid' | 'list';
  isSelected?: boolean;
  onSelect?: (id: string) => void;
  onAction?: (action: string, id: string) => void;
}
```

**Features:**
- Animated hover effects (scale, shadow)
- Quality score badge with color coding
- Classification badge
- Read status indicator
- Quick actions menu (edit, delete, add to collection)
- Skeleton loader variant

## Data Models

### Frontend Type Definitions

```typescript
// Resource Types
interface Resource {
  id: string;
  title: string;
  description?: string;
  creator?: string;
  publisher?: string;
  source: string;
  language?: string;
  type?: string;
  subject: string[];
  classification_code?: string;
  quality_score?: number;
  read_status: 'unread' | 'in_progress' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
  ingestion_status?: 'pending' | 'processing' | 'completed' | 'failed';
  ingestion_error?: string;
}

// Search Types
interface SearchRequest {
  text: string;
  hybrid_weight?: number; // 0.0-1.0
  filters?: SearchFilters;
  limit?: number;
  offset?: number;
  sort_by?: 'relevance' | 'updated_at' | 'created_at' | 'quality_score' | 'title';
  sort_dir?: 'asc' | 'desc';
}

interface SearchFilters {
  classification_code?: string[];
  language?: string[];
  type?: string[];
  read_status?: string[];
  min_quality?: number;
  max_quality?: number;
  subject_any?: string[];
  subject_all?: string[];
}

interface SearchResponse {
  total: number;
  items: Resource[];
  facets: {
    classification_code: FacetItem[];
    type: FacetItem[];
    language: FacetItem[];
    read_status: FacetItem[];
    subject: FacetItem[];
  };
}

interface FacetItem {
  key: string;
  count: number;
}

// Collection Types
interface Collection {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id?: string;
  created_at: string;
  updated_at: string;
  resource_count: number;
  resources?: Resource[];
  subcollections?: Collection[];
}

// Graph Types
interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Citation Types
interface Citation {
  id: string;
  source_resource_id: string;
  target_resource_id?: string;
  target_url: string;
  citation_type: 'reference' | 'dataset' | 'code' | 'general';
  context_snippet?: string;
  importance_score?: number;
}

// Recommendation Types
interface Recommendation {
  url: string;
  title: string;
  snippet: string;
  relevance_score: number;
  reasoning: string[];
}

// User Preferences
interface UserPreferences {
  subjects: string[];
  languages: string[];
  notifications: {
    ingestion_complete: boolean;
    quality_updates: boolean;
    recommendations: boolean;
  };
  display: {
    theme: 'dark' | 'light';
    defaultView: 'grid' | 'list';
    itemsPerPage: number;
  };
}
```

## Color Scheme Design

### Color Palette

**Primary Colors (60% - Charcoal Grey):**
```css
--charcoal-grey-50: #F7FAFC;
--charcoal-grey-100: #EDF2F7;
--charcoal-grey-200: #E2E8F0;
--charcoal-grey-300: #CBD5E0;
--charcoal-grey-400: #A0AEC0;
--charcoal-grey-500: #718096;
--charcoal-grey-600: #4A5568;
--charcoal-grey-700: #2D3748;
--charcoal-grey-800: #1A202C;
--charcoal-grey-900: #171923;
```

**Secondary Colors (30% - Neutral Blue):**
```css
--neutral-blue-50: #EBF8FF;
--neutral-blue-100: #BEE3F8;
--neutral-blue-200: #90CDF4;
--neutral-blue-300: #63B3ED;
--neutral-blue-400: #4299E1;
--neutral-blue-500: #3182CE;
--neutral-blue-600: #2B6CB0;
--neutral-blue-700: #2C5282;
--neutral-blue-800: #2A4365;
--neutral-blue-900: #1A365D;
```

**Accent Colors (10% - Blue):**
```css
--accent-blue-50: #EFF6FF;
--accent-blue-100: #DBEAFE;
--accent-blue-200: #BFDBFE;
--accent-blue-300: #93C5FD;
--accent-blue-400: #60A5FA;
--accent-blue-500: #3B82F6;
--accent-blue-600: #2563EB;
--accent-blue-700: #1D4ED8;
--accent-blue-800: #1E40AF;
--accent-blue-900: #1E3A8A;
```

### Color Usage Guidelines

**Backgrounds:**
- Primary background: `charcoal-grey-900`
- Secondary background: `charcoal-grey-800`
- Card backgrounds: `charcoal-grey-700` with subtle gradient
- Hover states: `charcoal-grey-600`

**Text:**
- Primary text: `charcoal-grey-50`
- Secondary text: `charcoal-grey-300`
- Muted text: `charcoal-grey-400`

**Interactive Elements:**
- Primary buttons: `accent-blue-500` with hover `accent-blue-600`
- Secondary buttons: `neutral-blue-600` with hover `neutral-blue-700`
- Links: `accent-blue-400` with hover `accent-blue-300`
- Focus rings: `accent-blue-500`

**Status Indicators:**
- Success: `#10B981` (green)
- Warning: `#F59E0B` (amber)
- Error: `#EF4444` (red)
- Info: `accent-blue-500`

## Animation System

### Animation Principles

1. **Purposeful**: Every animation serves a functional purpose
2. **Performant**: Use GPU-accelerated properties (transform, opacity)
3. **Consistent**: Maintain consistent timing and easing
4. **Subtle**: Animations enhance, not distract

### Animation Specifications

**Timing Functions:**
```css
--ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0.0, 1, 1);
--spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

**Duration Scale:**
```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;
```

**Micro-interactions:**
- Button hover: scale(1.02) + shadow, 150ms
- Card hover: translateY(-4px) + shadow, 200ms
- Input focus: border color + ring, 150ms
- Checkbox toggle: scale + rotate, 200ms

**Page Transitions:**
- Route change: fade + slide (300ms)
- Modal open: scale(0.95 → 1) + fade (200ms)
- Dropdown: slide + fade (150ms)

**Loading States:**
- Skeleton shimmer: linear gradient animation (1.5s infinite)
- Spinner: rotate (1s infinite linear)
- Progress bar: width transition (300ms)

**Scroll Animations:**
- Navbar background: 200ms ease-out
- Parallax elements: transform based on scroll position
- Fade-in on scroll: intersection observer + fade (500ms)

### Framer Motion Variants

```typescript
// Page transitions
const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
};

const pageTransition = {
  type: 'tween',
  ease: 'easeInOut',
  duration: 0.3
};

// Card animations
const cardVariants = {
  rest: { scale: 1, y: 0 },
  hover: { 
    scale: 1.02, 
    y: -4,
    transition: { duration: 0.2 }
  }
};

// Stagger children
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};
```

## API Integration

### API Client Configuration

```typescript
// src/services/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);
```

### TanStack Query Configuration

```typescript
// src/services/api/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});
```

### API Service Modules

```typescript
// src/services/api/resources.ts
export const resourcesApi = {
  getAll: (params: GetResourcesParams) => 
    apiClient.get<ResourceListResponse>('/resources', { params }),
  
  getById: (id: string) => 
    apiClient.get<Resource>(`/resources/${id}`),
  
  create: (data: CreateResourceRequest) => 
    apiClient.post<Resource>('/resources', data),
  
  update: (id: string, data: UpdateResourceRequest) => 
    apiClient.put<Resource>(`/resources/${id}`, data),
  
  delete: (id: string) => 
    apiClient.delete(`/resources/${id}`),
  
  getStatus: (id: string) => 
    apiClient.get<IngestionStatus>(`/resources/${id}/status`)
};

// src/services/api/search.ts
export const searchApi = {
  search: (request: SearchRequest) => 
    apiClient.post<SearchResponse>('/search', request),
  
  getSuggestions: (query: string) => 
    apiClient.get<string[]>('/authority/subjects/suggest', { 
      params: { q: query } 
    })
};

// src/services/api/graph.ts
export const graphApi = {
  getNeighbors: (resourceId: string, limit?: number) => 
    apiClient.get<GraphData>(`/graph/resource/${resourceId}/neighbors`, { 
      params: { limit } 
    }),
  
  getOverview: (limit?: number, threshold?: number) => 
    apiClient.get<GraphData>('/graph/overview', { 
      params: { limit, vector_threshold: threshold } 
    })
};

// src/services/api/collections.ts
export const collectionsApi = {
  getAll: (params: GetCollectionsParams) => 
    apiClient.get<CollectionListResponse>('/collections', { params }),
  
  getById: (id: string, userId?: string) => 
    apiClient.get<Collection>(`/collections/${id}`, { 
      params: { user_id: userId } 
    }),
  
  create: (data: CreateCollectionRequest, userId: string) => 
    apiClient.post<Collection>('/collections', data, { 
      params: { user_id: userId } 
    }),
  
  addResources: (id: string, resourceIds: string[], userId: string) => 
    apiClient.post(`/collections/${id}/resources`, 
      { resource_ids: resourceIds }, 
      { params: { user_id: userId } }
    ),
  
  getRecommendations: (id: string, userId?: string, limit?: number) => 
    apiClient.get<CollectionRecommendations>(
      `/collections/${id}/recommendations`, 
      { params: { user_id: userId, limit } }
    )
};

// src/services/api/citations.ts
export const citationsApi = {
  getCitations: (resourceId: string, direction?: string) => 
    apiClient.get<CitationResponse>(
      `/citations/resources/${resourceId}/citations`, 
      { params: { direction } }
    ),
  
  getGraph: (params: CitationGraphParams) => 
    apiClient.get<GraphData>('/citations/graph/citations', { params })
};
```

### Custom Hooks

```typescript
// src/hooks/useResources.ts
export function useResources(params: GetResourcesParams) {
  return useQuery({
    queryKey: ['resources', params],
    queryFn: () => resourcesApi.getAll(params)
  });
}

export function useResource(id: string) {
  return useQuery({
    queryKey: ['resource', id],
    queryFn: () => resourcesApi.getById(id),
    enabled: !!id
  });
}

export function useCreateResource() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: resourcesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
    }
  });
}

// src/hooks/useSearch.ts
export function useSearch(request: SearchRequest) {
  return useQuery({
    queryKey: ['search', request],
    queryFn: () => searchApi.search(request),
    enabled: !!request.text
  });
}

// src/hooks/useKnowledgeGraph.ts
export function useKnowledgeGraph(resourceId: string, limit?: number) {
  return useQuery({
    queryKey: ['graph', 'neighbors', resourceId, limit],
    queryFn: () => graphApi.getNeighbors(resourceId, limit),
    enabled: !!resourceId
  });
}
```

## State Management

### Zustand Store Structure

```typescript
// src/store/useAppStore.ts
interface AppState {
  // UI State
  isSidebarOpen: boolean;
  theme: 'dark' | 'light';
  
  // User State
  userId: string | null;
  preferences: UserPreferences;
  
  // Selection State
  selectedResources: string[];
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setUserId: (id: string | null) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  toggleResourceSelection: (id: string) => void;
  clearSelection: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      isSidebarOpen: true,
      theme: 'dark',
      userId: null,
      preferences: defaultPreferences,
      selectedResources: [],
      
      toggleSidebar: () => set((state) => ({ 
        isSidebarOpen: !state.isSidebarOpen 
      })),
      
      setTheme: (theme) => set({ theme }),
      
      setUserId: (userId) => set({ userId }),
      
      updatePreferences: (prefs) => set((state) => ({
        preferences: { ...state.preferences, ...prefs }
      })),
      
      toggleResourceSelection: (id) => set((state) => ({
        selectedResources: state.selectedResources.includes(id)
          ? state.selectedResources.filter(rid => rid !== id)
          : [...state.selectedResources, id]
      })),
      
      clearSelection: () => set({ selectedResources: [] })
    }),
    {
      name: 'neo-alexandria-storage',
      partialize: (state) => ({
        theme: state.theme,
        userId: state.userId,
        preferences: state.preferences
      })
    }
  )
);
```

## Routing Structure

```typescript
// src/App.tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />
      },
      {
        path: 'library',
        element: <LibraryPage />
      },
      {
        path: 'resources/:id',
        element: <ResourceDetailPage />
      },
      {
        path: 'classification',
        element: <ClassificationPage />
      },
      {
        path: 'collections',
        children: [
          {
            index: true,
            element: <CollectionsPage />
          },
          {
            path: ':id',
            element: <CollectionDetailPage />
          }
        ]
      },
      {
        path: 'profile',
        element: <ProfilePage />
      },
      {
        path: 'search',
        element: <SearchPage />
      }
    ]
  }
]);
```

## Error Handling

### Error Boundary

```typescript
// src/components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component<Props, State> {
  // Catches React errors
  // Displays fallback UI
  // Logs errors to service
}
```

### API Error Handling

```typescript
// src/utils/errorHandling.ts
export function handleApiError(error: unknown): ErrorMessage {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      return {
        title: 'Request Failed',
        message: error.response.data.detail || 'An error occurred',
        code: error.response.status
      };
    } else if (error.request) {
      return {
        title: 'Network Error',
        message: 'Unable to reach the server',
        code: 0
      };
    }
  }
  
  return {
    title: 'Unexpected Error',
    message: 'An unexpected error occurred',
    code: -1
  };
}
```

## Testing Strategy

### Unit Tests
- Component rendering and props
- Custom hooks behavior
- Utility functions
- State management logic

### Integration Tests
- API service integration
- Component interactions
- Form submissions
- Navigation flows

### E2E Tests (Playwright)
- Critical user journeys
- Resource creation flow
- Search and filter
- Collection management

### Visual Regression Tests
- Component snapshots
- Animation states
- Responsive layouts

## Performance Optimization

### Code Splitting
```typescript
// Lazy load routes
const LibraryPage = lazy(() => import('./pages/LibraryPage'));
const ResourceDetailPage = lazy(() => import('./pages/ResourceDetailPage'));
```

### Memoization
```typescript
// Memoize expensive computations
const sortedResources = useMemo(() => 
  resources.sort((a, b) => b.quality_score - a.quality_score),
  [resources]
);

// Memoize callbacks
const handleSelect = useCallback((id: string) => {
  toggleResourceSelection(id);
}, [toggleResourceSelection]);
```

### Virtual Scrolling
- Use react-window for large lists
- Render only visible items
- Reduce DOM nodes

### Image Optimization
- Lazy load images
- Use WebP format with fallbacks
- Implement blur-up technique

## Accessibility

### WCAG 2.1 Level AA Compliance

**Keyboard Navigation:**
- All interactive elements focusable
- Logical tab order
- Skip links for main content
- Escape key closes modals

**Screen Readers:**
- Semantic HTML elements
- ARIA labels and descriptions
- Live regions for dynamic content
- Alt text for images

**Color Contrast:**
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text
- Focus indicators visible

**Motion:**
- Respect prefers-reduced-motion
- Disable animations when requested
- Provide static alternatives

## Deployment Configuration

### Environment Variables

```env
# .env.development
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_NAME=Neo Alexandria 2.0
VITE_ENABLE_ANALYTICS=false

# .env.production
VITE_API_BASE_URL=https://api.neoalexandria.com
VITE_APP_NAME=Neo Alexandria 2.0
VITE_ENABLE_ANALYTICS=true
```

### Build Configuration

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['framer-motion', '@headlessui/react'],
          'data-vendor': ['@tanstack/react-query', 'axios', 'zustand'],
          'viz-vendor': ['d3', 'react-force-graph-2d']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
});
```

## Security Considerations

- XSS prevention through React's built-in escaping
- CSRF protection via API tokens
- Content Security Policy headers
- Secure storage of sensitive data
- Input validation and sanitization
- Rate limiting on client side
