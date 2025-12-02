# Implementation Plan

This implementation plan is organized in logical development order, from foundation to features to polish.

## Phase 1: Foundation and Infrastructure (Days 1-2)

- [-] 1. Project setup and directory structure

  - Create all necessary directories and base files
  - Set up TypeScript configuration
  - Install required dependencies
  - _Requirements: 1.1_

- [x] 1.1 Create directory structure




  - Create src/components/Sidebar directory
  - Create src/components/Sidebar/__tests__ directory for tests
  - Create src/types/sidebar.ts for type definitions
  - Create src/config/sidebarConfig.ts for navigation configuration
  - Create src/config/animations.ts for animation constants
  - Create src/hooks directory for custom hooks
  - Create src/services/api/sidebar.ts for API functions
  - Create src/store/useSidebarStore.ts for state management
  - Create index.ts barrel export in Sidebar directory
  - _Requirements: 1.1_

- [-] 1.2 Install dependencies



  - Verify framer-motion is installed (npm install framer-motion)
  - Verify @tanstack/react-query is installed
  - Verify zustand is installed
  - Verify axios is installed
  - Verify @headlessui/react is installed for accessible components
  - Install @heroicons/react for icons if not present
  - _Requirements: 1.1_


- [x] 2. TypeScript types and interfaces

  - Define all TypeScript interfaces for components
  - Create type definitions for configuration
  - Export all types for reuse
  - _Requirements: 1.1, 19.1_

- [x] 2.1 Define core component interfaces

  - Create src/types/sidebar.ts
  - Define SidebarProps: `{ isOpen?: boolean; onClose?: () => void; className?: string; variant?: 'desktop' | 'mobile' }`
  - Define SidebarItemProps: `{ icon: React.ReactNode; label: string; to?: string; onClick?: () => void; badge?: number | string; active?: boolean; contextMenu?: ContextMenuItem[] }`
  - Define SidebarSectionProps: `{ title: string; children: React.ReactNode; collapsible?: boolean; defaultExpanded?: boolean; icon?: React.ReactNode }`
  - Define SidebarBadgeProps: `{ count: number | string; variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger'; pulse?: boolean }`
  - Define UserProfileWidgetProps: `{ user: UserProfile; menuItems?: ProfileMenuItem[] }`
  - Add JSDoc comments to all interfaces
  - _Requirements: 1.1, 19.1_

- [x] 2.2 Define configuration types

  - Define NavigationConfig: `{ sections: SidebarSectionConfig[] }`
  - Define SidebarSectionConfig: `{ id: string; title: string; collapsible: boolean; defaultExpanded: boolean; items: SidebarItemConfig[] }`
  - Define SidebarItemConfig: `{ id: string; label: string; icon: string; to: string; badge?: BadgeConfig; contextMenu?: ContextMenuConfig[] }`
  - Define BadgeConfig: `{ source: 'collection' | 'category' | 'static'; key?: string; value?: number | string }`
  - Define ContextMenuConfig: `{ label: string; icon?: string; action: string; variant?: 'default' | 'danger' }`
  - Define ContextMenuItem: `{ label: string; icon?: React.ReactNode; onClick: () => void; variant?: 'default' | 'danger' }`
  - Define ProfileMenuItem: `{ label: string; icon?: React.ReactNode; onClick: () => void; divider?: boolean }`
  - Define UserProfile: `{ id: string; name: string; email: string; avatar?: string }`
  - Export all types
  - _Requirements: 1.1, 19.1_

- [x] 3. Animation configuration


  - Create centralized animation constants
  - Define reusable animation variants
  - Export timing and easing functions
  - _Requirements: 20.1, 20.2_

- [x] 3.1 Create animation constants file


  - Create src/config/animations.ts
  - Export DURATION object: `{ FAST: 0.15, NORMAL: 0.2, SLOW: 0.3, SLOWER: 0.5 }`
  - Export EASE object: `{ IN_OUT: [0.4, 0, 0.2, 1], OUT: [0, 0, 0.2, 1], IN: [0.4, 0, 1, 1] }`
  - Export SPRING object: `{ SMOOTH: { stiffness: 300, damping: 30 }, BOUNCY: { stiffness: 400, damping: 25 }, GENTLE: { stiffness: 200, damping: 20 } }`
  - Add JSDoc comments explaining each configuration
  - _Requirements: 20.1, 20.2_

- [x] 3.2 Define reusable animation variants

  - Export VARIANTS object with common animations
  - Define fadeIn: `{ hidden: { opacity: 0 }, visible: { opacity: 1 } }`
  - Define slideIn: `{ hidden: { x: -20, opacity: 0 }, visible: { x: 0, opacity: 1 } }`
  - Define scaleIn: `{ hidden: { scale: 0.95, opacity: 0 }, visible: { scale: 1, opacity: 1 } }`
  - Define sidebarVariants: `{ open: { x: 0, transition: SPRING.SMOOTH }, closed: { x: -260, transition: SPRING.SMOOTH } }`
  - Define backdropVariants: `{ open: { opacity: 0.5 }, closed: { opacity: 0 } }`
  - Define sectionContentVariants for expand/collapse
  - Define accentBarVariants for hover effects
  - Define badgePulseVariants for count updates
  - _Requirements: 20.1, 20.2, 20.3_


- [x] 4. Zustand store for state management


  - Create sidebar state store
  - Implement state actions
  - Add persistence middleware
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [x] 4.1 Create Zustand store structure


  - Create src/store/useSidebarStore.ts
  - Import create from zustand and persist middleware
  - Define SidebarState interface with all state properties
  - State properties: `isOpen: boolean, isMobile: boolean, expandedSections: Record<string, boolean>, collectionCounts: Record<string, number>, categoryCounts: Record<string, number>`
  - Initialize default state: isOpen true for desktop, expandedSections empty object, counts empty objects
  - _Requirements: 17.1, 17.2_

