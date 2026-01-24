# Monaco Editor Decoration Batching

## Overview

The `DecorationManager` class provides optimized decoration updates for Monaco Editor through batching, debouncing, and concurrent operation limiting. This significantly improves performance when working with large files and frequent decoration updates.

## Features

### 1. Debouncing (100ms)
- Decoration updates are debounced to prevent excessive reflows
- Multiple rapid updates to the same key are coalesced into a single update
- Reduces CPU usage and improves responsiveness

### 2. Batching
- Multiple decoration updates are processed in batches (up to 5 per batch)
- Minimizes the number of DOM reflows
- Improves performance when updating multiple decoration types simultaneously

### 3. Concurrent Operation Limiting
- Maximum of 3 concurrent decoration operations
- Prevents performance degradation with many simultaneous updates
- Automatically queues excess operations for later processing

### 4. Immediate Updates
- Critical updates can bypass batching using `updateDecorationsImmediate()`
- Useful for user interactions that require instant visual feedback
- Still respects concurrent operation limits

### 5. Flush Capability
- `flush()` method applies all pending updates immediately
- Useful before critical operations (screenshots, printing, etc.)
- Ensures all decorations are in sync

## Usage

### Basic Usage

```typescript
import { DecorationManager } from '@/lib/monaco/decorations';

// Create manager
const manager = new DecorationManager(editor);

// Update decorations (debounced and batched)
manager.updateDecorations('chunks', chunkDecorations);
manager.updateDecorations('annotations', annotationDecorations);
manager.updateDecorations('quality', qualityDecorations);

// Clear specific decorations
manager.clearDecorations('chunks');

// Clear all decorations
manager.clearAll();

// Dispose when done
manager.dispose();
```

### Immediate Updates

```typescript
// For user interactions that need instant feedback
manager.updateDecorationsImmediate('selection', selectionDecorations);
```

### Flushing Pending Updates

```typescript
// Before taking a screenshot or printing
manager.flush();
await takeScreenshot();
```

### Monitoring Performance

```typescript
const stats = manager.getStats();
console.log('Active decorations:', stats.activeDecorations);
console.log('Pending updates:', stats.pendingUpdates);
console.log('Concurrent operations:', stats.concurrentOperations);
console.log('Is processing:', stats.isProcessing);
```

## Performance Characteristics

### Timing

- **Debounce delay**: 100ms (configurable via `DEBOUNCE_MS`)
- **Batch delay**: 16ms (~60fps, configurable via `BATCH_DELAY_MS`)
- **Batch size**: 5 updates per batch (configurable via `BATCH_SIZE`)
- **Max concurrent**: 3 operations (configurable via `MAX_CONCURRENT_OPERATIONS`)

### Memory

- Minimal memory overhead (only stores decoration IDs and pending updates)
- Automatic cleanup on dispose
- No memory leaks from pending timeouts

### CPU

- Reduces reflows by batching updates
- Prevents UI blocking with concurrent operation limiting
- Efficient coalescing of rapid updates to same key

## Integration with Components

### SemanticChunkOverlay

```typescript
useEffect(() => {
  if (!editor || !decorationManager) return;

  if (shouldShowChunks) {
    const decorations = createChunkDecorations(chunks, selectedChunk?.id);
    decorationManager.updateDecorations('chunks', decorations);
  } else {
    decorationManager.clearDecorations('chunks');
  }
}, [editor, decorationManager, chunks, selectedChunk, shouldShowChunks]);
```

### AnnotationGutter

```typescript
useEffect(() => {
  if (!editor || !decorationManager) return;

  if (annotationsVisible) {
    decorationManager.updateDecorations('annotation-gutter', gutterDecorations);
    decorationManager.updateDecorations('annotation-highlights', highlightDecorations);
  } else {
    decorationManager.clearDecorations('annotation-gutter');
    decorationManager.clearDecorations('annotation-highlights');
  }
}, [editor, decorationManager, annotationsVisible, gutterDecorations, highlightDecorations]);
```

### QualityBadgeGutter

```typescript
useEffect(() => {
  if (!editor || !decorationManager) return;

  if (visible && qualityData) {
    const decorations = createQualityDecorations(extractQualityBadges(qualityData));
    decorationManager.updateDecorations('quality-badges', decorations);
  } else {
    decorationManager.clearDecorations('quality-badges');
  }
}, [editor, decorationManager, visible, qualityData]);
```

## Best Practices

### 1. Use Descriptive Keys

```typescript
// Good: Descriptive keys make debugging easier
manager.updateDecorations('semantic-chunks', decorations);
manager.updateDecorations('annotation-highlights', decorations);
manager.updateDecorations('quality-badges', decorations);

// Bad: Generic keys are hard to debug
manager.updateDecorations('dec1', decorations);
manager.updateDecorations('dec2', decorations);
```

### 2. Clear Decorations When Not Needed

```typescript
// Good: Clear decorations when visibility is toggled off
if (visible) {
  manager.updateDecorations('chunks', decorations);
} else {
  manager.clearDecorations('chunks');
}

// Bad: Leaving decorations active when hidden
if (visible) {
  manager.updateDecorations('chunks', decorations);
}
```

### 3. Use Immediate Updates Sparingly

```typescript
// Good: Use immediate updates only for critical user interactions
onUserClick(() => {
  manager.updateDecorationsImmediate('selection', selectionDecorations);
});

// Bad: Using immediate updates for everything defeats batching
manager.updateDecorationsImmediate('chunks', chunkDecorations);
manager.updateDecorationsImmediate('annotations', annotationDecorations);
```

### 4. Always Dispose

```typescript
// Good: Dispose in cleanup effect
useEffect(() => {
  const manager = new DecorationManager(editor);
  
  return () => {
    manager.dispose();
  };
}, [editor]);

// Bad: Not disposing causes memory leaks
const manager = new DecorationManager(editor);
// No cleanup
```

## Troubleshooting

### Decorations Not Appearing

1. Check if decorations are being cleared immediately after update
2. Verify the decoration key is correct
3. Check if concurrent operation limit is reached (use `getStats()`)
4. Try using `flush()` to force immediate application

### Performance Issues

1. Reduce batch size if updates are too slow
2. Increase debounce delay if updates are too frequent
3. Check concurrent operation count (should be ≤ 3)
4. Profile with `getStats()` to identify bottlenecks

### Memory Leaks

1. Ensure `dispose()` is called when component unmounts
2. Check for pending timeouts with `getStats()`
3. Verify all decoration keys are being cleared

## Testing

The decoration manager includes comprehensive unit tests covering:

- Basic debouncing functionality
- Batch processing with size limits
- Concurrent operation limiting
- Immediate updates
- Flush functionality
- Statistics tracking
- Error handling
- Cleanup and disposal

Run tests with:

```bash
npm test -- src/lib/monaco/__tests__/decorations.test.ts
```

## Requirements Validation

This implementation validates:

- **Requirement 7.1**: Performance and Responsiveness
  - Virtualized rendering for large files (>5000 lines)
  - Incremental decoration rendering
  
- **Requirement 7.2**: Performance and Responsiveness
  - Lazy-loading of badge data on scroll
  - Debounced decoration updates (100ms)
  - Batched updates to reduce reflows
  - Limited concurrent operations (max 3)

## Future Enhancements

Potential improvements for future iterations:

1. **Adaptive Batching**: Adjust batch size based on file size and update frequency
2. **Priority Queue**: Allow high-priority decorations to jump the queue
3. **Metrics Collection**: Track performance metrics for optimization
4. **Web Worker Support**: Offload decoration calculation to web workers
5. **Virtual Scrolling Integration**: Only update decorations for visible lines
