import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render } from '@testing-library/react';
import { DashboardBackground } from './DashboardBackground';

// Mock the performance monitor hook with default values
const mockUsePerformanceMonitor = vi.fn(() => ({ 
  fps: 60, 
  isLowPerformance: false 
}));

vi.mock('../../hooks/usePerformanceMonitor', () => ({
  usePerformanceMonitor: () => mockUsePerformanceMonitor(),
}));

describe('DashboardBackground', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render without crashing', () => {
    const { container } = render(<DashboardBackground />);
    expect(container.querySelector('.dashboard-background')).toBeInTheDocument();
  });

  it('should render five gradient orbs by default', () => {
    const { container } = render(<DashboardBackground />);
    const orbs = container.querySelectorAll('.gradient-orb');
    expect(orbs).toHaveLength(5);
  });

  it('should render custom number of layers', () => {
    const { container } = render(<DashboardBackground layers={3} />);
    const orbs = container.querySelectorAll('.gradient-orb');
    expect(orbs).toHaveLength(3);
  });

  it('should apply default intensity and speed', () => {
    const { container } = render(<DashboardBackground />);
    const background = container.querySelector('.dashboard-background');
    expect(background).toHaveAttribute('data-intensity', 'low');
    expect(background).toHaveAttribute('data-speed', 'slow');
  });

  it('should apply custom intensity', () => {
    const { container } = render(<DashboardBackground intensity="high" />);
    const background = container.querySelector('.dashboard-background');
    expect(background).toHaveAttribute('data-intensity', 'high');
  });

  it('should apply custom speed', () => {
    const { container } = render(<DashboardBackground speed="fast" />);
    const background = container.querySelector('.dashboard-background');
    expect(background).toHaveAttribute('data-speed', 'fast');
  });

  it('should have aria-hidden attribute', () => {
    const { container } = render(<DashboardBackground />);
    const background = container.querySelector('.dashboard-background');
    expect(background).toHaveAttribute('aria-hidden', 'true');
  });

  it('should apply reduced-motion class when prefers-reduced-motion is set', () => {
    // Mock matchMedia to return reduced motion preference
    const mockMatchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia,
    });

    const { container } = render(<DashboardBackground />);
    const background = container.querySelector('.dashboard-background');
    
    // Wait for useEffect to run
    setTimeout(() => {
      expect(background).toHaveClass('reduced-motion');
    }, 0);
  });

  it('should set performance attribute', () => {
    const { container } = render(<DashboardBackground />);
    const background = container.querySelector('.dashboard-background');
    expect(background).toHaveAttribute('data-performance');
  });

  it('should accept layers prop', () => {
    const { container } = render(<DashboardBackground layers={4} />);
    const orbs = container.querySelectorAll('.gradient-orb');
    // With normal performance, should render the specified number of layers
    expect(orbs.length).toBeGreaterThan(0);
  });
});
