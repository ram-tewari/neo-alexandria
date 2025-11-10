# Data Visualization Components

This directory contains reusable data visualization components for the Neo Alexandria 2.0 Frontend.

## Components

### 1. QualityScoreRadial
**Status:** ✅ Completed (Task 12.1)

A radial progress indicator for displaying quality scores with color coding and animations.

**Features:**
- SVG-based radial progress with smooth animations
- Color-coded by quality level (red: 0-59, yellow: 60-79, green: 80-100)
- Animated fill on mount with configurable duration
- Displays percentage in center with optional label
- Fully customizable size and styling

**Usage:**
```tsx
import { QualityScoreRadial } from '@/components/visualizations';

<QualityScoreRadial 
  value={85} 
  size={120} 
  label="Quality Score"
/>
```

### 2. CitationNetworkGraph
**Status:** ✅ Completed (Task 12.2)

Interactive force-directed graph visualization for citation networks using react-force-graph-2d.

**Features:**
- Renders citation graph using force-directed layout
- Sizes nodes by importance score (PageRank)
- Colors nodes by citation type (reference, dataset, code, general)
- Hover tooltips with resource information
- Click navigation to resource details
- Customizable width and height

**Usage:**
```tsx
import { CitationNetworkGraph } from '@/components/visualizations';

<CitationNetworkGraph 
  data={graphData} 
  width={800}
  height={600}
  onNodeClick={(id) => navigate(`/resources/${id}`)}
/>
```

**Data Structure:**
```typescript
interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
```

### 3. ClassificationDistributionChart
**Status:** ✅ Completed (Task 12.3)

Interactive bar chart showing resource distribution across classifications using Recharts.

**Features:**
- Bar chart with classification codes on x-axis
- Resource counts on y-axis
- Hover tooltips with detailed information
- Click to filter by classification
- Responsive container that adapts to parent width
- Color-coded bars for visual distinction
- Automatically shows top 20 classifications

**Usage:**
```tsx
import { ClassificationDistributionChart } from '@/components/visualizations';

<ClassificationDistributionChart 
  data={classificationData}
  height={400}
  onBarClick={(code) => filterByClassification(code)}
/>
```

**Data Structure:**
```typescript
interface ClassificationData {
  code: string;
  name?: string;
  count: number;
}
```

### 4. TemporalTrendsChart
**Status:** ✅ Completed (Task 12.4)

Interactive line chart showing resource creation trends over time using Recharts.

**Features:**
- Line chart with dates on x-axis
- Resource creation counts on y-axis
- Multiple series for different resource types
- Zoom and pan interactions with brush component
- Interactive legend to toggle series visibility
- Hover tooltips with detailed breakdown
- Responsive container that adapts to parent width
- Customizable date format

**Usage:**
```tsx
import { TemporalTrendsChart } from '@/components/visualizations';

<TemporalTrendsChart 
  data={trendsData}
  series={['article', 'dataset', 'code']}
  height={400}
  enableBrush={true}
/>
```

**Data Structure:**
```typescript
interface TemporalDataPoint {
  date: string; // ISO date string
  [key: string]: number | string; // Dynamic keys for different resource types
}
```

## Example Usage

See `VisualizationsExample.tsx` for a complete example demonstrating all visualization components together.

## Dependencies

- **Recharts** (^3.3.0): React charting library for bar and line charts
- **react-force-graph-2d** (^1.25.4): Force-directed graph visualization
- **Framer Motion** (^12.23.24): Animation library for smooth transitions
- **date-fns** (^4.1.0): Date formatting utilities

## Design Philosophy

The visualization components follow a refined, minimal aesthetic inspired by modern developer tools:

### Color Palette
- **Background:** True black (#000000) and very dark grey (#0A0A0A)
- **Borders:** Subtle zinc borders (#27272A) with low opacity
- **Text Primary:** Zinc-100 (#FAFAFA) for headings
- **Text Secondary:** Zinc-400/500 (#A1A1AA, #71717A) for labels
- **Text Tertiary:** Zinc-600 (#52525B) for hints
- **Accent:** Blue (#3B82F6) - used sparingly, primarily on interaction

### Data Visualization Colors
- **Reference/Primary:** #3B82F6 (Blue)
- **Dataset/Success:** #10B981 (Green)
- **Code/Special:** #8B5CF6 (Purple)
- **Warning/Medium:** #F59E0B (Amber)
- **Error/Low:** #EF4444 (Red)
- **General/Other:** #71717A (Grey)

### Design Principles
1. **Minimal by default:** Clean backgrounds, subtle borders, generous whitespace
2. **Interactive accents:** Blue highlights appear only on hover/active states
3. **Refined typography:** Smaller font sizes (11-12px), medium weight, proper hierarchy
4. **Subtle shadows:** Deep, soft shadows (rgba(0,0,0,0.4)) for depth
5. **Reduced visual noise:** Thinner lines, lower opacity, vertical-only grid lines

## Accessibility

All components include:
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast colors meeting WCAG 2.1 Level AA
- Semantic HTML structure
- Descriptive tooltips

## Performance

- Components use React.memo for optimization where appropriate
- Recharts components are responsive and performant
- Force-directed graphs use canvas rendering for better performance
- Data is memoized to prevent unnecessary recalculations

## Requirements Mapping

These components fulfill the following requirements from the specification:

- **Requirement 14.1:** Quality score visualizations using radial progress indicators
- **Requirement 14.2:** Citation network rendering using force-directed graph with PageRank-based node sizing
- **Requirement 14.3:** Classification distribution using interactive bar charts
- **Requirement 14.4:** Temporal trends for resource creation using line charts
- **Requirement 14.5:** Interactive tooltips with detailed information for all visualizations
