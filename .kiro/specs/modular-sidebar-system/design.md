# Design Document

## Overview

The Modular Sidebar System is a comprehensive navigation component built with React, TypeScript, and Framer Motion. It provides a flexible, reusable sidebar that can be easily integrated into any page of the Neo Alexandria application. The design emphasizes modularity through composition, allowing individual sidebar components to be mixed and matched based on application needs.

## Architecture

### Component Hierarchy

```
Sidebar (Container)
├── SidebarHeader
│   ├── Logo
│   └── SearchInput (optional)
├── SidebarContent (scrollable)
│   ├── SidebarSection (Main)
│   │   ├── SidebarItem (Dashboard)
│   │   ├── SidebarItem (Library)
│   │   ├── SidebarItem (Search)
│   │   └── SidebarItem (Knowledge Graph)
│   ├── SidebarSection (Collections)
│   │   ├── SidebarItem (Favorites) + Badge
│   │   ├── SidebarItem (Recent) + Badge
│   │   ├── SidebarItem (Read Later) + Badge
│   │   └── SidebarItem (Shared) + Badge
│   ├── SidebarSection (Categories)
│   │   ├── SidebarItem (Science) + Badge
│   │   ├── SidebarItem (Technology) + Badge
│   │   ├── SidebarItem (Art & Design) + Badge
│   │   └── SidebarItem (Business) + Badge
│   └── SidebarSection (Settings)
│       └── SidebarItem (Settings)
└── SidebarFooter
    └── UserProfileWidget
        ├── Avatar
        ├── UserInfo (name, email)
        └── DropdownMenu
```

### Technology Stack

- React 18.3.1 with TypeScript
- Framer Motion for animations
- Zustand for state management
- React Router for navigation
- TailwindCSS for styling
- Headless UI for accessible components


## Core Components

### 1. Sidebar Component

**File:** `src/components/Sidebar/Sidebar.tsx`

**Props:**
```typescript
interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  className?: string;
  variant?: 'desktop' | 'mobile';
}
```

**Responsibilities:**
- Container for all sidebar content
- Manages open/closed state for mobile
- Handles backdrop overlay for mobile drawer
- Provides context for child components

**State:**
- `isOpen: boolean` - Controls visibility on mobile
- `scrollPosition: number` - Tracks scroll for effects


### 2. SidebarHeader Component

**File:** `src/components/Sidebar/SidebarHeader.tsx`

**Props:**
```typescript
interface SidebarHeaderProps {
  logoSrc?: string;
  appName: string;
  onLogoClick?: () => void;
  showSearch?: boolean;
}
```

**Features:**
- Logo with gradient background
- Application name display
- Optional search input
- Click handler for home navigation


### 3. SidebarSection Component

**File:** `src/components/Sidebar/SidebarSection.tsx`

**Props:**
```typescript
interface SidebarSectionProps {
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  icon?: React.ReactNode;
}
```

**Features:**
- Section header with title
- Collapsible functionality
- Expand/collapse animation
- Persists state to localStorage


### 4. SidebarItem Component

**File:** `src/components/Sidebar/SidebarItem.tsx`

**Props:**
```typescript
interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  to?: string;
  onClick?: () => void;
  badge?: number | string;
  active?: boolean;
  contextMenu?: ContextMenuItem[];
}

interface ContextMenuItem {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: 'default' | 'danger';
}
```

**Features:**
- Icon and label display
- Active state highlighting
- Hover effects with accent bar
- Optional badge display
- Context menu support
- Keyboard navigation


### 5. SidebarBadge Component

**File:** `src/components/Sidebar/SidebarBadge.tsx`

**Props:**
```typescript
interface SidebarBadgeProps {
  count: number | string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  pulse?: boolean;
}
```

**Features:**
- Displays count or notification indicator
- Multiple color variants
- Optional pulse animation
- Handles large numbers (99+)


### 6. UserProfileWidget Component

**File:** `src/components/Sidebar/UserProfileWidget.tsx`

**Props:**
```typescript
interface UserProfileWidgetProps {
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  menuItems?: ProfileMenuItem[];
}

interface ProfileMenuItem {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  divider?: boolean;
}
```

**Features:**
- User avatar display
- Name and email display
- Dropdown menu on click
- Default menu items (Profile, Settings, Sign Out)
- Customizable menu items


