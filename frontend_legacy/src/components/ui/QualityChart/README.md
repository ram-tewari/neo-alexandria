# QualityChart Component

A radial chart component for displaying quality scores with animated sweep effects.

## Features

- **Animated Sweep**: Smooth animation on mount using Framer Motion
- **Responsive**: Configurable size prop
- **Accessible**: Displays score percentage in center
- **Theme Support**: Uses CSS variables for colors

## Usage

```tsx
import { QualityChart } from '@/components/ui/QualityChart';

function MyComponent() {
  return <QualityChart score={0.85} size={192} />;
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `score` | `number` | required | Quality score between 0 and 1 |
| `size` | `number` | `192` | Chart diameter in pixels |

## Implementation Details

- Uses SVG for rendering the radial chart
- Stroke animation controlled by `strokeDashoffset`
- Score animates from 0 to actual value on mount
- 1 second animation duration with ease-out timing
