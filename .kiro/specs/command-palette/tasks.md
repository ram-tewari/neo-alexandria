 # Implementation Plan

## Phase 1: Core Functionality & Visual Foundation

- [x] 1. Create fuzzy search utility and command registry service









  - Implement lightweight fuzzy search algorithm with character matching and scoring
  - Create CommandRegistry service with Map-based storage and registration methods
  - Add search method that returns ranked results with match positions
  - Add validation for command structure on registration


  - _Requirements: 2.1, 2.2, 2.3, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 1.1 Write unit tests for fuzzy search and command registry


  - Test fuzzy search scoring, case-insensitivity, and keyword matching
  - Test command registration, unregistration, and duplicate prevention
  - Test search filtering and category grouping
  - _Requirements: 2.1, 2.2, 7.1, 7.2, 7.3_



- [x] 2. Update CSS variables for marble backdrop colors
  - Add marble-specific color variables to variables.css
  - Define --marble-base, --marble-vein-black, --marble-vein-gold
  - Define --marble-gradient-gold and --marble-gradient-black

  - Ensure variables are scoped to .light theme only
  - _Requirements: 6.2, 6.3_

- [x] 3. Create MarbleBackdrop component for light mode

  - Create MarbleBackdrop.tsx component with theme detection
  - Implement CSS-based marble texture using SVG or gradient patterns
  - Add off-white base color (#fafaf8) with gold and black veins
  - Create subtle animated gradient overlay with 20-second loop
  - Add conditional rendering to show only in light mode
  - Apply GPU acceleration with CSS transforms and will-change
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Write tests for MarbleBackdrop component

  - Test visibility in light mode and hidden in dark mode
  - Test theme switching behavior
  - Test animation performance
  - _Requirements: 6.1, 6.5_


- [x] 4. Integrate MarbleBackdrop into MainLayout

  - Import MarbleBackdrop component in MainLayout.tsx
  - Position backdrop behind existing AnimatedOrbs and GridPattern
  - Ensure proper z-index layering (backdrop at z-index: -1)
  - Verify no interference with content readability
  - _Requirements: 6.1, 6.4_


- [x] 5. Enhance CommandPalette with fuzzy search
  - Integrate fuzzy search utility into CommandPalette component
  - Replace simple filter with fuzzy search algorithm
  - Implement result ranking based on relevance score and priority
  - Add match highlighting by wrapping matched characters in mark elements
  - Apply debouncing (50ms) to search input
  - Display top 10 results maximum
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 4.4_

- [x] 6. Implement theme-aware styling for command palette
  - Update CommandPalette.css with CSS variables for theme support
  - Define dark mode styles using purple accent system
  - Define light mode styles using gold accent system
  - Add theme-specific overlay colors with backdrop blur
  - Style search bar with theme-aware borders and focus states
  - Style result items with theme-aware hover and selected states
  - Add smooth transitions for theme switching (100ms)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Extend command registry with built-in commands
  - Register navigation commands (Dashboard, Library, Knowledge Graph)
  - Register action commands (Add Resource, Create Collection)
  - Register filter commands (Unread, Completed)
  - Add help command that explains palette usage
  - Define keyboard shortcuts for each command
  - Set appropriate priority values for ranking
  - _Requirements: 2.5, 7.1, 7.3, 8.4_

## Phase 2: Enhanced UX & Polish

- [x] 8. Improve keyboard navigation with wrap-around
  - Modify arrow key handlers to wrap from last to first result
  - Modify arrow key handlers to wrap from first to last result
  - Add Tab and Shift+Tab support as alternatives to arrow keys
  - Ensure selected item scrolls into view automatically
  - Update aria-activedescendant for screen reader support
  - _Requirements: 3.1, 3.2, 3.5, 3.6_

- [x] 9. Enhance result display with icons and shortcuts
  - Update CommandItem to display icon, title, and optional shortcut
  - Add description field support for secondary text below title
  - Implement consistent spacing (12px gaps) and sizing (48px height)
  - Style shortcut hints with kbd element on the right side
  - Add category headers with proper grouping
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.2, 8.3, 8.5_

- [x] 10. Add empty state and default commands display
  - Create EmptyState component with "No results found" message
  - Display empty state when filteredCommands.length === 0
  - Show suggested/frequently used commands when query is empty
  - Add help hint in empty state ("Press ESC to close")
  - Group default commands by category with headers
  - _Requirements: 2.4, 8.1, 8.2, 8.3, 8.4_

- [x] 11. Implement smooth animations and transitions
  - Enhance modal entrance/exit animations with spring physics
  - Add hover animation to result items (4px x-shift)
  - Implement reduced motion support using useReducedMotion hook
  - Add loading state animation for async command execution
  - Ensure all animations complete within 200ms
  - _Requirements: 1.3_

- [x] 12. Add command execution error handling
  - Wrap command execution in try-catch block
  - Display toast notification for async command failures
  - Log errors to console for debugging
  - Keep palette open on error for retry
  - Add error icon indicator next to failed command
  - _Requirements: 7.4_

- [x] 13. Optimize performance with memoization and virtual scrolling
  - Memoize CommandItem components with React.memo
  - Use useMemo for filtered results calculation
  - Use useCallback for event handlers
  - Implement virtual scrolling for results list if >50 items
  - Add performance monitoring for search execution time
  - _Requirements: 1.3, 2.1_

- [x] 14. Enhance accessibility with ARIA attributes and focus management
  - Add role="dialog" and aria-modal="true" to modal
  - Add role="combobox" to search input with aria-expanded
  - Add role="listbox" to results container
  - Add role="option" to each result item with unique IDs
  - Implement focus trap within modal when open
  - Restore focus to previous element on close
  - Update aria-activedescendant on selection change
  - _Requirements: 3.4_

- [x] 14.1 Write accessibility tests
  - Test keyboard navigation functionality
  - Test screen reader announcements
  - Test focus management on open/close
  - Test ARIA attributes presence
  - Test color contrast ratios
  - _Requirements: 3.1, 3.2, 3.3, 5.3_

- [x] 15. Create integration tests for theme and navigation
  - Test theme switching updates palette styles immediately
  - Test marble backdrop visibility toggles with theme
  - Test navigation commands route correctly
  - Test palette closes after command execution
  - Test UIStore state synchronization
  - _Requirements: 5.1, 5.2, 5.4, 6.1, 6.5_

- [x] 16. Add visual regression tests
  - Capture palette appearance in dark mode
  - Capture palette appearance in light mode
  - Capture marble backdrop rendering
  - Capture search results layout
  - Capture empty state appearance
  - Capture hover and selected states
  - _Requirements: 5.1, 5.2, 6.1_
