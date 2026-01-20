/**
 * Example Test File
 * 
 * Demonstrates testing patterns and utilities
 */

import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, createMockResponse } from './utils';
import * as fc from 'fast-check';
import { jwtArbitrary, propertyTestConfig } from './property-helpers';

describe('Test Infrastructure', () => {
  describe('Unit Testing', () => {
    it('should render components with providers', () => {
      const TestComponent = () => <div>Test Component</div>;
      const { getByText } = renderWithProviders(<TestComponent />);
      expect(getByText('Test Component')).toBeInTheDocument();
    });

    it('should create mock responses', () => {
      const mockData = { id: '123', name: 'Test' };
      const response = createMockResponse(mockData);
      expect(response.ok).toBe(true);
      expect(response.status).toBe(200);
    });

    it('should mock localStorage', () => {
      localStorage.setItem('test', 'value');
      expect(localStorage.getItem('test')).toBe('value');
      localStorage.clear();
      expect(localStorage.getItem('test')).toBeNull();
    });

    it('should mock sessionStorage', () => {
      sessionStorage.setItem('test', 'value');
      expect(sessionStorage.getItem('test')).toBe('value');
      sessionStorage.clear();
      expect(sessionStorage.getItem('test')).toBeNull();
    });
  });

  describe('Property-Based Testing', () => {
    it('should generate valid JWT structures', () => {
      fc.assert(
        fc.property(jwtArbitrary, (claims) => {
          // Property: All generated JWT claims should have required fields
          expect(claims).toHaveProperty('sub');
          expect(claims).toHaveProperty('email');
          expect(claims).toHaveProperty('exp');
          expect(claims).toHaveProperty('iat');
          expect(claims.exp).toBeGreaterThan(claims.iat);
          return true;
        }),
        propertyTestConfig
      );
    });

    it('should handle arbitrary strings', () => {
      fc.assert(
        fc.property(fc.string(), (str) => {
          // Property: String length should match actual length
          expect(str.length).toBe(str.length);
          return true;
        }),
        propertyTestConfig
      );
    });
  });

  describe('Mock Functions', () => {
    it('should create and use mock functions', () => {
      const mockFn = vi.fn();
      mockFn('test');
      expect(mockFn).toHaveBeenCalledWith('test');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should mock fetch', async () => {
      const mockData = { message: 'success' };
      global.fetch = vi.fn().mockResolvedValue(createMockResponse(mockData));

      const response = await fetch('/api/test');
      const data = await response.json();

      expect(data).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith('/api/test');
    });
  });
});
