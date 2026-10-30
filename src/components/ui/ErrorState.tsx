import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export const ErrorState = forwardRef<HTMLDivElement, ErrorStateProps>(
  (
    {
      className,
      title = 'System Error Encountered',
      message,
      onRetry,
      retryLabel = 'Retry Operation',
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center p-8 bg-status-critical-bg border border-status-critical-border rounded-sm text-center',
          className
        )}
        {...props}
      >
        <div className="p-2.5 bg-red-100 rounded-sm mb-3">
          <AlertTriangle className="w-6 h-6 text-status-critical" />
        </div>
        <h4 className="text-sm font-bold text-red-950 uppercase tracking-wide">
          {title}
        </h4>
        <p className="mt-1 text-xs text-red-800 max-w-md font-mono">
          {message}
        </p>
        {onRetry && (
          <div className="mt-4">
            <Button variant="danger" size="sm" onClick={onRetry}>
              {retryLabel}
            </Button>
          </div>
        )}
      </div>
    );
  }
);
ErrorState.displayName = 'ErrorState';
