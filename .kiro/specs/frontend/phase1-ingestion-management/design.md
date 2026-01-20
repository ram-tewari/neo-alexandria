# Design Document - Phase 1: Ingestion Management

## Overview

Phase 1 implements the resource ingestion and management interface for Neo Alexandria 2.0. This design builds on the Phase 0 authentication foundation to create a complete "Admin" experience where users can ingest content via multiple methods and manage their resource library through a data table interface.

The design emphasizes real-time feedback through polling, strict type safety, and a component architecture that leverages shadcn/ui and TanStack libraries for a polished, performant user experience.

## Architecture

### High-Level Component Structure

```
src/features/resources/
├── api.ts                          # API client functions
├── hooks/
│   ├── useResourcePoller.ts        # Real-time status polling
│   ├── useResourceList.ts          # Table data fetching
│   └── useIngestResource.ts        # Ingestion mutation
├── components/
│   ├── ResourceDataTable.tsx       # Main table with @tanstack/react-table
│   ├── IngestionWizard.tsx         # Dialog with tabs
│   ├── StatusBadge.tsx             # Reusable status indicator
│   └── ResourceTableColumns.tsx    # Column definitions
└── types.ts                        # Feature-specific types

src/core/types/
└── resource.ts                     # Shared resource types

src/routes/
└── _auth.resources.tsx             # Protected route
```

### Data Flow

```mermaid
graph TD
    A[User clicks "Add Resource"] --> B[IngestionWizard Dialog Opens]
    B --> C[User selects tab: URL/File/Batch]
    C --> D[User submits form]
    D --> E[POST /api/v1/resources]
    E --> F{Response Status}
    F -->|201 Created| G[Close dialog, show toast]
    F -->|400/500 Error| H[Show error toast]
    G --> I[useResourcePoller starts]
    I --> J[Poll GET /resources/:id/status every 2s]
    J --> K{Status?}
    K -->|pending/processing| J
    K -->|completed| L[Invalidate resources list query]
    K -->|failed| M[Show error notification]
    L --> N[Table auto-refreshes]
```

### State Management Strategy

**TanStack Query** handles all server state:
- `['resources', 'list']` - Resource list with pagination/sorting
- `['resources', 'detail', id]` - Individual resource details
- `['resources', 'status', id]` - Polling for ingestion status

**Zustand** (from Phase 0) handles:
- Authentication state (already implemented)
- UI preferences (future: table column visibility, page size)

**React State** handles:
- Form inputs (controlled components)
- Dialog open/close state
- Local loading states

## Components and Interfaces

### 1. Type Definitions

**Location**: `src/core/types/resource.ts`

```typescript
export enum ResourceStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface Resource {
  id: string;
  title: string;
  url: string;
  status: ResourceStatus;
  quality_score: number | null;
  created_at: string;
  updated_at: string;
  classification_code: string | null;
  ingestion_error?: string;
}

export interface ResourceListResponse {
  items: Resource[];
  total: number;
}

export interface ResourceAccepted {
  id: string;
  status: string;
  title: string;
  ingestion_status: string;
}

export interface ResourceStatusResponse {
  id: string;
  status: ResourceStatus;
  progress?: number;
  error?: string;
}

export interface IngestResourcePayload {
  url: string;
  title?: string;
  type?: string;
}
```

### 2. API Client

**Location**: `src/features/resources/api.ts`

```typescript
import { apiClient } from '@/core/api/client';
import type { 
  Resource, 
  ResourceListResponse, 
  ResourceAccepted,
  ResourceStatusResponse,
  IngestResourcePayload 
} from '@/core/types/resource';

interface FetchResourcesParams {
  page: number;
  limit: number;
  sort?: string; // Format: "field:direction" e.g. "created_at:desc"
}

export async function fetchResources(
  params: FetchResourcesParams
): Promise<ResourceListResponse> {
  const { page, limit, sort } = params;
  const offset = (page - 1) * limit;
  
  const response = await apiClient.get<ResourceListResponse>('/resources', {
    params: {
      limit,
      offset,
      sort_by: sort?.split(':')[0] || 'created_at',
      sort_dir: sort?.split(':')[1] || 'desc'
    }
  });
  
  return response.data;
}

export async function ingestResource(
  payload: IngestResourcePayload
): Promise<ResourceAccepted> {
  const response = await apiClient.post<ResourceAccepted>('/resources', payload);
  return response.data;
}

export async function getResourceStatus(
  id: string
): Promise<ResourceStatusResponse> {
  const response = await apiClient.get<ResourceStatusResponse>(
    `/resources/${id}/status`
  );
  return response.data;
}

export async function getResource(id: string): Promise<Resource> {
  const response = await apiClient.get<Resource>(`/resources/${id}`);
  return response.data;
}
```

