# Planning API

AI-powered multi-hop planning and architecture document parsing endpoints.

## Overview

The Planning API provides functionality for:
- Multi-hop task planning with dependency tracking
- Iterative plan refinement
- Architecture document parsing
- Component and relationship extraction
- Design pattern recognition
- Gap analysis between documentation and implementation

## Endpoints

### POST /api/planning/generate

**Phase 20** - Generate a multi-step plan for a task.

Creates a structured plan with dependencies using LLM-powered reasoning.

**Request Body:**
```json
{
  "task_description": "Implement user authentication system",
  "context": {
    "existing_modules": ["users", "database"],
    "constraints": ["Must use JWT tokens", "Support OAuth2"]
  },
  "max_steps": 10
}
```

**Parameters:**
- `task_description` (required): Description of the task to plan
- `context` (optional): Additional context for planning
- `max_steps` (optional): Maximum number of steps (default: 10)

**Response:**
```json
{
  "plan_id": "plan-uuid-1",
  "task_description": "Implement user authentication system",
  "steps": [
    {
      "step_number": 1,
      "description": "Create User model with password hashing",
      "dependencies": [],
      "estimated_effort": "2 hours"
    },
    {
      "step_number": 2,
      "description": "Implement JWT token generation",
      "dependencies": [1],
      "estimated_effort": "1 hour"
    }
  ],
  "status": "draft",
  "created_at": "2024-01-01T10:00:00Z"
}
```

**Performance:**
- Response time: <3s per planning step (P95)
- Supports up to 20 steps per plan
- Validates dependency DAG (no cycles)

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/planning/generate" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Implement user authentication system", "max_steps": 10}'
```

**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5

---

### PUT /api/planning/{plan_id}/refine

**Phase 20** - Refine an existing plan with feedback.

Iteratively improves a plan based on user feedback or new context.

**Path Parameters:**
- `plan_id` (required): Plan ID (UUID)

**Request Body:**
```json
{
  "feedback": "Add error handling to step 2",
  "context_updates": {
    "new_constraint": "Must support 2FA"
  }
}
```

**Parameters:**
- `feedback` (required): User feedback for refinement
- `context_updates` (optional): Updated context information

**Response:**
```json
{
  "plan_id": "plan-uuid-1",
  "task_description": "Implement user authentication system",
  "steps": [
    {
      "step_number": 1,
      "description": "Create User model with password hashing",
      "dependencies": [],
      "estimated_effort": "2 hours"
    },
    {
      "step_number": 2,
      "description": "Implement JWT token generation with error handling",
      "dependencies": [1],
      "estimated_effort": "1.5 hours"
    },
    {
      "step_number": 3,
      "description": "Add 2FA support",
      "dependencies": [2],
      "estimated_effort": "3 hours"
    }
  ],
  "status": "refined",
  "updated_at": "2024-01-01T10:05:00Z",
  "refinement_count": 1
}
```

**Example:**
```bash
curl -X PUT "http://127.0.0.1:8000/api/planning/plan-uuid-1/refine" \
  -H "Content-Type: application/json" \
  -d '{"feedback": "Add error handling to step 2"}'
```

**Requirements:** 7.2, 7.3, 7.5

---

### GET /api/planning/{plan_id}

**Phase 20** - Retrieve a specific plan by ID.

**Path Parameters:**
- `plan_id` (required): Plan ID (UUID)

**Response:**
```json
{
  "plan_id": "plan-uuid-1",
  "task_description": "Implement user authentication system",
  "steps": [...],
  "status": "draft",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z",
  "refinement_count": 1,
  "context": {
    "existing_modules": ["users", "database"],
    "constraints": ["Must use JWT tokens", "Support OAuth2", "Must support 2FA"]
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/planning/plan-uuid-1"
```

**Requirements:** 7.1, 7.5

---

### POST /api/planning/parse-architecture

**Phase 20** - Parse an architecture document and extract components.

Analyzes architecture documentation to extract components, relationships, design patterns, and identify gaps with actual implementation.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "compare_with_codebase": true
}
```

**Parameters:**
- `resource_id` (required): Resource ID (UUID) of the architecture document
- `compare_with_codebase` (optional): Compare with actual codebase (default: true)

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "components": [
    {
      "name": "AuthenticationService",
      "type": "service",
      "description": "Handles user authentication and JWT tokens",
      "responsibilities": ["Token generation", "Password validation"]
    }
  ],
  "relationships": [
    {
      "source": "AuthenticationService",
      "target": "UserRepository",
      "type": "depends_on",
      "description": "Fetches user data for authentication"
    }
  ],
  "design_patterns": [
    {
      "pattern": "Repository Pattern",
      "components": ["UserRepository", "ResourceRepository"],
      "confidence": 0.9
    }
  ],
  "gaps": [
    {
      "type": "missing_implementation",
      "component": "AuthenticationService",
      "description": "Documented but not found in codebase"
    }
  ],
  "formats_detected": ["markdown", "diagrams"],
  "execution_time": 2.5
}
```

**Performance:**
- Response time: <5s for typical documents (P95)
- Supports Markdown, PlantUML, Mermaid diagrams
- Uses existing RepositoryParser for codebase comparison

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/planning/parse-architecture" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "550e8400-e29b-41d4-a716-446655440000", "compare_with_codebase": true}'
```

**Requirements:** 8.1, 8.2, 8.3, 8.4, 8.5

---

## Data Models

### Planning Session Model

```json
{
  "plan_id": "uuid",
  "task_description": "string",
  "steps": [
    {
      "step_number": "integer",
      "description": "string",
      "dependencies": ["integer"],
      "estimated_effort": "string"
    }
  ],
  "status": "draft|refined|approved|rejected",
  "context": "object",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "refinement_count": "integer"
}
```

### Architecture Parse Result Model

```json
{
  "resource_id": "uuid",
  "components": [
    {
      "name": "string",
      "type": "string",
      "description": "string",
      "responsibilities": ["string"]
    }
  ],
  "relationships": [
    {
      "source": "string",
      "target": "string",
      "type": "string",
      "description": "string"
    }
  ],
  "design_patterns": [
    {
      "pattern": "string",
      "components": ["string"],
      "confidence": "float (0.0-1.0)"
    }
  ],
  "gaps": [
    {
      "type": "string",
      "component": "string",
      "description": "string"
    }
  ],
  "formats_detected": ["string"],
  "execution_time": "float"
}
```

## Module Structure

The Planning module is implemented as a self-contained vertical slice:

**Module**: `app.modules.planning`  
**Router Prefix**: `/api/planning`  
**Version**: 1.0.0

```python
from app.modules.planning import (
    router,
    PlanningService,
    MultiHopAgent,
    ArchitectureParser
)
```

### Events

**Emitted Events:**
- `plan.generated` - When a new plan is created
- `plan.refined` - When a plan is refined
- `architecture.parsed` - When an architecture document is parsed

**Subscribed Events:**
- None

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Graph API](graph.md) - Knowledge graph functionality
- [MCP API](mcp.md) - MCP server integration
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [API Overview](overview.md) - Authentication, errors, pagination
