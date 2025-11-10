# Neo Alexandria 2.0 - Accessibility Implementation

This document outlines the accessibility features implemented in the Neo Alexandria 2.0 frontend application to ensure WCAG 2.1 Level AA compliance.

## Overview

The application has been enhanced with comprehensive accessibility features including:
- ARIA labels and semantic HTML
- Keyboard navigation and shortcuts
- Focus indicators
- Skip links
- Screen reader support

## Features Implemented

### 1. ARIA Labels and Semantic HTML

#### Semantic HTML Structure
- Used `<nav>` element with `role="navigation"` and `aria-label="Main navigation"`
- Used `<main>` element with `id="main-content"` and `role="main"`
- Used semantic heading hierarchy throughout

#### ARIA Labels
- Added `aria-label` to icon-only buttons (e.g., mobile menu toggle, close buttons)
- Added `aria-hidden="true"` to decorative icons
- Added `aria-describedby` to form inputs linking to error/hint messages
- Added `aria-invalid` to form inputs with validation errors
- Added `aria-live` regions for dynamic content (loading states, toasts)
- Added `aria-modal="true"` to modal dialogs
- Added `aria-haspopup="true"` to dropdown triggers

#### Form Accessibility
- All form inputs have associated labels using `htmlFor` and `id`
- Error messages have `role="alert"` for immediate announcement
- Form inputs use `aria-describedby` to link to hints and errors
- Form inputs use `aria-invalid` to indicate validation state

#### Loading States
- Loading spinners have `role="status"` and `aria-live="polite"`
- Screen reader text provided with `.sr-only` class when no visible text
- Loading overlays have `aria-busy="true"`

### 2. Keyboard Navigation

#### Global Keyboard Shortcuts
- `Alt + H` - Navigate to Home
- `Alt + L` - Navigate to Library
- `Alt + S` - Navigate to Search
- `Alt + G` - Navigate to Knowledge Graph
- `Alt + C` - Navigate to Collections
- `Alt + P` - Navigate to Profile
- `Ctrl/Cmd + K` - Quick search (focuses search input)
- `?` - Show keyboard shortcuts help

#### Navigation
- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Shift + Tab for reverse navigation
- Enter/Space to activate buttons and links

#### Modal and Dropdown Behavior
- Escape key closes modals and dropdowns
- Focus trap implemented in modals
- Focus returns to trigger element when modal closes
- Arrow keys for dropdown navigation

#### Custom Hooks
Created `useKeyboardShortcuts.ts` with the following hooks:
- `useKeyboardShortcut()` - Register individual keyboard shortcuts
- `useGlobalKeyboardShortcuts()` - Enable global navigation shortcuts
- `useFocusTrap()` - Trap focus within modals
- `useEscapeKey()` - Handle escape key press
- `useArrowKeyNavigation()` - Navigate lists with arrow keys

### 3. Focus Indicators

#### Global Focus Styles
- All focusable elements have visible focus indicators
- Focus ring color: `accent-blue-500` (high contrast)
- Focus ring width: 2px with 2px offset
- Focus-visible pseudo-class used to show focus only for keyboard users

#### Component-Specific Focus
- Buttons: 2px ring with offset, color varies by variant
- Links: 2px ring with accent blue color
- Inputs: 2px ring with primary color
- Navigation items: 2px ring with accent blue color
- Cards and interactive elements: visible focus outline

#### CSS Implementation
```css
*:focus-visible {
  outline: 2px solid theme('colors.accent-blue.500');
  outline-offset: 2px;
}

/* Remove focus for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}
```

### 4. Skip Links

#### Implementation
Two skip links at the top of every page:
1. "Skip to main content" - Jumps to `#main-content`
2. "Skip to navigation" - Jumps to `#navigation`

#### Styling
- Hidden by default using `.sr-only` class
- Visible when focused with keyboard
- Positioned absolutely at top-left
- High z-index (100) to appear above all content
- Styled with accent blue background for visibility
- Includes focus ring for additional visibility

### 5. Screen Reader Support

#### Screen Reader Only Content
- `.sr-only` utility class for visually hidden content
- Used for:
  - Loading state announcements
  - Icon button labels
  - Form field descriptions
  - Status updates

#### Live Regions
- Toast notifications: `aria-live="polite"` and `aria-atomic="true"`
- Loading states: `aria-live="polite"`
- Error messages: `role="alert"` (implicit `aria-live="assertive"`)

#### Semantic Structure
- Proper heading hierarchy (h1 → h2 → h3)
- Landmark regions (nav, main, footer)
- Lists for navigation items
- Buttons vs links used appropriately

## Testing Recommendations

### Manual Testing
1. **Keyboard Navigation**
   - Tab through all interactive elements
   - Verify focus indicators are visible
   - Test all keyboard shortcuts
   - Verify modal focus trap works

2. **Screen Reader Testing**
   - Test with NVDA (Windows)
   - Test with VoiceOver (macOS)
   - Verify all content is announced
   - Test form validation announcements
   - **See detailed guide**: [SCREEN_READER_TESTING.md](./SCREEN_READER_TESTING.md)
   - **Quick checklist**: [SCREEN_READER_TEST_CHECKLIST.md](./SCREEN_READER_TEST_CHECKLIST.md)
   - **Results template**: [SCREEN_READER_TEST_RESULTS_TEMPLATE.md](./SCREEN_READER_TEST_RESULTS_TEMPLATE.md)

3. **Visual Testing**
   - Verify focus indicators are visible on all elements
   - Check color contrast ratios (minimum 4.5:1 for text)
   - Test with browser zoom at 200%

### Automated Testing
- Use axe DevTools browser extension
- Run Lighthouse accessibility audit
- Use WAVE browser extension

## Browser Support

Focus-visible is supported in:
- Chrome 86+
- Firefox 85+
- Safari 15.4+
- Edge 86+

For older browsers, a polyfill may be needed.

## Future Enhancements

1. **Reduced Motion**
   - Respect `prefers-reduced-motion` media query
   - Disable animations when requested

2. **High Contrast Mode**
   - Test and optimize for Windows High Contrast Mode
   - Ensure focus indicators remain visible

3. **Voice Control**
   - Ensure all interactive elements have accessible names
   - Test with voice control software

4. **Mobile Accessibility**
   - Ensure touch targets are at least 44x44px
   - Test with mobile screen readers (TalkBack, VoiceOver)

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Compliance

This implementation targets WCAG 2.1 Level AA compliance, addressing:
- Perceivable: Text alternatives, adaptable content, distinguishable elements
- Operable: Keyboard accessible, enough time, navigable, input modalities
- Understandable: Readable, predictable, input assistance
- Robust: Compatible with assistive technologies

## Contact

For accessibility issues or suggestions, please contact the development team.
