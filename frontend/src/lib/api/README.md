# API Client Documentation

This directory contains typed API clients for interacting with the Neo Alexandria backend.

## Overview

All API clients are strongly typed using TypeScript interfaces that match the backend Pydantic models. Error handling is centralized using the `ApiError` class.

## API Clients

### Resources API (`resources.ts`)

Handles all resource-related operations:

- `list(params)` - List resources with pagination and filtering
- `get(id)` - Get a single resource by ID
- `create(data, options)` - Create a new resource (file or URL ingestion) with optional upload progress tracking
- `update(id, data)` - Update an existing resource
- `delete(id)` - Delete a resource
- `getStatus(id)` - Get resource ingestion status
- `batchUpdate(ids, data)` - Batch update multiple resources

**Example Usage:**

```typescript
import { resourcesApi } from '@/lib/api';

// List resources with filters
const response = await resourcesApi.list({
  limit: 20,
  offset: 0,
  classification_code: 'CS',
  min_quality: 0.7,
});

// Upload a file with progress tracking
const result = await resourcesApi.create(
  { file: myFile },
  {
    onUploadProgress: (progress) => {
      const percent = (progress.loaded / progress.total) * 100;
      console.log(`Upload progress: ${percent}%`);
    },
  }
);

// Poll for ingestion status
const status = await resourcesApi.getStatus(result.id);
```

### Quality API (`quality.ts`)

Handles quality-related operations:

- `getDetails(resourceId)` - Get detailed quality information for a resource

**Example Usage:**

```typescript
import { qualityApi } from '@/lib/api';

const quality = await qualityApi.getDetails('resource-id');
console.log(`Overall score: ${quality.overall_score}`);
console.log(`Dimensions:`, quality.dimensions);
```

### Graph API (`graph.ts`)

Handles knowledge graph operations:

- `getNeighbors(resourceId, limit)` - Get neighboring resources in the knowledge graph

**Example Usage:**

```typescript
import { graphApi } from '@/lib/api';

const neighbors = await graphApi.getNeighbors('resource-id', 10);
console.log(`Found ${neighbors.neighbors.length} related resources`);
```

## Type Definitions

All types are defined in `types.ts` and exported from the main index file:

```typescript
import {
  ResourceRead,
  ResourceListParams,
  QualityDetails,
  GraphNeighbor,
  ApiError,
} from '@/lib/api';
```

### Key Types

- `ResourceRead` - Full resource data from the backend
- `ResourceIngestRequest` - Data for creating a new resource
- `ResourceUpdate` - Data for updating a resource
- `ResourceListParams` - Query parameters for listing resources
- `ResourceListResponse` - Paginated list response
- `QualityDetails` - Quality metrics for a resource
- `GraphNeighbor` - Related resource in the knowledge graph
- `ApiError` - Custom error class with status and data

## Error Handling

All API clients use a centralized error handling function that converts HTTP errors into `ApiError` instances:

```typescript
try {
  const resource = await resourcesApi.get('invalid-id');
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.status}: ${error.message}`);
    console.error('Error data:', error.data);
  }
}
```

## Configuration

The API base URL is configured via environment variable:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If not set, it defaults to `http://127.0.0.1:8000`.

## React Query Integration

These API clients are designed to work seamlessly with React Query. See the query client configuration in `lib/query/queryClient.ts`.

**Example with React Query:**

```typescript
import { useQuery } from '@tanstack/react-query';
import { resourcesApi } from '@/lib/api';

function ResourceDetail({ id }: { id: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['resource', id],
    queryFn: () => resourcesApi.get(id),
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{data.title}</div>;
}
```

## Future Enhancements

- Add request cancellation support
- Implement retry logic with exponential backoff
- Add request deduplication
- Support for batch operations endpoint (when available on backend)
- WebSocket support for real-time updates
