# Accessibility Features - Phase 2 Living Code Editor

## Overview

This document describes the accessibility features implemented in the Phase 2 Living Code Editor to ensure WCAG 2.1 AA compliance and provide an inclusive experience for all users.

## WCAG 2.1 AA Compliance

### 1. Keyboard Navigation

**All interactive elements are keyboard accessible:**

- **Tab Navigation**: All buttons, links, and interactive elements can be reached via Tab key
- **Focus Indicators**: 2px solid outline with 2px offset on all focused elements
- **Focus Trap**: Modals and popovers trap focus and restore it on close
- **Escape Key**: Closes all modals, popovers, and dialogs

**Editor-Specific Shortcuts:**

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + /` | Toggle annotation mode |
| `Cmd/Ctrl + Shift + A` | Show all annotations |
| `Cmd/Ctrl + Shift + Q` | Toggle quality badges |
| `Cmd/Ctrl + Shift + C` | Toggle chunk boundaries |
| `Cmd/Ctrl + Shift + R` | Toggle references |
| `Cmd/Ctrl + F` | Find in file (Monaco native) |
| `Cmd/Ctrl + G` | Go to line (Monaco native) |
| `Escape` | Close active panel/popover |

**Annotation Mode Shortcuts:**

| Shortcut | Action |
|----------|--------|
| `Enter` | Create annotation from selection |
| `Cmd/Ctrl + S` | Save annotation |
| `Cmd/Ctrl + Backspace` | Delete annotation |
| `Tab` | Next annotation |
| `Shift + Tab` | Previous annotation |

### 2. Screen Reader Support

**ARIA Labels:**

- All icon-only buttons have descriptive `aria-label` attributes
- Example: `<Button aria-label="Toggle quality badges">...</Button>`

**ARIA Live Regions:**

- Status updates announced via `aria-live="polite"` regions
- Errors announced via `aria-live="assertive"` regions
- Loading states announced to screen readers

**ARIA Roles:**

- `role="region"` for major sections (editor, panels)
- `role="dialog"` for modals and popovers
- `role="alert"` for error messages
- `role="status"` for loading states
- `role="list"` and `role="listitem"` for lists

**ARIA States:**

- `aria-expanded` for collapsible sections
- `aria-pressed` for toggle buttons
- `aria-selected` for selected items
- `aria-busy` for loading states
- `aria-hidden="true"` for decorative icons

**Screen Reader Announcements:**

```typescript
// Success announcement
announceSuccess("Annotation created successfully");

// Error announcement
announceError("Failed to load quality data");

// Warning announcement
announceWarning("Using cached annotations");

// Loading announcement
announceLoading("Loading code chunks");
```

### 3. Color Contrast

**All text meets WCAG AA contrast ratio (4.5:1):**

- Primary text: High contrast against background
- Secondary text: Muted but still readable
- Error text: Red with sufficient contrast
- Warning text: Yellow/amber with sufficient contrast

**Quality Badges - Non-Color Identification:**

Quality badges use both color AND patterns for identification:

- **High Quality (Green)**: Checkmark icon pattern
- **Medium Quality (Yellow)**: Dash icon pattern  
- **Low Quality (Red)**: X icon pattern

This ensures users with color blindness can distinguish quality levels.

**Annotation Highlights:**

- Annotations use both color AND border for identification
- Border-bottom: 2px solid for visibility
- Background: Semi-transparent overlay

### 4. Focus Management

**Modal Focus Trap:**

```typescript
// Focus is trapped within modals
createFocusTrap(modalElement, {
  initialFocus: firstButton,
  returnFocus: previouslyFocusedElement,
  onEscape: closeModal,
});
```

**Focus Restoration:**

- Focus returns to trigger element when modal closes
- Focus moves to first focusable element when modal opens
- Tab cycles through focusable elements within modal

**Focus Indicators:**

- 2px solid outline in primary color
- 2px offset from element
- Visible on all interactive elements
- Applied via `:focus-visible` pseudo-class

### 5. Semantic HTML

**Proper HTML Structure:**

- `<button>` for clickable actions
- `<a>` for navigation links
- `<nav>` for navigation sections
- `<main>` for main content
- `<aside>` for side panels
- `<article>` for independent content
- `<section>` for thematic grouping

**Heading Hierarchy:**

- Proper heading levels (h1, h2, h3, etc.)
- No skipped heading levels
- Logical document outline

## Component-Specific Accessibility

### MonacoEditorWrapper

**Features:**

- `role="region"` with `aria-label="Code editor"`
- Loading state announced to screen readers
- Keyboard shortcuts for navigation
- Focus management for editor instance

**ARIA Attributes:**

```tsx
<div 
  role="region"
  aria-label="Code editor"
  aria-busy={isLoading}
>
  <Editor ... />
