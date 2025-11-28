# Design Document

## Overview

This design document outlines the architecture for implementing the Neo Alexandria frontend in 2 major phases, consolidating the original 10-phase roadmap while maintaining all features. The design builds incrementally on the existing minimal setup (dashboard, library panel, fuzzy search, light/dark mode) and ensures the application remains production-ready at every milestone.

### Design Philosophy

1. **Always Production Ready**: Each phase ends with a deployable application
2. **UI Polish First**: Visual refinements integrated into feature development
3. **Progressive Enhancement**: Core functionality works without JavaScript where possible
4. **Performance Budget**: Every feature meets defined performance thresholds
5. **Accessibility Default**: WCAG compliance built in from the start
6. **Mobile Consideration**: Responsive design throughout

### Phase Structure

**Phase 1: Core Platform (12 weeks)**
- Foundation Enhancement (1 week)
- Core Resource Management (3 weeks)
- Search and Discovery (3 weeks)
- Collections and Organization (3 weeks)
- Performance and Accessibility Baseline (2 weeks)

**Phase 2: Advanced Intelligence (13 weeks)**
- Recommendations and Personalization (2 weeks)
- Annotations and Active Reading (3 weeks)
- Knowledge Graph and Discovery (3 weeks)
- Quality and Curation (2 weeks)
- Taxonomy and Classification (2 weeks)
- System Monitoring (1 week)
- Final Polish and Performance (2 weeks)

**Total Timeline**: 25 weeks (approximately 6 months)

## Architecture

### Technology Stack

**Frontend Framework**: React 18+ with TypeScript
- Chosen for component reusability, strong typing, and ecosystem maturity
- Hooks-based architecture for state management
- Concurrent rendering for improved UX

**State Management**: Zustand + React Query
- Zustand for global UI state (theme, command palette, notifications)
- React Query for server state management (caching, invalidation, optimistic updates)
- Local state with useState/useReducer for component-specific state

**Routing**: React Router v6
- Code splitting at route level
- Nested routes for hierarchical navigation
- Lazy loading for performance

**Styling**: CSS Modules + Tailwind CSS
- CSS Modules for component-scoped styles
- Tailwind for utility-first rapid development
- CSS custom properties for theming

**Animation**: Framer Motion
- Declarative animations with motion preferences support
- Layout animations for smooth transitions
- Gesture support for mobile interactions

**Data Visualization**: D3.js + Recharts
- D3 for custom graph visualizations (knowledge graph, citation network)
- Recharts for standard charts (histograms, bar charts, radar charts)

**PDF Viewing**: React-PDF
- PDF rendering with zoom and navigation
- Text selection support for annotations

