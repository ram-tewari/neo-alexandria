# Implementation Plan

- [x] 1. Set up project infrastructure and base configuration





















  - Create directory structure for components/ui, components/features, lib/hooks, lib/utils, contexts
  - Configure Tailwind CSS with custom theme variables for light/dark mode
  - Set up Framer Motion and configure animation defaults



  - Create globals.css with CSS custom properties and transition-base class
  - Install and configure fuse.js for fuzzy search

  - _Requirements: 8.1, 8.2, 8.3, 9.1, 9.3, 10.1, 10.2_


- [x] 2. Implement core utility hooks and functions



  - [x] 2.1 Create useLocalStorage hook for persistent state


    - Implement hook with TypeScript generics for type-safe storage
    - Add serialization/deserialization with error handling

    - _Requirements: 2.3, 2.4, 4.3, 4.4_


  
  - [ ] 2.2 Create useKeyboardShortcut hook for global shortcuts
    - Implement keyboard event listener with modifier key support
    - Add cleanup on unmount to prevent memory leaks
    - Support Cmd (Mac) and Ctrl (Windows/Linux) detection



    - _Requirements: 3.1_

  
  - [ ] 2.3 Create useFocusTrap hook for modal focus management
    - Query focusable elements within container
    - Implement Tab key cycling between first and last elements


    - Auto-focus first element when trap activates

    - _Requirements: 3.2, 6.2, 6.4_




  

  - [ ] 2.4 Create animation utilities library
    - Define fadeIn, slideUp, scalePress, and hover animation objects
    - Export standard duration constants (100ms, 200ms, 300ms, 500ms)


    - Document usage patterns with TypeScript interfaces
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Build atomic UI components


  - [ ] 3.1 Create Skeleton component with variants
    - Implement text, circular, and rectangular variants
    - Add pulse animation with 1.5s duration
    - Support custom width/height props
    - Use Tailwind classes for theming (light/dark)
    - _Requirements: 1.1, 1.5, 9.1, 9.2, 9.3_


  
  - [ ] 3.2 Create preset skeleton components
    - Build SkeletonCard matching ResourceCard dimensions
    - Build SkeletonTable matching table row structure


    - Build SkeletonText for text content placeholders
    - _Requirements: 1.1, 1.3, 1.4_
  




  - [ ] 3.3 Create Button component with micro-interactions
    - Implement base button with variant prop (primary, secondary, ghost)
    - Add scale-press animation (95% on press, 100ms duration)
    - Add hover state transition (150ms)
    - Disable pointer events during animation


    - Export ButtonProps TypeScript interface
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 9.2, 9.3_
  
  - [ ] 3.4 Create Card component for content containers
    - Implement with padding, border-radius, and shadow
    - Support light/dark theme via CSS custom properties


    - Add optional hover animation
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [x] 3.5 Create Input component with focus indicators


    - Implement with 2px focus outline
    - Add aria-label support for accessibility



    - Support disabled and error states
    - _Requirements: 6.1, 9.2, 9.3_

- [x] 4. Implement Toast notification system


  - [ ] 4.1 Create Toast context and provider
    - Define Toast interface with id, variant, message, duration
    - Implement ToastContext with showToast, dismissToast, updateToast methods
    - Create queue management logic (max 3 visible, FIFO overflow)

    - Add auto-dismiss timer for success/info toasts (4s)
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 4.2 Create Toast component with animations
    - Implement success, error, info, and loading variants
    - Add slide-in from right animation (200ms)
    - Add slide-out to right animation on dismiss (200ms)
    - Animate Y position when toasts stack
    - Add manual dismiss button for error toasts
    - _Requirements: 5.1, 5.5_
  
  - [ ] 4.3 Create ToastContainer component
    - Position at top-right corner
    - Render active toasts with 8px vertical gap
    - Integrate with ToastContext
    - _Requirements: 5.1, 5.2_
  
  - [ ] 4.4 Add ToastProvider to root layout
    - Wrap application with ToastProvider
    - Render ToastContainer in layout
    - _Requirements: 5.1_

