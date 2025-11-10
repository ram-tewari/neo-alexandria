// Neo Alexandria 2.0 Frontend - Toast Notification Store
// Manages toast notifications state

import { create } from 'zustand';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: Toast = {
      ...toast,
      id,
      duration: toast.duration ?? 5000,
    };

    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));

    // Auto-remove toast after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, newToast.duration);
    }
  },

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),

  clearToasts: () => set({ toasts: [] }),
}));

// Convenience functions for common toast types
export const toast = {
  success: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'success', title, message, duration });
  },

  error: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'error', title, message, duration });
  },

  warning: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'warning', title, message, duration });
  },

  info: (title: string, message?: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'info', title, message, duration });
  },

  custom: (toast: Omit<Toast, 'id'>) => {
    useToastStore.getState().addToast(toast);
  },
};
