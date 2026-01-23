# Design Document: Phase 2 - Living Code Editor

## Overview

Phase 2 implements an intelligent code viewing experience using Monaco Editor with semantic understanding, quality insights, and collaborative annotations. This transforms static code into a "living document" that reveals structure, quality, relationships, and insights through visual overlays and interactive features.

**Implementation Approach**: Hybrid Power (Option C)
- **magic-mcp** for generating Monaco wrapper and initial component structure
- **shadcn-ui** for reliable UI primitives (popovers, tooltips, badges, dialogs)
- **magic-ui** for strategic animations (hover effects, smooth transitions)
- **Monaco Editor** as the core code viewing engine

## Architecture

### Component Hierarchy

```
_auth.repositories.tsx (route)
└── RepositoryDetailView (new)
    └── CodeEditorView (new)
        ├── MonacoEditorWrapper (new)
        │   ├── Monaco Editor Instance
        │   ├── SemanticChunkOverlay (new)
        │   ├── QualityBadgeGutter (new)
        │   ├── AnnotationGutter (new)
        │   └── ReferenceGutter (new)
        ├── HoverCardProvider (new)
        │   └── HoverCard (shadcn-ui)
        ├── AnnotationPanel (new)
        │   ├── AnnotationList
        │   ├── AnnotationEditor
        │   └── AnnotationSearch
        └── ChunkMetadataPanel (new)
            ├── ChunkInfo
            └── ChunkNavigation
```

### State Management

**Zustand Stores**:

1. **editorStore** (new)
   ```typescript
   interface EditorState {
     activeFile: CodeFile | null;
     cursorPosition: { line: number; column: number };
     selection: { start: Position; end: Position } | null;
     scrollPosition: number;
     fontSize: number;
     showLineNumbers: boolean;
     showMinimap: boolean;
     setActiveFile: (file: CodeFile) => void;
     updateCursorPosition: (position: Position) => void;
     updateSelection: (selection: Selection | null) => void;
   }
   ```

2. **annotationStore** (new)
   ```typescript
   interface AnnotationState {
     annotations: Annotation[];
     selectedAnnotation: Annotation | null;
     isCreating: boolean;
     fetchAnnotations: (resourceId: string) => Promise<void>;
     createAnnotation: (data: AnnotationCreate) => Promise<void>;
     updateAnnotation: (id: string, data: AnnotationUpdate) => Promise<void>;
     deleteAnnotation: (id: string) => Promise<void>;
     selectAnnotation: (id: string) => void;
   }
   ```

3. **chunkStore** (new)
   ```typescript
   interface ChunkState {
     chunks: SemanticChunk[];
     selectedChunk: SemanticChunk | null;
     chunkVisibility: boolean;
     fetchChunks: (resourceId: string) => Promise<void>;
     selectChunk: (id: string) => void;
     toggleChunkVisibility: () => void;
   }
   ```

4. **qualityStore** (new)
   ```typescript
   interface QualityState {
     qualityData: QualityDetails | null;
     badgeVisibility: boolean;
     fetchQualityData: (resourceId: string) => Promise<void>;
     toggleBadgeVisibility: () => void;
   }
   ```

5. **editorPreferencesStore** (new)
   ```typescript
   interface EditorPreferencesState {
     theme: 'vs-light' | 'vs-dark';
     fontSize: number;
     lineNumbers: boolean;
     minimap: boolean;
     wordWrap: boolean;
     chunkBoundaries: boolean;
     qualityBadges: boolean;
     annotations: boolean;
     references: boolean;
     updatePreference: (key: string, value: any) => void;
   }
   ```

## Components and Interfaces

### 1. MonacoEditorWrapper

**Purpose**: Core Monaco Editor integration with custom overlays

**Props**:
```typescript
interface MonacoEditorWrapperProps {
  file: CodeFile;
  language: string;
  theme: 'vs-light' | 'vs-dark';
  readOnly: boolean;
  onCursorChange?: (position: Position) => void;
  onSelectionChange?: (selection: Selection) => void;
}
```