- [x] 4.2 Implement state actions

  - Create toggleSidebar action: `() => set((state) => ({ isOpen: !state.isOpen }))`
  - Create setSidebarOpen action: `(open: boolean) => set({ isOpen: open })`
  - Create toggleSection action: `(sectionId: string) => set((state) => ({ expandedSections: { ...state.expandedSections, [sectionId]: !state.expandedSections[sectionId] } }))`
  - Create setExpandedSection action: `(sectionId: string, expanded: boolean) => set((state) => ({ expandedSections: { ...state.expandedSections, [sectionId]: expanded } }))`
  - Create updateCollectionCounts action: `(counts: Record<string, number>) => set({ collectionCounts: counts })`
  - Create updateCategoryCounts action: `(counts: Record<string, number>) => set({ categoryCounts: counts })`
  - Create setIsMobile action: `(isMobile: boolean) => set({ isMobile })`
  - _Requirements: 17.3, 17.4_

- [x] 4.3 Add persistence middleware

  - Wrap store with persist middleware
  - Set storage name as 'neo-alexandria-sidebar'
  - Persist expandedSections to localStorage
  - Persist isOpen for mobile only (conditional persistence)
  - Exclude collectionCounts and categoryCounts from persistence (fetch fresh)
  - Use partialize option to select which state to persist
  - Add version number for migration support
  - _Requirements: 17.5_

- [x] 5. Navigation configuration

  - Define sidebar navigation structure
  - Configure all navigation items
  - Set up badge configurations
  - Define context menus
  - _Requirements: 3.1, 4.1, 5.1, 8.1_

- [x] 5.1 Create navigation configuration file

  - Create src/config/sidebarConfig.ts
  - Import NavigationConfig type
  - Create navigationConfig object with sections array
  - Export navigationConfig as default
  - _Requirements: 3.1, 4.1, 5.1, 8.1_

- [x] 5.2 Define Main navigation section

  - Create Main section with id 'main', title 'Main', collapsible false
  - Add Dashboard item: `{ id: 'dashboard', label: 'Dashboard', icon: 'fas fa-home', to: '/' }`
  - Add Library item: `{ id: 'library', label: 'Library', icon: 'fas fa-book', to: '/library' }`
  - Add Search item: `{ id: 'search', label: 'Search', icon: 'fas fa-search', to: '/search' }`
  - Add Knowledge Graph item: `{ id: 'knowledge-graph', label: 'Knowledge Graph', icon: 'fas fa-project-diagram', to: '/knowledge-graph' }`
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 5.3 Define Collections navigation section
  - Create Collections section with id 'collections', title 'Collections', collapsible true, defaultExpanded true
  - Add Favorites item with badge: `{ id: 'favorites', label: 'Favorites', icon: 'fas fa-star', to: '/collections/favorites', badge: { source: 'collection', key: 'favorites' } }`
  - Add Recent item with badge: `{ id: 'recent', label: 'Recent', icon: 'fas fa-clock', to: '/collections/recent', badge: { source: 'collection', key: 'recent' } }`
  - Add Read Later item with badge: `{ id: 'read-later', label: 'Read Later', icon: 'fas fa-bookmark', to: '/collections/read-later', badge: { source: 'collection', key: 'read_later' } }`
  - Add Shared item with badge: `{ id: 'shared', label: 'Shared', icon: 'fas fa-share-alt', to: '/collections/shared', badge: { source: 'collection', key: 'shared' } }`
  - Add context menu to each item: Rename, Delete, Share actions
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_


- [x] 5.4 Define Categories navigation section
  - Create Categories section with id 'categories', title 'Categories', collapsible true, defaultExpanded true
  - Add Science item: `{ id: 'science', label: 'Science', icon: 'fas fa-microscope', to: '/categories/science', badge: { source: 'category', key: 'science' } }`
  - Add Technology item: `{ id: 'technology', label: 'Technology', icon: 'fas fa-laptop-code', to: '/categories/technology', badge: { source: 'category', key: 'technology' } }`
  - Add Art & Design item: `{ id: 'art-design', label: 'Art & Design', icon: 'fas fa-paint-brush', to: '/categories/art_design', badge: { source: 'category', key: 'art_design' } }`
  - Add Business item: `{ id: 'business', label: 'Business', icon: 'fas fa-chart-line', to: '/categories/business', badge: { source: 'category', key: 'business' } }`

  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5.5 Define Settings navigation section

  - Create Settings section with id 'settings', title 'Settings', collapsible false
  - Add Settings item: `{ id: 'settings', label: 'Settings', icon: 'fas fa-cog', to: '/settings' }`
  - Position this section at the bottom with visual separator
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


## Phase 2: API Integration and Data Layer (Days 3-4)

- [x] 6. API service layer


  - Create API functions for sidebar data
  - Implement error handling
  - Add TypeScript types for responses
  - _Requirements: 14.1, 14.2, 14.3_


- [x] 6.1 Create sidebar API service

  - Create src/services/api/sidebar.ts
  - Import axios client from existing API configuration
  - Define CollectionCountsResponse type: `{ favorites: number; recent: number; read_later: number; shared: number }`
  - Define CategoryCountsResponse type: `{ science: number; technology: number; art_design: number; business: number }`
  - Implement getCollectionCounts function with userId parameter
  - API endpoint: `GET /collections/counts?user_id={userId}`
  - Implement getCategoryCounts function
  - API endpoint: `GET /resources/category-counts`
  - Add try-catch error handling to both functions
  - Set request timeout to 10 seconds
  - Return typed responses
  - Export all functions
  - _Requirements: 14.1, 14.2_


- [ ] 6.2 Create user profile API functions
  - Add getUserProfile function to API service
  - API endpoint: `GET /users/me`
  - Define UserProfileResponse type matching backend
  - Add error handling for unauthorized (401) responses
  - Return user profile data
  - _Requirements: 14.3_

- [x] 7. Custom React hooks for data fetching



  - Create hooks using TanStack Query
  - Configure caching and refetch strategies
  - Handle loading and error states
  - _Requirements: 14.1, 14.2, 14.3, 14.4_


- [x] 7.1 Create useSidebarData hook

  - Create src/hooks/useSidebarData.ts
  - Import useQuery from @tanstack/react-query
  - Import API functions from sidebar service
  - Create query for collection counts with key ['sidebar', 'collections', userId]
  - Configure refetchInterval: 30000 (30 seconds)
  - Configure staleTime: 300000 (5 minutes)
  - Configure retry: 2 attempts with exponential backoff
  - Create query for category counts with key ['sidebar', 'categories']
  - Configure refetchInterval: 60000 (60 seconds)
  - Configure staleTime: 600000 (10 minutes)
  - Return object: `{ collectionCounts, categoryCounts, isLoading, error, refetch }`
  - Enable queries only when user is authenticated
  - _Requirements: 14.1, 14.2, 14.3_