### 3. useResourcePoller Hook

**Location**: `src/features/resources/hooks/useResourcePoller.ts`

**Purpose**: Automatically poll resource status until completion or failure.

```typescript
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getResourceStatus } from '../api';
import { ResourceStatus } from '@/core/types/resource';

interface UseResourcePollerOptions {
  resourceId: string | null;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export function useResourcePoller({
  resourceId,
  onComplete,
  onError
}: UseResourcePollerOptions) {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['resources', 'status', resourceId],
    queryFn: () => getResourceStatus(resourceId!),
    enabled: !!resourceId,
    refetchInterval: (data) => {
      // Stop polling if completed or failed
      if (!data) return false;
      if (data.status === ResourceStatus.COMPLETED) {
        // Invalidate list to refresh table
        queryClient.invalidateQueries({ queryKey: ['resources', 'list'] });
        onComplete?.();
        return false;
      }
      if (data.status === ResourceStatus.FAILED) {
        onError?.(data.error || 'Ingestion failed');
        return false;
      }
      // Continue polling every 2 seconds
      return 2000;
    },
    refetchIntervalInBackground: true,
    staleTime: 0 // Always fetch fresh data
  });

  return {
    status: data?.status,
    progress: data?.progress,
    error: data?.error,
    isLoading
  };
}
```

### 4. useResourceList Hook

**Location**: `src/features/resources/hooks/useResourceList.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchResources } from '../api';

interface UseResourceListOptions {
  page: number;
  limit: number;
  sort?: string;
}

export function useResourceList({ page, limit, sort }: UseResourceListOptions) {
  return useQuery({
    queryKey: ['resources', 'list', { page, limit, sort }],
    queryFn: () => fetchResources({ page, limit, sort }),
    keepPreviousData: true, // Smooth pagination transitions
    staleTime: 30000 // Cache for 30 seconds
  });
}
```

### 5. useIngestResource Hook

**Location**: `src/features/resources/hooks/useIngestResource.ts`

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ingestResource } from '../api';
import type { IngestResourcePayload } from '@/core/types/resource';

export function useIngestResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ingestResource,
    onSuccess: () => {
      // Invalidate list to show new resource
      queryClient.invalidateQueries({ queryKey: ['resources', 'list'] });
    }
  });
}
```

### 6. StatusBadge Component

**Location**: `src/features/resources/components/StatusBadge.tsx`

```typescript
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { ResourceStatus } from '@/core/types/resource';

interface StatusBadgeProps {
  status: ResourceStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = {
    [ResourceStatus.PENDING]: {
      label: 'Pending',
      variant: 'secondary' as const,
      icon: Clock,
      className: 'bg-yellow-100 text-yellow-800 border-yellow-300'
    },
    [ResourceStatus.PROCESSING]: {
      label: 'Processing',
      variant: 'default' as const,
      icon: Loader2,
      className: 'bg-blue-100 text-blue-800 border-blue-300'
    },
    [ResourceStatus.COMPLETED]: {
      label: 'Ready',
      variant: 'default' as const,
      icon: CheckCircle2,
      className: 'bg-green-100 text-green-800 border-green-300'
    },
    [ResourceStatus.FAILED]: {
      label: 'Failed',
      variant: 'destructive' as const,
      icon: XCircle,
      className: 'bg-red-100 text-red-800 border-red-300'
    }
  };

  const { label, icon: Icon, className: statusClassName } = config[status];
  const isProcessing = status === ResourceStatus.PROCESSING;