- [ ] 5. Implement theme system with smooth transitions
  - [ ] 5.1 Create ThemeContext and provider
    - Define ThemeContext with theme, setTheme, toggleTheme
    - Implement localStorage persistence
    - Apply theme class to document.documentElement
    - _Requirements: 4.3, 4.4, 4.5_
  
  - [ ] 5.2 Add FOUC prevention script
    - Create inline script in HTML head to apply theme before render
    - Read theme from localStorage and add class immediately
    - _Requirements: 4.2, 4.4_

  
  - [ ] 5.3 Configure CSS custom properties for theming
    - Define color variables in :root for light theme
    - Define color variables in .dark for dark theme
    - Add 200ms transition to all color properties


    - _Requirements: 4.1, 4.5_
  
  - [ ] 5.4 Create ThemeToggle component
    - Implement toggle button with icon (sun/moon)




    - Add smooth rotation or slide animation
    - Connect to ThemeContext
    - _Requirements: 4.1_


- [ ] 6. Build Command Palette feature
  - [ ] 6.1 Create Command interface and mock data
    - Define Command interface with id, label, category, icon, keywords, onSelect
    - Create mock commands for Resources, Collections, Actions
    - _Requirements: 3.5, 10.3, 10.4_

  
  - [ ] 6.2 Create CommandPalette component structure
    - Implement modal overlay with backdrop
    - Create search input with autofocus
    - Add results list container

    - Implement keyboard navigation (↑↓ arrows, Enter, Escape)
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ] 6.3 Implement fuzzy search with fuse.js
    - Configure fuse.js with threshold 0.3

    - Search across label and keywords fields
    - Ensure maximum 50ms search latency
    - _Requirements: 3.3_
  
  - [x] 6.4 Add command grouping and rendering

    - Group results by category (Resources, Collections, Actions)
    - Render category headers
    - Highlight matching text in results
    - _Requirements: 3.5_



  
  - [ ] 6.5 Integrate focus trap and keyboard shortcuts
    - Apply useFocusTrap hook to modal
    - Add useKeyboardShortcut for Cmd+K / Ctrl+K


    - Restore focus to previous element on close
    - _Requirements: 3.1, 3.2, 3.4, 6.3_
  
  - [-] 6.6 Add command palette animations

    - Implement fade-in + scale animation on open (100ms)
    - Implement fade-out animation on close (100ms)
    - Add slide-up animation for results list
    - _Requirements: 3.1_

- [ ] 7. Implement View Toggle and library layouts
  - [ ] 7.1 Create ViewToggle component
    - Implement toggle with grid and table icons
    - Add active state styling
    - Connect to viewMode state
    - _Requirements: 2.1_
  
  - [ ] 7.2 Create ResourceGrid component (card view)
    - Implement grid layout with responsive columns
    - Render ResourceCard components
    - _Requirements: 2.1, 10.2_

  
  - [ ] 7.3 Create ResourceTable component (table view)
    - Implement table with columns for title, type, tags, date
    - Add row hover states

    - _Requirements: 2.1, 10.2_

  
  - [ ] 7.4 Implement view mode persistence and transitions
    - Use useLocalStorage hook for viewMode state
    - Wrap layouts in AnimatePresence for smooth transitions
    - Add exit animation (fade-out + scale-down, 150ms)


    - Add enter animation (fade-in + slide-up, 300ms)
    - Implement scroll position restoration
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [x] 8. Implement loading states with skeletons

  - [ ] 8.1 Add skeleton loading to Dashboard
    - Replace loading text with Skeleton components
    - Match skeleton dimensions to final content layout
    - Ensure transition completes within 200ms

    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ] 8.2 Add skeleton loading to LibraryPanel
    - Display 6 SkeletonCard components in grid during loading
    - Prevent layout shift by matching final dimensions
    - _Requirements: 1.3, 1.4_
  
  - [x] 8.3 Create useResources hook with loading state

    - Implement hook that returns data, isLoading, error
    - Use mock API client with simulated 300ms latency
    - _Requirements: 10.3, 10.4_




