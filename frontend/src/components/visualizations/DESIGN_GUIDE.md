# Visualization Design Guide

This guide outlines the design principles and patterns for Neo Alexandria's data visualization components, inspired by modern developer tools like Cursor.

## Core Philosophy

**"Minimal, refined, and purposeful"**

- Start with darkness and subtlety
- Add color only where it serves a purpose
- Use blue accents sparingly, primarily for interaction
- Prioritize readability and clarity over decoration

## Color System

### Background Layers
```css
/* Base layer */
background: #000000;  /* True black for main background */

/* Elevated layer */
background: #0A0A0A;  /* Very dark grey for cards/panels */

/* Interactive layer */
background: #18181B;  /* Slightly lighter for hover states */
```

### Borders & Dividers
```css
/* Default border */
border: 1px solid #27272A;  /* Zinc-800 */

/* Subtle divider */
border: 1px solid rgba(39, 39, 42, 0.5);  /* 50% opacity */
```

### Text Hierarchy
```css
/* Primary headings */
color: #FAFAFA;  /* Zinc-50 */
font-weight: 500-600;
font-size: 14-16px;

/* Secondary text / labels */
color: #A1A1AA;  /* Zinc-400 */
font-weight: 400-500;
font-size: 11-12px;

/* Tertiary text / hints */
color: #71717A;  /* Zinc-500 */
font-weight: 400;
font-size: 10-11px;

/* Disabled / muted */
color: #52525B;  /* Zinc-600 */
```

### Interactive States

#### Default State
- Minimal color
- Subtle borders
- Low contrast

#### Hover State
```css
/* Add subtle highlight */
background: rgba(59, 130, 246, 0.05);  /* 5% blue */
border-color: #3B82F6;  /* Blue border */
cursor: pointer;
```

#### Active/Selected State
```css
/* Stronger highlight */
background: rgba(59, 130, 246, 0.1);  /* 10% blue */
border-color: #3B82F6;
color: #3B82F6;  /* Blue text */
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
             "Roboto", "Helvetica Neue", sans-serif;
```

### Size Scale
- **Tiny:** 10px (hints, footnotes)
- **Small:** 11px (labels, secondary text)
- **Base:** 12px (body text, tooltips)
- **Medium:** 14px (headings, emphasis)
- **Large:** 16px (page titles)

### Weight Scale
- **Regular:** 400 (body text)
- **Medium:** 500 (labels, secondary headings)
- **Semibold:** 600 (primary headings)

## Spacing

### Padding Scale
```css
/* Compact */
padding: 8px 12px;  /* Tooltips, small buttons */

/* Default */
padding: 12px 16px;  /* Cards, panels */

/* Comfortable */
padding: 16px 24px;  /* Large containers */
```

### Gap Scale
```css
/* Tight */
gap: 4px;  /* Icon + text */

/* Default */
gap: 8px;  /* List items */

/* Comfortable */
gap: 12px;  /* Card grid */

/* Spacious */
gap: 16px;  /* Section spacing */
```

## Chart-Specific Guidelines

### Grid Lines
```css
/* Horizontal only (preferred) */
stroke: #27272A;
strokeDasharray: "3 3";
opacity: 0.5;
vertical: false;  /* Hide vertical lines */
```

### Axes
```css
/* Axis lines */
stroke: #27272A;
strokeWidth: 1;

/* Tick labels */
fill: #71717A;
fontSize: 11px;
fontWeight: 400;
```

### Data Points

#### Bars
```css
/* Default */
fill: #3B82F6;
opacity: 0.8;
radius: [2, 2, 0, 0];  /* Subtle rounding */

/* Hover */
opacity: 1.0;
```

#### Lines
```css
/* Default */
stroke: #3B82F6;
strokeWidth: 1.5px;

/* Dots */
r: 3;  /* Small by default */
strokeWidth: 0;  /* No outline */

/* Active dot */
r: 5;
```

#### Nodes (Force Graph)
```css
/* Node fill */
fill: #18181B;  /* Dark grey */

/* Node border */
stroke: #3B82F6;  /* Type color */
strokeWidth: 2;

/* Label */
fill: #A1A1AA;
fontSize: 11px;
```

### Tooltips
```css
/* Container */
background: #09090B;  /* Almost black */
border: 1px solid #27272A;
borderRadius: 8px;
padding: 10px 14px;
boxShadow: 0 4px 12px rgba(0, 0, 0, 0.4);

/* Title */
color: #FAFAFA;
fontSize: 12px;
fontWeight: 500;

/* Content */
color: #71717A;
fontSize: 11px;
lineHeight: 1.5;
```

## Animation Guidelines

### Timing
```css
/* Fast interactions */
duration: 150ms;
easing: ease-out;

/* Standard transitions */
duration: 200ms;
easing: ease-in-out;

/* Slow reveals */
duration: 300ms;
easing: ease-out;
```

### Hover Transitions
```css
transition: all 150ms ease-out;
```

### Loading States
```css
/* Subtle pulse */
animation: pulse 2s ease-in-out infinite;
opacity: 0.5 → 1.0;
```

## Accessibility

### Focus States
```css
/* Keyboard focus */
outline: 2px solid #3B82F6;
outlineOffset: 2px;
borderRadius: 4px;
```

### Color Contrast
- All text must meet WCAG 2.1 Level AA (4.5:1 for normal text)
- Interactive elements must be distinguishable without color alone
- Provide text alternatives for data visualizations

### Touch Targets
```css
/* Minimum size */
minWidth: 44px;
minHeight: 44px;

/* Spacing */
margin: 4px;  /* Between targets */
```

## Examples

### Good ✅
```tsx
// Minimal card with subtle border
<div className="bg-[#0A0A0A] border border-[#27272A] rounded-lg p-6">
  <h2 className="text-sm font-medium text-zinc-300 mb-4">
    Chart Title
  </h2>
  <Chart />
</div>
```

### Avoid ❌
```tsx
// Too much color, heavy styling
<div className="bg-gradient-to-r from-blue-500 to-purple-600 
                rounded-xl p-8 shadow-2xl border-4 border-blue-400">
  <h2 className="text-2xl font-bold text-white mb-6 
                 drop-shadow-lg animate-pulse">
    Chart Title
  </h2>
  <Chart />
</div>
```

## Component Checklist

When creating or updating visualization components:

- [ ] Uses true black (#000000) or very dark grey (#0A0A0A) backgrounds
- [ ] Borders are subtle (#27272A) and 1px wide
- [ ] Text uses zinc color scale (100, 400, 500, 600)
- [ ] Font sizes are 11-14px for most content
- [ ] Blue accent (#3B82F6) appears only on interaction
- [ ] Tooltips use dark background (#09090B) with subtle border
- [ ] Grid lines are horizontal-only and low opacity (0.5)
- [ ] Animations are subtle and fast (150-200ms)
- [ ] Spacing is generous (12-16px gaps)
- [ ] Focus states are clearly visible
- [ ] Touch targets are minimum 44px

## Resources

- **Zinc Color Scale:** https://tailwindcss.com/docs/customizing-colors#color-palette-reference
- **WCAG Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Cursor Design Reference:** Use as inspiration for minimal, refined aesthetics
