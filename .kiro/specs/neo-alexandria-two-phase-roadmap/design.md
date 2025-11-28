# Design Document

## Overview

This design document outlines the architecture for implementing the Neo Alexandria frontend in two major phases over 25 weeks. The system builds on an existing minimal setup (dashboard, library panel, fuzzy search, light/dark mode) to create a comprehensive knowledge management platform for academic and research resources.

### Two-Phase Structure

**Phase 1: Core Platform (Weeks 1-13)**
- Foundation Enhancement (Week 1)
- Core Resource Management (Weeks 2-4)
- Search and Discovery (Weeks 5-7)
- Recommendations and Personalization (Weeks 8-9)
- Collections and Organization (Weeks 10-13)

**Phase 2: Advanced Features (Weeks 14-25)**
- Annotations and Active Reading (Weeks 14-16)
- Knowledge Graph and Discovery (Weeks 17-19)
- Quality and Curation (Weeks 20-21)
- Taxonomy and Classification (Weeks 22-23)
- System Monitoring and Administration (Week 24)
- Polish and Performance (Weeks 25)

Each phase maintains a production-ready, deployable state. Phase 1 delivers core functionality for resource management, search, and organization. Phase 2 adds advanced features for deep engagement, visualization, and system optimization.

### Design Principles

1. **Always Production Ready**: Each week ends with a deployable application
2. **UI Polish First**: Visual refinements integrated into feature development
3. **Progressive Enhancement**: Core functionality works without JavaScript where possible
4. **Performance Budget**: Every feature meets defined performance thresholds
5. **Accessibility Default**: WCAG compliance built in from the start
6. **Mobile Consideration**: Responsive design throughout

## Architecture

### Technology Stack

**Frontend Framework**: React 18+ with TypeScript
**State Management**: Zustand for global state, React Query for server state
**Routing**: React Router v6 with code splitting
**Styling**: CSS Modules with CSS Variables for theming
**Animation**: Framer Motion for complex animations, CSS transitions for simple ones
**Build Tool**: Vite for fast development and optimized production builds
**Testing**: Vitest for unit tests, React Testing Library for component tests
**Accessibility**: axe-core for automated testing

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pages   │  │Components│  │ Layouts  │  │  Hooks   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      State Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Zustand │  │React Query│ │  Context │  │  Local   │   │
│  │  Stores  │  │  Cache   │  │Providers │  │  State   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │  Toast   │  │Animation │  │  Focus   │   │
│  │  Client  │  │ Service  │  │ Service  │  │ Manager  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Resources │  │  Search  │  │  Graph   │  │  Quality │   │
│  │    API   │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── components/
│   ├── common/           # Reusable UI components
│   ├── layout/           # Layout components
│   ├── features/         # Feature-specific components
│   └── animations/       # Animation components
├── pages/                # Route pages
├── hooks/                # Custom React hooks
├── services/             # API and utility services
├── stores/               # Zustand stores
├── contexts/             # React contexts
├── types/                # TypeScript types
├── utils/                # Utility functions
├── styles/               # Global styles and themes
└── config/               # Configuration files
```

## Components and Interfaces

### Core UI Components

#### 1. Command Palette
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];
  onExecute: (command: Command) => void;
}

interface Command {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  category: string;
  action: () => void;
}
```

#### 2. Toast Notification System
```typescript
interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  action?: ToastAction;
}

interface ToastAction {
  label: string;
  onClick: () => void;
}

interface ToastService {
  show: (toast: Omit<ToastProps, 'id'>) => string;
  dismiss: (id: string) => void;
  dismissAll: () => void;
}
```

#### 3. Skeleton Loading Components
```typescript
interface SkeletonProps {
  variant: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

// Specialized skeletons
interface ResourceCardSkeletonProps {
  count: number;
  layout: 'grid' | 'list';
}
```

#### 4. Animation Utilities
```typescript
interface AnimationConfig {
  duration: number;
  easing: string;
  respectMotionPreference: boolean;
}

interface AnimationService {
  fade: (element: HTMLElement, config?: AnimationConfig) => Promise<void>;
  slide: (element: HTMLElement, direction: 'up' | 'down' | 'left' | 'right', config?: AnimationConfig) => Promise<void>;
  scale: (element: HTMLElement, config?: AnimationConfig) => Promise<void>;
  stagger: (elements: HTMLElement[], animation: Animation, delay: number) => Promise<void>;
}
```

### Feature Components