**Testing**: Vitest + React Testing Library + Playwright
- Unit tests with Vitest
- Component tests with React Testing Library
- E2E tests with Playwright
- Accessibility tests with axe-core

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pages   │  │Components│  │  Hooks   │  │ Contexts │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      State Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Zustand  │  │React Query│ │  Local   │  │ Derived  │   │
│  │  Store   │  │  Cache   │  │  State   │  │  State   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │WebSocket │  │  Local   │  │Analytics │   │
│  │ Client   │  │  Client  │  │ Storage  │  │  Client  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Layer                         │
│                  (Existing FastAPI Backend)                  │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/           # Reusable UI components
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   ├── Toast/
│   │   │   ├── Skeleton/
│   │   │   └── ...
│   │   ├── layout/           # Layout components
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── CommandPalette/
│   │   │   └── ...
│   │   ├── resource/         # Resource-specific components
│   │   │   ├── ResourceCard/
│   │   │   ├── ResourceList/
│   │   │   ├── ResourceDetail/
│   │   │   ├── UploadZone/
│   │   │   └── ...
│   │   ├── search/           # Search components
│   │   │   ├── SearchBar/
│   │   │   ├── SearchStudio/
│   │   │   ├── SearchResults/
│   │   │   └── ...
│   │   ├── collection/       # Collection components
│   │   ├── annotation/       # Annotation components
│   │   ├── graph/            # Graph visualization components
│   │   ├── quality/          # Quality dashboard components
│   │   ├── taxonomy/         # Taxonomy components
│   │   └── monitoring/       # Monitoring components
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── Library/
│   │   ├── ResourceDetail/
│   │   ├── Search/
│   │   ├── SearchStudio/
│   │   ├── Collections/
│   │   ├── CollectionDetail/
│   │   ├── Annotations/
│   │   ├── Graph/
│   │   ├── Quality/
│   │   ├── Taxonomy/
│   │   ├── Profile/
│   │   ├── Monitoring/
│   │   └── Analytics/
│   ├── hooks/
│   │   ├── useResources.ts
│   │   ├── useSearch.ts
│   │   ├── useCollections.ts
│   │   ├── useAnnotations.ts
│   │   ├── useGraph.ts
│   │   ├── useKeyboard.ts
│   │   ├── useInfiniteScroll.ts
│   │   ├── useMediaQuery.ts
│   │   └── ...
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── resources.ts
│   │   │   ├── search.ts
│   │   │   ├── collections.ts
│   │   │   ├── annotations.ts
│   │   │   ├── graph.ts
│   │   │   ├── quality.ts
│   │   │   ├── taxonomy.ts
│   │   │   └── ...
│   │   ├── websocket/
│   │   │   └── client.ts
│   │   ├── storage/
│   │   │   └── localStorage.ts
│   │   └── analytics/
│   │       └── tracker.ts
│   ├── store/
│   │   ├── uiStore.ts        # UI state (theme, modals, etc.)
│   │   ├── commandStore.ts   # Command palette state
│   │   ├── toastStore.ts     # Toast notifications
│   │   └── ...
│   ├── utils/
│   │   ├── animations.ts
│   │   ├── formatting.ts
│   │   ├── validation.ts
│   │   ├── accessibility.ts
│   │   └── ...
│   ├── types/
│   │   ├── resource.ts
│   │   ├── collection.ts
│   │   ├── annotation.ts
│   │   ├── search.ts
│   │   └── ...
│   ├── styles/
│   │   ├── globals.css
│   │   ├── theme.css
│   │   ├── animations.css
│   │   └── variables.css
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── package.json
```

## Components and Interfaces

### Core UI Components

#### 1. Command Palette
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Command {
  id: string;
  label: string;
  icon?: React.ReactNode;
  shortcut?: string;
  action: () => void;
  category: 'navigation' | 'search' | 'action';
}
```

**Features**:
- Fuzzy search across commands
- Keyboard navigation (arrow keys, Enter, Escape)
- Recent commands history
- Command categories with visual separation
- Keyboard shortcut display

#### 2. Toast Notification System
```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearAll: () => void;
}
```

**Features**:
- Queue management (max 3 visible)
- Auto-dismiss with configurable duration
- Manual dismiss
- Action buttons (e.g., "Undo")
- Stacked positioning with animations

#### 3. Skeleton Loading Components
```typescript
interface SkeletonProps {
  variant: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}
```

**Variants**:
- `SkeletonCard`: Matches resource card layout
- `SkeletonList`: Matches list view layout
- `SkeletonDetail`: Matches detail page layout
- `SkeletonGraph`: Matches graph visualization layout

#### 4. Resource Components

**ResourceCard**:
```typescript
interface ResourceCardProps {
  resource: Resource;
  view: 'card' | 'list' | 'compact';
  isSelected?: boolean;
  onSelect?: (id: string) => void;
  onClick?: (id: string) => void;
}

interface Resource {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  type: 'pdf' | 'url' | 'arxiv';
  thumbnail?: string;
  qualityScore: number;
  classification: string[];
  createdAt: Date;
  updatedAt: Date;
}
```

**ResourceList**:
```typescript
interface ResourceListProps {
  resources: Resource[];
  view: 'card' | 'list' | 'compact';
  density: 'comfortable' | 'compact' | 'spacious';
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}
```

**UploadZone**:
```typescript
interface UploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  onUrlSubmit: (url: string) => void;
  accept?: string;
  maxFiles?: number;
  maxSize?: number;
}

interface UploadProgress {
  id: string;
  filename: string;
  progress: number;
  stage: 'uploading' | 'extracting' | 'analyzing' | 'complete' | 'error';
  error?: string;
}
```