**Implementation Strategy**:
- Use **@monaco-editor/react** for React integration
- Use **magic-mcp** to generate initial wrapper component
- Configure Monaco with custom decorations API for overlays
- Use **shadcn-ui** Popover for hover cards
- Use **magic-ui** smooth transitions for overlay animations

**Key Features**:
- Read-only mode (no editing)
- Tree-sitter semantic highlighting via Monaco themes
- Custom gutter decorations for annotations, quality, references
- Virtualized rendering for large files (>5000 lines)
- Debounced hover events (300ms)

**Monaco Configuration**:
```typescript
const monacoOptions = {
  readOnly: true,
  minimap: { enabled: preferences.minimap },
  lineNumbers: preferences.lineNumbers ? 'on' : 'off',
  fontSize: preferences.fontSize,
  wordWrap: preferences.wordWrap ? 'on' : 'off',
  scrollBeyondLastLine: false,
  renderLineHighlight: 'line',
  glyphMargin: true, // Enable gutter for decorations
  folding: true,
  automaticLayout: true,
};
```

---

### 2. SemanticChunkOverlay

**Purpose**: Visual boundaries around AST-based code chunks

**Props**:
```typescript
interface SemanticChunkOverlayProps {
  chunks: SemanticChunk[];
  visible: boolean;
  selectedChunk: SemanticChunk | null;
  onChunkClick: (chunk: SemanticChunk) => void;
  onChunkHover: (chunk: SemanticChunk | null) => void;
}
```

**Implementation Strategy**:
- Use Monaco's `deltaDecorations` API for chunk boundaries
- Use **magic-ui** subtle border animations on hover
- Use **shadcn-ui** Tooltip for chunk metadata preview

**Chunk Visualization**:
```typescript
const chunkDecoration = {
  range: new monaco.Range(
    chunk.start_line,
    1,
    chunk.end_line,
    Number.MAX_VALUE
  ),
  options: {
    isWholeLine: false,
    className: 'semantic-chunk-boundary',
    glyphMarginClassName: 'chunk-glyph',
    hoverMessage: { value: `Chunk: ${chunk.metadata.function_name}` },
  },
};
```

**Chunk Metadata**:
```typescript
interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: {
    function_name?: string;
    class_name?: string;
    start_line: number;
    end_line: number;
    language: string;
  };
  created_at: string;
}
```

---

### 3. QualityBadgeGutter

**Purpose**: Display quality scores in the editor gutter

**Props**:
```typescript
interface QualityBadgeGutterProps {
  qualityData: QualityDetails;
  visible: boolean;
  onBadgeClick: (line: number) => void;
}
```

**Implementation Strategy**:
- Use Monaco's glyph margin for badge placement
- Use **shadcn-ui** Badge component for styling
- Use **magic-ui** subtle glow effect for low-quality indicators
- Use **shadcn-ui** Tooltip for detailed quality metrics

**Quality Badge Rendering**:
```typescript
const qualityDecoration = {
  range: new monaco.Range(line, 1, line, 1),
  options: {
    glyphMarginClassName: `quality-badge quality-${getQualityLevel(score)}`,
    glyphMarginHoverMessage: {
      value: `Quality: ${(score * 100).toFixed(0)}%\n` +
             `Accuracy: ${dimensions.accuracy}\n` +
             `Completeness: ${dimensions.completeness}`,
    },
  },
};
```

**Quality Levels**:
- `quality-high`: score >= 0.8 (green)
- `quality-medium`: 0.6 <= score < 0.8 (yellow)
- `quality-low`: score < 0.6 (red)

---

### 4. AnnotationGutter

**Purpose**: Display annotation chips in the editor gutter

**Props**:
```typescript
interface AnnotationGutterProps {
  annotations: Annotation[];
  visible: boolean;
  onAnnotationClick: (annotation: Annotation) => void;
  onAnnotationHover: (annotation: Annotation | null) => void;
}
```

