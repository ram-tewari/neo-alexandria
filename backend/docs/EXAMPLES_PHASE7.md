# Phase 7: Collection Management Examples

This document provides practical examples for using the Collection Management features in Neo Alexandria 2.0.

## Table of Contents
- [Basic Collection Operations](#basic-collection-operations)
- [Resource Membership Management](#resource-membership-management)
- [Hierarchical Collections](#hierarchical-collections)
- [Collection Recommendations](#collection-recommendations)
- [Access Control and Visibility](#access-control-and-visibility)
- [Integration Examples](#integration-examples)
- [Advanced Use Cases](#advanced-use-cases)

## Basic Collection Operations

### Create a Collection

```bash
# Create a simple public collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research papers and articles",
    "visibility": "public"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research papers and articles",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "resources": []
}
```

### Get Collection Details

```bash
# Retrieve collection with member resources
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research papers and articles",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 2,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z",
  "resources": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Deep Learning Fundamentals",
      "creator": "John Doe",
      "quality_score": 0.92
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Neural Network Architectures",
      "creator": "Jane Smith",
      "quality_score": 0.88
    }
  ]
}
```

### Update Collection Metadata

```bash
# Update collection name and description
curl -X PUT http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Machine Learning",
    "description": "Updated collection focusing on advanced ML topics",
    "visibility": "private"
  }'
```

### Delete a Collection

```bash
# Delete collection (and all subcollections)
curl -X DELETE http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000
```

### List Collections

```bash
# List all accessible collections
curl "http://127.0.0.1:8000/collections"

# Filter by owner
curl "http://127.0.0.1:8000/collections?owner_id=user123"

# Filter by visibility
curl "http://127.0.0.1:8000/collections?visibility=public&limit=10"

# Pagination
curl "http://127.0.0.1:8000/collections?page=2&limit=25"
```

## Resource Membership Management

### Add Resources to Collection

```bash
# Add single resource
curl -X POST http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["660e8400-e29b-41d4-a716-446655440001"]
  }'

# Add multiple resources (batch operation)
curl -X POST http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "660e8400-e29b-41d4-a716-446655440001",
      "770e8400-e29b-41d4-a716-446655440002",
      "880e8400-e29b-41d4-a716-446655440003"
    ]
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research papers and articles",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 3,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:10:00Z",
  "resources": []
}
```

### Remove Resources from Collection

```bash
# Remove single resource
curl -X DELETE http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["660e8400-e29b-41d4-a716-446655440001"]
  }'

# Remove multiple resources (batch operation)
curl -X DELETE http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "660e8400-e29b-41d4-a716-446655440001",
      "770e8400-e29b-41d4-a716-446655440002"
    ]
  }'
```

## Hierarchical Collections

### Create Nested Collections

```bash
# Create parent collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science",
    "description": "Top-level CS collection",
    "visibility": "public"
  }'

# Create child collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "description": "ML subset of CS",
    "parent_id": "550e8400-e29b-41d4-a716-446655440000",
    "visibility": "public"
  }'

# Create grandchild collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning",
    "description": "DL subset of ML",
    "parent_id": "660e8400-e29b-41d4-a716-446655440001",
    "visibility": "public"
  }'
```

### Move Collection to Different Parent

```bash
# Update parent_id to move collection
curl -X PUT http://127.0.0.1:8000/collections/770e8400-e29b-41d4-a716-446655440002 \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": "880e8400-e29b-41d4-a716-446655440003"
  }'

# Make collection top-level (remove parent)
curl -X PUT http://127.0.0.1:8000/collections/770e8400-e29b-41d4-a716-446655440002 \
  -H "Content-Type: application/json" \
  -d '{
    "parent_id": null
  }'
```

## Collection Recommendations

### Get Similar Resources and Collections

```bash
# Get all recommendations
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations"
```

**Response:**
```json
{
  "resources": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "title": "Advanced Neural Networks",
      "similarity": 0.92
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "title": "Reinforcement Learning Basics",
      "similarity": 0.87
    }
  ],
  "collections": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "name": "AI Research Papers",
      "similarity": 0.85
    },
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440007",
      "name": "Neural Network Architectures",
      "similarity": 0.82
    }
  ]
}
```

### Get Only Resource Recommendations

```bash
# Get resource recommendations only
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations?include_collections=false&limit=20"
```

### Get Only Collection Recommendations

```bash
# Get collection recommendations only
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/recommendations?include_resources=false&limit=5"
```

### Get Collection Embedding

```bash
# Retrieve aggregate embedding vector
curl "http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000/embedding"
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 768
}
```

## Access Control and Visibility

### Create Private Collection

```bash
# Private collection (default)
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Private Research",
    "description": "Personal research notes",
    "visibility": "private"
  }'
```

### Create Public Collection

```bash
# Public collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Public Reading List",
    "description": "Recommended papers for beginners",
    "visibility": "public"
  }'
```

### Change Collection Visibility

```bash
# Make collection public
curl -X PUT http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "visibility": "public"
  }'

# Make collection private
curl -X PUT http://127.0.0.1:8000/collections/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "visibility": "private"
  }'
```

## Integration Examples

### Python Client Example

```python
import requests
from typing import List, Dict, Optional

class CollectionClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        visibility: str = "private",
        parent_id: Optional[str] = None
    ) -> Dict:
        """Create a new collection."""
        url = f"{self.base_url}/collections"
        data = {
            "name": name,
            "description": description,
            "visibility": visibility,
            "parent_id": parent_id
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_collection(self, collection_id: str) -> Dict:
        """Get collection details."""
        url = f"{self.base_url}/collections/{collection_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def update_collection(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> Dict:
        """Update collection metadata."""
        url = f"{self.base_url}/collections/{collection_id}"
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if visibility is not None:
            data["visibility"] = visibility
        if parent_id is not None:
            data["parent_id"] = parent_id
        
        response = requests.put(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_collection(self, collection_id: str) -> None:
        """Delete a collection."""
        url = f"{self.base_url}/collections/{collection_id}"
        response = requests.delete(url)
        response.raise_for_status()
    
    def list_collections(
        self,
        owner_id: Optional[str] = None,
        visibility: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict:
        """List collections with filtering."""
        url = f"{self.base_url}/collections"
        params = {"page": page, "limit": limit}
        if owner_id:
            params["owner_id"] = owner_id
        if visibility:
            params["visibility"] = visibility
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def add_resources(
        self,
        collection_id: str,
        resource_ids: List[str]
    ) -> Dict:
        """Add resources to collection."""
        url = f"{self.base_url}/collections/{collection_id}/resources"
        data = {"resource_ids": resource_ids}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def remove_resources(
        self,
        collection_id: str,
        resource_ids: List[str]
    ) -> Dict:
        """Remove resources from collection."""
        url = f"{self.base_url}/collections/{collection_id}/resources"
        data = {"resource_ids": resource_ids}
        response = requests.delete(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_recommendations(
        self,
        collection_id: str,
        limit: int = 10,
        include_resources: bool = True,
        include_collections: bool = True
    ) -> Dict:
        """Get recommendations for a collection."""
        url = f"{self.base_url}/collections/{collection_id}/recommendations"
        params = {
            "limit": limit,
            "include_resources": include_resources,
            "include_collections": include_collections
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_embedding(self, collection_id: str) -> Dict:
        """Get collection aggregate embedding."""
        url = f"{self.base_url}/collections/{collection_id}/embedding"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# Usage Examples
client = CollectionClient()

# Create a collection
collection = client.create_collection(
    name="Machine Learning Papers",
    description="Curated ML research",
    visibility="public"
)
print(f"Created collection: {collection['id']}")

# Add resources
client.add_resources(
    collection['id'],
    ["660e8400-e29b-41d4-a716-446655440001", "770e8400-e29b-41d4-a716-446655440002"]
)

# Get recommendations
recommendations = client.get_recommendations(collection['id'], limit=5)
print(f"Found {len(recommendations['resources'])} resource recommendations")
print(f"Found {len(recommendations['collections'])} collection recommendations")

# List all public collections
public_collections = client.list_collections(visibility="public")
print(f"Total public collections: {public_collections['total']}")
```

### JavaScript/TypeScript Example

```typescript
interface Collection {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id?: string;
  resource_count: number;
  created_at: string;
  updated_at: string;
  resources: ResourceSummary[];
}

interface ResourceSummary {
  id: string;
  title: string;
  creator?: string;
  quality_score: number;
}

interface Recommendations {
  resources: Array<{ id: string; title: string; similarity: number }>;
  collections: Array<{ id: string; name: string; similarity: number }>;
}

class CollectionService {
  constructor(private baseUrl: string = 'http://127.0.0.1:8000') {}

  async createCollection(data: {
    name: string;
    description?: string;
    visibility?: 'private' | 'shared' | 'public';
    parent_id?: string;
  }): Promise<Collection> {
    const response = await fetch(`${this.baseUrl}/collections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create collection');
    return response.json();
  }

  async getCollection(collectionId: string): Promise<Collection> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}`);
    if (!response.ok) throw new Error('Failed to fetch collection');
    return response.json();
  }

  async updateCollection(
    collectionId: string,
    updates: Partial<Pick<Collection, 'name' | 'description' | 'visibility' | 'parent_id'>>
  ): Promise<Collection> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (!response.ok) throw new Error('Failed to update collection');
    return response.json();
  }

  async deleteCollection(collectionId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete collection');
  }

  async listCollections(options: {
    owner_id?: string;
    visibility?: string;
    page?: number;
    limit?: number;
  } = {}): Promise<{ items: Collection[]; total: number; page: number; limit: number }> {
    const params = new URLSearchParams();
    if (options.owner_id) params.append('owner_id', options.owner_id);
    if (options.visibility) params.append('visibility', options.visibility);
    if (options.page) params.append('page', options.page.toString());
    if (options.limit) params.append('limit', options.limit.toString());

    const response = await fetch(`${this.baseUrl}/collections?${params}`);
    if (!response.ok) throw new Error('Failed to list collections');
    return response.json();
  }

  async addResources(collectionId: string, resourceIds: string[]): Promise<Collection> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}/resources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource_ids: resourceIds })
    });
    if (!response.ok) throw new Error('Failed to add resources');
    return response.json();
  }

  async removeResources(collectionId: string, resourceIds: string[]): Promise<Collection> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}/resources`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource_ids: resourceIds })
    });
    if (!response.ok) throw new Error('Failed to remove resources');
    return response.json();
  }

  async getRecommendations(
    collectionId: string,
    options: {
      limit?: number;
      include_resources?: boolean;
      include_collections?: boolean;
    } = {}
  ): Promise<Recommendations> {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.include_resources !== undefined) {
      params.append('include_resources', options.include_resources.toString());
    }
    if (options.include_collections !== undefined) {
      params.append('include_collections', options.include_collections.toString());
    }

    const response = await fetch(
      `${this.baseUrl}/collections/${collectionId}/recommendations?${params}`
    );
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return response.json();
  }

  async getEmbedding(collectionId: string): Promise<{ embedding: number[]; dimension: number }> {
    const response = await fetch(`${this.baseUrl}/collections/${collectionId}/embedding`);
    if (!response.ok) throw new Error('Failed to fetch embedding');
    return response.json();
  }
}

