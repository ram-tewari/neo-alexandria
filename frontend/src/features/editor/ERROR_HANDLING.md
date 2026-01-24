# Editor Error Handling Documentation

## Overview

The Living Code Editor implements comprehensive error handling with graceful fallbacks for all API operations. This ensures users can continue working even when backend services are unavailable or fail.

## Error Handling Strategy

### 1. Annotation Store Error Handling

**Requirement**: 10.4 - When annotation API fails, show cached annotations with a warning banner

#### Implementation

- **Cached Data Fallback**: When `fetchAnnotations()` fails, the store automatically falls back to cached annotations if available
- **Warning Banner**: Sets `usingCachedData: true` to trigger warning UI
- **Optimistic Updates**: All CRUD operations use optimistic updates with automatic rollback on failure
- **Retry Support**: `retryLastOperation()` allows users to retry failed operations

#### Error States

```typescript
interface AnnotationState {
  error: string | null;           // Error message
  usingCachedData: boolean;       // True when showing cached data
  annotationCache: Record<...>;   // Persistent cache
}
```

#### Usage Example

```typescript
// Fetch annotations with automatic fallback
await annotationStore.fetchAnnotations(resourceId);

if (annotationStore.usingCachedData) {
  // Show warning banner: "Using cached annotations"
}

// Retry failed operation
await annotationStore.retryLastOperation();
```

---

### 2. Chunk Store Error Handling

**Requirement**: 10.2 - When AST chunking fails, fall back to line-based display

#### Implementation

- **Line-Based Fallback**: When `fetchChunks()` fails and file content is available, generates line-based chunks (50 lines per chunk)
- **Fallback Indicator**: Sets `usingFallback: true` to show warning
- **Cache Support**: Caches both AST chunks and fallback chunks
- **Graceful Degradation**: If no file content available, shows error without breaking UI

#### Fallback Chunk Generation

```typescript
function generateLineBasedChunks(
  resourceId: string,
  fileContent: string,
  language: string
): SemanticChunk[]
```

- Splits file into 50-line chunks
- Preserves line number metadata
- Maintains chunk interface compatibility

#### Error States

```typescript
interface ChunkState {
  error: string | null;      // Error message
  usingFallback: boolean;    // True when using line-based chunks
  chunkCache: Record<...>;   // Persistent cache
}
```

#### Usage Example

```typescript
// Fetch chunks with line-based fallback
await chunkStore.fetchChunks(resourceId, fileContent, language);

if (chunkStore.usingFallback) {
  // Show warning: "AST chunking unavailable. Using line-based display."
}

// Retry to get AST chunks
await chunkStore.retryLastOperation();
```

---

### 3. Quality Store Error Handling

**Requirement**: 10.3 - When quality scores fail to load, hide quality badges without breaking UI

#### Implementation

- **Auto-Hide Badges**: When `fetchQualityData()` fails, sets `hideBadgesDueToError: true`
- **Silent Failure**: Quality failures don't block other editor features
- **Cache Support**: Uses cached quality data when available
- **Manual Override**: Users can manually toggle badges even after error

#### Error States

```typescript
interface QualityState {
  error: string | null;           // Error message
  hideBadgesDueToError: boolean;  // Auto-hide flag
  qualityCache: Record<...>;      // Persistent cache
}
```

#### Usage Example

```typescript
// Fetch quality data with auto-hide on failure
await qualityStore.fetchQualityData(resourceId);

if (qualityStore.hideBadgesDueToError) {
  // Badges automatically hidden
  // Show warning: "Quality data unavailable. Badges are hidden."
}

// Retry to fetch quality data
await qualityStore.retryLastOperation();

// Manual override
qualityStore.setBadgeVisibility(true); // Clears error flag
```

---

## Error Banner Components

### ErrorBanner (Generic)

Base component for displaying errors with retry options.

```typescript
<ErrorBanner
  title="Error Title"
  message="Error description"
  variant="error" | "warning" | "info"
  showRetry={true}
  onRetry={() => store.retryLastOperation()}
  showDismiss={true}
  onDismiss={() => store.clearError()}
  isRetrying={isLoading}
/>
```

### AnnotationErrorBanner

Specialized banner for annotation errors.

