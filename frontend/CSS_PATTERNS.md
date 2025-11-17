# CSS Patterns - Copy & Paste Examples

Quick reference for common patterns in the minimal monochromatic design.

---

## 🎨 Color Usage

### Text Colors
```css
/* Primary text (headings, important content) */
color: var(--text-primary);  /* white */

/* Secondary text (body, descriptions) */
color: var(--text-secondary);  /* light gray */

/* Tertiary text (timestamps, metadata) */
color: var(--text-tertiary);  /* medium gray */

/* Disabled text */
color: var(--text-disabled);  /* dark gray */
```

### Background Colors
```css
/* Main background */
background: var(--black);

/* Card/surface background */
background: var(--surface-base);  /* charcoal dark */

/* Raised surface (hover) */
background: var(--surface-raised);  /* charcoal */

/* Overlay/modal background */
background: var(--surface-overlay);  /* charcoal light */
```

### Border Colors
```css
/* Subtle border (default) */
border: 1px solid var(--border-subtle);

/* Medium border (hover) */
border: 1px solid var(--border-medium);

/* Strong border (active) */
border: 1px solid var(--border-strong);
```

---

## 🔘 Button Patterns

### Primary Button (Black → White Inversion)
```css
.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--black);
  color: var(--white);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary:hover {
  background: var(--white);
  color: var(--black);
  border-color: var(--white);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
}
```

### Secondary Button (Transparent → White)
```css
.btn-secondary {
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-secondary:hover {
  background: var(--white);
  color: var(--black);
  border-color: var(--white);
}
```

### Icon Button
```css
.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  background: var(--black);
  color: var(--white);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-icon:hover {
  background: var(--white);
  color: var(--black);
  border-color: var(--white);
}
```

---

## 📦 Card Patterns

### Basic Card
```css
.card {
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1rem;
  transition: all var(--transition-base);
}

.card:hover {
  background: var(--surface-raised);
  border-color: var(--border-medium);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
```

### Card with Bottom Border Animation
```css
.card-animated {
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1rem;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-base);
}

.card-animated::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--white);
  transition: width var(--transition-slow);
}

.card-animated:hover {
  background: var(--surface-raised);
  border-color: var(--border-medium);
  transform: translateY(-2px);
}

.card-animated:hover::after {
  width: 100%;
}
```

### Card with Full Inversion
```css
.card-invert {
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1rem;
  transition: all var(--transition-base);
}

.card-invert:hover {
  background: var(--white);
  border-color: var(--white);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Invert text colors on hover */
.card-invert:hover .card-title {
  color: var(--black);
}

.card-invert:hover .card-description {
  color: var(--gray-dark);
}
```

---

## 🔗 Link Patterns

### Text Link with Underline Animation
```css
.link {
  color: var(--text-secondary);
  text-decoration: none;
  position: relative;
  transition: color var(--transition-base);
}

.link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--white);
  transition: width var(--transition-base);
}

.link:hover {
  color: var(--text-primary);
}

.link:hover::after {
  width: 100%;
}
```

### Navigation Link
```css
.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: 500;
  padding: 0.375rem 0;
  position: relative;
  transition: color var(--transition-base);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--white);
  transition: width var(--transition-base);
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
}

.nav-link:hover::after,
.nav-link.active::after {
  width: 100%;
}
```

---

## 📝 Input Patterns

### Text Input
```css
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
}

.input::placeholder {
  color: var(--text-tertiary);
}

.input:focus {
  outline: none;
  background: var(--surface-raised);
  border-color: var(--border-medium);
  box-shadow: var(--shadow-sm);
}
```

### Search Input with Button
```css
.search-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 1rem;
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
}

.search-input:focus {
  outline: none;
  background: var(--surface-raised);
  border-color: var(--border-medium);
}

.search-button {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  background: var(--black);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
}

.search-button:hover {
  background: var(--white);
  color: var(--black);
  border-color: var(--white);
}
```

---

## 🏷️ Badge/Tag Patterns

### Minimal Tag
```css
.tag {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  font-weight: 500;
  display: inline-block;
  transition: all var(--transition-base);
  cursor: pointer;
}

.tag:hover {
  background: var(--white);
  color: var(--black);
  border-color: var(--white);
  transform: translateY(-1px);
}
```

### Status Badge
```css
.badge {
  padding: 0.25rem 0.5rem;
  background: var(--charcoal-light);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-xs);
  font-weight: 500;
  display: inline-block;
}
```

---

## 📊 List Patterns

### List Item with Hover
```css
.list-item {
  padding: 0.75rem;
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  cursor: pointer;
  border: 1px solid transparent;
}

.list-item:hover {
  background: var(--surface-raised);
  border-color: var(--border-subtle);
  transform: translateX(2px);
}
```

### List Item with Left Border
```css
.list-item-border {
  padding: 0.75rem;
  border-radius: var(--radius-md);
  position: relative;
  transition: all var(--transition-base);
  cursor: pointer;
}

.list-item-border::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 2px;
  background: var(--white);
  transform: scaleY(0);
  transition: transform var(--transition-base);
}

.list-item-border:hover {
  background: var(--surface-raised);
}

.list-item-border:hover::before {
  transform: scaleY(1);
}
```

---

## 🎭 Loading Patterns

### Spinner
```css
.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-subtle);
  border-top-color: var(--white);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

### Skeleton Loader
```css
.skeleton {
  background: var(--charcoal-light);
  border-radius: var(--radius-sm);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.skeleton-text {
  height: 1rem;
  margin-bottom: 0.5rem;
}

.skeleton-title {
  height: 1.5rem;
  width: 60%;
  margin-bottom: 0.75rem;
}
```

---

## 🎨 Overlay Patterns

### Modal Overlay
```css
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-lg);
}
```

### Tooltip
```css
.tooltip {
  position: absolute;
  background: var(--white);
  color: var(--black);
  padding: 0.375rem 0.625rem;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  box-shadow: var(--shadow-md);
  z-index: 1000;
}
```

---

## 📐 Layout Patterns

### Flex Container
```css
.flex-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.flex-column {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
```

### Grid Container
```css
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

@media (max-width: 768px) {
  .grid-2,
  .grid-3,
  .grid-4 {
    grid-template-columns: 1fr;
  }
}
```

---

## 🎯 Utility Classes

### Spacing
```css
.mt-sm { margin-top: var(--spacing-sm); }
.mt-md { margin-top: var(--spacing-md); }
.mt-lg { margin-top: var(--spacing-lg); }

.mb-sm { margin-bottom: var(--spacing-sm); }
.mb-md { margin-bottom: var(--spacing-md); }
.mb-lg { margin-bottom: var(--spacing-lg); }

.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }
```

### Text
```css
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-tertiary { color: var(--text-tertiary); }

.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-h3); }

.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
```

### Display
```css
.hidden { display: none; }
.block { display: block; }
.inline-block { display: inline-block; }
.flex { display: flex; }
.grid { display: grid; }
```

---

## 🎬 Animation Utilities

### Fade In
```css
.fade-in {
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Slide In
```css
.slide-in-left {
  animation: slideInLeft 0.3s ease forwards;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

---

**Usage**: Copy any pattern above and customize as needed. All patterns follow the minimal monochromatic design system.
