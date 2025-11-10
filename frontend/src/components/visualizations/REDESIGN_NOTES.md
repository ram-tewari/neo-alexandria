# Visualization Redesign Notes

## Overview

The visualization components have been redesigned to follow a more refined, minimal aesthetic inspired by modern developer tools like Cursor.

## Key Changes

### 1. Color Palette Refinement

**Before:**
- Bright charcoal grey backgrounds (#1A202C, #171923)
- Heavy use of accent blue throughout
- High contrast borders (#4B5563)
- Bright text colors (#F9FAFB)

**After:**
- True black (#000000) and very dark grey (#0A0A0A) backgrounds
- Blue accents only on interaction
- Subtle zinc borders (#27272A)
- Refined text hierarchy (zinc-100, zinc-400, zinc-500, zinc-600)

### 2. Typography Updates

**Before:**
- Font sizes: 12-14px
- Font weights: 600-700 (bold/semibold)
- Mixed hierarchy

**After:**
- Font sizes: 11-12px (more compact)
- Font weights: 400-500 (regular/medium)
- Clear hierarchy: 14px headings, 12px body, 11px labels

### 3. Component-Specific Changes

#### CitationNetworkGraph
- **Background:** #171923 → #000000 (true black)
- **Node fill:** Colored → #18181B (dark grey with colored border)
- **Node border:** Subtle → 2px colored stroke
- **Labels:** #F9FAFB → #A1A1AA (zinc-400)
- **Tooltips:** Refined with better spacing and contrast

#### ClassificationDistributionChart
- **Grid:** Vertical + horizontal → Horizontal only
- **Grid color:** #374151 → #27272A (more subtle)
- **Grid opacity:** 0.3 → 0.5
- **Axis labels:** 12px → 11px
- **Bar radius:** 4px → 2px (more subtle)
- **Bar opacity:** 1.0 → 0.8
- **Tooltips:** Darker background, better hierarchy

#### TemporalTrendsChart
- **Grid:** Same as ClassificationDistributionChart
- **Line width:** 2px → 1.5px (more refined)
- **Dot size:** 4px → 3px (more subtle)
- **Active dot:** 6px → 5px
- **Legend:** Larger text → 12px with zinc-400 color
- **Brush fill:** #1F2937 → #09090B (darker)

#### QualityScoreRadial
- **Background circle:** text-charcoal-grey-700 → #27272A
- **Background opacity:** 0.3 → 0.5
- **Center text:** text-charcoal-grey-50 → text-zinc-100
- **Label:** text-charcoal-grey-400 → text-zinc-500
- **Font weight:** bold → semibold

### 4. Layout & Spacing

**Before:**
- Heavy padding (p-4, p-8)
- Bright card backgrounds
- Large gaps (gap-8)

**After:**
- Refined padding (p-6)
- Minimal card backgrounds (#0A0A0A)
- Subtle borders (border-[#27272A])
- Generous spacing (space-y-16, gap-12)

### 5. Interactive States

**Before:**
- Always visible accent colors
- Heavy hover effects

**After:**
- Neutral default state
- Blue accents appear only on hover/interaction
- Subtle cursor changes (rgba(59, 130, 246, 0.05))

## Design Principles Applied

1. **Darkness First:** Start with true black, add subtle layers
2. **Minimal Color:** Use grey scale by default, color for meaning
3. **Refined Typography:** Smaller sizes, lighter weights, clear hierarchy
4. **Subtle Interactions:** Gentle hover states, smooth transitions
5. **Generous Whitespace:** Let content breathe
6. **Purposeful Accents:** Blue only where it serves a function

## Visual Comparison

### Old Style (Tacky)
```
┌─────────────────────────────────────┐
│  🎨 Bright Background (#1A202C)     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Heavy Border (#4B5563)             │
│  Bold Text (700 weight)             │
│  Lots of Blue Everywhere            │
│  Large Padding                      │
└─────────────────────────────────────┘
```

### New Style (Refined)
```
┌─────────────────────────────────────┐
│  ⬛ Dark Background (#0A0A0A)       │
│  ─────────────────────────────────  │
│  Subtle Border (#27272A)            │
│  Medium Text (500 weight)           │
│  Grey by Default, Blue on Hover     │
│  Comfortable Padding                │
└─────────────────────────────────────┘
```

## Implementation Details

### Zinc Color Scale Used
```css
zinc-50:  #FAFAFA  /* Primary headings */
zinc-100: #F4F4F5  /* Primary text */
zinc-200: #E4E4E7  /* (not used) */
zinc-300: #D4D4D8  /* Secondary headings */
zinc-400: #A1A1AA  /* Secondary text, labels */
zinc-500: #71717A  /* Tertiary text, hints */
zinc-600: #52525B  /* Muted text */
zinc-700: #3F3F46  /* (not used) */
zinc-800: #27272A  /* Borders, dividers */
zinc-900: #18181B  /* Elevated backgrounds */
zinc-950: #09090B  /* Tooltips, overlays */
```

### Custom Colors
```css
Black:    #000000  /* Main background */
Dark:     #0A0A0A  /* Card backgrounds */
Blue:     #3B82F6  /* Interactive accents */
Green:    #10B981  /* Success, datasets */
Purple:   #8B5CF6  /* Code */
Amber:    #F59E0B  /* Warning, medium */
Red:      #EF4444  /* Error, low quality */
```

## Testing Checklist

- [x] All components render without errors
- [x] TypeScript types are correct
- [x] Colors follow the new palette
- [x] Typography is consistent
- [x] Spacing is generous
- [x] Interactions are subtle
- [x] Tooltips are refined
- [x] Accessibility is maintained
- [x] Dark mode looks clean
- [x] No bright/tacky colors

## Future Improvements

1. Add hover states to more interactive elements
2. Consider adding subtle animations on data updates
3. Implement theme switching (if needed)
4. Add more chart types following the same design language
5. Create a shared tooltip component for consistency

## References

- Cursor IDE design patterns
- Tailwind CSS Zinc color scale
- Modern developer tool aesthetics
- Minimal design principles