- [x] 7.2 Create useUserProfile hook


  - Create src/hooks/useUserProfile.ts
  - Implement useQuery for user profile
  - Query key: ['user', 'profile']
  - Configure staleTime: 600000 (10 minutes)
  - Configure cacheTime: 1800000 (30 minutes)
  - Handle 401 errors by redirecting to login
  - Return user data, loading state, error state
  - _Requirements: 14.3_

- [x] 7.3 Integrate data with Zustand store


  - Create useEffect in Sidebar component
  - Watch collectionCounts from useSidebarData
  - Call updateCollectionCounts when data changes
  - Watch categoryCounts from useSidebarData
  - Call updateCategoryCounts when data changes
  - Implement optimistic updates for user actions
  - Store previous values for rollback on error
  - _Requirements: 14.5, 17.4_

- [x] 8. Error handling and loading states


  - Implement error boundaries
  - Create loading skeletons
  - Add retry mechanisms
  - _Requirements: 14.4, 15.1_


- [x] 8.1 Create error handling utilities

  - Create src/utils/errorHandling.ts
  - Implement handleApiError function for axios errors
  - Extract error messages from response
  - Log errors with context to console
  - Return user-friendly error messages
  - _Requirements: 14.4_


- [x] 8.2 Implement loading skeletons

  - Create SkeletonBadge component
  - Use shimmer animation with linear gradient
  - Animate background position continuously
  - Match dimensions to actual badge
  - Display during initial data fetch
  - _Requirements: 15.1_


- [ ] 8.3 Add error indicators
  - Show red dot on sidebar header when API errors occur
  - Display subtle error message in tooltip
  - Add retry button in error state
  - Show toast notification for critical errors
  - Gracefully degrade to cached data
  - Store last successful response in localStorage
  - _Requirements: 14.4_


## Phase 3: Core UI Components (Days 5-8)

- [-] 9. Sidebar container component


  - Build main Sidebar component
  - Implement animations
  - Add responsive behavior
  - Style component
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 9.1 Create Sidebar component structure

  - Create src/components/Sidebar/Sidebar.tsx
  - Import motion, AnimatePresence from framer-motion
  - Import useSidebarStore hook
  - Import animation variants from config
  - Define component with SidebarProps interface
  - Create motion.aside element for sidebar
  - Set fixed positioning: left-0 top-0
  - Set dimensions: w-64 (260px) h-screen
  - Add scrollable content area with overflow-y-auto
  - Add data-testid="sidebar" for testing
  - _Requirements: 1.1, 1.2, 1.3_


- [ ] 9.2 Implement Framer Motion animations
  - Apply sidebarVariants to motion.aside
  - Set initial="closed" for first render
  - Animate based on isOpen prop: animate={isOpen ? 'open' : 'closed'}
  - Use spring physics from animation config
  - Ensure smooth 60fps animation
  - _Requirements: 20.1, 20.2_


- [ ] 9.3 Add mobile drawer with backdrop
  - Wrap sidebar in fragment
  - Add AnimatePresence for backdrop
  - Create motion.div for backdrop overlay
  - Position backdrop: fixed inset-0
  - Apply background: bg-black/50
  - Set z-index: 40 for backdrop, 50 for sidebar
  - Apply backdropVariants for fade animation
  - Add onClick to backdrop calling onClose
  - Render backdrop only when variant='mobile' and isOpen=true
  - _Requirements: 1.5, 11.1, 11.2, 11.3_


- [ ] 9.4 Implement responsive behavior
  - Create src/hooks/useMediaQuery.ts hook
  - Detect viewport width < 768px
  - Use window.matchMedia for efficient detection
  - Add event listener for viewport changes
  - Debounce resize handler (150ms)
  - Update Zustand store isMobile state
  - Conditionally render desktop or mobile variant
  - _Requirements: 11.1, 11.2_

- [x] 9.5 Style Sidebar component

  - Apply background gradient: bg-gradient-to-b from-charcoal-grey-700 to-charcoal-grey-800
  - Add border: border-r border-white/10
  - Add shadow: shadow-2xl
  - Apply transitions: transition-all duration-300
  - Set proper z-index layering
  - Add custom scrollbar styling
  - _Requirements: 1.1, 16.1_


- [x] 10. SidebarBadge component

  - Create badge component
  - Implement variants
  - Add pulse animation
  - Handle large numbers
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 10.1 Build SidebarBadge component

  - Create src/components/Sidebar/SidebarBadge.tsx
  - Import motion, useAnimation from framer-motion
  - Define component with SidebarBadgeProps
  - Create motion.span element
  - Position absolutely: absolute -top-1 -right-1
  - Create circular shape: rounded-full w-[18px] h-[18px]
  - Center content: flex items-center justify-center
  - Set font: text-[0.7rem] font-semibold
  - _Requirements: 12.1, 12.2, 12.3_


- [ ] 10.2 Implement badge variants
  - Create variant styles object
  - Default variant: bg-cyan-500 text-white
  - Primary variant: bg-blue-500 text-white
  - Success variant: bg-green-500 text-white
  - Warning variant: bg-amber-500 text-white
  - Danger variant: bg-red-500 text-white
  - Apply variant className based on prop
  - _Requirements: 12.1, 12.2_


- [ ] 10.3 Add pulse animation on count change
  - Import badgePulseVariants from animation config
  - Use useAnimation hook for programmatic control
  - Use useRef to store previous count
  - Use useEffect to detect count changes
  - Trigger pulse animation when count increases
  - Animation: scale [1, 1.15, 1] with glow effect
  - Duration: 300ms with easeInOut

  - _Requirements: 12.5, 20.3_

- [ ] 10.4 Handle large numbers
  - Check if count > 99
  - Display "99+" for counts over 99
  - Adjust font size for longer strings
  - Ensure badge remains circular

  - Handle string values (e.g., "new")
  - _Requirements: 12.4_

- [ ] 10.5 Style and export SidebarBadge
  - Add subtle box shadow for depth
  - Ensure proper contrast for accessibility
  - Export component from index.ts
  - Add prop-types or TypeScript validation

  - _Requirements: 12.1, 12.3_


