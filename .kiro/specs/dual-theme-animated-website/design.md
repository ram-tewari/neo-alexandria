# Design Document: Dual-Theme Animated Website

## Overview

This design document outlines the technical architecture for a modern, animated website featuring a comprehensive dual-theme system (light and dark modes). The implementation leverages React with TypeScript, Framer Motion for animations, and CSS custom properties for theme management. The design emphasizes performance, accessibility, and maintainability while delivering smooth, elegant animations and strong visual contrast.

The system will build upon the existing frontend infrastructure (React, Framer Motion, Zustand) and extend it with a robust theme system, collapsible navigation components, and coordinated animation sequences.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Pages      │  │  Components  │  │   Layouts    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    State Management                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Theme Store  │  │  UI Store    │  │  Nav Store   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CSS Variables│  │   Animations │  │   Textures   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Framework**: React 18 with TypeScript
- **Animation Library**: Framer Motion 10
- **State Management**: Zustand 4
- **Styling**: CSS Modules + CSS Custom Properties
- **Build Tool**: Vite 5
- **Testing**: Vitest + React Testing Library
- **Icons**: Lucide React

### Design Principles

1. **Theme-First Design**: All components must be theme-aware from the start
2. **Performance-Optimized Animations**: Use GPU-accelerated transforms and opacity
3. **Accessibility by Default**: Support reduced motion and maintain WCAG AA contrast
4. **Component Reusability**: Build atomic, composable components
5. **Progressive Enhancement**: Core functionality works without JavaScript

## Components and Interfaces

### Core Components

#### 1. ThemeProvider

**Purpose**: Manages theme state and provides theme context to all components

**Interface**:
```typescript
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: 'light' | 'dark';
  storageKey?: string;
}
```

**Responsibilities**:
- Persist theme preference to localStorage
- Apply theme class to document root
- Update CSS custom properties
- Provide theme context to children

#### 2. ThemeToggle

**Purpose**: Interactive control for switching between themes

**Interface**:
```typescript
interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

**Features**:
- Animated icon transition
- Accessible button with ARIA labels
- Visual feedback on interaction
- Theme-aware styling

#### 3. Header / Navbar

**Purpose**: Sticky navigation header with collapse functionality

**Interface**:
```typescript
interface HeaderProps {
  links: NavigationLink[];
  logo?: React.ReactNode;
  className?: string;
}

interface NavigationLink {
  label: string;
  href: string;
  icon?: React.ReactNode;
  active?: boolean;
}
```

**Features**:
- Sticky positioning with scroll detection
- Collapsible with animated height transition
- Animated underline indicators on hover
- Rotating arrow icon for collapse state
- Theme toggle integration

#### 4. Sidebar

**Purpose**: Collapsible side navigation with sorting controls

**Interface**:
```typescript
interface SidebarProps {
  items: SidebarItem[];
  defaultCollapsed?: boolean;
  sortOptions?: SortOption[];
  onSort?: (option: SortOption) => void;
}

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  badge?: number;
}

interface SortOption {
  id: string;
  label: string;
  direction: 'asc' | 'desc';
}
```

**Features**:
- Slide in/out animation with width transition
- Icon-only mode when collapsed
- Rotating collapse arrow
- Animated sort indicators
- Hover highlights with accent colors

#### 5. Hero Section

**Purpose**: Impactful landing section with animated backgrounds

**Interface**:
```typescript
interface HeroProps {
  title: string;
  subtitle?: string;
  cta?: React.ReactNode;
  backgroundAnimation?: boolean;
}
```

**Features**:
- Large, bold typography
- Animated background accents using theme colors
- Staggered intro animation sequence
- Parallax effect on scroll (light mode)
- Glow effects (dark mode)

#### 6. ContentSection

**Purpose**: Reusable content block with scroll-triggered animations

**Interface**:
```typescript
interface ContentSectionProps {
  children: React.ReactNode;
  animationType?: 'fade' | 'slide' | 'scale';
  delay?: number;
  className?: string;
}
```

**Features**:
- Intersection Observer for viewport detection
- Configurable animation types
- Staggered child animations
- Theme-aware styling

#### 7. Footer

**Purpose**: Minimalist footer with themed links

**Interface**:
```typescript
interface FooterProps {
  links: FooterLink[];
  copyright?: string;
  className?: string;
}

interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}
```

**Features**:
- Minimalist design
- Themed interactive elements
- Smooth color transitions
- Responsive layout

### Utility Components

#### AnimatedBackground

**Purpose**: Renders theme-specific background textures

**Interface**:
```typescript
interface AnimatedBackgroundProps {
  variant: 'marble' | 'grain';
  intensity?: number;
  parallax?: boolean;
}
```

#### CollapseButton

**Purpose**: Reusable collapse control with animated arrow

**Interface**:
```typescript
interface CollapseButtonProps {
  isCollapsed: boolean;
  onToggle: () => void;
  direction?: 'up' | 'down' | 'left' | 'right';
  ariaLabel: string;
}
```

#### ScrollReveal

**Purpose**: Wrapper for scroll-triggered animations

**Interface**:
```typescript
interface ScrollRevealProps {
  children: React.ReactNode;
  threshold?: number;
  once?: boolean;
}
```

## Data Models

### Theme Configuration

```typescript
interface ThemeConfig {
  light: ThemeColors;
  dark: ThemeColors;
}

interface ThemeColors {
  // Primary colors
  primary: string;
  primaryDark: string;
  primaryLight: string;
  
  // Background colors
  background: string;
  backgroundAlt: string;
  backgroundTexture: string;
  
  // Text colors
  text: string;
  textSecondary: string;
  textMuted: string;
  
  // Accent colors
  accent: string;
  accentHover: string;
  accentActive: string;
  
  // UI colors
  border: string;
  shadow: string;
  overlay: string;
}
```

### Animation Configuration

```typescript
interface AnimationConfig {
  duration: {
    fast: number;
    normal: number;
    slow: number;
  };
  easing: {
    easeIn: string;
    easeOut: string;
    easeInOut: string;
    spring: SpringConfig;
  };
  reducedMotion: boolean;
}

