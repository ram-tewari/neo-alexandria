# Design Document: Phase 1 - Core Workbench & Navigation

## Overview

Phase 1 implements the foundational "Command Center" layout using a Hybrid Power approach that combines:
- **magic-mcp** for generating initial component structure
- **shadcn-ui** for reliable core UI primitives
- **magic-ui** for strategic animations and polish

This creates a professional, performant workspace with keyboard-first navigation and strategic visual enhancements.

## Architecture

### Component Hierarchy

```
App
├── AuthProvider (existing)
├── ThemeProvider (new)
└── Router
    ├── __root.tsx
    │   └── RootLayout (new)
    │       ├── Toaster
    │       └── Outlet
    └── _auth.tsx (existing, enhanced)
        └── WorkbenchLayout (new)
            ├── WorkbenchHeader
            │   ├── RepositorySwitcher
            │   ├── CommandPaletteTrigger
            │   └── UserMenu
            ├── WorkbenchSidebar
            │   ├── NavigationItems
            │   └── SidebarToggle
            └── WorkbenchContent
                └── Outlet (route content)
```

### State Management

**Zustand Stores**:

1. **workbenchStore**
   - `sidebarOpen: boolean`
   - `sidebarCollapsed: boolean`
   - `toggleSidebar()`
   - `setSidebarOpen(open: boolean)`

2. **repositoryStore**
   - `repositories: Repository[]`
   - `activeRepository: Repository | null`
   - `setActiveRepository(id: string)`
   - `fetchRepositories()`

3. **commandPaletteStore**
   - `isOpen: boolean`
   - `commands: Command[]`
   - `recentCommands: Command[]`
   - `open()`
   - `close()`
   - `executeCommand(id: string)`

4. **themeStore**
   - `theme: 'light' | 'dark' | 'system'`
   - `resolvedTheme: 'light' | 'dark'`
   - `setTheme(theme: Theme)`

## Components and Interfaces

### 1. WorkbenchLayout

**Purpose**: Main layout container with sidebar and content area

**Props**:
```typescript
interface WorkbenchLayoutProps {
  children: React.ReactNode;
}
```

**Implementation Strategy**:
- Use **magic-mcp** to generate initial layout structure
- Use **shadcn-ui** Sheet component for sidebar base
- Add **magic-ui** smooth transitions for sidebar animation

**Key Features**:
- Responsive sidebar (collapsible, auto-collapse on mobile)
- Persistent state in localStorage
- Smooth animations (200ms duration)
- Touch-friendly on mobile

---

### 2. WorkbenchSidebar

**Purpose**: Navigation sidebar with module links

**Props**:
```typescript
interface WorkbenchSidebarProps {
  isOpen: boolean;
  isCollapsed: boolean;
  onToggle: () => void;
}
```

**Implementation Strategy**:
- Use **shadcn-ui** Button, Tooltip components
- Use **magic-ui** animated entrance for nav items
- Custom icons from lucide-react

**Navigation Items**:
```typescript
const navigationItems = [
  { id: 'repositories', label: 'Repositories', icon: FolderGit2, path: '/repositories' },
  { id: 'cortex', label: 'Cortex', icon: Brain, path: '/cortex' },
  { id: 'library', label: 'Library', icon: Library, path: '/library' },
  { id: 'planner', label: 'Planner', icon: ListTodo, path: '/planner' },
  { id: 'wiki', label: 'Wiki', icon: BookOpen, path: '/wiki' },
  { id: 'ops', label: 'Ops', icon: Activity, path: '/ops' },
];
```

**States**:
- Default: Full width with icons + labels
- Collapsed: Icon-only with tooltips
- Mobile: Overlay with backdrop

---

### 3. CommandPalette

**Purpose**: Global keyboard-driven command interface