#### 5. Search Components

**SearchBar**:
```typescript
interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (query: string) => void;
  suggestions: SearchSuggestion[];
  history: string[];
  quickFilters: QuickFilter[];
  isLoading: boolean;
}

interface SearchSuggestion {
  text: string;
  type: 'resource' | 'collection' | 'tag' | 'author';
  highlight: [number, number][];
}

interface QuickFilter {
  id: string;
  label: string;
  filter: SearchFilter;
}
```

**SearchStudio**:
```typescript
interface SearchStudioProps {
  onSearch: (query: SearchQuery) => void;
  savedSearches: SavedSearch[];
}

interface SearchQuery {
  text: string;
  booleanOperators: BooleanExpression[];
  weights: {
    keyword: number;
    semantic: number;
    sparse: number;
  };
  method: 'fts5' | 'vector' | 'hybrid';
  filters: SearchFilter[];
}

interface BooleanExpression {
  operator: 'AND' | 'OR' | 'NOT';
  terms: string[];
}
```

**SearchResults**:
```typescript
interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
  sortBy: SortOption;
  onSortChange: (sort: SortOption) => void;
}

interface SearchResult {
  resource: Resource;
  score: number;
  explanation: RelevanceExplanation;
  highlights: Highlight[];
}

interface RelevanceExplanation {
  keywordScore: number;
  semanticScore: number;
  sparseScore: number;
  factors: string[];
}

interface Highlight {
  field: 'title' | 'abstract' | 'content';
  text: string;
  start: number;
  end: number;
}
```

#### 6. Collection Components

**CollectionCard**:
```typescript
interface CollectionCardProps {
  collection: Collection;
  onClick: (id: string) => void;
  onDelete: (id: string) => void;
}

interface Collection {
  id: string;
  name: string;
  description: string;
  thumbnail?: string;
  resourceCount: number;
  type: 'manual' | 'smart';
  rules?: CollectionRule[];
  createdAt: Date;
  updatedAt: Date;
}
```

**CollectionRuleBuilder**:
```typescript
interface CollectionRuleBuilderProps {
  rules: CollectionRule[];
  onChange: (rules: CollectionRule[]) => void;
  matchCount: number;
}

interface CollectionRule {
  id: string;
  field: 'quality' | 'classification' | 'author' | 'date' | 'tag';
  operator: '>' | '<' | '=' | 'contains' | 'in';
  value: any;
  logic: 'AND' | 'OR';
}
```

#### 7. Annotation Components

**AnnotationToolbar**:
```typescript
interface AnnotationToolbarProps {
  selection: TextSelection;
  onHighlight: (color: string) => void;
  onNote: () => void;
  onTag: (tags: string[]) => void;
  position: { x: number; y: number };
}

interface TextSelection {
  text: string;
  start: number;
  end: number;
  rects: DOMRect[];
}
```

**AnnotationSidebar**:
```typescript
interface AnnotationSidebarProps {
  annotations: Annotation[];
  scrollPosition: number;
  onAnnotationClick: (id: string) => void;
  onAnnotationEdit: (id: string, updates: Partial<Annotation>) => void;
  onAnnotationDelete: (id: string) => void;
}

interface Annotation {
  id: string;
  resourceId: string;
  type: 'highlight' | 'note' | 'tag';
  text: string;
  note?: string;
  tags: string[];
  color: string;
  position: {
    start: number;
    end: number;
    page?: number;
  };
  createdAt: Date;
  updatedAt: Date;
}
```

**AnnotationNotebook**:
```typescript
interface AnnotationNotebookProps {
  annotations: Annotation[];
  filters: AnnotationFilters;
  onFilterChange: (filters: AnnotationFilters) => void;
  groupBy: 'chronological' | 'resource' | 'tag';
  onGroupByChange: (groupBy: string) => void;
}

interface AnnotationFilters {
  resourceIds?: string[];
  tags?: string[];
  colors?: string[];
  dateRange?: [Date, Date];
  searchQuery?: string;
}
```

