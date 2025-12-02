# Design Document: Sidebar Redesign

## Overview

This design document outlines the architecture for redesigning the Neo Alexandria sidebar using shadcn/ui principles. The new sidebar will be composable, highly functional, and maintain the Modern Charcoal theme with purple accents.

### Design Goals

1. **Composable Architecture** - Build from small, reusable components
2. **Collapsible States** - Support expanded, icon-only, and mobile modes
3. **Smooth Animations** - GPU-accelerated transitions at 60fps
4. **Theme Consistency** - Maintain Modern Charcoal + Purple aesthetic
5. **Developer Friendly** - Easy to customize and extend

## Architecture

### Component Hierarchy

```
SidebarProvider (Context)
└── Sidebar (Container)
    ├── SidebarHeader (Sticky Top)
    │   └── Custom Content
    ├── SidebarContent (Scrollable)
    │   └── SidebarGroup (Section)
    │       ├── SidebarGroupLabel
    │       ├── SidebarGroupContent
    │       │   └── SidebarMenu
    │       │       └── SidebarMenuItem
    │       │           ├── SidebarMenuButton
    │       │           ├── SidebarMenuBadge
    │       │           └── SidebarMenuAction
    │       └── SidebarGroupAction
    ├── SidebarFooter (Sticky Bottom)
    │   └── Custom Content
    └── SidebarRail (Toggle Handle)
```

### State Management

```typescript
interface SidebarState {
  open: boolean;              // Desktop open/closed
  openMobile: boolean;        // Mobile open/closed
  isMobile: boolean;          // Is mobile viewport
  state: 'expanded' | 'collapsed';  // Current state
}

interface SidebarContext extends SidebarState {
  setOpen: (open: boolean) => void;
  setOpenMobile: (open: boolean) => void;
  toggleSidebar: () => void;
}
```

## Components and Interfaces

### 1. SidebarProvider

**Purpose**: Manages sidebar state and provides context

```typescript
interface SidebarProviderProps {
  defaultOpen?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

export const SidebarProvider = ({
  defaultOpen = true,
  open: controlledOpen,
  onOpenChange,
  children
}: SidebarProviderProps) => {
  const [open, setOpen] = useState(defaultOpen);
  const [openMobile, setOpenMobile] = useState(false);
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  // Keyboard shortcut (Ctrl/Cmd + B)
  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
    };
    window.addEventListener('keydown', handleKeyboard);
    return () => window.removeEventListener('keydown', handleKeyboard);
  }, []);
  
  // Persist state
  useEffect(() => {
    localStorage.setItem('sidebar-state', JSON.stringify(open));
  }, [open]);
  
  return (
    <SidebarContext.Provider value={contextValue}>
      {children}
    </SidebarContext.Provider>
  );
};
```

### 2. Sidebar (Main Container)

**Purpose**: Main sidebar container with collapsible functionality

```typescript
interface SidebarProps {
  side?: 'left' | 'right';
  variant?: 'sidebar' | 'floating' | 'inset';
  collapsible?: 'offcanvas' | 'icon' | 'none';
  className?: string;
  children: React.ReactNode;
}

// Width constants
const SIDEBAR_WIDTH = '260px';
const SIDEBAR_WIDTH_ICON = '60px';
const SIDEBAR_WIDTH_MOBILE = '280px';
```

**Styling**:
```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background: var(--primary-black);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 900;
}

.sidebar[data-state="expanded"] {
  width: 260px;
}

.sidebar[data-state="collapsed"] {
  width: 60px;
}

.sidebar[data-mobile="true"] {
  transform: translateX(-100%);
}

.sidebar[data-mobile="true"][data-state="expanded"] {
  transform: translateX(0);
}
```

### 3. SidebarHeader & SidebarFooter

**Purpose**: Sticky header and footer areas

```typescript
interface SidebarHeaderProps {
  className?: string;
  children: React.ReactNode;
}

export const SidebarHeader = ({ className, children }: SidebarHeaderProps) => {
  return (
    <div className={cn("sidebar-header", className)}>
      {children}
    </div>
  );
};
```

