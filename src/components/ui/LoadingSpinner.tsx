import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

export interface LoadingSpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export const LoadingSpinner = forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  ({ className, size = 'md', label, ...props }, ref) => {
    const sizeMap = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
    };

    return (
      <div
        ref={ref}
        className={cn('inline-flex items-center justify-center gap-2 text-industrial-600', className)}
        {...props}
      >
        <Loader2 className={cn('animate-spin text-brand-orange', sizeMap[size])} />
        {label && <span className="text-xs font-medium tracking-wide uppercase">{label}</span>}
      </div>
    );
  }
);
LoadingSpinner.displayName = 'LoadingSpinner';

export interface LoadingStateProps extends HTMLAttributes<HTMLDivElement> {
  message?: string;
}

export const LoadingState = forwardRef<HTMLDivElement, LoadingStateProps>(
  ({ className, message = 'Loading system data...', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center p-12 bg-white border border-industrial-200 rounded-sm text-center',
          className
        )}
        {...props}
      >
        <LoadingSpinner size="lg" />
        <p className="mt-3 text-xs uppercase tracking-wider text-industrial-500 font-mono">
          {message}
        </p>
      </div>
    );
  }
);
LoadingState.displayName = 'LoadingState';