```typescript
<AnnotationErrorBanner
  error={annotationStore.error}
  usingCachedData={annotationStore.usingCachedData}
  onRetry={() => annotationStore.retryLastOperation()}
  onDismiss={() => annotationStore.clearError()}
  isRetrying={annotationStore.isLoading}
/>
```

### ChunkErrorBanner

Specialized banner for chunk errors.

```typescript
<ChunkErrorBanner
  error={chunkStore.error}
  usingFallback={chunkStore.usingFallback}
  onRetry={() => chunkStore.retryLastOperation()}
  onDismiss={() => chunkStore.clearError()}
  isRetrying={chunkStore.isLoading}
/>
```

### QualityErrorBanner

Specialized banner for quality errors.

```typescript
<QualityErrorBanner
  error={qualityStore.error}
  onRetry={() => qualityStore.retryLastOperation()}
  onDismiss={() => qualityStore.clearError()}
  isRetrying={qualityStore.isLoading}
/>
```

---

## UI Integration

### CodeEditorView Component

The `CodeEditorView` component integrates all error banners and provides a complete error handling experience:

```typescript
import { CodeEditorView } from '@/features/editor/CodeEditorView';

// Usage
<CodeEditorView file={codeFile} />
```

**Features**:
- Automatically displays error banners when API failures occur
- Handles retry functionality for all error types
- Supports error dismissal
- Shows multiple error banners simultaneously when needed
- Clears errors when file changes

**Error Banner Placement**:
Error banners are displayed at the top of the editor view, above the Monaco editor instance. This ensures they are immediately visible to users without blocking the code view.

**Example Integration**:

```typescript
export function CodeEditorView({ file }: CodeEditorViewProps) {
  const {
    error: annotationError,
    usingCachedData,
    retryLastOperation: retryAnnotations,
    clearError: clearAnnotationError,
    isLoading: annotationsLoading,
  } = useAnnotationStore();

  const {
    error: chunkError,
    usingFallback,
    retryLastOperation: retryChunks,
    clearError: clearChunkError,
    isLoading: chunksLoading,
  } = useChunkStore();

  const {
    error: qualityError,
    hideBadgesDueToError,
    retryLastOperation: retryQuality,
    clearError: clearQualityError,
    isLoading: qualityLoading,
  } = useQualityStore();

  return (
    <div className="code-editor-view">
      {/* Error Banners */}
      <div className="error-banners-container">
        {annotationError && (
          <AnnotationErrorBanner
            error={annotationError}
            usingCachedData={usingCachedData}
            onRetry={retryAnnotations}
            onDismiss={clearAnnotationError}
            isRetrying={annotationsLoading}
          />
        )}

        {chunkError && (
          <ChunkErrorBanner
            error={chunkError}
            usingFallback={usingFallback}
            onRetry={retryChunks}
            onDismiss={clearChunkError}
            isRetrying={chunksLoading}
          />
        )}

        {qualityError && hideBadgesDueToError && (
          <QualityErrorBanner
            error={qualityError}
            onRetry={retryQuality}
            onDismiss={clearQualityError}
            isRetrying={qualityLoading}
          />
        )}
      </div>

      {/* Monaco Editor and Overlays */}
      <MonacoEditorWrapper file={file} />
    </div>
  );
}
```

---

## Optimistic Updates

All annotation CRUD operations use optimistic updates for better UX:

### Create Annotation

1. Generate temporary annotation with `temp-${timestamp}` ID
2. Add to store immediately (optimistic)
3. Call API
4. On success: Replace temp annotation with real one
5. On failure: Remove temp annotation and show error

### Update Annotation

1. Store original annotation
2. Apply update immediately (optimistic)
3. Call API
4. On success: Keep updated annotation
5. On failure: Rollback to original and show error

### Delete Annotation

1. Store original annotation
2. Remove from store immediately (optimistic)
3. Call API
4. On success: Keep removed
5. On failure: Restore annotation and show error

---

## Retry Functionality

All stores support retry via `retryLastOperation()`:

```typescript
// Stores last operation internally
let lastOperation: (() => Promise<void>) | null = null;

// Retry mechanism
retryLastOperation: async () => {
  if (lastOperation) {
    await lastOperation();
  }
}
```

**Usage**:
- User clicks "Retry" button in error banner
- Store re-executes last failed operation
- Loading state shown during retry
- Success clears error, failure shows updated error

---

## Cache Persistence

