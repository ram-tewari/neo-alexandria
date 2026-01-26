# Graph Intelligence Guide

How to use centrality metrics, community detection, and graph visualization in Neo Alexandria 2.0.

> **Phase**: 20 - Frontend-Backend Infrastructure Support
> **Status**: Complete

## Overview

The Graph Intelligence feature provides advanced graph analytics capabilities for knowledge graphs and citation networks. It includes centrality metrics, community detection, and graph visualization layouts to help understand relationships and structure in your knowledge base.

## Features

### 1. Centrality Metrics

Compute importance metrics for resources in the knowledge graph:

- **Degree Centrality**: Number of connections (in-degree and out-degree)
- **Betweenness Centrality**: How often a resource lies on shortest paths
- **PageRank**: Importance based on link structure (configurable damping factor)
- **Fast Computation**: <500ms for graphs with 1000 nodes (P95)
- **Caching**: 10-minute TTL for computed metrics

### 2. Community Detection

Discover clusters of related resources:

- **Louvain Algorithm**: Hierarchical community detection
- **Modularity Score**: Quality metric for community structure
- **Configurable Resolution**: Control granularity of communities
- **Fast Detection**: <2s for graphs with 1000 nodes (P95)
- **Caching**: 15-minute TTL for community assignments

### 3. Graph Visualization

Generate layout coordinates for graph visualization:

- **Force-Directed Layout**: Fruchterman-Reingold algorithm
- **Hierarchical Layout**: Kamada-Kawai algorithm
- **Circular Layout**: Nodes arranged in a circle
- **Normalized Coordinates**: [0, 1000] range for easy rendering
- **Fast Layout**: <1s for graphs with 500 nodes (P95)
- **Caching**: 10-minute TTL for layouts

## API Reference

### GET `/graph/centrality`

Compute centrality metrics for resources in the graph.

**Parameters**:
- `resource_ids` (array of UUIDs, optional): Specific resources to compute metrics for
- `metric_types` (array of strings, optional): Metrics to compute (`degree`, `betweenness`, `pagerank`)
- `damping_factor` (float, optional): PageRank damping factor (default: 0.85)

**Response**:
```json
{
  "metrics": [
    {
      "resource_id": "uuid-1",
      "degree_centrality": {
        "in_degree": 15,
        "out_degree": 8,
        "total_degree": 23
      },
      "betweenness_centrality": 0.042,
      "pagerank": 0.0035
    }
  ],
  "computed_at": "2024-01-15T10:30:00Z",
  "cache_ttl": 600
}
```

### POST `/graph/communities`

Detect communities in the knowledge graph.

**Request Body**:
```json
{
  "resource_ids": ["uuid-1", "uuid-2"],  // Optional: subset of graph
  "resolution": 1.0,  // Optional: community granularity (default: 1.0)
  "algorithm": "louvain"  // Optional: algorithm (default: louvain)
}
```

**Response**:
```json
{
  "communities": [
    {
      "community_id": 0,
      "resource_ids": ["uuid-1", "uuid-3", "uuid-5"],
      "size": 3
    },
    {
      "community_id": 1,
      "resource_ids": ["uuid-2", "uuid-4"],
      "size": 2
    }
  ],
  "modularity": 0.42,
  "num_communities": 2,
  "computed_at": "2024-01-15T10:30:00Z",
  "cache_ttl": 900
}
```

### POST `/graph/layout`

Generate visualization layout for the graph.

**Request Body**:
```json
{
  "resource_ids": ["uuid-1", "uuid-2", "uuid-3"],  // Optional: subset
  "layout_type": "force",  // "force", "hierarchical", or "circular"
  "width": 1000,  // Optional: canvas width (default: 1000)
  "height": 1000  // Optional: canvas height (default: 1000)
}
```

**Response**:
```json
{
  "nodes": [
    {
      "resource_id": "uuid-1",
      "x": 250.5,
      "y": 380.2,
      "label": "Resource Title"
    }
  ],
  "edges": [
    {
      "source": "uuid-1",
      "target": "uuid-2",
      "weight": 1.0
    }
  ],
  "layout_type": "force",
  "computed_at": "2024-01-15T10:30:00Z",
  "cache_ttl": 600
}
```

## Usage Examples

### Python Client