interface SpringConfig {
  type: 'spring';
  stiffness: number;
  damping: number;
  mass: number;
}
```

### UI State

```typescript
interface UIState {
  sidebarCollapsed: boolean;
  navbarCollapsed: boolean;
  currentSort: SortOption | null;
  scrollPosition: number;
  isScrollingDown: boolean;
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Theme color palette consistency

*For any* interactive element in light mode, the element's color value should be within the defined olive green palette range (#171a0e to #a1b766)
**Validates: Requirements 1.3, 1.4**

### Property 2: Theme color palette consistency (dark mode)

*For any* interactive element in dark mode, the element's color value should be within the defined red palette range (#C41E3A to #E57373)
**Validates: Requirements 2.3, 2.4, 2.6**

### Property 3: Layout invariance across themes

*For any* component, switching between light and dark modes should preserve identical layout dimensions (width, height, padding, margin)
**Validates: Requirements 4.1, 4.3, 4.5**

### Property 4: Typography consistency across themes

*For any* text element, switching themes should only change color properties while preserving font-size, font-weight, font-family, and line-height
**Validates: Requirements 4.2**

### Property 5: Animation timing consistency

*For any* animation, the duration and easing function should remain identical across both themes
**Validates: Requirements 4.4**

### Property 6: Viewport-triggered animations

*For any* content section, entering the viewport should trigger the appropriate reveal animation (fade-in or slide)
**Validates: Requirements 3.1, 3.2, 8.1**

### Property 7: Collapse state synchronization

*For any* collapsible component (navbar or sidebar), the collapse button arrow should rotate 180 degrees when the component's collapsed state changes
**Validates: Requirements 5.7, 6.3**

### Property 8: Sidebar visibility states

*For any* sidebar navigation item, when collapsed the item should show only the icon, and when expanded the item should show both icon and text label
**Validates: Requirements 6.4, 6.5**

### Property 9: Theme accent color application

*For any* active or hovered interactive element, the element should use the current theme's accent color (olive green in light mode, red in dark mode)
**Validates: Requirements 5.4, 6.6, 8.4, 9.2, 9.3**

### Property 10: Hardware-accelerated animations

*For any* animation, the implementation should use only transform and opacity properties (not layout-triggering properties like width, height, top, left)
**Validates: Requirements 10.1, 10.4, 10.5**

### Property 11: Reduced motion compliance

*For any* animation, when prefers-reduced-motion is enabled, decorative animations should be disabled or replaced with simple fades
**Validates: Requirements 11.1, 11.3, 11.4**

### Property 12: Color contrast compliance (light mode)

*For any* text element in light mode, the contrast ratio between text color and background color should meet or exceed 4.5:1
**Validates: Requirements 12.1**

### Property 13: Color contrast compliance (dark mode)

*For any* text element in dark mode, the contrast ratio between text color and background color should meet or exceed 4.5:1
**Validates: Requirements 12.2**

### Property 14: Theme persistence

*For any* theme selection, reloading the page should restore the previously selected theme from localStorage
**Validates: Requirements 13.3**

### Property 15: Theme transition performance

*For any* theme switch, the transition should complete within 300 milliseconds
**Validates: Requirements 13.5**

### Property 16: CSS variable architecture

*For any* themed element, the styling should reference CSS custom properties rather than hardcoded color values
**Validates: Requirements 14.1, 14.4, 15.4**

### Property 17: Component theme reactivity

*For any* component, changing the theme should automatically update the component's appearance without requiring manual refresh
**Validates: Requirements 13.2, 15.2**

### Property 18: Scroll-based parallax (light mode)

*For any* background texture in light mode, scrolling should apply transform values that create a parallax effect
**Validates: Requirements 3.4**

### Property 19: Glow effects (dark mode)

*For any* accent element in dark mode, the element should have box-shadow or glow effects applied
**Validates: Requirements 3.5**

### Property 20: Sort indicator animation

*For any* sort control, clicking should rotate the arrow indicator and apply the theme's accent color
**Validates: Requirements 6.7, 6.8**

## Error Handling

### Theme Loading Errors

**Scenario**: Theme preference cannot be loaded from localStorage

**Handling**:
- Fall back to system preference (prefers-color-scheme media query)
- If system preference unavailable, default to light mode
- Log error to console for debugging
- Continue with default theme without blocking render

### Animation Performance Issues

**Scenario**: Device cannot maintain 60fps during animations

**Handling**:
- Detect performance issues using requestAnimationFrame timing
- Automatically reduce animation complexity
- Disable parallax and complex effects
- Maintain core functionality without animations

### CSS Variable Support

**Scenario**: Browser doesn't support CSS custom properties

**Handling**:
- Detect support using CSS.supports()
- Fall back to inline styles with theme colors
- Provide degraded but functional experience
- Display warning in development mode

### Intersection Observer Unavailable

**Scenario**: Browser doesn't support Intersection Observer API

**Handling**:
- Detect support before initializing scroll animations
- Fall back to showing all content immediately
- Disable scroll-triggered reveals
- Maintain full content accessibility

### LocalStorage Unavailable

**Scenario**: localStorage is blocked or unavailable (private browsing)

**Handling**:
- Catch localStorage errors gracefully
- Store theme preference in memory only
- Theme resets on page reload
- Display subtle notification to user

### Framer Motion Errors

**Scenario**: Animation library fails to load or throws errors

**Handling**:
- Wrap animations in error boundaries
- Fall back to CSS transitions
- Log errors for monitoring
- Ensure UI remains functional without animations

## Testing Strategy

### Unit Testing

**Framework**: Vitest + React Testing Library

**Focus Areas**:
1. **Theme Context**: Test theme state management, toggle functionality, and persistence
2. **Component Rendering**: Test that components render correctly in both themes
3. **Collapse Logic**: Test sidebar and navbar collapse state management
4. **Color Utilities**: Test color contrast calculation functions
5. **Animation Utilities**: Test animation configuration and reduced motion detection

**Example Tests**:
- Theme toggle switches between light and dark
- Theme preference persists to localStorage
- Collapsed sidebar shows only icons
- Expanded sidebar shows icons and labels
- Color contrast meets WCAG AA standards

### Property-Based Testing

**Framework**: fast-check (JavaScript property-based testing library)

**Approach**: Generate random component states and verify universal properties hold

**Property Tests**:

1. **Property 1-2: Theme Color Palette Consistency**
   - Generate random interactive elements
   - Verify colors fall within theme palette ranges
   - Test across both light and dark modes

2. **Property 3: Layout Invariance**
   - Generate random component configurations
   - Measure dimensions in light mode
   - Switch to dark mode and verify dimensions unchanged

3. **Property 4: Typography Consistency**
   - Generate random text elements
   - Extract typography properties in both themes
   - Verify only color properties differ

4. **Property 10: Hardware-Accelerated Animations**
   - Generate random animated components
   - Parse animation styles
   - Verify only transform/opacity used

5. **Property 12-13: Color Contrast Compliance**
   - Generate random text/background color combinations from theme palettes
   - Calculate contrast ratios
   - Verify all combinations meet 4.5:1 minimum

6. **Property 14: Theme Persistence**
   - Generate random theme selections
   - Simulate page reload
   - Verify theme restored from storage

7. **Property 16: CSS Variable Architecture**
   - Generate random themed elements
   - Parse computed styles
   - Verify colors reference CSS variables

### Integration Testing

**Focus Areas**:
1. **Theme Switching Flow**: Test complete theme switch including all components
2. **Navigation Interactions**: Test navbar and sidebar collapse/expand
3. **Scroll Animations**: Test viewport detection and animation triggers
4. **Accessibility**: Test keyboard navigation and screen reader compatibility

### Visual Regression Testing

**Approach**: Capture screenshots of components in both themes and compare

**Tools**: Playwright or Chromatic

**Coverage**:
- All major components in light and dark modes
- Hover and active states
- Collapsed and expanded states
- Mobile and desktop viewports

### Performance Testing

**Metrics**:
- Animation frame rate (target: 60fps)
- Theme switch duration (target: <300ms)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)

**Tools**:
- Chrome DevTools Performance panel
- Lighthouse
- Web Vitals library