**Implementation Strategy**:
- Use Monaco's glyph margin for chip placement
- Use **shadcn-ui** Popover for annotation details
- Use **magic-ui** smooth slide-in animation for popover
- Stack multiple annotations vertically if on same line

**Annotation Chip Rendering**:
```typescript
const annotationDecoration = {
  range: new monaco.Range(
    annotation.start_offset_line,
    1,
    annotation.start_offset_line,
    1
  ),
  options: {
    glyphMarginClassName: 'annotation-chip',
    glyphMarginHoverMessage: {
      value: annotation.note || annotation.highlighted_text,
    },
    inlineClassName: 'annotation-highlight',
    inlineClassNameAffectsLetterSpacing: false,
  },
};
```

**Annotation Model**:
```typescript
interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  created_at: string;
  updated_at: string;
}
```

---

### 5. ReferenceGutter

**Purpose**: Display reference icons linking to papers/documentation

**Props**:
```typescript
interface ReferenceGutterProps {
  references: Reference[];
  visible: boolean;
  onReferenceClick: (reference: Reference) => void;
}
```

**Implementation Strategy**:
- Use Monaco's glyph margin for book icons
- Use **shadcn-ui** Dialog for reference details panel
- Use **magic-ui** smooth modal entrance animation

**Reference Model**:
```typescript
interface Reference {
  id: string;
  resource_id: string;
  line_number: number;
  reference_type: 'paper' | 'documentation' | 'external';
  title: string;
  authors?: string[];
  url?: string;
  pdf_id?: string; // Link to library PDF
  citation?: string;
}
```

---

### 6. HoverCardProvider

**Purpose**: Contextual hover cards with Node2Vec summaries and graph connections

**Props**:
```typescript
interface HoverCardProviderProps {
  editor: monaco.editor.IStandaloneCodeEditor;
  onSymbolHover: (symbol: string, position: Position) => void;
}
```

**Implementation Strategy**:
- Use Monaco's `onMouseMove` event with debouncing (300ms)
- Use **shadcn-ui** HoverCard component
- Use **magic-ui** fade-in animation
- Fetch Node2Vec data from backend on hover

**Hover Card Content**:
```typescript
interface HoverCardData {
  symbol: string;
  summary: string; // Node2Vec summary
  connections: {
    name: string;
    type: 'function' | 'class' | 'variable';
    relationship: 'calls' | 'imports' | 'defines';
    file: string;
  }[];
  loading: boolean;
  error?: string;
}
```

---

### 7. AnnotationPanel

**Purpose**: Sidebar panel for managing annotations

**Props**:
```typescript
interface AnnotationPanelProps {
  annotations: Annotation[];
  selectedAnnotation: Annotation | null;
  onAnnotationSelect: (id: string) => void;
  onAnnotationCreate: (data: AnnotationCreate) => void;
  onAnnotationUpdate: (id: string, data: AnnotationUpdate) => void;
  onAnnotationDelete: (id: string) => void;
}
```

**Implementation Strategy**:
- Use **shadcn-ui** Sheet component for slide-out panel
- Use **shadcn-ui** Input, Textarea, Badge for annotation editor
- Use **magic-ui** smooth slide animation
- Use **shadcn-ui** Command for annotation search

**Panel Sections**:
1. **Annotation List**: Scrollable list of all annotations
2. **Annotation Editor**: Form for creating/editing annotations
3. **Annotation Search**: Full-text and semantic search

---

### 8. ChunkMetadataPanel

**Purpose**: Display metadata for selected semantic chunk

**Props**:
```typescript
interface ChunkMetadataPanelProps {
  chunk: SemanticChunk | null;
  onNavigateToChunk: (chunkId: string) => void;
}
```

**Implementation Strategy**:
- Use **shadcn-ui** Card component for metadata display
- Use **shadcn-ui** Button for navigation
- Use **magic-ui** smooth expand/collapse animation

