# Phase 6: Citation Network Examples

This document provides practical examples for using the Citation Network & Link Intelligence features in Neo Alexandria 2.0.

## Table of Contents
- [Basic Citation Retrieval](#basic-citation-retrieval)
- [Citation Graph Visualization](#citation-graph-visualization)
- [Manual Citation Extraction](#manual-citation-extraction)
- [Citation Resolution](#citation-resolution)
- [PageRank Importance Scoring](#pagerank-importance-scoring)
- [Integration Examples](#integration-examples)

## Basic Citation Retrieval

### Get All Citations for a Resource

```bash
# Get both inbound and outbound citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations"
```

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "outbound": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "source_resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "target_url": "https://arxiv.org/abs/1234.5678",
      "target_resource_id": "770e8400-e29b-41d4-a716-446655440002",
      "citation_type": "reference",
      "context_snippet": "...as described in the paper [1]...",
      "position": 1,
      "importance_score": 0.85,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "target_resource": {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "title": "Machine Learning Paper",
        "source": "https://arxiv.org/abs/1234.5678"
      }
    }
  ],
  "inbound": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "source_resource_id": "990e8400-e29b-41d4-a716-446655440004",
      "target_url": "https://example.com/my-article",
      "target_resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "citation_type": "reference",
      "context_snippet": "...building on the work of...",
      "position": 5,
      "importance_score": 0.72,
      "created_at": "2024-01-02T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  ],
  "counts": {
    "outbound": 1,
    "inbound": 1,
    "total": 2
  }
}
```

### Get Only Outbound Citations

```bash
# Get citations from this resource
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=outbound"
```

### Get Only Inbound Citations

```bash
# Get citations to this resource
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=inbound"
```

## Citation Graph Visualization

### Get Citation Network for a Resource

```bash
# Get citation graph with depth 1
curl "http://127.0.0.1:8000/citations/graph/citations?resource_ids={resource_id}&depth=1"
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "My Article",
      "type": "source"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Referenced Paper",
      "type": "cited"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "title": "Citing Article",
      "type": "citing"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "770e8400-e29b-41d4-a716-446655440002",
      "type": "reference"
    },
    {
      "source": "990e8400-e29b-41d4-a716-446655440004",
      "target": "550e8400-e29b-41d4-a716-446655440000",
      "type": "reference"
    }
  ]
}
```

### Get Deeper Citation Network

```bash
# Get citation graph with depth 2 (includes neighbors of neighbors)
curl "http://127.0.0.1:8000/citations/graph/citations?resource_ids={resource_id}&depth=2"
```

### Filter by Importance Score

```bash
# Get only high-importance citations
curl "http://127.0.0.1:8000/citations/graph/citations?min_importance=0.7"
```

### Get Global Citation Network

```bash
# Get overview of all citations in the system
curl "http://127.0.0.1:8000/citations/graph/citations?limit=100"
```

## Manual Citation Extraction

### Trigger Citation Extraction

```bash
# Manually extract citations from a resource
curl -X POST "http://127.0.0.1:8000/citations/resources/{resource_id}/citations/extract"
```

**Response:**
```json
{
  "status": "queued",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Citation extraction queued for processing"
}
```

**Use Cases:**
- Re-extract citations after content updates
- Debug citation extraction issues
- Process resources that failed automatic extraction

## Citation Resolution

### Resolve Internal Citations

```bash
# Match citation URLs to existing resources
curl -X POST "http://127.0.0.1:8000/citations/resolve"
```

**Response:**
```json
{
  "status": "queued"
}
```

**What It Does:**
1. Finds all citations with `target_resource_id = NULL`
2. Normalizes citation URLs
3. Matches URLs to existing resources
4. Updates `target_resource_id` for matches

**When to Run:**
- After bulk resource imports
- Periodically (e.g., daily) to link new resources
- After URL changes or updates

## PageRank Importance Scoring

### Compute Importance Scores

```bash
# Calculate PageRank scores for all citations
curl -X POST "http://127.0.0.1:8000/citations/importance/compute"
```

**Response:**
```json
{
  "status": "queued"
}
```

**What It Does:**
1. Builds citation graph from all resolved citations
2. Runs PageRank algorithm (damping=0.85, max_iter=100)
3. Normalizes scores to [0, 1] range
4. Updates `importance_score` for all citations

**When to Run:**
- Periodically (e.g., weekly) to update scores
- After bulk citation imports
- To identify influential resources

## Integration Examples

### Python Client Example

```python
import requests
import time

class CitationClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def get_citations(self, resource_id, direction="both"):
        """Get citations for a resource."""
        url = f"{self.base_url}/citations/resources/{resource_id}/citations"
        params = {"direction": direction}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_citation_graph(self, resource_ids=None, min_importance=0.0, depth=1):
        """Get citation network for visualization."""
        url = f"{self.base_url}/citations/graph/citations"
        params = {
            "min_importance": min_importance,
            "depth": depth
        }
        if resource_ids:
            params["resource_ids"] = resource_ids
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def extract_citations(self, resource_id):
        """Trigger citation extraction."""
        url = f"{self.base_url}/citations/resources/{resource_id}/citations/extract"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    
    def resolve_citations(self):
        """Resolve internal citations."""
        url = f"{self.base_url}/citations/resolve"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    
    def compute_importance(self):
        """Compute PageRank importance scores."""
        url = f"{self.base_url}/citations/importance/compute"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()

# Usage
client = CitationClient()

# Get citations for a resource
citations = client.get_citations("550e8400-e29b-41d4-a716-446655440000")
print(f"Outbound: {citations['counts']['outbound']}")
print(f"Inbound: {citations['counts']['inbound']}")

# Get citation graph
graph = client.get_citation_graph(
    resource_ids=["550e8400-e29b-41d4-a716-446655440000"],
    depth=2
)
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")

# Trigger citation extraction
result = client.extract_citations("550e8400-e29b-41d4-a716-446655440000")
print(f"Status: {result['status']}")
```

### JavaScript/TypeScript Example

```typescript
class CitationService {
  constructor(private baseUrl: string = 'http://127.0.0.1:8000') {}

  async getCitations(resourceId: string, direction: 'outbound' | 'inbound' | 'both' = 'both') {
    const url = `${this.baseUrl}/citations/resources/${resourceId}/citations`;
    const params = new URLSearchParams({ direction });
    const response = await fetch(`${url}?${params}`);
    if (!response.ok) throw new Error('Failed to fetch citations');
    return response.json();
  }

  async getCitationGraph(options: {
    resourceIds?: string[];
    minImportance?: number;
    depth?: number;
  } = {}) {
    const url = `${this.baseUrl}/citations/graph/citations`;
    const params = new URLSearchParams();
    
    if (options.resourceIds) {
      options.resourceIds.forEach(id => params.append('resource_ids', id));
    }
    if (options.minImportance !== undefined) {
      params.append('min_importance', options.minImportance.toString());
    }
    if (options.depth !== undefined) {
      params.append('depth', options.depth.toString());
    }
    
    const response = await fetch(`${url}?${params}`);
    if (!response.ok) throw new Error('Failed to fetch citation graph');
    return response.json();
  }

  async extractCitations(resourceId: string) {
    const url = `${this.baseUrl}/citations/resources/${resourceId}/citations/extract`;
    const response = await fetch(url, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to trigger citation extraction');
    return response.json();
  }

  async resolveCitations() {
    const url = `${this.baseUrl}/citations/resolve`;
    const response = await fetch(url, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to trigger citation resolution');
    return response.json();
  }

  async computeImportance() {
    const url = `${this.baseUrl}/citations/importance/compute`;
    const response = await fetch(url, { method: 'POST' });
    if (!response.ok) throw new Error('Failed to trigger importance computation');
    return response.json();
  }
}

// Usage
const citationService = new CitationService();

// Get citations
const citations = await citationService.getCitations('550e8400-e29b-41d4-a716-446655440000');
console.log(`Outbound: ${citations.counts.outbound}`);
console.log(`Inbound: ${citations.counts.inbound}`);

// Get citation graph for visualization
const graph = await citationService.getCitationGraph({
  resourceIds: ['550e8400-e29b-41d4-a716-446655440000'],
  depth: 2,
  minImportance: 0.5
});

// Render with D3.js or similar
renderCitationGraph(graph.nodes, graph.edges);
```

### Visualization with D3.js

```javascript
function renderCitationGraph(nodes, edges) {
  const width = 800;
  const height = 600;

  const svg = d3.select('#citation-graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  // Create force simulation
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  // Draw edges
  const link = svg.append('g')
    .selectAll('line')
    .data(edges)
    .enter().append('line')
    .attr('stroke', d => {
      const colors = {
        reference: '#3498db',
        dataset: '#2ecc71',
        code: '#e74c3c',
        general: '#95a5a6'
      };
      return colors[d.type] || '#95a5a6';
    })
    .attr('stroke-width', 2);

  // Draw nodes
  const node = svg.append('g')
    .selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', d => {
      return d.type === 'source' ? 12 : 8;
    })
    .attr('fill', d => {
      const colors = {
        source: '#e74c3c',
        cited: '#3498db',
        citing: '#2ecc71'
      };
      return colors[d.type] || '#95a5a6';
    })
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  // Add labels
  const label = svg.append('g')
    .selectAll('text')
    .data(nodes)
    .enter().append('text')
    .text(d => d.title.substring(0, 20))
    .attr('font-size', 10)
    .attr('dx', 15)
    .attr('dy', 4);

  // Update positions on tick
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);

