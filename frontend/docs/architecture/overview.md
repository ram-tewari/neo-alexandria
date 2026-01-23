# Architecture Overview

High-level system architecture for Neo Alexandria 2.0 Frontend.

> **Last Updated**: Phase 1 Complete - Core Workbench & Navigation

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Technology Stack](#technology-stack)
3. [Component Architecture](#component-architecture)
4. [State Management](#state-management)
5. [Routing Strategy](#routing-strategy)
6. [Design Patterns](#design-patterns)
7. [Key Architectural Principles](#key-architectural-principles)

---

## High-Level Architecture

### "Second Brain" Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - FRONTEND ARCHITECTURE               │
│                         "Second Brain" for Code                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         React Application                            │   │
│  │                    (React 18 + TypeScript 5)                         │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                   │                                         │
│                                   │ Routing                                 │
│                                   ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      TanStack Router                                 │   │
│  │                    (Type-safe routing)                               │   │
│  └────────────────────────────────┬─────────────────────────────────────┘   │
│                                   │                                         │
│                                   │ Route Tree                              │
│                                   ▼                                         │
│       ┌───────────────────────────┼───────────────────────────────────┐     │
│       │                           │                                   │     │
│       ▼                           ▼                                   ▼     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Login   │  │Reposito- │  │  Cortex  │  │ Library  │  │ Planner  │     │
│  │  Route   │  │  ries    │  │  Route   │  │  Route   │  │  Route   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │           │
│       │             │             │             │             │           │
│  ┌──────────┐  ┌──────────┐                                               │
│  │   Wiki   │  │   Ops    │                                               │
│  │  Route   │  │  Route   │                                               │
│  └────┬─────┘  └────┬─────┘                                               │
│       │             │                                                     │
│       └─────────────┴──────────────────────────────────────┐              │
│                                                             │              │
│                                                             ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Workbench Layout                               │   │
│  │  ┌──────────────┐  ┌──────────────────────────────────────────┐     │   │
│  │  │   Sidebar    │  │           Content Area                   │     │   │
│  │  │              │  │                                          │     │   │
│  │  │ • Repos      │  │  Route-specific content                  │     │   │
│  │  │ • Cortex     │  │  (Repositories, Cortex, Library, etc.)   │     │   │
│  │  │ • Library    │  │                                          │     │   │
│  │  │ • Planner    │  │                                          │     │   │
│  │  │ • Wiki       │  │                                          │     │   │
│  │  │ • Ops        │  │                                          │     │   │
│  │  └──────────────┘  └──────────────────────────────────────────┘     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                        Header                                │   │   │
│  │  │  • Repository Switcher  • Theme Toggle  • Command Palette   │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      State Management (Zustand)                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │Workbench │  │  Theme   │  │Repository│  │ Command  │            │   │
│  │  │  Store   │  │  Store   │  │  Store   │  │  Store   │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Global Components                              │   │
│  │  • CommandPalette (Cmd+K)                                           │   │
│  │  • ThemeProvider (Light/Dark/System)                                │   │
│  │  • Global Keyboard Handler                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Framework

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI Library | React 18 | Component-based UI |
| Language | TypeScript 5 | Type safety |
| Build Tool | Vite 5 | Fast dev server & builds |
| Routing | TanStack Router | Type-safe routing |

### State Management

| Tool | Purpose |
|------|---------|
| Zustand | Client state (UI, preferences) |
| TanStack Query | Server state (planned) |
| localStorage | Persistence |

### UI Components

| Library | Purpose |
|---------|---------|
| shadcn/ui | Core UI primitives (via MCP) |
| magic-ui | Animations & effects (via MCP) |
| lucide-react | Icon library |
| cmdk | Command palette |
| Framer Motion | Animations |

### Styling

| Tool | Purpose |
|------|---------|
| Tailwind CSS | Utility-first CSS |
| CSS Modules | Component-scoped styles |
| PostCSS | CSS processing |

### Testing

| Tool | Purpose |
|------|---------|
| Vitest | Unit testing |
| React Testing Library | Component testing |
| fast-check | Property-based testing |

---

## Component Architecture

### Component Hierarchy

```
App
├── ThemeProvider
│   └── Router
│       ├── __root (Root Layout)
│       │   ├── login (Login Route)
│       │   └── _auth (Auth Layout)
│       │       ├── WorkbenchLayout
│       │       │   ├── WorkbenchHeader
│       │       │   │   ├── RepositorySwitcher
│       │       │   │   ├── ThemeToggle
│       │       │   │   └── CommandPalette Trigger
│       │       │   ├── WorkbenchSidebar
│       │       │   │   └── Navigation Items
│       │       │   └── Content Area
│       │       │       └── Route-specific content
│       │       └── CommandPalette (Global)
│       └── auth.callback (OAuth Callback)
```

### Component Categories

**1. Layouts** (`src/layouts/`)
- `WorkbenchLayout.tsx` - Main container
- `WorkbenchSidebar.tsx` - Navigation sidebar
- `WorkbenchHeader.tsx` - Top header bar
- `navigation-config.ts` - Navigation configuration

**2. Components** (`src/components/`)
- `CommandPalette.tsx` - Global command interface
- `RepositorySwitcher.tsx` - Repository dropdown
- `ThemeToggle.tsx` - Theme switcher

**3. UI Primitives** (`src/components/ui/`)
- `command.tsx` - Command primitive (shadcn)
- `tooltip.tsx` - Tooltip primitive (shadcn)
- `button.tsx` - Button primitive (shadcn)
- `dropdown-menu.tsx` - Dropdown primitive (shadcn)

**4. Providers** (`src/app/providers/`)
- `ThemeProvider.tsx` - Theme context
- `AuthProvider.tsx` - Auth context (preserved)
- `QueryProvider.tsx` - TanStack Query (planned)

**5. Routes** (`src/routes/`)
- `__root.tsx` - Root layout
- `login.tsx` - Login page (bypassed)
- `_auth.tsx` - Protected route wrapper
- `_auth.repositories.tsx` - Repositories route
- `_auth.cortex.tsx` - Cortex route
- `_auth.library.tsx` - Library route
- `_auth.planner.tsx` - Planner route
- `_auth.wiki.tsx` - Wiki route
- `_auth.ops.tsx` - Ops route

---

## State Management

### Zustand Stores

**1. Workbench Store** (`stores/workbench.ts`)
```typescript
interface WorkbenchState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}
```
- Manages sidebar collapsed state
- Persists to localStorage
- Used by WorkbenchLayout and WorkbenchSidebar

**2. Theme Store** (`stores/theme.ts`)
```typescript
interface ThemeState {
  theme: 'light' | 'dark' | 'system';
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}
```
- Manages theme selection
- Detects system preference
- Persists to localStorage
- Auto-updates on system change

**3. Repository Store** (`stores/repository.ts`)
```typescript
interface RepositoryState {
  repositories: Repository[];
  selectedRepository: Repository | null;
  selectRepository: (id: string) => void;
}
```
- Manages repository list (mock data)
- Tracks selected repository
- Used by RepositorySwitcher

**4. Command Store** (`stores/command.ts`)
```typescript
interface CommandState {
  isOpen: boolean;
  recentCommands: string[];
  open: () => void;
  close: () => void;
  addRecentCommand: (command: string) => void;
}
```
- Manages command palette state
- Tracks recent commands
- Used by CommandPalette

### State Flow

```
User Action
    ↓
Component Event Handler
    ↓
Zustand Store Action
    ↓
State Update
    ↓
Component Re-render
    ↓
localStorage Sync (if persistent)
```

---

## Routing Strategy

### TanStack Router

**File-based routing** with type safety:

```
src/routes/
├── __root.tsx              # Root layout
├── login.tsx               # /login
├── auth.callback.tsx       # /auth/callback
└── _auth.tsx               # Protected routes
    ├── _auth.repositories.tsx  # /repositories
    ├── _auth.cortex.tsx        # /cortex
    ├── _auth.library.tsx       # /library
    ├── _auth.planner.tsx       # /planner
    ├── _auth.wiki.tsx          # /wiki
    └── _auth.ops.tsx           # /ops
```

### Route Tree

```
/
├── login
├── auth/callback
└── _auth (layout)
    ├── repositories
    ├── cortex
    ├── library
    ├── planner
    ├── wiki
    └── ops
```

### Navigation Flow

```
User clicks sidebar item
    ↓
TanStack Router navigates
    ↓
Route component loads
    ↓
Content area updates
    ↓
Sidebar highlights active route
```

---

## Design Patterns

### 1. Compound Components

**Example**: WorkbenchLayout
```typescript
<WorkbenchLayout>
  <WorkbenchHeader />
  <WorkbenchSidebar />
  <Outlet /> {/* Route content */}
</WorkbenchLayout>
```

### 2. Custom Hooks

**Example**: useGlobalKeyboard
```typescript
const useGlobalKeyboard = () => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === 'k') {
        commandStore.open();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);
};
```

### 3. Provider Pattern

**Example**: ThemeProvider
```typescript
<ThemeProvider>
  <App />
</ThemeProvider>
```

### 4. Render Props

**Example**: CommandPalette
```typescript
<Command.Item onSelect={() => navigate('/repositories')}>
  {({ selected }) => (
    <div className={selected ? 'bg-accent' : ''}>
      Repositories
    </div>
  )}
</Command.Item>
```

### 5. Composition

**Example**: UI Components
```typescript
<DropdownMenu>
  <DropdownMenuTrigger>
    <Button>Open</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Item 1</DropdownMenuItem>
    <DropdownMenuItem>Item 2</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Key Architectural Principles

### 1. Component Isolation

**Principle**: Components should be self-contained and reusable

**Example**:
- CommandPalette doesn't depend on WorkbenchLayout
- ThemeToggle works anywhere
- RepositorySwitcher is standalone

### 2. Single Responsibility

**Principle**: Each component has one clear purpose

**Example**:
- WorkbenchLayout: Container
- WorkbenchSidebar: Navigation
- WorkbenchHeader: Top controls
- CommandPalette: Global commands

### 3. Composition Over Inheritance

**Principle**: Build complex UIs by composing simple components

**Example**:
```typescript
<WorkbenchLayout>
  <WorkbenchHeader>
    <RepositorySwitcher />
    <ThemeToggle />
  </WorkbenchHeader>
  <WorkbenchSidebar />
  <Outlet />
</WorkbenchLayout>
```

### 4. Unidirectional Data Flow

**Principle**: Data flows down, events flow up

**Example**:
```
Zustand Store (State)
    ↓ Props
Component
    ↓ Events
Store Actions
    ↓ State Update
Component Re-render
```

### 5. Separation of Concerns

**Principle**: Separate UI, logic, and state

**Example**:
- UI: React components
- Logic: Custom hooks
- State: Zustand stores
- Styling: Tailwind CSS

### 6. Progressive Enhancement

**Principle**: Core functionality works, enhancements add polish

**Example**:
- Sidebar works without animations
- Command palette works without fuzzy search
- Theme works without system detection

### 7. Accessibility First

**Principle**: Build accessible by default

**Example**:
- Keyboard navigation for all features
- ARIA labels on icon-only buttons
- Focus indicators
- Screen reader support

### 8. Performance Optimization

**Principle**: Optimize for perceived performance

**Example**:
- Lazy loading routes
- CSS transforms for animations
- Zustand selectors to prevent re-renders
- Code splitting with Vite

---

## Future Architecture

### Phase 2: Living Code Editor

**New Components**:
- Monaco Editor wrapper
- Annotation gutter
- Quality badge overlay
- Hover card system

**New State**:
- Editor store (cursor, selection)
- Annotation store (highlights, notes)
- Quality store (scores, badges)

### Phase 3: Living Library

**New Components**:
- PDF viewer
- Document grid
- Equation drawer
- Table drawer

**New State**:
- Library store (PDFs, docs)
- Document store (current doc)

### Phase 4: Cortex/Knowledge Base

**New Components**:
- Graph visualization (React Flow)
- Node detail panel
- Hypothesis mode UI

**New State**:
- Graph store (nodes, edges)
- Hypothesis store (contradictions, connections)

### Phase 5-8

See [Frontend Roadmap](../../../.kiro/specs/frontend/ROADMAP.md) for details

---

## Related Documentation

- [Routing](routing.md) - TanStack Router details
- [State Management](state-management.md) - Zustand stores
- [Component Patterns](component-patterns.md) - Component design
- [Frontend Roadmap](../../../.kiro/specs/frontend/ROADMAP.md)
- [Phase 1 Spec](../../../.kiro/specs/frontend/phase1-workbench-navigation/)

---

**Last Updated**: January 22, 2026
**Phase**: Phase 1 Complete
**Next**: Phase 2 - Living Code Editor