## State Management

### Zustand Store

**File:** `src/store/useSidebarStore.ts`

```typescript
interface SidebarState {
  // UI State
  isOpen: boolean;
  isMobile: boolean;
  
  // Section State
  expandedSections: Record<string, boolean>;
  
  // Data State
  collectionCounts: Record<string, number>;
  categoryCounts: Record<string, number>;
  
  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSection: (sectionId: string) => void;
  setExpandedSection: (sectionId: string, expanded: boolean) => void;
  updateCollectionCounts: (counts: Record<string, number>) => void;
  updateCategoryCounts: (counts: Record<string, number>) => void;
}
```

**Persistence:**
- `expandedSections` persisted to localStorage
- `isOpen` persisted for mobile only
- Counts fetched from API on mount


## Data Models

### Navigation Configuration

**File:** `src/config/sidebarConfig.ts`

```typescript
interface NavigationConfig {
  sections: SidebarSectionConfig[];
}

interface SidebarSectionConfig {
  id: string;
  title: string;
  collapsible: boolean;
  defaultExpanded: boolean;
  items: SidebarItemConfig[];
}

interface SidebarItemConfig {
  id: string;
  label: string;
  icon: string; // FontAwesome class name
  to: string;
  badge?: {
    source: 'collection' | 'category' | 'static';
    key?: string;
    value?: number | string;
  };
  contextMenu?: ContextMenuConfig[];
}

interface ContextMenuConfig {
  label: string;
  icon?: string;
  action: string;
  variant?: 'default' | 'danger';
}
```


## Styling and Theming

### Color Scheme

**Dark Theme (Default):**
```css
--sidebar-bg: #2D3748; /* charcoal-grey-700 */
--sidebar-bg-dark: #1A202C; /* charcoal-grey-800 */
--sidebar-text: #F7FAFC; /* charcoal-grey-50 */
--sidebar-text-muted: #CBD5E0; /* charcoal-grey-300 */
--sidebar-accent: #3B82F6; /* accent-blue-500 */
--sidebar-hover: rgba(74, 144, 226, 0.1);
--sidebar-active: rgba(74, 144, 226, 0.15);
--sidebar-border: rgba(255, 255, 255, 0.1);
```

**Light Theme:**
```css
--sidebar-bg: #F7FAFC; /* charcoal-grey-50 */
--sidebar-bg-dark: #EDF2F7; /* charcoal-grey-100 */
--sidebar-text: #1A202C; /* charcoal-grey-800 */
--sidebar-text-muted: #718096; /* charcoal-grey-500 */
--sidebar-accent: #3B82F6; /* accent-blue-500 */
--sidebar-hover: rgba(74, 144, 226, 0.08);
--sidebar-active: rgba(74, 144, 226, 0.12);
--sidebar-border: rgba(0, 0, 0, 0.1);
```


### Animation Specifications

**Sidebar Open/Close:**
```typescript
const sidebarVariants = {
  open: {
    x: 0,
    transition: { duration: 0.3, ease: 'easeInOut' }
  },
  closed: {
    x: -260,
    transition: { duration: 0.3, ease: 'easeInOut' }
  }
};
```

**Section Expand/Collapse:**
```typescript
const sectionVariants = {
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.2, ease: 'easeInOut' }
  },
  collapsed: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeInOut' }
  }
};
```

**Item Hover:**
```typescript
const itemVariants = {
  rest: { x: 0 },
  hover: {
    x: 2,
    transition: { duration: 0.15 }
  }
};
```

**Badge Pulse:**
```typescript
const badgePulseVariants = {
  pulse: {
    scale: [1, 1.1, 1],
    transition: { duration: 0.3, ease: 'easeInOut' }
  }
};
```


## API Integration

### Endpoints

**Collection Counts:**
```typescript
GET /collections/counts?user_id={userId}

Response:
{
  "favorites": 12,
  "recent": 8,
  "read_later": 5,
  "shared": 3
}
```

**Category Counts:**
```typescript
GET /resources/category-counts

Response:
{
  "science": 45,
  "technology": 67,
  "art_design": 23,
  "business": 34
}
```

**User Profile:**
```typescript
GET /users/me

Response:
{
  "id": "user123",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "avatar": "https://example.com/avatar.jpg"
}
```


### Custom Hooks