**Metadata Display**:
- Function/class name
- Start/end line numbers
- Language
- Chunk size (tokens)
- Related chunks (via graph)

---

## Data Models

### CodeFile

```typescript
interface CodeFile {
  id: string;
  resource_id: string;
  path: string;
  name: string;
  language: string;
  content: string;
  size: number;
  lines: number;
  created_at: string;
  updated_at: string;
}
```

### SemanticChunk

```typescript
interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: {
    function_name?: string;
    class_name?: string;
    start_line: number;
    end_line: number;
    language: string;
  };
  embedding_id?: string;
  created_at: string;
}
```

### QualityDetails

```typescript
interface QualityDetails {
  resource_id: string;
  quality_dimensions: {
    accuracy: number;
    completeness: number;
    consistency: number;
    timeliness: number;
    relevance: number;
  };
  quality_overall: number;
  quality_weights: {
    accuracy: number;
    completeness: number;
    consistency: number;
    timeliness: number;
    relevance: number;
  };
  quality_last_computed: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
}
```

### Annotation

```typescript
interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];
  created_at: string;
  updated_at: string;
}

interface AnnotationCreate {
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color?: string;
  collection_ids?: string[];
}

interface AnnotationUpdate {
  note?: string;
  tags?: string[];
  color?: string;
  is_shared?: boolean;
}
```

### Reference

```typescript
interface Reference {
  id: string;
  resource_id: string;
  line_number: number;
  reference_type: 'paper' | 'documentation' | 'external';
  title: string;
  authors?: string[];
  url?: string;
  pdf_id?: string;
  citation?: string;
  created_at: string;
}
```

---

## API Integration

### Backend Endpoints

**Annotations API** (`/annotations`):
- `POST /resources/{resource_id}/annotations` - Create annotation
- `GET /resources/{resource_id}/annotations` - List annotations
- `GET /annotations/{annotation_id}` - Get annotation
- `PUT /annotations/{annotation_id}` - Update annotation
- `DELETE /annotations/{annotation_id}` - Delete annotation
- `GET /annotations/search/fulltext` - Full-text search
- `GET /annotations/search/semantic` - Semantic search

**Resources API** (`/resources`):
- `GET /resources/{resource_id}/chunks` - List semantic chunks
- `GET /chunks/{chunk_id}` - Get chunk details
- `POST /resources/{resource_id}/chunks` - Trigger chunking

**Quality API** (`/quality`):
- `GET /resources/{resource_id}/quality-details` - Get quality data
- `POST /quality/recalculate` - Recalculate quality

**Graph API** (planned):
- `GET /graph/node2vec/{symbol}` - Get Node2Vec summary
- `GET /graph/connections/{symbol}` - Get 1-hop connections

### API Client Structure

```typescript
// src/lib/api/editor.ts
export const editorApi = {
  // Annotations
  createAnnotation: (resourceId: string, data: AnnotationCreate) => 
    api.post(`/resources/${resourceId}/annotations`, data),
  
  getAnnotations: (resourceId: string) => 
    api.get(`/resources/${resourceId}/annotations`),
  
  updateAnnotation: (id: string, data: AnnotationUpdate) => 
    api.put(`/annotations/${id}`, data),
  
  deleteAnnotation: (id: string) => 
    api.delete(`/annotations/${id}`),
  
  searchAnnotations: (query: string, type: 'fulltext' | 'semantic') => 
    api.get(`/annotations/search/${type}`, { params: { query } }),
  
  // Chunks
  getChunks: (resourceId: string) => 
    api.get(`/resources/${resourceId}/chunks`),
  
  getChunk: (chunkId: string) => 
    api.get(`/chunks/${chunkId}`),
  
  // Quality
  getQualityDetails: (resourceId: string) => 
    api.get(`/resources/${resourceId}/quality-details`),
  
  // Graph (planned)
  getNode2VecSummary: (symbol: string) => 
    api.get(`/graph/node2vec/${symbol}`),
  
  getConnections: (symbol: string) => 
    api.get(`/graph/connections/${symbol}`),
};
```

