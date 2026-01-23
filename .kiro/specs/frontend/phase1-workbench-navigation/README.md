# Phase 1: Core Workbench & Navigation

**Status**: Ready for Implementation
**Approach**: Option C - Hybrid Power
**Complexity**: ⭐⭐⭐ Medium

## Overview

Phase 1 establishes the foundational "Command Center" layout for Neo Alexandria's "Second Brain" interface. This phase creates the primary navigation structure, global command palette, and responsive workspace layout that all future features will build upon.

## What This Phase Delivers

### Core Features

1. **Workbench Layout**
   - Collapsible sidebar navigation
   - Responsive header bar
   - Adaptive content area
   - Mobile-friendly design

2. **Sidebar Navigation**
   - Six module links (Repositories, Cortex, Library, Planner, Wiki, Ops)
   - Active route highlighting
   - Icon-only collapsed mode
   - Smooth animations

3. **Global Command Palette**
   - Keyboard-driven (Cmd+K / Ctrl+K)
   - Fuzzy search filtering
   - Command categories
   - Recent commands tracking

4. **Repository Switcher**
   - Dropdown for repository selection
   - Repository status indicators
   - Empty state handling

5. **Theme System**
   - Light / Dark / System modes
   - Smooth transitions
   - System preference detection
   - Persistent preferences

6. **Keyboard Navigation**
   - Comprehensive shortcuts
   - Visible focus indicators
   - Accessible to screen readers

## Implementation Strategy

### Hybrid Power Approach (Option C)

**Component Generation**:
- Use **magic-mcp** (`@21st-dev/magic-mcp`) to generate initial component structures
- Saves time on boilerplate while maintaining control

**Core UI Primitives**:
- Use **shadcn-ui** (`@jpisnice/shadcn-ui-mcp-server`) for reliable components
- Command, Sheet, DropdownMenu, Button, Tooltip, Badge

**Strategic Polish**:
- Use **magic-ui** (`@magicuidesign/mcp`) for animations and effects
- Sidebar slide animation, command palette spotlight, theme transitions

### Technology Stack

**Core**:
- React 18 + TypeScript 5
- Vite 5
- TanStack Router

**State Management**:
- Zustand (4 stores: workbench, theme, repository, command)

**UI Components**:
- shadcn/ui (via MCP)
- magic-ui (via MCP)
- lucide-react (icons)
- cmdk (command palette)

**Styling**:
- Tailwind CSS
- Framer Motion (strategic animations)

**Testing**:
- Vitest + React Testing Library
- fast-check (property-based testing)

## File Structure

```
.kiro/specs/frontend/phase1-workbench-navigation/
├── README.md (this file)
├── requirements.md (8 requirements, 40+ acceptance criteria)
├── design.md (architecture, components, properties)
└── tasks.md (12 top-level tasks, 35+ sub-tasks)
```

## Dependencies

### Backend APIs Needed

✅ **Already Available**:
- Authentication endpoints
- User profile endpoints

⚠️ **Minimal New Work**:
- Repository listing endpoint (GET /api/repositories)
- Repository selection endpoint (POST /api/repositories/{id}/select)

### Frontend Dependencies

**New Packages to Install**:
```bash
npm install zustand cmdk framer-motion
npm install -D fast-check
```

**MCP Servers** (already configured):
- `@jpisnice/shadcn-ui-mcp-server`
- `@magicuidesign/mcp`
- `@21st-dev/magic-mcp`

## Key Design Decisions

### Why Zustand?

- Lightweight (< 1KB)
- No boilerplate
- Easy to test
- Perfect for this scale

### Why cmdk?

- Battle-tested command palette
- Excellent keyboard handling
- Fuzzy search built-in
- Used by Vercel, Linear, etc.

### Why Hybrid Power?

- **Professional**: Clean, polished, production-ready
- **Performant**: Strategic animations, not overdone
- **Balanced**: Leverages all 3 MCP servers effectively
- **Maintainable**: Clear component boundaries

## Testing Strategy

### Property-Based Tests (6 properties)

1. Sidebar state persistence round-trip
2. Theme consistency across components
3. Command palette keyboard navigation
4. Responsive breakpoint behavior
5. Repository switcher selection
6. Keyboard shortcut uniqueness

**Configuration**: 100 iterations per property test

### Unit Tests

- Component rendering
- User interactions
- State updates
- Keyboard events
- Responsive behavior

### Integration Tests

- Full user workflows
- Cross-component interactions
- Route navigation
- Theme switching

## Performance Targets

- **Initial render**: < 100ms
- **Sidebar toggle**: < 200ms animation
- **Command palette open**: < 50ms
- **Animation frame rate**: 60fps
- **Initial bundle**: < 200KB (gzipped)

## Accessibility

**WCAG 2.1 AA Compliance**:
- ✅ Keyboard navigation for all features
- ✅ Visible focus indicators
- ✅ Color contrast ≥ 4.5:1
- ✅ Screen reader support
- ✅ Touch-friendly targets (44x44px minimum)

## Migration Notes

### Preserve from Existing Code

- ✅ `src/routes/_auth.tsx` - Enhance with WorkbenchLayout
- ✅ `src/features/auth/` - Keep all auth code
- ✅ `src/app/providers/AuthProvider.tsx` - Keep as-is
- ✅ `src/components/ui/` - Enhance with new MCP components

### New Files to Create

**Layouts**:
- `src/layouts/WorkbenchLayout.tsx`
- `src/layouts/WorkbenchSidebar.tsx`
- `src/layouts/WorkbenchHeader.tsx`

**Components**:
- `src/components/CommandPalette.tsx`
- `src/components/RepositorySwitcher.tsx`
- `src/components/ThemeProvider.tsx`
- `src/components/ThemeToggle.tsx`

**Stores**:
- `src/stores/workbench.ts`
- `src/stores/repository.ts`
- `src/stores/command.ts`
- `src/stores/theme.ts`

**Routes** (placeholders):
- `src/routes/_auth.repositories.tsx`
- `src/routes/_auth.cortex.tsx`
- `src/routes/_auth.library.tsx`
- `src/routes/_auth.planner.tsx`
- `src/routes/_auth.wiki.tsx`
- `src/routes/_auth.ops.tsx`

## Next Steps

1. **Review the spec documents**:
   - `requirements.md` - User stories and acceptance criteria
   - `design.md` - Architecture and component details
   - `tasks.md` - Implementation checklist

2. **Start implementation**:
   - Begin with Task 1 (setup dependencies)
   - Work through tasks sequentially
   - Mark tasks complete as you go

3. **Use MCP servers**:
   - Generate components with magic-mcp
   - Add UI primitives with shadcn-ui
   - Polish with magic-ui animations

4. **Test as you build**:
   - Write property tests for core behaviors
   - Add unit tests for components
   - Run tests frequently

## Future Integration Points

**Phase 2+ will add**:
- More commands to the command palette
- Notification badges on sidebar items
- Breadcrumbs in the header
- Progress indicators in repository switcher
- Additional keyboard shortcuts

## Questions?

- Check `requirements.md` for detailed acceptance criteria
- Check `design.md` for component specifications
- Check `tasks.md` for implementation steps
- Ask the user if anything is unclear!

---

**Ready to start building?** Begin with Task 1 in `tasks.md`!