- [ ] 9. Implement focus management and accessibility
  - [ ] 9.1 Add focus indicators to all interactive elements
    - Apply 2px outline with 2px offset to :focus-visible
    - Use primary color for outline
    - Add 4px border-radius

    - _Requirements: 6.1_

  
  - [ ] 9.2 Create skip-to-content link
    - Position absolutely off-screen by default
    - Move on-screen when focused
    - Link to main content area with id="main-content"
    - _Requirements: 6.5_

  
  - [ ] 9.3 Add aria-labels to icon-only buttons
    - Add aria-label to ThemeToggle
    - Add aria-label to ViewToggle icons
    - Add aria-label to Toast dismiss buttons
    - _Requirements: 6.1_

  
  - [ ] 9.4 Implement modal focus management
    - Move focus to first element when modal opens
    - Restore focus to trigger element when modal closes
    - Apply focus trap to CommandPalette
    - _Requirements: 6.2, 6.3, 6.4_

- [x] 10. Create API interfaces and mock data

  - [x] 10.1 Define TypeScript interfaces for API models

    - Create Resource interface matching backend Pydantic model
    - Create Collection interface
    - Create SearchResult interface
    - Create ApiClient interface with all endpoints
    - _Requirements: 10.3_
  

  - [ ] 10.2 Implement mock data generators
    - Create mockResources array with sample data
    - Create mockCollections array
    - Add variety in resource types, tags, dates
    - _Requirements: 10.4_

  
  - [ ] 10.3 Create mock API client
    - Implement createMockApiClient function
    - Add simulated network latency (300ms)
    - Implement list, get, create, update, delete methods
    - Return properly typed responses



    - _Requirements: 10.4, 10.5_

- [ ] 11. Integration and polish
  - [ ] 11.1 Wire up all components in MainLayout
    - Add ThemeProvider wrapper
    - Add ToastProvider wrapper
    - Render ThemeToggle in header

    - Render CommandPalette with global state
    - Add skip-to-content link as first element
    - _Requirements: 4.1, 5.1, 6.5_
  
  - [ ] 11.2 Create LibraryPanel feature component
    - Integrate ViewToggle, ResourceGrid, ResourceTable
    - Add loading state with skeletons
    - Connect to useResources hook
    - Handle error states with toast notifications
    - _Requirements: 1.1, 2.1, 10.2_

  
  - [x] 11.3 Verify all transitions and animations

    - Test theme toggle transition (200ms)
    - Test view toggle transition (300ms)
    - Test command palette open/close (100ms)
    - Test toast animations (200ms)
    - Test button press animations (100ms)
    - _Requirements: 1.2, 2.2, 3.1, 4.1, 5.5, 7.1, 7.2_

  
  - [ ] 11.4 Test keyboard navigation flows
    - Test Cmd+K / Ctrl+K opens command palette

    - Test Escape closes command palette
    - Test Tab navigation through all interactive elements
    - Test focus trap in modals
    - Test skip-to-content link
    - _Requirements: 3.1, 3.2, 3.4, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ] 11.5 Verify accessibility compliance
    - Run axe-core accessibility audit
    - Verify all interactive elements have focus indicators
    - Verify color contrast meets WCAG AA (4.5:1)
    - Test with keyboard-only navigation
    - Verify aria-labels on icon-only buttons
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 12. Testing and documentation
  - [ ] 12.1 Write unit tests for utility hooks
    - Test useLocalStorage with various data types
    - Test useKeyboardShortcut with different key combinations
    - Test useFocusTrap behavior
    - _Requirements: 8.4_
  
  - [ ] 12.2 Write unit tests for UI components
    - Test Button renders and handles clicks
    - Test Skeleton variants render correctly
    - Test Toast variants and animations
    - Test Card component theming
    - _Requirements: 9.2, 9.3_
  
  - [ ] 12.3 Write integration tests for features
    - Test CommandPalette keyboard navigation
    - Test Toast queue management
    - Test Theme persistence and application
    - Test ViewToggle state persistence
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4, 5.1, 5.2_
  
  - [ ] 12.4 Create Storybook documentation
    - Document all UI primitives with examples
    - Document animation utilities
    - Document theme system usage
    - _Requirements: 9.4, 8.5_
  
  - [ ] 12.5 Run performance audits
    - Run Lighthouse CI for FCP, TTI, accessibility scores
    - Verify FCP < 1.5s
    - Verify accessibility score ≥ 95
    - Verify zero layout shift (CLS = 0)
    - _Requirements: 1.2, 1.3_
