# Design Document

## Overview

Neo Alexandria 2.0 Frontend is a modern, futuristic knowledge management interface built with React, TypeScript, and Vite. The design features a striking black and white color scheme with blue accents, glassmorphism effects, animated gradient backgrounds, and smooth micro-interactions.

## Architecture

### Technology Stack

- **Framework**: React 18
- **Language**: TypeScript 5
- **Build Tool**: Vite 5
- **Styling**: CSS-in-JS (styled-components) + CSS Modules
- **State Management**: Zustand
- **Routing**: React Router 6
- **Icons**: Font Awesome 6
- **Animations**: Framer Motion + CSS animations

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainLayout.tsx
│   │   │   └── FAB.tsx
│   │   ├── background/
│   │   │   ├── AnimatedOrbs.tsx
│   │   │   └── GridPattern.tsx
│   │   ├── cards/
│   │   │   ├── StatCard.tsx
│   │   │   ├── ResourceCard.tsx
│   │   │   └── ActivityCard.tsx
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── SearchInput.tsx
│   │   │   ├── Tag.tsx
│   │   │   └── Avatar.tsx
│   │   └── pages/
│   │       ├── Dashboard.tsx
│   │       ├── Library.tsx
│   │       └── KnowledgeGraph.tsx
│   ├── styles/
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── animations.css
│   ├── hooks/
│   │   ├── useScrollPosition.ts
│   │   └── useMediaQuery.ts
│   ├── store/
│   │   └── navigationStore.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js (optional)
```

## Components and Interfaces

### 1. Background Components

#### AnimatedOrbs Component

```typescript
interface Orb {
  x: number;
  y: number;
  radius: number;
  dx: number;
  dy: number;
  color: string;
  opacity: number;
}

const AnimatedOrbs: React.FC = () => {
  // Canvas-based animation
  // 5 orbs with random positions and velocities
  // Bounce physics on edges
  // Radial gradient rendering
}
```

#### GridPattern Component

```typescript
const GridPattern: React.FC = () => {
  // SVG-based grid pattern
  // 40x40px grid cells
  // 0.08 opacity
  // Fixed positioning
}
```

### 2. Layout Components

#### Navbar Component

```typescript
interface NavbarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  // Glassmorphic navbar
  // Logo with gradient
  // Navigation links with active state
  // Notification bell with badge
  // User avatar
  // Scroll-based styling
}
```

#### Sidebar Component

```typescript
interface SidebarItem {
  icon: string;
  label: string;
  path: string;
}

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  isOpen: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate, isOpen }) => {
  // Fixed sidebar with glassmorphism
  // Main section items
  // Collections section items
  // Active state with blue accent bar
  // Hover effects
}
```

### 3. Card Components

#### StatCard Component

```typescript
interface StatCardProps {
  icon: string;
  value: string | number;
  label: string;
  color: 'blue' | 'cyan' | 'purple' | 'teal';
  delay?: number;
}

const StatCard: React.FC<StatCardProps> = ({ icon, value, label, color, delay }) => {
  // Glassmorphic card
  // Color-coded icon wrapper
  // Large value display
  // Fade-in animation with delay
}
```

#### ResourceCard Component

```typescript
interface Resource {
  title: string;
  description: string;
  author: string;
  readTime: number;
  rating: number;
  tags: string[];
  type: 'article' | 'video' | 'book' | 'paper';
}

interface ResourceCardProps {
  resource: Resource;
  delay?: number;
}

const ResourceCard: React.FC<ResourceCardProps> = ({ resource, delay }) => {
  // Glassmorphic card with hover effects
  // Type icon with color coding
  // Rating display
  // Interactive tags
  // Author and read time metadata
  // Float animation
}
```

### 4. Common Components

#### Button Component

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary';
  icon?: string;
  children: React.ReactNode;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({ variant, icon, children, onClick }) => {
  // Glassmorphic button
  // Shine effect on hover
  // Icon support
  // Transform and shadow on hover
}
```

#### SearchInput Component

```typescript
interface SearchInputProps {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

const SearchInput: React.FC<SearchInputProps> = ({ placeholder, value, onChange }) => {
  // Glassmorphic input
  // Blue accent on focus
  // Search button with icon
  // Smooth transitions
}
```

## Design System

### Color Palette

```css
:root {
  /* Primary Colors */
  --primary-black: #0a0a0a;
  --primary-white: #ffffff;
  
  /* Accent Colors */
  --accent-blue: #3b82f6;
  --accent-blue-light: #60a5fa;
  --accent-cyan: #06b6d4;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.03);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-shadow: rgba(0, 0, 0, 0.5);
  
  /* Grays */
  --gray-400: #a3a3a3;
  --gray-600: #525252;
  
  /* Semantic Colors */
  --color-purple: #8b5cf6;
  --color-teal: #14b8a6;
  --color-yellow: #fbbf24;
}
```

### Typography Scale

```css
/* Headings */
--font-size-h1: 2rem;      /* 32px */
--font-size-h2: 1.5rem;    /* 24px */
--font-size-h3: 1.125rem;  /* 18px */

/* Body */
--font-size-base: 1rem;    /* 16px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-xs: 0.75rem;   /* 12px */

/* Weights */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Spacing Scale

```css
--spacing-xs: 0.5rem;   /* 8px */
--spacing-sm: 0.75rem;  /* 12px */
--spacing-md: 1rem;     /* 16px */
--spacing-lg: 1.5rem;   /* 24px */
--spacing-xl: 2rem;     /* 32px */
--spacing-2xl: 3rem;    /* 48px */
```

### Border Radius

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-full: 9999px;
```

## Animations

### Fade In Animation

```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Float Animation

```css
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
```

### Shine Effect

```css
.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}
```

## State Management

### Navigation Store (Zustand)

```typescript
interface NavigationState {
  currentPage: string;
  sidebarOpen: boolean;
  scrolled: boolean;
  setCurrentPage: (page: string) => void;
  toggleSidebar: () => void;
  setScrolled: (scrolled: boolean) => void;
}

const useNavigationStore = create<NavigationState>((set) => ({
  currentPage: 'dashboard',
  sidebarOpen: true,
  scrolled: false,
  setCurrentPage: (page) => set({ currentPage: page }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setScrolled: (scrolled) => set({ scrolled }),
}));
```

## Responsive Breakpoints

```typescript
const breakpoints = {
  mobile: '768px',
  tablet: '1024px',
  desktop: '1280px',
  wide: '1536px',
};
```

## Performance Optimizations

1. **Code Splitting**: Lazy load page components
2. **Memoization**: Use React.memo for expensive components
3. **Canvas Optimization**: RequestAnimationFrame for orb animations
4. **CSS Transforms**: Use transform instead of position changes
5. **Image Optimization**: WebP format with fallbacks
6. **Bundle Size**: Tree-shaking and dynamic imports

## Accessibility Features

1. **Keyboard Navigation**: Full tab support
2. **Focus Indicators**: Blue outline on focus-visible
3. **ARIA Labels**: All interactive elements labeled
4. **Color Contrast**: WCAG AA compliant (4.5:1 minimum)
5. **Reduced Motion**: Respect prefers-reduced-motion
6. **Semantic HTML**: Proper heading hierarchy

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Android 90+)

## Future Enhancements

1. **Dark/Light Mode Toggle**: Theme switching capability
2. **Customizable Orbs**: User-configurable background animations
3. **Advanced Filters**: Multi-criteria resource filtering
4. **Real-time Updates**: WebSocket integration for live data
5. **Offline Support**: Service worker for PWA functionality
6. **Graph Visualization**: D3.js integration for knowledge graph