// Usage Examples
const collectionService = new CollectionService();

// Create and populate a collection
async function createMLCollection() {
  const collection = await collectionService.createCollection({
    name: 'Machine Learning Papers',
    description: 'Curated ML research',
    visibility: 'public'
  });

  await collectionService.addResources(collection.id, [
    '660e8400-e29b-41d4-a716-446655440001',
    '770e8400-e29b-41d4-a716-446655440002'
  ]);

  const recommendations = await collectionService.getRecommendations(collection.id, {
    limit: 10
  });

  console.log(`Created collection with ${collection.resource_count} resources`);
  console.log(`Found ${recommendations.resources.length} similar resources`);
}

// List and filter collections
async function listPublicCollections() {
  const result = await collectionService.listCollections({
    visibility: 'public',
    limit: 20
  });

  console.log(`Found ${result.total} public collections`);
  result.items.forEach(col => {
    console.log(`- ${col.name} (${col.resource_count} resources)`);
  });
}
```

## Advanced Use Cases

### Building a Research Workflow

```python
def build_research_workflow(client: CollectionClient):
    """Create a hierarchical research organization."""
    
    # Create top-level collection
    research = client.create_collection(
        name="PhD Research",
        description="All research materials",
        visibility="private"
    )
    
    # Create topic-specific subcollections
    ml_collection = client.create_collection(
        name="Machine Learning",
        parent_id=research['id'],
        visibility="private"
    )
    
    nlp_collection = client.create_collection(
        name="Natural Language Processing",
        parent_id=research['id'],
        visibility="private"
    )
    
    # Create reading lists
    must_read = client.create_collection(
        name="Must-Read Papers",
        parent_id=ml_collection['id'],
        visibility="private"
    )
    
    # Add resources to collections
    # ... add resources ...
    
    return {
        'research': research,
        'ml': ml_collection,
        'nlp': nlp_collection,
        'must_read': must_read
    }
