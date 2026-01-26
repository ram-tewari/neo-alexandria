/**
 * ErrorToast - Toast notification for transient errors
 */
import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ClassifiedError } from '@/lib/errors';
import { formatError } from '@/lib/errors';

export interface ErrorToastProps {
  error: ClassifiedError;
  onDismiss?: () => void;
  autoHideDuration?: number;
}

export function ErrorToast({ error, onDismiss, autoHideDuration = 5000 }: ErrorToastProps) {
  const [isVisible, setIsVisible] = useState(true);
  const formatted = formatError(error);

  useEffect(() => {
    if (autoHideDuration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onDismiss?.(), 300); // Wait for animation
      }, autoHideDuration);

      return () => clearTimeout(timer);
    }
  }, [autoHideDuration, onDismiss]);

  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(() => onDismiss?.(), 300);
  };

  const getSeverityStyles = () => {
    switch (error.severity) {
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950 dark:border-blue-800 dark:text-blue-100';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-950 dark:border-yellow-800 dark:text-yellow-100';
      case 'high':
        return 'bg-orange-50 border-orange-200 text-orange-900 dark:bg-orange-950 dark:border-orange-800 dark:text-orange-100';
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-900 dark:bg-red-950 dark:border-red-800 dark:text-red-100';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-900 dark:bg-gray-950 dark:border-gray-800 dark:text-gray-100';
    }
  };

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        'fixed bottom-4 right-4 z-50 w-96 rounded-lg border p-4 shadow-lg transition-all duration-300',
        getSeverityStyles(),
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl flex-shrink-0" aria-hidden="true">
          {formatted.icon}
        </span>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm mb-1">{formatted.title}</h3>
          <p className="text-sm opacity-90">{formatted.message}</p>
        </div>
        <button
          onClick={handleDismiss}
          className="flex-shrink-0 p-1 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