**File:** `src/hooks/useSidebarData.ts`

```typescript
export function useSidebarData() {
  const { data: collectionCounts, isLoading: loadingCollections } = useQuery({
    queryKey: ['sidebar', 'collections'],
    queryFn: () => sidebarApi.getCollectionCounts(),
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const { data: categoryCounts, isLoading: loadingCategories } = useQuery({
    queryKey: ['sidebar', 'categories'],
    queryFn: () => sidebarApi.getCategoryCounts(),
    refetchInterval: 60000 // Refresh every minute
  });

  const { data: user, isLoading: loadingUser } = useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => userApi.getProfile()
  });

  return {
    collectionCounts,
    categoryCounts,
    user,
    isLoading: loadingCollections || loadingCategories || loadingUser
  };
}
```


## Responsive Design

### Breakpoints

- **Desktop:** >= 768px - Full sidebar visible
- **Tablet:** 768px - 1024px - Full sidebar with adjusted padding
- **Mobile:** < 768px - Drawer mode with overlay

### Mobile Drawer Behavior

1. Sidebar positioned off-screen by default (translateX(-100%))
2. Hamburger button in navbar toggles drawer
3. Semi-transparent backdrop (rgba(0, 0, 0, 0.5)) overlays content
4. Swipe gesture support for closing
5. Auto-close on navigation or backdrop click

### Touch Interactions

- Minimum touch target size: 44x44px
- Increased padding on mobile (0.875rem vs 0.75rem)
- Disabled hover effects on touch devices
- Swipe-to-close gesture with velocity threshold


## Accessibility

### ARIA Attributes

```typescript
// Sidebar container
<aside
  role="navigation"
  aria-label="Main navigation"
  aria-hidden={!isOpen}
>

// Collapsible section
<button
  aria-expanded={isExpanded}
  aria-controls={`section-${id}`}
>

// Navigation item
<a
  role="menuitem"
  aria-current={isActive ? 'page' : undefined}
  aria-label={`${label}${badge ? ` (${badge} items)` : ''}`}
>

// Badge
<span
  role="status"
  aria-label={`${count} notifications`}
>
```

### Keyboard Navigation

- Tab: Move focus to next item
- Shift+Tab: Move focus to previous item
- Enter/Space: Activate focused item
- Arrow Up/Down: Navigate within section
- Escape: Close mobile drawer or context menu
- Home: Focus first item
- End: Focus last item


## Performance Optimization

### Rendering Optimization

1. **React.memo** on all sidebar components to prevent unnecessary re-renders
2. **useCallback** for event handlers to maintain referential equality
3. **useMemo** for computed values (filtered items, sorted sections)
4. **Virtual scrolling** if item count exceeds 50 (using react-window)

### Code Splitting

```typescript
// Lazy load context menu
const ContextMenu = lazy(() => import('./ContextMenu'));

// Lazy load user profile dropdown
const ProfileDropdown = lazy(() => import('./ProfileDropdown'));
```

### Data Fetching Strategy

1. Initial data fetched on mount
2. Background refetch every 30-60 seconds
3. Optimistic updates for immediate feedback
4. Stale-while-revalidate caching strategy
5. Error boundaries for graceful degradation


## Testing Strategy

### Unit Tests

- Component rendering with different props
- State management (Zustand store)
- Event handlers and callbacks
- Utility functions (badge formatting, etc.)

### Integration Tests

- Navigation flow between pages
- Section expand/collapse behavior
- Badge count updates from API
- Context menu interactions
- Mobile drawer open/close

### Accessibility Tests

- Keyboard navigation flow
- Screen reader announcements
- Focus management
- ARIA attribute correctness

### Visual Regression Tests

- Component snapshots in different states
- Theme switching (dark/light)
- Responsive layouts (desktop/tablet/mobile)
- Animation states


## File Structure

```
src/
├── components/
│   └── Sidebar/
│       ├── Sidebar.tsx
│       ├── SidebarHeader.tsx
│       ├── SidebarContent.tsx
│       ├── SidebarSection.tsx
│       ├── SidebarItem.tsx
│       ├── SidebarBadge.tsx
│       ├── SidebarFooter.tsx
│       ├── UserProfileWidget.tsx
│       ├── ContextMenu.tsx
│       ├── ProfileDropdown.tsx
│       ├── index.ts
│       └── __tests__/
│           ├── Sidebar.test.tsx
│           ├── SidebarItem.test.tsx
│           └── SidebarSection.test.tsx
├── config/
│   └── sidebarConfig.ts
├── hooks/
│   ├── useSidebarData.ts
│   └── useSidebarNavigation.ts
├── store/
│   └── useSidebarStore.ts
├── services/
│   └── api/
│       └── sidebar.ts
└── types/
    └── sidebar.ts
```


