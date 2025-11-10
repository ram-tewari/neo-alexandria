# Neo Alexandria Design System

## Design Philosophy

**"Clean, minimal, and purposeful"** - Inspired by modern developer tools like Cursor and Readspace.

### Core Principles

1. **Darkness First**: Start with true black (#000000), build up with subtle layers
2. **Minimal Color**: Use greyscale by default, color only for meaning and interaction
3. **Refined Typography**: Smaller sizes (11-14px), lighter weights (400-500), clear hierarchy
4. **Subtle Interactions**: Gentle hover states, smooth transitions, no flashy animations
5. **Generous Whitespace**: Let content breathe, avoid cramped layouts
6. **Purposeful Accents**: Blue (#3B82F6) only where it serves a function

## Color Palette

### Background Layers
```css
/* Base layer - Main background */
#000000  /* True black */

/* Elevated layer - Cards, panels */
#0A0A0A  /* Very dark grey */

/* Interactive layer - Hover states */
#18181B  /* Zinc-950 */
```

### Borders & Dividers
```css
/* Primary border */
#27272A  /* Zinc-800 - Subtle, low contrast */

/* Secondary border */
#18181B  /* Zinc-950 - Even more subtle */

/* Divider */
#3F3F46  /* Zinc-700 - Slightly more visible */
```

### Text Hierarchy
```css
/* Primary - Headings, important text */
#FAFAFA  /* Zinc-50 */
font-weight: 500-600;
font-size: 14-16px;

/* Secondary - Body text, labels */
#A1A1AA  /* Zinc-400 */
font-weight: 400-500;
font-size: 12-13px;

/* Tertiary - Supporting text, hints */
#71717A  /* Zinc-500 */
font-weight: 400;
font-size: 11-12px;

/* Quaternary - Disabled, muted */
#52525B  /* Zinc-600 */
font-weight: 400;
font-size: 10-11px;
```

### Interactive States

#### Default
```css
background: transparent;
border: 1px solid #27272A;
color: #A1A1AA;
```

#### Hover
```css
background: #18181B;  /* Zinc-950 */
border: 1px solid #3F3F46;  /* Zinc-700 */
color: #FAFAFA;  /* Zinc-50 */
cursor: pointer;
transition: all 150ms ease-out;
```

#### Active/Selected
```css
background: #27272A;  /* Zinc-800 */
border: 1px solid #3B82F6;  /* Blue accent */
color: #FAFAFA;  /* Zinc-50 */
```

#### Focus (Keyboard)
```css
outline: 2px solid #3B82F6;
outline-offset: 2px;
```

### Accent Colors

Use sparingly, primarily for interactive elements and data visualization:

```css
/* Primary accent - Interactive elements */
#3B82F6  /* Blue */

/* Success - Positive actions, datasets */
#10B981  /* Green */

/* Warning - Caution, medium priority */
#F59E0B  /* Amber */

/* Error - Destructive actions, low quality */
#EF4444  /* Red */

/* Special - Code, unique items */
#8B5CF6  /* Purple */
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
             "Roboto", "Helvetica Neue", "Arial", sans-serif;
```

### Size Scale
```css
/* Tiny - Footnotes, timestamps */
10px / 0.625rem

/* Small - Labels, captions */
11px / 0.6875rem

/* Base - Body text, UI elements */
12px / 0.75rem

/* Medium - Secondary headings */
13px / 0.8125rem

/* Large - Primary headings */
14px / 0.875rem

/* XLarge - Page titles */
16px / 1rem

/* XXLarge - Hero text */
24px / 1.5rem
```

### Weight Scale
```css
/* Regular - Body text, labels */
400

/* Medium - Emphasis, secondary headings */
500

/* Semibold - Primary headings */
600
```

### Line Height
```css
/* Tight - Headings */
1.2

/* Normal - Body text */
1.5

/* Relaxed - Long-form content */
1.6
```

## Spacing

### Padding Scale
```css
/* Compact */
padding: 8px 12px;

/* Default */
padding: 12px 16px;

/* Comfortable */
padding: 16px 24px;

/* Spacious */
padding: 24px 32px;
```

### Gap Scale
```css
/* Tight - Icon + text */
gap: 4px / 0.25rem;

/* Snug - Related items */
gap: 8px / 0.5rem;

/* Default - List items */
gap: 12px / 0.75rem;

/* Comfortable - Card grid */
gap: 16px / 1rem;

/* Spacious - Section spacing */
gap: 24px / 1.5rem;

/* Generous - Major sections */
gap: 32px / 2rem;
```

### Margin Scale
```css
/* Small */
margin: 8px / 0.5rem;

/* Medium */
margin: 16px / 1rem;

/* Large */
margin: 24px / 1.5rem;

/* XLarge */
margin: 32px / 2rem;
```

## Components

### Navigation Bar
```css
/* Container */
background: rgba(0, 0, 0, 0.8);
backdrop-filter: blur(12px);
border-bottom: 1px solid #18181B;
height: 56px;  /* 14 * 4 */

/* Logo */
font-size: 14px;
font-weight: 500;
color: #FAFAFA;

/* Nav items */
font-size: 12px;
font-weight: 500;
padding: 6px 12px;
border-radius: 4px;

/* Active state */
background: #27272A;
color: #FAFAFA;

/* Hover state */
background: #18181B;
color: #FAFAFA;
```

### Cards
```css
/* Container */
background: #0A0A0A;
border: 1px solid #27272A;
border-radius: 8px;
padding: 16px 24px;

/* Hover state (if interactive) */
border-color: #3F3F46;
background: #0F0F0F;
```

### Buttons

#### Primary
```css
background: #3B82F6;
color: #FFFFFF;
padding: 8px 16px;
border-radius: 6px;
font-size: 12px;
font-weight: 500;

/* Hover */
background: #2563EB;
```

#### Secondary
```css
background: #27272A;
color: #FAFAFA;
border: 1px solid #3F3F46;

/* Hover */
background: #3F3F46;
```

#### Ghost
```css
background: transparent;
color: #A1A1AA;

/* Hover */
background: #18181B;
color: #FAFAFA;
```

### Inputs
```css
/* Container */
background: #0A0A0A;
border: 1px solid #27272A;
border-radius: 6px;
padding: 8px 12px;
font-size: 12px;
color: #FAFAFA;

/* Placeholder */
color: #52525B;

/* Focus */
border-color: #3B82F6;
outline: none;
```

### Tooltips
```css
/* Container */
background: #09090B;
border: 1px solid #27272A;
border-radius: 8px;
padding: 10px 14px;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);

/* Title */
font-size: 12px;
font-weight: 500;
color: #FAFAFA;

/* Content */
font-size: 11px;
color: #71717A;
line-height: 1.5;
```

## Layout

### Container Widths
```css
/* Narrow - Reading content */
max-width: 640px;  /* 40rem */

/* Default - Most pages */
max-width: 1024px;  /* 64rem */

/* Wide - Dashboards */
max-width: 1280px;  /* 80rem */

/* Full - Data tables */
max-width: 1536px;  /* 96rem */
```

### Grid Systems
```css
/* 2-column */
grid-template-columns: repeat(2, 1fr);
gap: 16px;

/* 3-column */
grid-template-columns: repeat(3, 1fr);
gap: 24px;

/* Sidebar layout */
grid-template-columns: 240px 1fr;
gap: 24px;
```

## Animation

### Timing Functions
```css
/* Fast - Micro-interactions */
transition: all 150ms ease-out;

/* Normal - Standard transitions */
transition: all 200ms ease-in-out;

/* Slow - Page transitions */
transition: all 300ms ease-out;
```

### Common Animations
```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* Scale in */
@keyframes scaleIn {
  from { 
    opacity: 0; 
    transform: scale(0.95); 
  }
  to { 
    opacity: 1; 
    transform: scale(1); 
  }
}
```

## Accessibility

### Focus Indicators
```css
/* Keyboard focus */
outline: 2px solid #3B82F6;
outline-offset: 2px;
border-radius: 4px;
```

### Color Contrast
- All text must meet WCAG 2.1 Level AA (4.5:1 for normal text, 3:1 for large text)
- Interactive elements must be distinguishable without color alone
- Provide text alternatives for visual content

### Touch Targets
```css
/* Minimum size */
min-width: 44px;
min-height: 44px;

/* Spacing between targets */
margin: 4px;
```

## Best Practices

### Do ✅
- Use true black (#000000) for main backgrounds
- Keep borders subtle (#27272A)
- Use zinc color scale for text hierarchy
- Add blue accent only on interaction
- Provide generous whitespace
- Use small, refined typography (11-14px)
- Keep animations subtle and fast (150-200ms)
- Maintain consistent spacing (8px increments)

### Don't ❌
- Use bright or saturated backgrounds
- Add gradients or heavy shadows
- Use large, bold typography everywhere
- Add color without purpose
- Cram content together
- Use flashy animations
- Mix different spacing scales
- Use more than 2-3 font weights

## Examples

### Good Card ✅
```tsx
<div className="bg-[#0A0A0A] border border-[#27272A] rounded-lg p-6">
  <h3 className="text-sm font-medium text-zinc-100 mb-2">
    Card Title
  </h3>
  <p className="text-xs text-zinc-400">
    Card content goes here
  </p>
</div>
```

### Bad Card ❌
```tsx
<div className="bg-gradient-to-r from-blue-500 to-purple-600 
                rounded-xl p-8 shadow-2xl border-4 border-blue-400">
  <h3 className="text-2xl font-bold text-white mb-4 
                 drop-shadow-lg animate-pulse">
    Card Title
  </h3>
  <p className="text-lg text-white">
    Card content goes here
  </p>
</div>
```

## Resources

- **Tailwind Zinc Colors**: https://tailwindcss.com/docs/customizing-colors
- **WCAG Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Cursor Design**: Use as reference for minimal aesthetics
- **Readspace Design**: Use as reference for clean layouts