```

### Discovering Related Content

```python
def discover_related_content(client: CollectionClient, collection_id: str):
    """Find and add related resources to a collection."""
    
    # Get recommendations
    recommendations = client.get_recommendations(
        collection_id,
        limit=20,
        include_resources=True,
        include_collections=False
    )
    
    # Filter high-similarity resources
    high_quality = [
        r for r in recommendations['resources']
        if r['similarity'] > 0.85
    ]
    
    print(f"Found {len(high_quality)} highly similar resources")
    
    # Optionally add them to collection
    if high_quality:
        resource_ids = [r['id'] for r in high_quality[:5]]
        client.add_resources(collection_id, resource_ids)
        print(f"Added {len(resource_ids)} resources to collection")
```

### Collection Analytics

```python
def analyze_collection(client: CollectionClient, collection_id: str):
    """Analyze collection composition and recommendations."""
    
    # Get collection details
    collection = client.get_collection(collection_id)
    
    # Calculate statistics
    total_resources = collection['resource_count']
    avg_quality = sum(r['quality_score'] for r in collection['resources']) / total_resources
    
    # Get recommendations
    recommendations = client.get_recommendations(collection_id, limit=50)
    
    # Analyze recommendation quality
    resource_similarities = [r['similarity'] for r in recommendations['resources']]
    collection_similarities = [c['similarity'] for c in recommendations['collections']]
    
    print(f"Collection: {collection['name']}")
    print(f"Resources: {total_resources}")
    print(f"Average Quality: {avg_quality:.2f}")
    print(f"Resource Recommendations: {len(resource_similarities)}")
    print(f"  Avg Similarity: {sum(resource_similarities)/len(resource_similarities):.2f}")
    print(f"Collection Recommendations: {len(collection_similarities)}")
    print(f"  Avg Similarity: {sum(collection_similarities)/len(collection_similarities):.2f}")
