# Neo Alexandria 2.0 Frontend

A futuristic knowledge management interface built with React, TypeScript, and Vite.

## 🎨 Design Features

- **Glassmorphism UI**: Beautiful frosted glass effects with backdrop blur
- **Animated Background**: Floating gradient orbs with physics-based movement
- **Responsive Design**: Mobile-first approach with breakpoints for all devices
- **Accessibility**: Full ARIA support, keyboard navigation, and reduced motion support
- **Dark Theme**: Black and white with blue accents (#3b82f6, #06b6d4)

## 🚀 Tech Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool and dev server
- **React Router 6** - Client-side routing
- **Zustand** - State management
- **CSS Modules** - Component styling

## 📦 Installation

```bash
npm install
```

## 🛠️ Development

```bash
npm run dev
```

Runs the app at [http://localhost:3000](http://localhost:3000)

## 🏗️ Build

```bash
npm run build
```

Builds the app for production to the `dist` folder.

## 📁 Project Structure

```
src/
├── components/
│   ├── layout/          # Navbar, Sidebar, MainLayout, FAB
│   ├── background/      # AnimatedOrbs, GridPattern
│   ├── cards/           # StatCard, ResourceCard, ActivityCard
│   ├── common/          # Button, SearchInput, Tag, Avatar, LoadingSpinner
│   └── pages/           # Dashboard, Library, KnowledgeGraph
├── styles/
│   ├── globals.css      # Global styles and resets
│   ├── variables.css    # CSS custom properties
│   └── animations.css   # Keyframe animations
├── hooks/
│   ├── useScrollPosition.ts
│   ├── useMediaQuery.ts
│   └── useReducedMotion.ts
├── store/
│   └── navigationStore.ts
├── types/
│   └── index.ts
├── App.tsx
└── main.tsx
```

## 🎯 Key Components

### Layout Components

- **Navbar**: Fixed top navigation with logo, links, notifications, and user avatar
- **Sidebar**: Fixed left sidebar with main navigation and collections
- **MainLayout**: Wrapper component with background effects
- **FAB**: Floating Action Button for quick actions

### Card Components

- **StatCard**: Display key metrics with color-coded icons
- **ResourceCard**: Rich resource display with tags, ratings, and metadata
- **ActivityCard**: Timeline-style activity feed items

### Common Components

- **Button**: Primary and secondary variants with icon support
- **SearchInput**: Glassmorphic search input with focus states
- **Tag**: Color-coded tags with hover effects
- **Avatar**: User avatar with size variants
- **LoadingSpinner**: Loading indicator with size options

## 🎨 Design System

### Colors

```css
--primary-black: #0a0a0a
--primary-white: #ffffff
--accent-blue: #3b82f6
--accent-blue-light: #60a5fa
--accent-cyan: #06b6d4
--glass-bg: rgba(255, 255, 255, 0.03)
--glass-border: rgba(255, 255, 255, 0.08)
```

### Spacing Scale

```css
--spacing-xs: 0.5rem   (8px)
--spacing-sm: 0.75rem  (12px)
--spacing-md: 1rem     (16px)
--spacing-lg: 1.5rem   (24px)
--spacing-xl: 2rem     (32px)
--spacing-2xl: 3rem    (48px)
```

### Typography

- Font Stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter'`
- Base Size: 16px
- Line Height: 1.5

## ♿ Accessibility

- Full keyboard navigation support
- ARIA labels on all interactive elements
- Focus indicators with 2px blue outline
- Color contrast ratio of 4.5:1 minimum
- Respects `prefers-reduced-motion` setting
- Semantic HTML structure

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: 1024px - 1280px
- Wide: > 1280px

## ⚡ Performance

- Code splitting with React.lazy
- Memoized components with React.memo
- Optimized animations with CSS transforms
- Bundle size: ~57KB gzipped
- 60fps animations

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 License

MIT
