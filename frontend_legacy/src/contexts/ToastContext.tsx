/**
 * Toast notification context and provider
 * Manages toast queue with max 3 visible toasts and auto-dismiss timers
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

export interface Toast {
  id: string;
  variant: 'success' | 'error' | 'info' | 'loading';
  message: string;
  duration?: number | null; // null for manual dismiss
}

interface ToastContextValue {
  toasts: Toast[];
  showToast: (toast: Omit<Toast, 'id'>) => string;
  dismissToast: (id: string) => void;
  updateToast: (id: string, updates: Partial<Omit<Toast, 'id'>>) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

const MAX_VISIBLE_TOASTS = 3;
const DEFAULT_DURATION = 4000; // 4 seconds

/**
 * Generate unique toast ID
 */
const generateId = (): string => {
  return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Get default duration based on variant
 */
const getDefaultDuration = (variant: Toast['variant']): number | null => {
  if (variant === 'error' || variant === 'loading') {
    return null; // Manual dismiss
  }
  return DEFAULT_DURATION;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [timers, setTimers] = useState<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  /**
   * Show a new toast
   */
  const showToast = useCallback((toast: Omit<Toast, 'id'>): string => {
    const id = generateId();
    const duration = toast.duration !== undefined ? toast.duration : getDefaultDuration(toast.variant);
    
    const newToast: Toast = {
      ...toast,
      id,
      duration,
    };

    setToasts((prev) => [...prev, newToast]);

    // Set auto-dismiss timer if duration is specified
    if (duration !== null && duration > 0) {
      const timer = setTimeout(() => {
        dismissToast(id);
      }, duration);
      
      setTimers((prev) => new Map(prev).set(id, timer));
    }

    return id;
  }, []);

  /**
   * Dismiss a toast by ID
   */
  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
    
    // Clear timer if exists
    setTimers((prev) => {
      const newTimers = new Map(prev);
      const timer = newTimers.get(id);
      if (timer) {
        clearTimeout(timer);
        newTimers.delete(id);
      }
      return newTimers;
    });
  }, []);

  /**
   * Update an existing toast
   */
  const updateToast = useCallback((id: string, updates: Partial<Omit<Toast, 'id'>>) => {
    setToasts((prev) =>
      prev.map((toast) =>
        toast.id === id ? { ...toast, ...updates } : toast
      )
    );
  }, []);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [timers]);

  const value: ToastContextValue = {
    toasts: toasts.slice(-MAX_VISIBLE_TOASTS), // Only show last 3 toasts
    showToast,
    dismissToast,
    updateToast,
  };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
};

/**
 * Hook to access toast context
 */
export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