#### 8. Graph Components

**GraphCanvas**:
```typescript
interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout: 'force' | 'hierarchical' | 'circular';
  onNodeClick: (id: string) => void;
  onNodeExpand: (id: string) => void;
  selectedNodeId?: string;
}

interface GraphNode {
  id: string;
  label: string;
  type: 'resource' | 'concept' | 'author';
  cluster?: string;
  metadata: Record<string, any>;
  x?: number;
  y?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  type: 'citation' | 'similarity' | 'co-authorship';
  weight: number;
}
```

**DiscoveryPanel**:
```typescript
interface DiscoveryPanelProps {
  sourceNode: string;
  targetNode: string;
  paths: DiscoveryPath[];
  hypotheses: Hypothesis[];
  onPathSelect: (path: DiscoveryPath) => void;
  onHypothesisValidate: (id: string, valid: boolean) => void;
}

interface DiscoveryPath {
  nodes: string[];
  edges: GraphEdge[];
  score: number;
}

interface Hypothesis {
  id: string;
  description: string;
  plausibility: number;
  evidence: string[];
  status: 'pending' | 'validated' | 'rejected';
}
```

#### 9. Quality Components

**QualityDashboard**:
```typescript
interface QualityDashboardProps {
  distribution: QualityDistribution;
  trends: QualityTrend[];
  outliers: Resource[];
  onRecalculate: () => void;
}

interface QualityDistribution {
  bins: { min: number; max: number; count: number }[];
  mean: number;
  median: number;
  stdDev: number;
}

interface QualityTrend {
  dimension: string;
  values: { date: Date; score: number }[];
}
```

**QualityRadarChart**:
```typescript
interface QualityRadarChartProps {
  dimensions: QualityDimension[];
  animated: boolean;
}

interface QualityDimension {
  name: string;
  score: number;
  maxScore: number;
  description: string;
}
```

#### 10. Taxonomy Components

**TaxonomyTree**:
```typescript
interface TaxonomyTreeProps {
  nodes: TaxonomyNode[];
  selectedId?: string;
  onNodeSelect: (id: string) => void;
  onNodeMove: (id: string, newParentId: string) => void;
  onNodeCreate: (parentId: string, name: string) => void;
  onNodeEdit: (id: string, name: string) => void;
}

interface TaxonomyNode {
  id: string;
  name: string;
  parentId?: string;
  children: TaxonomyNode[];
  resourceCount: number;
  depth: number;
}
```

**ClassificationSuggestions**:
```typescript
interface ClassificationSuggestionsProps {
  resourceId: string;
  suggestions: ClassificationSuggestion[];
  onAccept: (suggestionId: string) => void;
  onReject: (suggestionId: string) => void;
}

interface ClassificationSuggestion {
  id: string;
  category: string;
  confidence: number;
  reasoning: string[];
}
```

## Data Models

### Frontend Data Models

