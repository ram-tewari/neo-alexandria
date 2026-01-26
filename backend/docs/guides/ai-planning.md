# AI Planning Guide

How to use multi-hop planning and architecture document parsing in Neo Alexandria 2.0.

> **Phase**: 20 - Frontend-Backend Infrastructure Support
> **Status**: Complete

## Overview

The AI Planning feature provides intelligent task planning and architecture analysis capabilities. It uses LLMs to generate multi-step plans with dependency tracking and parse architecture documents to identify gaps between documentation and implementation.

## Features

### 1. Multi-Hop Planning

Generate intelligent, multi-step plans for complex tasks:

- **LLM-Powered**: Uses language models for plan generation
- **Dependency Tracking**: Automatic extraction of task dependencies
- **Iterative Refinement**: Refine plans based on feedback
- **Context Preservation**: Maintains context across planning steps
- **DAG Validation**: Ensures dependency graph is acyclic
- **Fast Generation**: <3s per planning step (P95)

### 2. Architecture Document Parsing

Extract structured information from architecture documents:

- **Component Extraction**: Identify system components
- **Relationship Mapping**: Extract component relationships
- **Pattern Recognition**: Detect design patterns
- **Gap Analysis**: Compare documented vs. implemented architecture
- **Multi-Format Support**: Markdown, reStructuredText, plain text
- **Repository Integration**: Compare with actual codebase

## API Reference

### POST `/planning/generate`

Generate a multi-step plan for a task.

**Request Body**:
```json
{
  "task_description": "Implement user authentication with OAuth2",
  "context": {
    "existing_features": ["database", "API endpoints"],
    "constraints": ["must use JWT tokens", "support Google OAuth"],
    "preferences": ["prefer FastAPI patterns"]
  },
  "max_steps": 10
}
```

