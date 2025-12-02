# Implementation Plan: Sidebar Redesign

## Overview

This implementation plan breaks down the sidebar redesign into manageable tasks. The approach is to build new components alongside the existing sidebar, then swap them in once complete.

---

## Phase 1: Foundation and Core Components

### 1. Create Sidebar Context and Provider

- [x] 1.1 Create useSidebar hook
  - Create `src/components/sidebar/useSidebar.ts`
  - Define SidebarContext interface with state, open, openMobile, isMobile, setOpen, setOpenMobile, toggleSidebar
  - Create SidebarContext with createContext
  - Implement useSidebar hook that returns context
  - Throw error if used outside provider
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 1.2 Create SidebarProvider component
  - Create `src/components/sidebar/SidebarProvider.tsx`
  - Define SidebarProviderProps interface (defaultOpen, open, onOpenChange, children)
  - Implement controlled and uncontrolled state management
  - Add useMediaQuery hook for mobile detection
  - Implement keyboard shortcut handler (Ctrl/Cmd + B)
  - Add localStorage persistence for sidebar state
  - Wrap children in SidebarContext.Provider
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 5.4_

- [x] 1.3 Create sidebar CSS variables
  - Create `src/components/sidebar/sidebar.css`
  - Define CSS variables for sidebar widths (260px, 60px, 280px mobile)
  - Define transition timing variables
  - Define purple accent colors for sidebar
  - Export all variables
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

### 2. Create Main Sidebar Container

- [x] 2.1 Create Sidebar component structure
  - Create `src/components/sidebar/Sidebar.tsx`
  - Define SidebarProps interface (side, variant, collapsible, className, children)
  - Import useSidebar hook
  - Create motion.aside element with data attributes for state
  - Apply conditional classes based on state
  - _Requirements: 1.1, 1.2, 1.3, 8.1_

- [x] 2.2 Implement collapsible width animation
  - Use Framer Motion for width transitions
  - Animate between 260px (expanded) and 60px (collapsed)
  - Use cubic-bezier easing for smooth motion
  - Set duration to 300ms
  - _Requirements: 1.1, 1.2, 8.1, 8.2, 11.3_

- [x] 2.3 Implement mobile responsive behavior
  - Add translateX animation for mobile
  - Show/hide based on openMobile state
  - Add backdrop overlay when open on mobile
  - Handle backdrop click to close
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2.4 Add sidebar styling
  - Apply glassmorphism background
  - Add border-right with purple tint
  - Set fixed positioning
  - Add z-index layering
  - Apply smooth transitions
  - _Requirements: 9.1, 9.2, 9.3, 11.2_

### 3. Create Sidebar Layout Components

- [x] 3.1 Create SidebarHeader component
  - Create `src/components/sidebar/SidebarHeader.tsx`
  - Define SidebarHeaderProps interface
  - Create sticky header container
  - Add border-bottom separator
  - Apply padding and styling
  - _Requirements: 7.1, 7.3, 7.5_

- [x] 3.2 Create SidebarFooter component
  - Create `src/components/sidebar/SidebarFooter.tsx`
  - Define SidebarFooterProps interface
  - Create sticky footer container
  - Add border-top separator
  - Apply padding and styling
  - _Requirements: 7.2, 7.3, 7.5_

- [x] 3.3 Create SidebarContent component
  - Create `src/components/sidebar/SidebarContent.tsx`
  - Define SidebarContentProps interface
  - Create scrollable content container
  - Add custom scrollbar styling (4px, purple)
  - Set flex: 1 for proper layout
  - _Requirements: 7.3, 11.1_

---

## Phase 2: Navigation Components

### 4. Create Sidebar Group Components

- [x] 4.1 Create SidebarGroup component
  - Create `src/components/sidebar/SidebarGroup.tsx`
  - Define SidebarGroupProps interface
  - Create group container with padding
  - Add margin-bottom for spacing
  - _Requirements: 3.1, 3.5_

- [x] 4.2 Create SidebarGroupLabel component
  - Create `src/components/sidebar/SidebarGroupLabel.tsx`
  - Define SidebarGroupLabelProps interface
  - Style as uppercase, small text
  - Add fade out animation in collapsed mode
  - Apply gray-400 color
  - _Requirements: 3.2, 8.2_

- [x] 4.3 Create SidebarGroupContent component
  - Create `src/components/sidebar/SidebarGroupContent.tsx`
  - Define SidebarGroupContentProps interface
  - Create container for group items
  - Support collapsible functionality
  - _Requirements: 3.1, 3.4_

### 5. Create Menu Components

- [x] 5.1 Create SidebarMenu component
  - Create `src/components/sidebar/SidebarMenu.tsx`
  - Define SidebarMenuProps interface
  - Create menu list container
  - Apply proper spacing
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 5.2 Create SidebarMenuItem component
  - Create `src/components/sidebar/SidebarMenuItem.tsx`
  - Define SidebarMenuItemProps interface
  - Create menu item wrapper
  - Support active state
  - _Requirements: 4.1, 4.2, 4.5_

