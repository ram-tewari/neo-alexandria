# Kiro Configuration

This directory contains Kiro IDE configuration and specifications.

## Directory Structure

```
.kiro/
├── steering/           # Project steering documentation
│   ├── product.md      # Product vision and goals
│   ├── tech.md         # Tech stack and constraints
│   └── structure.md    # Repository map and truth sources
│
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

## Steering Documentation

Project-level context and guidelines for AI agents and developers.

### Quick Reference

| Need | Read |
|------|------|
| What is this project? | `steering/product.md` |
| What tech do we use? | `steering/tech.md` |
| Where is X located? | `steering/structure.md` |

### Steering Files

- **`product.md`** - Product vision, users, goals, and non-goals
- **`tech.md`** - Tech stack, constraints, and common commands
- **`structure.md`** - Repository map and documentation hierarchy

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

See [Specs README](specs/README.md) for detailed guidance.

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

- [Agent Context Rules](../AGENTS.md) - Token hygiene and routing
- [Steering: Product](steering/product.md) - Product vision and goals
- [Steering: Tech](steering/tech.md) - Tech stack and constraints
- [Steering: Structure](steering/structure.md) - Repository map
- [Specs Overview](specs/README.md) - Feature specifications
- [Backend Developer Guide](../backend/docs/DEVELOPER_GUIDE.md)
- [Frontend README](../frontend/README.md)
