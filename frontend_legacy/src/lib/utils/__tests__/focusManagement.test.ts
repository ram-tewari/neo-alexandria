/**
 * Tests for focus management utilities
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import {
  getFocusableElements,
  trapFocus,
  FocusManager,
  moveFocusTo,
} from '../focusManagement';

describe('getFocusableElements', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  it('finds all focusable elements', () => {
    container.innerHTML = `
      <button>Button 1</button>
      <a href="#">Link</a>
      <input type="text" />
      <button disabled>Disabled Button</button>
      <div tabindex="0">Focusable Div</div>
      <div tabindex="-1">Non-focusable Div</div>
    `;

    const focusable = getFocusableElements(container);
    
    expect(focusable).toHaveLength(4); // button, link, input, div with tabindex="0"
    expect(focusable[0].tagName).toBe('BUTTON');
    expect(focusable[1].tagName).toBe('A');
    expect(focusable[2].tagName).toBe('INPUT');
    expect(focusable[3].tagName).toBe('DIV');
  });

  it('excludes disabled elements', () => {
    container.innerHTML = `
      <button>Enabled</button>
      <button disabled>Disabled</button>
      <input type="text" disabled />
    `;

    const focusable = getFocusableElements(container);
    
    expect(focusable).toHaveLength(1);
    expect(focusable[0].textContent).toBe('Enabled');
  });

  it('returns empty array for container with no focusable elements', () => {
    container.innerHTML = `
      <div>Not focusable</div>
      <span>Also not focusable</span>
    `;

    const focusable = getFocusableElements(container);
    
    expect(focusable).toHaveLength(0);
  });
});

describe('trapFocus', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  it('focuses first element when trap is activated', () => {
    container.innerHTML = `
      <button id="first">First</button>
      <button id="second">Second</button>
    `;

    const cleanup = trapFocus(container);
    
    const firstButton = document.getElementById('first');
    expect(document.activeElement).toBe(firstButton);
    
    cleanup();
  });

  it('returns cleanup function', () => {
    container.innerHTML = `<button>Button</button>`;
    
    const cleanup = trapFocus(container);
    
    expect(typeof cleanup).toBe('function');
    expect(() => cleanup()).not.toThrow();
  });
});

describe('FocusManager', () => {
  let button: HTMLButtonElement;

  beforeEach(() => {
    button = document.createElement('button');
    button.textContent = 'Test Button';
    document.body.appendChild(button);
  });

  afterEach(() => {
    document.body.removeChild(button);
  });

  it('saves and restores focus', () => {
    const manager = new FocusManager();
    
    button.focus();
    expect(document.activeElement).toBe(button);
    
    manager.saveFocus();
    
    // Blur the button
    button.blur();
    expect(document.activeElement).not.toBe(button);
    
    manager.restoreFocus();
    expect(document.activeElement).toBe(button);
  });

  it('handles restoring focus when no element was saved', () => {
    const manager = new FocusManager();
    
    expect(() => manager.restoreFocus()).not.toThrow();
  });
});

describe('moveFocusTo', () => {
  let button: HTMLButtonElement;

  beforeEach(() => {
    button = document.createElement('button');
    button.textContent = 'Test Button';
    document.body.appendChild(button);
  });

  afterEach(() => {
    document.body.removeChild(button);
  });

  it('moves focus to specified element', () => {
    moveFocusTo(button);
    
    expect(document.activeElement).toBe(button);
  });

  it('handles null element gracefully', () => {
    expect(() => moveFocusTo(null)).not.toThrow();
  });

  it('respects preventScroll option', () => {
    moveFocusTo(button, { preventScroll: true });
    
    expect(document.activeElement).toBe(button);
  });
});