```typescript
// Resource Model
interface Resource {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  content?: string;
  type: 'pdf' | 'url' | 'arxiv';
  url?: string;
  filePath?: string;
  thumbnail?: string;
  qualityScore: number;
  qualityDimensions: QualityDimension[];
  classification: string[];
  tags: string[];
  metadata: ResourceMetadata;
  createdAt: Date;
  updatedAt: Date;
}

interface ResourceMetadata {
  doi?: string;
  arxivId?: string;
  publicationDate?: Date;
  journal?: string;
  citationCount?: number;
  pageCount?: number;
  fileSize?: number;
}

// Collection Model
interface Collection {
  id: string;
  name: string;
  description: string;
  type: 'manual' | 'smart';
  parentId?: string;
  thumbnail?: string;
  resourceIds: string[];
  resourceCount: number;
  rules?: CollectionRule[];
  sharing: 'private' | 'shared' | 'public';
  statistics: CollectionStatistics;
  createdAt: Date;
  updatedAt: Date;
}

interface CollectionStatistics {
  totalResources: number;
  averageQuality: number;
  topClassifications: { name: string; count: number }[];
  recentActivity: Date;
}

// Annotation Model
interface Annotation {
  id: string;
  resourceId: string;
  userId: string;
  type: 'highlight' | 'note' | 'tag';
  text: string;
  note?: string;
  tags: string[];
  color: string;
  position: AnnotationPosition;
  createdAt: Date;
  updatedAt: Date;
}

interface AnnotationPosition {
  start: number;
  end: number;
  page?: number;
  rects?: DOMRect[];
}

// Search Models
interface SearchQuery {
  text: string;
  filters: SearchFilter[];
  weights: SearchWeights;
  method: 'fts5' | 'vector' | 'hybrid';
  booleanOperators?: BooleanExpression[];
}

interface SearchFilter {
  field: string;
  operator: string;
  value: any;
}

interface SearchWeights {
  keyword: number;
  semantic: number;
  sparse: number;
}

interface SearchResult {
  resource: Resource;
  score: number;
  explanation: RelevanceExplanation;
  highlights: Highlight[];
}

// Graph Models
interface GraphNode {
  id: string;
  label: string;
  type: 'resource' | 'concept' | 'author';
  cluster?: string;
  metadata: Record<string, any>;
  position?: { x: number; y: number };
}

interface GraphEdge {
  source: string;
  target: string;
  type: 'citation' | 'similarity' | 'co-authorship';
  weight: number;
}

// Recommendation Models
interface Recommendation {
  resource: Resource;
  score: number;
  category: 'fresh' | 'similar' | 'hidden';
  explanation: string;
}

interface UserPreferences {
  interests: string[];
  diversity: number;
  novelty: number;
  recency: number;
  domains: string[];
}

// Quality Models
interface QualityScore {
  overall: number;
  dimensions: QualityDimension[];
  timestamp: Date;
}

interface QualityDimension {
  name: string;
  score: number;
  maxScore: number;
  description: string;
}

// Taxonomy Models
interface TaxonomyNode {
  id: string;
  name: string;
  parentId?: string;
  children: TaxonomyNode[];
  resourceCount: number;
  depth: number;
}

interface ClassificationSuggestion {
  id: string;
  resourceId: string;
  category: string;
  confidence: number;
  reasoning: string[];
  status: 'pending' | 'accepted' | 'rejected';
}

// Monitoring Models
interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  components: ComponentHealth[];
  timestamp: Date;
}

interface ComponentHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  metrics: Record<string, number>;
}
```

### API Response Models

