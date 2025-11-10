# Collection Management API Guide

## Overview

The Collection Management API enables users to organize resources into curated collections with hierarchical organization, semantic recommendations, and access control.

## Quick Start

### Create a Collection

```bash
curl -X POST "http://localhost:8000/collections?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research",
    "visibility": "public"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "created_at": "2025-11-09T10:00:00Z",
  "updated_at": "2025-11-09T10:00:00Z",
  "resource_count": 0
}
```

### Add Resources to Collection

```bash
curl -X POST "http://localhost:8000/collections/{collection_id}/resources?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "resource-uuid-1",
      "resource-uuid-2",
      "resource-uuid-3"
    ]
  }'
```

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "added_count": 3,
  "total_resources": 3
}
```

### Get Collection with Resources

```bash
curl "http://localhost:8000/collections/{collection_id}?user_id=user123"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "created_at": "2025-11-09T10:00:00Z",
  "updated_at": "2025-11-09T10:00:00Z",
  "resource_count": 3,
  "resources": [
    {
      "id": "resource-uuid-1",
      "title": "Deep Learning Fundamentals",
      "quality_score": 0.92,
      "classification_code": "004"
    }
  ],
  "subcollections": []
}
```

### Get Recommendations

```bash
curl "http://localhost:8000/collections/{collection_id}/recommendations?user_id=user123&limit=10"
```

**Response:**
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_recommendations": [
    {
      "id": "resource-uuid-4",
      "title": "Neural Networks in Practice",
      "type": "resource",
      "relevance_score": 0.87,
      "description": "Practical guide to neural networks",
      "quality_score": 0.85
    }
  ],
  "collection_recommendations": [
    {
      "id": "collection-uuid-2",
      "title": "Deep Learning Resources",
      "type": "collection",
      "relevance_score": 0.82,
      "description": "Comprehensive DL collection",
      "quality_score": null
    }
  ]
}
```

## API Endpoints

### Collection CRUD

#### POST /collections
Create a new collection.

**Query Parameters:**
- `user_id` (required): Owner user ID

**Request Body:**
```json
{
  "name": "string (1-255 chars, required)",
  "description": "string (optional)",
  "visibility": "private|shared|public (default: private)",
  "parent_id": "uuid (optional)"
}
```

**Response:** 201 Created with CollectionResponse

---

#### GET /collections
List collections with filtering and pagination.

**Query Parameters:**
- `user_id` (optional): User ID for access control
- `owner_filter` (optional): Filter by owner ID
- `visibility_filter` (optional): Filter by visibility
- `page` (default: 1): Page number
- `limit` (default: 50, max: 100): Items per page

**Response:** CollectionListResponse

---

#### GET /collections/{id}
Retrieve a specific collection with resources.

**Query Parameters:**
- `user_id` (optional): User ID for access control

**Response:** CollectionDetailResponse

---

#### PUT /collections/{id}
Update collection metadata.

**Query Parameters:**
- `user_id` (required): User ID (must be owner)

**Request Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "visibility": "private|shared|public (optional)",
  "parent_id": "uuid (optional)"
}
```

**Response:** CollectionResponse

---

#### DELETE /collections/{id}
Delete a collection (cascades to subcollections).

**Query Parameters:**
- `user_id` (required): User ID (must be owner)

**Response:** 204 No Content

---

### Resource Membership

#### POST /collections/{id}/resources
Add resources to collection (batch operation).

**Query Parameters:**
- `user_id` (required): User ID (must be owner)

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2", ...] // 1-100 resources
}
```

**Response:** ResourceMembershipResponse

**Background Task:** Recomputes collection embedding

---

#### DELETE /collections/{id}/resources
Remove resources from collection (batch operation).

**Query Parameters:**
- `user_id` (required): User ID (must be owner)

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2", ...] // 1-100 resources
}
```

**Response:** ResourceMembershipResponse

**Background Task:** Recomputes collection embedding

---

### Recommendations

#### GET /collections/{id}/recommendations
Get semantic recommendations based on collection.

**Query Parameters:**
- `user_id` (optional): User ID for access control
- `limit` (default: 10, range: 1-50): Recommendations per type

**Response:** CollectionRecommendationsResponse

---

## Access Control

### Visibility Levels

- **private**: Only owner can access
- **shared**: Owner + explicit permissions (future: permission system)
- **public**: All authenticated users can access

### Operations by Role

| Operation | Owner | Non-Owner (Public) | Non-Owner (Private) |
|-----------|-------|-------------------|---------------------|
| View | ✅ | ✅ | ❌ |
| Update | ✅ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ |
| Add Resources | ✅ | ❌ | ❌ |
| Remove Resources | ✅ | ❌ | ❌ |
| Get Recommendations | ✅ | ✅ | ❌ |

## Hierarchical Collections

### Create Nested Collection

```bash
# Create parent
curl -X POST "http://localhost:8000/collections?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science",
    "visibility": "public"
  }'

# Create child
curl -X POST "http://localhost:8000/collections?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "visibility": "public",
    "parent_id": "parent-collection-uuid"
  }'
