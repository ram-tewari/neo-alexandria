/**
 * Spinner - Loading spinner component
 */
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  label?: string;
}

export function Spinner({ size = 'md', className, label = 'Loading...' }: SpinnerProps) {
  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'h-4 w-4';
      case 'lg':
        return 'h-8 w-8';
      case 'xl':
        return 'h-12 w-12';
      case 'md':
      default:
        return 'h-6 w-6';
    }
  };

  return (
    <div className="flex items-center justify-center" role="status" aria-label={label}>
      <Loader2 className={cn('animate-spin text-primary', getSizeStyles(), className)} />
      <span className="sr-only">{label}</span>
    </div>
  );
}

/**
 * FullPageSpinner - Centered spinner for full page loading
 */
export function FullPageSpinner({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <Spinner size="xl" label={label} />
    </div>
  );
}

/**
 * InlineSpinner - Small inline spinner
 */
export function InlineSpinner({ label = 'Loading...' }: { label?: string }) {
  return <Spinner size="sm" label={label} />;
}