```typescript
// Paginated Response
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// API Error
interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// Upload Status
interface UploadStatus {
  id: string;
  status: 'pending' | 'processing' | 'complete' | 'error';
  progress: number;
  stage: string;
  error?: string;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### UI and Animation Properties

Property 1: View transition timing consistency
*For any* view transition (card/table toggle, theme switch), the transition duration should be 200ms or less
**Validates: Requirements 1.2, 1.4**

Property 2: Async operation notification
*For any* async operation (upload, search, save), when it completes, a toast notification should be displayed with appropriate messaging
**Validates: Requirements 1.5**

Property 3: Keyboard focus visibility
*For any* interactive element, when it receives keyboard focus, a visible focus indicator should be displayed
**Validates: Requirements 1.6**

Property 4: Motion preference respect
*For any* animation, when the user has prefers-reduced-motion set, the animation should be disabled or minimized
**Validates: Requirements 1.7**

### Upload and Ingestion Properties

Property 5: Multi-file queue creation
*For any* set of N files dropped on the upload zone, N upload queue items should be created with individual progress tracking
**Validates: Requirements 2.2**

Property 6: URL validation before ingestion
*For any* URL input, invalid URLs should be rejected before ingestion is initiated, and valid URLs should be accepted
**Validates: Requirements 2.3**

### Library and Filtering Properties

Property 7: Filter result count accuracy
*For any* filter applied, the displayed result count should match the actual number of resources matching that filter
**Validates: Requirements 3.2**

Property 8: Sort and filter transition smoothness
*For any* sort or filter operation, the result reordering should include smooth transition animations
**Validates: Requirements 7.6**

### Search Properties

Property 9: Search suggestion highlighting
*For any* search suggestion with matched text, the matching portions should be highlighted
**Validates: Requirements 5.5**

Property 10: Search history persistence
*For any* search query submitted, it should be stored in local search history and retrievable later
**Validates: Requirements 5.7**

Property 11: Result relevance tooltips
*For any* search result displayed, relevance explanation tooltips should be available
**Validates: Requirements 6.4**

Property 12: Saved search persistence
*For any* search configuration saved, it should be persisted and retrievable for future use
**Validates: Requirements 6.6**

Property 13: Keyword highlighting in results
*For any* matched keyword in search results, it should be highlighted with yellow background
**Validates: Requirements 7.2**

### Collection Properties

Property 14: Collection card hover effects
*For any* collection card, hovering over it should apply scale and shadow effects
**Validates: Requirements 8.3**

Property 15: Smart collection live counter
*For any* rule configuration change in a smart collection, the matched resource counter should update immediately
**Validates: Requirements 10.2**

Property 16: Rule validation error display
*For any* invalid rule in a smart collection, inline error messages should be displayed
**Validates: Requirements 10.3**

Property 17: Smart collection rule persistence
*For any* smart collection rule saved, it should be stored in collection metadata and retrievable
**Validates: Requirements 10.5**

### Performance Properties

Property 18: Route code splitting
*For any* major route in the application, it should be code-split and lazy-loaded
**Validates: Requirements 25.1**

Property 19: Bundle size optimization
*For any* production build, bundles should be optimized through tree shaking and lazy loading
**Validates: Requirements 25.3**

Property 20: Image lazy loading
*For any* image in the application, it should be lazy-loaded to improve initial page load
**Validates: Requirements 25.4**

Property 21: Virtual scrolling for large lists
*For any* list with more than 100 items, virtual scrolling should be implemented
**Validates: Requirements 25.5**

Property 22: First Contentful Paint performance
*For any* page load, First Contentful Paint should occur within 1.5 seconds
**Validates: Requirements 25.6**

Property 23: Time to Interactive performance
*For any* page load, Time to Interactive should occur within 3.5 seconds
**Validates: Requirements 25.7**

Property 24: Lighthouse score threshold
*For any* Lighthouse audit, the performance score should be above 90
**Validates: Requirements 25.8**

### Accessibility Properties

Property 25: ARIA label completeness
*For any* interactive element, it should have complete and appropriate ARIA labels
**Validates: Requirements 26.1**

Property 26: Keyboard navigation support
*For any* feature in the application, it should be fully accessible via keyboard navigation
**Validates: Requirements 26.2**

Property 27: Screen reader optimization
*For any* component, it should provide optimized announcements and descriptions for screen readers
**Validates: Requirements 26.3**

Property 28: Color contrast compliance
*For any* text element, it should meet WCAG AA color contrast standards
**Validates: Requirements 26.4**

Property 29: Error boundary coverage
*For any* component error, it should be caught by an error boundary and handled gracefully
**Validates: Requirements 26.6**

Property 30: Accessibility test compliance
*For any* page, it should pass axe-core accessibility tests with no violations
**Validates: Requirements 26.7**

Property 31: Focus indicator visibility
*For any* focusable element, when navigating with keyboard only, a visible focus indicator should be present
**Validates: Requirements 26.9**

## Error Handling

### Error Boundary Strategy

**Global Error Boundary**:
- Wraps the entire application
- Catches unhandled errors in any component
- Displays user-friendly error page with recovery options
- Logs errors to monitoring service

**Route-Level Error Boundaries**:
- Wrap each major route
- Allow other routes to continue functioning
- Display route-specific error messages
- Provide navigation to working routes

**Component-Level Error Boundaries**:
- Wrap critical components (graph visualization, PDF viewer)
- Allow page to remain functional
- Display component-specific error messages
- Provide retry functionality

### Error Types and Handling

**Network Errors**:
- Display toast notification with retry option
- Implement exponential backoff for retries
- Cache failed requests for offline recovery
- Show offline indicator when network is unavailable

**Validation Errors**:
- Display inline error messages near input fields
- Highlight invalid fields with red border
- Provide clear error messages explaining the issue
- Prevent form submission until errors are resolved

**API Errors**:
- Parse error responses from backend
- Display user-friendly error messages
- Log detailed error information for debugging
- Provide contextual actions (retry, contact support)

**State Errors**:
- Detect invalid state transitions
- Reset to last known good state
- Log state errors for debugging
- Notify user of state recovery

### Error Recovery Patterns

**Retry with Backoff**:
```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(baseDelay * Math.pow(2, i));
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Optimistic Updates with Rollback**:
```typescript
function useOptimisticUpdate<T>(
  mutationFn: (data: T) => Promise<T>,
  queryKey: string[]
) {
  const queryClient = useQueryClient();
  
  return useMutation(mutationFn, {
    onMutate: async (newData) => {
      await queryClient.cancelQueries(queryKey);
      const previousData = queryClient.getQueryData(queryKey);
      queryClient.setQueryData(queryKey, newData);
      return { previousData };
    },
    onError: (err, newData, context) => {
      queryClient.setQueryData(queryKey, context.previousData);
      showToast({ type: 'error', message: 'Update failed' });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(queryKey);
    },
  });
}
```


