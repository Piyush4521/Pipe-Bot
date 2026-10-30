import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import type { SystemHealthStatus } from '@/types';

export interface StatusIndicatorProps extends HTMLAttributes<HTMLDivElement> {
  status: SystemHealthStatus;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showPing?: boolean;
}

export const StatusIndicator = forwardRef<HTMLDivElement, StatusIndicatorProps>(
  ({ className, status, label, size = 'md', showPing = false, ...props }, ref) => {
    const dotColors: Record<SystemHealthStatus, string> = {
      healthy: 'bg-status-healthy',
      warning: 'bg-status-warning',
      critical: 'bg-status-critical',
      offline: 'bg-industrial-400',
      idle: 'bg-industrial-500',
    };

    const pingColors: Record<SystemHealthStatus, string> = {
      healthy: 'bg-status-healthy',
      warning: 'bg-status-warning',
      critical: 'bg-status-critical',
      offline: 'bg-industrial-400',
      idle: 'bg-industrial-500',
    };

    const dotSizes = {
      sm: 'w-2 h-2',
      md: 'w-2.5 h-2.5',
      lg: 'w-3 h-3',
    };

    const textSizes = {
      sm: 'text-xs',
      md: 'text-xs font-medium',
      lg: 'text-sm font-medium',
    };

    return (
      <div
        ref={ref}
        className={cn('inline-flex items-center gap-2 select-none', className)}
        {...props}
      >
        <span className="relative flex items-center justify-center">
          {showPing && status !== 'offline' && (
            <span
              className={cn(
                'absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping',
                pingColors[status]
              )}
            />
          )}
          <span
            className={cn('relative inline-flex rounded-full', dotSizes[size], dotColors[status])}
          />
        </span>
        {label && (
          <span className={cn('text-industrial-700', textSizes[size])}>
            {label}
          </span>
        )}
      </div>
    );
  }
);
StatusIndicator.displayName = 'StatusIndicator';
