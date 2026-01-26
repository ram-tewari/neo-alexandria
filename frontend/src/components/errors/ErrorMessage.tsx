/**
 * ErrorMessage - Inline error message component
 */
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ClassifiedError } from '@/lib/errors';
import { formatError } from '@/lib/errors';

export interface ErrorMessageProps {
  error: ClassifiedError;
  className?: string;
  showIcon?: boolean;
  compact?: boolean;
}

export function ErrorMessage({ 
  error, 
  className, 
  showIcon = true,
  compact = false 
}: ErrorMessageProps) {
  const formatted = formatError(error);

  const getSeverityIcon = () => {
    switch (error.severity) {
      case 'low':
        return <Info className="h-4 w-4" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />;
      case 'high':
        return <AlertCircle className="h-4 w-4" />;
      case 'critical':
        return <XCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
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

  if (compact) {
    return (
      <div
        role="alert"
        className={cn(
          'flex items-center gap-2 text-sm',
          getSeverityStyles(),
          className
        )}
      >
        {showIcon && getSeverityIcon()}
        <span>{formatted.message}</span>
      </div>
    );
  }

  return (
    <div
      role="alert"
      className={cn(
        'rounded-lg border p-4',
        getSeverityStyles(),
        className
      )}
    >
      <div className="flex items-start gap-3">
        {showIcon && (
          <div className="flex-shrink-0 mt-0.5">
            {getSeverityIcon()}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm mb-1">{formatted.title}</h3>
          <p className="text-sm opacity-90">{formatted.message}</p>
        </div>
      </div>
    </div>
  );
}