```

### Hierarchy Rules

- Maximum depth: 10 levels
- Circular references prevented automatically
- Parent must belong to same owner
- Deleting parent cascades to all children

## Aggregate Embeddings

### How It Works

1. When resources are added/removed, embedding recomputation is triggered
2. System computes mean vector from all member resource embeddings
3. Embedding used for semantic recommendations
4. Empty collections have null embedding

### Automatic Recomputation

Embeddings are automatically recomputed when:
- Resources are added to collection
- Resources are removed from collection
- Triggered as background task (non-blocking)

## Recommendations

### Resource Recommendations

- Based on cosine similarity between collection and resource embeddings
- Excludes resources already in the collection
- Sorted by relevance score (0.0-1.0)
- Configurable limit (1-50)

### Collection Recommendations

- Based on cosine similarity between collection embeddings
- Only recommends public collections
- Excludes the source collection
- Sorted by relevance score (0.0-1.0)
- Configurable limit (1-50)

## Error Handling

### Common Errors

**400 Bad Request**
- Invalid collection name (empty or >255 chars)
- Invalid visibility value
- Invalid UUID format
- Batch size exceeds 100 resources
- Circular reference detected

**403 Forbidden**
- User is not collection owner (for write operations)
- Collection is private and user is not owner

**404 Not Found**
- Collection does not exist
- Parent collection does not exist
- Resources not found

## Best Practices

### Collection Organization

1. **Use Hierarchies**: Organize related collections under parent collections
2. **Descriptive Names**: Use clear, descriptive collection names
3. **Public vs Private**: Make educational collections public, personal ones private
4. **Batch Operations**: Add/remove multiple resources at once for efficiency

### Performance Tips

1. **Limit Collection Size**: Keep collections under 1000 resources
2. **Batch Operations**: Use batch add/remove instead of individual operations
3. **Pagination**: Use pagination for large collection lists
4. **Background Tasks**: Embedding recomputation happens in background

### Recommendation Quality

1. **Add Quality Resources**: Higher quality resources improve recommendations
2. **Diverse Content**: Include diverse resources for better semantic coverage
3. **Regular Updates**: Keep collections current for relevant recommendations
4. **Minimum Size**: Collections need at least 3-5 resources for good recommendations

## Python SDK Example

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "user123"

# Create collection
response = requests.post(
    f"{BASE_URL}/collections",
    params={"user_id": USER_ID},
    json={
        "name": "My Research Collection",
        "description": "Important papers for my research",
        "visibility": "private"
    }
)
collection = response.json()
collection_id = collection["id"]

# Add resources
response = requests.post(
    f"{BASE_URL}/collections/{collection_id}/resources",
    params={"user_id": USER_ID},
    json={
        "resource_ids": ["resource-uuid-1", "resource-uuid-2"]
    }
)
print(f"Added {response.json()['added_count']} resources")

# Get recommendations
response = requests.get(
    f"{BASE_URL}/collections/{collection_id}/recommendations",
    params={"user_id": USER_ID, "limit": 10}
)
recommendations = response.json()
print(f"Found {len(recommendations['resource_recommendations'])} resource recommendations")
```

## JavaScript SDK Example

```javascript
const BASE_URL = 'http://localhost:8000';
const USER_ID = 'user123';

// Create collection
const createResponse = await fetch(`${BASE_URL}/collections?user_id=${USER_ID}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'My Research Collection',
    description: 'Important papers for my research',
    visibility: 'private'
  })
});
const collection = await createResponse.json();

// Add resources
const addResponse = await fetch(
  `${BASE_URL}/collections/${collection.id}/resources?user_id=${USER_ID}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resource_ids: ['resource-uuid-1', 'resource-uuid-2']
    })
  }
);
const result = await addResponse.json();
console.log(`Added ${result.added_count} resources`);

// Get recommendations
const recsResponse = await fetch(
  `${BASE_URL}/collections/${collection.id}/recommendations?user_id=${USER_ID}&limit=10`
);
const recommendations = await recsResponse.json();
console.log(`Found ${recommendations.resource_recommendations.length} recommendations`);
```

## Troubleshooting

### No Recommendations Returned

**Problem**: Recommendations endpoint returns empty arrays.

**Solutions**:
- Ensure collection has at least 3-5 resources
- Verify resources have embeddings (check resource.embedding field)
- Wait for background embedding computation to complete
- Check that other resources/collections exist in the system

### Circular Reference Error

**Problem**: Cannot set parent_id due to circular reference.

**Solutions**:
- Verify the parent chain doesn't already include this collection
- Check hierarchy depth (max 10 levels)
- Remove existing parent before setting new one

### Access Denied Error

**Problem**: Cannot access or modify collection.

**Solutions**:
- Verify user_id matches collection owner_id
- Check collection visibility (private collections only accessible to owner)
- Ensure user_id is provided in query parameters

### Batch Operation Fails

**Problem**: Adding/removing resources fails.

**Solutions**:
- Verify all resource UUIDs are valid
- Check batch size (max 100 resources)
- Ensure all resources exist in database
- Verify user is collection owner

## Support

For issues or questions:
- Check [PHASE7_IMPLEMENTATION_SUMMARY.md](../PHASE7_IMPLEMENTATION_SUMMARY.md) for technical details
- Review test cases in `tests/test_phase7_collections.py`
- Consult the main [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
