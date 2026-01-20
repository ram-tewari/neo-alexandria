# Quick Reference Card - Minimal Monochromatic Design

## 🎨 Color Palette

```css
/* Use these colors ONLY */
--black: #000000           /* Backgrounds, buttons */
--charcoal-dark: #1a1a1a   /* Cards, surfaces */
--charcoal: #2a2a2a        /* Raised elements */
--charcoal-light: #3a3a3a  /* Subtle backgrounds */
--gray: #6a6a6a            /* Tertiary text */
--gray-light: #9a9a9a      /* Secondary text */
--white: #ffffff           /* Primary text, accents */
```

## 📏 Sizing

```css
/* Typography */
H1: 1.75rem (28px)
H2: 1.25rem (20px)
Base: 0.875rem (14px)
Small: 0.8125rem (13px)
XSmall: 0.75rem (12px)

/* Spacing */
XS: 0.375rem (6px)
SM: 0.5rem (8px)
MD: 0.75rem (12px)
LG: 1rem (16px)
XL: 1.5rem (24px)

/* Border Radius */
SM: 2px
MD: 4px
LG: 6px

/* Icons */
Default: 16-18px
Maximum: 20px
```

## ⚡ Animations

```css
/* Timing */
Fast: 150ms
Base: 250ms
Slow: 350ms

/* Easing */
cubic-bezier(0.4, 0, 0.2, 1)
```

## 🎯 Key Patterns

### Button Hover
```
Black → White
White text → Black text
Lift: 1px
```

### Card Hover
```
Background: Charcoal → White
Border: Subtle → White
Lift: 2px
White line animates in
```

### Link Hover
```
Color: Gray → White
Underline: 0 → 100% width
```

## ✅ Do's

- Use black, white, and grays only
- Keep animations subtle (1-2px movements)
- Use color inversion for hover states
- Maintain high contrast (white on black)
- Keep spacing tight and consistent
- Use minimal border radius (2-6px)

## ❌ Don'ts

- No colors (purple, blue, pink, etc.)
- No large movements (>2px)
- No glowing effects or shadows (except subtle)
- No large icons (>20px)
- No decorative elements
- No rounded corners (>6px)

## 🔧 Common Components

### Button
```css
padding: 0.5rem 1rem;
background: black;
color: white;
border: 1px solid rgba(255,255,255,0.12);
border-radius: 2px;

:hover {
  background: white;
  color: black;
}
```

### Card
```css
padding: 1rem;
background: #1a1a1a;
border: 1px solid rgba(255,255,255,0.06);
border-radius: 4px;

:hover {
  background: white;
  transform: translateY(-2px);
}
```

### Input
```css
padding: 0.75rem 1rem;
background: #1a1a1a;
border: 1px solid rgba(255,255,255,0.06);
color: white;

:focus {
  border-color: rgba(255,255,255,0.12);
}
```

## 📱 Responsive

```css
Desktop: max-width: 1200px
Tablet: < 1200px
Mobile: < 768px

/* Reduce sizes by 10-15% on mobile */
```

## 🎭 Icon Usage

### Keep (Essential)
- Search (16px)
- Menu (20px)
- Close (16px)
- Chevrons (14px)
- Plus (20px)

### Remove (Decorative)
- Stat card icons
- Activity icons
- Resource type icons
- Navigation icons
- Button icons (with text)

## 🚀 Quick Wins

1. Remove all colorful elements
2. Reduce padding by 30-40%
3. Shrink icons to 16-20px
4. Use white for hover states
5. Simplify animations to 250ms
6. Remove unnecessary icons

## 📊 Metrics

- **Size Reduction**: 30-50% smaller components
- **Animation Speed**: 40% faster (300ms → 250ms)
- **Color Palette**: 90% reduction (10+ colors → 3 shades)
- **Icon Usage**: 60% fewer icons recommended

## 🎨 Design Philosophy

> "Black, white, and nothing else. Small, fast, and elegant. Every element earns its place."

---

**Remember**: When in doubt, make it smaller, faster, and more minimal.