## Detailed Animation Examples

### Sidebar Open/Close Animation

```typescript
// Sidebar.tsx
import { motion, AnimatePresence } from 'framer-motion';

const sidebarVariants = {
  open: {
    x: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30
    }
  },
  closed: {
    x: -260,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30
    }
  }
};

const backdropVariants = {
  open: {
    opacity: 0.5,
    transition: { duration: 0.3 }
  },
  closed: {
    opacity: 0,
    transition: { duration: 0.3 }
  }
};

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed inset-0 bg-black z-40"
            variants={backdropVariants}
            initial="closed"
            animate="open"
            exit="closed"
            onClick={onClose}
          />
        )}
      </AnimatePresence>
      
      <motion.aside
        className="fixed left-0 top-0 h-full w-64 bg-charcoal-grey-700 z-50"
        variants={sidebarVariants}
        initial="closed"
        animate={isOpen ? 'open' : 'closed'}
      >
        {/* Sidebar content */}
      </motion.aside>
    </>
  );
}
```

### Section Expand/Collapse Animation

```typescript
// SidebarSection.tsx
import { motion, AnimatePresence } from 'framer-motion';

const sectionContentVariants = {
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: {
      height: {
        duration: 0.2,
        ease: [0.4, 0, 0.2, 1]
      },
      opacity: {
        duration: 0.2,
        delay: 0.05
      }
    }
  },
  collapsed: {
    height: 0,
    opacity: 0,
    transition: {
      height: {
        duration: 0.2,
        ease: [0.4, 0, 0.2, 1]
      },
      opacity: {
        duration: 0.15
      }
    }
  }
};

const chevronVariants = {
  expanded: { rotate: 90 },
  collapsed: { rotate: 0 }
};

export function SidebarSection({ title, children, isExpanded, onToggle }: Props) {
  return (
    <div className="sidebar-section">
      <button onClick={onToggle} className="section-header">
        <motion.span
          variants={chevronVariants}
          animate={isExpanded ? 'expanded' : 'collapsed'}
          transition={{ duration: 0.2 }}
        >
          <ChevronIcon />
        </motion.span>
        <span>{title}</span>
      </button>
      
      <motion.div
        variants={sectionContentVariants}
        initial="collapsed"
        animate={isExpanded ? 'expanded' : 'collapsed'}
        style={{ overflow: 'hidden' }}
      >
        {children}
      </motion.div>
    </div>
  );
}
```

### Stagger Animation for Navigation Items

```typescript
// SidebarSection.tsx
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { 
    opacity: 0, 
    x: -10 
  },
  show: { 
    opacity: 1, 
    x: 0,
    transition: {
      duration: 0.2,
      ease: [0.4, 0, 0.2, 1]
    }
  }
};

export function SidebarSection({ items }: Props) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-1"
    >
      {items.map((item) => (
        <motion.li key={item.id} variants={itemVariants}>
          <SidebarItem {...item} />
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### Accent Bar Slide-In Animation

```typescript
// SidebarItem.tsx
const accentBarVariants = {
  rest: {
    x: -3,
    opacity: 0,
    transition: { duration: 0.15 }
  },
  hover: {
    x: 0,
    opacity: 1,
    transition: {
      duration: 0.15,
      ease: 'easeOut'
    }
  },
  active: {
    x: 0,
    opacity: 1
  }
};

const itemVariants = {
  rest: { 
    x: 0,
    backgroundColor: 'transparent'
  },
  hover: { 
    x: 2,
    backgroundColor: 'rgba(74, 144, 226, 0.1)',
    transition: { duration: 0.15 }
  }
};