```

### Batch Collection Management

```python
def batch_organize_resources(
    client: CollectionClient,
    resource_ids: List[str],
    collection_mapping: Dict[str, List[str]]
):
    """Organize resources into multiple collections efficiently."""
    
    for collection_id, resource_subset in collection_mapping.items():
        # Add resources in batches of 100
        for i in range(0, len(resource_subset), 100):
            batch = resource_subset[i:i+100]
            client.add_resources(collection_id, batch)
            print(f"Added {len(batch)} resources to collection {collection_id}")
```

### Sharing Collections

```python
def share_collection(client: CollectionClient, collection_id: str):
    """Make a private collection public for sharing."""
    
    # Update visibility
    collection = client.update_collection(
        collection_id,
        visibility="public"
    )
    
    print(f"Collection '{collection['name']}' is now public")
    print(f"Share URL: http://127.0.0.1:8000/collections/{collection_id}")
    
    return collection
```

## Troubleshooting

### Collection Not Found

**Problem:** Getting 404 errors when accessing a collection.

**Solutions:**
1. Verify the collection ID is correct
2. Check if you have access (visibility rules)
3. Ensure the collection hasn't been deleted

### Circular Reference Error

**Problem:** Getting 400 error when setting parent_id.

**Solutions:**
1. Verify you're not creating a circular reference
2. Check the hierarchy depth (max 10 levels)
3. Ensure parent collection exists

### Embedding Not Available

**Problem:** Recommendations return 400 error about missing embedding.

**Solutions:**
1. Add resources with embeddings to the collection
2. Wait for embedding computation to complete
3. Verify resources have embeddings (check resource details)

### Permission Denied

**Problem:** Getting 403 errors when modifying a collection.

**Solutions:**
1. Verify you're the collection owner
2. Check authentication token is valid
3. Ensure you're not trying to modify a collection you don't own

## Best Practices

1. **Hierarchical Organization**: Use parent-child relationships for complex topic structures
2. **Batch Operations**: Add/remove multiple resources in single requests (up to 100)
3. **Visibility Management**: Start with private, make public when ready to share
4. **Regular Cleanup**: Remove outdated resources to keep embeddings relevant
5. **Recommendation Monitoring**: Check recommendations periodically to discover new content
6. **Descriptive Names**: Use clear, descriptive names for easy discovery
7. **Quality Curation**: Focus on high-quality resources for better recommendations
8. **Access Control**: Use appropriate visibility levels for different use cases
