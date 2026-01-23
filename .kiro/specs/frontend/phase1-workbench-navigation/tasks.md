# Implementation Plan: Phase 1 - Core Workbench & Navigation

## Overview

This implementation plan builds the foundational "Command Center" layout using the Hybrid Power approach (Option C), leveraging magic-mcp for generation, shadcn-ui for core primitives, and magic-ui for strategic polish.

## Tasks

- [x] 1. Setup project foundation and dependencies
  - Install required dependencies (Zustand, cmdk, framer-motion)
  - Configure shadcn-ui components via MCP
  - Set up Tailwind CSS theme configuration
  - _Requirements: All_

- [x] 2. Create Zustand stores for state management
  - [x] 2.1 Create workbench store (sidebar state)
    - Define store interface with sidebar open/collapsed state
    - Implement toggle and setter actions
    - Add localStorage persistence
    - _Requirements: 1.6_

  - [x] 2.2 Create theme store
    - Define theme type ('light' | 'dark' | 'system')
    - Implement theme setter with localStorage persistence
    - Add system preference detection
    - _Requirements: 5.1, 5.3_

  - [x] 2.3 Create repository store
    - Define Repository interface
    - Implement active repository state
    - Add repository selection action
    - Create mock repository data for development
    - _Requirements: 4.1, 4.4_

  - [x] 2.4 Create command palette store
    - Define Command interface
    - Implement open/close actions
    - Add command execution logic
    - Create initial command registry
    - _Requirements: 3.1, 3.2, 3.6_

- [x] 3. Build ThemeProvider and theme system
  - [x] 3.1 Create ThemeProvider component
    - Use magic-mcp to generate provider structure
    - Implement theme context
    - Add system preference listener
    - Apply theme to document root
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 3.2 Create ThemeToggle component
    - Use shadcn-ui DropdownMenu via MCP
    - Add theme selection options (Light, Dark, System)
    - Display current theme with icons
    - Add magic-ui smooth transition effect
    - _Requirements: 5.5, 5.6_

  - [x]* 3.3 Write property test for theme persistence
    - **Property 2: Theme Consistency**
    - **Validates: Requirements 5.1, 5.4**

- [x] 4. Build WorkbenchLayout component
  - [x] 4.1 Generate layout structure with magic-mcp
    - Create WorkbenchLayout component shell
    - Define responsive grid layout
    - Add sidebar and content area containers
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 4.2 Implement sidebar toggle logic
    - Connect to workbench store
    - Add collapse/expand animations
    - Implement responsive auto-collapse
    - Add localStorage persistence
    - _Requirements: 1.4, 1.5, 1.6_

  - [x]* 4.3 Write property test for sidebar state persistence
    - **Property 1: Sidebar State Persistence**
    - **Validates: Requirements 1.6**

  - [x]* 4.4 Write property test for responsive breakpoints
    - **Property 4: Responsive Breakpoint Behavior**
    - **Validates: Requirements 1.5, 6.1**

- [x] 5. Build WorkbenchSidebar component
  - [x] 5.1 Create navigation items configuration
    - Define navigation items array with icons and paths
    - Use lucide-react icons
    - Add route matching logic
    - _Requirements: 2.1_

  - [x] 5.2 Build sidebar navigation UI
    - Use shadcn-ui Button and Tooltip via MCP
    - Implement active route highlighting
    - Add collapsed state (icon-only view)
    - Add magic-ui entrance animations for nav items
    - _Requirements: 2.2, 2.3, 2.4, 2.6_

  - [x] 5.3 Add sidebar toggle button
    - Place at bottom of sidebar
    - Use chevron icon (left/right based on state)
    - Connect to workbench store
    - _Requirements: 2.5_

  - [x]* 5.4 Write unit tests for sidebar navigation
    - Test active route highlighting
    - Test collapsed state rendering
    - Test tooltip display
    - _Requirements: 2.1, 2.2, 2.4, 2.6_