## Testing Strategy

### Dual Testing Approach

The application will use both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
**Property Tests**: Verify universal properties that should hold across all inputs

Together they provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness.

### Unit Testing

**Testing Framework**: Vitest
- Fast execution with native ESM support
- Compatible with Jest API
- Built-in code coverage

**Component Testing**: React Testing Library
- Test components from user perspective
- Avoid implementation details
- Focus on accessibility and user interactions

**Unit Test Coverage**:
- Component rendering and props
- User interactions (clicks, typing, navigation)
- Conditional rendering logic
- Error states and edge cases
- Integration between components
- API client functions
- Utility functions
- State management logic

**Example Unit Tests**:
```typescript
describe('ResourceCard', () => {
  it('displays resource information correctly', () => {
    const resource = createMockResource();
    render(<ResourceCard resource={resource} />);
    
    expect(screen.getByText(resource.title)).toBeInTheDocument();
    expect(screen.getByText(resource.authors[0])).toBeInTheDocument();
  });
  
  it('calls onClick when card is clicked', () => {
    const onClick = vi.fn();
    const resource = createMockResource();
    render(<ResourceCard resource={resource} onClick={onClick} />);
    
    fireEvent.click(screen.getByRole('article'));
    expect(onClick).toHaveBeenCalledWith(resource.id);
  });
  
  it('displays quality score badge', () => {
    const resource = createMockResource({ qualityScore: 85 });
    render(<ResourceCard resource={resource} />);
    
    expect(screen.getByText('85')).toBeInTheDocument();
  });
});
```

### Property-Based Testing

**Testing Framework**: fast-check
- Property-based testing library for JavaScript/TypeScript
- Generates random test cases
- Shrinks failing cases to minimal examples

**Property Test Configuration**:
- Minimum 100 iterations per property test
- Configurable seed for reproducibility
- Verbose mode for debugging failures

**Property Test Coverage**:
- Animation timing properties
- Accessibility properties
- Performance properties
- Data transformation properties
- State consistency properties

**Property Test Tagging**:
Each property-based test MUST be tagged with a comment explicitly referencing the correctness property in the design document using this format:
```typescript
/**
 * Feature: two-phase-frontend-roadmap, Property 1: View transition timing consistency
 */
```

