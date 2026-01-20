/**
 * Tests for screen reader announcement utilities
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  announceToScreenReader,
  announceFilterChange,
  announceUploadProgress,
  announceBatchSelection,
} from '../announceToScreenReader';

describe('announceToScreenReader', () => {
  beforeEach(() => {
    // Clear any existing live regions
    document.body.innerHTML = '';
  });

  afterEach(() => {
    // Clean up
    document.body.innerHTML = '';
  });

  it('creates a polite live region when first called', () => {
    announceToScreenReader('Test message', 'polite');
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion).toBeTruthy();
    expect(liveRegion?.getAttribute('aria-live')).toBe('polite');
    expect(liveRegion?.getAttribute('role')).toBe('status');
  });

  it('creates an assertive live region when specified', () => {
    announceToScreenReader('Urgent message', 'assertive');
    
    const liveRegion = document.getElementById('aria-live-assertive');
    expect(liveRegion).toBeTruthy();
    expect(liveRegion?.getAttribute('aria-live')).toBe('assertive');
    expect(liveRegion?.getAttribute('role')).toBe('alert');
  });

  it('updates existing live region with new message', async () => {
    announceToScreenReader('First message', 'polite');
    
    // Wait for the timeout
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toBe('First message');
    
    announceToScreenReader('Second message', 'polite');
    
    // Wait for the timeout
    await new Promise(resolve => setTimeout(resolve, 150));
    
    expect(liveRegion?.textContent).toBe('Second message');
  });

  it('has sr-only class for visual hiding', () => {
    announceToScreenReader('Test', 'polite');
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.className).toContain('sr-only');
  });
});

describe('announceFilterChange', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('announces filter change with result count', async () => {
    announceFilterChange('Classification', 'Computer Science', 42);
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('Classification');
    expect(liveRegion?.textContent).toContain('Computer Science');
    expect(liveRegion?.textContent).toContain('42');
  });

  it('announces filter change without result count', async () => {
    announceFilterChange('Type', 'Article');
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('Type');
    expect(liveRegion?.textContent).toContain('Article');
  });
});

describe('announceUploadProgress', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('announces upload progress with stage', async () => {
    announceUploadProgress('document.pdf', 75, 'Analyzing');
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('document.pdf');
    expect(liveRegion?.textContent).toContain('75%');
    expect(liveRegion?.textContent).toContain('Analyzing');
  });

  it('announces upload progress without stage', async () => {
    announceUploadProgress('file.txt', 50);
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('file.txt');
    expect(liveRegion?.textContent).toContain('50%');
  });
});

describe('announceBatchSelection', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('announces selection count with total', async () => {
    announceBatchSelection(5, 20);
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('5');
    expect(liveRegion?.textContent).toContain('20');
  });

  it('announces selection count without total', async () => {
    announceBatchSelection(3);
    
    await new Promise(resolve => setTimeout(resolve, 150));
    
    const liveRegion = document.getElementById('aria-live-polite');
    expect(liveRegion?.textContent).toContain('3');
    expect(liveRegion?.textContent).toContain('items selected');
  });
});