- [ ] 11. SidebarItem component
  - Create navigation item component
  - Implement active state
  - Add hover effects
  - Integrate badge
  - Add context menu support
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 11.1 Build SidebarItem component structure

  - Create src/components/Sidebar/SidebarItem.tsx
  - Import motion from framer-motion
  - Import Link from react-router-dom
  - Import useLocation hook
  - Define component with SidebarItemProps
  - Create motion.div wrapper for animations
  - Add relative positioning for accent bar
  - _Requirements: 3.1, 3.2_


- [ ] 11.2 Implement active state detection
  - Use useLocation to get current pathname
  - Compare pathname with item's 'to' prop
  - Support nested route matching (startsWith)
  - Set isActive boolean based on match
  - Apply active styles when isActive is true
  - _Requirements: 9.1, 9.2, 9.3, 9.4_


- [ ] 11.3 Create accent bar animation
  - Create motion.div for accent bar
  - Position absolutely: absolute left-0 top-0 h-full w-[3px]
  - Apply background: bg-accent-blue-500
  - Import accentBarVariants from animation config
  - Animate based on hover and active states
  - Rest state: x: -3, opacity: 0
  - Hover state: x: 0, opacity: 1
  - Active state: x: 0, opacity: 1 (no transition)

  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 11.4 Add hover micro-interactions
  - Apply itemVariants to motion.div wrapper
  - Define rest state: x: 0, backgroundColor: transparent
  - Define hover state: x: 2, backgroundColor: rgba(74, 144, 226, 0.1)
  - Use whileHover="hover" prop
  - Add whileTap for click feedback: scale: 0.98
  - Animate icon scale on hover: 1 to 1.1
  - Animate label slide on hover: x: 0 to 2

  - Duration: 150ms for all hover effects
  - _Requirements: 10.4, 10.5_

- [ ] 11.5 Integrate badge display
  - Add conditional rendering for badge prop
  - Position badge in top-right corner
  - Import and use SidebarBadge component

  - Pass count value to badge
  - Handle badge visibility (hide if count is 0)
  - _Requirements: 12.1, 12.2, 12.3_

- [ ] 11.6 Implement navigation
  - Wrap content in Link component if 'to' prop exists
  - Use onClick handler if provided instead of Link
  - Prevent default link behavior if onClick exists
  - Close mobile drawer on navigation

  - Update active state immediately
  - _Requirements: 3.3, 3.4, 3.5_

- [ ] 11.7 Add context menu support
  - Add onContextMenu handler for right-click
  - Show three-dot menu icon on hover
  - Position menu icon in top-right

  - Pass contextMenu prop to ContextMenu component
  - Handle menu open/close state
  - _Requirements: 19.1, 19.2_

- [ ] 11.8 Style SidebarItem
  - Apply padding: px-4 py-3
  - Display flex with items-center
  - Add icon margin: mr-3
  - Set text color: text-charcoal-grey-50
  - Active state: text-accent-blue-400 bg-accent-blue-500/15
  - Add smooth transitions: transition-all duration-150
  - Export component
  - _Requirements: 3.5, 10.1_

- [-] 12. SidebarSection component

  - Create section container
  - Implement collapsible functionality
  - Add expand/collapse animation
  - Persist state
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 12.1 Build SidebarSection component

  - Create src/components/Sidebar/SidebarSection.tsx
  - Import motion, AnimatePresence from framer-motion
  - Import useSidebarStore hook
  - Define component with SidebarSectionProps
  - Create section container div
  - Add section header button
  - Create collapsible content area
  - _Requirements: 6.1_


- [ ] 12.2 Implement section header
  - Create button element for header
  - Display section title in uppercase
  - Add chevron icon (conditional on collapsible prop)
  - Apply header styling: text-xs text-charcoal-grey-400 uppercase tracking-wider
  - Add padding: px-4 py-2
  - Make clickable if collapsible
  - _Requirements: 6.1, 6.2_


- [ ] 12.3 Add chevron rotation animation
  - Wrap chevron in motion.span
  - Define chevronVariants: expanded {rotate: 90}, collapsed {rotate: 0}
  - Animate based on isExpanded state
  - Transition duration: 200ms
  - Use smooth easing

  - _Requirements: 6.2, 6.5_

- [ ] 12.4 Implement expand/collapse animation
  - Wrap content in motion.div
  - Import sectionContentVariants from animation config
  - Expanded state: height: auto, opacity: 1
  - Collapsed state: height: 0, opacity: 0
  - Set overflow: hidden to prevent content overflow
  - Transition duration: 200ms with custom easing

  - Use AnimatePresence for smooth exit
  - _Requirements: 6.2, 6.3, 6.5_

- [ ] 12.5 Connect to Zustand store
  - Get expandedSections from useSidebarStore
  - Get toggleSection action from store
  - Read isExpanded state from store using section id

  - Call toggleSection on header click
  - Use section id as key in expandedSections object
  - _Requirements: 6.3, 6.4, 17.3_

- [ ] 12.6 Add state persistence
  - Persistence handled by Zustand middleware
  - Verify expandedSections persists to localStorage
  - Test state restoration on page reload
  - Handle multiple sections independently
  - _Requirements: 6.4, 17.5_

- [x] 12.7 Style and export SidebarSection

  - Add spacing between sections: mb-6
  - Style header with hover effect
  - Add border-top for Settings section
  - Export component from index.ts
  - _Requirements: 6.1_


- [x] 13. SidebarHeader component


  - Create header with logo
  - Add navigation on click
  - Implement optional search
  - Style component
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 13.1 Build SidebarHeader component

  - Create src/components/Sidebar/SidebarHeader.tsx
  - Import useNavigate from react-router-dom
  - Define component with SidebarHeaderProps
  - Create header container div
  - Add fixed positioning to prevent scrolling
  - _Requirements: 2.1_


- [ ] 13.2 Create logo section
  - Create clickable logo container
  - Add gradient background: bg-gradient-to-br from-blue-500 to-cyan-400
  - Create circular icon container: w-10 h-10 rounded-full
  - Add brain icon: fas fa-brain
  - Display app name "Neo Alexandria" next to icon
  - Add onClick handler to navigate to home (/)
  - _Requirements: 2.2, 2.3, 2.4_