---

## Performance Considerations

### Monaco Editor Optimization

**Large File Handling**:
- Use virtualized rendering for files >5000 lines
- Lazy-load decorations as user scrolls
- Debounce decoration updates (100ms)
- Limit concurrent decoration operations

**Memory Management**:
- Dispose Monaco instances on unmount
- Clear decorations when switching files
- Use WeakMap for decoration caching
- Limit hover card data retention

### API Optimization

**Caching Strategy**:
- Cache annotations per resource (5 minutes)
- Cache chunks per resource (10 minutes)
- Cache quality data per resource (15 minutes)
- Use TanStack Query for automatic caching

**Request Batching**:
- Batch annotation fetches on file open
- Debounce hover card requests (300ms)
- Prefetch chunks for active file
- Lazy-load quality data on demand

### Rendering Optimization

**React Optimization**:
- Memoize expensive components (Monaco wrapper, overlays)
- Use React.memo for annotation chips
- Virtualize annotation list (react-window)
- Debounce scroll events (100ms)

**CSS Optimization**:
- Use CSS transforms for animations (not width/height)
- Use `will-change` for animated elements
- Minimize repaints with `contain: layout`
- Use GPU acceleration for overlays

---

## Keyboard Navigation

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd+/ | Toggle annotation mode |
| Cmd+Shift+A | Show all annotations |
| Cmd+Shift+Q | Toggle quality badges |
| Cmd+Shift+C | Toggle chunk boundaries |
| Cmd+Shift+R | Toggle references |
| Cmd+F | Find in file (Monaco native) |
| Cmd+G | Go to line (Monaco native) |
| Escape | Close active panel/popover |

### Annotation Mode Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Create annotation from selection |
| Cmd+S | Save annotation |
| Cmd+Backspace | Delete annotation |
| Tab | Next annotation |
| Shift+Tab | Previous annotation |

---

## Accessibility

### WCAG 2.1 AA Compliance

**Keyboard Navigation**:
- All features accessible via keyboard
- Focus indicators visible (2px outline)
- Tab order logical and predictable
- Escape key closes modals/popovers

**Screen Reader Support**:
- ARIA labels on all icon-only buttons
- ARIA live regions for status updates
- ARIA descriptions for complex interactions
- Semantic HTML structure

**Color Contrast**:
- All text meets 4.5:1 contrast ratio
- Quality badges use patterns + color
- Annotation highlights use borders + color
- High contrast mode support

**Focus Management**:
- Focus trapped in modals
- Focus restored on modal close
- Skip links for long content
- Focus visible on all interactive elements

---

## Error Handling

### Monaco Editor Errors

**Scenario**: Monaco fails to load
**Handling**:
- Show fallback text viewer (read-only textarea)
- Display error message with retry button
- Log error to console
- Preserve file content

### API Errors

**Scenario**: Annotation API fails
**Handling**:
- Show cached annotations with warning banner
- Disable annotation creation
- Provide retry button
- Log error details

**Scenario**: Chunk API fails
**Handling**:
- Hide chunk boundaries
- Show error toast
- Fall back to line-based display
- Allow manual retry

**Scenario**: Quality API fails
**Handling**:
- Hide quality badges
- Show warning icon in header
- Provide manual refresh button
- Don't block other features

### Hover Card Errors

**Scenario**: Node2Vec data fails to load
**Handling**:
- Show basic symbol information from Monaco
- Display "Unable to load summary" message
- Provide retry button
- Don't block hover card display

---

## Testing Strategy

### Unit Tests

**Components to Test**:
- MonacoEditorWrapper: Initialization, decorations, events
- SemanticChunkOverlay: Chunk rendering, selection, hover
- QualityBadgeGutter: Badge placement, color coding, tooltips
- AnnotationGutter: Chip rendering, stacking, click handling
- HoverCardProvider: Debouncing, data fetching, display
- AnnotationPanel: CRUD operations, search, filtering