### Accessibility Testing

**Tools**:
- axe-core
- WAVE
- Manual keyboard testing
- Screen reader testing (NVDA, JAWS, VoiceOver)

**Coverage**:
- Color contrast ratios
- Keyboard navigation
- Focus management
- ARIA labels and roles
- Reduced motion support

## Implementation Notes

### CSS Custom Properties Structure

```css
:root {
  /* Light mode colors */
  --color-light-primary: #3e4822;
  --color-light-accent: #525c31;
  --color-light-bg: #f4f3e5;
  --color-light-text: #171a0e;
  
  /* Dark mode colors */
  --color-dark-primary: #C41E3A;
  --color-dark-accent: #DC143C;
  --color-dark-bg: #1a1a1a;
  --color-dark-text: #ffffff;
  
  /* Animation durations */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  
  /* Easing functions */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

[data-theme="light"] {
  --color-primary: var(--color-light-primary);
  --color-accent: var(--color-light-accent);
  --color-bg: var(--color-light-bg);
  --color-text: var(--color-light-text);
}

[data-theme="dark"] {
  --color-primary: var(--color-dark-primary);
  --color-accent: var(--color-dark-accent);
  --color-bg: var(--color-dark-bg);
  --color-text: var(--color-dark-text);
}
```

### Framer Motion Animation Variants

```typescript
// Fade in animation
export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.3 }
  }
};

// Slide up animation
export const slideUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
  }
};

// Collapse animation
export const collapse = {
  collapsed: { height: 0, opacity: 0 },
  expanded: { 
    height: 'auto', 
    opacity: 1,
    transition: { duration: 0.3 }
  }
};

// Rotate arrow
export const rotateArrow = {
  collapsed: { rotate: 0 },
  expanded: { rotate: 180 }
};
```

### Zustand Store Structure

```typescript
interface ThemeStore {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
}

interface UIStore {
  sidebarCollapsed: boolean;
  navbarCollapsed: boolean;
  toggleSidebar: () => void;
  toggleNavbar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setNavbarCollapsed: (collapsed: boolean) => void;
}
```

### Accessibility Considerations

1. **Keyboard Navigation**: All interactive elements must be keyboard accessible
2. **Focus Indicators**: Visible focus rings using theme accent colors
3. **ARIA Labels**: Descriptive labels for icon-only buttons
4. **Screen Reader Announcements**: Theme changes announced to screen readers
5. **Reduced Motion**: Respect prefers-reduced-motion media query
6. **Color Contrast**: All text meets WCAG AA standards (4.5:1 minimum)
7. **Focus Management**: Focus trapped in modals, restored after collapse/expand

### Performance Optimizations

1. **CSS Containment**: Use `contain: layout style paint` on animated elements
2. **Will-Change**: Apply `will-change: transform, opacity` to animated elements
3. **Lazy Loading**: Defer non-critical animations until after initial render
4. **Debounced Scroll**: Throttle scroll event handlers to 16ms (60fps)
5. **Memoization**: Memoize theme-dependent computed values
6. **Code Splitting**: Lazy load animation library for above-the-fold content
7. **GPU Acceleration**: Use `transform: translate3d(0, 0, 0)` to force GPU rendering

### Browser Support

**Target Browsers**:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Chrome Android 90+

**Required Features**:
- CSS Custom Properties
- CSS Grid
- Flexbox
- Intersection Observer API
- LocalStorage
- ES6+ JavaScript

**Graceful Degradation**:
- Fallback for CSS Custom Properties
- Polyfill for Intersection Observer
- Static layout if animations fail

## Security Considerations

1. **XSS Prevention**: Sanitize any user-provided content in theme customization
2. **LocalStorage**: Validate theme values before applying to prevent injection
3. **CSP Compliance**: Ensure inline styles comply with Content Security Policy
4. **Third-Party Scripts**: Audit animation libraries for vulnerabilities

## Deployment Strategy

### Development Environment

- Hot module replacement for instant theme updates
- Development-only theme debugging tools
- Performance monitoring overlay

### Staging Environment

- Visual regression testing against baseline
- Performance benchmarking
- Accessibility audit

### Production Environment

- Minified and optimized CSS
- Tree-shaken JavaScript
- CDN-hosted static assets
- Monitoring for animation performance issues

## Future Enhancements

1. **Custom Theme Builder**: Allow users to create custom color schemes
2. **System Theme Sync**: Automatically switch based on OS theme
3. **Scheduled Themes**: Auto-switch based on time of day
4. **Animation Presets**: Multiple animation style options
5. **Theme Marketplace**: Share and download community themes
6. **High Contrast Mode**: Additional theme for accessibility
7. **Print Styles**: Optimized theme for printing
8. **Theme Preview**: Live preview before applying theme
