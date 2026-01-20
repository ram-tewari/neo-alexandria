# DensityToggle Component

A toggle control that allows users to switch between three view density modes: compact, comfortable, and spacious.

## Features

- **Three density modes**: Compact, Comfortable, and Spacious
- **Persistent state**: Density preference is saved to localStorage
- **Smooth animations**: Layout transitions animate smoothly using Framer Motion
- **Accessible**: Proper ARIA attributes and keyboard navigation
- **Theme support**: Works with light and dark themes

## Usage

```tsx
import { DensityToggle } from '@/components/ui/DensityToggle';
import { useLocalStorage } from '@/lib/hooks';

function MyComponent() {
  const [density, setDensity] = useLocalStorage<Density>('view-density', 'comfortable');

  return (
    <DensityToggle value={density} onChange={setDensity} />
  );
}
```

## Density Configuration

The density setting affects:
- **Grid gap**: Spacing between resource cards
- **Card padding**: Internal padding of cards

| Density | Gap | Card Padding |
|---------|-----|--------------|
| Compact | 0.5rem (gap-2) | Small (p-3) |
| Comfortable | 1rem (gap-4) | Medium (p-4) |
| Spacious | 1.5rem (gap-6) | Large (p-6) |

## Integration

The DensityToggle is integrated into:
1. **LibraryView**: Header toolbar with density control
2. **LibraryPanel**: Passes density to ResourceGrid
3. **ResourceGrid**: Applies density configuration to grid layout and cards
4. **ResourceCard**: Receives padding prop based on density

## Animation

Layout transitions use Framer Motion's `layout` prop with:
- Duration: 300ms
- Easing: ease-out
- Maintains scroll position during transitions
