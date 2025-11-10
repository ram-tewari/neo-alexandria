# Responsive Design Quick Reference

## Breakpoints

```typescript
xs:   320px  // Extra small phones
sm:   640px  // Small phones
md:   768px  // Tablets
lg:  1024px  // Desktop
xl:  1280px  // Large desktop
2xl: 1536px  // Extra large desktop
```

## Test Viewports (Requirements)

### Mobile
- 320px (iPhone SE, small phones)
- 375px (iPhone 12/13/14)
- 414px (iPhone Plus/Max)

### Tablet
- 768px (iPad Mini)
- 1024px (iPad)

### Desktop
- 1280px (Standard desktop)
- 1920px (Full HD)

## Touch Target Sizes

```css
Minimum: 44x44px (WCAG 2.1 Level AAA)
Small:   36x36px (use sparingly)
Large:   48x48px (recommended for primary actions)
```

## Tailwind Classes

### Touch-Friendly Utilities
```html
<!-- Minimum touch target -->
<button class="touch-target">Button</button>

<!-- Small touch target -->
<button class="touch-target-sm">Icon</button>

<!-- Large touch target -->
<button class="touch-target-lg">Primary</button>

<!-- Touch manipulation -->
<div class="touch-manipulation">Content</div>
```

### Responsive Display
```html
<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<div class="block lg:hidden">Mobile only</div>

<!-- Different layouts per breakpoint -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  <!-- Cards -->
</div>
```

### Responsive Spacing
```html
<!-- Responsive padding -->
<div class="p-4 md:p-6 lg:p-8">Content</div>

<!-- Responsive margin -->
<div class="mt-4 md:mt-6 lg:mt-8">Content</div>

<!-- Responsive gap -->
<div class="flex gap-2 md:gap-4 lg:gap-6">Items</div>
```

### Responsive Typography
```html
<!-- Responsive text size -->
<h1 class="text-2xl md:text-3xl lg:text-4xl">Heading</h1>

<!-- Responsive line height -->
<p class="leading-relaxed md:leading-loose">Text</p>
```

## Testing Tools

### Browser DevTools
```
Chrome:  F12 → Toggle device toolbar (Ctrl+Shift+M)
Firefox: F12 → Responsive Design Mode (Ctrl+Shift+M)
```

### Development Overlay
```
Keyboard Shortcut: Ctrl+Shift+R
Shows: Viewport size, breakpoint, touch target validation
```

### Console Commands
```javascript
// Get current viewport
window.responsiveTester.getCurrentViewport()

// Get current breakpoint
window.responsiveTester.getCurrentBreakpoint()

// Check all touch targets
window.responsiveTester.checkAllTouchTargets()

// Highlight invalid touch targets
window.responsiveTester.highlightInvalidTouchTargets()

// Remove highlights
window.responsiveTester.removeHighlights()

// Log responsive info
window.responsiveTester.logResponsiveInfo()

// Toggle testing overlay
window.responsiveTester.createTestingOverlay()
```

## Common Patterns

### Responsive Navigation
```tsx
// Desktop: horizontal menu
// Mobile: hamburger + slide-in menu
<nav className="hidden lg:flex">Desktop Nav</nav>
<button className="lg:hidden touch-target">☰</button>
```

### Responsive Grid
```tsx
// Mobile: 1 column
// Tablet: 2-3 columns
// Desktop: 3-4 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```

### Responsive Sidebar
```tsx
// Mobile: drawer/modal
// Desktop: fixed sidebar
<aside className="fixed inset-y-0 left-0 w-64 hidden lg:block">
  Sidebar
</aside>
<button className="lg:hidden touch-target" onClick={openDrawer}>
  Filters
</button>
```

### Responsive Modal
```tsx
// Mobile: full screen
// Desktop: centered with max-width
<div className="fixed inset-0 lg:inset-auto lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2 lg:max-w-2xl">
  Modal Content
</div>
```

### Responsive Form
```tsx
// Mobile: stacked
// Desktop: side-by-side
<form className="space-y-4">
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    <input className="min-h-[44px]" />
    <input className="min-h-[44px]" />
  </div>
</form>
```

## Checklist for New Components

- [ ] Test at 320px, 768px, 1280px minimum
- [ ] All touch targets are 44x44px minimum
- [ ] No horizontal scrolling on mobile
- [ ] Text is readable at all sizes
- [ ] Images scale appropriately
- [ ] Spacing is adequate (8px minimum between targets)
- [ ] Hover states work on desktop
- [ ] Touch feedback on mobile
- [ ] Keyboard navigation works
- [ ] Focus indicators visible

## Common Issues

### Issue: Horizontal Scrolling
**Fix:** Use `max-w-full` or `overflow-x-hidden`

### Issue: Touch Targets Too Small
**Fix:** Add `min-h-[44px] min-w-[44px]` or use `touch-target` class

### Issue: Text Truncation
**Fix:** Use responsive font sizes or `truncate` with tooltips

### Issue: Images Not Scaling
**Fix:** Add `w-full h-auto` or `object-cover`

### Issue: Layout Breaking
**Fix:** Use responsive grid/flex with proper breakpoints

### Issue: Navigation Not Accessible
**Fix:** Implement mobile menu with hamburger button

## Resources

- [Tailwind Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [WCAG Touch Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Chrome DevTools Device Mode](https://developer.chrome.com/docs/devtools/device-mode/)

## Quick Test Command

```bash
# Start dev server with network access for device testing
npm run dev -- --host

# Access from mobile device
# http://[your-ip]:5173
```

## Lighthouse Audit

```bash
# Run Lighthouse in Chrome DevTools
# 1. Open DevTools (F12)
# 2. Click "Lighthouse" tab
# 3. Select "Mobile" or "Desktop"
# 4. Click "Generate report"
```

## Sign-off Criteria

✅ All test viewports pass (320px, 375px, 414px, 768px, 1024px, 1280px, 1920px)
✅ All touch targets are 44x44px minimum
✅ No horizontal scrolling on any page
✅ Lighthouse accessibility score > 90
✅ Tested on at least 2 physical devices
✅ All interactive elements keyboard accessible