- [x] 5.3 Create SidebarMenuButton component
  - Create `src/components/sidebar/SidebarMenuButton.tsx`
  - Define SidebarMenuButtonProps interface (asChild, isActive, tooltip, icon, children)
  - Implement button with icon and label
  - Add purple glow effect on hover
  - Add left accent bar animation
  - Support asChild pattern for custom elements
  - _Requirements: 4.1, 4.2, 4.3, 8.1, 8.2_

- [x] 5.4 Add collapsed mode styling to menu button
  - Hide label text in collapsed mode (opacity 0, width 0)
  - Center icon when collapsed
  - Adjust padding for icon-only mode
  - Add smooth transitions
  - _Requirements: 1.2, 8.2_

- [x] 5.5 Create SidebarMenuBadge component
  - Create `src/components/sidebar/SidebarMenuBadge.tsx`
  - Define SidebarMenuBadgeProps interface
  - Style badge with purple background
  - Position absolutely on menu item
  - Hide in collapsed mode
  - _Requirements: 4.4_

### 6. Create Tooltip System

- [x] 6.1 Create Tooltip component
  - Create `src/components/sidebar/Tooltip.tsx`
  - Define TooltipProps interface (content, side, children)
  - Implement tooltip wrapper
  - Show tooltip only in collapsed mode
  - Position tooltip to the right of icon
  - _Requirements: 1.4_

- [x] 6.2 Style tooltip component
  - Create tooltip CSS in sidebar.css
  - Add glassmorphism background
  - Add purple border
  - Position with absolute positioning
  - Add fade-in animation
  - Add arrow pointer
  - _Requirements: 1.4, 9.3_

- [x] 6.3 Integrate tooltip with SidebarMenuButton
  - Wrap SidebarMenuButton content in Tooltip
  - Pass label as tooltip content
  - Only show when sidebar is collapsed
  - Add hover delay (200ms)
  - _Requirements: 1.4_

---

## Phase 3: Interactive Features

### 7. Create Sidebar Rail

- [x] 7.1 Create SidebarRail component
  - Create `src/components/sidebar/SidebarRail.tsx`
  - Define SidebarRailProps interface
  - Create 4px wide rail button
  - Position on right edge of sidebar
  - Only show when sidebar is collapsed
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 7.2 Style sidebar rail
  - Add purple background color
  - Set opacity to 0 by default
  - Increase opacity on hover (0.5)
  - Increase width on hover (6px)
  - Add smooth transitions
  - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [x] 7.3 Implement rail click handler
  - Connect onClick to toggleSidebar from context
  - Add aria-label for accessibility
  - Add visual feedback on click
  - _Requirements: 5.3, 10.2_

### 8. Implement Collapsible Groups

- [x] 8.1 Add Collapsible wrapper support
  - Install or create Collapsible component if needed
  - Wrap SidebarGroup in Collapsible
  - Add ChevronDown icon to group label
  - Rotate icon when expanded
  - _Requirements: 3.3, 3.4_

- [x] 8.2 Style collapsible groups
  - Add transition to group content
  - Animate max-height for smooth collapse
  - Add rotation animation to chevron icon
  - _Requirements: 3.4, 8.2_

### 9. Add Keyboard Shortcuts

- [x] 9.1 Implement keyboard shortcut handler
  - Listen for Ctrl/Cmd + B in SidebarProvider
  - Call toggleSidebar when triggered
  - Prevent default browser behavior
  - Add cleanup on unmount
  - _Requirements: 2.4, 10.1_

- [x] 9.2 Add keyboard navigation within sidebar
  - Support Tab key for sequential navigation
  - Support Arrow keys for menu navigation
  - Support Enter/Space for activation
  - Support Escape to close on mobile
  - _Requirements: 10.1, 10.2_

---

## Phase 4: Integration and Migration

### 10. Update MainLayout

- [x] 10.1 Wrap app in SidebarProvider
  - Update `src/components/layout/MainLayout.tsx`
  - Import SidebarProvider
  - Wrap entire layout in provider
  - Set defaultOpen based on localStorage
  - _Requirements: 2.1, 2.2, 5.5_

- [x] 10.2 Replace old Sidebar with new implementation
  - Import new Sidebar components
  - Build sidebar structure with Header, Content, Footer
  - Add SidebarGroups for Main and Collections
  - Add SidebarRail component
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 5.1_

- [x] 10.3 Update navigation data structure
  - Ensure all navigation items have iconName
  - Add tooltip text for collapsed mode
  - Add badge counts where needed
  - Update paths to match routing
  - _Requirements: 4.3, 4.4_

- [x] 10.4 Update main content area margin
  - Adjust margin-left based on sidebar state
  - Animate margin changes with sidebar
  - Handle mobile layout (no margin)
  - Test responsive behavior
  - _Requirements: 6.1, 6.2, 8.5_

### 11. Add Sidebar Toggle Button

- [x] 11.1 Create SidebarTrigger component
  - Create `src/components/sidebar/SidebarTrigger.tsx`
  - Define SidebarTriggerProps interface
  - Create button that calls toggleSidebar
  - Add menu icon
  - Style as minimal button
  - _Requirements: 2.4, 10.2_

