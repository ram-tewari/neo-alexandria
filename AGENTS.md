# Agent Context Management

## Purpose

This document provides routing rules for AI agents working with Neo Alexandria 2.0. It ensures efficient context usage and points to the right documentation.

## Token Hygiene Rules

1. **Never load entire files** unless explicitly needed for the current task
2. **Use targeted reads** with line ranges when possible
3. **Reference documentation** by path rather than loading it
4. **Close completed specs** - archive or mark as done when features are implemented
5. **Rotate context** - only keep active work in focus

## Documentation Structure

```
AGENTS.md (this file)          # Routing and hygiene rules
.kiro/steering/
  ├── product.md               # Product vision and goals
  ├── tech.md                  # Tech stack and constraints
  └── structure.md             # Repo map and truth sources
.kiro/specs/
  ├── [feature-name]/          # Active feature specs
  │   ├── requirements.md
  │   ├── design.md
  │   └── tasks.md
  └── README.md                # Spec organization
backend/docs/
  ├── index.md                 # Documentation index
  ├── api/                     # API reference (split by domain)
  ├── architecture/            # System architecture
  └── guides/                  # Developer guides
frontend/                      # Frontend-specific docs
```

## Finding the Right Documentation

### For Product Questions
→ Read `.kiro/steering/product.md`

### For Tech Stack Questions
→ Read `.kiro/steering/tech.md`

### For Repo Navigation
→ Read `.kiro/steering/structure.md`

### For Feature Work
→ Read `.kiro/specs/[feature-name]/requirements.md` and `design.md`

### For API Documentation
→ Read `backend/docs/index.md` then navigate to specific domain
→ Example: `backend/docs/api/search.md` for search endpoints

### For Architecture Details
→ Read `backend/docs/architecture/overview.md`
→ Example: `backend/docs/architecture/database.md` for schema

### For Development Guides
→ Read `backend/docs/guides/setup.md` for getting started
→ Example: `backend/docs/guides/testing.md` for test strategies

## Working with Specs

### Active Specs Only
Only load specs that are:
- Currently being worked on
- Explicitly requested by the user
- Needed for context on current task

### Completed Specs
Specs in `.kiro/specs/` that are fully implemented should be:
- Marked as complete in their README
- Referenced by path only (not loaded)
- Archived if no longer relevant

### Creating New Specs
Follow the spec workflow:
1. Create `.kiro/specs/[feature-name]/` directory
2. Write `requirements.md` first
3. Then `design.md`
4. Finally `tasks.md`
5. Execute tasks incrementally

## Context Budget Guidelines

- **Small tasks** (<5 files): Load files directly
- **Medium tasks** (5-15 files): Load selectively, reference others
- **Large tasks** (>15 files): Use structure.md as map, load only what's needed
- **Exploratory work**: Start with structure.md, drill down as needed

## Quick Reference

| Need | Read |
|------|------|
| What is this project? | `.kiro/steering/product.md` |
| What tech do we use? | `.kiro/steering/tech.md` |
| Where is X located? | `.kiro/steering/structure.md` |
| How do I implement Y? | `.kiro/specs/[feature]/design.md` |
| What's the API? | `backend/docs/index.md` → `api/` |
| What's the architecture? | `backend/docs/architecture/overview.md` |
| How do I set up dev env? | `backend/docs/guides/setup.md` |
| How do I test? | `backend/docs/guides/testing.md` |

## Anti-Patterns to Avoid

❌ Loading all specs at once
❌ Reading entire backend/README.md for simple questions
❌ Loading documentation "just in case"
❌ Keeping completed spec context open
❌ Reading files without a specific purpose

✅ Load only what's needed for current task
✅ Use structure.md as a map
✅ Reference docs by path
✅ Close completed work
✅ Ask user if unsure what's needed
