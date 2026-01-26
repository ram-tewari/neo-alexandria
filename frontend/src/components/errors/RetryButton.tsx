/**
 * RetryButton - Button component for retrying failed operations
 */
import { useState, useEffect } from 'react';
import { RefreshCw, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatRetryCountdown } from '@/lib/errors';

export interface RetryButtonProps {
  onRetry: () => void | Promise<void>;
  disabled?: boolean;
  retryAfter?: number; // Seconds to wait before allowing retry
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export function RetryButton({
  onRetry,
  disabled = false,
  retryAfter,
  className,
  variant = 'default',
  size = 'md',
}: RetryButtonProps) {
  const [isRetrying, setIsRetrying] = useState(false);
  const [countdown, setCountdown] = useState(retryAfter || 0);

  useEffect(() => {
    if (retryAfter && retryAfter > 0) {
      setCountdown(retryAfter);

      const interval = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [retryAfter]);

  const handleRetry = async () => {
    if (disabled || isRetrying || countdown > 0) {
      return;
    }

    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  const isDisabled = disabled || isRetrying || countdown > 0;

  const getVariantStyles = () => {
    switch (variant) {
      case 'outline':
        return 'border border-input bg-background hover:bg-accent hover:text-accent-foreground';
      case 'ghost':
        return 'hover:bg-accent hover:text-accent-foreground';
      case 'default':
      default:
        return 'bg-primary text-primary-foreground hover:bg-primary/90';
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'h-8 px-3 text-xs';
      case 'lg':
        return 'h-11 px-8 text-base';
      case 'md':
      default:
        return 'h-9 px-4 text-sm';
    }
  };

  return (
    <button
      onClick={handleRetry}
      disabled={isDisabled}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        getVariantStyles(),
        getSizeStyles(),
        className
      )}
      aria-label={countdown > 0 ? formatRetryCountdown(countdown) : 'Retry'}
    >
      {countdown > 0 ? (
        <>
          <Clock className={cn('animate-pulse', size === 'sm' ? 'h-3 w-3' : 'h-4 w-4')} />
          <span>{formatRetryCountdown(countdown)}</span>
        </>
      ) : (
        <>
          <RefreshCw
            className={cn(
              size === 'sm' ? 'h-3 w-3' : 'h-4 w-4',
              isRetrying && 'animate-spin'
            )}
          />
          <span>{isRetrying ? 'Retrying...' : 'Retry'}</span>
        </>
      )}
    </button>
  );
}