#### 5. Resource Library
```typescript
interface ResourceLibraryProps {
  viewMode: 'grid' | 'list';
  density: 'comfortable' | 'compact' | 'spacious';
  filters: ResourceFilters;
  onFilterChange: (filters: ResourceFilters) => void;
}

interface ResourceFilters {
  classification?: string[];
  quality?: { min: number; max: number };
  dateRange?: { start: Date; end: Date };
  tags?: string[];
}

interface ResourceCard {
  id: string;
  title: string;
  authors: string[];
  thumbnail?: string;
  quality: number;
  classification: string;
  dateAdded: Date;
}
```

#### 6. Upload Manager
```typescript
interface UploadManagerProps {
  onUploadComplete: (resources: Resource[]) => void;
  onUploadError: (error: UploadError) => void;
}

interface UploadTask {
  id: string;
  file: File | { url: string };
  status: 'pending' | 'downloading' | 'extracting' | 'analyzing' | 'complete' | 'error';
  progress: number;
  error?: string;
}

interface UploadQueue {
  tasks: UploadTask[];
  add: (file: File | string) => void;
  remove: (id: string) => void;
  retry: (id: string) => void;
  clear: () => void;
}
```

#### 7. Search Components
```typescript
interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  suggestions: SearchSuggestion[];
  history: SearchHistory[];
}

interface SearchStudioProps {
  query: SearchQuery;
  onQueryChange: (query: SearchQuery) => void;
  onSearch: () => void;
}

interface SearchQuery {
  text: string;
  operators: BooleanOperator[];
  weights: { keyword: number; semantic: number };
  method: 'fts5' | 'vector' | 'hybrid';
  filters: ResourceFilters;
}
```

#### 8. Collection Components
```typescript
interface CollectionGridProps {
  collections: Collection[];
  onSelect: (id: string) => void;
  onCreate: () => void;
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
  permissions: 'private' | 'shared' | 'public';
}

interface SmartCollectionBuilderProps {
  rules: CollectionRule[];
  onRulesChange: (rules: CollectionRule[]) => void;
  preview: Resource[];
}
```

#### 9. Annotation Components
```typescript
interface AnnotationToolbarProps {
  selection: TextSelection;
  onHighlight: (color: string) => void;
  onNote: () => void;
  onTag: (tags: string[]) => void;
}

interface Annotation {
  id: string;
  resourceId: string;
  type: 'highlight' | 'note';
  color?: string;
  text: string;
  note?: string;
  tags: string[];
  position: AnnotationPosition;
  createdAt: Date;
}

interface AnnotationNotebookProps {
  annotations: Annotation[];
  filters: AnnotationFilters;
  onFilterChange: (filters: AnnotationFilters) => void;
  onExport: (format: 'markdown' | 'json') => void;
}
```

#### 10. Graph Visualization
```typescript
interface GraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout: 'force' | 'hierarchical' | 'circular';
  onNodeClick: (node: GraphNode) => void;
  onNodeExpand: (nodeId: string) => void;
}

interface GraphNode {
  id: string;
  label: string;
  type: 'resource' | 'concept' | 'author';
  cluster?: string;
  metadata: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: 'citation' | 'similarity' | 'co-authorship';
  weight: number;
}
```

## Data Models

### Client-Side State Models

#### Resource State
```typescript
interface ResourceState {
  resources: Map<string, Resource>;
  filters: ResourceFilters;
  viewMode: 'grid' | 'list';
  density: 'comfortable' | 'compact' | 'spacious';
  selection: Set<string>;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    hasMore: boolean;
  };
}
```

#### Search State
```typescript
interface SearchState {
  query: SearchQuery;
  results: SearchResult[];
  history: SearchHistory[];
  savedSearches: SavedSearch[];
  isLoading: boolean;
  error?: string;
}
```

#### UI State
```typescript
interface UIState {
  theme: 'light' | 'dark';
  commandPaletteOpen: boolean;
  toasts: Toast[];
  focusTrap: FocusTrap | null;
  motionPreference: 'full' | 'reduced';
}
```

### API Response Models

#### Resource Response
```typescript
interface ResourceResponse {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  content: string;
  metadata: ResourceMetadata;
  quality: QualityScore;
  classification: string[];
  embeddings?: number[];
  createdAt: string;
  updatedAt: string;
}

interface QualityScore {
  overall: number;
  dimensions: {
    completeness: number;
    accuracy: number;
    relevance: number;
    freshness: number;
  };
}
```

#### Search Response
```typescript
interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  pageSize: number;
  facets: SearchFacets;
  timing: {
    total: number;
    keyword: number;
    semantic: number;
    fusion: number;
  };
}

interface SearchResult {
  resource: ResourceResponse;
  score: number;
  explanation: ScoreExplanation;
  highlights: TextHighlight[];
}
```

