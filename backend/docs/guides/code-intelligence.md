# Code Intelligence Guide

How to use hover information and code navigation features in Neo Alexandria 2.0.

> **Phase**: 20 - Frontend-Backend Infrastructure Support
> **Status**: Complete

## Overview

The Code Intelligence feature provides IDE-like hover information and code navigation capabilities for code repositories. It leverages existing static analysis and embedding infrastructure to deliver rich symbol information and related code chunks.

## Features

### 1. Hover Information

Get detailed information about symbols at specific positions in code files:

- **Symbol Information**: Name, type, definition location
- **Related Chunks**: Semantically similar code chunks
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++
- **Fast Response**: <200ms (P95) with caching

### 2. Related Chunk Discovery

Automatically discover related code chunks using:

- **Semantic Similarity**: Cosine similarity with existing embeddings
- **Threshold-Based**: Only chunks with similarity >0.7
- **Contextual**: Based on symbol and surrounding code

## API Reference

### GET `/graph/hover`

Get hover information for a symbol at a specific position.

**Parameters**:
- `file_path` (string, required): Relative path to file within repository
- `line` (integer, required): Line number (1-indexed)
- `column` (integer, required): Column number (0-indexed)
- `resource_id` (UUID, required): Repository resource ID

**Response**:
```json
{
  "symbol_info": {
    "name": "calculate_loss",
    "type": "function",
    "definition_location": {
      "file": "src/model.py",
      "line": 45,
      "column": 4
    },
    "docstring": "Calculate cross-entropy loss for model predictions.",
    "signature": "calculate_loss(predictions: Tensor, targets: Tensor) -> Tensor"
  },
  "related_chunks": [
    {
      "chunk_id": "uuid-1",
      "content": "def train_model(...):\n    loss = calculate_loss(outputs, labels)\n    ...",
      "similarity_score": 0.85,
      "file_path": "src/training.py",
      "start_line": 120,
      "end_line": 135
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Hover information retrieved successfully
- `404 Not Found`: File not found or no symbol at position
- `422 Unprocessable Entity`: Invalid parameters

**Performance**:
- Cached responses: <10ms
- Uncached responses: <200ms (P95)
- Cache TTL: 5 minutes

## Usage Examples

### Python Client

```python
import requests

# Get hover information
response = requests.get(
    "http://localhost:8000/graph/hover",
    params={
        "file_path": "src/model.py",
        "line": 50,
        "column": 10,
        "resource_id": "uuid-of-repository"
    },
    headers={"Authorization": f"Bearer {token}"}
)

hover_info = response.json()
print(f"Symbol: {hover_info['symbol_info']['name']}")
print(f"Type: {hover_info['symbol_info']['type']}")
print(f"Related chunks: {len(hover_info['related_chunks'])}")
```

### JavaScript/TypeScript Client

```typescript
interface HoverInfo {
  symbol_info: {
    name: string;
    type: string;
    definition_location: {
      file: string;
      line: number;
      column: number;
    };
    docstring?: string;
    signature?: string;
  };
  related_chunks: Array<{
    chunk_id: string;
    content: string;
    similarity_score: number;
    file_path: string;
    start_line: number;
    end_line: number;
  }>;
}