    label
      .attr('x', d => d.x)
      .attr('y', d => d.y);
  });

  // Drag functions
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}
```

### Scheduled Tasks (Cron Jobs)

```bash
# /etc/cron.d/neo-alexandria-citations

# Resolve internal citations daily at 2 AM
0 2 * * * curl -X POST http://127.0.0.1:8000/citations/resolve

# Compute PageRank scores weekly on Sunday at 3 AM
0 3 * * 0 curl -X POST http://127.0.0.1:8000/citations/importance/compute
```

## Advanced Use Cases

### Find Most Cited Resources

```python
# Get all resources and sort by inbound citation count
def get_most_cited_resources(client, limit=10):
    # This would require a custom endpoint or client-side aggregation
    # For now, you can query individual resources and aggregate
    pass
```

### Citation Network Analysis

```python
import networkx as nx

def analyze_citation_network(graph_data):
    """Analyze citation network using NetworkX."""
    G = nx.DiGraph()
    
    # Add nodes
    for node in graph_data['nodes']:
        G.add_node(node['id'], title=node['title'], type=node['type'])
    
    # Add edges
    for edge in graph_data['edges']:
        G.add_edge(edge['source'], edge['target'], type=edge['type'])
    
    # Compute metrics
    metrics = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
    }
    
    # Find most influential nodes (by in-degree)
    in_degrees = dict(G.in_degree())
    most_cited = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    
    metrics['most_cited'] = [
        {'id': node_id, 'citations': count, 'title': G.nodes[node_id]['title']}
        for node_id, count in most_cited
    ]
    
    return metrics

# Usage
graph = client.get_citation_graph()
metrics = analyze_citation_network(graph)
print(f"Network density: {metrics['density']:.3f}")
print(f"Average degree: {metrics['avg_degree']:.2f}")
print("\nMost cited resources:")
for item in metrics['most_cited']:
    print(f"  {item['title']}: {item['citations']} citations")
```

## Troubleshooting

### Citations Not Extracted

**Problem:** Citations are not being extracted during ingestion.

**Solutions:**
1. Check that the resource has a supported content type (HTML, PDF, Markdown)
2. Verify the resource has completed ingestion (`ingestion_status = "completed"`)
3. Manually trigger extraction: `POST /citations/resources/{id}/citations/extract`
4. Check logs for extraction errors

### Citations Not Resolved

**Problem:** Citations have `target_resource_id = NULL` even though the resource exists.

**Solutions:**
1. Run citation resolution: `POST /citations/resolve`
2. Check URL normalization (fragments, trailing slashes)
3. Verify the target resource's `source` URL matches the citation's `target_url`
4. Check for case sensitivity issues

### PageRank Scores Not Updating

**Problem:** Importance scores are not being computed.

**Solutions:**
1. Ensure NetworkX is installed: `pip install networkx`
2. Trigger computation: `POST /citations/importance/compute`
3. Check that citations have resolved `target_resource_id` values
4. Verify the citation graph is connected (not isolated nodes)

### Performance Issues

**Problem:** Citation queries are slow.

**Solutions:**
1. Ensure database indexes are created (check migration)
2. Limit graph depth to 1 for faster queries
3. Use `min_importance` filter to reduce result set
4. Consider pagination for large result sets
5. Run PageRank computation as a scheduled background job

## Best Practices

1. **Automatic Extraction**: Let the system extract citations automatically during ingestion
2. **Periodic Resolution**: Run citation resolution daily to link new resources
3. **Scheduled PageRank**: Compute importance scores weekly, not on every request
4. **Graph Depth**: Use depth=1 for interactive visualizations, depth=2 for analysis
5. **Importance Filtering**: Use `min_importance` to focus on significant citations
6. **Error Handling**: Citation extraction failures should not block ingestion
7. **Monitoring**: Track citation extraction success rates and resolution percentages
