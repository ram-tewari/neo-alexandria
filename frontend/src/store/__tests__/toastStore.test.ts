import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useToastStore } from '../toastStore';

describe('toastStore', () => {
  beforeEach(() => {
    useToastStore.getState().clearAll();
  });

  it('adds a toast', () => {
    const { addToast, toasts } = useToastStore.getState();
    
    addToast({
      type: 'success',
      message: 'Test message',
      duration: 0,
    });

    expect(useToastStore.getState().toasts).toHaveLength(1);
    expect(useToastStore.getState().toasts[0].message).toBe('Test message');
    expect(useToastStore.getState().toasts[0].type).toBe('success');
  });

  it('removes a toast', () => {
    const { addToast, removeToast } = useToastStore.getState();
    
    addToast({
      type: 'info',
      message: 'Test',
      duration: 0,
    });

    const toastId = useToastStore.getState().toasts[0].id;
    removeToast(toastId);

    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it('limits toasts to maximum of 3', () => {
    const { addToast } = useToastStore.getState();
    
    addToast({ type: 'info', message: '1', duration: 0 });
    addToast({ type: 'info', message: '2', duration: 0 });
    addToast({ type: 'info', message: '3', duration: 0 });
    addToast({ type: 'info', message: '4', duration: 0 });

    expect(useToastStore.getState().toasts).toHaveLength(3);
    expect(useToastStore.getState().toasts[2].message).toBe('4');
  });

  it('clears all toasts', () => {
    const { addToast, clearAll } = useToastStore.getState();
    
    addToast({ type: 'info', message: '1', duration: 0 });
    addToast({ type: 'info', message: '2', duration: 0 });
    
    clearAll();

    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it('auto-dismisses toast after duration', async () => {
    vi.useFakeTimers();
    const { addToast } = useToastStore.getState();
    
    addToast({
      type: 'success',
      message: 'Auto dismiss',
      duration: 1000,
    });

    expect(useToastStore.getState().toasts).toHaveLength(1);

    vi.advanceTimersByTime(1000);

    expect(useToastStore.getState().toasts).toHaveLength(0);
    
    vi.useRealTimers();
  });
});