- [x] 6. Build CommandPalette component
  - [x] 6.1 Generate command palette with magic-mcp
    - Create CommandPalette component structure
    - Set up cmdk base component
    - Add search input and results list
    - _Requirements: 3.3, 3.4_

  - [x] 6.2 Implement command palette UI
    - Use shadcn-ui Command component via MCP
    - Add magic-ui spotlight entrance animation
    - Style command items with icons and shortcuts
    - Add category grouping
    - _Requirements: 3.5, 3.6_

  - [x] 6.3 Add keyboard handling
    - Implement Cmd+K / Ctrl+K to open
    - Implement Cmd+Shift+P / Ctrl+Shift+P to open
    - Add Escape to close
    - Add arrow key navigation
    - Add Enter to execute
    - _Requirements: 3.1, 3.2, 3.7, 3.8_

  - [x] 6.4 Implement command filtering
    - Add fuzzy search logic
    - Filter commands as user types
    - Update results in real-time
    - _Requirements: 3.4_

  - [x]* 6.5 Write property test for command navigation
    - **Property 3: Command Palette Keyboard Navigation**
    - **Validates: Requirements 3.7, 3.8**

  - [x]* 6.6 Write property test for keyboard shortcut uniqueness
    - **Property 6: Keyboard Shortcut Uniqueness**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 7. Build RepositorySwitcher component
  - [x] 7.1 Create RepositorySwitcher UI
    - Use shadcn-ui DropdownMenu via MCP
    - Display current repository name
    - Add repository icon based on source
    - Add magic-ui subtle open animation
    - _Requirements: 4.1, 4.3_

  - [x] 7.2 Implement repository dropdown
    - List all available repositories
    - Show repository status badges
    - Add keyboard navigation
    - Connect to repository store
    - _Requirements: 4.2, 4.4, 4.6_

  - [x] 7.3 Add empty state handling
    - Display "No repositories" message
    - Add link to repository ingestion
    - _Requirements: 4.5_

  - [x]* 7.4 Write property test for repository selection
    - **Property 5: Repository Switcher Selection**
    - **Validates: Requirements 4.4**

- [x] 8. Build WorkbenchHeader component
  - [x] 8.1 Create header layout
    - Add logo/branding
    - Add RepositorySwitcher
    - Add CommandPalette trigger button
    - Add ThemeToggle
    - Add UserMenu (placeholder)
    - _Requirements: 1.2_

  - [x] 8.2 Make header responsive
    - Hide logo text on mobile
    - Adjust spacing for small screens
    - Ensure touch-friendly tap targets
    - _Requirements: 6.3, 6.5_

- [x] 9. Integrate components into routing
  - [x] 9.1 Update __root.tsx
    - Wrap app with ThemeProvider
    - Add global keyboard listeners
    - Add Toaster for notifications
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 9.2 Update _auth.tsx
    - Wrap authenticated routes with WorkbenchLayout
    - Pass through children to content area
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 9.3 Create placeholder routes
    - Create /repositories route
    - Create /cortex route
    - Create /library route
    - Create /planner route
    - Create /wiki route
    - Create /ops route
    - _Requirements: 2.1_

- [x] 10. Add keyboard shortcuts and accessibility
  - [x] 10.1 Implement global keyboard shortcuts
    - Cmd+B / Ctrl+B for sidebar toggle
    - Cmd+K / Ctrl+K for command palette
    - Cmd+Shift+P / Ctrl+Shift+P for command palette
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 10.2 Add accessibility features
    - Add ARIA labels to icon-only buttons
    - Ensure focus indicators are visible
    - Add screen reader announcements
    - Test keyboard navigation flow
    - _Requirements: 7.5, 7.6_

  - [x]* 10.3 Write unit tests for keyboard shortcuts
    - Test Cmd+B toggles sidebar
    - Test Cmd+K opens command palette
    - Test Escape closes command palette
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 11. Optimize performance
  - [x] 11.1 Add lazy loading for routes
    - Use React.lazy for route components
    - Add Suspense boundaries with loading states
    - _Requirements: 8.5_

  - [x] 11.2 Optimize animations
    - Use CSS transforms for sidebar animation
    - Add will-change hints
    - Ensure 60fps during animations
    - _Requirements: 1.4, 8.2, 8.4_

  - [x] 11.3 Debounce and throttle events
    - Debounce command palette search (150ms)
    - Throttle window resize events
    - _Requirements: 8.3_

- [x] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Use MCP servers (magic-mcp, shadcn-ui, magic-ui) as specified in design