**Test Approach**:
- React Testing Library for component tests
- Mock Monaco Editor API
- Mock Zustand stores
- Test keyboard events
- Test API integration with MSW

### Integration Tests

**Workflows to Test**:
1. User opens file → Monaco loads → Chunks display
2. User selects text → Creates annotation → Chip appears
3. User hovers over function → Hover card shows → Displays summary
4. User clicks quality badge → Tooltip shows → Displays metrics
5. User toggles chunk visibility → Boundaries hide/show
6. User searches annotations → Results filter → Navigates to annotation

### Property-Based Tests

Property tests will be defined after prework analysis.

### Visual Regression Tests

**Scenarios**:
- Monaco editor with all overlays enabled
- Annotation chips stacked on same line
- Quality badges at different levels
- Hover card with graph connections
- Chunk boundaries highlighted
- Light vs dark theme

---

## Implementation Notes

### MCP Server Usage

**magic-mcp** (`@21st-dev/magic-mcp`):
- Generate MonacoEditorWrapper component structure
- Generate AnnotationPanel component shell
- Generate API client boilerplate

**shadcn-ui** (`@jpisnice/shadcn-ui-mcp-server`):
- HoverCard component for hover cards
- Popover component for annotation details
- Dialog component for reference panel
- Badge component for quality indicators
- Tooltip component for gutter tooltips
- Sheet component for annotation panel
- Input, Textarea for annotation editor
- Command component for annotation search

**magic-ui** (`@magicuidesign/mcp`):
- Smooth fade-in for hover cards
- Slide animation for annotation panel
- Glow effect for low-quality badges
- Subtle border animation for chunk hover

### Technology Stack

**Core**:
- React 18
- TypeScript 5
- Vite 5
- TanStack Router
- TanStack Query (for API caching)

**Editor**:
- Monaco Editor (@monaco-editor/react)
- Tree-sitter (via backend)

**State Management**:
- Zustand (editor, annotation, chunk, quality stores)

**UI Components**:
- shadcn/ui (via MCP)
- magic-ui (via MCP)
- lucide-react (icons)

**Styling**:
- Tailwind CSS
- CSS Modules (for Monaco customization)

**Testing**:
- Vitest
- React Testing Library
- MSW (API mocking)
- fast-check (property-based testing)

---

## Migration from Phase 1

### Preserve

- All Phase 1 components (WorkbenchLayout, Sidebar, Header, etc.)
- All Phase 1 stores (workbench, theme, repository, command)
- All Phase 1 routes

### Create New

- `src/features/editor/` - Editor feature directory
  - `MonacoEditorWrapper.tsx`
  - `SemanticChunkOverlay.tsx`
  - `QualityBadgeGutter.tsx`
  - `AnnotationGutter.tsx`
  - `ReferenceGutter.tsx`
  - `HoverCardProvider.tsx`
  - `AnnotationPanel.tsx`
  - `ChunkMetadataPanel.tsx`
- `src/stores/editor.ts`
- `src/stores/annotation.ts`
- `src/stores/chunk.ts`
- `src/stores/quality.ts`
- `src/stores/editorPreferences.ts`
- `src/lib/api/editor.ts`
- `src/lib/monaco/` - Monaco utilities
  - `decorations.ts`
  - `themes.ts`
  - `languages.ts`

### Update

- `src/routes/_auth.repositories.tsx` - Add code editor view
- `src/lib/api/index.ts` - Export editor API
- `package.json` - Add Monaco dependencies

---

## Future Enhancements

**Phase 3+ Integration Points**:
- Reference overlay will link to Library PDFs
- Hover cards will show paper citations
- Annotations will sync with Library highlights
- Quality badges will integrate with Curation workflow

**Potential Improvements**:
- Collaborative annotations (real-time)
- Annotation threads (replies)
- Code diff view (compare versions)
- Split editor (side-by-side)
- Custom Monaco themes
- Annotation export to Notion/Obsidian
- Voice annotations (audio notes)
- AI-powered annotation suggestions

---