- [ ] 13.3 Add hover effect to logo
  - Use motion.div for logo container
  - Add whileHover animation: scale: 1.05
  - Add whileTap animation: scale: 0.95
  - Transition duration: 200ms
  - Add cursor-pointer class

  - _Requirements: 2.5_

- [ ] 13.4 Implement optional search input
  - Add showSearch prop to component
  - Conditionally render search input
  - Create input with search icon
  - Style with rounded corners: rounded-full
  - Apply subtle background: bg-white/10
  - Add border: border border-white/20
  - Position below logo section
  - _Requirements: 18.1_

- [x] 13.5 Style and export SidebarHeader

  - Apply padding: p-4
  - Add bottom border: border-b border-white/10
  - Set background to match sidebar

  - Export component from index.ts
  - _Requirements: 2.1, 2.5_

- [ ] 14. UserProfileWidget component
  - Create user profile display
  - Add dropdown menu
  - Implement menu actions
  - Style component
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 14.1 Build UserProfileWidget component

  - Create src/components/Sidebar/UserProfileWidget.tsx
  - Import Menu from @headlessui/react
  - Import useUserProfile hook
  - Define component with UserProfileWidgetProps
  - Create container div with border-top separator
  - Position at bottom of sidebar
  - _Requirements: 7.1, 7.2_

- [x] 14.2 Create avatar display

  - Create circular avatar container: w-10 h-10 rounded-full
  - Display user avatar image if available
  - Show default placeholder if no avatar (user initials)
  - Add overflow-hidden for circular crop
  - Apply border: border-2 border-white/20
  - _Requirements: 7.4_

- [x] 14.3 Display user information

  - Show user name with font-medium
  - Show user email with text-sm text-charcoal-grey-400
  - Truncate long text with ellipsis
  - Stack vertically next to avatar
  - _Requirements: 7.2, 7.3_

- [x] 14.4 Implement dropdown menu

  - Use Headless UI Menu component
  - Create Menu.Button wrapping widget content
  - Create Menu.Items for dropdown
  - Position dropdown above widget: bottom-full mb-2
  - Add default menu items: Profile, Settings, Sign Out
  - Support custom menu items via props
  - Add dividers between sections
  - _Requirements: 7.3, 7.5_

- [x] 14.5 Add menu animations

  - Import dropdownVariants from animation config
  - Wrap Menu.Items in motion.div
  - Closed state: opacity: 0, scale: 0.95, y: 10
  - Open state: opacity: 1, scale: 1, y: 0
  - Use spring transition
  - Stagger menu items with 30ms delay
  - _Requirements: 20.2_

- [x] 14.6 Implement menu item actions

  - Add onClick handlers for each menu item
  - Profile: navigate to /profile
  - Settings: navigate to /settings
  - Sign Out: call logout function
  - Support custom actions via props
  - Close menu after selection
  - _Requirements: 7.5_

- [x] 14.7 Add keyboard navigation

  - Support Arrow Up/Down for navigation
  - Support Enter to select
  - Support Escape to close
  - Implement focus trap
  - Add ARIA attributes
  - _Requirements: 13.2, 13.3_

- [x] 14.8 Style and export UserProfileWidget

  - Apply padding: p-4
  - Add hover effect: bg-white/5
  - Style dropdown with shadow and border
  - Add transition: transition-colors duration-200
  - Export component from index.ts
  - _Requirements: 7.1, 7.2_


## Phase 4: Advanced Features (Days 9-11)

- [-] 15. Assemble complete Sidebar with all sections

  - Integrate all components
  - Wire up navigation
  - Connect data sources
  - Test complete flow
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 8.1, 8.2, 8.3, 8.4, 8.5_


- [ ] 15.1 Assemble Sidebar component
  - Import all child components (SidebarHeader, SidebarSection, SidebarItem, UserProfileWidget)
  - Import navigationConfig
  - Import useSidebarData and useUserProfile hooks
  - Render SidebarHeader at top
  - Map through navigationConfig sections
  - Render SidebarSection for each section
  - Map through section items
  - Render SidebarItem for each item
  - Render UserProfileWidget at bottom
  - _Requirements: 1.1, 1.2, 1.3, 1.4_


- [ ] 15.2 Connect badges to data
  - Get collectionCounts from Zustand store
  - Get categoryCounts from Zustand store
  - Map badge source to appropriate count
  - Pass count to SidebarItem badge prop
  - Handle missing or zero counts

  - _Requirements: 4.3, 4.4, 4.5, 5.3, 5.4, 12.1, 12.2_

- [ ] 15.3 Wire up navigation items
  - Ensure all items use correct routes
  - Test navigation between pages
  - Verify active state updates
  - Test mobile drawer closes on navigation

  - Verify browser back/forward works
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1, 9.2, 9.3_

- [ ] 15.4 Test data fetching integration
  - Verify collection counts update every 30 seconds
  - Verify category counts update every 60 seconds
  - Test error handling when API fails
  - Test loading states display correctly
  - Verify optimistic updates work
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [-] 16. Context menu functionality

  - Create ContextMenu component
  - Implement positioning
  - Add menu actions
  - Handle keyboard navigation
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

- [x] 16.1 Build ContextMenu component

  - Create src/components/Sidebar/ContextMenu.tsx
  - Import Menu from @headlessui/react
  - Import motion from framer-motion
  - Define component with ContextMenuProps
  - Accept items array and position coordinates
  - _Requirements: 19.1_


- [ ] 16.2 Implement positioning logic
  - Calculate menu position based on click coordinates
  - Check if menu would overflow viewport
  - Adjust position to stay within bounds
  - Position near clicked item
  - Use absolute positioning
  - _Requirements: 19.2_


- [ ] 16.3 Create menu animations
  - Import menuVariants from animation config
  - Wrap menu in AnimatePresence
  - Closed state: opacity: 0, scale: 0.95, y: -10
  - Open state: opacity: 1, scale: 1, y: 0
  - Stagger menu items with 30ms delay
  - Duration: 150ms

  - _Requirements: 20.2_

- [ ] 16.4 Implement menu actions
  - Add Rename action with inline edit
  - Add Delete action with confirmation dialog
  - Add Share action with share modal
  - Execute action callbacks on selection

  - Close menu after action
  - _Requirements: 19.1, 19.3, 19.4_

