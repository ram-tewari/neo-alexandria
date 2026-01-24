# Install Optimization Dependencies

## Required for Task 16.2: React Optimization

### react-window

The virtualized annotation list requires react-window for efficient rendering of large lists.

```bash
cd frontend
npm install react-window
npm install --save-dev @types/react-window
```

### Verification

After installation, verify the packages are in `package.json`:

```json
{
  "dependencies": {
    "react-window": "^1.8.10"
  },
  "devDependencies": {
    "@types/react-window": "^1.8.8"
  }
}
```

### Alternative: Use Without react-window

If you prefer not to install react-window, you can create a fallback implementation using:

1. **Radix UI ScrollArea** (already installed)
2. **CSS containment** for performance
3. **Intersection Observer** for lazy loading

Example fallback implementation:

```tsx
import { ScrollArea } from '@/components/ui/scroll-area';

export function SimpleAnnotationList({ annotations, ...props }) {
  return (
    <ScrollArea className="h-full" style={{ contain: 'layout' }}>
      {annotations.map((annotation) => (
        <AnnotationItem key={annotation.id} annotation={annotation} {...props} />
      ))}
    </ScrollArea>
  );
}
```

However, for optimal performance with 500+ annotations, react-window is recommended.