- [x] 11.2 Add trigger to Navbar
  - Import SidebarTrigger
  - Add to navbar on mobile
  - Position appropriately
  - Add hover animation
  - _Requirements: 2.4, 6.2_

### 12. Polish and Refinement

- [x] 12.1 Add smooth animations to all transitions
  - Verify all width transitions are smooth
  - Verify label fade in/out is smooth
  - Verify mobile slide animation is smooth
  - Test on different devices
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12.2 Refine purple accent styling
  - Update all hover states to use purple
  - Update active states to use purple
  - Update glow effects to use purple
  - Verify consistency across all states
  - _Requirements: 9.2, 9.3, 9.4_

- [x] 12.3 Add focus indicators
  - Add visible focus rings to all interactive elements
  - Use purple color for focus indicators
  - Ensure 2px outline with 2px offset
  - Test keyboard navigation
  - _Requirements: 10.2, 10.4_

---

## Phase 5: Testing and Accessibility

### 13. Accessibility Testing

- [x] 13.1 Test keyboard navigation
  - Test Tab navigation through all items
  - Test Arrow key navigation
  - Test Enter/Space activation
  - Test Escape to close on mobile
  - Test Ctrl/Cmd + B shortcut
  - _Requirements: 10.1, 10.2_

- [x] 13.2 Add ARIA labels and roles
  - Add aria-label to sidebar container
  - Add aria-current to active items
  - Add aria-expanded to collapsible groups
  - Add aria-hidden to decorative elements
  - Add role="navigation" to sidebar
  - _Requirements: 10.2, 10.3, 10.4_

- [ ] 13.3 Test with screen reader
  - Test with NVDA or VoiceOver
  - Verify all items are announced
  - Verify state changes are announced
  - Verify tooltips are read correctly
  - _Requirements: 10.3, 10.5_

### 14. Performance Testing

- [ ] 14.1 Test animation performance
  - Open Chrome DevTools Performance tab
  - Record collapse/expand animations
  - Verify 60fps during transitions
  - Check for layout thrashing
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 14.2 Test on mobile devices
  - Test on iOS Safari
  - Test on Android Chrome
  - Verify touch interactions
  - Verify overlay behavior
  - Test performance
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 14.3 Optimize re-renders
  - Memoize all menu items
  - Use useCallback for event handlers
  - Verify no unnecessary re-renders with React DevTools
  - _Requirements: 11.1, 11.4_

### 15. Cross-Browser Testing

- [ ] 15.1 Test on Chrome
  - Verify all features work
  - Test animations
  - Test keyboard shortcuts
  - _Requirements: All_

- [ ] 15.2 Test on Firefox
  - Verify backdrop-filter support
  - Test animations
  - Test keyboard shortcuts
  - _Requirements: All_

- [ ] 15.3 Test on Safari
  - Verify webkit-backdrop-filter
  - Test on macOS and iOS
  - Test keyboard shortcuts (Cmd + B)
  - _Requirements: All_

---

## Phase 6: Cleanup and Documentation

### 16. Remove Old Sidebar

- [ ] 16.1 Remove old sidebar components
  - Delete old `src/components/layout/Sidebar.tsx`
  - Delete old `src/components/layout/Sidebar.css`
  - Remove old sidebar from imports
  - _Requirements: 12.1_

- [ ] 16.2 Update all sidebar references
  - Search for old Sidebar imports
  - Replace with new sidebar components
  - Update any hardcoded widths
  - Test all pages
  - _Requirements: 12.1_

### 17. Final Polish

- [ ] 17.1 Create sidebar index file
  - Create `src/components/sidebar/index.ts`
  - Export all sidebar components
  - Export useSidebar hook
  - Export types and interfaces
  - _Requirements: 12.5_

- [ ] 17.2 Add reduced motion support
  - Check prefers-reduced-motion
  - Disable animations if preferred
  - Use instant transitions instead
  - Test with browser settings
  - _Requirements: 8.4_

- [ ] 17.3 Final visual polish
  - Verify all spacing is consistent
  - Verify all colors match theme
  - Verify all animations are smooth
  - Test all interactive states
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 17.4 Create component documentation
  - Document all component props
  - Add usage examples
  - Document useSidebar hook
  - Create README for sidebar system
  - _Requirements: 12.3, 12.4, 12.5_

---

## Summary

**Total Tasks**: 17 major tasks with 40+ sub-tasks
**Estimated Time**: 4-6 hours

**Phase Breakdown:**
- Phase 1: Foundation (1 hour)
- Phase 2: Navigation Components (1.5 hours)
- Phase 3: Interactive Features (1 hour)
- Phase 4: Integration (1 hour)
- Phase 5: Testing (1 hour)
- Phase 6: Cleanup (0.5 hours)

**Key Deliverables:**
- Composable sidebar system
- Collapsible to icon mode (60px)
- Keyboard shortcut support (Ctrl/Cmd + B)
- Mobile responsive with overlay
- Tooltips in collapsed mode
- Purple accent theme
- Smooth 300ms animations
- Full accessibility support

**Next Steps:**
Open this tasks.md file and click "Start task" to begin implementation.