```python
import requests

# Compute centrality metrics
response = requests.get(
    "http://localhost:8000/graph/centrality",
    params={
        "metric_types": ["degree", "pagerank"]
    },
    headers={"Authorization": f"Bearer {token}"}
)

metrics = response.json()
for metric in metrics["metrics"]:
    print(f"Resource {metric['resource_id']}: PageRank = {metric['pagerank']}")

# Detect communities
response = requests.post(
    "http://localhost:8000/graph/communities",
    json={
        "resolution": 1.0,
        "algorithm": "louvain"
    },
    headers={"Authorization": f"Bearer {token}"}
)

communities = response.json()
print(f"Found {communities['num_communities']} communities")
print(f"Modularity: {communities['modularity']}")

# Generate visualization layout
response = requests.post(
    "http://localhost:8000/graph/layout",
    json={
        "layout_type": "force",
        "width": 1200,
        "height": 800
    },
    headers={"Authorization": f"Bearer {token}"}
)

layout = response.json()
print(f"Generated layout with {len(layout['nodes'])} nodes")
```

### JavaScript/TypeScript Client

```typescript
interface CentralityMetrics {
  resource_id: string;
  degree_centrality: {
    in_degree: number;
    out_degree: number;
    total_degree: number;
  };
  betweenness_centrality: number;
  pagerank: number;
}

interface Community {
  community_id: number;
  resource_ids: string[];
  size: number;
}

interface GraphLayout {
  nodes: Array<{
    resource_id: string;
    x: number;
    y: number;
    label: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
    weight: number;
  }>;
}

// Compute centrality
async function getCentrality(): Promise<CentralityMetrics[]> {
  const response = await fetch(
    '/graph/centrality?metric_types=degree&metric_types=pagerank',
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  const data = await response.json();
  return data.metrics;
}

// Detect communities
async function detectCommunities(resolution: number = 1.0): Promise<Community[]> {
  const response = await fetch('/graph/communities', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ resolution, algorithm: 'louvain' })
  });
  const data = await response.json();
  return data.communities;
}

// Generate layout
async function getGraphLayout(layoutType: string): Promise<GraphLayout> {
  const response = await fetch('/graph/layout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ layout_type: layoutType })
  });
  return response.json();
}
```

## Centrality Metrics Explained

### Degree Centrality

Measures the number of direct connections:

- **In-Degree**: Number of incoming citations/references
- **Out-Degree**: Number of outgoing citations/references
- **Total Degree**: Sum of in-degree and out-degree

**Use Cases**:
- Identify highly cited papers (high in-degree)
- Find comprehensive surveys (high out-degree)
- Discover hub resources (high total degree)

### Betweenness Centrality

Measures how often a resource lies on shortest paths between other resources:

- **Range**: 0.0 to 1.0
- **High Values**: Resource is a bridge between communities
- **Low Values**: Resource is peripheral

**Use Cases**:
- Identify bridging papers that connect different research areas
- Find resources that facilitate knowledge transfer
- Discover interdisciplinary work

### PageRank

