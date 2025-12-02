# Batch Selection Implementation

This document describes the batch selection feature implementation for the Neo Alexandria library view.

## Overview

The batch selection feature allows users to select multiple resources and perform bulk operations on them. It includes:

- **Batch mode toggle** in the library header
- **Checkboxes** on resource cards when batch mode is active
- **Floating toolbar** with batch action buttons
- **Keyboard shortcuts** for efficient selection
- **Range selection** with Shift+Click

## Components

### 1. useBatchSelection Hook

Location: `frontend/src/lib/hooks/useBatchSelection.ts`

A custom hook that manages batch selection state using a Set for efficient lookups.

**API:**
```typescript
const {
  selectedIds,      // Set<string> - Currently selected IDs
  toggleSelection,  // (id: string) => void - Toggle single item
  selectAll,        // (ids: string[]) => void - Select all items
  clearSelection,   // () => void - Clear all selections
  isSelected,       // (id: string) => boolean - Check if selected
  selectedCount,    // number - Count of selected items
} = useBatchSelection();
```

### 2. Checkbox Component

Location: `frontend/src/components/ui/Checkbox/Checkbox.tsx`

An accessible checkbox component with:
- Custom styling matching the design system
- Focus indicators for keyboard navigation
- Animated checkmark appearance
- Support for disabled state

### 3. BatchToolbar Component

Location: `frontend/src/components/features/library/BatchToolbar.tsx`

A floating toolbar that appears at the bottom of the screen when resources are selected.

**Features:**
- Displays selected count
- Batch action buttons (Add to Collection, Change Status, Update Tags)
- Clear selection button
- Slide-up animation with Framer Motion
- Calls `resourcesApi.batchUpdate()` for operations

**Note:** The batch action buttons currently show placeholder toasts. Full implementation requires:
- Collection selection modal
- Status selection dropdown
- Tag editor interface

### 4. Enhanced ResourceCard

Location: `frontend/src/components/features/ResourceGrid/ResourceCard.tsx`

Updated to support batch mode:
- Shows checkbox when `batchMode` is true
- Highlights with blue ring when selected
- Handles click events differently in batch mode
- Prevents event bubbling for checkbox clicks

### 5. LibraryView Integration

Location: `frontend/src/components/features/library/LibraryView.tsx`

Main integration point that:
- Manages batch mode state
- Renders batch mode toggle button
- Passes batch props down to child components
- Implements keyboard shortcuts
- Handles range selection logic

## Keyboard Shortcuts

When batch mode is active:

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + A` | Select all visible resources |
| `Shift + Click` | Range selection from last clicked item |
| `Escape` | Clear all selections |

## Usage Example

```tsx
import { LibraryView } from './components/features/library/LibraryView';

function App() {
  return (
    <LibraryView
      onResourceClick={(resource) => console.log('Clicked:', resource)}
      facets={mockFacets}
    />
  );
}
```

## Implementation Details

### Range Selection

Range selection is implemented by:
1. Tracking the last clicked item index in a ref
2. Detecting Shift key state with keydown/keyup listeners
3. When Shift+Click occurs, selecting all items between last clicked and current
4. Using array slice to get the range of resources

### Batch API Calls

The `resourcesApi.batchUpdate()` method currently:
- Takes an array of resource IDs and update data
- Performs sequential updates (one API call per resource)
- Should be replaced with a dedicated batch endpoint when available

### State Management

- Batch mode state: Local component state in LibraryView
- Selection state: Managed by useBatchSelection hook
- Shift key state: Tracked in a ref to avoid re-renders
- Last clicked index: Tracked in a ref for range selection

## Accessibility

- All checkboxes have proper ARIA labels
- Batch mode toggle has `aria-pressed` attribute
- Keyboard shortcuts work without mouse
- Focus indicators visible on all interactive elements
- Screen readers announce selection count in toolbar

## Future Enhancements

1. **Batch Action Modals**
   - Collection selection modal
   - Status dropdown with options
   - Tag editor with autocomplete

2. **Performance Optimization**
   - Virtual scrolling for large selections
   - Debounced batch operations
   - Optimistic UI updates

3. **Additional Features**
   - Select all across pages (not just visible)
   - Invert selection
   - Save selection as smart collection
   - Export selected resources

## Testing

To test batch selection:

1. Navigate to library view
2. Click "Batch Select" button in header
3. Click checkboxes or cards to select items
4. Try keyboard shortcuts:
   - Cmd/Ctrl+A to select all
   - Shift+Click for range selection
   - Escape to clear
5. Verify toolbar appears with correct count
6. Test batch action buttons (currently show toasts)

## Related Files

- `frontend/src/lib/hooks/useBatchSelection.ts` - Selection state hook
- `frontend/src/components/ui/Checkbox/Checkbox.tsx` - Checkbox component
- `frontend/src/components/features/library/BatchToolbar.tsx` - Floating toolbar
- `frontend/src/components/features/library/LibraryView.tsx` - Main integration
- `frontend/src/components/features/ResourceGrid/ResourceCard.tsx` - Card with checkbox
- `frontend/src/components/features/ResourceGrid/ResourceGrid.tsx` - Grid with batch support
- `frontend/src/components/features/LibraryPanel/LibraryPanel.tsx` - Panel with batch support
- `frontend/src/lib/api/resources.ts` - API client with batchUpdate method
