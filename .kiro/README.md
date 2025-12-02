# Kiro Configuration

This directory contains Kiro IDE configuration and specifications.

## Directory Structure

```
.kiro/
├── specs/              # Feature specifications
│   ├── backend/        # Backend (Python/FastAPI) specs (21)
│   ├── frontend/       # Frontend (React/TypeScript) specs (6)
│   └── README.md       # Specs documentation
│
├── settings/           # Kiro IDE settings
│   └── mcp.json        # Model Context Protocol config
│
└── README.md           # This file
```

## Specifications

Neo Alexandria 2.0 uses **Spec-Driven Development** for complex features.

### What is a Spec?

A spec is a structured way to plan and implement features:
1. **Requirements** - User stories and acceptance criteria
2. **Design** - Technical architecture and implementation details
3. **Tasks** - Step-by-step implementation checklist

### Spec Categories

- **Backend** (21 specs) - API, database, ML, testing, architecture
- **Frontend** (6 specs) - UI components, visual design, UX

### Working with Specs

```bash
# View all specs
ls .kiro/specs/backend/
ls .kiro/specs/frontend/

# Read documentation
cat .kiro/specs/README.md
cat .kiro/specs/backend/README.md
cat .kiro/specs/frontend/README.md

# Execute tasks
# 1. Open tasks.md in Kiro IDE
# 2. Click "Start task" next to any task
# 3. Follow Kiro's guidance
```

## Settings

### MCP (Model Context Protocol)

Configure external tools and services in `.kiro/settings/mcp.json`.

Example:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package-name"],
      "disabled": false
    }
  }
}
```

## Related Documentation

- [Specs Overview](.kiro/specs/README.md)
- [Backend Specs](.kiro/specs/backend/README.md)
- [Frontend Specs](.kiro/specs/frontend/README.md)
- [Backend Developer Guide](../backend/docs/DEVELOPER_GUIDE.md)
- [Frontend README](../frontend/README.md)
