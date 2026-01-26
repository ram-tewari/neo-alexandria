# MCP Server API

Model Context Protocol (MCP) server endpoints for tool registration and invocation.

## Overview

The MCP API provides a standardized interface for:
- Tool registration and discovery
- Tool invocation with schema validation
- Session management with context preservation
- Authentication and rate limiting
- Logging and monitoring

## Endpoints

### GET /api/mcp/tools

**Phase 20** - List all available MCP tools.

Returns a catalog of registered tools with their schemas and descriptions.

**Response:**
```json
{
  "tools": [
    {
      "name": "search_resources",
      "description": "Search for resources using hybrid search",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "Search query"
          },
          "limit": {
            "type": "integer",
            "description": "Maximum results",
            "default": 10
          }
        },
        "required": ["query"]
      },
      "category": "search"
    },
    {
      "name": "get_hover_info",
      "description": "Get hover information for code at a position",
      "input_schema": {
        "type": "object",
        "properties": {
          "file_path": {"type": "string"},
          "line": {"type": "integer"},
          "column": {"type": "integer"},
          "resource_id": {"type": "string"}
        },
        "required": ["file_path", "line", "column", "resource_id"]
      },
      "category": "code_intelligence"
    }
  ],
  "total_count": 7
}
```

**Tool Categories:**
- `search` - Search and discovery tools
- `code_intelligence` - Code analysis tools
- `graph` - Knowledge graph tools
- `planning` - AI planning tools
- `document` - Document processing tools

**Example:**
```bash
curl "http://127.0.0.1:8000/api/mcp/tools" \
  -H "Authorization: Bearer <token>"
```

**Requirements:** 10.1, 10.7

---

### POST /api/mcp/invoke

**Phase 20** - Invoke an MCP tool with validated input.

Executes a registered tool with schema validation and returns the result.

**Request Body:**
```json
{
  "tool_name": "search_resources",
  "arguments": {
    "query": "machine learning",
    "limit": 5
  },
  "session_id": "session-uuid-1"
}
```

**Parameters:**
- `tool_name` (required): Name of the tool to invoke
- `arguments` (required): Tool arguments (validated against schema)
- `session_id` (optional): Session ID for context preservation

**Response:**
```json
{
  "tool_name": "search_resources",
  "result": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Machine Learning Fundamentals",
        "score": 0.95
      }
    ],
    "total": 1
  },
  "execution_time": 0.15,
  "invoked_at": "2024-01-01T10:00:00Z"
}
```

**Error Response (Schema Validation Failed):**
```json
{
  "error": "Schema validation failed",
  "details": {
    "field": "limit",
    "message": "Expected integer, got string"
  }
}
```

**Error Response (Tool Not Found):**
```json
{
  "error": "Tool not found",
  "tool_name": "invalid_tool"
}
```

