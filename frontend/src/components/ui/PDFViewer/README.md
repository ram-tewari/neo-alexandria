# PDFViewer Component

## Overview

The PDFViewer component provides a full-featured PDF viewing experience with zoom controls, page navigation, and responsive design. It integrates with the react-pdf library to render PDF documents directly in the browser.

## Features

- **Page Navigation**: Previous/next buttons and page indicator
- **Zoom Controls**: 
  - Zoom in/out buttons
  - Preset zoom levels (75%, 100%, 125%, 150%)
  - Custom zoom range (50% - 200%)
- **Responsive Design**:
  - Mobile-optimized layout with stacked controls
  - Automatic scale adjustment for mobile devices
  - Touch-friendly controls (44x44px minimum)
- **Loading States**: Skeleton loaders for document and page loading
- **Error Handling**: User-friendly error messages with retry options
- **Accessibility**: Keyboard navigation and ARIA labels

## Usage

```tsx
import { PDFViewer } from '@/components/ui/PDFViewer';

function ContentTab({ resource }) {
  return (
    <div className="content-viewer">
      <PDFViewer 
        url={resource.url}
        initialPage={1}
        onPageChange={(page) => console.log('Page changed:', page)}
      />
    </div>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `url` | `string` | required | URL of the PDF document to display |
| `initialPage` | `number` | `1` | Initial page number to display |
| `onPageChange` | `(page: number) => void` | optional | Callback fired when page changes |

## Responsive Behavior

### Desktop (≥768px)
- Full toolbar with horizontal layout
- All controls visible and accessible
- Optimal zoom level: 100%

### Mobile (<768px)
- Stacked toolbar layout
- Touch-friendly controls (44x44px)
- Automatic zoom adjustment to 75%
- Width-constrained PDF rendering

## Keyboard Shortcuts

Currently, the component supports mouse/touch interaction. Future enhancements may include:
- Arrow keys for page navigation
- +/- keys for zoom control
- Home/End for first/last page

## Styling

The component uses CSS custom properties for theming:
- `--color-primary`: Primary accent color
- `--color-border`: Border colors
- `--color-background`: Background colors
- `--color-text-primary`: Primary text color
- `--color-text-secondary`: Secondary text color

## Dependencies

- `react-pdf`: PDF rendering library
- `pdfjs-dist`: PDF.js worker for document parsing

## Future Enhancements

- Annotation overlay support (Phase 2)
- Text selection and search
- Thumbnail navigation
- Full-screen mode
- Print functionality
- Download button

## Implementation Notes

- PDF.js worker is loaded from unpkg CDN
- Text layer and annotation layer are enabled by default
- Component handles responsive scaling automatically
- Error states provide user-friendly messages and recovery options
