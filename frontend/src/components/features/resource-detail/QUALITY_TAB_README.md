# QualityTab Implementation

Implementation of the Quality tab for resource detail pages, displaying comprehensive quality metrics with visualizations.

## Overview

The QualityTab component fetches and displays quality analysis data for a resource, including:
- Overall quality score with radial chart visualization
- Individual dimension scores with animated progress bars
- Outlier warnings for resources with significantly lower quality

## Components

### QualityTab
Main tab component that orchestrates data fetching and layout.

**Features:**
- Fetches quality data using React Query
- Displays loading, error, and empty states
- Renders overall score chart
- Shows dimension breakdown grid
- Displays outlier warning when applicable

### QualityChart
Reusable radial chart component for displaying quality scores.

**Features:**
- Animated stroke sweep on mount (1s duration)
- Displays percentage in center
- Responsive sizing
- Theme-aware colors

## Data Structure

The component expects quality data in the following format:

```typescript
interface QualityDetails {
  overall_score: number;           // 0-1 range
  dimensions: QualityDimension[];  // Array of dimension scores
  is_outlier: boolean;             // Outlier flag
  calculated_at: string;           // ISO timestamp
}

interface QualityDimension {
  name: string;      // e.g., "accuracy", "completeness"
  score: number;     // 0-1 range
  weight: number;    // Dimension weight in overall score
}
```

## API Integration

Uses the `qualityApi.getDetails(resourceId)` method to fetch quality data:

```typescript
const { data: quality, isLoading, error } = useQuery({
  queryKey: ['resource-quality', resourceId],
  queryFn: () => qualityApi.getDetails(resourceId),
});
```

## Animations

1. **Chart Sweep**: Radial chart animates from 0 to actual score over 1 second
2. **Progress Bars**: Each dimension bar animates with staggered delays (0.2s + index * 0.1s)
3. **Tab Transition**: Fade in/out handled by parent ResourceDetailPage

## Styling

Uses CSS custom properties for theming:
- `--color-primary`: Progress bar and chart stroke color
- `--color-border`: Background circle and bar container
- `--color-text-primary`: Score and dimension labels
- `--color-text-secondary`: Descriptive text
- `--color-warning-*`: Outlier warning colors

## Responsive Design

- Desktop: 2-column grid for dimensions
- Tablet: 2-column grid (auto-fit)
- Mobile: Single column layout
- Chart size remains consistent across breakpoints

## Accessibility

- Proper ARIA roles (`role="tabpanel"`)
- Associated with tab via `aria-labelledby`
- Semantic HTML structure
- Color contrast meets WCAG AA standards
- Loading states announced to screen readers

## Future Enhancements

- Quality history chart showing score over time
- Dimension detail tooltips with explanations
- Export quality report functionality
- Comparison with similar resources
- Quality improvement suggestions