**Response**:
```json
{
  "plan_id": "uuid-plan-1",
  "task_description": "Implement user authentication with OAuth2",
  "steps": [
    {
      "step_number": 1,
      "description": "Set up OAuth2 client configuration",
      "dependencies": [],
      "estimated_time": "30 minutes",
      "resources": ["OAuth2 documentation", "FastAPI OAuth guide"]
    },
    {
      "step_number": 2,
      "description": "Implement JWT token generation",
      "dependencies": [1],
      "estimated_time": "1 hour",
      "resources": ["PyJWT library", "JWT best practices"]
    }
  ],
  "dependencies": {
    "1": [],
    "2": [1],
    "3": [1, 2]
  },
  "status": "generated",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### PUT `/planning/{plan_id}/refine`

Refine an existing plan based on feedback.

**Request Body**:
```json
{
  "feedback": "Add step for database migration",
  "step_to_modify": 2,
  "modification_type": "add_before"
}
```

**Response**:
```json
{
  "plan_id": "uuid-plan-1",
  "steps": [
    {
      "step_number": 1,
      "description": "Set up OAuth2 client configuration",
      "dependencies": []
    },
    {
      "step_number": 2,
      "description": "Create database migration for user table",
      "dependencies": [1]
    },
    {
      "step_number": 3,
      "description": "Implement JWT token generation",
      "dependencies": [1, 2]
    }
  ],
  "refinement_history": [
    {
      "timestamp": "2024-01-15T10:35:00Z",
      "feedback": "Add step for database migration",
      "changes": "Inserted step 2, renumbered subsequent steps"
    }
  ]
}
```

### GET `/planning/{plan_id}`

Retrieve an existing plan.

**Response**:
```json
{
  "plan_id": "uuid-plan-1",
  "task_description": "Implement user authentication with OAuth2",
  "steps": [...],
  "dependencies": {...},
  "status": "in_progress",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### POST `/planning/parse-architecture`

Parse an architecture document and analyze gaps.

**Request Body**:
```json
{
  "resource_id": "uuid-doc-1",
  "compare_with_repo": true,
  "repo_resource_id": "uuid-repo-1"
}
```

**Response**:
```json
{
  "components": [
    {
      "name": "AuthenticationService",
      "type": "service",
      "description": "Handles user authentication and token management",
      "responsibilities": ["OAuth2 flow", "JWT generation", "Token validation"]
    },
    {
      "name": "UserRepository",
      "type": "repository",
      "description": "Database access layer for user data",
      "responsibilities": ["CRUD operations", "User queries"]
    }
  ],
  "relationships": [
    {
      "source": "AuthenticationService",
      "target": "UserRepository",
      "type": "depends_on",
      "description": "Uses UserRepository to fetch user data"
    }
  ],
  "patterns": [
    {
      "name": "Repository Pattern",
      "confidence": 0.95,
      "components": ["UserRepository", "ResourceRepository"]
    },
    {
      "name": "Service Layer",
      "confidence": 0.90,
      "components": ["AuthenticationService", "ResourceService"]
    }
  ],
  "gaps": [
    {
      "type": "missing_implementation",
      "component": "AuthenticationService",
      "description": "Documented but not found in codebase",
      "severity": "high"
    },
    {
      "type": "undocumented_component",
      "component": "CacheService",
      "description": "Implemented but not documented",
      "severity": "medium"
    }
  ]
}
```

## Usage Examples

### Python Client

```python
import requests

# Generate a plan
response = requests.post(
    "http://localhost:8000/planning/generate",
    json={
        "task_description": "Implement user authentication with OAuth2",
        "context": {
            "existing_features": ["database", "API endpoints"],
            "constraints": ["must use JWT tokens"]
        },
        "max_steps": 10
    },
    headers={"Authorization": f"Bearer {token}"}
)

plan = response.json()
print(f"Generated plan with {len(plan['steps'])} steps")

# Refine the plan
response = requests.put(
    f"http://localhost:8000/planning/{plan['plan_id']}/refine",
    json={
        "feedback": "Add step for testing",
        "step_to_modify": len(plan['steps']),
        "modification_type": "add_after"
    },
    headers={"Authorization": f"Bearer {token}"}
)

refined_plan = response.json()
print(f"Refined plan now has {len(refined_plan['steps'])} steps")

# Parse architecture document
response = requests.post(
    "http://localhost:8000/planning/parse-architecture",
    json={
        "resource_id": "uuid-doc-1",
        "compare_with_repo": True,
        "repo_resource_id": "uuid-repo-1"
    },
    headers={"Authorization": f"Bearer {token}"}
)

architecture = response.json()
print(f"Found {len(architecture['components'])} components")
print(f"Detected {len(architecture['patterns'])} design patterns")
print(f"Identified {len(architecture['gaps'])} gaps")
```

### JavaScript/TypeScript Client

```typescript
interface PlanStep {
  step_number: number;
  description: string;
  dependencies: number[];
  estimated_time?: string;
  resources?: string[];
}

interface Plan {
  plan_id: string;
  task_description: string;
  steps: PlanStep[];
  dependencies: Record<string, number[]>;
  status: string;
}

interface ArchitectureComponent {
  name: string;
  type: string;
  description: string;
  responsibilities: string[];
}

interface ArchitectureGap {
  type: string;
  component: string;
  description: string;
  severity: string;
}

// Generate plan
async function generatePlan(
  taskDescription: string,
  context: Record<string, any>
): Promise<Plan> {
  const response = await fetch('/planning/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      task_description: taskDescription,
      context: context,
      max_steps: 10
    })
  });
  return response.json();
}

// Refine plan
async function refinePlan(
  planId: string,
  feedback: string,
  stepToModify: number
): Promise<Plan> {
  const response = await fetch(`/planning/${planId}/refine`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      feedback: feedback,
      step_to_modify: stepToModify,
      modification_type: 'add_after'
    })
  });
  return response.json();
}

// Parse architecture
async function parseArchitecture(
  resourceId: string,
  repoResourceId?: string
): Promise<{
  components: ArchitectureComponent[];
  gaps: ArchitectureGap[];
}> {
  const response = await fetch('/planning/parse-architecture', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      resource_id: resourceId,
      compare_with_repo: !!repoResourceId,
      repo_resource_id: repoResourceId
    })
  });
  return response.json();
}
```

## Multi-Hop Planning

### How It Works

1. **Task Analysis**: LLM analyzes task description and context
2. **Step Generation**: Generates sequence of actionable steps
3. **Dependency Extraction**: Identifies dependencies between steps
4. **DAG Validation**: Ensures no circular dependencies
5. **Context Preservation**: Maintains context for refinement

### Planning Strategies

#### Top-Down Planning

Start with high-level goals and decompose:

```python
plan = generate_plan(
    task_description="Build a recommendation system",
    context={
        "approach": "top-down",
        "existing_features": ["user data", "item catalog"],
        "constraints": ["must scale to 1M users"]
    }
)

# Result: High-level steps like "Design architecture", "Implement core algorithm"
```

#### Bottom-Up Planning

Start with specific tasks and build up:

```python
plan = generate_plan(
    task_description="Optimize database queries",
    context={
        "approach": "bottom-up",
        "existing_features": ["PostgreSQL database"],
        "constraints": ["minimize downtime"]
    }
)

# Result: Specific steps like "Add index on user_id", "Optimize JOIN queries"
```

### Dependency Management

Plans automatically track dependencies:

```python
# Visualize dependency graph
def visualize_dependencies(plan):
    import networkx as nx
    import matplotlib.pyplot as plt
    
    G = nx.DiGraph()
    
    # Add nodes
    for step in plan['steps']:
        G.add_node(step['step_number'], label=step['description'][:30])
    
    # Add edges
    for step in plan['steps']:
        for dep in step['dependencies']:
            G.add_edge(dep, step['step_number'])
    
    # Draw
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue')
    plt.show()

visualize_dependencies(plan)
```

### Iterative Refinement

Refine plans based on feedback:

```python
# Initial plan
plan = generate_plan("Implement caching layer")

# Add missing step
plan = refine_plan(
    plan['plan_id'],
    feedback="Add step for cache invalidation strategy",
    step_to_modify=3,
    modification_type="add_after"
)

# Modify existing step
plan = refine_plan(
    plan['plan_id'],
    feedback="Use Redis instead of Memcached",
    step_to_modify=2,
    modification_type="replace"
)

# Remove unnecessary step
plan = refine_plan(
    plan['plan_id'],
    feedback="Remove benchmarking step",
    step_to_modify=5,
    modification_type="remove"
)
```

## Architecture Document Parsing

### Supported Formats

| Format | Extensions | Features |
|--------|-----------|----------|
| Markdown | `.md` | Headers, lists, code blocks |
| reStructuredText | `.rst` | Directives, roles |
| Plain Text | `.txt` | Simple parsing |

### Component Extraction

The parser identifies components using:

- **Pattern Matching**: Keywords like "service", "repository", "controller"
- **Structure Analysis**: Headers, sections, diagrams
- **LLM Understanding**: Semantic understanding of descriptions

Example architecture document:

```markdown
# System Architecture

## Components

### AuthenticationService
Handles user authentication and token management.

Responsibilities:
- OAuth2 flow
- JWT generation
- Token validation

### UserRepository
Database access layer for user data.

Responsibilities:
- CRUD operations
- User queries
```

Parsed result:

```python
{
  "components": [
    {
      "name": "AuthenticationService",
      "type": "service",
      "responsibilities": ["OAuth2 flow", "JWT generation", "Token validation"]
    },
    {
      "name": "UserRepository",
      "type": "repository",
      "responsibilities": ["CRUD operations", "User queries"]
    }
  ]
}
```

### Relationship Extraction

The parser identifies relationships:

- **Dependencies**: "uses", "depends on", "requires"
- **Inheritance**: "extends", "inherits from"
- **Composition**: "contains", "has a"
- **Communication**: "calls", "sends to", "receives from"

### Pattern Recognition

Detects common design patterns:

- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **Factory Pattern**: Object creation
- **Observer Pattern**: Event-driven communication
- **Singleton Pattern**: Single instance

### Gap Analysis

Compares documentation with actual codebase:

```python
# Parse architecture and compare with repo
result = parse_architecture(
    resource_id="uuid-doc-1",
    compare_with_repo=True,
    repo_resource_id="uuid-repo-1"
)

# Analyze gaps
for gap in result['gaps']:
    if gap['type'] == 'missing_implementation':
        print(f"⚠️  {gap['component']}: {gap['description']}")
    elif gap['type'] == 'undocumented_component':
        print(f"📝 {gap['component']}: {gap['description']}")
    elif gap['type'] == 'mismatch':
        print(f"❌ {gap['component']}: {gap['description']}")
```

## Integration Examples

### Project Planning Workflow

```python
def plan_project(project_description, architecture_doc_id, repo_id):
    # 1. Parse architecture document
    architecture = parse_architecture(
        resource_id=architecture_doc_id,
        compare_with_repo=True,
        repo_resource_id=repo_id
    )
    
    # 2. Identify gaps
    missing_components = [
        gap['component'] for gap in architecture['gaps']
        if gap['type'] == 'missing_implementation'
    ]
    
    # 3. Generate implementation plan
    plan = generate_plan(
        task_description=f"Implement missing components: {', '.join(missing_components)}",
        context={
            "existing_components": [c['name'] for c in architecture['components']],
            "design_patterns": [p['name'] for p in architecture['patterns']]
        }
    )
    
    # 4. Return comprehensive project plan
    return {
        "architecture": architecture,
        "implementation_plan": plan,
        "gaps": architecture['gaps']
    }
```

### Interactive Planning Assistant

```typescript
class PlanningAssistant {
  private currentPlan: Plan | null = null;
  
  async startPlanning(taskDescription: string, context: any): Promise<Plan> {
    this.currentPlan = await generatePlan(taskDescription, context);
    return this.currentPlan;
  }
  
  async provideFeedback(feedback: string, stepNumber: number): Promise<Plan> {
    if (!this.currentPlan) {
      throw new Error('No active plan');
    }
    
    this.currentPlan = await refinePlan(
      this.currentPlan.plan_id,
      feedback,
      stepNumber
    );
    
    return this.currentPlan;
  }
  
  async analyzeArchitecture(docId: string, repoId?: string) {
    const architecture = await parseArchitecture(docId, repoId);
    
    // Generate plan to address gaps
    if (architecture.gaps.length > 0) {
      const gapDescriptions = architecture.gaps
        .map(g => `${g.component}: ${g.description}`)
        .join('; ');
      
      const plan = await this.startPlanning(
        `Address architecture gaps: ${gapDescriptions}`,
        { architecture: architecture.components }
      );
      
      return { architecture, plan };
    }
    
    return { architecture, plan: null };
  }
}
```

## Best Practices

### 1. Provide Rich Context

Include relevant context for better plans:

```python
plan = generate_plan(
    task_description="Implement caching",
    context={
        "existing_features": ["Redis", "PostgreSQL"],
        "constraints": ["must be thread-safe", "TTL < 5 minutes"],
        "preferences": ["prefer decorator pattern"],
        "team_expertise": ["Python", "FastAPI"],
        "timeline": "2 weeks"
    }
)
```

### 2. Iterative Refinement

Refine plans incrementally:

```python
# Start with high-level plan
plan = generate_plan("Build API")

# Refine based on feedback
plan = refine_plan(plan['plan_id'], "Add authentication step")
plan = refine_plan(plan['plan_id'], "Include testing phase")
plan = refine_plan(plan['plan_id'], "Add deployment step")
```

### 3. Validate Dependencies

Ensure dependency graph is valid:

```python
def validate_dag(plan):
    import networkx as nx
    
    G = nx.DiGraph()
    for step in plan['steps']:
        for dep in step['dependencies']:
            G.add_edge(dep, step['step_number'])
    
    if nx.is_directed_acyclic_graph(G):
        print("✓ Valid DAG")
    else:
        cycles = list(nx.simple_cycles(G))
        print(f"✗ Circular dependencies: {cycles}")

validate_dag(plan)
```

### 4. Track Progress

Monitor plan execution:

```python
class PlanTracker:
    def __init__(self, plan):
        self.plan = plan
        self.completed_steps = set()
    
    def complete_step(self, step_number):
        self.completed_steps.add(step_number)
    
    def get_next_steps(self):
        # Find steps whose dependencies are all completed
        next_steps = []
        for step in self.plan['steps']:
            if step['step_number'] in self.completed_steps:
                continue
            if all(dep in self.completed_steps for dep in step['dependencies']):
                next_steps.append(step)
        return next_steps
    
    def progress(self):
        return len(self.completed_steps) / len(self.plan['steps'])
```

## Troubleshooting

### Plan Generation Timeout

**Problem**: Plan generation taking >10s

**Solutions**:
1. Reduce `max_steps` parameter
2. Simplify task description
3. Reduce context size
4. Check LLM service availability

### Invalid Dependencies

**Problem**: Circular dependencies in plan

**Solutions**:
1. Refine plan to break cycles
2. Validate DAG after generation
3. Manually adjust dependencies
4. Regenerate plan with clearer description

### Architecture Parsing Errors

**Problem**: Components not extracted correctly

**Solutions**:
1. Verify document format (Markdown, RST, TXT)
2. Use clear section headers
3. Include explicit component descriptions
4. Check for parsing errors in response

## Related Documentation

- [API Reference - Planning](../api/planning.md) - Complete API documentation
- [Architecture - Phase 20](../architecture/phase20-features.md) - Architecture details
- [MCP Integration Guide](mcp-integration.md) - MCP server integration
- [Code Intelligence Guide](code-intelligence.md) - Code analysis

## Next Steps

1. **Try MCP Integration**: [MCP Integration Guide](mcp-integration.md)
2. **Build Planning UI**: Create interactive planning interface
3. **Automate Workflows**: Use plans to drive automation
4. **Analyze Your Architecture**: Identify gaps and improvements