- [ ] 16.5 Add keyboard navigation
  - Support Arrow Up/Down for navigation
  - Support Enter to select action
  - Support Escape to close menu
  - Implement focus trap
  - Add ARIA attributes
  - _Requirements: 19.3, 13.2, 13.3_

- [x] 16.6 Style ContextMenu

  - Apply shadow: shadow-lg
  - Add border: border border-white/10
  - Set background: bg-charcoal-grey-700
  - Style menu items with hover: bg-white/10
  - Use danger color for Delete: text-red-400
  - Add padding and spacing
  - Export component
  - _Requirements: 19.1, 19.2_

- [ ] 17. Search functionality
  - Add search to SidebarHeader
  - Implement filtering

  - Highlight matches
  - Handle empty states
  - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

- [ ] 17.1 Implement search input
  - Add controlled input to SidebarHeader
  - Add search icon (fas fa-search)

  - Implement debounced onChange (300ms)
  - Store search query in local state
  - Style with rounded-full and subtle background
  - _Requirements: 18.1_

- [ ] 17.2 Create filtering logic
  - Filter navigationConfig items based on query

  - Match against item labels (case-insensitive)
  - Match against section names
  - Include keyword matching
  - Return filtered sections array
  - _Requirements: 18.2, 18.3_


- [ ] 17.3 Implement result highlighting
  - Highlight matching text in labels
  - Use accent blue color for highlights
  - Preserve original text casing
  - Use mark element or span with styling
  - _Requirements: 18.4_


- [ ] 17.4 Handle empty states
  - Show all items when search is empty
  - Display "No results found" when no matches
  - Provide clear button to reset search
  - Show search icon in empty state
  - _Requirements: 18.5_

- [ ] 17.5 Add search animations
  - Animate filtered items with stagger
  - Fade out removed items
  - Fade in new matches
  - Use AnimatePresence for smooth transitions
  - _Requirements: 20.4_



- [ ] 18. Mobile optimizations
  - Implement swipe gestures
  - Optimize touch targets
  - Test on devices
  - Improve performance
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_


- [ ] 18.1 Implement swipe-to-close gesture
  - Use Framer Motion drag functionality
  - Add drag="x" to sidebar motion.aside
  - Set dragConstraints: { left: -260, right: 0 }
  - Detect swipe velocity and direction
  - Close drawer on left swipe with velocity > 500
  - Add visual feedback during drag
  - Snap back if velocity is insufficient
  - _Requirements: 11.5_

- [ ] 18.2 Optimize touch targets
  - Increase padding on mobile: py-3.5 (14px)

  - Ensure minimum 44x44px touch targets
  - Add touch-action: manipulation
  - Increase icon sizes on mobile
  - Add more spacing between items
  - _Requirements: 11.2, 11.5_

- [x] 18.3 Disable hover effects on touch

  - Detect touch device using matchMedia
  - Conditionally disable hover animations
  - Use @media (hover: hover) in CSS
  - Prevent sticky hover states
  - Use active states instead of hover on touch
  - _Requirements: 11.2, 11.5_

- [x] 18.4 Test on mobile devices

  - Test on iOS Safari (iPhone)
  - Test on Android Chrome
  - Test on various screen sizes (320px, 375px, 414px)
  - Test on tablets (768px, 1024px)
  - Verify touch interactions work smoothly
  - Test swipe gesture responsiveness
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 18.5 Optimize mobile performance
  - Reduce animation complexity on mobile
  - Use will-change sparingly
  - Lazy load non-critical components
  - Minimize re-renders during drawer transitions
  - Test on low-end devices
  - Profile with Chrome DevTools
  - _Requirements: 15.1, 15.2_

## Phase 5: Animation Polish (Days 12-13)


- [x] 19. Refine all animations


  - Polish sidebar animations
  - Add stagger effects
  - Implement scroll effects
  - Respect reduced motion
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

- [x] 19.1 Polish sidebar open/close animation

  - Verify spring physics feel natural
  - Test animation on different devices
  - Ensure 60fps performance
  - Adjust stiffness/damping if needed
  - Test backdrop fade timing
  - _Requirements: 20.1, 20.2_


- [ ] 19.2 Refine section expand/collapse
  - Verify height animation is smooth
  - Test with varying content heights
  - Ensure no content overflow during animation
  - Adjust timing if needed
  - Test chevron rotation sync
  - _Requirements: 20.2_


- [ ] 19.3 Perfect accent bar animation
  - Verify slide-in timing (150ms)
  - Test on hover and active states
  - Ensure GPU acceleration is used
  - Check for any jank or stuttering
  - Test on lower-end devices

  - _Requirements: 20.2_

- [ ] 19.4 Implement stagger animations
  - Add stagger to initial item load
  - Use staggerChildren: 0.05
  - Add delayChildren: 0.1
  - Apply to filtered search results

  - Test with different item counts
  - _Requirements: 20.4_

- [ ] 19.5 Add scroll-triggered animations
  - Use useInView hook from Framer Motion
  - Fade in items as they scroll into view
  - Set threshold: 0.1 for early triggering

  - Use once: true for single animation
  - Apply to category and collection items
  - _Requirements: 20.5_

- [ ] 19.6 Implement parallax effect
  - Use useScroll hook for scroll position
  - Use useTransform to map scroll to y position

  - Apply subtle parallax to header background
  - Limit movement to prevent excessive motion
  - Keep text fixed while background moves
  - _Requirements: 20.5_

- [ ] 19.7 Add loading skeleton animations
  - Create shimmer effect with linear gradient

  - Animate background position continuously
  - Apply to badge placeholders
  - Match skeleton dimensions to actual content
  - Use motion.div with animate prop
  - _Requirements: 20.4_

- [ ] 19.8 Implement page transition animations
  - Create pageTransitionVariants
  - Initial: opacity: 0, x: -20
  - Animate: opacity: 1, x: 0
  - Exit: opacity: 0, x: 20
  - Wrap route content in AnimatePresence
  - Coordinate with sidebar active state

  - _Requirements: 20.1_

- [x] 19.9 Create useReducedMotion hook

  - Create src/hooks/useReducedMotion.ts
  - Use window.matchMedia('(prefers-reduced-motion: reduce)')
  - Listen for changes to media query
  - Return boolean indicating preference
  - Update on media query change
  - _Requirements: 20.5_


