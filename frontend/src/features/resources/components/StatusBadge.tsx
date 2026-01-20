/**
 * StatusBadge component
 * 
 * Displays resource ingestion status with color-coded badges and icons.
 */
import { Badge } from '@/components/ui/badge';
import { Clock, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { ResourceStatus } from '@/core/types/resource';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: ResourceStatus;
  className?: string;
}

/**
 * Status badge with color-coded styling and icons
 * 
 * @param status - Resource ingestion status
 * @param className - Optional additional CSS classes
 * 
 * @example
 * ```tsx
 * <StatusBadge status={ResourceStatus.PROCESSING} />
 * ```
 */
export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = getStatusConfig(status);

  return (
    <Badge
      className={cn(config.className, className)}
      aria-label={`Status: ${status}`}
    >
      <config.icon className={cn('h-3 w-3 mr-1', config.iconClassName)} />
      {config.label}
    </Badge>
  );
}

/**
 * Get configuration for each status type
 */
function getStatusConfig(status: ResourceStatus) {
  switch (status) {
    case ResourceStatus.PENDING:
      return {
        label: 'Pending',
        icon: Clock,
        className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100',
        iconClassName: '',
      };
    case ResourceStatus.PROCESSING:
      return {
        label: 'Processing',
        icon: Loader2,
        className: 'bg-blue-100 text-blue-800 hover:bg-blue-100',
        iconClassName: 'animate-spin',
      };
    case ResourceStatus.COMPLETED:
      return {
        label: 'Completed',
        icon: CheckCircle2,
        className: 'bg-green-100 text-green-800 hover:bg-green-100',
        iconClassName: '',
      };
    case ResourceStatus.FAILED:
      return {
        label: 'Failed',
        icon: XCircle,
        className: 'bg-red-100 text-red-800 hover:bg-red-100',
        iconClassName: '',
      };
    default:
      return {
        label: 'Unknown',
        icon: Clock,
        className: 'bg-gray-100 text-gray-800 hover:bg-gray-100',
        iconClassName: '',
      };
  }
}