**Props**:
```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Implementation Strategy**:
- Use **shadcn-ui** Command component (cmdk)
- Use **magic-ui** spotlight effect for entrance animation
- Custom keyboard handling for Cmd+K / Ctrl+K

**Command Structure**:
```typescript
interface Command {
  id: string;
  label: string;
  description?: string;
  icon?: React.ComponentType;
  shortcut?: string[];
  action: () => void | Promise<void>;
  category: 'navigation' | 'actions' | 'settings';
}
```

**Built-in Commands**:
- Navigate to... (all routes)
- Toggle sidebar (Cmd+B)
- Toggle theme
- Search repositories
- Open settings

**Features**:
- Fuzzy search filtering
- Recent commands tracking
- Keyboard navigation (arrows, Enter, Escape)
- Command categories
- Keyboard shortcut display

---

### 4. RepositorySwitcher

**Purpose**: Dropdown for switching active repository

**Props**:
```typescript
interface RepositorySwitcherProps {
  repositories: Repository[];
  activeRepository: Repository | null;
  onSelect: (id: string) => void;
}
```

**Implementation Strategy**:
- Use **shadcn-ui** DropdownMenu component
- Use **magic-ui** subtle animation on open
- Custom repository icon based on source

**Repository Type**:
```typescript
interface Repository {
  id: string;
  name: string;
  source: 'github' | 'gitlab' | 'local';
  url?: string;
  lastUpdated: Date;
  status: 'ready' | 'indexing' | 'error';
}
```

**Features**:
- Search/filter repositories
- Display repository status badge
- Show last updated time
- Link to add new repository

---

### 5. ThemeProvider

**Purpose**: Theme management with system preference detection

**Implementation Strategy**:
- Use **shadcn-ui** theme system
- Custom hook `useTheme()`
- localStorage persistence
- System preference detection via `matchMedia`

**Theme Toggle**:
- Use **shadcn-ui** DropdownMenu
- Use **magic-ui** smooth color transitions
- Icons: Sun (light), Moon (dark), Monitor (system)

---

### 6. WorkbenchHeader

**Purpose**: Top header bar with global controls

**Props**:
```typescript
interface WorkbenchHeaderProps {
  onCommandPaletteOpen: () => void;
}
```

**Layout**:
```
[Logo] [RepositorySwitcher] ... [CommandTrigger] [ThemeToggle] [UserMenu]
```

**Implementation Strategy**:
- Use **shadcn-ui** Button, DropdownMenu
- Responsive: Hide logo text on mobile
- Sticky positioning

---

## Data Models

### Workbench State

```typescript
interface WorkbenchState {
  sidebar: {
    isOpen: boolean;
    isCollapsed: boolean;
    width: number;
  };
  commandPalette: {
    isOpen: boolean;
    searchQuery: string;
    selectedIndex: number;
  };
  theme: 'light' | 'dark' | 'system';
}
```

### Repository

```typescript
interface Repository {
  id: string;
  name: string;
  source: 'github' | 'gitlab' | 'local';
  url?: string;
  description?: string;
  language?: string;
  stars?: number;
  lastUpdated: Date;
  status: 'ready' | 'indexing' | 'error';
  stats?: {
    files: number;
    lines: number;
    size: number;
  };
}
```

### Command

```typescript
interface Command {
  id: string;
  label: string;
  description?: string;
  icon?: React.ComponentType;
  shortcut?: string[];
  action: () => void | Promise<void>;
  category: 'navigation' | 'actions' | 'settings';
  keywords?: string[];
}
```

---


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Sidebar State Persistence
*For any* sidebar state change (open/closed, collapsed/expanded), persisting to localStorage and then reloading the page should restore the exact same sidebar state.

**Validates: Requirements 1.6**

### Property 2: Theme Consistency
*For any* theme selection (light, dark, system), all UI components should render with consistent colors matching the selected theme without any mismatched elements.

**Validates: Requirements 5.1, 5.4**

### Property 3: Command Palette Keyboard Navigation
*For any* list of filtered commands, pressing arrow keys should cycle through all commands, and pressing Enter should execute the currently highlighted command.

**Validates: Requirements 3.7, 3.8**

### Property 4: Responsive Breakpoint Behavior
*For any* viewport width below 768px, the sidebar should automatically collapse, and for any width above 768px, the sidebar should respect the user's last manual state.

**Validates: Requirements 1.5, 6.1**

### Property 5: Repository Switcher Selection
*For any* repository selection, the active repository context should update immediately, and all components depending on repository context should reflect the new selection.

**Validates: Requirements 4.4**

### Property 6: Keyboard Shortcut Uniqueness
*For any* two different commands, they should not share the same keyboard shortcut combination.

**Validates: Requirements 7.1, 7.2, 7.3**

---

## Error Handling

### Sidebar State Errors

**Scenario**: localStorage is unavailable or corrupted
**Handling**: 
- Catch localStorage errors
- Fall back to default state (sidebar open, not collapsed)
- Log error to console
- Show toast notification if critical

### Repository Loading Errors

**Scenario**: API fails to fetch repositories
**Handling**:
- Display error state in RepositorySwitcher
- Show "Unable to load repositories" message
- Provide retry button
- Log error details

### Command Execution Errors

**Scenario**: Command action throws an error
**Handling**:
- Catch error in command executor
- Show error toast with message
- Log error with stack trace
- Keep command palette open for retry

### Theme Application Errors

**Scenario**: Theme fails to apply (CSS not loaded)
**Handling**:
- Fall back to light theme
- Log error
- Retry theme application after delay

---

## Testing Strategy

### Unit Tests

**Components to Test**:
- WorkbenchLayout: Sidebar toggle, responsive behavior
- CommandPalette: Search filtering, keyboard navigation
- RepositorySwitcher: Selection, filtering
- ThemeProvider: Theme switching, persistence

**Test Approach**:
- React Testing Library for component tests
- Mock Zustand stores
- Test keyboard events
- Test responsive behavior with viewport mocking

### Property-Based Tests

**Property Tests** (using fast-check):

1. **Sidebar State Round-Trip**
   - Generate random sidebar states
   - Persist to localStorage
   - Reload and verify state matches
   - **Validates Property 1**

2. **Theme Consistency**
   - Generate random theme selections
   - Apply theme
   - Query all themed elements
   - Verify all use correct theme colors
   - **Validates Property 2**

3. **Command Navigation**
   - Generate random command lists
   - Simulate arrow key presses
   - Verify selection cycles correctly
   - **Validates Property 3**

4. **Responsive Breakpoints**
   - Generate random viewport widths
   - Apply width
   - Verify sidebar state matches breakpoint rules
   - **Validates Property 4**

5. **Keyboard Shortcut Uniqueness**
   - Generate command list
   - Extract all shortcuts
   - Verify no duplicates exist
   - **Validates Property 6**

**Configuration**: Minimum 100 iterations per property test

### Integration Tests

**Workflows to Test**:
1. User opens app → sidebar loads in correct state
2. User toggles sidebar → state persists across reload
3. User opens command palette → executes command → palette closes
4. User switches repository → context updates everywhere
5. User changes theme → all components update

### Visual Regression Tests

**Scenarios**:
- Sidebar open vs collapsed
- Light vs dark theme
- Mobile vs desktop layout
- Command palette open
- Repository switcher dropdown

---

## Performance Considerations

### Bundle Size

**Optimization Strategies**:
- Lazy load route components
- Tree-shake unused UI components
- Use dynamic imports for heavy dependencies
- Target: < 200KB initial bundle (gzipped)

### Animation Performance

**Optimization Strategies**:
- Use CSS transforms (not width/height)
- Use `will-change` for animated elements
- Debounce resize events
- Target: 60fps during animations

### State Updates

**Optimization Strategies**:
- Use Zustand selectors to prevent unnecessary re-renders
- Memoize expensive computations
- Debounce command palette search (150ms)
- Throttle scroll events

### Accessibility

**WCAG 2.1 AA Compliance**:
- Keyboard navigation for all interactive elements
- Focus indicators visible
- Color contrast ratios ≥ 4.5:1
- Screen reader announcements for state changes
- ARIA labels for icon-only buttons

---

## Implementation Notes

### MCP Server Usage

**magic-mcp** (`@21st-dev/magic-mcp`):
- Generate initial WorkbenchLayout component structure
- Generate CommandPalette component shell
- Generate responsive layout utilities

**shadcn-ui** (`@jpisnice/shadcn-ui-mcp-server`):
- Command component for command palette
- Sheet component for sidebar
- DropdownMenu for repository switcher
- Button, Tooltip, Badge components

**magic-ui** (`@magicuidesign/mcp`):
- Smooth sidebar slide animation
- Command palette spotlight entrance
- Theme transition effects
- Subtle hover effects on nav items

### Technology Stack

**Core**:
- React 18
- TypeScript 5
- Vite 5
- TanStack Router

**State Management**:
- Zustand (workbench, repository, command, theme stores)

**UI Components**:
- shadcn/ui (via MCP)
- magic-ui (via MCP)
- lucide-react (icons)
- cmdk (command palette base)

**Styling**:
- Tailwind CSS
- CSS Modules (for complex animations)
- Framer Motion (strategic animations)

**Testing**:
- Vitest
- React Testing Library
- fast-check (property-based testing)

---

## Migration from Existing Code

### Preserve

- `src/routes/_auth.tsx` - Enhance with WorkbenchLayout
- `src/features/auth/` - Keep all auth code
- `src/app/providers/AuthProvider.tsx` - Keep as-is

### Create New

- `src/layouts/WorkbenchLayout.tsx`
- `src/layouts/WorkbenchSidebar.tsx`
- `src/layouts/WorkbenchHeader.tsx`
- `src/components/CommandPalette.tsx`
- `src/components/RepositorySwitcher.tsx`
- `src/components/ThemeProvider.tsx`
- `src/stores/workbench.ts`
- `src/stores/repository.ts`
- `src/stores/command.ts`
- `src/stores/theme.ts`

### Update

- `src/routes/__root.tsx` - Add ThemeProvider
- `src/routes/_auth.tsx` - Wrap with WorkbenchLayout
- `src/main.tsx` - Add global keyboard listeners

---

## Future Enhancements

**Phase 2+ Integration Points**:
- Command palette will gain commands from each new feature
- Sidebar will add badges for notifications
- Repository switcher will show indexing progress
- Header will add breadcrumbs for deep navigation

**Potential Improvements**:
- Customizable sidebar order
- Pinned commands in palette
- Recent repositories quick access
- Workspace presets (save layout configurations)
- Multi-panel layouts