  return (
    <Badge className={`${statusClassName} ${className}`}>
      <Icon 
        className={`mr-1 h-3 w-3 ${isProcessing ? 'animate-spin' : ''}`} 
      />
      {label}
    </Badge>
  );
}
```

### 7. ResourceDataTable Component

**Location**: `src/features/resources/components/ResourceDataTable.tsx`

**Key Features**:
- Uses `@tanstack/react-table` with manual pagination
- Server-side sorting by clicking column headers
- Skeleton loader during data fetching
- Responsive design with shadcn Table components

```typescript
import { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { useResourceList } from '../hooks/useResourceList';
import type { Resource } from '@/core/types/resource';

interface ResourceDataTableProps {
  page: number;
  limit: number;
  sort: string;
  onPageChange: (page: number) => void;
  onSortChange: (sort: string) => void;
}

export function ResourceDataTable({
  page,
  limit,
  sort,
  onPageChange,
  onSortChange
}: ResourceDataTableProps) {
  const { data, isLoading } = useResourceList({ page, limit, sort });

  const columns = useMemo<ColumnDef<Resource>[]>(
    () => [
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => <StatusBadge status={row.original.status} />
      },
      {
        accessorKey: 'title',
        header: 'Title',
        cell: ({ row }) => (
          <a
            href={`/resources/${row.original.id}`}
            className="font-semibold hover:underline"
          >
            {row.original.title}
          </a>
        )
      },
      {
        accessorKey: 'classification_code',
        header: 'Classification',
        cell: ({ row }) => (
          row.original.classification_code ? (
            <Badge variant="outline">{row.original.classification_code}</Badge>
          ) : (
            <span className="text-muted-foreground">—</span>
          )
        )
      },
      {
        accessorKey: 'quality_score',
        header: 'Quality',
        cell: ({ row }) => {
          const score = row.original.quality_score;
          if (score === null) return <span className="text-muted-foreground">—</span>;
          
          const color = score >= 0.7 ? 'text-green-600' : 
                       score >= 0.5 ? 'text-yellow-600' : 
                       'text-red-600';
          
          return <span className={color}>{score.toFixed(2)}</span>;
        }
      },
      {
        accessorKey: 'created_at',
        header: 'Date',
        cell: ({ row }) => new Date(row.original.created_at).toLocaleDateString()
      }
    ],
    []
  );

  const table = useReactTable({
    data: data?.items || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    manualSorting: true,
    pageCount: Math.ceil((data?.total || 0) / limit)
  });

  if (isLoading) {
    return <TableSkeleton />;
  }

  const totalPages = Math.ceil((data?.total || 0) / limit);

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Page {page} of {totalPages} ({data?.total || 0} total resources)
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-16 bg-muted animate-pulse rounded" />
      ))}
    </div>
  );
}
```

### 8. IngestionWizard Component

**Location**: `src/features/resources/components/IngestionWizard.tsx`

**Key Features**:
- Dialog with three tabs: Single URL, File Upload, Batch Paste
- Form validation using shadcn Form components
- Loading states during submission
- Toast notifications for success/error

```typescript
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { Plus, Loader2 } from 'lucide-react';
import { useIngestResource } from '../hooks/useIngestResource';

interface IngestionWizardProps {
  trigger?: React.ReactNode;
}