**Styling**:
```css
.sidebar-header,
.sidebar-footer {
  position: sticky;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: var(--primary-black);
  z-index: 10;
}

.sidebar-header {
  top: 0;
}

.sidebar-footer {
  bottom: 0;
  border-bottom: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
```

### 4. SidebarContent

**Purpose**: Scrollable content area

```typescript
export const SidebarContent = ({ className, children }: SidebarContentProps) => {
  return (
    <div className={cn("sidebar-content", className)}>
      {children}
    </div>
  );
};
```

**Styling**:
```css
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1rem 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(168, 85, 247, 0.3);
  border-radius: 2px;
}
```

### 5. SidebarGroup

**Purpose**: Logical section grouping

```typescript
interface SidebarGroupProps {
  className?: string;
  children: React.ReactNode;
}

export const SidebarGroup = ({ className, children }: SidebarGroupProps) => {
  return (
    <div className={cn("sidebar-group", className)}>
      {children}
    </div>
  );
};
```

**Styling**:
```css
.sidebar-group {
  padding: 0.5rem 0;
  margin-bottom: 1rem;
}

.sidebar-group-label {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--gray-400);
  transition: opacity 300ms;
}

.sidebar[data-state="collapsed"] .sidebar-group-label {
  opacity: 0;
  pointer-events: none;
}
```

### 6. SidebarMenu & SidebarMenuItem

**Purpose**: Navigation menu structure

```typescript
interface SidebarMenuButtonProps {
  asChild?: boolean;
  isActive?: boolean;
  tooltip?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
}

export const SidebarMenuButton = ({
  asChild,
  isActive,
  tooltip,
  icon: Icon,
  children
}: SidebarMenuButtonProps) => {
  const { state } = useSidebar();
  const Comp = asChild ? Slot : 'button';
  
  return (
    <Tooltip content={state === 'collapsed' ? tooltip : undefined}>
      <Comp
        className={cn(
          "sidebar-menu-button",
          isActive && "active"
        )}
        data-active={isActive}
      >
        {Icon && <Icon size={20} />}
        <span className="sidebar-menu-label">{children}</span>
      </Comp>
    </Tooltip>
  );
};
```

**Styling**:
```css
.sidebar-menu-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  color: var(--gray-400);
  text-decoration: none;
  border-radius: 8px;
  transition: all 200ms;
  position: relative;
  overflow: hidden;
}

.sidebar-menu-button::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: var(--accent-purple);
  transform: translateX(-100%);
  transition: transform 200ms;
}

.sidebar-menu-button:hover,
.sidebar-menu-button.active {
  background: rgba(168, 85, 247, 0.1);
  color: var(--primary-white);
}

.sidebar-menu-button:hover::before,
.sidebar-menu-button.active::before {
  transform: translateX(0);
}

.sidebar-menu-button:hover .sidebar-menu-glow {
  opacity: 1;
}

.sidebar-menu-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(168, 85, 247, 0.15), transparent 70%);
  opacity: 0;
  transition: opacity 300ms;
  pointer-events: none;
}

.sidebar[data-state="collapsed"] .sidebar-menu-button {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar[data-state="collapsed"] .sidebar-menu-label {
  opacity: 0;
  width: 0;
  overflow: hidden;
}
```

### 7. SidebarRail

**Purpose**: Toggle handle for collapsed sidebar

```typescript
export const SidebarRail = () => {
  const { toggleSidebar, state } = useSidebar();
  
  if (state === 'expanded') return null;
  
  return (
    <button
      className="sidebar-rail"
      onClick={toggleSidebar}
      aria-label="Expand sidebar"
    >
      <span className="sr-only">Expand sidebar</span>
    </button>
  );
};
```

**Styling**:
```css
.sidebar-rail {
  position: absolute;
  right: -4px;
  top: 0;
  width: 4px;
  height: 100%;
  background: var(--accent-purple);
  opacity: 0;
  transition: opacity 200ms, width 200ms;
  cursor: pointer;
  border: none;
}

.sidebar-rail:hover {
  opacity: 0.5;
  width: 6px;
}

.sidebar-rail:active {
  opacity: 0.8;
}
```

