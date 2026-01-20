# Upload System

A comprehensive file upload system with drag-and-drop, progress tracking, and status polling.

## Components

### UploadZone

Drag-and-drop file upload area with validation.

**Features:**
- Drag-and-drop file upload
- Click to browse files
- File type validation
- File size validation
- Visual feedback for drag state
- Keyboard accessible
- Error toast notifications

**Usage:**
```tsx
import { UploadZone } from './components/features/upload';

<UploadZone
  onFilesAdded={(files) => console.log('Files added:', files)}
  accept=".pdf,.epub,.txt"
  maxSize={50 * 1024 * 1024} // 50MB
  maxFiles={10}
/>
```

**Props:**
- `onFilesAdded: (files: File[]) => void` - Callback when valid files are added
- `accept?: string` - Accepted file types (default: `.pdf,.epub,.txt,.doc,.docx`)
- `maxSize?: number` - Maximum file size in bytes (default: 50MB)
- `maxFiles?: number` - Maximum number of files at once (default: 10)
- `disabled?: boolean` - Disable the upload zone

### UploadQueue

Displays upload queue with progress tracking and status.

**Features:**
- Progress summary with completion percentage
- Individual upload items with status
- Retry failed uploads
- Cancel in-progress uploads
- Clear completed uploads
- Animated transitions

**Usage:**
```tsx
import { UploadQueue } from './components/features/upload';

<UploadQueue
  queue={uploadQueue}
  onRetry={(id) => retryUpload(id)}
  onCancel={(id) => cancelUpload(id)}
  onClearCompleted={() => clearCompleted()}
/>
```

**Props:**
- `queue: UploadItem[]` - Array of upload items
- `onRetry?: (id: string) => void` - Callback to retry failed upload
- `onCancel?: (id: string) => void` - Callback to cancel upload
- `onClearCompleted?: () => void` - Callback to clear completed uploads

### UploadItem

Individual upload item with progress bar and actions.

**Features:**
- Status icon and label
- Progress bar with percentage
- Processing stage indicator
- Error message display
- Retry and cancel actions

**Usage:**
```tsx
import { UploadItem } from './components/features/upload';

<UploadItem
  item={uploadItem}
  onRetry={(id) => retryUpload(id)}
  onCancel={(id) => cancelUpload(id)}
/>
```

## Hooks

### useUploadQueue

Manages upload queue with concurrent uploads and status polling.

**Features:**
- Concurrent upload management (max 3 by default)
- Upload progress tracking
- Status polling with configurable interval
- Automatic retry on network errors
- Toast notifications for success/failure
- Abort controller for cancellation

**Usage:**
```tsx
import { useUploadQueue } from './lib/hooks';

const {
  queue,
  addFiles,
  addURL,
  retryUpload,
  cancelUpload,
  clearCompleted,
  clearAll,
  activeCount,
} = useUploadQueue({
  maxConcurrent: 3,
  pollInterval: 5000, // 5 seconds
  pollTimeout: 300000, // 5 minutes
  onUploadComplete: (item) => console.log('Upload complete:', item),
  onUploadError: (item, error) => console.error('Upload error:', error),
});

// Add files
addFiles([file1, file2]);

// Add URL
addURL('https://example.com/document.pdf');

// Retry failed upload
retryUpload(uploadId);

// Cancel upload
cancelUpload(uploadId);

// Clear completed uploads
clearCompleted();
```

**Options:**
- `maxConcurrent?: number` - Maximum concurrent uploads (default: 3)
- `pollInterval?: number` - Status polling interval in ms (default: 5000)
- `pollTimeout?: number` - Maximum polling time in ms (default: 300000)
- `onUploadComplete?: (item: UploadItem) => void` - Callback on upload completion
- `onUploadError?: (item: UploadItem, error: string) => void` - Callback on upload error

**Return Value:**
- `queue: UploadItem[]` - Array of upload items
- `addFiles: (files: File[]) => void` - Add files to queue
- `addURL: (url: string) => void` - Add URL to queue
- `retryUpload: (id: string) => void` - Retry failed upload
- `cancelUpload: (id: string) => void` - Cancel upload
- `clearCompleted: () => void` - Clear completed uploads
- `clearAll: () => void` - Clear all uploads
- `activeCount: number` - Number of active uploads

## Upload Flow

1. **File Selection**: User drags files or clicks to browse
2. **Validation**: Files are validated for type and size
3. **Queue Addition**: Valid files are added to the upload queue
4. **Upload**: Files are uploaded with progress tracking (max 3 concurrent)
5. **Processing**: Backend processes the uploaded resource
6. **Status Polling**: Frontend polls status every 5 seconds
7. **Completion**: Upload marked as complete or failed

## Status States

- `pending` - Waiting to start upload
- `uploading` - File is being uploaded
- `processing` - Backend is processing the resource
- `completed` - Upload and processing complete
- `failed` - Upload or processing failed

## Processing Stages

- `downloading` - Backend is downloading content
- `extracting` - Backend is extracting metadata
- `analyzing` - Backend is analyzing content

## Error Handling

- File validation errors show toast notifications
- Upload errors display in the upload item
- Network errors trigger automatic retry
- Timeout after 5 minutes of polling
- User can manually retry failed uploads

## Accessibility

- Keyboard navigation support
- ARIA labels and roles
- Screen reader announcements
- Focus management
- Visible focus indicators

## Responsive Design

- Mobile-friendly drag-and-drop
- Touch-friendly controls (44x44px minimum)
- Responsive layout adjustments
- Stacked layout on small screens

## Integration

The upload system integrates with:
- **Toast Context**: For notifications
- **Resources API**: For file upload and status polling
- **React Query**: For data fetching and caching (future)
- **Framer Motion**: For animations

## Future Enhancements

- URL ingestion component
- Batch metadata editing before upload
- Upload history and analytics
- Resume interrupted uploads
- Drag-and-drop reordering
- Upload presets/templates
