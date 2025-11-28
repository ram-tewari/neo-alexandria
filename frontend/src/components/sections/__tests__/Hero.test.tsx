/**
 * Unit Tests for Hero Component
 */

import { describe, it, expect } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { Hero } from '../Hero';
import { ThemeProvider } from '../../../contexts/ThemeContext';

describe('Hero Component', () => {
  it('should render hero with title', () => {
    const { container } = render(
      <ThemeProvider>
        <Hero title="Test Title" />
      </ThemeProvider>
    );

    expect(container.querySelector('.hero__title')).toHaveTextContent('Test Title');
  });

  it('should render background in light mode after mount', async () => {
    const { container } = render(
      <ThemeProvider defaultTheme="light">
        <Hero title="Test" backgroundAnimation={true} />
      </ThemeProvider>
    );

    await waitFor(() => {
      const background = container.querySelector('.hero__background');
      expect(background).toBeTruthy();
    }, { timeout: 1000 });

    const lightAccent = container.querySelector('.hero__background-accent--light');
    expect(lightAccent).toBeTruthy();
  });

  it('should render glow effects in dark mode after mount', async () => {
    // Set dark theme in localStorage before rendering
    localStorage.setItem('theme-preference', 'dark');
    
    const { container, rerender } = render(
      <ThemeProvider defaultTheme="dark" storageKey="theme-preference">
        <Hero title="Test" backgroundAnimation={true} />
      </ThemeProvider>
    );

    // Wait for theme to be applied
    await waitFor(() => {
      const hero = container.querySelector('.hero');
      expect(hero?.getAttribute('data-theme')).toBe('dark');
    }, { timeout: 1000 });

    const glow1 = container.querySelector('.hero__background-accent--glow-1');
    const glow2 = container.querySelector('.hero__background-accent--glow-2');
    
    expect(glow1).toBeTruthy();
    expect(glow2).toBeTruthy();
    
    // Cleanup
    localStorage.removeItem('theme-preference');
  });
});