All stores use Zustand persist middleware for offline support:

### Annotation Cache

```typescript
persist(
  (set, get) => ({ /* store */ }),
  {
    name: 'annotation-storage',
    partialize: (state) => ({
      annotationCache: state.annotationCache,
    }),
  }
)
```

### Chunk Cache

```typescript
persist(
  (set, get) => ({ /* store */ }),
  {
    name: 'chunk-storage',
    partialize: (state) => ({
      chunkVisibility: state.chunkVisibility,
      chunkCache: state.chunkCache,
    }),
  }
)
```

### Quality Cache

```typescript
persist(
  (set, get) => ({ /* store */ }),
  {
    name: 'quality-storage',
    partialize: (state) => ({
      badgeVisibility: state.badgeVisibility,
      qualityCache: state.qualityCache,
    }),
  }
)
```

---

## Testing

Comprehensive test suite in `src/stores/__tests__/error-handling.test.ts`:

### Annotation Tests
- ✅ Use cached data when API fails
- ✅ Show error when no cache available
- ✅ Rollback optimistic create on failure
- ✅ Rollback optimistic update on failure
- ✅ Rollback optimistic delete on failure
- ✅ Support retry functionality

### Chunk Tests
- ✅ Use line-based fallback when API fails
- ✅ Show error when no fallback available
- ✅ Generate correct line-based chunks
- ✅ Support retry functionality

### Quality Tests
- ✅ Hide badges when API fails
- ✅ Clear error flag on manual toggle
- ✅ Clear error flag on manual set
- ✅ Support retry functionality
- ✅ Use cached data when available

---

## Error Messages

### Annotation Errors

- **Cached Data**: "Unable to fetch latest annotations. Showing cached data."
- **No Cache**: Original error message from API
- **Create Failed**: Original error message from API
- **Update Failed**: Original error message from API
- **Delete Failed**: Original error message from API

### Chunk Errors

- **Fallback Used**: "AST chunking unavailable. Using line-based display."
- **No Fallback**: Original error message from API

### Quality Errors

- **Fetch Failed**: Original error message from API
- **Banner Message**: "{error} Quality badges are hidden."

---

## Accessibility

All error banners follow WCAG 2.1 AA guidelines:

- **ARIA Live Regions**: `role="alert"` and `aria-live="polite"`
- **ARIA Labels**: All buttons have descriptive labels
- **Keyboard Support**: All actions accessible via keyboard
- **Focus Management**: Focus preserved on retry/dismiss
- **Color Contrast**: Error colors meet 4.5:1 ratio

---

## Best Practices

### For Component Developers

1. **Always check error state** before rendering features
2. **Show error banners** prominently but non-blocking
3. **Provide retry options** for all failed operations
4. **Clear errors** when user takes action
5. **Test error scenarios** with MSW mocks

### For Store Developers

1. **Implement caching** for all data fetching
2. **Use optimistic updates** for better UX
3. **Provide fallbacks** when possible
4. **Store last operation** for retry support
5. **Clear errors** on successful operations

### For Users

1. **Check warning banners** for data freshness
2. **Use retry button** when network recovers
3. **Dismiss errors** that are no longer relevant
4. **Manual toggles** override error states
5. **Cached data** is safe to use offline

---

## Future Enhancements

- [ ] Exponential backoff for retries
- [ ] Network status detection
- [ ] Offline mode indicator
- [ ] Batch retry for multiple failures
- [ ] Error analytics/logging
- [ ] User-configurable retry behavior
- [ ] Cache expiration policies
- [ ] Conflict resolution for cached data

---

## Related Files

- `src/stores/annotation.ts` - Annotation store with error handling
- `src/stores/chunk.ts` - Chunk store with line-based fallback
- `src/stores/quality.ts` - Quality store with badge hiding
- `src/features/editor/components/ErrorBanner.tsx` - Error UI components
- `src/stores/__tests__/error-handling.test.ts` - Comprehensive test suite
- `src/lib/api/editor.ts` - API client with error propagation

---

## Requirements Validation

✅ **Requirement 10.2**: AST chunking fails → Line-based fallback implemented
✅ **Requirement 10.3**: Quality scores fail → Badge hiding implemented
✅ **Requirement 10.4**: Annotation API fails → Cached data fallback implemented

All error handling requirements from the design document are fully implemented and tested.
