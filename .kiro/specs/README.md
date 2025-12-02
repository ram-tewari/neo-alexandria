# Neo Alexandria 2.0 - Kiro Specs

This directory contains all feature specifications organized by domain.

## Directory Structure

```
.kiro/specs/
├── backend/          # Backend (Python/FastAPI) specifications
├── frontend/         # Frontend (React/TypeScript) specifications
└── README.md         # This file
```

## Backend Specs (21 specs)

Backend specifications cover API development, database, ML/AI, testing, and architecture.

**Location**: `.kiro/specs/backend/`

### Core Features
- `phase7-collection-management` - User collections and organization
- `phase7-5-annotation-system` - Text highlighting and notes
- `phase8-three-way-hybrid-search` - Advanced search (FTS5 + Vector + Sparse)
- `phase8-5-ml-classification` - ML-based taxonomy classification
- `phase9-quality-assessment` - Resource quality scoring
- `phase10-advanced-graph-intelligence` - Knowledge graph and relationships
- `phase11-hybrid-recommendation-engine` - Personalized recommendations
- `phase13-postgresql-migration` - PostgreSQL database support

### Architecture & Refactoring
- `phase10-5-code-standardization` - Code quality and standards
- `phase12-fowler-refactoring` - Martin Fowler refactoring patterns
- `phase12-5-event-driven-architecture` - Event system and hooks
- `phase13-5-vertical-slice-refactor` - Modular monolith architecture

### ML & Training
- `ml-model-training` - ML model training infrastructure
- `production-ml-training` - Production ML pipelines
- `phase11-5-ml-benchmarking` - ML performance benchmarking

### Testing
- `test-suite-critical-fixes` - Critical test fixes
- `test-suite-fixes` - General test improvements
- `test-suite-fixes-phase2` - Additional test fixes
- `test-suite-stabilization` - Test stability improvements
- `phase12-6-test-suite-fixes` - Phase 12 test fixes

### Integration
- `frontend-backend-integration` - API integration with frontend

## Frontend Specs (6 specs)

Frontend specifications cover UI/UX, components, and visual design.

**Location**: `.kiro/specs/frontend/`

### UI Components
- `command-palette` - Command palette (Cmd+K) interface
- `modular-sidebar-system` - Modular sidebar architecture
- `sidebar-redesign` - Sidebar UX improvements

### Visual Design
- `purple-theme-visual-enhancement` - Purple theme and styling
- `neo-alexandria-frontend-enhancements` - General UI enhancements
- `neo-alexandria-frontend-rebuild` - Frontend architecture rebuild

## Working with Specs

### Creating a New Spec

1. Determine if it's backend or frontend
2. Create directory in appropriate folder:
   ```bash
   mkdir .kiro/specs/backend/my-new-feature
   # or
   mkdir .kiro/specs/frontend/my-new-feature
   ```
3. Create spec files:
   - `requirements.md` - User stories and acceptance criteria
   - `design.md` - Technical design and architecture
   - `tasks.md` - Implementation task list

### Executing Tasks

1. Open the `tasks.md` file in Kiro IDE
2. Click "Start task" next to any task item
3. Kiro will guide you through implementation

### Spec Workflow

```
Requirements → Design → Tasks → Implementation
     ↓            ↓        ↓           ↓
  Review      Review   Review      Execute
```

## Naming Conventions

- **Phase specs**: `phaseX-feature-name` (e.g., `phase13-postgresql-migration`)
- **Feature specs**: `feature-name` (e.g., `command-palette`)
- **Fix specs**: `fix-type-description` (e.g., `test-suite-fixes`)

## Related Documentation

- [Backend Developer Guide](../../backend/docs/DEVELOPER_GUIDE.md)
- [Backend Architecture](../../backend/docs/ARCHITECTURE_DIAGRAM.md)
- [Frontend README](../../frontend/README.md)
