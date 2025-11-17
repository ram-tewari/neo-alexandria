/**
 * Test Setup
 * 
 * Global test configuration and setup
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock environment variables
vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000');
vi.stubEnv('VITE_ENVIRONMENT', 'test');

// Global fetch mock
global.fetch = vi.fn();
