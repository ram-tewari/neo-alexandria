/**
 * ToastContainer component
 * Renders active toasts at top-right corner with 8px vertical gap
 */

import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { useToast } from '../../../contexts/ToastContext';
import { Toast } from './Toast';

/**
 * Container for rendering toast notifications
 */
export const ToastContainer: React.FC = () => {
  const { toasts, dismissToast } = useToast();

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"
      aria-live="polite"
      aria-atomic="false"
    >
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <Toast toast={toast} onDismiss={dismissToast} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
};
