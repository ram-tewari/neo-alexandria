# Resource Detail Page

This directory contains the resource detail page implementation for Phase 1, Task 8.

## Components

### ResourceDetailPage
Main page component that orchestrates the resource detail view.

**Features:**
- Route: `/resources/:id`
- Fetches resource data with React Query
- URL-synced tab navigation
- Animated tab transitions
- Error handling and loading states

### Breadcrumbs
Navigation breadcrumb component showing the path to the current resource.

**Features:**
- ARIA-compliant navigation
- Responsive truncation
- Keyboard accessible

### ResourceHeader
Displays resource title, metadata, and subject tags.

**Features:**
- Title with proper typography
- Metadata icons (creator, type, date, language)
- Subject tags as styled pills
- Responsive layout

### ResourceTabs
Tab navigation component with keyboard support.

**Features:**
- 5 tabs: Content, Annotations, Metadata, Graph, Quality
- ARIA-compliant tab interface
- Keyboard navigation (arrow keys, Home, End)
- URL synchronization
- Visual active state
- Responsive (horizontal on desktop, vertical on mobile)

### FloatingActionButton
Floating action button that appears on scroll.

**Features:**
- Shows when scrolled past 200px
- Animated scale transition
- Opens resource URL or scrolls to content
- Fixed position at bottom-right
- Touch-friendly on mobile (44x44px minimum)

### Tab Content Components

#### ContentTab
Placeholder for PDF viewer (to be implemented in Task 9).

#### AnnotationsTab
Placeholder for annotations feature (future phase).

#### MetadataTab
Displays all Dublin Core and Neo Alexandria metadata fields.

**Features:**
- Responsive grid layout
- Formatted dates
- Subject tags
- External links
- Description with proper formatting

#### GraphTab
Placeholder for graph visualization (future phase).

#### QualityTab
Placeholder for quality metrics visualization (to be implemented in Task 10).

## Usage

```tsx
import { ResourceDetailPage } from './components/features/resource-detail/ResourceDetailPage';

// In App.tsx routing
<Route path="resources/:id" element={<ResourceDetailPage />} />
```

## Accessibility

- All components are keyboard accessible
- ARIA roles and attributes properly implemented
- Focus indicators visible (2px outline, 2px offset)
- Screen reader friendly
- Touch targets meet minimum size requirements (44x44px)

## Responsive Design

- Desktop (≥768px): Full layout with horizontal tabs
- Mobile (<768px): Compact layout with vertical tabs
- Touch-friendly controls on mobile

## Next Steps

- Task 9: Implement PDF viewer in ContentTab
- Task 10: Implement quality visualization in QualityTab
- Future: Implement annotations and graph features
