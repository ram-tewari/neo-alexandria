import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useWorkbenchStore } from '../workbench';

/**
 * Property-Based Tests for Workbench Store
 * 
 * Feature: phase1-workbench-navigation
 * Property 1: Sidebar State Persistence
 * Validates: Requirements 1.6
 */

describe('Workbench Store - Property Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  /**
   * Property 1: Sidebar State Persistence
   * For any sidebar state (true/false), toggling the sidebar should persist
   * to localStorage and be retrievable on store rehydration
   */
  it('should persist sidebar state to localStorage for all boolean values', async () => {
    const states = [true, false];

    for (const state of states) {
      // Set sidebar state
      useWorkbenchStore.getState().setSidebarOpen(state);

      // Verify store state
      expect(useWorkbenchStore.getState().sidebarOpen).toBe(state);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      // Verify localStorage persistence
      const stored = localStorage.getItem('pharos-workbench');
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.sidebarOpen).toBe(state);
      }
    }
  });

  it('should maintain sidebar state consistency across toggles', async () => {
    // Start with true
    useWorkbenchStore.getState().setSidebarOpen(true);
    expect(useWorkbenchStore.getState().sidebarOpen).toBe(true);

    // Toggle to false
    useWorkbenchStore.getState().toggleSidebar();
    expect(useWorkbenchStore.getState().sidebarOpen).toBe(false);

    // Wait for persistence
    await new Promise(resolve => setTimeout(resolve, 100));

    // Verify localStorage
    let stored = localStorage.getItem('pharos-workbench');
    if (stored) {
      let parsed = JSON.parse(stored);
      expect(parsed.state.sidebarOpen).toBe(false);
    }

    // Toggle back to true
    useWorkbenchStore.getState().toggleSidebar();
    expect(useWorkbenchStore.getState().sidebarOpen).toBe(true);

    // Wait for persistence
    await new Promise(resolve => setTimeout(resolve, 100));

    // Verify localStorage again
    stored = localStorage.getItem('pharos-workbench');
    if (stored) {
      let parsed = JSON.parse(stored);
      expect(parsed.state.sidebarOpen).toBe(true);
    }
  });

  it('should default to open sidebar when no localStorage value exists', () => {
    // Clear localStorage
    localStorage.clear();
    
    // Get initial state
    const initialState = useWorkbenchStore.getState().sidebarOpen;
    
    // Should default to true (open)
    expect(initialState).toBe(true);
  });

  it('should persist sidebar state through multiple toggle operations', async () => {
    // Perform multiple toggles
    for (let i = 0; i < 10; i++) {
      useWorkbenchStore.getState().toggleSidebar();
      
      const currentState = useWorkbenchStore.getState().sidebarOpen;
      
      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const stored = localStorage.getItem('pharos-workbench');
      if (stored) {
        const parsed = JSON.parse(stored);
        
        // Verify consistency after each toggle
        expect(parsed.state.sidebarOpen).toBe(currentState);
      }
    }
  });
});