**Performance:**
- Response time: Varies by tool (typically <500ms)
- Rate limiting: 100 requests/minute (Free), 1000 requests/minute (Premium)
- Schema validation: <10ms

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/mcp/invoke" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"tool_name": "search_resources", "arguments": {"query": "machine learning", "limit": 5}}'
```

**Requirements:** 10.1, 10.2, 10.3, 10.4, 10.5, 10.7

---

### POST /api/mcp/sessions

**Phase 20** - Create a new MCP session.

Creates a session for maintaining context across multiple tool invocations.

**Request Body:**
```json
{
  "context": {
    "user_id": "user-uuid-1",
    "workspace": "my-project"
  }
}
```

**Parameters:**
- `context` (optional): Initial session context

**Response:**
```json
{
  "session_id": "session-uuid-1",
  "context": {
    "user_id": "user-uuid-1",
    "workspace": "my-project"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "expires_at": "2024-01-01T11:00:00Z"
}
```

**Session Expiration:**
- Default TTL: 1 hour
- Automatic cleanup after expiration
- Context preserved across invocations

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/mcp/sessions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"context": {"user_id": "user-uuid-1", "workspace": "my-project"}}'
```

**Requirements:** 10.6

---

### DELETE /api/mcp/sessions/{session_id}

**Phase 20** - Close an MCP session.

Terminates a session and cleans up associated resources.

**Path Parameters:**
- `session_id` (required): Session ID (UUID)

**Response:** `204 No Content`

**Example:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/mcp/sessions/session-uuid-1" \
  -H "Authorization: Bearer <token>"
```

**Requirements:** 10.6

---

### GET /api/mcp/sessions/{session_id}

**Phase 20** - Retrieve session details.

Returns the current state and context of a session.

**Path Parameters:**
- `session_id` (required): Session ID (UUID)

**Response:**
```json
{
  "session_id": "session-uuid-1",
  "context": {
    "user_id": "user-uuid-1",
    "workspace": "my-project",
    "last_query": "machine learning"
  },
  "tool_invocations": [
    {
      "tool_name": "search_resources",
      "invoked_at": "2024-01-01T10:00:00Z",
      "execution_time": 0.15
    }
  ],
  "created_at": "2024-01-01T10:00:00Z",
  "expires_at": "2024-01-01T11:00:00Z"
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/mcp/sessions/session-uuid-1" \
  -H "Authorization: Bearer <token>"
```

**Requirements:** 10.6

---

## Registered Tools

### Search Tools

**search_resources**
- Description: Search for resources using hybrid search
- Input: `query` (string), `limit` (integer)
- Output: List of matching resources with scores

### Code Intelligence Tools

**get_hover_info**
- Description: Get hover information for code at a position
- Input: `file_path` (string), `line` (integer), `column` (integer), `resource_id` (string)
- Output: Symbol information and related chunks

### Graph Tools

**compute_graph_metrics**
- Description: Compute centrality metrics for resources
- Input: `resource_ids` (array), `metrics` (array)
- Output: Centrality metrics (degree, betweenness, pagerank)

**detect_communities**
- Description: Detect communities in the knowledge graph
- Input: `resolution` (float), `resource_ids` (array)
- Output: Community assignments and modularity score

### Planning Tools

**generate_plan**
- Description: Generate a multi-step plan for a task
- Input: `task_description` (string), `context` (object), `max_steps` (integer)
- Output: Structured plan with dependencies

**parse_architecture**
- Description: Parse an architecture document
- Input: `resource_id` (string), `compare_with_codebase` (boolean)
- Output: Components, relationships, patterns, and gaps

### Document Tools

**link_pdf_to_code**
- Description: Automatically link PDF chunks to code chunks
- Input: `resource_id` (string), `similarity_threshold` (float), `max_links_per_chunk` (integer)
- Output: Number of links created

---

## Data Models

### Tool Schema Model

```json
{
  "name": "string",
  "description": "string",
  "input_schema": {
    "type": "object",
    "properties": "object",
    "required": ["string"]
  },
  "category": "string"
}
```

### Tool Invocation Model

```json
{
  "tool_name": "string",
  "arguments": "object",
  "session_id": "uuid (optional)",
  "result": "any",
  "execution_time": "float",
  "invoked_at": "datetime (ISO 8601)"
}
```

### Session Model

```json
{
  "session_id": "uuid",
  "context": "object",
  "tool_invocations": [
    {
      "tool_name": "string",
      "invoked_at": "datetime (ISO 8601)",
      "execution_time": "float"
    }
  ],
  "created_at": "datetime (ISO 8601)",
  "expires_at": "datetime (ISO 8601)"
}
```

## Authentication & Authorization

**Authentication:**
- JWT token required for all endpoints
- Token passed in `Authorization: Bearer <token>` header
- Tokens expire after 24 hours

**Rate Limiting:**
- Free tier: 100 requests/minute
- Premium tier: 1000 requests/minute
- Admin tier: Unlimited

**Enforcement:**
- 429 Too Many Requests when rate limit exceeded
- 401 Unauthorized when token is missing or invalid
- 403 Forbidden when token lacks required permissions

## Module Structure

The MCP module is implemented as a self-contained vertical slice:

**Module**: `app.modules.mcp`  
**Router Prefix**: `/api/mcp`  
**Version**: 1.0.0

```python
from app.modules.mcp import (
    router,
    MCPServer,
    ToolRegistry,
    SessionManager
)
```

### Events

**Emitted Events:**
- `mcp.tool_invoked` - When a tool is invoked
- `mcp.session_created` - When a session is created
- `mcp.session_closed` - When a session is closed

**Subscribed Events:**
- None

## Security Considerations

**Schema Validation:**
- All tool arguments validated against JSON Schema
- Type checking and required field validation
- Protection against injection attacks

**Rate Limiting:**
- Per-user rate limits enforced
- Sliding window algorithm
- Graceful degradation under load

**Logging:**
- All tool invocations logged
- Session activity tracked
- Audit trail for security analysis

**Error Handling:**
- Sensitive information not exposed in errors
- Detailed errors logged server-side
- Generic errors returned to clients

## Related Documentation

- [Planning API](planning.md) - AI planning tools
- [Graph API](graph.md) - Knowledge graph tools
- [Search API](search.md) - Search tools
- [Resources API](resources.md) - Resource management tools
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [API Overview](overview.md) - Authentication, errors, pagination