</div>
```

### QualityBadgeGutter

**Features:**

- Quality badges have `aria-label` with level and percentage
- Keyboard focusable with Tab
- Focus indicator visible
- Non-color identification via patterns

**ARIA Labels:**

```typescript
aria-label="Quality high, 85 percent"
aria-label="Quality medium, 65 percent"
aria-label="Quality low, 45 percent"
```

### AnnotationGutter

**Features:**

- Annotation chips have `aria-label` with position info
- Keyboard focusable
- Focus indicator visible
- Click and keyboard activation

**ARIA Labels:**

```typescript
aria-label="Annotation 1 of 3"
```

### HoverCardProvider

**Features:**

- `role="dialog"` for hover card
- `aria-label` and `aria-describedby` for content
- Loading state announced
- Keyboard navigation for related symbols
- Escape key closes hover card

**ARIA Attributes:**

```tsx
<HoverCardContent
  role="dialog"
  aria-label="Symbol information"
  aria-describedby="hover-card-content"
>
  ...
</HoverCardContent>
```

### ChunkMetadataPanel

**Features:**

- `role="region"` with `aria-label="Chunk metadata"`
- Expand/collapse button has `aria-expanded` state
- All metadata labeled for screen readers
- Keyboard navigation

**ARIA Attributes:**

```tsx
<Button
  aria-label="Collapse chunk metadata"
  aria-expanded={expanded}
>
  ...
</Button>
```

### ErrorBanner

**Features:**

- `role="alert"` for error messages
- `aria-live="polite"` for status updates
- Retry and dismiss buttons have descriptive labels
- Error announced to screen readers on mount

**ARIA Attributes:**

```tsx
<Alert
  role="alert"
  aria-live="polite"
  aria-atomic="true"
>
  ...
</Alert>
```

## Testing Accessibility

### Manual Testing

**Keyboard-Only Navigation:**

1. Disconnect mouse
2. Navigate entire editor using only keyboard
3. Verify all features are accessible
4. Check focus indicators are visible
5. Test all keyboard shortcuts

**Screen Reader Testing:**

1. Enable screen reader (NVDA, JAWS, VoiceOver)
2. Navigate through editor
3. Verify all elements are announced correctly
4. Check ARIA labels are descriptive
5. Test status announcements

**Color Contrast Testing:**

1. Use browser DevTools contrast checker
2. Verify all text meets 4.5:1 ratio
3. Test with color blindness simulators
4. Verify quality badges are distinguishable without color

### Automated Testing

**Accessibility Tests:**

```typescript
// Test keyboard navigation
test('all interactive elements are keyboard accessible', () => {
  // Test implementation
});

// Test ARIA labels
test('all icon buttons have aria-label', () => {
  // Test implementation
});

// Test focus management
test('focus is trapped in modal', () => {
  // Test implementation
});

// Test color contrast
test('all text meets WCAG AA contrast ratio', () => {
  // Test implementation
});
```

## Accessibility Utilities

### Screen Reader Announcer

```typescript
import { announce, announceError, announceSuccess } from '@/lib/accessibility';

// Announce message
announce('Annotation created', 'polite');

// Announce error
announceError('Failed to load data');

// Announce success
announceSuccess('Changes saved');
```

### Focus Trap

```typescript
import { createFocusTrap } from '@/lib/accessibility';

const cleanup = createFocusTrap(modalElement, {
  initialFocus: firstButton,
  returnFocus: triggerButton,
  onEscape: closeModal,
});

// Later...
cleanup();
```

### ARIA Utilities

```typescript
import { 
  setAriaLabel,
  setAriaExpanded,
  createIconButtonLabel,
  createToggleButtonLabel,
} from '@/lib/accessibility';

// Set ARIA label
setAriaLabel(button, 'Close dialog');

// Set ARIA expanded
setAriaExpanded(button, true);

// Create labels
const label = createIconButtonLabel('Delete', 'annotation');
const toggleLabel = createToggleButtonLabel('quality badges', true);
```

## Known Limitations

1. **Monaco Editor**: Some Monaco-specific features may have limited screen reader support
2. **Hover Cards**: Hover-triggered content may be difficult for some users to access
3. **Gutter Decorations**: Monaco gutter decorations have limited ARIA support

## Future Improvements

1. **Voice Control**: Add voice command support for common actions
2. **High Contrast Mode**: Dedicated high contrast theme
3. **Reduced Motion**: Respect `prefers-reduced-motion` setting
4. **Font Scaling**: Better support for browser font size changes
5. **Touch Targets**: Ensure all touch targets are at least 44x44px

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)

## Compliance Checklist

- [x] All interactive elements keyboard accessible
- [x] Focus indicators visible (2px outline, 2px offset)
- [x] ARIA labels on all icon-only buttons
- [x] Screen reader announcements for status updates
- [x] Color contrast meets WCAG AA (4.5:1)
- [x] Focus management for modals and popovers
- [x] Semantic HTML structure
- [x] Proper heading hierarchy
- [x] Non-color identification for quality badges
- [x] Keyboard shortcuts documented
- [x] Error messages accessible
- [x] Loading states announced
- [x] Skip links for navigation (if applicable)