export function IngestionWizard({ trigger }: IngestionWizardProps) {
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('url');
  const { toast } = useToast();
  const { mutate: ingest, isLoading } = useIngestResource();

  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const onSubmit = (data: any) => {
    ingest(
      { url: data.url, title: data.title },
      {
        onSuccess: () => {
          toast({
            title: 'Ingestion Started',
            description: 'Your resource is being processed.'
          });
          setOpen(false);
          reset();
        },
        onError: (error: any) => {
          toast({
            title: 'Ingestion Failed',
            description: error.response?.data?.detail || 'An error occurred',
            variant: 'destructive'
          });
        }
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Resource
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Add Resource</DialogTitle>
          <DialogDescription>
            Choose a method to add resources to your library.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="url">Single URL</TabsTrigger>
            <TabsTrigger value="file">File Upload</TabsTrigger>
            <TabsTrigger value="batch">Batch Paste</TabsTrigger>
          </TabsList>

          <TabsContent value="url" className="space-y-4">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <Label htmlFor="url">Resource URL</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://example.com/article"
                  {...register('url', { required: 'URL is required' })}
                />
                {errors.url && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.url.message as string}
                  </p>
                )}
              </div>
              <div>
                <Label htmlFor="title">Title (Optional)</Label>
                <Input
                  id="title"
                  placeholder="Custom title for this resource"
                  {...register('title')}
                />
              </div>
              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ingest
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="file" className="space-y-4">
            <div>
              <Label htmlFor="file">Upload File</Label>
              <Input
                id="file"
                type="file"
                accept=".pdf,.txt"
                disabled
              />
              <p className="text-sm text-muted-foreground mt-2">
                File upload coming soon. Currently supports PDF and TXT files.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="batch" className="space-y-4">
            <div>
              <Label htmlFor="batch">URLs (one per line)</Label>
              <Textarea
                id="batch"
                placeholder="https://example.com/article1&#10;https://example.com/article2"
                rows={6}
                disabled
              />
              <p className="text-sm text-muted-foreground mt-2">
                Batch ingestion coming soon.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
```

### 9. Resources Route

**Location**: `src/routes/_auth.resources.tsx`

```typescript
import { useState } from 'react';
import { IngestionWizard } from '@/features/resources/components/IngestionWizard';
import { ResourceDataTable } from '@/features/resources/components/ResourceDataTable';

export default function ResourcesPage() {
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at:desc');
  const limit = 25;

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Resource Library</h1>
          <p className="text-muted-foreground">
            Manage and browse your knowledge base
          </p>
        </div>
        <IngestionWizard />
      </div>

      <ResourceDataTable
        page={page}
        limit={limit}
        sort={sort}
        onPageChange={setPage}
        onSortChange={setSort}
      />
    </div>
  );
}
```

## Data Models

### Resource Entity (Backend)

The frontend consumes the following resource structure from the backend:

```typescript
interface Resource {
  id: string;                    // UUID
  title: string;                 // Resource title
  url: string;                   // Source URL (mapped from 'source' field)
  status: ResourceStatus;        // Ingestion status
  quality_score: number | null;  // 0.0 to 1.0, null if not computed
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  classification_code: string | null; // Taxonomy code
  ingestion_error?: string;      // Error message if failed
  ingestion_started_at?: string; // When ingestion began
  ingestion_completed_at?: string; // When ingestion finished
}
```

### API Response Formats

**List Resources Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Article Title",
      "url": "https://example.com",
      "status": "completed",
      "quality_score": 0.85,
      "created_at": "2024-01-15T10:30:00Z",
      "classification_code": "CS.AI"
    }
  ],
  "total": 42
}
```

**Ingest Resource Response** (201 Created):
```json
{
  "id": "uuid",
  "status": "pending",
  "title": "Article Title",
  "ingestion_status": "pending"
}
```

**Resource Status Response**:
```json
{
  "id": "uuid",
  "status": "processing",
  "progress": 45,
  "error": null
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: API Client Parameter Correctness

*For any* valid combination of page, limit, and sort parameters, the API client SHALL construct the correct query string with offset calculated as (page - 1) * limit, sort_by extracted from the sort field before the colon, and sort_dir extracted after the colon.

**Validates: Requirements 1.7, 3.6**

### Property 2: Polling Interval Consistency

*For any* resource with status "pending" or "processing", the useResourcePoller hook SHALL call GET /api/v1/resources/{id}/status at 2-second intervals (±100ms tolerance for timing variations).

**Validates: Requirements 2.2**

### Property 3: Polling Termination

*For any* resource, when its status transitions to "completed" or "failed", the polling mechanism SHALL stop making further status requests.

**Validates: Requirements 2.3**

### Property 4: Status Badge Color Mapping

*For any* resource status value, the StatusBadge component SHALL render with the correct color scheme: "pending" → yellow (bg-yellow-100), "processing" → blue (bg-blue-100), "completed" → green (bg-green-100), "failed" → red (bg-red-100).

**Validates: Requirements 3.3, 6.2-6.5**

### Property 5: Quality Score Color Coding

*For any* quality_score value, the display SHALL use the correct color: score < 0.5 → red (text-red-600), 0.5 ≤ score < 0.7 → yellow (text-yellow-600), score ≥ 0.7 → green (text-green-600).

**Validates: Requirements 3.4**

## Error Handling

### API Error Handling

**Error Response Structure**:
```typescript
interface APIError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}
```

**Error Handling Strategy**:

1. **Network Errors** (No response from server):
   - Display toast: "Network error. Please check your connection."
   - Log error to console
   - Provide retry button in toast

2. **401 Unauthorized**:
   - Handled automatically by API client (from Phase 0)
   - Triggers token refresh
   - Retries original request
   - Redirects to login if refresh fails

3. **400 Bad Request**:
   - Display toast with backend error message
   - Highlight form field if validation error
   - Keep form data for user to correct

4. **429 Rate Limit**:
   - Extract `retry-after` header
   - Display toast: "Rate limit exceeded. Please try again in X seconds"
   - Disable submit button for X seconds

5. **500 Internal Server Error**:
   - Display toast: "Server error. Please try again later"
   - Log full error details to console
   - Provide "Report Issue" link

### Polling Error Handling

**Scenarios**:

1. **Status endpoint returns 404**:
   - Resource was deleted during polling
   - Stop polling
   - Display toast: "Resource no longer exists"
   - Remove from table

2. **Status endpoint returns error**:
   - Retry up to 3 times with exponential backoff
   - After 3 failures, stop polling
   - Display toast: "Unable to check status. Please refresh the page"

3. **Status changes to "failed"**:
   - Stop polling
   - Display error badge
   - Show error message in tooltip or detail view
   - Log ingestion_error to console

### Form Validation

**URL Validation**:
```typescript
const urlSchema = z.string()
  .url('Please enter a valid URL')
  .refine(
    (url) => url.startsWith('http://') || url.startsWith('https://'),
    'URL must start with http:// or https://'
  );
