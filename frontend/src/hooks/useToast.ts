// Neo Alexandria 2.0 Frontend - Toast Hook
// Custom hook for toast notifications

import { useCallback } from 'react';
import { useToastStore, Toast } from '@/store/toastStore';

export function useToast() {
  const { addToast, removeToast, clearToasts } = useToastStore();

  const success = useCallback(
    (title: string, message?: string, duration?: number) => {
      addToast({ type: 'success', title, message, duration });
    },
    [addToast]
  );

  const error = useCallback(
    (title: string, message?: string, duration?: number) => {
      addToast({ type: 'error', title, message, duration });
    },
    [addToast]
  );

  const warning = useCallback(
    (title: string, message?: string, duration?: number) => {
      addToast({ type: 'warning', title, message, duration });
    },
    [addToast]
  );

  const info = useCallback(
    (title: string, message?: string, duration?: number) => {
      addToast({ type: 'info', title, message, duration });
    },
    [addToast]
  );

  const custom = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      addToast(toast);
    },
    [addToast]
  );

  return {
    success,
    error,
    warning,
    info,
    custom,
    remove: removeToast,
    clear: clearToasts,
  };
}