- [ ] 19.10 Respect reduced motion preference
  - Use useReducedMotion hook in components
  - Conditionally disable animations
  - Replace spring with instant transitions
  - Set duration: 0 when reduced motion preferred
  - Remove parallax and scroll effects
  - Provide instant state changes
  - Test with browser/OS settings
  - _Requirements: 20.5_


- [ ] 19.11 Optimize animation performance
  - Use only transform and opacity
  - Avoid animating width, height, margin
  - Use will-change sparingly
  - Remove will-change after animation
  - Profile with Chrome DevTools Performance
  - Ensure 60fps on mid-range devices
  - Test on mobile devices
  - _Requirements: 20.1, 20.2_


## Phase 6: Accessibility and Keyboard Navigation (Days 14-15)

- [x] 20. Implement full keyboard navigation


  - Add keyboard support
  - Implement focus management
  - Add ARIA attributes
  - Test with screen readers
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 20.1 Implement keyboard navigation

  - Support Tab/Shift+Tab for focus movement
  - Support Arrow Up/Down within sections
  - Support Enter/Space for item activation
  - Support Home key for first item
  - Support End key for last item
  - Support Escape for closing drawer/menus
  - _Requirements: 13.2, 13.3, 13.4_


- [ ] 20.2 Add ARIA attributes
  - Add role="navigation" to sidebar container
  - Add aria-label="Main navigation" to sidebar
  - Add aria-label to each section
  - Add aria-expanded to collapsible sections
  - Add aria-current="page" to active items
  - Add aria-label to badges with counts
  - Add aria-hidden to decorative icons
  - _Requirements: 13.5_


- [ ] 20.3 Implement focus management
  - Create visible focus rings with accent blue
  - Use focus-visible for keyboard-only focus
  - Implement focus trap in mobile drawer
  - Restore focus after modal/menu close
  - Add skip to main content link
  - Ensure logical tab order

  - _Requirements: 13.3, 13.4_

- [ ] 20.4 Test with screen readers
  - Test with NVDA on Windows
  - Test with VoiceOver on macOS
  - Verify all content is announced correctly
  - Test navigation flow with screen reader
  - Verify badge counts are announced
  - Test section expand/collapse announcements

  - _Requirements: 13.5_


- [ ] 20.5 Add keyboard shortcuts
  - Implement Ctrl+B to toggle sidebar
  - Implement / to focus search
  - Implement Esc to close sidebar on mobile
  - Document shortcuts in help section
  - Add visual indicators for shortcuts
  - _Requirements: 13.2, 13.3_

- [ ] 21. Theming support
  - Implement dark theme

  - Implement light theme
  - Add theme toggle
  - Ensure smooth transitions
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [ ] 21.1 Create theme configuration
  - Define dark theme color variables in CSS
  - Define light theme color variables in CSS

  - Create theme context or use existing system
  - Export theme utilities
  - _Requirements: 16.1, 16.2_

- [ ] 21.2 Apply theme to components
  - Update Sidebar with theme colors
  - Update SidebarItem with theme colors
  - Update SidebarSection with theme colors

  - Update UserProfileWidget with theme colors
  - Update SidebarBadge with theme colors
  - Use CSS variables for dynamic theming
  - _Requirements: 16.1, 16.2, 16.3_

- [x] 21.3 Implement theme transitions

  - Add CSS transitions for color changes (200ms)
  - Ensure smooth transitions between themes
  - Prevent flash of unstyled content
  - Use transition-colors utility
  - _Requirements: 16.2_

- [ ] 21.4 Test both themes
  - Verify color contrast in both themes (WCAG AA)
  - Test all component states in both themes
  - Ensure readability in both themes
  - Test hover and active states
  - Verify badge visibility in both themes
  - _Requirements: 16.1, 16.2, 16.4_

## Phase 7: Performance Optimization (Days 16-17)

- [x] 22. Optimize component performance


  - Memoize components
  - Optimize callbacks
  - Reduce re-renders
  - Implement virtual scrolling
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_


- [x] 22.1 Memoize components

  - Add React.memo to SidebarItem
  - Add React.memo to SidebarSection
  - Add React.memo to SidebarBadge
  - Add React.memo to UserProfileWidget
  - Add React.memo to ContextMenu
  - Add custom comparison functions where needed
  - _Requirements: 15.2_


- [ ] 22.2 Optimize callbacks
  - Wrap event handlers with useCallback
  - Memoize computed values with useMemo
  - Prevent unnecessary function recreations
  - Pass stable references to child components
  - _Requirements: 15.2_


- [ ] 22.3 Reduce re-renders
  - Use Zustand selectors for specific state slices
  - Avoid passing entire objects as props
  - Split large components into smaller ones
  - Profile with React DevTools Profiler
  - Identify and fix unnecessary re-renders

  - _Requirements: 15.1, 15.2_

- [ ] 22.4 Implement virtual scrolling
  - Add react-window if item count exceeds 50
  - Configure item size and overscan
  - Maintain scroll position on updates

  - Test with large datasets
  - _Requirements: 15.3_

- [ ] 22.5 Lazy load components
  - Lazy load ContextMenu component
  - Lazy load ProfileDropdown component

  - Add Suspense boundaries with fallbacks
  - Test loading behavior
  - _Requirements: 15.5_

- [ ] 22.6 Optimize bundle size
  - Analyze bundle with vite-bundle-visualizer
  - Remove unused dependencies
  - Optimize imports (tree-shaking)
  - Use dynamic imports where appropriate
  - Compress assets
  - _Requirements: 15.5_

## Phase 8: Integration and Testing (Days 18-20)

- [ ] 23. Integrate with main application
  - Add to AppLayout
  - Connect to React Router
  - Wire up hamburger menu
  - Test complete flow
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 23.1 Add Sidebar to AppLayout

  - Import Sidebar component into AppLayout
  - Position Sidebar in layout structure
  - Adjust main content margin for sidebar width (ml-64)
  - Handle sidebar state in layout
  - Pass necessary props to Sidebar
  - _Requirements: 1.1, 1.2_


- [ ] 23.2 Connect to React Router
  - Ensure all navigation items use React Router
  - Test route matching and active states

  - Verify nested route support
  - Test browser back/forward navigation
  - Test deep linking to specific pages
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1, 9.2, 9.3_