**Example Property Tests**:
```typescript
import fc from 'fast-check';

/**
 * Feature: two-phase-frontend-roadmap, Property 1: View transition timing consistency
 */
describe('Property 1: View transition timing consistency', () => {
  it('all view transitions complete within 200ms', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('card', 'table', 'compact'),
        fc.constantFrom('card', 'table', 'compact'),
        async (fromView, toView) => {
          const startTime = performance.now();
          await transitionView(fromView, toView);
          const duration = performance.now() - startTime;
          
          expect(duration).toBeLessThanOrEqual(200);
        }
      ),
      { numRuns: 100 }
    );
  });
});

/**
 * Feature: two-phase-frontend-roadmap, Property 5: Multi-file queue creation
 */
describe('Property 5: Multi-file queue creation', () => {
  it('creates N queue items for N files', () => {
    fc.assert(
      fc.property(
        fc.array(fc.record({
          name: fc.string(),
          size: fc.nat(),
          type: fc.constantFrom('application/pdf', 'text/plain'),
        }), { minLength: 1, maxLength: 10 }),
        (files) => {
          const queue = createUploadQueue(files);
          expect(queue.length).toBe(files.length);
          
          queue.forEach((item, index) => {
            expect(item.filename).toBe(files[index].name);
            expect(item.progress).toBe(0);
          });
        }
      ),
      { numRuns: 100 }
    );
  });
});

/**
 * Feature: two-phase-frontend-roadmap, Property 6: URL validation before ingestion
 */
describe('Property 6: URL validation before ingestion', () => {
  it('rejects invalid URLs and accepts valid URLs', () => {
    fc.assert(
      fc.property(
        fc.webUrl(),
        (validUrl) => {
          expect(validateUrl(validUrl)).toBe(true);
        }
      ),
      { numRuns: 100 }
    );
    
    fc.assert(
      fc.property(
        fc.string().filter(s => !isValidUrl(s)),
        (invalidUrl) => {
          expect(validateUrl(invalidUrl)).toBe(false);
        }
      ),
      { numRuns: 100 }
    );
  });
});

/**
 * Feature: two-phase-frontend-roadmap, Property 28: Color contrast compliance
 */
describe('Property 28: Color contrast compliance', () => {
  it('all text meets WCAG AA contrast standards', () => {
    fc.assert(
      fc.property(
        fc.hexaString({ minLength: 6, maxLength: 6 }),
        fc.hexaString({ minLength: 6, maxLength: 6 }),
        (fgColor, bgColor) => {
          const contrast = calculateContrast(`#${fgColor}`, `#${bgColor}`);
          
          // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
          if (isLargeText) {
            expect(contrast).toBeGreaterThanOrEqual(3);
          } else {
            expect(contrast).toBeGreaterThanOrEqual(4.5);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### E2E Testing

**Testing Framework**: Playwright
- Cross-browser testing (Chromium, Firefox, WebKit)
- Reliable auto-waiting
- Network interception and mocking

**E2E Test Coverage**:
- Critical user journeys
- Multi-step workflows
- Cross-page interactions
- Authentication flows
- Error recovery scenarios

**Example E2E Tests**:
```typescript
test('user can upload and view a resource', async ({ page }) => {
  await page.goto('/library');
  
  // Upload file
  await page.click('[data-testid="upload-button"]');
  await page.setInputFiles('input[type="file"]', 'test.pdf');
  
  // Wait for upload to complete
  await page.waitForSelector('[data-testid="upload-success"]');
  
  // Verify resource appears in library
  await expect(page.locator('text=test.pdf')).toBeVisible();
  
  // Open resource detail
  await page.click('text=test.pdf');
  
  // Verify detail page loads
  await expect(page.locator('[data-testid="resource-detail"]')).toBeVisible();
});
```

### Accessibility Testing

**Automated Testing**: axe-core
- Run on every page and component
- Check for WCAG violations
- Integrate into CI/CD pipeline

**Manual Testing Checklist**:
- Screen reader navigation (NVDA, JAWS, VoiceOver)
- Keyboard-only navigation
- High contrast mode
- Zoom to 200%
- Color blindness simulation

### Performance Testing

**Metrics to Track**:
- First Contentful Paint (FCP)
- Time to Interactive (TTI)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- First Input Delay (FID)
- Bundle size
- Memory usage

**Performance Budgets**:
- FCP < 1.5s
- TTI < 3.5s
- LCP < 2.5s
- CLS < 0.1
- FID < 100ms
- Main bundle < 200KB (gzipped)
- Total bundle < 500KB (gzipped)

**Performance Testing Tools**:
- Lighthouse CI for automated audits
- WebPageTest for detailed analysis
- Chrome DevTools for profiling
- Bundle analyzer for size optimization