export function SidebarItem({ label, icon, isActive }: Props) {
  return (
    <motion.div
      className="relative sidebar-item"
      variants={itemVariants}
      initial="rest"
      whileHover="hover"
      whileTap={{ scale: 0.98 }}
    >
      <motion.div
        className="absolute left-0 top-0 h-full w-[3px] bg-accent-blue-500"
        variants={accentBarVariants}
        animate={isActive ? 'active' : 'rest'}
      />
      
      <div className="flex items-center px-4 py-3">
        <motion.span
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.2 }}
        >
          {icon}
        </motion.span>
        <motion.span
          whileHover={{ x: 2 }}
          transition={{ duration: 0.2 }}
        >
          {label}
        </motion.span>
      </div>
    </motion.div>
  );
}
```

### Badge Pulse Animation

```typescript
// SidebarBadge.tsx
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useRef } from 'react';

const badgePulseVariants = {
  pulse: {
    scale: [1, 1.15, 1],
    boxShadow: [
      '0 0 0 rgba(59, 130, 246, 0)',
      '0 0 8px rgba(59, 130, 246, 0.6)',
      '0 0 0 rgba(59, 130, 246, 0)'
    ],
    transition: {
      duration: 0.3,
      ease: 'easeInOut'
    }
  }
};

export function SidebarBadge({ count }: Props) {
  const controls = useAnimation();
  const prevCountRef = useRef(count);

  useEffect(() => {
    if (prevCountRef.current !== count && count > 0) {
      controls.start('pulse');
    }
    prevCountRef.current = count;
  }, [count, controls]);

  return (
    <motion.span
      className="badge"
      variants={badgePulseVariants}
      animate={controls}
    >
      {count > 99 ? '99+' : count}
    </motion.span>
  );
}
```

### Context Menu Animation

```typescript
// ContextMenu.tsx
const menuVariants = {
  closed: {
    opacity: 0,
    scale: 0.95,
    y: -10,
    transition: {
      duration: 0.15
    }
  },
  open: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.15,
      ease: 'easeOut',
      staggerChildren: 0.03,
      delayChildren: 0.05
    }
  }
};

const menuItemVariants = {
  closed: {
    opacity: 0,
    x: -10
  },
  open: {
    opacity: 1,
    x: 0
  }
};

export function ContextMenu({ isOpen, items }: Props) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="context-menu"
          variants={menuVariants}
          initial="closed"
          animate="open"
          exit="closed"
        >
          {items.map((item) => (
            <motion.button
              key={item.id}
              variants={menuItemVariants}
              whileHover={{
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                x: 2
              }}
            >
              {item.label}
            </motion.button>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

### Scroll-Triggered Fade-In

```typescript
// SidebarItem.tsx
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

export function SidebarItem({ label }: Props) {
  const ref = useRef(null);
  const isInView = useInView(ref, { 
    once: true, 
    amount: 0.1 
  });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      {label}
    </motion.div>
  );
}
```

### Reduced Motion Support

```typescript
// hooks/useReducedMotion.ts
import { useEffect, useState } from 'react';

export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

// Usage in component
export function Sidebar() {
  const prefersReducedMotion = useReducedMotion();
  
  const transition = prefersReducedMotion 
    ? { duration: 0 } 
    : { type: 'spring', stiffness: 300, damping: 30 };

  return (
    <motion.aside
      animate={{ x: isOpen ? 0 : -260 }}
      transition={transition}
    >
      {/* Content */}
    </motion.aside>
  );
}
```

### Animation Configuration File

```typescript
// config/animations.ts

// Timing constants
export const DURATION = {
  FAST: 0.15,
  NORMAL: 0.2,
  SLOW: 0.3,
  SLOWER: 0.5
} as const;

// Easing functions
export const EASE = {
  IN_OUT: [0.4, 0, 0.2, 1],
  OUT: [0, 0, 0.2, 1],
  IN: [0.4, 0, 1, 1],
  SPRING: [0.68, -0.55, 0.265, 1.55]
} as const;

// Spring configurations
export const SPRING = {
  SMOOTH: { stiffness: 300, damping: 30 },
  BOUNCY: { stiffness: 400, damping: 25 },
  GENTLE: { stiffness: 200, damping: 20 }
} as const;

// Reusable variant objects
export const VARIANTS = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  },
  slideIn: {
    hidden: { x: -20, opacity: 0 },
    visible: { x: 0, opacity: 1 }
  },
  scaleIn: {
    hidden: { scale: 0.95, opacity: 0 },
    visible: { scale: 1, opacity: 1 }
  }
} as const;
```