- [ ] 23.3 Wire up mobile menu toggle
  - Add hamburger button to navbar
  - Connect button to Zustand store
  - Toggle sidebar open/closed on click
  - Test on mobile viewports
  - Verify drawer animations work
  - _Requirements: 11.1, 11.2, 11.3_


- [ ] 23.4 Test complete navigation flow
  - Test navigation between all pages
  - Verify active states update correctly
  - Test mobile drawer behavior
  - Test keyboard navigation throughout app
  - Test with different user roles
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.1, 9.2, 9.3, 11.1, 11.2, 11.3, 11.4, 13.1, 13.2, 13.3_


- [ ] 24. Write comprehensive tests
  - Write unit tests
  - Write integration tests
  - Perform accessibility testing

  - Conduct visual regression testing
  - _Requirements: All_

- [ ] 24.1 Write unit tests for components
  - Test Sidebar component rendering
  - Test SidebarItem active state logic
  - Test SidebarSection collapse/expand
  - Test SidebarBadge formatting (99+ logic)
  - Test Zustand store actions
  - Test animation variants

  - Use React Testing Library
  - Achieve 80%+ code coverage
  - _Requirements: All_

- [ ] 24.2 Write integration tests
  - Test navigation flow between pages
  - Test mobile drawer open/close
  - Test context menu interactions
  - Test search filtering
  - Test badge updates from API
  - Test error handling scenarios

  - Use React Testing Library + MSW for API mocking
  - _Requirements: All_

- [ ] 24.3 Perform accessibility testing
  - Test keyboard navigation flow
  - Test screen reader announcements
  - Verify ARIA attributes with axe-core

  - Test focus management
  - Run automated accessibility checks
  - Test with actual assistive technologies
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 24.4 Visual regression testing
  - Capture component snapshots
  - Test dark and light themes
  - Test responsive layouts (mobile, tablet, desktop)
  - Test animation states

  - Compare against baseline
  - Use Percy or Chromatic
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 11.1, 11.2_

- [ ] 24.5 Performance testing
  - Test with large datasets (100+ items)
  - Measure render times
  - Test animation frame rates
  - Profile with React DevTools
  - Test on low-end devices

  - Ensure < 100ms interaction response
  - _Requirements: 15.1, 15.2, 15.3_

- [ ] 24.6 Cross-browser testing
  - Test on Chrome (latest)
  - Test on Firefox (latest)
  - Test on Safari (latest)
  - Test on Edge (latest)

  - Test on mobile browsers (iOS Safari, Android Chrome)
  - Verify animations work consistently
  - _Requirements: All_

## Phase 9: Documentation and Polish (Days 21-22)

- [x] 25. Write comprehensive documentation

  - Document components
  - Create usage examples
  - Document API integration
  - Add inline comments
  - _Requirements: All_

- [x] 25.1 Write component documentation

  - Document all component props with JSDoc
  - Add usage examples for each component
  - Document Zustand store interface
  - Document configuration options
  - Create Storybook stories for components
  - _Requirements: All_


- [ ] 25.2 Create usage examples
  - Create example of basic sidebar setup
  - Create example of custom navigation items
  - Create example of custom context menu
  - Create example of theme customization
  - Create example of custom badges
  - Add examples to documentation site
  - _Requirements: All_

- [x] 25.3 Document API integration

  - Document required API endpoints
  - Document expected response formats
  - Document error handling approach
  - Provide example API implementations
  - Create API integration guide
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_



- [ ] 25.4 Add inline code comments
  - Add JSDoc comments to all functions
  - Explain complex logic with comments
  - Document animation configurations

  - Add TODO comments for future improvements
  - _Requirements: All_

- [ ] 25.5 Create README for sidebar system
  - Write overview and features
  - Add installation instructions
  - Document configuration options
  - Add troubleshooting section
  - Include screenshots and demos
  - _Requirements: All_

- [ ] 26. Final polish and review
  - Review all animations
  - Verify consistency

  - Check spacing and alignment
  - Test on multiple browsers
  - Optimize bundle size
  - _Requirements: All_

- [ ] 26.1 Review all animations
  - Verify smoothness of all animations

  - Check timing consistency
  - Test on different devices
  - Ensure 60fps performance
  - Adjust any janky animations
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

- [x] 26.2 Verify design consistency

  - Check color scheme consistency (60:30:10 ratio)
  - Verify spacing follows 8px grid
  - Check typography consistency
  - Verify icon sizes are consistent
  - Ensure hover states are consistent
  - _Requirements: 1.1, 16.1_

- [ ] 26.3 Check spacing and alignment
  - Verify padding and margins

  - Check vertical rhythm
  - Ensure proper alignment
  - Test with different content lengths
  - Fix any layout issues
  - _Requirements: 1.1_


- [ ] 26.4 Final cross-browser testing
  - Test on all major browsers
  - Test on different OS (Windows, macOS, Linux)
  - Test on mobile devices
  - Verify animations work everywhere
  - Fix any browser-specific issues

  - _Requirements: All_

- [ ] 26.5 Optimize final bundle size
  - Run bundle analyzer
  - Remove any unused code
  - Optimize imports
  - Compress assets
  - Verify bundle size is acceptable (< 50KB gzipped)
  - _Requirements: 15.5_

- [x] 26.6 Create demo and showcase

  - Build interactive demo page
  - Showcase all features
  - Add code examples
  - Create video walkthrough
  - Prepare for presentation
  - _Requirements: All_

## Summary

**Total Estimated Time: 22 days**

**Phase Breakdown:**
- Phase 1: Foundation (2 days)
- Phase 2: API Integration (2 days)
- Phase 3: Core UI Components (4 days)
- Phase 4: Advanced Features (3 days)
- Phase 5: Animation Polish (2 days)
- Phase 6: Accessibility (2 days)
- Phase 7: Performance (2 days)
- Phase 8: Integration & Testing (3 days)
- Phase 9: Documentation & Polish (2 days)

**Key Milestones:**
- Day 2: Foundation complete, ready to build components
- Day 4: API integration complete, data flowing
- Day 8: All core components built and functional
- Day 11: Advanced features complete
- Day 15: Accessibility and theming complete
- Day 17: Performance optimized
- Day 20: Fully integrated and tested
- Day 22: Documented and production-ready

**Ready to start development!** 🚀