```

**File Validation**:
```typescript
const fileSchema = z.instanceof(File)
  .refine(
    (file) => file.size <= 10 * 1024 * 1024,
    'File must be less than 10MB'
  )
  .refine(
    (file) => ['application/pdf', 'text/plain'].includes(file.type),
    'Only PDF and TXT files are supported'
  );
```

## Testing Strategy

### Unit Tests

**Component Tests** (Vitest + React Testing Library):

1. **StatusBadge Component**:
   - Test each status renders correct color and icon
   - Test processing status shows spinning animation
   - Test accessibility (ARIA labels)

2. **IngestionWizard Component**:
   - Test tab switching
   - Test form validation (URL format, required fields)
   - Test submit button disabled during loading
   - Test success toast on 201 response
   - Test error toast on 400/500 response
   - Test dialog closes on successful submission

3. **ResourceDataTable Component**:
   - Test columns render correctly
   - Test pagination button states (first/last page)
   - Test skeleton loader during loading
   - Test empty state when no resources
   - Test row click navigation

**Hook Tests** (Vitest):

1. **useResourcePoller**:
   - Test polling starts for pending/processing status
   - Test polling stops for completed/failed status
   - Test 2-second interval
   - Test query invalidation on completion
   - Test error callback on failure

2. **useResourceList**:
   - Test query key includes page, limit, sort
   - Test keepPreviousData for smooth pagination
   - Test staleTime caching

3. **useIngestResource**:
   - Test mutation calls API with correct payload
   - Test query invalidation on success
   - Test error handling

**API Client Tests**:

1. **fetchResources**:
   - Test offset calculation: (page - 1) * limit
   - Test sort parameter parsing: "created_at:desc" → sort_by="created_at", sort_dir="desc"
   - Test query string construction

2. **ingestResource**:
   - Test POST request with correct payload
   - Test response parsing

3. **getResourceStatus**:
   - Test GET request to correct endpoint
   - Test response parsing

### Property-Based Tests

**Configuration**: Minimum 100 iterations per property test using fast-check library.

**Property 1: API Client Parameter Correctness**:
```typescript
// Feature: phase1-ingestion-management, Property 1
test('API client constructs correct query parameters', () => {
  fc.assert(
    fc.property(
      fc.integer({ min: 1, max: 100 }), // page
      fc.integer({ min: 1, max: 100 }), // limit
      fc.constantFrom('created_at:desc', 'created_at:asc', 'title:asc', 'title:desc'), // sort
      (page, limit, sort) => {
        const params = buildQueryParams({ page, limit, sort });
        const expectedOffset = (page - 1) * limit;
        const [sortBy, sortDir] = sort.split(':');
        
        expect(params.offset).toBe(expectedOffset);
        expect(params.sort_by).toBe(sortBy);
        expect(params.sort_dir).toBe(sortDir);
        expect(params.limit).toBe(limit);
      }
    ),
    { numRuns: 100 }
  );
});
```

**Property 2: Polling Interval Consistency**:
```typescript
// Feature: phase1-ingestion-management, Property 2
test('Poller maintains 2-second interval for pending/processing resources', async () => {
  fc.assert(
    fc.asyncProperty(
      fc.constantFrom('pending', 'processing'),
      async (status) => {
        const timestamps: number[] = [];
        const mockGetStatus = vi.fn(() => 
          Promise.resolve({ id: '123', status })
        );
        
        // Record timestamps of API calls
        mockGetStatus.mockImplementation(() => {
          timestamps.push(Date.now());
          return Promise.resolve({ id: '123', status });
        });
        
        // Run poller for 6 seconds
        await runPollerForDuration(mockGetStatus, 6000);
        
        // Check intervals between calls
        for (let i = 1; i < timestamps.length; i++) {
          const interval = timestamps[i] - timestamps[i - 1];
          expect(interval).toBeGreaterThanOrEqual(1900); // 2000ms - 100ms tolerance
          expect(interval).toBeLessThanOrEqual(2100); // 2000ms + 100ms tolerance
        }
      }
    ),
    { numRuns: 100 }
  );
});
```

**Property 3: Polling Termination**:
```typescript
// Feature: phase1-ingestion-management, Property 3
test('Poller stops for completed/failed resources', () => {
  fc.assert(
    fc.property(
      fc.constantFrom('completed', 'failed'),
      (finalStatus) => {
        const mockGetStatus = vi.fn()
          .mockResolvedValueOnce({ id: '123', status: 'processing' })
          .mockResolvedValueOnce({ id: '123', status: finalStatus });
        
        const { result } = renderHook(() => 
          useResourcePoller({ resourceId: '123' })
        );
        
        // Wait for status to change to final state
        waitFor(() => {
          expect(result.current.status).toBe(finalStatus);
        });
        
        // Verify no more calls after final status
        const callCountAtFinal = mockGetStatus.mock.calls.length;
        
        // Wait 5 more seconds
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Call count should not have increased
        expect(mockGetStatus.mock.calls.length).toBe(callCountAtFinal);
      }
    ),
    { numRuns: 100 }
  );
});
```

**Property 4: Status Badge Color Mapping**:
```typescript
// Feature: phase1-ingestion-management, Property 4
test('Status badges render with correct colors', () => {
  fc.assert(
    fc.property(
      fc.constantFrom('pending', 'processing', 'completed', 'failed'),
      (status) => {
        const { container } = render(<StatusBadge status={status} />);
        const badge = container.querySelector('[class*="bg-"]');
        
        const expectedColors = {
          pending: 'bg-yellow-100',
          processing: 'bg-blue-100',
          completed: 'bg-green-100',
          failed: 'bg-red-100'
        };
        
        expect(badge?.className).toContain(expectedColors[status]);
      }
    ),
    { numRuns: 100 }
  );
});
```

**Property 5: Quality Score Color Coding**:
```typescript
// Feature: phase1-ingestion-management, Property 5
test('Quality scores render with correct colors', () => {
  fc.assert(
    fc.property(
      fc.float({ min: 0, max: 1 }),
      (score) => {
        const { container } = render(<QualityCell score={score} />);
        const cell = container.querySelector('[class*="text-"]');
        
        let expectedColor: string;
        if (score < 0.5) {
          expectedColor = 'text-red-600';
        } else if (score < 0.7) {
          expectedColor = 'text-yellow-600';
        } else {
          expectedColor = 'text-green-600';
        }
        
        expect(cell?.className).toContain(expectedColor);
      }
    ),
    { numRuns: 100 }
  );
});
```

### Integration Tests

**End-to-End Flows**:

1. **Complete Ingestion Flow**:
   - Open ingestion wizard
   - Submit URL
   - Verify POST request sent
   - Verify dialog closes
   - Verify toast appears
   - Verify table refreshes
   - Verify polling starts
   - Mock status changes
   - Verify badge updates
   - Verify polling stops on completion

2. **Pagination Flow**:
   - Load initial page
   - Click "Next"
   - Verify API called with correct offset
   - Verify table updates
   - Verify "Previous" enabled
   - Navigate to last page
   - Verify "Next" disabled

3. **Error Recovery Flow**:
   - Submit invalid URL
   - Verify error toast
   - Correct URL
   - Resubmit
   - Verify success

### Test Coverage Goals

- **Unit Tests**: 80% code coverage
- **Property Tests**: All 5 properties implemented
- **Integration Tests**: All critical user flows covered
- **Component Tests**: All interactive components tested
- **Hook Tests**: All custom hooks tested

### Testing Tools

- **Test Runner**: Vitest
- **Component Testing**: React Testing Library
- **Property Testing**: fast-check
- **Mocking**: vitest/mock
- **Coverage**: vitest --coverage

### CI/CD Integration

- Run all tests on every commit
- Fail build if coverage drops below 80%
- Run property tests with 100 iterations in CI
- Generate coverage reports
- Block merge if tests fail