### 8. Tooltip Component

**Purpose**: Show labels in collapsed mode

```typescript
interface TooltipProps {
  content?: string;
  side?: 'right' | 'left' | 'top' | 'bottom';
  children: React.ReactNode;
}

export const Tooltip = ({ content, side = 'right', children }: TooltipProps) => {
  if (!content) return <>{children}</>;
  
  return (
    <div className="tooltip-wrapper">
      {children}
      <div className="tooltip" data-side={side}>
        {content}
      </div>
    </div>
  );
};
```

## Data Models

### Sidebar Configuration

```typescript
interface SidebarConfig {
  mainItems: SidebarItem[];
  collections: SidebarItem[];
}

interface SidebarItem {
  iconName: IconName;
  label: string;
  path: string;
  badge?: number;
  children?: SidebarItem[];
}
```

## Animation Strategy

### Collapse/Expand Animation

```typescript
const sidebarVariants = {
  expanded: {
    width: 260,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  },
  collapsed: {
    width: 60,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
};

const labelVariants = {
  expanded: {
    opacity: 1,
    width: 'auto',
    transition: { duration: 0.2, delay: 0.1 }
  },
  collapsed: {
    opacity: 0,
    width: 0,
    transition: { duration: 0.2 }
  }
};
```

### Mobile Slide Animation

```typescript
const mobileSidebarVariants = {
  open: {
    x: 0,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  },
  closed: {
    x: '-100%',
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
};
```

## Theme Integration

### CSS Variables

```css
:root {
  /* Sidebar specific */
  --sidebar-background: #0a0a0a;
  --sidebar-foreground: #ffffff;
  --sidebar-accent: #a855f7;
  --sidebar-accent-hover: #c084fc;
  --sidebar-border: rgba(255, 255, 255, 0.08);
  --sidebar-width: 260px;
  --sidebar-width-icon: 60px;
  --sidebar-width-mobile: 280px;
}
```

## Performance Considerations

1. **Memoization**: Memoize all menu items to prevent re-renders
2. **GPU Acceleration**: Use transform and opacity only
3. **Lazy Loading**: Defer loading of collapsed group content
4. **Virtual Scrolling**: For very long navigation lists (future)
5. **Debounced Resize**: Throttle resize event handlers

## Accessibility

1. **Keyboard Navigation**: Full Tab/Arrow key support
2. **ARIA Labels**: Proper labels on all interactive elements
3. **Focus Management**: Trap focus in mobile overlay
4. **Screen Reader**: Announce state changes
5. **Reduced Motion**: Respect prefers-reduced-motion

## Migration Strategy

### Phase 1: Create New Components
- Build new sidebar components alongside existing
- No breaking changes to current implementation

### Phase 2: Update MainLayout
- Wrap app in SidebarProvider
- Replace old Sidebar with new implementation
- Test all navigation flows

### Phase 3: Cleanup
- Remove old sidebar components
- Update all navigation data
- Final testing and polish

## File Structure

```
src/
├── components/
│   └── sidebar/
│       ├── Sidebar.tsx
│       ├── SidebarProvider.tsx
│       ├── SidebarHeader.tsx
│       ├── SidebarFooter.tsx
│       ├── SidebarContent.tsx
│       ├── SidebarGroup.tsx
│       ├── SidebarMenu.tsx
│       ├── SidebarMenuItem.tsx
│       ├── SidebarMenuButton.tsx
│       ├── SidebarRail.tsx
│       ├── useSidebar.ts
│       ├── sidebar.css
│       └── index.ts
```

## Success Criteria

- ✅ Sidebar collapses to 60px icon mode
- ✅ Smooth 300ms transitions at 60fps
- ✅ Keyboard shortcut (Ctrl/Cmd + B) works
- ✅ Mobile responsive with overlay
- ✅ Tooltips show in collapsed mode
- ✅ State persists in localStorage
- ✅ Purple accent theme maintained
- ✅ Fully keyboard accessible
- ✅ Zero console errors
- ✅ Composable and extensible

This design provides a solid foundation for a professional, shadcn-inspired sidebar while maintaining the Neo Alexandria aesthetic.