Measures importance based on link structure (like Google's algorithm):

- **Range**: 0.0 to 1.0 (normalized)
- **Damping Factor**: Probability of following links (default: 0.85)
- **High Values**: Resource is cited by other important resources

**Use Cases**:
- Rank papers by importance
- Identify seminal works
- Prioritize reading list

## Community Detection

### Louvain Algorithm

Hierarchical community detection algorithm that maximizes modularity:

**Parameters**:
- **Resolution**: Controls community granularity
  - `< 1.0`: Fewer, larger communities
  - `= 1.0`: Default granularity
  - `> 1.0`: More, smaller communities

**Modularity Score**:
- **Range**: -0.5 to 1.0
- **> 0.3**: Significant community structure
- **> 0.7**: Strong community structure

**Use Cases**:
- Discover research clusters
- Identify related topics
- Organize knowledge base
- Find collaboration networks

### Interpreting Results

```python
# Analyze community structure
communities = detect_communities(resolution=1.0)

# Find largest community
largest = max(communities['communities'], key=lambda c: c['size'])
print(f"Largest community: {largest['size']} resources")

# Check modularity
if communities['modularity'] > 0.3:
    print("Significant community structure detected")
else:
    print("Weak community structure")

# Analyze community sizes
sizes = [c['size'] for c in communities['communities']]
print(f"Average community size: {sum(sizes) / len(sizes):.1f}")
```

## Graph Visualization

### Layout Algorithms

#### Force-Directed Layout (Fruchterman-Reingold)

Simulates physical forces between nodes:

- **Attractive Forces**: Between connected nodes
- **Repulsive Forces**: Between all nodes
- **Result**: Clusters emerge naturally

**Best For**:
- General-purpose visualization
- Discovering clusters
- Medium-sized graphs (< 500 nodes)

#### Hierarchical Layout (Kamada-Kawai)

Minimizes energy based on graph-theoretic distances:

- **Preserves Distances**: Shortest path distances reflected in layout
- **Hierarchical Structure**: Natural hierarchy emerges
- **Result**: Tree-like or layered structure

**Best For**:
- Citation networks
- Dependency graphs
- Hierarchical relationships

#### Circular Layout

Arranges nodes in a circle:

- **Simple**: Easy to implement and understand
- **Uniform**: All nodes equally spaced
- **Result**: Clean, symmetric layout

**Best For**:
- Small graphs (< 50 nodes)
- Highlighting connections
- Comparing graph structures

### Rendering with D3.js

```javascript
import * as d3 from 'd3';

async function renderGraph(layoutType) {
  // Get layout from API
  const layout = await getGraphLayout(layoutType);
  
  // Create SVG
  const svg = d3.select('#graph')
    .append('svg')
    .attr('width', 1000)
    .attr('height', 1000);
  
  // Draw edges
  svg.selectAll('line')
    .data(layout.edges)
    .enter()
    .append('line')
    .attr('x1', d => layout.nodes.find(n => n.resource_id === d.source).x)
    .attr('y1', d => layout.nodes.find(n => n.resource_id === d.source).y)
    .attr('x2', d => layout.nodes.find(n => n.resource_id === d.target).x)
    .attr('y2', d => layout.nodes.find(n => n.resource_id === d.target).y)
    .attr('stroke', '#999')
    .attr('stroke-width', d => d.weight);
  
  // Draw nodes
  svg.selectAll('circle')
    .data(layout.nodes)
    .enter()
    .append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', 5)
    .attr('fill', '#69b3a2');
  
  // Add labels
  svg.selectAll('text')
    .data(layout.nodes)
    .enter()
    .append('text')
    .attr('x', d => d.x + 8)
    .attr('y', d => d.y + 4)
    .text(d => d.label)
    .attr('font-size', '10px');
}
```

### Rendering with Cytoscape.js

```javascript
import cytoscape from 'cytoscape';

async function renderGraph(layoutType) {
  const layout = await getGraphLayout(layoutType);
  
  // Convert to Cytoscape format
  const elements = [
    ...layout.nodes.map(n => ({
      data: { id: n.resource_id, label: n.label },
      position: { x: n.x, y: n.y }
    })),
    ...layout.edges.map(e => ({
      data: { source: e.source, target: e.target, weight: e.weight }
    }))
  ];
  
  // Create graph
  const cy = cytoscape({
    container: document.getElementById('graph'),
    elements: elements,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#69b3a2',
          'label': 'data(label)'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 'data(weight)',
          'line-color': '#999'
        }
      }
    ],
    layout: { name: 'preset' }  // Use API-provided positions
  });
}
```

## Performance Optimization

### Caching Strategy

All graph intelligence operations use caching:

| Operation | Cache TTL | Cache Key |
|-----------|-----------|-----------|
| Centrality | 10 minutes | `centrality:{resource_ids}:{metric_types}` |
| Communities | 15 minutes | `communities:{resource_ids}:{resolution}` |
| Layout | 10 minutes | `layout:{resource_ids}:{layout_type}` |

### Incremental Updates

For large graphs, compute metrics incrementally:

```python
# Compute centrality for new resources only
new_resource_ids = ["uuid-10", "uuid-11"]
response = requests.get(
    "http://localhost:8000/graph/centrality",
    params={"resource_ids": new_resource_ids}
)
```

### Batch Processing

Process multiple operations in parallel:

```python
import asyncio
import aiohttp

async def compute_all_metrics(resource_ids):
    async with aiohttp.ClientSession() as session:
        # Compute centrality, communities, and layout in parallel
        tasks = [
            session.get(f"{base_url}/graph/centrality"),
            session.post(f"{base_url}/graph/communities", json={}),
            session.post(f"{base_url}/graph/layout", json={"layout_type": "force"})
        ]
        results = await asyncio.gather(*tasks)
        return results
```

## Troubleshooting

### Slow Centrality Computation

**Problem**: Centrality computation taking >1s

**Solutions**:
1. Check graph size (>1000 nodes may be slow)
2. Compute only needed metrics (not all three)
3. Use caching effectively
4. Consider computing for subset of resources

### Low Modularity Score

**Problem**: Modularity < 0.3 indicates weak community structure

**Solutions**:
1. Adjust resolution parameter (try 0.5 or 1.5)
2. Check if graph is too sparse or too dense
3. Verify edge weights are meaningful
4. Consider different community detection algorithm

### Layout Overlapping Nodes

**Problem**: Nodes overlap in visualization

**Solutions**:
1. Increase canvas size (width/height)
2. Try different layout algorithm
3. Filter to smaller subgraph
4. Adjust node size in rendering

## Best Practices

### 1. Choose Right Metrics

Select metrics based on your use case:

- **Discovery**: Use PageRank to find important resources
- **Navigation**: Use betweenness to find bridging resources
- **Organization**: Use communities to group related resources

### 2. Tune Resolution

Experiment with resolution parameter:

```python
# Try different resolutions
for resolution in [0.5, 1.0, 1.5, 2.0]:
    communities = detect_communities(resolution=resolution)
    print(f"Resolution {resolution}: {communities['num_communities']} communities")
```

### 3. Combine Metrics

Use multiple metrics together:

```python
# Find important bridging papers
metrics = get_centrality()
for metric in metrics['metrics']:
    if metric['pagerank'] > 0.01 and metric['betweenness_centrality'] > 0.05:
        print(f"Important bridge: {metric['resource_id']}")
```

### 4. Visualize Communities

Color nodes by community:

```javascript
const communities = await detectCommunities();
const communityMap = {};
communities.communities.forEach(c => {
  c.resource_ids.forEach(id => {
    communityMap[id] = c.community_id;
  });
});

// Color nodes by community
svg.selectAll('circle')
  .attr('fill', d => d3.schemeCategory10[communityMap[d.resource_id] % 10]);
```

## Integration Examples

### Research Dashboard

```python
# Build comprehensive research dashboard
def build_dashboard(resource_ids):
    # Get all metrics
    centrality = get_centrality(resource_ids)
    communities = detect_communities()
    layout = get_graph_layout("force")
    
    # Find top papers by PageRank
    top_papers = sorted(
        centrality['metrics'],
        key=lambda x: x['pagerank'],
        reverse=True
    )[:10]
    
    # Analyze community structure
    community_sizes = [c['size'] for c in communities['communities']]
    
    return {
        "top_papers": top_papers,
        "num_communities": communities['num_communities'],
        "modularity": communities['modularity'],
        "avg_community_size": sum(community_sizes) / len(community_sizes),
        "layout": layout
    }
```

### Citation Network Explorer

```typescript
interface CitationNetwork {
  metrics: CentralityMetrics[];
  communities: Community[];
  layout: GraphLayout;
}

async function exploreCitationNetwork(): Promise<CitationNetwork> {
  const [metrics, communities, layout] = await Promise.all([
    getCentrality(),
    detectCommunities(1.0),
    getGraphLayout('hierarchical')
  ]);
  
  return { metrics, communities, layout };
}

// Render interactive visualization
function renderCitationNetwork(network: CitationNetwork) {
  // Combine all data for rich visualization
  const enrichedNodes = network.layout.nodes.map(node => {
    const metric = network.metrics.find(m => m.resource_id === node.resource_id);
    const community = network.communities.find(c => 
      c.resource_ids.includes(node.resource_id)
    );
    
    return {
      ...node,
      pagerank: metric?.pagerank || 0,
      community_id: community?.community_id || -1
    };
  });
  
  // Render with size based on PageRank, color based on community
  renderGraph(enrichedNodes, network.layout.edges);
}
```

## Related Documentation

- [API Reference - Graph](../api/graph.md) - Complete API documentation
- [Architecture - Phase 20](../architecture/phase20-features.md) - Architecture details
- [Code Intelligence Guide](code-intelligence.md) - Hover information
- [Document Intelligence Guide](document-intelligence.md) - PDF processing

## Next Steps

1. **Explore AI Planning**: [AI Planning Guide](ai-planning.md)
2. **Try MCP Integration**: [MCP Integration Guide](mcp-integration.md)
3. **Build Visualizations**: Create interactive graph visualizations
4. **Analyze Your Data**: Discover patterns in your knowledge base