async function getHoverInfo(
  filePath: string,
  line: number,
  column: number,
  resourceId: string
): Promise<HoverInfo> {
  const response = await fetch(
    `/graph/hover?file_path=${filePath}&line=${line}&column=${column}&resource_id=${resourceId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return response.json();
}
```

### cURL

```bash
curl -X GET "http://localhost:8000/graph/hover" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G \
  --data-urlencode "file_path=src/model.py" \
  --data-urlencode "line=50" \
  --data-urlencode "column=10" \
  --data-urlencode "resource_id=uuid-of-repository"
```

## Supported Languages

| Language | File Extensions | Static Analysis | Symbol Types |
|----------|----------------|-----------------|--------------|
| Python | `.py` | ✅ Full | functions, classes, methods, variables |
| JavaScript | `.js` | ✅ Full | functions, classes, methods, variables |
| TypeScript | `.ts`, `.tsx` | ✅ Full | functions, classes, interfaces, types |
| Java | `.java` | ✅ Full | classes, methods, fields |
| C++ | `.cpp`, `.h`, `.hpp` | ✅ Full | functions, classes, structs |

## Architecture

### Components

1. **Graph Router** (`app/modules/graph/router.py`)
   - Handles HTTP requests
   - Validates parameters
   - Returns hover information

2. **Static Analyzer** (`app/modules/graph/logic/static_analysis.py`)
   - Parses code files using Tree-sitter
   - Extracts symbol information
   - Identifies definition locations

3. **Embedding Service** (`app/shared/embeddings.py`)
   - Generates embeddings for code chunks
   - Computes cosine similarity
   - Retrieves related chunks

4. **Cache Service** (`app/shared/cache.py`)
   - Caches hover responses (5-minute TTL)
   - Cache key: `hover:{resource_id}:{file_path}:{line}:{column}`

### Data Flow

```
1. Client requests hover info
   ↓
2. Check cache (5-minute TTL)
   ↓
3. If miss: Parse file with StaticAnalyzer
   ↓
4. Extract symbol information
   ↓
5. Query DocumentChunk table for related chunks
   ↓
6. Compute cosine similarity with embeddings
   ↓
7. Filter chunks (similarity >0.7)
   ↓
8. Cache response
   ↓
9. Return hover information
```

## Performance Optimization

### Caching Strategy

- **Cache Key**: `hover:{resource_id}:{file_path}:{line}:{column}`
- **TTL**: 5 minutes
- **Hit Rate**: ~70% for active development
- **Invalidation**: Automatic on resource update

### Similarity Threshold

- **Default**: 0.7 (70% similarity)
- **Rationale**: Balance between precision and recall
- **Tuning**: Adjust based on use case

### Batch Processing

For multiple hover requests:

```python
# Batch hover requests
positions = [
    {"file_path": "src/model.py", "line": 50, "column": 10},
    {"file_path": "src/training.py", "line": 120, "column": 15},
]

results = []
for pos in positions:
    response = requests.get(
        "http://localhost:8000/graph/hover",
        params={**pos, "resource_id": resource_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    results.append(response.json())
```

## Troubleshooting

### No Symbol Found

**Problem**: 404 error with "No symbol found at position"

**Solutions**:
1. Verify line and column numbers (1-indexed line, 0-indexed column)
2. Check file path is relative to repository root
3. Ensure file is part of ingested repository
4. Verify language is supported

### Slow Response Times

**Problem**: Hover requests taking >500ms

**Solutions**:
1. Check cache hit rate (should be >50%)
2. Verify Redis is running and accessible
3. Check database query performance
4. Consider increasing cache TTL

### No Related Chunks

**Problem**: Empty `related_chunks` array

**Solutions**:
1. Verify embeddings exist for repository chunks
2. Check similarity threshold (default 0.7)
3. Ensure repository has been fully ingested
4. Verify embedding generation completed

## Best Practices

### 1. Cache Warming

Pre-populate cache for frequently accessed files:

```python
# Warm cache for main files
main_files = ["src/main.py", "src/model.py", "src/training.py"]
for file_path in main_files:
    for line in range(1, 100):  # First 100 lines
        requests.get(
            "http://localhost:8000/graph/hover",
            params={
                "file_path": file_path,
                "line": line,
                "column": 0,
                "resource_id": resource_id
            }
        )
```

### 2. Error Handling

Always handle 404 errors gracefully:

```python
try:
    response = requests.get(...)
    response.raise_for_status()
    hover_info = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("No symbol at position")
    else:
        raise
```

### 3. Debouncing

Debounce hover requests in UI to avoid excessive API calls:

```typescript
import { debounce } from 'lodash';

const debouncedHover = debounce(
  (filePath, line, column) => getHoverInfo(filePath, line, column),
  300  // 300ms delay
);
```

## Integration with Frontend

### Monaco Editor

```typescript
import * as monaco from 'monaco-editor';

// Register hover provider
monaco.languages.registerHoverProvider('python', {
  provideHover: async (model, position) => {
    const filePath = model.uri.path;
    const line = position.lineNumber;
    const column = position.column;
    
    const hoverInfo = await getHoverInfo(filePath, line, column, resourceId);
    
    return {
      contents: [
        { value: `**${hoverInfo.symbol_info.name}** (${hoverInfo.symbol_info.type})` },
        { value: hoverInfo.symbol_info.docstring || '' },
        { value: `\n**Related Chunks**: ${hoverInfo.related_chunks.length}` }
      ]
    };
  }
});
```

### VS Code Extension

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const hoverProvider = vscode.languages.registerHoverProvider(
    { scheme: 'file', language: 'python' },
    {
      async provideHover(document, position) {
        const filePath = vscode.workspace.asRelativePath(document.uri);
        const line = position.line + 1;  // Convert to 1-indexed
        const column = position.character;
        
        const hoverInfo = await getHoverInfo(filePath, line, column, resourceId);
        
        const markdown = new vscode.MarkdownString();
        markdown.appendMarkdown(`**${hoverInfo.symbol_info.name}** (${hoverInfo.symbol_info.type})\n\n`);
        markdown.appendMarkdown(hoverInfo.symbol_info.docstring || '');
        
        return new vscode.Hover(markdown);
      }
    }
  );
  
  context.subscriptions.push(hoverProvider);
}
```

## Related Documentation

- [API Reference - Graph](../api/graph.md) - Complete API documentation
- [Architecture - Phase 20](../architecture/phase20-features.md) - Architecture details
- [Code Ingestion Guide](code-ingestion.md) - Repository ingestion
- [Advanced RAG Guide](advanced-rag.md) - Embedding and chunking

## Next Steps

1. **Explore Document Intelligence**: [Document Intelligence Guide](document-intelligence.md)
2. **Try Graph Intelligence**: [Graph Intelligence Guide](graph-intelligence.md)
3. **Integrate with Frontend**: Build rich code navigation experiences
4. **Optimize Performance**: Tune caching and similarity thresholds
